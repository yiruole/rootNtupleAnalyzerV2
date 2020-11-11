#ifndef baseClass_h
#define baseClass_h

#include <TChain.h>
#include <TFile.h>
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
#include <TH1F.h>
#include <TH2F.h>
#include <TH3F.h>
#include <math.h>
#include <stdlib.h>

#define STDOUT(STRING) {		   \
	std::cout << __FILE__ <<" - Line "<<__LINE__<<" - "<<__FUNCTION__<<": "<< STRING <<std::endl;   \
}

using namespace std;

struct cut {
  const static size_t MAX_ARRAY_SIZE = 200;
  string variableName = "";
  float minValue1 = -1;
  float maxValue1 = -1;
  float minValue2 = -1;
  float maxValue2 = -1;
  int level_int = -1;
  string level_str = "";
  int histoNBins = -1;
  float histoMin = -1;
  float histoMax = -1;
  bool saveVariableInReducedSkim = false;
  bool saveVariableArrayInReducedSkim = false;
  // Not filled from file
  int id = -1;
  TH1F histo1;
  TH1F histo2;
  TH1F histo3;
  TH1F histo4;
  TH1F histo5;
  // Filled event by event
  bool filled = false;
  float value = -1;
  unsigned int arraySize = 0;
  float weight = 1;
  bool passed = false;
  float nEvtInput = -1;
  float nEvtPassedBeforeWeight = -1;
  float nEvtPassed = -1;
  float nEvtPassedErr2 = -1;
  bool nEvtPassedBeforeWeight_alreadyFilled = -1;

};

struct preCut {
  string variableName = "";
  string string1 = "";
  string string2 = "";
  string string3 = "";
  string string4 = "";
  float value1 = -1;
  float value2 = -1;
  float value3 = -1;
  float value4 = -1;
  int level_int = -1;
  string level_str = "";
};

// Create structure to hold
class Optimize {
 public:
  Optimize(){count=0; variableName=""; minvalue=0; maxvalue=0; testgreater=false; level_int=-10;};
  Optimize(int x0, string x1, float x2, float x3, bool x4, int x5, int x6)
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
      increment=(maxvalue-minvalue)/(nCuts - 1);
      if (increment<=0)
        increment=1;
      testgreater=x4;
      level_int=x5;
      value=-999999; // dummy start value
    };
  ~Optimize(){};
  int nCuts;
  int count; // store number for ordering of optimization cuts
  string variableName; // store name of variable
  float minvalue; // minimum threshold value to test
  float maxvalue; // maximum threshold to test
  float increment; // max-min, divided into 10 parts
  bool testgreater; // tests whether value should be greater or less than threshold
  int level_int; // cut level -- not used?
  float value;  // value to check against threshold

  bool Compare(int counter)
    {
      // compare value to threshold # <counter>

      // if testing that value is greater than some threshold, start with lowest threshold first
      bool passed=false;
      if (testgreater)
        {
          float thresh=minvalue+increment*counter; // convert counter # to physical threshold
          value > thresh ? passed=true: passed=false;
        }
      // if testing that value is less than threshold, start with largest threshold first.  This keep the number of \events "monotonically decreasing" over a series of 10 cuts.
      else
        {
          float thresh=maxvalue-increment*counter;
          value < thresh ? passed=true : passed = false;
        }
      return passed;
    }; // comparison function
}; // class Optimize


//class baseClass : public rootNtupleClass {
class baseClass {
  public :
  map<string, bool> combCutName_passed_;

  int passJSON(int run, int ls, bool isData);
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
  void fillVariableWithValue(const std::string&, const float&, const float& w = 1.);
  void fillVariableWithValue(const std::string&, TTreeReaderValue<float>&, const float& w = 1.);
  void fillArrayVariableWithValue(const std::string&, float*);
  template <typename T> void fillArrayVariableWithValue(const string& s, TTreeReaderArray<T>& reader);
  void evaluateCuts(bool verbose = false);
  
