#include "Collection.h"
#include "PFJet.h"
#include "JMESystematicsCalculators.h"
#include <variant>
#include <filesystem>

using namespace ROOT;
using METSystematicsResult = std::map<std::string, double>;

class JMEUncertainties {

  public:
    using JetMETArgType = std::variant<RVecF, RVecI, float, std::uint32_t>;
    using JetVariationsResult = JetVariationsCalculator::result_t;
    using METVariationsResult = Type1METVariationsCalculator::result_t;

    template <typename T>
      JMEUncertainties(T&& t, analysisClass* d,
          const std::vector<std::string>& jesUncertainties, const std::string& jecTextFilePath, const std::string& jerTextFilePath,
          const std::string& jecTag, const std::string& jerTag, bool splitJER=false,
          bool doGenMatch=true,
          float genMatchMaxDR=0.2, float genMatchMaxDPt = 3.0) :
        m_calc(std::forward<T>(t)),
        m_data(d),
        m_splitJER (splitJER),
        m_doGenMatch (doGenMatch),
        m_genMatchMaxDR (genMatchMaxDR),
        m_genMatchMaxDPt (genMatchMaxDPt)
        {
          // redo JEC, push_back corrector parameters for different levels
          std::vector<JetCorrectorParameters> jecParams;
          std::string ourJecTextFilePath = jecTextFilePath+jecTag+"/"+jecTag;
          std::string ourJerTextFilePath = jerTextFilePath+jerTag+"/"+jerTag;
          m_jerTextFilePath = ourJerTextFilePath;
          std::string textFilePath_UncertaintySources = ourJecTextFilePath + "_UncertaintySources_AK4PFchs.txt";
          CheckFileExists(textFilePath_UncertaintySources);
          std::string textFilePath_PtResolution = ourJerTextFilePath + "_PtResolution_AK4PFchs.txt";
          CheckFileExists(textFilePath_PtResolution);
          m_ptResTxtFile = textFilePath_PtResolution;
          std::string textFilePath_SF =  ourJerTextFilePath + "_SF_AK4PFchs.txt";
          CheckFileExists(textFilePath_SF);
          m_sfTxtFile = textFilePath_SF;
          std::string textFilePath_L1Corr = ourJecTextFilePath+"_L1FastJet_AK4PFchs.txt";
          CheckFileExists(textFilePath_L1Corr);
          std::string textFilePath_L2Corr = ourJecTextFilePath+"_L2Relative_AK4PFchs.txt";
          CheckFileExists(textFilePath_L2Corr);
          std::string textFilePath_L3Corr = ourJecTextFilePath+"_L3Absolute_AK4PFchs.txt";
          CheckFileExists(textFilePath_L3Corr);
          std::string textFilePath_L2L3Corr = ourJecTextFilePath+"_L2L3Residual_AK4PFchs.txt";
          CheckFileExists(textFilePath_L2L3Corr);
          jecParams.push_back(JetCorrectorParameters(textFilePath_L1Corr));
          std::vector<JetCorrectorParameters> l1JecParams(jecParams);
          jecParams.push_back(JetCorrectorParameters(textFilePath_L2Corr));
          jecParams.push_back(JetCorrectorParameters(textFilePath_L3Corr));
          jecParams.push_back(JetCorrectorParameters(textFilePath_L2L3Corr));
          std::visit(
              [&jecParams](auto& calc) {
              calc.setJEC(jecParams);
              }, m_calc);
          if(std::holds_alternative<Type1METVariationsCalculator>(m_calc))
              std::get<Type1METVariationsCalculator>(m_calc).setL1JEC(l1JecParams);
          else if(std::holds_alternative<FixEE2017Type1METVariationsCalculator>(m_calc))
              std::get<FixEE2017Type1METVariationsCalculator>(m_calc).setL1JEC(l1JecParams);
          // calculate JES uncertainties
          for(const auto& jesSource : jesUncertainties) {
            JetCorrectorParameters jcp_unc(textFilePath_UncertaintySources, jesSource);
            std::visit(
                [&jesSource, &jcp_unc](auto& calc) {
                calc.addJESUncertainty(jesSource, jcp_unc);
                }, m_calc);
          }
        }

