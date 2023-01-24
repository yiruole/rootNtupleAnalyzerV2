#ifndef baseClass_h
#define baseClass_h

#include "jsonParser.h"
#include "eventListHelper.h"
#include "TTreeReaderTools.h"

#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <fstream>
#include <stdio.h>
#include <iomanip>
#include <math.h>
#include <stdlib.h>
#include <variant>

#include <TChain.h>
#include <TFile.h>
#include <TH1.h>
#include <TH2F.h>
#include <TH3F.h>
#include <TProfile.h>
#include <TTreeFormula.h>

#include <TMVA/Tools.h>
#include <TMVA/RReader.hxx>

#define STDOUT(STRING) {		   \
  std::cout << __FILE__ <<" - Line "<<__LINE__<<" - "<<__FUNCTION__<<": "<< STRING <<std::endl;   \
}

static const std::string SYSTHISTSUFFIX = "WithSystematics";

class SimpleCut {
  public:
    virtual ~SimpleCut() = default;
    typedef std::variant<float, int, unsigned long long int, unsigned int, unsigned char> ValueType;

    std::string variableName = "";
    int level_int = -1;
    std::string level_str = "";
    bool filled = false;
    bool passed = false;
    bool evaluatedPreviousCuts = false;
    bool passedPreviousCuts = false;
    ValueType value;
    float weight = 1;
    float minValue1 = -999;
    float maxValue1 = -999;
    float minValue2 = -999;
    float maxValue2 = -999;
    char branchType = 'x';
    bool isStatic = false;

    std::string getValueTypeName() const {
      return std::visit( [](auto&&x)->decltype(auto){ return typeid(x).name(); }, value);
    }

    std::string getStringValue() const {
      return std::visit( [](auto&&x)->decltype(auto){ return std::to_string(x); }, value);
    }

    template <typename T>
      const T& getValue() const {
        return std::get<T>(value);
      }

    template <typename T>
      T* getValueAddress() {
        return &std::get<T>(value);
      }

    virtual bool evaluateCut() {
      if(isStatic)
        return true;
      else {
        return std::visit( [this](auto&&val)->bool{
            using T = std::decay_t<decltype(val)>;
            if constexpr (std::is_same_v<float, T>) {
            if(filled && (minValue1 < val && val <= maxValue1
                  || minValue2 < val && val <= maxValue2 ) )
            return true;
            }
            else if constexpr (std::is_same_v<int, T>) {
            if(filled && (minValue1 < val && val <= maxValue1
                  || minValue2 < val && val <= maxValue2 ) )
            return true;
            }
            else if constexpr (std::is_same_v<unsigned long long int, T>) {
            if(filled && (minValue1 < val && val <= maxValue1
                  || minValue2 < val && val <= maxValue2 ) )
            return true;
            }
            else if constexpr (std::is_same_v<unsigned int, T>) {
            if(filled && (minValue1 < val && val <= maxValue1
                  || minValue2 < val && val <= maxValue2 ) )
            return true;
            }
            else if constexpr (std::is_same_v<unsigned char, T>) {
              if(filled && (minValue1 < val && val <= maxValue1
                    || minValue2 < val && val <= maxValue2 ) )
                return true;
            }
            else {
              STDOUT("ERROR: value type '" << getValueTypeName() << "' for saved variable named '" << variableName << "' is not one supported. Must add support for additional branch types.");
              exit(-2);
            }
            return false;

        }, value);
      }
    }

    template <typename T>
      void setValue(const T& newValue) {
        // in this case, we are reading branches only and haven't read the branch once yet
        if(branchType == 'x') {
          if constexpr (std::is_same_v<T, double>)
            value = static_cast<float>(newValue);
          else if constexpr (std::is_same_v<T, bool>)
            value = static_cast<unsigned char>(newValue);
          else
            value = newValue;
          branchType = 'y';
        }
        if constexpr (std::is_same_v<T, double>)
          value = static_cast<float>(newValue);
        else if constexpr (std::is_same_v<T, bool>)
          value = static_cast<unsigned char>(newValue);
        else if (!valueIsType<T>()) {
          std::string varTypeName = getValueTypeName();
          STDOUT("ERROR: Trying to set value of variable " << variableName << " which is of type " << varTypeName << " to a value of different type " << typeid(T).name() << "; can't do this.");
          exit(-10);
        }
        else
          value = newValue;
      }

