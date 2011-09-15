#define analysisClass_cxx
#include "analysisClass.h"
#include <TH2.h>
#include <TH1F.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TLorentzVector.h>
#include <TVector2.h>
#include <TVector3.h>


//-----------------------------

typedef vector<double>::const_iterator myiter;


//-----------------------------

analysisClass::analysisClass(string * inputList, string * cutFile, string * treeName, string * outputFileName, string * cutEfficFile)
  :baseClass(inputList, cutFile, treeName, outputFileName, cutEfficFile)
{
  //STDOUT("analysisClass::analysisClass() was called");
}

analysisClass::~analysisClass()
{
  //STDOUT("analysisClass::~analysisClass() was called");
}

void analysisClass::Loop()
{
  //STDOUT("analysisClass::Loop() begins");
  
  if (fChain == 0) return;
   

  ////////////////////// User's code to get preCut values - BEGIN ///////////////

  //  double eleEta_bar = getPreCutValue1("eleEta_bar");

  ////////////////////// User's code to get preCut values - END /////////////////
    
  Long64_t nentries = fChain->GetEntriesFast();
  STDOUT("analysisClass::Loop(): nentries = " << nentries);   
  
  ////// The following ~7 lines have been taken from rootNtupleClass->Loop() /////
  ////// If the root version is updated and rootNtupleClass regenerated,     /////
  ////// these lines may need to be updated.                                 /////    
  Long64_t nbytes = 0, nb = 0;
  for (Long64_t jentry=0; jentry<nentries;jentry++) { // Begin of loop over events
    //for (Long64_t jentry=0; jentry<10000;jentry++) { // Begin of loop over events
    Long64_t ientry = LoadTree(jentry);
    if (ientry < 0) break;
    nb = fChain->GetEntry(jentry);   nbytes += nb;
    if(jentry < 10 || jentry%1000 == 0) STDOUT("analysisClass::Loop(): jentry = " << jentry);   
    // if (Cut(ientry) < 0) continue;
    
    ////////////////////// User's code to be done for every event - BEGIN ///////////////////////

    if (jentry == 1000) continue;

    double w = 0.1;

    resetCuts();

    for (int i=0; i<1; i++) 
      {
	fillVariableWithValue( "var1", jentry, i==0 ? 1 : 0) ;
	fillVariableWithValue( "var2", jentry, w ) ;
	fillVariableWithValue( "var3", jentry, w ) ;
	evaluateCuts();
	resetCuts("sameEvent");
      }

        
    ////////////////////// User's code to be done for every event - END ///////////////////////
    
  } // End of loop over events
  

  
  
  //STDOUT("analysisClass::Loop() ends");   
}