    void setSmearing() {
      std::visit(
          [this](auto& calc) {
          calc.setSmearing(m_ptResTxtFile, m_sfTxtFile,
              m_splitJER,       // decorrelate for different regions
              m_doGenMatch, m_genMatchMaxDR, m_genMatchMaxDPt);  // use hybrid recipe, matching parameters
          }, m_calc);
    }

    void setGenMatching(bool doGenMatch) {
      m_doGenMatch = doGenMatch;
      setSmearing();
    }

    void ComputeJetVariations(CollectionPtr jetCollection, CollectionPtr genJetCollection = nullptr,
        bool isMC=false, bool verbose=false) {
      JetVariationsResult result = produceJetVariations(jetCollection, genJetCollection, isMC);
      std::vector<std::string> variations = available();
      std::vector<RVecF> systematics;
      std::vector<RVecF> massSystematics;
      std::vector<std::string> systematicsNames;
      std::vector<unsigned short> rawIndices = jetCollection->GetRawIndices();
      sort(rawIndices.begin(), rawIndices.end());
      for(unsigned short varIdx = 0; varIdx < result.size(); ++varIdx) {
        RVecF calculatedPtVariations = result.pt(varIdx);
        RVecF calculatedMassVariations = result.mass(varIdx);
        RVecF ptVariationByJet;
        RVecF massVariationByJet;
        unsigned short vecIdx = 0;
        if(!rawIndices.size())
          break;
        unsigned short lastRawIdxIdx = 0;
        for(unsigned short idx = 0; idx <= rawIndices[rawIndices.size()-1]; ++idx) {
          bool foundElement = idx == rawIndices[lastRawIdxIdx];
          float pt = foundElement ? calculatedPtVariations[lastRawIdxIdx] : 0.0;
          ptVariationByJet.emplace_back(pt);
          float mass = foundElement ? calculatedMassVariations[lastRawIdxIdx] : 0.0;
          massVariationByJet.emplace_back(mass);
          if(foundElement)
            lastRawIdxIdx++;
        }
        systematics.push_back(ptVariationByJet);
        massSystematics.push_back(massVariationByJet);
      }
      systematics.insert(systematics.end(), massSystematics.begin(), massSystematics.end());
      for(unsigned short i = 0; i < result.size(); ++i) {
        systematicsNames.push_back("Pt_"+variations[i]);
      }
      for(unsigned short i = 0; i < result.size(); ++i) {
        systematicsNames.push_back("mass_"+variations[i]);
      }
      jetCollection->SetSystematics(std::move(systematicsNames), std::move(systematics));
    }
    
    METSystematicsResult ComputeType1METVariations(CollectionPtr jetCollection, CollectionPtr genJetCollection = nullptr,
        bool isMC=false, bool verbose=false) {
      METVariationsResult result = produceType1METVariations(jetCollection, genJetCollection, isMC);
      std::vector<std::string> variations = available();
      METSystematicsResult returnVal;
      for(unsigned short i = 0; i < result.size(); ++i)
        returnVal["Pt_"+variations[i]] = result.pt(i);
      for(unsigned short i = 0; i < result.size(); ++i) 
        returnVal["Phi_"+variations[i]] = result.phi(i);
      return returnVal;
    }

    METSystematicsResult ComputeFixEE2017Type1METVariations(CollectionPtr jetCollection, CollectionPtr genJetCollection,
        bool isMC=true, bool verbose=false) {
      METVariationsResult result = produceFixEE2017Type1METVariations(jetCollection, genJetCollection, isMC);
      std::vector<std::string> variations = available();
      METSystematicsResult returnVal;
      for(unsigned short i = 0; i < result.size(); ++i)
        returnVal["Pt_"+variations[i]] = result.pt(i);
      for(unsigned short i = 0; i < result.size(); ++i) 
        returnVal["Phi_"+variations[i]] = result.phi(i);
      return returnVal;
    }