    template <typename T>
      bool valueIsType() const noexcept {
        return std::holds_alternative<T>(value);
      }

    void resetValue() {
      if(valueIsType<float>()) {
        value = float(0.0);
      }
      else if(valueIsType<int>())
        value = int(0);
      else if(valueIsType<unsigned long long int>())
        value = static_cast<unsigned long long int>(0);
      else if(valueIsType<unsigned int>())
        value = static_cast<unsigned int>(0);
      else if(valueIsType<unsigned char>()) {
        value = static_cast<unsigned char>(0);
      }
      else {
        STDOUT("ERROR: value type '" << getValueTypeName() << "' for saved variable named '" << variableName << "' is not one supported. Must add support for additional branch types.");
        exit(-2);
      }
    }

};

class cut : public SimpleCut {
  public:
    const static size_t MAX_ARRAY_SIZE = 200;
    int histoNBins = 1;
    float histoMin = -999;
    float histoMax = 999;
    bool saveVariableInReducedSkim = false;
    bool saveVariableArrayInReducedSkim = false;
    // Not filled from file
    int id = -999;
    TH1D histo1;
    TH1D histo2;
    TH1D histo3;
    TH1D histo4;
    TH1D histo5;
    TH1D histo6;
    // Filled event by event
    unsigned int arraySize = 0;
    double nEvtInput = -999;
    double nEvtPassedBeforeWeight = -999;
    double nEvtPassed = -999;
    double nEvtPassedErr2 = -999;
    bool nEvtPassedBeforeWeight_alreadyFilled = -999;

    virtual std::vector<std::string> getInputVariableNames() { return std::vector<std::string>(); }
    virtual void setupReader(std::vector<std::shared_ptr<cut> >& inputVariableList) {}
};

class TMVACut : public cut {
  public:
    std::string modelName;
    std::string weightFileName;
    std::vector<std::shared_ptr<cut> > inputVariables;

    std::string readerOptions = "!Color:!Silent";
    std::unique_ptr<TMVA::Reader> reader;
    //std::unique_ptr<TMVA::Experimental::RReader> reader;
    TMVA::Experimental::Internal::XMLConfig xmlConfig;

    bool evaluateCut() override {
      std::string cutsNotFilled;
      for(auto& cut : inputVariables) {
        if(!cut->filled) {
          cutsNotFilled+=cut->variableName+" ";
        }
      }
      if(!cutsNotFilled.empty()) {
          STDOUT("ERROR: Cut(s) " << cutsNotFilled << " was not filled. Cannot evaluate TMVA model.");
          //return false;
          exit(-7);
      }
      weight = (*(inputVariables.begin()))->weight; // FIXME: a bit of a gotcha here. to fix,
      // maybe we need to mark static variables as such so that we don't use them for the weight.
      value = static_cast<float>(reader->EvaluateMVA(modelName));
      filled = true;
      return cut::evaluateCut();
    }

    void setupReader(std::vector<std::shared_ptr<cut> >& inputVariableList) override {
      inputVariables = inputVariableList;
      for(auto& cut : inputVariables)
        reader->AddVariable(cut->variableName, cut->getValueAddress<float>());
      reader->BookMVA(modelName, weightFileName);
    }

    std::vector<std::string> getInputVariableNames() override {
      return xmlConfig.variables;
    }