  void fillSkim                           ( bool b ) { fillSkim_                          = b; } 
  void fillAllPreviousCuts                ( bool b ) { fillAllPreviousCuts_               = b; } 
  void fillAllOtherCuts                   ( bool b ) { fillAllOtherCuts_                  = b; } 
  void fillAllSameLevelAndLowerLevelCuts  ( bool b ) { fillAllSameLevelAndLowerLevelCuts_ = b; } 
  void fillAllCuts                        ( bool b ) { fillAllCuts_                       = b; } 
  
  bool passedCut(const string& s);
  bool passedAllPreviousCuts(const string& s);
  bool passedAllOtherCuts(const string& s);
  bool passedAllOtherSameAndLowerLevelCuts(const string& s);
  bool variableIsFilled(const string& s);
  bool isOptimizationEnabled() { return optimizeName_cut_.size()>0; }
  bool hasCut(const string& s);
  float getVariableValue(const string& s);
  float getPreCutValue1(const string& s);
  float getPreCutValue2(const string& s);
  float getPreCutValue3(const string& s);
  float getPreCutValue4(const string& s);
  string getPreCutString1(const string& s);
  string getPreCutString2(const string& s);
  string getPreCutString3(const string& s);
  string getPreCutString4(const string& s);
  float getCutMinValue1(const string& s);
  float getCutMaxValue1(const string& s);
  float getCutMinValue2(const string& s);
  float getCutMaxValue2(const string& s);

  const TH1F& getHisto_noCuts_or_skim(const string& s);
  const TH1F& getHisto_allPreviousCuts(const string& s);
  const TH1F& getHisto_allOthrSmAndLwrLvlCuts(const string& s);
  const TH1F& getHisto_allOtherCuts(const string& s);
  const TH1F& getHisto_allCuts(const string& s);

  int    getHistoNBins(const string& s);
  float getHistoMin(const string& s);
  float getHistoMax(const string& s);

  baseClass(string * inputList, string * cutFile, string * treeName, string *outputFileName=0, string * cutEfficFile=0);
  virtual ~baseClass();

  // Optimization stuff
  void fillOptimizerWithValue(const string& s, const float& d);
  void runOptimizer();

  void CreateAndFillUserTH1D(const char*  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Double_t value, Double_t weight=1);
  void CreateUserTH1D(const char*  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup);
  void FillUserTH1D(const char*  nameAndTitle, Double_t value, Double_t weight=1);
  void FillUserTH1D(const char*  nameAndTitle, TTreeReaderValue<double>& reader, Double_t weight=1);
  void CreateAndFillUserTH2D(const char*  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup,  Double_t value_x,  Double_t value_y, Double_t weight=1);
  void CreateUserTH2D(const char*  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup);
  void CreateUserTH2D(const char* nameAndTitle, Int_t nbinsx, Double_t * x, Int_t nbinsy, Double_t * y );
  void FillUserTH2D(const char*   nameAndTitle, Double_t value_x,  Double_t value_y, Double_t weight=1);
  void FillUserTH2D(const char*  nameAndTitle, TTreeReaderValue<double>& xReader, TTreeReaderValue<double>& yReader, Double_t weight=1);
  void FillUserTH2DLower(const char*   nameAndTitle, Double_t value_x,  Double_t value_y, Double_t weight=1);
  void CreateAndFillUserTH3D(const char*  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup,  Int_t binsz, Double_t zlow, Double_t zup, Double_t value_x,  Double_t value_y, Double_t z, Double_t weight=1);
  void CreateUserTH3D(const char*  nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup, Int_t nbinsz, Double_t zlow, Double_t zup);
  void CreateUserTH3D(const char* nameAndTitle, Int_t nbinsx, Double_t * x, Int_t nbinsy, Double_t * y, Int_t nbinsz, Double_t * z );
  void FillUserTH3D(const char*   nameAndTitle, Double_t value_x,  Double_t value_y, Double_t value_z, Double_t weight=1);
  void FillUserTH3D(const char*  nameAndTitle, TTreeReaderValue<double>& xReader, TTreeReaderValue<double>& yReader, TTreeReaderValue<double>& zReader, Double_t weight=1);

