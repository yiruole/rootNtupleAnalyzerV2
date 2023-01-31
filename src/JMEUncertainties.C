#include "Collection.h"
#include "JMESystematicsCalculators.h"
#include <variant>

using namespace ROOT::VecOps;

class JMEUncertainties {
  public:

    typedef std::variant<RVec<float>, RVec<int>, float, std::uint32_t> JetMETArgType;
    typedef JetVariationsCalculator::result_t JetVariationsResult;

    JMEUncertainties(analysisClass & d) :
      m_data (&d) {
        //FIXME TODO how to specify text file paths? probably have to be in cutfiles
        // redo JEC, push_back corrector parameters for different levels
        std::vector<JetCorrectorParameters> jecParams;
        std::string jecTextFilePath = "/afs/cern.ch/user/s/scooper/work/public/Leptoquarks/jecUL/Summer19UL16APV_V7_MC/";
        std::string jerTextFilePath = "/afs/cern.ch/user/s/scooper/work/public/Leptoquarks/jerUL/Summer20UL16APV_JRV3_MC/";
        std::string textFilePath_UncertaintySources = jecTextFilePath + "Summer19UL16APV_V7_MC_UncertaintySources_AK4PFchs.txt";
        std::string textFilePath_PtResolution = jerTextFilePath + "Summer20UL16APV_JRV3_MC_PtResolution_AK4PFchs.txt";
        std::string textFilePath_SF =  jerTextFilePath + "Summer20UL16APV_JRV3_MC_SF_AK4PFchs.txt";
        jecParams.push_back(JetCorrectorParameters(jecTextFilePath+"Summer19UL16APV_V7_MC_L1FastJet_AK4PFchs.txt"));
        jecParams.push_back(JetCorrectorParameters(jecTextFilePath+"Summer19UL16APV_V7_MC_L2Relative_AK4PFchs.txt"));
        jecParams.push_back(JetCorrectorParameters(jecTextFilePath+"Summer19UL16APV_V7_MC_L3Absolute_AK4PFchs.txt"));
        jecParams.push_back(JetCorrectorParameters(jecTextFilePath+"Summer19UL16APV_V7_MC_L2L3Residual_AK4PFchs.txt"));
        m_calc.setJEC(jecParams);
        // calculate JES uncertainties (repeat for all sources)
        //JetCorrectorParameters jcp_unc(textFilePath_UncertaintySources);
        JetCorrectorParameters jcp_unc(textFilePath_UncertaintySources, "Total");
        //TODO: add sources
        m_calc.addJESUncertainty("Total", jcp_unc);
        // Smear jets, with JER uncertainty
        bool splitJER = false;
        m_calc.setSmearing(textFilePath_PtResolution, textFilePath_SF,
            splitJER,       // decorrelate for different regions
            true, 0.2, 3.);  // use hybrid recipe, matching parameters
        //TODO: make options configurable from outside
      }

    void ComputeJetVariations(CollectionPtr jetCollection, bool isMC=true, bool forMET=false, bool isMETFixEE2017=false,
        bool addHEM2018Issue=false, bool verbose=false) {
      JetVariationsResult result = produce(isMC, forMET, isMETFixEE2017, addHEM2018Issue);
      std::vector<std::string> variations = available();
      std::vector<RVec<float> > systematics;
      std::vector<std::string> systematicsNames;
      for(unsigned short i = 0; i < result.size(); ++i) {
        systematics.push_back(result.pt(i));
        systematicsNames.push_back("pt_"+variations[i]);
      }
      for(unsigned short i = 0; i < result.size(); ++i) {
        systematics.push_back(result.mass(i));
        systematicsNames.push_back("mass_"+variations[i]);
      }
      jetCollection->SetSystematics(std::move(systematicsNames), std::move(systematics));
      // TODO will need to handle the RVec<double> types in the MET result...
    }