    TMVACut() = delete;
    TMVACut(const std::string& modelName, const std::string& weightFileName) :
      modelName(modelName), weightFileName(weightFileName) {
        TMVA::Tools::Instance();
        //reader.reset(new TMVA::Experimental::RReader(weightFileName));
        //reader = std::make_unique<TMVA::Experimental::RReader>(weightFileName);
        reader = std::make_unique<TMVA::Reader>(readerOptions);
        xmlConfig = TMVA::Experimental::Internal::ParseXMLConfig(weightFileName);
        branchType = 'F';
        value = float(0.0);
      }
};

struct preCut {
  std::string variableName = "";
  std::string string1 = "";
  std::string string2 = "";
  std::string string3 = "";
  std::string string4 = "";
  float value1 = -999;
  float value2 = -999;
  float value3 = -999;
  float value4 = -999;
  int level_int = -999;
  std::string level_str = "";
};

struct Systematic {
  std::string name = "";
  std::unique_ptr<TTreeFormula> formula;
  std::string regex = "";
  std::map<std::string, std::string> cutNamesToBranchNames;
  std::map<std::string, float> cutNamesToSystValues;
  std::map<std::string, bool> cutNamesToSystFilled;
  int length = 1;
  float value;
  bool filled;

  Systematic(const std::string& systName, int systLength = 1) :
    name(systName), length(systLength), value(0.0), filled(false) {}
  bool affectsCut(std::string cutName) {
    return cutNamesToBranchNames.count(cutName);
  }
};

// Create structure to hold
class Optimize {
  public:
    Optimize(){count=0; variableName=""; minvalue=0; maxvalue=0; testgreater=false; level_int=-10;};
    Optimize(int x0, std::string& x1, double x2, double x3, bool x4, int x5, int x6)
    {
      count=x0;
      variableName=x1;
      minvalue=x2;
      maxvalue=x3;
      nCuts = x6;
      if (minvalue>maxvalue)
      {
        maxvalue=x2;
        minvalue=x3;
      }
      increment=(maxvalue-minvalue)/static_cast<double>(nCuts - 1);
      if (increment<=0)
        increment=1;
      testgreater=x4;
      level_int=x5;
      value=-999999; // dummy start value
    };
    ~Optimize(){};
    int nCuts;
    int count; // store number for ordering of optimization cuts
    std::string variableName; // store name of variable
    double minvalue; // minimum threshold value to test
    double maxvalue; // maximum threshold to test
    double increment; // max-min, divided into 10 parts
    bool testgreater; // tests whether value should be greater or less than threshold
    int level_int; // cut level -- not used?
    double value;  // value to check against threshold

    bool Compare(int counter)
    {
      // compare value to threshold # <counter>

      // if testing that value is greater than some threshold, start with lowest threshold first
      bool passed=false;
      if (testgreater)
      {
        double thresh=minvalue+increment*static_cast<double>(counter); // convert counter # to physical threshold
        value > thresh ? passed=true: passed=false;
      }
      // if testing that value is less than threshold, start with largest threshold first.  This keep the number of \events "monotonically decreasing" over a series of 10 cuts.
      else
      {
        double thresh=maxvalue-increment*static_cast<double>(counter);
        value < thresh ? passed=true : passed = false;
      }
      return passed;
    }; // comparison function
}; // class Optimize


class baseClass {
  public :
    enum CUTLEVELS { SKIM_LEVEL=0 };
    std::map<std::string, bool> combCutName_passed_;

    bool passJSON(int run, int ls, bool isData);
    bool triggerExists   ( const char* name);
    bool triggerFired    ( const char* name );
    int  triggerPrescale ( const char* name );
    void fillTriggerVariable ( const char * hlt_path, const char* variable_name, int extraPrescale=1 ) ;
    void printTriggers();
    void printFiredTriggers();
    void getTriggers(Long64_t entry);
    const std::string& getInputListName() { return *inputList_;};
    const std::string getCurrentFileName() { return tree_->GetCurrentFile()->GetName();};