    std::vector<std::string> available() {
      return std::visit(
          [](auto& calc)->std::vector<std::string> {
          return calc.available();
          }, m_calc);
    }

    void setAddHEM2018Issue(bool addHEM2018) {
      std::visit(
          [&addHEM2018](auto& calc) {
          calc.setAddHEM2018Issue(addHEM2018);
          }, m_calc);
    }

  private:
    std::string getValueTypeName() const {
      return std::visit( [](auto&&x)->decltype(auto){ return typeid(x).name(); }, m_calc);
    }
    template <typename T = float> T GetValueFromBranchName(const std::string& branchName) {
      return m_data->readerTools_->ReadValueBranch<T>(branchName);
    }
    template <typename T = float> RVec<T> GetRVecFromBranchName(const std::string& branchName) {
      return RVec<T>(static_cast<T*>(m_data->readerTools_->ReadArrayBranch<T>(branchName).GetAddress()),
          m_data->readerTools_->ReadArrayBranch<T>(branchName).GetSize());
    }
    template <typename T = float> RVec<T> GetRVecFromJetCollection(CollectionPtr jetCollection, const std::string& varName) {
      RVec<T> result;
      std::vector<unsigned short> indices = jetCollection->GetRawIndices();
      for(const auto& idx : indices) {
        result.emplace_back(jetCollection->ReadArrayBranch<T>(varName, idx));
      }
      return result;
    }
    JetVariationsResult produceJetVariations(CollectionPtr jetCollection, CollectionPtr genJetCollection, bool isMC=false) {
      bool forMET=false;
      bool isMETFixEE2017=false;
      bool addHEM2018Issue=false;
      std::vector<JetMETArgType> jetArgs = GetJetMETArgs(jetCollection, isMC, forMET, isMETFixEE2017, addHEM2018Issue, genJetCollection);
      return std::get<JetVariationsCalculator>(m_calc).produce(std::get<RVecF >(jetArgs[0]), std::get<RVecF >(jetArgs[1]), std::get<RVecF >(jetArgs[2]),
          std::get<RVecF >(jetArgs[3]),std::get<RVecF >(jetArgs[4]),std::get<RVecF >(jetArgs[5]),
          std::get<RVecI >(jetArgs[6]), std::get<RVecI >(jetArgs[7]),
          std::get<float>(jetArgs[8]),
          std::get<std::uint32_t>(jetArgs[9]),
          std::get<RVecF >(jetArgs[10]), std::get<RVecF >(jetArgs[11]), std::get<RVecF >(jetArgs[12]), std::get<RVecF >(jetArgs[13])
          );
    }

    METVariationsResult produceType1METVariations(CollectionPtr jetCollection, CollectionPtr genJetCollection, bool isMC=false) {
      bool forMET=true;
      bool isMETFixEE2017=false;
      bool addHEM2018Issue=false;
      std::vector<JetMETArgType> metArgs = GetJetMETArgs(jetCollection, isMC, forMET, isMETFixEE2017, addHEM2018Issue, genJetCollection);
      return std::get<Type1METVariationsCalculator>(m_calc).produce(std::get<RVecF >(metArgs[0]), std::get<RVecF >(metArgs[1]), std::get<RVecF >(metArgs[2]),
          std::get<RVecF >(metArgs[3]),std::get<RVecF >(metArgs[4]),std::get<RVecF >(metArgs[5]),
          std::get<RVecI >(metArgs[6]),
          std::get<RVecF >(metArgs[7]),std::get<RVecF >(metArgs[8]),std::get<RVecF >(metArgs[9]),
          std::get<RVecI >(metArgs[10]),
          std::get<float>(metArgs[11]),
          std::get<std::uint32_t>(metArgs[12]),
          std::get<RVecF >(metArgs[13]), std::get<RVecF >(metArgs[14]), std::get<RVecF >(metArgs[15]), std::get<RVecF >(metArgs[16]),
          std::get<float>(metArgs[17]),std::get<float>(metArgs[18]),std::get<float>(metArgs[19]),std::get<float>(metArgs[20]),
          std::get<RVecF >(metArgs[21]), std::get<RVecF >(metArgs[22]), std::get<RVecF >(metArgs[23]), std::get<RVecF >(metArgs[24]),
          std::get<RVecF >(metArgs[25]), std::get<RVecF >(metArgs[26]), std::get<RVecF >(metArgs[27])
          );
    }

