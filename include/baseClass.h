#ifndef baseClass_h
#define baseClass_h

#include "rootNtupleClass.h"
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <fstream>
#include <stdio.h>
#include <iomanip>
#include <TH1F.h>
#include <math.h>
#include <stdlib.h>

#define STDOUT(STRING) {		   \
	std::cout << __FILE__ <<" - Line "<<__LINE__<<" - "<<__FUNCTION__<<": "<< STRING <<std::endl;   \
}

using namespace std;

struct cut {
  string variableName;
  double minValue1;
  double maxValue1;
  double minValue2;
  double maxValue2;
  int level_int;
  string level_str;
  int histoNBins;
  double histoMin;
  double histoMax;
  // Not filled from file
  int id;
  TH1F histo1;
  TH1F histo2;
  TH1F histo3;
  TH1F histo4;
  TH1F histo5;
  // Filled event by event
  bool filled;
  double value;
  bool passed;
  int nEvtInput;
  int nEvtPassed;
};

struct preCut {
  string variableName;
  double value1;
  double value2;
  double value3;
  double value4;
  int level_int;
  string level_str;
};

// Create structure to hold
class Optimize {
 public:
  Optimize(){count=0; variableName=""; minvalue=0; maxvalue=0; testgreater=false; level_int=-10;};
  Optimize(int x0, string x1, double x2, double x3, bool x4, int x5)
    {
      count=x0;
      variableName=x1;
      minvalue=x2;
      maxvalue=x3;
      if (minvalue>maxvalue)
        {
          maxvalue=x2;
          minvalue=x3;
        }
      increment=(maxvalue-minvalue)/9.;
      if (increment<=0)
        increment=1;
      testgreater=x4;
      level_int=x5;
      value=-999999; // dummy start value
    };
  ~Optimize(){};
  int count; // store number for ordering of optimization cuts
  string variableName; // store name of variable
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
          double thresh=minvalue+increment*counter; // convert counter # to physical threshold
          value > thresh ? passed=true: passed=false;
        }
      // if testing that value is less than threshold, start with largest threshold first.  This keep the number of \events "monotonically decreasing" over a series of 10 cuts.
      else
        {
          double thresh=maxvalue-increment*counter;
          value < thresh ? passed=true : passed = false;
        }
      return passed;
    }; // comparison function
}; // class Optimize


class baseClass : public rootNtupleClass {
  public :
  map<string, bool> combCutName_passed_;

  void resetCuts();
  void fillVariableWithValue(const std::string&, const double&);
  void evaluateCuts();
  bool passedCut(const string& s);
  bool passedAllPreviousCuts(const string& s);
  bool passedAllOtherCuts(const string& s);
  bool passedAllOtherSameAndLowerLevelCuts(const string& s);
  bool variableIsFilled(const string& s);
  double getVariableValue(const string& s);
  double getPreCutValue1(const string& s);
  double getPreCutValue2(const string& s);
  double getPreCutValue3(const string& s);
  double getPreCutValue4(const string& s);
  double getCutMinValue1(const string& s);
  double getCutMaxValue1(const string& s);
  double getCutMinValue2(const string& s);
  double getCutMaxValue2(const string& s);

  const TH1F& getHisto_noCuts_or_skim(const string& s);
  const TH1F& getHisto_allPreviousCuts(const string& s);
  const TH1F& getHisto_allOthrSmAndLwrLvlCuts(const string& s);
  const TH1F& getHisto_allOtherCuts(const string& s);
  const TH1F& getHisto_allCuts(const string& s);

  int    getHistoNBins(const string& s);
  double getHistoMin(const string& s);
  double getHistoMax(const string& s);


  baseClass(string * inputList, string * cutFile, string * treeName, string *outputFileName=0, string * cutEfficFile=0);
  virtual ~baseClass();

  // Optimization stuff
  void fillOptimizerWithValue(const string& s, const double& d);
  void runOptimizer();

  private :
  string * configFile_;
  string * outputFileName_; 
  TFile * output_root_;
  string * inputList_;
  string * cutFile_;
  string * treeName_; // Name of input tree objects in (.root) files
  TTree * tree_; // main tree
  TTree * tree2_; // tree for globalInfo
  string * cutEfficFile_;
  std::stringstream preCutInfo_;
  map<string, preCut> preCutName_cut_;
  map<string, cut> cutName_cut_;
  vector<string> orderedCutNames_; 
  void init();
  void readInputList();
  void readCutFile();
  bool fillCutHistos();
  bool writeCutHistos();
  bool updateCutEffic();
  bool writeCutEfficFile();
  bool sortCuts(const cut&, const cut&);
  vector<string> split(const string& s);
  double decodeCutValue(const string& s);
  bool skimWasMade_;
  int getGlobalInfoNstart( char* );
  int NBeforeSkim_;
  
  // Optimization stuff
  map<int, Optimize> optimizeName_cut_;
  TH1F* eventcuts_; // number of events passing each cut
  TH1F* h_optimizer_; // optimization histogram

};

#endif

#ifdef baseClass_cxx

#endif // #ifdef baseClass_cxx