    void resetCuts(const std::string& s = "newEvent");
    void fillSystVariableWithValue(const std::string&, const std::string&, const float&);
    void fillSystVariableWithValue(const std::string&, const float&);
    template<typename T = float> void fillVariableWithValue(const std::string& s, const T& d, const float& w = 1.)
    {
      auto&& cc = cutName_cut_.find(s);
      if( cc == cutName_cut_.end() )
      {
        STDOUT("ERROR: variableName = "<< s << " not found in cutName_cut_. Exiting.");
        exit(-5);
      }
      else
      {
        cc->second->setValue(d);
        cc->second->filled = true;
        cc->second->weight = w;
      }
      fillOptimizerWithValue(s, d);
    }
    template<typename T = float> void fillVariableWithValue(const std::string& s, TTreeReaderValue<T>& reader, const float& w = 1.)
    {
      fillVariableWithValue(s, *reader, w);
    }
    template<typename T = float> void fillArrayVariableWithValue(const std::string&, float*);
    template <typename T> void fillArrayVariableWithValue(const std::string& s, TTreeReaderArray<T>& reader);
    void evaluateCuts(bool verbose = false);
    template<typename T> void evaluateCuts(std::map<std::string, T>& cutNameToCut, std::map<std::string, bool>& combNameToPassFail, std::vector<std::string>& orderedCutNames, bool verbose = false);

    void fillAllPreviousCuts                ( bool b ) { fillAllPreviousCuts_               = b; } 
    void fillAllOtherCuts                   ( bool b ) { fillAllOtherCuts_                  = b; } 
    void fillAllSameLevelAndLowerLevelCuts  ( bool b ) { fillAllSameLevelAndLowerLevelCuts_ = b; } 
    void fillAllCuts                        ( bool b ) { fillAllCuts_                       = b; } 
    void fillAllSameLevelCuts               ( bool b ) { fillAllSameLevelCuts_              = b; } 

    // need to define these here
    template <typename T> bool passedCut(const std::string& s, std::map<std::string, T>& cutNameToCut, std::map<std::string, bool>& combCutNameToPassed) {
      bool ret = false;
      auto const& cc = cutNameToCut.find(s);
      if( cc != cutNameToCut.end() )
      {
        auto const& c = cc->second;
        return (c->filled && c->passed);
      }
      std::map<std::string, bool>::iterator cp = combCutNameToPassed.find(s);
      if( cp != combCutNameToPassed.end() )
        return ret = cp->second;
      STDOUT("ERROR: did not find variableName = "<<s<<" neither in cutNameToCut nor combCutNameToPassed. Returning false.");
      return (ret=false);
    }
    template <typename T> bool passedAllPreviousCuts(const std::string& s, std::map<std::string, T>& cutNameToCut, std::vector<std::string>& orderedCutNames) {
      auto&& cc = cutNameToCut.find(s);
      if( cc == cutNameToCut.end() ) {
        STDOUT("ERROR: did not find variableName = "<<s<<" in cutNameToCut. Returning false.");
        return false;
      }
      if(!cc->second->evaluatedPreviousCuts) {
        for (auto& cutName : orderedCutNames) {
          auto& c = cutNameToCut.find(cutName)->second;
          if( c->variableName == cc->second->variableName ) {
            cc->second->evaluatedPreviousCuts = true;
            cc->second->passedPreviousCuts = true;
            break;
          }
          else {
            if( ! (c->filled && c->passed) ) {
              cc->second->evaluatedPreviousCuts = true;
              cc->second->passedPreviousCuts = false;
              break;
            }
          }
        }
      }
      return cc->second->passedPreviousCuts;
    }

    template <typename T> bool passedAllOtherCuts(const std::string& s, std::map<std::string, T>& cutNameToCut)
    {
      //STDOUT("Examining variableName = "<<s);
      bool ret = true;

      auto&& cc = cutNameToCut.find(s);
      if( cc == cutNameToCut.end() )
      {
        STDOUT("ERROR: did not find variableName = "<<s<<" in cutNameToCut. Returning false.");
        return false;
      }

      for (auto const& ccl : cutNameToCut)
      {
        auto const& c = ccl.second;
        if( c->variableName == s )
        {
          continue;
        }
        else
        {
          if( ! (c->filled && c->passed) ) return false;
        }
      }
      return ret;
    }

