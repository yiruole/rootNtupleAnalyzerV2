#define analysisClass_cxx
#include "analysisClass.h"
#include <TH2.h>
#include <TH1F.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TLorentzVector.h>
#include <TVector2.h>
#include <TVector3.h>

analysisClass::analysisClass(string * inputList, string * cutFile, string * treeName, string * outputFileName, string * cutEfficFile)
  :baseClass(inputList, cutFile, treeName, outputFileName, cutEfficFile)
{
  std::cout << "analysisClass::analysisClass(): begins " << std::endl;

  std::cout << "analysisClass::analysisClass(): ends " << std::endl;
}

analysisClass::~analysisClass()
{
  std::cout << "analysisClass::~analysisClass(): begins " << std::endl;

  std::cout << "analysisClass::~analysisClass(): ends " << std::endl;
}

void analysisClass::Loop()
{
   std::cout << "analysisClass::Loop() begins" <<std::endl;   
    
   if (fChain == 0) return;
   
   //////////book histos here

#ifdef USE_EXAMPLE
   STDOUT("WARNING: using example code. In order NOT to use it, comment line that defines USE_EXAMPLE flag in Makefile.");   
   // number of electrons
   TH1F *h_nEleFinal = new TH1F ("h_nEleFinal","",11,-0.5,10.5);
   h_nEleFinal->Sumw2();
   //pT 1st ele
   TH1F *h_pT1stEle = new TH1F ("h_pT1stEle","",100,0,1000);
   h_pT1stEle->Sumw2();
   //pT 2nd ele
   TH1F *h_pT2ndEle = new TH1F ("h_pT2ndEle","",100,0,1000);
   h_pT2ndEle->Sumw2();

#endif //end of USE_EXAMPLE

   /////////initialize variables

   Long64_t nentries = fChain->GetEntriesFast();
   std::cout << "analysisClass::Loop(): nentries = " << nentries << std::endl;   

   ////// The following ~7 lines have been taken from rootNtupleClass->Loop() /////
   ////// If the root version is updated and rootNtupleClass regenerated,     /////
   ////// these lines may need to be updated.                                 /////    
   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
     Long64_t ientry = LoadTree(jentry);
     if (ientry < 0) break;
     nb = fChain->GetEntry(jentry);   nbytes += nb;
     if(jentry < 10 || jentry%1000 == 0) std::cout << "analysisClass::Loop(): jentry = " << jentry << std::endl;   
     // if (Cut(ientry) < 0) continue;

     ////////////////////// User's code starts here ///////////////////////

     ///Stuff to be done every event

#ifdef USE_EXAMPLE
     // Electrons
     vector<int> v_idx_ele_final;
     for(int iele=0;iele<ElectronPt->size();iele++)
       {
	 // ECAL barrel fiducial region
	 bool pass_ECAL_FR=false;
	 if( fabs(ElectronEta->at(iele)) < getPreCutValue1("eleFidRegion") )	v_idx_ele_final.push_back(iele);
       }     

     // Set the evaluation of the cuts to false and clear the variable values and filled status
     resetCuts();
     
     // Set the value of the variableNames listed in the cutFile to their current value
     fillVariableWithValue("nEleFinal", v_idx_ele_final.size()) ;
     if( v_idx_ele_final.size() >= 1 ) 
       {
	 fillVariableWithValue( "pT1stEle", ElectronPt->at(v_idx_ele_final[0]) );
       }
     if( v_idx_ele_final.size() >= 2 ) 
       {
	 fillVariableWithValue( "pT2ndEle", ElectronPt->at(v_idx_ele_final[1]) );
	 // Calculate Mee
	 TLorentzVector v_ee, ele1, ele2;
	 ele1.SetPtEtaPhiM(ElectronPt->at(v_idx_ele_final[0]),ElectronEta->at(v_idx_ele_final[0]),ElectronPhi->at(v_idx_ele_final[0]),0);
	 ele2.SetPtEtaPhiM(ElectronPt->at(v_idx_ele_final[1]),ElectronEta->at(v_idx_ele_final[1]),ElectronPhi->at(v_idx_ele_final[1]),0);
	 v_ee = ele1 + ele2;
	 fillVariableWithValue( "invMass_ee", v_ee.M() ) ;
       }

     // Evaluate cuts (but do not apply them)
     evaluateCuts();

     // optional call to fill a skim with the full content of the input roottuple
     if( passedCut("nEleFinal") ) fillSkimTree();     

     // optional call to fill a skim with a subset of the variables defined in the cutFile (use flag SAVE)
     if( passedCut("nEleFinal") ) fillReducedSkimTree();     
     
     // Fill histograms and do analysis based on cut evaluation
     h_nEleFinal->Fill(v_idx_ele_final.size());
     //if( v_idx_ele_final.size()>=1 ) h_pT1stEle->Fill(elePt[v_idx_ele_final[0]]);
     //if( v_idx_ele_final.size()>=2 && (elePt[v_idx_ele_final[0]])>85 ) h_pT2ndEle->Fill(elePt[v_idx_ele_final[1]]);
     if( passedCut("pT1stEle") ) h_pT1stEle->Fill(ElectronPt->at(v_idx_ele_final[0]));
     if( passedCut("pT2ndEle") ) h_pT2ndEle->Fill(ElectronPt->at(v_idx_ele_final[1]));
     
     // retrieve value of previously filled variables (after making sure that they were filled)
     double totpTEle;
     if ( variableIsFilled("pT1stEle") && variableIsFilled("pT2ndEle") ) 
       totpTEle = getVariableValue("pT1stEle")+getVariableValue("pT2ndEle");

     // reject events that did not pass level 0 cuts
     if( !passedCut("0") ) continue;
     // ......
     
     // reject events that did not pass level 1 cuts
     if( !passedCut("1") ) continue;
     // ......

     // reject events that did not pass the full cut list
     if( !passedCut("all") ) continue;
     // ......

#endif  // end of USE_EXAMPLE


     ////////////////////// User's code ends here ///////////////////////

   } // End loop over events

   //////////write histos 

#ifdef USE_EXAMPLE
   STDOUT("WARNING: using example code. In order NOT to use it, comment line that defines USE_EXAMPLE flag in Makefile.");   

   h_nEleFinal->Write();
   h_pT1stEle->Write();
   h_pT2ndEle->Write();

   //pT of both electrons, to be built using the histograms produced automatically by baseClass
   TH1F * h_pTElectrons = new TH1F ("h_pTElectrons","", getHistoNBins("pT1stEle"), getHistoMin("pT1stEle"), getHistoMax("pT1stEle"));
   h_pTElectrons->Add( & getHisto_noCuts_or_skim("pT1stEle") ); // all histos can be retrieved, see other getHisto_xxxx methods in baseClass.h
   h_pTElectrons->Add( & getHisto_noCuts_or_skim("pT2ndEle") );
   //one could also do:  *h_pTElectrons = getHisto_noCuts_or_skim("pT1stEle") + getHisto_noCuts_or_skim("pT2ndEle");
   h_pTElectrons->Write();
   //one could also do:   const TH1F& h = getHisto_noCuts_or_skim// and use h
#endif // end of USE_EXAMPLE
   std::cout << "analysisClass::Loop() ends" <<std::endl;   
}