    template <typename T> RVec<T> GetRVecFromBranchName(const std::string& branchName) {
      return RVec<T>(static_cast<T*>(m_data->readerTools_->ReadArrayBranch<T>(branchName).GetAddress()),
          m_data->readerTools_->ReadArrayBranch<T>(branchName).GetSize());
    }
    RVec<float> GetRVecFloatFromBranchName(const std::string& branchName) {
      return GetRVecFromBranchName<float>(branchName);
    }
    std::vector<std::string> available() {
      return m_calc.available();
    }
    JetVariationsCalculator::result_t produce(bool isMC=true, bool forMET=false, bool isMETFixEE2017=false, bool addHEM2018Issue=false) {
      std::vector<JetMETArgType> jetArgs = GetJetMETArgs(isMC, forMET, isMETFixEE2017, addHEM2018Issue);
      return m_calc.produce(std::get<RVec<float> >(jetArgs[0]), std::get<RVec<float> >(jetArgs[1]), std::get<RVec<float> >(jetArgs[2]),
          std::get<RVec<float> >(jetArgs[3]),std::get<RVec<float> >(jetArgs[4]),std::get<RVec<float> >(jetArgs[5]),
          std::get<RVec<int> >(jetArgs[6]), std::get<RVec<int> >(jetArgs[7]),
          std::get<float>(jetArgs[8]),
          std::get<std::uint32_t>(jetArgs[9]),
          std::get<RVec<float> >(jetArgs[10]), std::get<RVec<float> >(jetArgs[11]), std::get<RVec<float> >(jetArgs[12]), std::get<RVec<float> >(jetArgs[13])
          );
    }
    // reimplemented in C++ from https://gitlab.cern.ch/cp3-cms/CMSJMECalculators/-/blob/main/python/CMSJMECalculators/utils.py#L23
    std::vector<JetMETArgType> GetJetMETArgs(bool isMC=true, bool forMET=false, bool isMETFixEE2017=false, bool addHEM2018Issue=false) {
      std::vector<JetMETArgType> args;
      UInt_t nJet = m_data->readerTools_->ReadValueBranch<UInt_t>("nJet");
      args.push_back(GetRVecFloatFromBranchName("Jet_pt"));
      RVec<float> jetEta = GetRVecFloatFromBranchName("Jet_eta");
      args.push_back(jetEta);
      args.push_back(GetRVecFloatFromBranchName("Jet_phi"));
      args.push_back(GetRVecFloatFromBranchName("Jet_mass"));
      args.push_back(GetRVecFloatFromBranchName("Jet_rawFactor"));
      args.push_back(GetRVecFloatFromBranchName("Jet_area"));
      args.push_back(GetRVecFromBranchName<int>("Jet_partonFlavour"));
      if(forMET) {
        args.push_back(GetRVecFloatFromBranchName("Jet_muonSubtrFactor"));
        args.push_back(GetRVecFloatFromBranchName("Jet_neEmEF"));
        args.push_back(GetRVecFloatFromBranchName("Jet_chEmEF"));
      }
      if( !(forMET && isMETFixEE2017) ) {
        if(addHEM2018Issue)
          args.push_back(GetRVecFromBranchName<int>("Jet_jetId"));
        else
          args.push_back(RVec<int>());
      }
      args.push_back(m_data->readerTools_->ReadValueBranch<float>("fixedGridRhoFastjetAll"));
      if(isMC) {
        UInt_t run = m_data->readerTools_->ReadValueBranch<UInt_t>("run");
        UInt_t luminosityBlock = m_data->readerTools_->ReadValueBranch<UInt_t>("luminosityBlock");
        ULong64_t event = m_data->readerTools_->ReadValueBranch<ULong64_t>("event");
        args.push_back(static_cast<std::uint32_t>((run<<20) + (luminosityBlock<<10) + event + 1 + (nJet != 0 ? int(jetEta[0]/.01) : 0)));
        args.push_back(GetRVecFloatFromBranchName("GenJet_pt"));
        args.push_back(GetRVecFloatFromBranchName("GenJet_eta"));
        args.push_back(GetRVecFloatFromBranchName("GenJet_phi"));
        args.push_back(GetRVecFloatFromBranchName("GenJet_mass"));
      }
      else {
        args.push_back(std::uint32_t(0));
        args.push_back(RVec<float>());
        args.push_back(RVec<float>());
        args.push_back(RVec<float>());
        args.push_back(RVec<float>());
      }
      if(forMET) {
        args.push_back(GetRVecFloatFromBranchName("RawMET_phi"));
        args.push_back(GetRVecFloatFromBranchName("RawMET_pt"));
        if(!isMETFixEE2017) {
          args.push_back(GetRVecFloatFromBranchName("MET_MetUnclustEnUpDeltaX"));
          args.push_back(GetRVecFloatFromBranchName("MET_MetUnclustEnUpDeltaY"));
        }
        else {
          args.push_back(GetRVecFloatFromBranchName("METFixEE2017_MetUnclustEnUpDeltaX"));
          args.push_back(GetRVecFloatFromBranchName("METFixEE2017_MetUnclustEnUpDeltaY"));
        }
        args.push_back(GetRVecFloatFromBranchName("CorrT1METJet_rawPt"));
        args.push_back(GetRVecFloatFromBranchName("CorrT1METJet_eta"));
        args.push_back(GetRVecFloatFromBranchName("CorrT1METJet_phi"));
        args.push_back(GetRVecFloatFromBranchName("CorrT1METJet_area"));
        args.push_back(GetRVecFloatFromBranchName("CorrT1METJet_muonSubtrFactor"));
        args.push_back(RVec<float>());
        args.push_back(RVec<float>());
        if(isMETFixEE2017) {
          args.push_back(GetRVecFloatFromBranchName("MET_phi"));
          args.push_back(GetRVecFloatFromBranchName("MET_pt"));
          args.push_back(GetRVecFloatFromBranchName("METFixEE2017_phi"));
          args.push_back(GetRVecFloatFromBranchName("METFixEE2017_pt"));
        }
      }
      return args;
    }

  private:
		JetVariationsCalculator m_calc;
    analysisClass* m_data;
};

namespace JMEUtils {



};