    template <typename T> bool passedAllOtherSameAndLowerLevelCuts(const std::string& s, std::map<std::string, T>& cutNameToCut)
    {
      //STDOUT("Examining variableName = "<<s);
      bool ret = true;
      int cutLevel;
      auto cc = cutNameToCut.find(s);
      if( cc == cutNameToCut.end() )
      {
        STDOUT("ERROR: did not find variableName = "<<s<<" in cutNameToCut. Returning false.");
        return false;
      }
      else
      {
        cutLevel = cc->second->level_int;
      }

      for (auto& ccl : cutNameToCut)
      {
        auto& c = ccl.second;
        if( c->level_int > cutLevel || c->variableName == s )
        {
          continue;
        }
        else
        {
          if( ! (c->filled && c->passed) ) return false;
        }
      }
      return ret;
    }

    template <typename T> bool passedAllCutsAtLevel(const int cutLevel,  const std::map<std::string, T>& cutNameToCut)
    {
      bool ret = true;
      for (auto const& cc : cutNameToCut)
      {
        auto const& c = cc.second;
        if(c->level_int == cutLevel)
        {
          if( ! (c->filled && c->passed) ) return false;
        }
      }
      return ret;
    }

    template <typename T> bool passedAllOtherCutsAtSameLevel(const std::string& s,  const std::map<std::string, T>& cutNameToCut)
    {
      bool ret = true;
      int cutLevel;
      auto cc = cutNameToCut.find(s);
      if( cc == cutNameToCut.end() )
      {
        STDOUT("ERROR: did not find variableName = "<<s<<" in cutNameToCut. Returning false.");
        return false;
      }
      else
      {
        cutLevel = cc->second->level_int;
      }
      for (auto const& ccl :cutNameToCut)
      {
        auto const& c = ccl.second;
        if(c->variableName == s)
          continue;
        if(c->level_int == cutLevel)
        {
          if( ! (c->filled && c->passed) ) return false;
        }
      }
      return ret;
    }

    template <typename T> std::map<std::string, T> getCutsAtLevel(const int cutLevel, const std::map<std::string, T>& cutNameToCut)
    {
      std::map<std::string, T> cutsAtLevel;
      for (auto const& cc : cutNameToCut)
      {
        auto const& c = cc.second;
        if(c->level_int == cutLevel)
          cutsAtLevel.insert(cc);
      }
      return cutsAtLevel;
    }

    std::map<std::string, std::shared_ptr<cut>> getCutsAtLevel(const int cutLevel) { return getCutsAtLevel(cutLevel, cutName_cut_); }

    template <typename T> bool passedSelection(const std::string& s, std::map<std::string, T>& cutNameToCut, std::map<std::string, bool>& combCutNameToPassed, std::vector<std::string>& orderedCutNames) {
      return passedAllPreviousCuts(s, cutNameToCut, orderedCutNames) && passedCut(s, cutNameToCut, combCutNameToPassed);
    }
    template <typename T> bool variableIsFilled(const std::string& s, std::map<std::string, T>& cutNameToCut) const
    {
      auto&& cc = cutNameToCut.find(s);
      if( cc == cutNameToCut.end() )
      {
        STDOUT("ERROR: did not find variableName = "<<s<<" in cutNameToCut. Returning");
      }
      auto const& c = cc->second;
      return c->filled;
    }