    METVariationsResult produceFixEE2017Type1METVariations(CollectionPtr jetCollection, CollectionPtr genJetCollection, bool isMC=false) {
      bool forMET=true;
      bool isMETFixEE2017=true;
      bool addHEM2018Issue=false;
      std::vector<JetMETArgType> metArgs = GetJetMETArgs(jetCollection, isMC, forMET, isMETFixEE2017, addHEM2018Issue, genJetCollection);
      return std::get<FixEE2017Type1METVariationsCalculator>(m_calc).produce(std::get<RVecF >(metArgs[0]), std::get<RVecF >(metArgs[1]), std::get<RVecF >(metArgs[2]),
          std::get<RVecF >(metArgs[3]),std::get<RVecF >(metArgs[4]),std::get<RVecF >(metArgs[5]),
          std::get<RVecI >(metArgs[6]),
          std::get<RVecF >(metArgs[7]),std::get<RVecF >(metArgs[8]),std::get<RVecF >(metArgs[9]),
          std::get<float>(metArgs[10]),
          std::get<std::uint32_t>(metArgs[11]),
          std::get<RVecF >(metArgs[12]), std::get<RVecF >(metArgs[13]), std::get<RVecF >(metArgs[14]), std::get<RVecF >(metArgs[15]),
          std::get<float>(metArgs[16]),std::get<float>(metArgs[17]),std::get<float>(metArgs[18]),std::get<float>(metArgs[19]),
          std::get<RVecF >(metArgs[20]), std::get<RVecF >(metArgs[21]), std::get<RVecF >(metArgs[22]), std::get<RVecF >(metArgs[23]),
          std::get<RVecF >(metArgs[24]), std::get<RVecF >(metArgs[25]), std::get<RVecF >(metArgs[26]),
          std::get<float>(metArgs[27]),std::get<float>(metArgs[28]),std::get<float>(metArgs[29]),std::get<float>(metArgs[30])
          );
    }