  void fillSkimTree();
  void fillReducedSkimTree();

  void createOptCutFile();

  bool isData();

  Long64_t GetTreeEntries() { return treeEntries_; }

  bool hasBranch(const std::string& branchName) { return readerTools_->GetTree()->GetBranch(branchName.c_str()); }

  TFile * output_root_;

  std::shared_ptr<TTreeReaderTools> readerTools_;

  private :
  int nOptimizerCuts_;
  string * configFile_;
  string outputFileName_;
  string * inputList_;
  string * cutFile_;
  string * treeName_; // Name of input tree objects in (.root) files
  std::shared_ptr<TChain> tree_; // main tree
  TTree * tree2_; // tree for globalInfo
  Long64_t readerEntry_;
  Long64_t treeEntries_;
  string * cutEfficFile_;
  std::stringstream preCutInfo_;
  map<string, preCut> preCutName_cut_;
  map<string, cut> cutName_cut_;
  vector<string> orderedCutNames_;
  map<std::string , TH1D*> userTH1Ds_;
  map<std::string , TH2D*> userTH2Ds_;
  map<std::string , TH3D*> userTH3Ds_;
  void init();
  void readInputList();
  void readCutFile();
  bool fillCutHistos();
  bool writeCutHistos();
  bool writeUserHistos();
  bool updateCutEffic();
  bool writeCutEfficFile();
  bool sortCuts(const cut&, const cut&);
  vector<string> split(const string& s);
  float decodeCutValue(const string& s);
  bool skimWasMade_;
  double getInfoFromHist(const std::string& fileName, const std::string& histName, int bin);
  double getGlobalInfoNstart(const std::string& fileName);
  double getSumAMCNLOWeights(const std::string& fileName);
  double getSumTopPtWeights(const std::string& fileName);
  double getSumWeightFromRunsTree(const std::string& fName, const std::string& name, int index = -1);
  std::vector<double> getSumArrayFromRunsTree(const std::string& fName, const std::string& name, bool isArrayBranch);
  void saveLHEPdfSumw(const std::string& fileName);
  Long64_t NBeforeSkim_;
  double sumAMCNLOWeights_;
  float sumTopPtWeights_;

  template <typename T> void checkOverflow(const TH1*, const T);

  // JSON file stuff
  JSONParser jsonParser_;
  bool jsonFileWasUsed_;
  std::string jsonFileName_;

  // Trigger stuff
  std::string oldKey_; 
  std::map<std::string, bool> triggerDecisionMap_; 
  std::map<std::string, int > triggerPrescaleMap_; 

  // Which plots to fill
  bool fillSkim_;
  bool fillAllPreviousCuts_;
  bool fillAllOtherCuts_;
  bool fillAllSameLevelAndLowerLevelCuts_;
  bool fillAllCuts_;

  // Skim stuff
  bool produceSkim_;
  int NAfterSkim_;
  float getSkimPreCutValue(const string& s);
  TFile *skim_file_;
  TTree* skim_tree_;
  TH1F* hCount_;
  bool writeSkimTree();

  //Reduced Skim stuff
  bool produceReducedSkim_;
  int NAfterReducedSkim_;
  float getReducedSkimPreCutValue(const string& s);
  TFile *reduced_skim_file_;
  TTree *reduced_skim_tree_;
  TH1F* hReducedCount_;
  bool writeReducedSkimTree();

  // Optimization stuff
  map<int, Optimize> optimizeName_cut_;
  TH1F* eventcuts_; // number of events passing each cut
  TH1F* h_optimizer_; // optimization histogram
  TH1I* h_optimizer_entries_;

  // Other stuff
  TH1F* h_weightSums_; // sums of various weights over all events
  std::vector<std::shared_ptr<TH1> > histsToSave_; // various histograms to save, like LHEPdfWeightSumHist

};

#endif

#ifdef baseClass_cxx

#endif // #ifdef baseClass_cxx