    template <typename T> bool hasCut(const std::string& s, std::map<std::string, T>& cutNameToCut, std::map<std::string, bool>& combCutNameToPassed) const
    {
      auto&& cc = cutNameToCut.find(s);
      if( cc != cutNameToCut.end() )
        return true;
      // check the comb map for completeness
      std::map<std::string, bool>::iterator cp = combCutNameToPassed.find(s);
      if( cp != combCutNameToPassed.end() )
        return true;
      return false;
    }
    bool passedCut(const std::string& s) { return passedCut(s, cutName_cut_, combCutName_passed_); }
    bool passedAllPreviousCuts(const std::string& s) { return passedAllPreviousCuts(s, cutName_cut_, orderedCutNames_); }
    bool passedAllOtherCuts(const std::string& s) { return passedAllOtherCuts(s, cutName_cut_); }
    bool passedAllOtherSameAndLowerLevelCuts(const std::string& s) { return passedAllOtherSameAndLowerLevelCuts(s, cutName_cut_); }
    bool passedAllOtherCutsAtSameLevel(const std::string& s) { return passedAllOtherCutsAtSameLevel(s, cutName_cut_); }
    bool passedAllCutsAtLevel(const int cutLevel) { return passedAllCutsAtLevel(cutLevel, cutName_cut_); }
    bool passedSelection(const std::string& s) { return passedAllPreviousCuts(s, cutName_cut_, orderedCutNames_); }
    bool variableIsFilled(const std::string& s) { return variableIsFilled(s, cutName_cut_); }
    bool isSkimCut(const cut& c) { return c.level_int == SKIM_LEVEL; }
    bool hasCut(const std::string& s) { return hasCut(s, cutName_cut_, combCutName_passed_); }
    bool hasPreCut(const std::string& s);
    template <typename T = float> T getVariableValue(const std::string& s)
    {
      auto&& cc = cutName_cut_.find(s);
      if( cc == cutName_cut_.end() )
      {
        STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_.");
        exit(-5);
      }
      auto const& c = cc->second;
      if( !variableIsFilled(s) )
      {
        STDOUT("ERROR: requesting value of not filled variable "<<s);
        exit(-5);
      }
      if(!c->valueIsType<T>()) {
        STDOUT("ERROR: Trying to get value of variable " << s << " which is of type " << c->getValueTypeName() << " and not " << typeid(T).name() << "; can't do this.");
        exit(-5);
      }
      //return *std::get_if<T>(&c.value);
      return c->getValue<T>();
    }
    float getPreCutValue1(const std::string& s);
    float getPreCutValue2(const std::string& s);
    float getPreCutValue3(const std::string& s);
    float getPreCutValue4(const std::string& s);
    std::string getPreCutString1(const std::string& s);
    std::string getPreCutString2(const std::string& s);
    std::string getPreCutString3(const std::string& s);
    std::string getPreCutString4(const std::string& s);
    float getCutMinValue1(const std::string& s);
    float getCutMaxValue1(const std::string& s);
    float getCutMinValue2(const std::string& s);
    float getCutMaxValue2(const std::string& s);

    const TH1D& getHisto_noCuts_or_skim(const std::string& s);
    const TH1D& getHisto_allPreviousCuts(const std::string& s);
    const TH1D& getHisto_allOthrSmAndLwrLvlCuts(const std::string& s);
    const TH1D& getHisto_allOtherCuts(const std::string& s);
    const TH1D& getHisto_allCuts(const std::string& s);

    int    getHistoNBins(const std::string& s);
    float getHistoMin(const std::string& s);
    float getHistoMax(const std::string& s);

    baseClass(std::string * inputList, std::string * cutFile, std::string * treeName, std::string *outputFileName=0, std::string * cutEfficFile=0);
    virtual ~baseClass();

    // Optimization stuff
    void fillOptimizerWithValue(const std::string& s, const float& d);
    void runOptimizer();
    bool isOptimizationEnabled() { return optimizeName_cut_.size()>0; }

    bool haveSystematics() { return !systematics_.empty(); }
    unsigned int getNumSystematics() { return systematics_.size(); }
    void runSystematics();