  private:
    // reimplemented in C++ from https://gitlab.cern.ch/cp3-cms/CMSJMECalculators/-/blob/main/python/CMSJMECalculators/utils.py#L23
    std::vector<JetMETArgType> GetJetMETArgs(CollectionPtr jetCollection,
        bool isMC=true, bool forMET=false, bool isMETFixEE2017=false, bool addHEM2018Issue=false,
        CollectionPtr genJetCollection = nullptr) {
      std::vector<JetMETArgType> args;
      UInt_t nJet = jetCollection->GetSize();
      args.push_back(GetRVecFromJetCollection(jetCollection, "Jet_pt"));
      RVecF jetEta = GetRVecFromJetCollection(jetCollection, "Jet_eta");
      args.push_back(jetEta);
      args.push_back(GetRVecFromJetCollection(jetCollection, "Jet_phi"));
      args.push_back(GetRVecFromJetCollection(jetCollection, "Jet_mass"));
      args.push_back(GetRVecFromJetCollection(jetCollection, "Jet_rawFactor"));
      args.push_back(GetRVecFromJetCollection(jetCollection, "Jet_area"));
      if(isMC)
        args.push_back(GetRVecFromJetCollection<int>(jetCollection, "Jet_partonFlavour"));
      else
        args.push_back(RVecI());
      if(forMET) {
        args.push_back(GetRVecFromJetCollection(jetCollection, "Jet_muonSubtrFactor"));
        args.push_back(GetRVecFromJetCollection(jetCollection, "Jet_neEmEF"));
        args.push_back(GetRVecFromJetCollection(jetCollection, "Jet_chEmEF"));
      }
      if( !(forMET && isMETFixEE2017) ) {
        if(addHEM2018Issue)
          args.push_back(GetRVecFromJetCollection<int>(jetCollection, "Jet_jetId"));
        else
          args.push_back(RVecI());
      }
      args.push_back(GetValueFromBranchName("fixedGridRhoFastjetAll"));
      if(isMC) {
        UInt_t run = GetValueFromBranchName<UInt_t>("run");
        UInt_t luminosityBlock = GetValueFromBranchName<UInt_t>("luminosityBlock");
        ULong64_t event = GetValueFromBranchName<ULong64_t>("event");
        args.push_back(static_cast<std::uint32_t>((run<<20) + (luminosityBlock<<10) + event + 1 + (nJet != 0 ? int(jetEta[0]/.01) : 0)));
        args.push_back(GetRVecFromJetCollection(genJetCollection, "GenJet_pt"));
        args.push_back(GetRVecFromJetCollection(genJetCollection, "GenJet_eta"));
        args.push_back(GetRVecFromJetCollection(genJetCollection, "GenJet_phi"));
        args.push_back(GetRVecFromJetCollection(genJetCollection, "GenJet_mass"));
      }
      else {
        args.push_back(std::uint32_t(0));
        args.push_back(RVecF());
        args.push_back(RVecF());
        args.push_back(RVecF());
        args.push_back(RVecF());
      }
      if(forMET) {
        args.push_back(GetValueFromBranchName("RawMET_phi"));
        args.push_back(GetValueFromBranchName("RawMET_pt"));
        if(!isMETFixEE2017) {
          args.push_back(GetValueFromBranchName("MET_MetUnclustEnUpDeltaX"));
          args.push_back(GetValueFromBranchName("MET_MetUnclustEnUpDeltaY"));
        }
        else {
          args.push_back(GetValueFromBranchName("METFixEE2017_MetUnclustEnUpDeltaX"));
          args.push_back(GetValueFromBranchName("METFixEE2017_MetUnclustEnUpDeltaY"));
        }
        args.push_back(GetRVecFromBranchName("CorrT1METJet_rawPt"));
        args.push_back(GetRVecFromBranchName("CorrT1METJet_eta"));
        args.push_back(GetRVecFromBranchName("CorrT1METJet_phi"));
        args.push_back(GetRVecFromBranchName("CorrT1METJet_area"));
        args.push_back(GetRVecFromBranchName("CorrT1METJet_muonSubtrFactor"));
        args.push_back(RVecF());
        args.push_back(RVecF());
        if(isMETFixEE2017) {
          args.push_back(GetRVecFromBranchName("MET_phi"));
          args.push_back(GetRVecFromBranchName("MET_pt"));
          args.push_back(GetRVecFromBranchName("METFixEE2017_phi"));
          args.push_back(GetRVecFromBranchName("METFixEE2017_pt"));
        }
      }
      return args;
    }

    void CheckFileExists(std::string& filePath) {
      if(!std::filesystem::exists(filePath)) {
        STDOUT("ERROR: JES/JER file " << filePath << " does not exist! Can't compute uncertainties. Exiting.");
        exit(-8);
      }
    }

    std::variant<JetVariationsCalculator, Type1METVariationsCalculator, FixEE2017Type1METVariationsCalculator> m_calc;
    analysisClass* m_data;

    std::string m_jerTextFilePath, m_ptResTxtFile, m_sfTxtFile;
    bool m_splitJER;
    bool m_doGenMatch;
    float m_genMatchMaxDR;
    float m_genMatchMaxDPt;
};

namespace JMEUtils {



};