    void CreateAndFillUserTH1D(const std::string&  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Double_t value, Double_t weight=1, bool systematics=true, std::string selection="");
    void CreateUserTH1D(const std::string&  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, bool systematics=false);
    void CreateUserTH1DWithSysts(const std::string&  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup) { CreateUserTH1D(nameAndTitle, nbinsx, xlow, xup, true); }
    void FillUserTH1D(const std::string&  nameAndTitle, Double_t value, Double_t weight=1, std::string selection="");
    void FillUserTH1D(const std::string&  nameAndTitle, TTreeReaderValue<double>& reader, Double_t weight=1, std::string selection="");
    void CreateAndFillUserTH2D(const std::string&  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup,  Double_t value_x,  Double_t value_y, Double_t weight=1);
    void CreateUserTH2D(const std::string&  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup);
    void CreateUserTH2D(const std::string& nameAndTitle, Int_t nbinsx, Double_t * x, Int_t nbinsy, Double_t * y );
    void FillUserTH2D(const std::string&   nameAndTitle, Double_t value_x,  Double_t value_y, Double_t weight=1);
    void FillUserTH2D(const std::string&  nameAndTitle, TTreeReaderValue<double>& xReader, TTreeReaderValue<double>& yReader, Double_t weight=1);
    void FillUserTH2DLower(const std::string&   nameAndTitle, Double_t value_x,  Double_t value_y, Double_t weight=1);
    void CreateUserTH2DForSysts(const std::string& nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup);
    void CreateAndFillUserTH3D(const std::string&  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup,  Int_t binsz, Double_t zlow, Double_t zup, Double_t value_x,  Double_t value_y, Double_t z, Double_t weight=1);
    void CreateUserTH3D(const std::string&  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup, Int_t nbinsz, Double_t zlow, Double_t zup);
    void CreateUserTH3D(const std::string& nameAndTitle, Int_t nbinsx, Double_t * x, Int_t nbinsy, Double_t * y, Int_t nbinsz, Double_t * z );
    void FillUserTH3D(const std::string&   nameAndTitle, Double_t value_x,  Double_t value_y, Double_t value_z, Double_t weight=1);
    void FillUserTH3D(const std::string&  nameAndTitle, TTreeReaderValue<double>& xReader, TTreeReaderValue<double>& yReader, TTreeReaderValue<double>& zReader, Double_t weight=1);
    void CreateUserTProfile(const std::string&  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup);
    void FillUserTProfile(const std::string&  nameAndTitle, Double_t x, Double_t y, Double_t weight=1);

    void createOptCutFile();

    bool isData();

    Long64_t GetTreeEntries() { return treeEntries_; }
    Long64_t GetCurrentEntry() { return readerTools_->GetCurrentEntry(); }

    bool hasBranch(const std::string& branchName) { return readerTools_->GetTree()->GetBranch(branchName.c_str()); }

    void resetSkimTreeBranchAddress(const std::string& branchName, void* addr);

    TFile * output_root_;

    std::shared_ptr<TTreeReaderTools> readerTools_;

  private :
    int nOptimizerCuts_;
    std::string * configFile_;
    std::string outputFileName_;
    std::string * inputList_;
    std::string * cutFile_;
    std::string * treeName_; // Name of input tree objects in (.root) files
    std::shared_ptr<TChain> tree_; // main tree
    //TTree * tree2_; // tree for globalInfo
    Long64_t readerEntry_;
    Long64_t treeEntries_;
    std::string * cutEfficFile_;
    std::stringstream preCutInfo_;
    std::map<std::string, std::unique_ptr<preCut>> preCutName_cut_;
    std::map<std::string, std::shared_ptr<cut>> cutName_cut_;
    std::vector<std::string> orderedCutNames_;
    std::vector<std::string> orderedSystCutNames_;
    std::map<std::string , std::unique_ptr<TH1D> > userTH1Ds_;
    std::map<std::string , std::unique_ptr<TH2D> > userTH2Ds_;
    std::map<std::string , std::unique_ptr<TH3D> > userTH3Ds_;
    std::map<std::string , std::unique_ptr<TProfile> > userTProfiles_;
    std::map<std::string , std::unique_ptr<TH2D> > user1DHistsWithSysts_;
    void init();
    void readInputList();
    void readCutFile();
    bool fillCutHistos();
    bool writeCutHistos();
    bool writeUserHistos();
    bool updateCutEffic();
    bool writeCutEfficFile();
    bool sortCuts(const cut&, const cut&);
    std::vector<std::string> split(const std::string& s);
    float decodeCutValue(const std::string& s);
    bool skimWasMade_;
    int nPreviousSkimCuts_;
    double getInfoFromHist(const std::string& fileName, const std::string& histName, int bin);
    template <typename T> std::shared_ptr<T> getSavedObjectFromFile(const std::string& fileName, const std::string& histName);
    double getGlobalInfoNstart(const std::string& fileName);
    double getSumGenWeights(const std::string& fileName);
    double getSumTopPtWeights(const std::string& fileName);
    double getTreeEntries(const std::string& fileName);
    double getSumWeightFromRunsTree(const std::string& fName, const std::string& name, int index = -1);
    std::vector<double> getSumArrayFromRunsTree(const std::string& fName, const std::string& name, bool isArrayBranch);
    void saveLHEPdfSumw(const std::string& fileName);
    void saveEventsPassingCuts(const std::string& fileName);
    std::shared_ptr<TProfile> makeNewEventsPassingSkimCutsProfile(const std::shared_ptr<TProfile> prevProfFromFile = 0);
    bool isData_;

    Long64_t NBeforeSkim_;
    double sumGenWeights_;
    double sumTopPtWeights_;

    template <typename T> void checkOverflow(const TH1*, const T);

    // JSON file stuff
    JSONParser jsonParser_;
    bool jsonFileWasUsed_;
    std::string jsonFileName_;

    // Trigger stuff
    std::string oldKey_; 
    std::unordered_set<std::string> triggerNames_;
    std::map<std::string, int > triggerPrescaleMap_; 

    // Which plots to fill
    bool fillAllPreviousCuts_;
    bool fillAllOtherCuts_;
    bool fillAllSameLevelAndLowerLevelCuts_;
    bool fillAllCuts_;
    bool fillAllSameLevelCuts_;

    // Skim stuff
    bool produceSkim_;
    int NAfterSkim_;
    float getSkimPreCutValue(const std::string& s);
    TFile *skim_file_;
    TTree* skim_tree_;
    TH1D* hCount_;
    bool writeSkimTree();
    void fillSkimTree();
    void fillReducedSkimTree();
    void updateBranchList();


    //Reduced Skim stuff
    bool produceReducedSkim_;
    int NAfterReducedSkim_;
    float getReducedSkimPreCutValue(const std::string& s);
    TFile *reduced_skim_file_;
    TTree *reduced_skim_tree_;
    TH1D* hReducedCount_;
    bool writeReducedSkimTree();

    // Optimization stuff
    std::map<int, Optimize> optimizeName_cut_;
    std::shared_ptr<TProfile> eventCuts_; // number of events passing each cut
    std::shared_ptr<TH1D> eventCutsHist_; // number of events passing each cut, in hist
    std::shared_ptr<TH1D> eventCutsEfficHist_; // efficiency of passing each cut, in hist
    TH1D* h_optimizer_; // optimization histogram
    TH1I* h_optimizer_entries_;

    // Other stuff
    TH1D* h_weightSums_; // sums of various weights over all events
    std::vector<std::shared_ptr<TH1> > histsToSave_; // various histograms to save, like LHEPdfWeightSumHist
    std::shared_ptr<TH1> findSavedHist(std::string histName);

    // systematics
    std::vector<Systematic> systematics_;
    TList systFormulas_;
    std::map<std::string, std::shared_ptr<SimpleCut>> systCutName_cut_;
    std::unique_ptr<TH2D> currentSystematicsHist_;
};

#endif

#ifdef baseClass_cxx

#endif // #ifdef baseClass_cxx
