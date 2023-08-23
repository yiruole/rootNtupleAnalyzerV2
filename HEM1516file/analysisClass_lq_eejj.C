#define analysisClass_cxx
#define USE_SINGLE_ELE_REDUCED_NTUPLE
#include "analysisClass.h"
#include <assert.h>
#include <memory>

#include <TH2.h>
#include <TH1F.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TLorentzVector.h>
#include <TVector2.h>
#include <TVector3.h>
#include <TProfile.h>
// for scale factors
#include "ElectronScaleFactors.C"
#include "MuonScaleFactors.C"

float GetMeejj(float Ele1_Pt, float Ele2_Pt, float Jet1_Pt, float Jet2_Pt,
    float Ele1_Eta, float Ele2_Eta, float Jet1_Eta, float Jet2_Eta,
    float Ele1_Phi, float Ele2_Phi, float Jet1_Phi, float Jet2_Phi) {
     TLorentzVector e1, j1, e2, j2;
     TLorentzVector eejj;
     e1.SetPtEtaPhiM ( Ele1_Pt, Ele1_Eta, Ele1_Phi, 0.0 );
     e2.SetPtEtaPhiM ( Ele2_Pt, Ele2_Eta, Ele2_Phi, 0.0 );
     j1.SetPtEtaPhiM ( Jet1_Pt, Jet1_Eta, Jet1_Phi, 0.0 );
     j2.SetPtEtaPhiM ( Jet2_Pt, Jet2_Eta, Jet2_Phi, 0.0 );
     eejj = e1 + e2 + j1 + j2 ;
     return eejj.M();
}

analysisClass::analysisClass(string * inputList, string * cutFile, string * treeName, string * outputFileName, string * cutEfficFile)
  :baseClass(inputList, cutFile, treeName, outputFileName, cutEfficFile){}

analysisClass::~analysisClass(){}

void analysisClass::Loop()
{
   std::cout << "analysisClass::Loop() begins" <<std::endl;

   //--------------------------------------------------------------------------
   // Final selection mass points
   //--------------------------------------------------------------------------
   const int n_lq_mass = 11;
   int LQ_MASS[n_lq_mass] = {
     1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000
   };
   ////const int n_lq_mass = 30; // 2017
   //const int n_lq_mass = 29; // 2016
   //int LQ_MASS[n_lq_mass] = {
   //  300,  400,  500,  600,
   //  700,  800,  900,  1000,
   //  1100, 1200, 1300, 1400,
   //  1500, 1600, 1700, 1800,
   //  //1900, 2000, // up to 2000 only for 2018
   //  1900, 2000, 2100, 2200, // 2017-2018
   //  2300, 2400, //2500, // 2500 for 2016 missing, FIXME
   //  //2300, 2400, 2500, // 2017
   //  2600, 2700, 2800, 2900,
   //  3000,
   //  3500, 4000
   //};

   //const int n_lq_mass = 18; // 2018
   //int LQ_MASS[n_lq_mass] = {
   //  300,  400,  500,  600,
   //  700,  800,  900,  1000,
   //  1100, 1200, 1300, 1400,
   //  1500, 1600, 1700, 1800,
   //  1900, 2000
   //};

   // SIC only look at LQ650 selection for now
   // LQ650 only 2012
   //const int n_lq_mass = 1;
   //int LQ_MASS[n_lq_mass] = {
   //   650
   //};

   // turn off totally for optimization
   //const int n_lq_mass = 0;
   //int LQ_MASS[n_lq_mass];

   std::vector<bool> passed_vector;

   char cut_name[100];

   //--------------------------------------------------------------------------
   // Decide which plots to save (default is to save everything)
   //--------------------------------------------------------------------------

   fillAllPreviousCuts              ( true  ) ;
   fillAllOtherCuts                 ( true  ) ;
   fillAllSameLevelAndLowerLevelCuts( !true  ) ;
   fillAllCuts                      ( !true  ) ;

   bool do_roi_plots = false;
   //--------------------------------------------------------------------------
   // Any extra features
   //--------------------------------------------------------------------------

   CreateUserTProfile("run_vs_nvtx_HLT", 164900, 160300, 325200);
   CreateUserTProfile("run_vs_nvtx_PAS", 164900, 160300, 325200);

   //--------------------------------------------------------------------------
   // Get pre-cut values
   //--------------------------------------------------------------------------
   // eta boundaries
   double eleEta_bar_max = getPreCutValue1("eleEta_bar");
   double eleEta_end_min = getPreCutValue1("eleEta_end1");
   double eleEta_end_max = getPreCutValue2("eleEta_end2");


   // eta boundaries
   double eleEta_bar            = getPreCutValue1("eleEta_bar");
   double eleEta_end1_min       = getPreCutValue1("eleEta_end1");
   double eleEta_end1_max       = getPreCutValue2("eleEta_end1");
   double eleEta_end2_min       = getPreCutValue1("eleEta_end2");
   double eleEta_end2_max       = getPreCutValue2("eleEta_end2");

   //--------------------------------------------------------------------------
   // Analysis year
   //--------------------------------------------------------------------------
   int analysisYear = getPreCutValue1("AnalysisYear");

   //--------------------------------------------------------------------------
   // B-tag stuff
   //--------------------------------------------------------------------------
   std::string btagAlgo = getPreCutString1("BTagAlgo");
   std::string btagWP = getPreCutString1("BTagWP");
   double btagCut = getPreCutValue1("BTagCutValue");

   //--------------------------------------------------------------------------
   // BDT weight file
   //--------------------------------------------------------------------------
   std::string bdtWeightFileName = "";
   bool evaluateBDT = false;
   if(hasPreCut("BDTWeightFileName")) {
       bdtWeightFileName = getPreCutString1("BDTWeightFileName");
       evaluateBDT = true;
   }

   //--------------------------------------------------------------------------
   // Create hists
   //--------------------------------------------------------------------------

   CreateUserHist( "sTfrac_Jet1_PAS"                 ,   100    ,  0.0    , 1.0      );
   CreateUserHist( "sTfrac_Jet2_PAS"                 ,   100    ,  0.0    , 1.0      );
   CreateUserHist( "sTfrac_Ele1_PAS"                 ,   100    ,  0.0    , 1.0      );
   CreateUserHist( "sTfrac_Ele2_PAS"                 ,   100    ,  0.0    , 1.0      );
   CreateUserHist( "sTfrac_Jet_PAS"                  ,   100    ,  0.0    , 1.0      );
   CreateUserHist( "sTfrac_Ele_PAS"                  ,   100    ,  0.0    , 1.0      );
   CreateUserHist( "sTfrac_Jet1_PASandMee100"        ,   100    ,  0.0    , 1.0      );
   CreateUserHist( "sTfrac_Jet2_PASandMee100"        ,   100    ,  0.0    , 1.0      );
   CreateUserHist( "sTfrac_Ele1_PASandMee100"        ,   100    ,  0.0    , 1.0      );
   CreateUserHist( "sTfrac_Ele2_PASandMee100"        ,   100    ,  0.0    , 1.0      );
   CreateUserHist( "sTfrac_Jet_PASandMee100"         ,   100    ,  0.0    , 1.0      );
   CreateUserHist( "sTfrac_Ele_PASandMee100"         ,   100    ,  0.0    , 1.0      );
   CreateUserHist( "Mej_selected_avg_PASandMee100"   ,    200   , 0       , 2000     );
   CreateUserHist( "EleChargeSum_PAS"                ,    3     , -2.5    , 2.5      );
   CreateUserHist( "EleChargeSum_PASandMee100"       ,    3     , -2.5    , 2.5      );
   //CreateUserHist( "ProcessID"                       ,    21    , -0.5    , 20.5     );
   //CreateUserHist( "ProcessID_PAS"                   ,    21    , -0.5    , 20.5     );
   //CreateUserHist( "ProcessID_ZWindow"               ,    21    , -0.5    , 20.5     );
   CreateUserHistWithSysts( "nElectron_PAS"                   ,    5     , -0.5    , 4.5      );
   CreateUserHistWithSysts( "nMuon_PAS"                       ,    5     , -0.5    , 4.5      );
   CreateUserHistWithSysts( "nJet_PAS"                        ,    10    , -0.5    , 9.5      );
   CreateUserHist( "nJet_PASandMee100"               ,    10    , -0.5    , 9.5      );
   CreateUserHistWithSysts( "Pt1stEle_PAS"                 ,     100    , 0       , 1000     );
   //CreateUserHist( "PtHeep1stEle_PAS"                 ,     100    , 0       , 1000     );
   CreateUserHist( "Pt1stEle_PASandMee100"           ,     100    , 0       , 1000     );
   CreateUserHistWithSysts( "Eta1stEle_PAS"                 ,     100    , -5      , 5      );
   CreateUserHistWithSysts( "SCEta1stEle_PAS"                 ,     100    , -5      , 5      );
   CreateUserHist( "DeltaEtaEleTrk1stEle_Presel", 400, -0.5,   0.5 );
   CreateUserHistWithSysts( "Phi1stEle_PAS"                 ,     60     , -3.1416 , +3.1416  );
   CreateUserHistWithSysts( "Pt2ndEle_PAS"                 ,     300    , 0       , 3000     );
   //CreateUserHist( "PtHeep2ndEle_PAS"                 ,     300    , 0       , 3000     );
   CreateUserHist( "Pt2ndEle_PASandMee100"           ,     300    , 0       , 3000     );
   CreateUserHistWithSysts( "Eta2ndEle_PAS"                 ,     100    , -5      , 5      );
   CreateUserHistWithSysts( "SCEta2ndEle_PAS"                 ,     100    , -5      , 5      );
   CreateUserHist( "DeltaEtaEleTrk2ndEle_Presel", 400, -0.5,   0.5 );
   CreateUserHistWithSysts( "Phi2ndEle_PAS"                 ,     60     , -3.1416 , +3.1416  );
   CreateUserHist( "Charge1stEle_PAS"                 ,     2      , -1.0001 , 1.0001      );
   CreateUserHist( "Charge2ndEle_PAS"                 ,     2      , -1.0001 , 1.0001      );
   CreateUserHistWithSysts( "MET_PAS"                         ,    200   , 0       , 1000      );
   CreateUserHistWithSysts( "METPhi_PAS"                     ,     60     , -3.1416 , +3.1416  );
   CreateUserHistWithSysts( "Pt1stJet_PAS"                    ,    200   , 0       , 2000      );
   CreateUserHistWithSysts( "Pt2ndJet_PAS"                    ,    200   , 0       , 2000      );
   CreateUserHist( "Pt1stJet_PASandMee100"           ,    200   , 0       , 2000      );
   CreateUserHist( "Pt2ndJet_PASandMee100"           ,    200   , 0       , 2000      );
   CreateUserHistWithSysts( "Eta1stJet_PAS"                   ,    100   , -5      , 5      );
   CreateUserHistWithSysts( "Eta2ndJet_PAS"                   ,    100   , -5      , 5      );
   CreateUserHistWithSysts( "Phi1stJet_PAS"                 ,      60    , -3.1416 , +3.1416  );
   CreateUserHistWithSysts( "Phi2ndJet_PAS"                 ,      60    , -3.1416 , +3.1416  );
   CreateUserHistWithSysts( "sTlep_PAS"                       ,    200   , 0       , 2000      );
   CreateUserHist( "sTlep_PASandMee100"              ,    200   , 0       , 2000      );
   CreateUserHistWithSysts( "sTjet_PAS"                       ,    200   , 0       , 2000      );
   CreateUserHist( "sTjet_PASandMee100"              ,    200   , 0       , 2000      );
   CreateUserHistWithSysts( "sT_PAS"                          ,    300   , 0       , 3000      );
   CreateUserHist( "sT_zjj_PAS"                      ,    300   , 0       , 3000      );
   CreateUserHist( "sT_zjj_PASandMee100"             ,    300   , 0       , 3000      );
   CreateUserHist( "sT_PASandMee100"                 ,    200   , 0       , 2000      );
   CreateUserHist( "sT_PASandMee110"                 ,    200   , 0       , 2000      );
   CreateUserHist( "sT_PASandMee120"                 ,    200   , 0       , 2000      );
   CreateUserHist( "sT_PASandMee130"                 ,    200   , 0       , 2000      );
   CreateUserHist( "sT_PASandMee140"                 ,    200   , 0       , 2000      );
   CreateUserHist( "sT_PASandMee150"                 ,    200   , 0       , 2000      );
   CreateUserHist( "sT_PASandMee160"                 ,    200   , 0       , 2000      );
   CreateUserHist( "sT_PASandMee170"                 ,    200   , 0       , 2000      );
   CreateUserHist( "sT_PASandMee180"                 ,    200   , 0       , 2000      );
   CreateUserHist( "sT_PASandMee190"                 ,    200   , 0       , 2000      );
   CreateUserHist( "sT_PASandMee200"                 ,    200   , 0       , 2000      );
   CreateUserHist( "Mjj_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mjj_PASandMee100"                 ,    200   , 0       , 2000      );
   CreateUserHistWithSysts( "Mee_PAS"                     ,    2000   , 0       , 2000      );
   CreateUserHist( "Mee_PASandST445"                 ,    2000   , 0       , 2000      );
   CreateUserHist( "MTenu_PAS"                       ,    200   , 0       , 1000      );
   CreateUserHistWithSysts( "Me1j1_PAS"                       ,    200   , 0       , 2000      );
   CreateUserHistWithSysts( "Me1j2_PAS"                       ,    200   , 0       , 2000      );
   CreateUserHistWithSysts( "Me2j1_PAS"                       ,    200   , 0       , 2000      );
   CreateUserHistWithSysts( "Me2j2_PAS"                       ,    200   , 0       , 2000      );
   CreateUserHistWithSysts( "Me1j_selected_PAS"               ,    200   , 0       , 2000      );
   CreateUserHistWithSysts( "Me2j_selected_PAS"               ,    200   , 0       , 2000   );
   CreateUserHistWithSysts( "Mej_selected_avg_PAS"            ,    200   , 0       , 2000   );
   CreateUserHistWithSysts( "Mej_selected_min_PAS"            ,    200   , 0       , 2000   );
   CreateUserHistWithSysts( "Mej_selected_max_PAS"            ,    200   , 0       , 2000   );
   CreateUserHistWithSysts( "Mej_asym_PAS"                    ,    50    , 0       , 1   );
   CreateUserHistWithSysts( "Mej_minmax_PAS"                  ,    200   , 0       , 2000   );
   CreateUserHistWithSysts( "Meejj_PAS"                       ,    400   , 0       , 4000   );
   CreateUserHist( "Mejj_PAS"                        ,    400   , 0       , 4000   );
   CreateUserHist( "Meej_PAS"                        ,    400   , 0       , 4000   );
   CreateUserHist( "run_PAS"                         ,    164900 , 160300  , 325200 );
   CreateUserHist( "run_HLT"                         ,    164900 , 160300  , 325200 );

   CreateUserHist( "Ptj1j2j3_PAS"                    ,    400 , 0       , 4000     );
   CreateUserHist( "Ptj1j2_PAS"                      ,    400 , 0       , 4000     );
   CreateUserHist( "Ptj2j3_PAS"                      ,    400 , 0       , 4000     );
   CreateUserHist( "Ptj1j3_PAS"                      ,    400 , 0       , 4000     );

   CreateUserHist( "Ptee_Minus_Ptj1j2_PAS"           ,    200 , -500    , 500      );
   CreateUserHist( "Ptee_Minus_Ptj1j2j3_PAS"         ,    200 , -500    , 500      );
   CreateUserHist( "Ptj1j2j3_PASandMee100"           ,    200 , 0       , 2000     );
   CreateUserHist( "Ptj1j2_PASandMee100"             ,    200 , 0       , 2000     );
   CreateUserHist( "Ptj2j3_PASandMee100"             ,    200 , 0       , 2000     );
   CreateUserHist( "Ptj1j3_PASandMee100"             ,    200 , 0       , 2000     );
   CreateUserHist( "Ptee_Minus_Ptj1j2_PASandMee100"  ,    200 , -500    , 500      );
   CreateUserHist( "Ptee_Minus_Ptj1j2j3_PASandMee100",    200 , -500    , 500      );
   CreateUserHistWithSysts( "Ptee_PAS"                        ,    200 , 0       , 2000     );
   CreateUserHist( "Ptee_PASandMee100"               ,    200 , 0       , 2000     );

   CreateUserHist( "M_j1j3_PAS"                      ,    200 , 0       , 2000     );
   CreateUserHist( "M_j2j3_PAS"                      ,    200 , 0       , 2000     );
   CreateUserHist( "M_e1j3_PAS"                      ,    200 , 0       , 2000     );
   CreateUserHist( "M_e2j3_PAS"                      ,    200 , 0       , 2000     );
   CreateUserHist( "M_eejjj_PAS"                     ,    500 , 0       , 5000     );

   CreateUserHist( "Me1j1_PASandMee100"             ,    200 , 0       , 2000   );
   CreateUserHist( "Me1j2_PASandMee100"             ,    200 , 0       , 2000   );
   CreateUserHist( "Me2j1_PASandMee100"             ,    200 , 0       , 2000   );
   CreateUserHist( "Me2j2_PASandMee100"             ,    200 , 0       , 2000   );

   CreateUserHist( "M_j1j3_PASandMee100"             ,    200 , 0       , 2000     );
   CreateUserHist( "M_j2j3_PASandMee100"             ,    200 , 0       , 2000     );
   CreateUserHist( "M_e1j3_PASandMee100"             ,    200 , 0       , 2000     );
   CreateUserHist( "M_e2j3_PASandMee100"             ,    200 , 0       , 2000     );
   CreateUserHist( "M_eejjj_PASandMee100"            ,    500 , 0       , 5000     );

   CreateUserHistWithSysts( "nVertex_PAS"                     ,    101   , -0.5   , 100.5     ) ;
   CreateUserHist( "nVertex_PASandMee100"            ,    101   , -0.5   , 100.5     ) ;

   CreateUserHistWithSysts( "DR_Ele1Jet1_PAS"       ,     getHistoNBins("DR_Ele1Jet1"), getHistoMin("DR_Ele1Jet1"), getHistoMax("DR_Ele1Jet1")     ) ;
   CreateUserHistWithSysts( "DR_Ele1Jet2_PAS"       ,     getHistoNBins("DR_Ele1Jet2"), getHistoMin("DR_Ele1Jet2"), getHistoMax("DR_Ele1Jet2")     ) ;
   CreateUserHistWithSysts( "DR_Ele2Jet1_PAS"       ,     getHistoNBins("DR_Ele2Jet1"), getHistoMin("DR_Ele2Jet1"), getHistoMax("DR_Ele2Jet1")     ) ;
   CreateUserHistWithSysts( "DR_Ele2Jet2_PAS"       ,     getHistoNBins("DR_Ele2Jet2"), getHistoMin("DR_Ele2Jet2"), getHistoMax("DR_Ele2Jet2")     ) ;
   CreateUserHistWithSysts( "DR_Jet1Jet2_PAS"       ,     getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
   CreateUserHistWithSysts( "DR_Ele1Ele2_PAS"       ,     getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
   CreateUserHist( "minDR_EleJet_PAS"       ,     getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
   CreateUserHist( "minDR_ZJet_PAS"        ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;

   CreateUserHist( "DR_ZJet1_PAS"        ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
   CreateUserHist( "DR_ZJet2_PAS"        ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;

   CreateUserTH2D( "MeeVsST_PAS"                 ,     400, 0, 4000, 400, 0, 4000) ;
   CreateUserTH2D( "MeeVsST_PASandMee100"        ,     400, 0, 4000, 400, 0, 4000) ;
   CreateUserTH2D( "MeeVsPtee_PAS"                 ,     400, 0, 4000, 400, 0, 4000) ;

   CreateUserTH2D( "Me1jVsMe2j_selected",     200, 0, 2000, 200, 0, 2000) ;
   CreateUserTH2D( "Me1jVsMe2j_rejected",     200, 0, 2000, 200, 0, 2000) ;

   CreateUserHist( "MTeemunu_PAS"          ,    200 , 0       , 1000     );

   CreateUserHist( "Mee_80_100_Preselection", 200, 60, 120 );
   CreateUserHist( "Mee_70_110_Preselection", 200, 60, 120 );
   CreateUserHist( "Mee_70_110_ST600_Preselection", 200, 60, 120 );

   CreateUserHist( "Mee_70_110_Preselection_Process0", 200, 60, 120 );
   CreateUserHist( "Mee_70_110_Preselection_Process1", 200, 60, 120 );
   CreateUserHist( "Mee_70_110_Preselection_Process2", 200, 60, 120 );
   CreateUserHist( "Mee_70_110_Preselection_Process3", 200, 60, 120 );
   CreateUserHist( "Mee_70_110_Preselection_Process4", 200, 60, 120 );

   CreateUserHistWithSysts( "Mee_EBEB_PAS"           ,    2000 , 0       , 2000     );
   CreateUserHistWithSysts( "Mee_EBEE_PAS"           ,    2000 , 0       , 2000     );
   CreateUserHistWithSysts( "Mee_EEEE_PAS"           ,    2000 , 0       , 2000     );
   CreateUserHistWithSysts( "Mee_EB_PAS"            ,    60 , 60       , 120     );

   CreateUserHist( "Mee_EBEB_80_100_PAS"       ,    60 , 60       , 120     );
   CreateUserHist( "Mee_EBEE_80_100_PAS"       ,    60 , 60       , 120     );
   CreateUserHist( "Mee_EEEE_80_100_PAS"       ,    60 , 60       , 120     );
   CreateUserHist( "Mee_EB_80_100_PAS"                 ,    60 , 60       , 120     );

   CreateUserHist( "Mee_EBEB_70_110_PAS"       ,    60 , 60       , 120     );
   CreateUserHist( "Mee_EBEE_70_110_PAS"       ,    60 , 60       , 120     );
   CreateUserHist( "Mee_EEEE_70_110_PAS"       ,    60 , 60       , 120     );
   CreateUserHist( "Mee_EB_70_110_PAS"                 ,    60 , 60       , 120     );
   CreateUserHist( "Mee_EBEB_70_110_Uncorr_PAS"     ,    60 , 60       , 120     );

   CreateUserHist( "PileupWeight"   , 100, -10, 10 );
   CreateUserHist( "GeneratorWeight", 100, -2.0, 2.0);

   // basic muon kinematics
   CreateUserHist( "Pt1stMuon_PAS"                 ,     100    , 0       , 1000     );
   CreateUserHist( "Eta1stMuon_PAS"                 ,     100    , -5      , 5      );
   CreateUserHist( "Phi1stMuon_PAS"                 ,     60     , -3.1416 , +3.1416  );
   CreateUserHist( "Pt2ndMuon_PAS"                 ,     100    , 0       , 1000     );
   CreateUserHist( "Eta2ndMuon_PAS"                 ,     100    , -5      , 5      );
   CreateUserHist( "Phi2ndMuon_PAS"                 ,     60     , -3.1416 , +3.1416  );


   CreateUserHist("CorrIsolation_1stEle_PAS"                 , 200,-25.0 ,  25.0  ); CreateUserHist("CorrIsolation_2ndEle_PAS"                 , 200,-25.0 ,  25.0  );
   CreateUserHist("DeltaEtaTrkSC_1stEle_PAS"                 , 200, -0.01,   0.01 ); CreateUserHist("DeltaEtaTrkSC_2ndEle_PAS"                 , 200, -0.01,   0.01 );
   CreateUserHist("EcalIsolation_1stEle_PAS"                 , 200,  0.0 ,  20.0  ); CreateUserHist("EcalIsolation_2ndEle_PAS"                 , 200,  0.0 ,  20.0  );
   CreateUserHist("HcalIsolation_1stEle_PAS"                 , 200,  0.0 ,  20.0  ); CreateUserHist("HcalIsolation_2ndEle_PAS"                 , 200,  0.0 ,  20.0  );
   CreateUserHist("TrkIsolation_1stEle_PAS"                  , 200,  0.0,    5.0  ); CreateUserHist("TrkIsolation_2ndEle_PAS"                  , 200,  0.0,    5.0  );
   CreateUserHist("Energy_1stEle_PAS"                        , 200,  0.0 ,3000.0  ); CreateUserHist("Energy_2ndEle_PAS"                        , 200,  0.0 ,3000.0  );
   CreateUserHist("HasMatchedPhot_1stEle_PAS"                , 2,   -0.5 ,   1.5  ); CreateUserHist("HasMatchedPhot_2ndEle_PAS"                , 2,   -0.5 ,   1.5  );
   CreateUserHist("HoE_1stEle_PAS"                           , 200,  0.0 ,   0.05 ); CreateUserHist("HoE_2ndEle_PAS"                           , 200,  0.0 ,   0.05 );
   CreateUserHist("LeadVtxDistXY_1stEle_PAS"                 , 200, -0.05,   0.05 ); CreateUserHist("LeadVtxDistXY_2ndEle_PAS"                 , 200, -0.05,   0.05 );
   CreateUserHist("LeadVtxDistZ_1stEle_PAS"                  , 200, -0.2 ,   0.2  ); CreateUserHist("LeadVtxDistZ_2ndEle_PAS"                  , 200, -0.2 ,   0.2  );
   CreateUserHist("MissingHits_1stEle_PAS"                   , 2  , -0.5,    1.5  ); CreateUserHist("MissingHits_2ndEle_PAS"                   , 2  , -0.5,    1.5  );
   CreateUserHist("Full5x5SigmaIEtaIEta_Barrel_1stEle_PAS"          , 200,  0.0,    0.04 ); CreateUserHist("Full5x5SigmaIEtaIEta_Barrel_2ndEle_PAS"          , 200,  0.0,    0.04 );
   CreateUserHist("Full5x5SigmaIEtaIEta_Endcap_1stEle_PAS"          , 200,  0.0,    0.1  ); CreateUserHist("Full5x5SigmaIEtaIEta_Endcap_2ndEle_PAS"          , 200,  0.0,    0.1  );
   CreateUserHist( "ECorrEle1_PAS", 100, 0, 1);
   CreateUserHist( "ECorrEle2_PAS", 100, 0, 1);

   CreateUserHist("CorrIsolation_1stEle_PASandMee100"        , 200,-25.0 ,  25.0  ); CreateUserHist("CorrIsolation_2ndEle_PASandMee100"        , 200,-25.0 ,  25.0  );
   CreateUserHist("DeltaEtaTrkSC_1stEle_PASandMee100"        , 200, -0.01,   0.01 ); CreateUserHist("DeltaEtaTrkSC_2ndEle_PASandMee100"        , 200, -0.01,   0.01 );
   CreateUserHist("EcalIsolation_1stEle_PASandMee100"        , 200,  0.0 ,  20.0  ); CreateUserHist("EcalIsolation_2ndEle_PASandMee100"        , 200,  0.0 ,  20.0  );
   CreateUserHist("HcalIsolation_1stEle_PASandMee100"        , 200,  0.0 ,  20.0  ); CreateUserHist("HcalIsolation_2ndEle_PASandMee100"        , 200,  0.0 ,  20.0  );
   CreateUserHist("TrkIsolation_1stEle_PASandMee100"         , 200,  0.0,    5.0  ); CreateUserHist("TrkIsolation_2ndEle_PASandMee100"         , 200,  0.0,    5.0  );
   CreateUserHist("Energy_1stEle_PASandMee100"               , 200,  0.0 ,3000.0  ); CreateUserHist("Energy_2ndEle_PASandMee100"               , 200,  0.0 ,3000.0  );
   CreateUserHist("HasMatchedPhot_1stEle_PASandMee100"       , 2,   -0.5 ,   1.5  ); CreateUserHist("HasMatchedPhot_2ndEle_PASandMee100"       , 2,   -0.5 ,   1.5  );
   CreateUserHist("HoE_1stEle_PASandMee100"                  , 200,  0.0 ,   0.05 ); CreateUserHist("HoE_2ndEle_PASandMee100"                  , 200,  0.0 ,   0.05 );
   CreateUserHist("LeadVtxDistXY_1stEle_PASandMee100"        , 200, -0.05,   0.05 ); CreateUserHist("LeadVtxDistXY_2ndEle_PASandMee100"        , 200, -0.05,   0.05 );
   CreateUserHist("LeadVtxDistZ_1stEle_PASandMee100"         , 200, -0.2 ,   0.2  ); CreateUserHist("LeadVtxDistZ_2ndEle_PASandMee100"         , 200, -0.2 ,   0.2  );
   CreateUserHist("MissingHits_1stEle_PASandMee100"          , 2  , -0.5,    1.5  ); CreateUserHist("MissingHits_2ndEle_PASandMee100"          , 2  , -0.5,    1.5  );
   CreateUserHist("Full5x5SigmaIEtaIEta_Barrel_1stEle_PASandMee100" , 200,  0.0,    0.02 ); CreateUserHist("Full5x5SigmaIEtaIEta_Barrel_2ndEle_PASandMee100" , 200,  0.0,    0.02 );
   CreateUserHist("Full5x5SigmaIEtaIEta_Endcap_1stEle_PASandMee100" , 200,  0.0,    0.1  ); CreateUserHist("Full5x5SigmaIEtaIEta_Endcap_2ndEle_PASandMee100" , 200,  0.0,    0.1  );

   if(do_roi_plots) {
     CreateUserHist( "EleChargeSum_ROI"                ,    3     , -2.5    , 2.5      );
     CreateUserHist( "Mej_selected_avg_ROI"            ,    200   , 0       , 2000     );
     CreateUserHist( "sTfrac_Jet1_ROI"                 ,   100    ,  0.0    , 1.0      );
     CreateUserHist( "sTfrac_Jet2_ROI"                 ,   100    ,  0.0    , 1.0      );
     CreateUserHist( "sTfrac_Ele1_ROI"                 ,   100    ,  0.0    , 1.0      );
     CreateUserHist( "sTfrac_Ele2_ROI"                 ,   100    ,  0.0    , 1.0      );
     CreateUserHist( "sTfrac_Jet_ROI"                  ,   100    ,  0.0    , 1.0      );
     CreateUserHist( "sTfrac_Ele_ROI"                  ,   100    ,  0.0    , 1.0      );
     CreateUserHist( "nJet_ROI"                        ,    10    , -0.5    , 9.5      );
     CreateUserHist( "Pt1stEle_ROI"                 ,     100    , 0       , 1000     );
     CreateUserHist( "Eta1stEle_ROI"                 ,     100    , -5      , 5      );
     CreateUserHist( "Phi1stEle_ROI"                 ,     60     , -3.1416 , +3.1416  );
     CreateUserHist( "Pt2ndEle_ROI"                 ,     300    , 0       , 3000     );
     CreateUserHist( "Eta2ndEle_ROI"                 ,     100    , -5      , 5      );
     CreateUserHist( "Phi2ndEle_ROI"                 ,     60     , -3.1416 , +3.1416  );
     CreateUserHist( "MET_ROI"                         ,    200   , 0       , 1000      );
     CreateUserHist( "Pt1stJet_ROI"                    ,    200   , 0       , 2000      );
     CreateUserHist( "Pt2ndJet_ROI"                    ,    200   , 0       , 2000      );
     CreateUserHist( "Eta1stJet_ROI"                   ,    100   , -5      , 5      );
     CreateUserHist( "Eta2ndJet_ROI"                   ,    100   , -5      , 5      );
     CreateUserHist( "Phi1stJet_ROI"                 ,      60    , -3.1416 , +3.1416  );
     CreateUserHist( "Phi2ndJet_ROI"                 ,      60    , -3.1416 , +3.1416  );
     CreateUserHist( "sTlep_ROI"                       ,    200   , 0       , 2000      );
     CreateUserHist( "sTjet_ROI"                       ,    200   , 0       , 2000      );
     CreateUserHist( "sT_zjj_ROI"                      ,    200   , 0       , 2000      );
     CreateUserHist( "sT_ROI"                          ,    200   , 0       , 2000      );
     CreateUserHist( "Mjj_ROI"                     ,    200   , 0       , 2000      );
     CreateUserHist( "Mee_ROI"                     ,    200   , 0       , 2000      );
     CreateUserHist( "Meejj_ROI"                       ,    400   , 0       , 4000   );
     CreateUserHist( "Mejj_ROI"                        ,    400   , 0       , 4000   );
     CreateUserHist( "Meej_ROI"                        ,    400   , 0       , 4000   );
     CreateUserHist( "Ptj1j2j3_ROI"                    ,    200 , 0       , 2000     );
     CreateUserHist( "Ptj1j2_ROI"                      ,    200 , 0       , 2000     );
     CreateUserHist( "Ptj2j3_ROI"                      ,    200 , 0       , 2000     );
     CreateUserHist( "Ptj1j3_ROI"                      ,    200 , 0       , 2000     );
     CreateUserHist( "Ptee_Minus_Ptj1j2_ROI"           ,    200 , -500    , 500      );
     CreateUserHist( "Ptee_Minus_Ptj1j2j3_ROI"         ,    200 , -500    , 500      );
     CreateUserHist( "Ptee_ROI"                        ,    200 , 0       , 2000     );
     CreateUserHist( "Me1j1_ROI"                      ,    200 , 0       , 2000   );
     CreateUserHist( "Me1j2_ROI"                      ,    200 , 0       , 2000   );
     CreateUserHist( "Me2j1_ROI"                      ,    200 , 0       , 2000   );
     CreateUserHist( "Me2j2_ROI"                      ,    200 , 0       , 2000   );
     CreateUserHist( "M_j1j3_ROI"                      ,    200 , 0       , 2000     );
     CreateUserHist( "M_j2j3_ROI"                      ,    200 , 0       , 2000     );
     CreateUserHist( "M_e1j3_ROI"                      ,    200 , 0       , 2000     );
     CreateUserHist( "M_e2j3_ROI"                      ,    200 , 0       , 2000     );
     CreateUserHist( "M_eejjj_ROI"                     ,    500 , 0       , 5000     );
     CreateUserHist( "nVertex_ROI"                     ,    101   , -0.5   , 100.5     ) ;
     CreateUserHist( "minDR_ZJet_ROI"        ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
     CreateUserHist( "DR_ZJet1_ROI"        ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
     CreateUserHist( "DR_ZJet2_ROI"        ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
     CreateUserTH2D( "MeeVsST_ROI"                 ,     400, 0, 4000, 400, 0, 4000) ;
     CreateUserHist("CorrIsolation_1stEle_ROI"                 , 200,-25.0 ,  25.0  ); CreateUserHist("CorrIsolation_2ndEle_ROI"                 , 200,-25.0 ,  25.0  );
     CreateUserHist("DeltaEtaTrkSC_1stEle_ROI"                 , 200, -0.01,   0.01 ); CreateUserHist("DeltaEtaTrkSC_2ndEle_ROI"                 , 200, -0.01,   0.01 );
     CreateUserHist("EcalIsolation_1stEle_ROI"                 , 200,  0.0 ,  20.0  ); CreateUserHist("EcalIsolation_2ndEle_ROI"                 , 200,  0.0 ,  20.0  );
     CreateUserHist("HcalIsolation_1stEle_ROI"                 , 200,  0.0 ,  20.0  ); CreateUserHist("HcalIsolation_2ndEle_ROI"                 , 200,  0.0 ,  20.0  );
     CreateUserHist("TrkIsolation_1stEle_ROI"                  , 200,  0.0,    5.0  ); CreateUserHist("TrkIsolation_2ndEle_ROI"                  , 200,  0.0,    5.0  );
     CreateUserHist("Energy_1stEle_ROI"                        , 200,  0.0 ,3000.0  ); CreateUserHist("Energy_2ndEle_ROI"                        , 200,  0.0 ,3000.0  );
     CreateUserHist("HasMatchedPhot_1stEle_ROI"                , 2,   -0.5 ,   1.5  ); CreateUserHist("HasMatchedPhot_2ndEle_ROI"                , 2,   -0.5 ,   1.5  );
     CreateUserHist("HoE_1stEle_ROI"                           , 200,  0.0 ,   0.05 ); CreateUserHist("HoE_2ndEle_ROI"                           , 200,  0.0 ,   0.05 );
     CreateUserHist("LeadVtxDistXY_1stEle_ROI"                 , 200, -0.05,   0.05 ); CreateUserHist("LeadVtxDistXY_2ndEle_ROI"                 , 200, -0.05,   0.05 );
     CreateUserHist("LeadVtxDistZ_1stEle_ROI"                  , 200, -0.2 ,   0.2  ); CreateUserHist("LeadVtxDistZ_2ndEle_ROI"                  , 200, -0.2 ,   0.2  );
     CreateUserHist("MissingHits_1stEle_ROI"                   , 2  , -0.5,    1.5  ); CreateUserHist("MissingHits_2ndEle_ROI"                   , 2  , -0.5,    1.5  );
     CreateUserHist("SigmaIEtaIEta_Barrel_1stEle_ROI"          , 200,  0.0,    0.02 ); CreateUserHist("SigmaIEtaIEta_Barrel_2ndEle_ROI"          , 200,  0.0,    0.02 );
     CreateUserHist("SigmaIEtaIEta_Endcap_1stEle_ROI"          , 200,  0.0,    0.1  ); CreateUserHist("SigmaIEtaIEta_Endcap_2ndEle_ROI"          , 200,  0.0,    0.1  );
   }

   // for scale factor dependence studies
   CreateUserHist( "Mee_NJetEq2_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_NJetEq3_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_NJetEq4_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_NJetEq5_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_NJetEq6_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_NJetEq7_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_NJetGeq3_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_NJetGeq4_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT300To500_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT500To750_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT750To1250_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1250ToInf_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin100To200_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin200To300_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin300To400_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin400To500_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin500To650_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin650ToInf_PAS"                     ,    200   , 0       , 2000      );
   // for Ptee bins
   CreateUserHist( "Mee_Ptee0To100_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_Ptee100To150_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_Ptee150To200_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_Ptee200To250_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_Ptee250To300_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_Ptee300To350_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_Ptee350To400_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_Ptee400ToInf_PAS"                     ,    200   , 0       , 2000      );
   // more plots with sT cuts for final selection thresholds
   CreateUserHist( "Mee_sT340_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT405_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT470_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT535_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT595_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT660_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT720_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT780_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT840_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT900_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT960_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1015_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1075_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1130_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1190_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1245_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1300_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1355_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1410_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1460_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1515_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1565_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1615_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1670_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1720_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1770_PAS"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1815_PAS"                     ,    200   , 0       , 2000      );
   // with zero B-tags
   CreateUserHist( "Mee_PAS_noBtaggedJets"               ,    2000 , 0       , 2000     );
   CreateUserHist( "Mee_EBEB_PAS_noBtaggedJets"           ,    2000 , 0       , 2000     );
   CreateUserHist( "Mee_EBEE_PAS_noBtaggedJets"           ,    2000 , 0       , 2000     );
   CreateUserHist( "Mee_EEEE_PAS_noBtaggedJets"           ,    2000 , 0       , 2000     );
   CreateUserHist( "Mee_sT300To500_PAS_noBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT500To750_PAS_noBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT750To1250_PAS_noBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1250ToInf_PAS_noBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin100To200_PAS_noBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin200To300_PAS_noBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin300To400_PAS_noBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin400To500_PAS_noBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin500To650_PAS_noBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin650ToInf_PAS_noBtaggedJets"                     ,    200   , 0       , 2000      );
  CreateUserHist( "nElectron_noBtaggedJets"         ,    5   , -0.5    , 4.5      );
  CreateUserHist( "nMuon_noBtaggedJets"             ,    5   , -0.5    , 4.5      );
  CreateUserHist( "nJet_noBtaggedJets"              ,    10  , -0.5    , 9.5      );
  CreateUserHist( "Pt1stEle_noBtaggedJets"       ,     100 , 0       , 1000     );
  CreateUserHist( "Eta1stEle_noBtaggedJets"       ,     100 , -5      , 5     );
  CreateUserHist( "Phi1stEle_noBtaggedJets"       ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "Pt2ndEle_noBtaggedJets"       ,     300 , 0       , 3000     );
  CreateUserHist( "Eta2ndEle_noBtaggedJets"       ,     100 , -5      , 5     );
  CreateUserHist( "Phi2ndEle_noBtaggedJets"       ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "Charge1stEle_noBtaggedJets"       ,     2   , -1.0001 , 1.0001     );
  CreateUserHist( "Charge2ndEle_noBtaggedJets"       ,     2   , -1.0001 , 1.0001     );
  CreateUserHist( "MET_noBtaggedJets"               ,    200 , 0       , 1000     );
  CreateUserHist( "METPhi_noBtaggedJets"           ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "Pt1stJet_noBtaggedJets"          ,    200 , 0       , 2000     );
  CreateUserHist( "Pt2ndJet_noBtaggedJets"          ,    200 , 0       , 2000     );
  CreateUserHist( "Eta1stJet_noBtaggedJets"         ,    100 , -5      , 5     );
  CreateUserHist( "Eta2ndJet_noBtaggedJets"         ,    100 , -5      , 5     );
  CreateUserHist( "Phi1stJet_noBtaggedJets"       ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "Phi2ndJet_noBtaggedJets"       ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "sTlep_noBtaggedJets"             ,    200 , 0       , 2000     );
  CreateUserHist( "sTjet_noBtaggedJets"             ,    200 , 0       , 2000     );
  CreateUserHist( "sT_noBtaggedJets"                ,    300   , 0       , 3000     );
  CreateUserHist( "sT_zjj_noBtaggedJets"            ,    300   , 0       , 3000      );
  CreateUserHist( "Mjj_noBtaggedJets"           ,    200 , 0       , 2000     );
  CreateUserHist( "Mee_noBtaggedJets"           ,    2000 , 0       , 2000     );
  CreateUserHist( "MTenu_noBtaggedJets"             ,    200 , 0       , 1000     );
  CreateUserHist( "Me1j1_noBtaggedJets"             ,    200 , 0       , 2000     );
  CreateUserHist( "Me1j2_noBtaggedJets"             ,    200 , 0       , 2000     );
  CreateUserHist( "Me2j1_noBtaggedJets"             ,    200 , 0       , 2000     );
  CreateUserHist( "Me2j2_noBtaggedJets"             ,    200 , 0       , 2000     );
  CreateUserHist( "Mej_selected_min_noBtaggedJets"  ,    200 , 0       , 2000     );
  CreateUserHist( "Mej_selected_max_noBtaggedJets"  ,    200 , 0       , 2000     );
  CreateUserHist( "Mej_minmax_noBtaggedJets"        ,    200 , 0       , 2000     );
  CreateUserHist( "Mej_selected_avg_noBtaggedJets"  ,    200 , 0       , 2000     );
  CreateUserHist( "Mejj_noBtaggedJets"              ,    400 , 0       , 4000     );
  CreateUserHist( "Meej_noBtaggedJets"              ,    400 , 0       , 4000     );
  CreateUserHist( "Meejj_noBtaggedJets"             ,    400 , 0       , 4000     );
   // with >= 1 B-tags
   CreateUserHist( "Mee_PAS_gteOneBtaggedJet"               ,    2000 , 0       , 2000     );
   CreateUserHist( "Mee_EBEB_PAS_gteOneBtaggedJet"           ,    2000 , 0       , 2000     );
   CreateUserHist( "Mee_EBEE_PAS_gteOneBtaggedJet"           ,    2000 , 0       , 2000     );
   CreateUserHist( "Mee_EEEE_PAS_gteOneBtaggedJet"           ,    2000 , 0       , 2000     );
   CreateUserHist( "Mee_sT300To500_PAS_gteOneBtaggedJet"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT500To750_PAS_gteOneBtaggedJet"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT750To1250_PAS_gteOneBtaggedJet"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1250ToInf_PAS_gteOneBtaggedJet"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin100To200_PAS_gteOneBtaggedJet"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin200To300_PAS_gteOneBtaggedJet"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin300To400_PAS_gteOneBtaggedJet"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin400To500_PAS_gteOneBtaggedJet"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin500To650_PAS_gteOneBtaggedJet"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin650ToInf_PAS_gteOneBtaggedJet"                     ,    200   , 0       , 2000      );
  CreateUserHist( "nElectron_gteOneBtaggedJet"         ,    5   , -0.5    , 4.5      );
  CreateUserHist( "nMuon_gteOneBtaggedJet"             ,    5   , -0.5    , 4.5      );
  CreateUserHist( "nJet_gteOneBtaggedJet"              ,    10  , -0.5    , 9.5      );
  CreateUserHist( "Pt1stEle_gteOneBtaggedJet"       ,     100 , 0       , 1000     );
  CreateUserHist( "Eta1stEle_gteOneBtaggedJet"       ,     100 , -5      , 5     );
  CreateUserHist( "Phi1stEle_gteOneBtaggedJet"       ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "Pt2ndEle_gteOneBtaggedJet"       ,     300 , 0       , 3000     );
  CreateUserHist( "Eta2ndEle_gteOneBtaggedJet"       ,     100 , -5      , 5     );
  CreateUserHist( "Phi2ndEle_gteOneBtaggedJet"       ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "Charge1stEle_gteOneBtaggedJet"       ,     2   , -1.0001 , 1.0001     );
  CreateUserHist( "Charge2ndEle_gteOneBtaggedJet"       ,     2   , -1.0001 , 1.0001     );
  CreateUserHist( "MET_gteOneBtaggedJet"               ,    200 , 0       , 1000     );
  CreateUserHist( "METPhi_gteOneBtaggedJet"           ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "Pt1stJet_gteOneBtaggedJet"          ,    200 , 0       , 2000     );
  CreateUserHist( "Pt2ndJet_gteOneBtaggedJet"          ,    200 , 0       , 2000     );
  CreateUserHist( "Eta1stJet_gteOneBtaggedJet"         ,    100 , -5      , 5     );
  CreateUserHist( "Eta2ndJet_gteOneBtaggedJet"         ,    100 , -5      , 5     );
  CreateUserHist( "Phi1stJet_gteOneBtaggedJet"       ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "Phi2ndJet_gteOneBtaggedJet"       ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "sTlep_gteOneBtaggedJet"             ,    200 , 0       , 2000     );
  CreateUserHist( "sTjet_gteOneBtaggedJet"             ,    200 , 0       , 2000     );
  CreateUserHist( "sT_gteOneBtaggedJet"                ,    300   , 0       , 3000     );
  CreateUserHist( "sT_zjj_gteOneBtaggedJet"            ,    300   , 0       , 3000      );
  CreateUserHist( "Mjj_gteOneBtaggedJet"           ,    200 , 0       , 2000     );
  CreateUserHist( "Mee_gteOneBtaggedJet"           ,    2000 , 0       , 2000     );
  CreateUserHist( "MTenu_gteOneBtaggedJet"             ,    200 , 0       , 1000     );
  CreateUserHist( "Me1j1_gteOneBtaggedJet"             ,    200 , 0       , 2000     );
  CreateUserHist( "Me1j2_gteOneBtaggedJet"             ,    200 , 0       , 2000     );
  CreateUserHist( "Me2j1_gteOneBtaggedJet"             ,    200 , 0       , 2000     );
  CreateUserHist( "Me2j2_gteOneBtaggedJet"             ,    200 , 0       , 2000     );
  CreateUserHist( "Mej_selected_min_gteOneBtaggedJet"  ,    200 , 0       , 2000     );
  CreateUserHist( "Mej_selected_max_gteOneBtaggedJet"  ,    200 , 0       , 2000     );
  CreateUserHist( "Mej_minmax_gteOneBtaggedJet"        ,    200 , 0       , 2000     );
  CreateUserHist( "Mej_selected_avg_gteOneBtaggedJet"  ,    200 , 0       , 2000     );
  CreateUserHist( "Mejj_gteOneBtaggedJet"              ,    400 , 0       , 4000     );
  CreateUserHist( "Meej_gteOneBtaggedJet"              ,    400 , 0       , 4000     );
  CreateUserHist( "Meejj_gteOneBtaggedJet"             ,    400 , 0       , 4000     );
   // with >= 2 B-tags
   CreateUserHist( "Mee_PAS_gteTwoBtaggedJets"               ,    2000 , 0       , 2000     );
   CreateUserHist( "Mee_EBEB_PAS_gteTwoBtaggedJets"           ,    2000 , 0       , 2000     );
   CreateUserHist( "Mee_EBEE_PAS_gteTwoBtaggedJets"           ,    2000 , 0       , 2000     );
   CreateUserHist( "Mee_EEEE_PAS_gteTwoBtaggedJets"           ,    2000 , 0       , 2000     );
   CreateUserHist( "Mee_sT300To500_PAS_gteTwoBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT500To750_PAS_gteTwoBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT750To1250_PAS_gteTwoBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_sT1250ToInf_PAS_gteTwoBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin100To200_PAS_gteTwoBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin200To300_PAS_gteTwoBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin300To400_PAS_gteTwoBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin400To500_PAS_gteTwoBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin500To650_PAS_gteTwoBtaggedJets"                     ,    200   , 0       , 2000      );
   CreateUserHist( "Mee_MejMin650ToInf_PAS_gteTwoBtaggedJets"                     ,    200   , 0       , 2000      );
  CreateUserHist( "nElectron_gteTwoBtaggedJets"         ,    5   , -0.5    , 4.5      );
  CreateUserHist( "nMuon_gteTwoBtaggedJets"             ,    5   , -0.5    , 4.5      );
  CreateUserHist( "nJet_gteTwoBtaggedJets"              ,    10  , -0.5    , 9.5      );
  CreateUserHist( "Pt1stEle_gteTwoBtaggedJets"       ,     100 , 0       , 1000     );
  CreateUserHist( "Eta1stEle_gteTwoBtaggedJets"       ,     100 , -5      , 5     );
  CreateUserHist( "Phi1stEle_gteTwoBtaggedJets"       ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "Pt2ndEle_gteTwoBtaggedJets"       ,     300 , 0       , 3000     );
  CreateUserHist( "Eta2ndEle_gteTwoBtaggedJets"       ,     100 , -5      , 5     );
  CreateUserHist( "Phi2ndEle_gteTwoBtaggedJets"       ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "Charge1stEle_gteTwoBtaggedJets"       ,     2   , -1.0001 , 1.0001     );
  CreateUserHist( "Charge2ndEle_gteTwoBtaggedJets"       ,     2   , -1.0001 , 1.0001     );
  CreateUserHist( "MET_gteTwoBtaggedJets"               ,    200 , 0       , 1000     );
  CreateUserHist( "METPhi_gteTwoBtaggedJets"           ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "Pt1stJet_gteTwoBtaggedJets"          ,    200 , 0       , 2000     );
  CreateUserHist( "Pt2ndJet_gteTwoBtaggedJets"          ,    200 , 0       , 2000     );
  CreateUserHist( "Eta1stJet_gteTwoBtaggedJets"         ,    100 , -5      , 5     );
  CreateUserHist( "Eta2ndJet_gteTwoBtaggedJets"         ,    100 , -5      , 5     );
  CreateUserHist( "Phi1stJet_gteTwoBtaggedJets"       ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "Phi2ndJet_gteTwoBtaggedJets"       ,     60  , -3.1416 , +3.1416     );
  CreateUserHist( "sTlep_gteTwoBtaggedJets"             ,    200 , 0       , 2000     );
  CreateUserHist( "sTjet_gteTwoBtaggedJets"             ,    200 , 0       , 2000     );
  CreateUserHist( "sT_gteTwoBtaggedJets"                ,    300   , 0       , 3000     );
  CreateUserHist( "sT_zjj_gteTwoBtaggedJets"            ,    300   , 0       , 3000      );
  CreateUserHist( "Mjj_gteTwoBtaggedJets"           ,    200 , 0       , 2000     );
  CreateUserHist( "Mee_gteTwoBtaggedJets"           ,    2000 , 0       , 2000     );
  CreateUserHist( "MTenu_gteTwoBtaggedJets"             ,    200 , 0       , 1000     );
  CreateUserHist( "Me1j1_gteTwoBtaggedJets"             ,    200 , 0       , 2000     );
  CreateUserHist( "Me1j2_gteTwoBtaggedJets"             ,    200 , 0       , 2000     );
  CreateUserHist( "Me2j1_gteTwoBtaggedJets"             ,    200 , 0       , 2000     );
  CreateUserHist( "Me2j2_gteTwoBtaggedJets"             ,    200 , 0       , 2000     );
  CreateUserHist( "Mej_selected_min_gteTwoBtaggedJets"  ,    200 , 0       , 2000     );
  CreateUserHist( "Mej_selected_max_gteTwoBtaggedJets"  ,    200 , 0       , 2000     );
  CreateUserHist( "Mej_minmax_gteTwoBtaggedJets"        ,    200 , 0       , 2000     );
  CreateUserHist( "Mej_selected_avg_gteTwoBtaggedJets"  ,    200 , 0       , 2000     );
  CreateUserHist( "Mejj_gteTwoBtaggedJets"              ,    400 , 0       , 4000     );
  CreateUserHist( "Meej_gteTwoBtaggedJets"              ,    400 , 0       , 4000     );
  CreateUserHist( "Meejj_gteTwoBtaggedJets"             ,    400 , 0       , 4000     );

  // bkg control region plots
  CreateUserHistWithSysts( "Mee_BkgControlRegion"                    ,    2000   , 0       , 2000      );
  CreateUserHistWithSysts( "Mee_BkgControlRegion_gteOneBtaggedJet"               ,    2000 , 0       , 2000     );
  CreateUserHistWithSysts( "Mee_BkgControlRegion_gteTwoBtaggedJets"               ,    2000 , 0       , 2000     );
  CreateUserHistWithSysts( "Mee_EB_BkgControlRegion"           ,    2000 , 0       , 2000     );
  CreateUserHistWithSysts( "Mee_EBEB_BkgControlRegion"           ,    2000 , 0       , 2000     );
  CreateUserHistWithSysts( "Mee_EBEE_BkgControlRegion"           ,    2000 , 0       , 2000     );
  CreateUserHistWithSysts( "Mee_EEEE_BkgControlRegion"           ,    2000 , 0       , 2000     );
  CreateUserHist( "Mee_NJetEq2_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_NJetEq3_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_NJetEq4_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_NJetEq5_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_NJetEq6_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_NJetEq7_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_NJetGeq3_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_NJetGeq4_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_sT300To500_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_sT500To750_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_sT750To1250_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_sT1250ToInf_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_MejMin100To200_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_MejMin200To300_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_MejMin300To400_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_MejMin400To500_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_MejMin500To650_BkgControlRegion"                     ,    200   , 0       , 2000      );
  CreateUserHist( "Mee_MejMin650ToInf_BkgControlRegion"                     ,    200   , 0       , 2000      );
   //// test opt
   //CreateUserHist( "Mee_sT2000_PAS"                     ,    200   , 0       , 2000      );
   //CreateUserHist( "OptBinLQ600", 200, 0, 2000);
   //CreateUserHist( "PtZforOptBin600",1000,0,2000);
   //CreateUserHist( "PtEEforOptBin600",1000,0,2000);
   //CreateUserTH2D( "PtEEVsZPtForOptBin600",1000,0,2000,1000,0,2000);
   //CreateUserHist( "OptBinLQ650", 200, 0, 2000);
   //CreateUserHist( "OptBinLQ700", 200, 0, 2000);
   //CreateUserHist( "OptBinLQ600_noWeight", 200, 0, 2000);
   //CreateUserHist( "OptBinLQ650_noWeight", 200, 0, 2000);
   //CreateUserHist( "OptBinLQ700_noWeight", 200, 0, 2000);
   // 3D opt cut space
   CreateUserTH3D( "OptimizationCutSpace", 200, 0, 2000, 200, 0, 2000, 200, 0, 2000);

   //CreateUserHist( "WZ_system_Pt" , 200,0,2000);
   //CreateUserHist( "WZ_system_Pt_GenEle" , 200,0,2000);
   //CreateUserHist( "WZ_system_Pt_WZPtCut" , 200,0,2000);
   // checking electrons
   CreateUserHist( "SCEta_1stEle_Presel",4000,0,10);
   CreateUserHist( "EleEta_1stEle_Presel",4000,0,10);
   CreateUserHist( "DeltaEtaTrkSC_1stEle_Presel",4000,0,10);
   CreateUserHist( "SCEtaMinusEleEta_1stEle_Presel",4000,0,10);
   CreateUserHist( "DeltaEtaTrkSC_Minus_SCEtaMinusEleEta_1stEle_Presel",4000,0,10);
   CreateUserHist( "SCEta_2ndEle_Presel",4000,0,10);
   CreateUserHist( "EleEta_2ndEle_Presel",4000,0,10);
   CreateUserHist( "DeltaEtaTrkSC_2ndEle_Presel",4000,0,10);
   CreateUserHist( "SCEtaMinusEleEta_2ndEle_Presel",4000,0,10);
   CreateUserHist( "DeltaEtaTrkSC_Minus_SCEtaMinusEleEta_2ndEle_Presel",4000,0,10);

   //--------------------------------------------------------------------------
   // Final selection plots
   //--------------------------------------------------------------------------
   bool doFinalSelections = false;
   // check if there is a final Mej specific in cutfile for any LQ mass
   for (int i_lq_mass = 0; i_lq_mass < n_lq_mass; ++i_lq_mass ){
     int lq_mass = LQ_MASS[i_lq_mass];
     //TODO FIXME; hack for now
     //sprintf(cut_name, "min_M_ej_LQ%d"   , lq_mass );
     sprintf(cut_name, "BDTOutput_TrainRegion_LQ%d"   , lq_mass );
     CreateUserHist(cut_name,2000,-1,1);
     sprintf(cut_name, "BDTOutput_noWeight_TrainRegion_LQ%d"   , lq_mass );
     CreateUserHist(cut_name,2000,-1,1);
     sprintf(cut_name, "BDTOutput_LQ%d"   , lq_mass );
     if(hasCut(cut_name))
       doFinalSelections = true;
   }
   if(doFinalSelections && !evaluateBDT) {
     STDOUT("ERROR: No BDTWeightFileName specified, yet asked to do final selections. Quitting here.");
     exit(-5);
   }
   // now, we must have an Mej cut and optimization must be off to have final selections enabled
   doFinalSelections = doFinalSelections && !isOptimizationEnabled();

   char plot_name[100];

   if(doFinalSelections)
   {
     for (int i_lq_mass = 0; i_lq_mass < n_lq_mass ; ++i_lq_mass ) {
       int lq_mass = LQ_MASS[i_lq_mass];
       sprintf(plot_name, "GeneratorWeight_LQ%d"        , lq_mass ); CreateUserHist ( plot_name, 200 , -2 , 2 );
       sprintf(plot_name, "Mej_selected_avg_LQ%d"       , lq_mass ); CreateUserHist ( plot_name, 60  , 0 , 3000 );
       sprintf(plot_name, "Mej_selected_min_LQ%d"       , lq_mass ); CreateUserHist ( plot_name, 60  , 0 , 3000 );
       sprintf(plot_name, "Mej_selected_max_LQ%d"       , lq_mass ); CreateUserHist ( plot_name, 60  , 0 , 3000 );
       sprintf(plot_name, "Mej_minmax_LQ%d"             , lq_mass ); CreateUserHist ( plot_name, 60  , 0 , 3000 );
       sprintf(plot_name, "sT_eejj_LQ%d"                , lq_mass ); CreateUserHist ( plot_name, 30  , 0 , 3000 );
       sprintf(plot_name, "Mee_LQ%d"                    , lq_mass ); CreateUserHist ( plot_name, 40  , 0 , 2000 );
       sprintf(plot_name, "Mej_selected_min_vs_max_LQ%d", lq_mass ); CreateUserTH2D ( plot_name, 150  , 0 , 3000, 150  , 0 , 3000 );
       sprintf(plot_name, "DR_Ele1Jet1_LQ%d"            , lq_mass ); CreateUserHist ( plot_name,
           getHistoNBins("DR_Ele1Jet1"),
           getHistoMin  ("DR_Ele1Jet1"),
           getHistoMax  ("DR_Ele1Jet1"));

       sprintf(plot_name, "nElectron_LQ%d"          , lq_mass ); CreateUserHist( plot_name , 5,  -0.5 ,   4.5  );
       sprintf(plot_name, "CorrIsolation_1stEle_LQ%d"        , lq_mass ); CreateUserHist( plot_name , 200,-25.0 ,  25.0  );
       sprintf(plot_name, "DeltaEtaTrkSC_1stEle_LQ%d"        , lq_mass ); CreateUserHist( plot_name , 200, -0.01,   0.01 );
       sprintf(plot_name, "EcalIsolation_1stEle_LQ%d"        , lq_mass ); CreateUserHist( plot_name , 200,  0.0 ,  20.0  );
       sprintf(plot_name, "HcalIsolation_1stEle_LQ%d"        , lq_mass ); CreateUserHist( plot_name , 200,  0.0 ,  20.0  );
       sprintf(plot_name, "TrkIsolation_1stEle_LQ%d"         , lq_mass ); CreateUserHist( plot_name , 200,  0.0,    5.0  );
       sprintf(plot_name, "Energy_1stEle_LQ%d"               , lq_mass ); CreateUserHist( plot_name , 200,  0.0 ,3000.0  );
       sprintf(plot_name, "HasMatchedPhot_1stEle_LQ%d"       , lq_mass ); CreateUserHist( plot_name , 2,   -0.5 ,   1.5  );
       sprintf(plot_name, "HoE_1stEle_LQ%d"                  , lq_mass ); CreateUserHist( plot_name , 200,  0.0 ,   0.05 );
       sprintf(plot_name, "LeadVtxDistXY_1stEle_LQ%d"        , lq_mass ); CreateUserHist( plot_name , 200, -0.05,   0.05 );
       sprintf(plot_name, "LeadVtxDistZ_1stEle_LQ%d"         , lq_mass ); CreateUserHist( plot_name , 200, -0.2 ,   0.2  );
       sprintf(plot_name, "MissingHits_1stEle_LQ%d"          , lq_mass ); CreateUserHist( plot_name , 2  , -0.5,    1.5  );
       sprintf(plot_name, "Full5x5SigmaIEtaIEta_Barrel_1stEle_LQ%d" , lq_mass ); CreateUserHist( plot_name , 200,  0.0,    0.02 );
       sprintf(plot_name, "Full5x5SigmaIEtaIEta_Endcap_1stEle_LQ%d" , lq_mass ); CreateUserHist( plot_name , 200,  0.0,    0.1  );


       sprintf(plot_name, "CorrIsolation_2ndEle_LQ%d"        , lq_mass ); CreateUserHist( plot_name , 200,-25.0 ,  25.0  );
       sprintf(plot_name, "DeltaEtaTrkSC_2ndEle_LQ%d"        , lq_mass ); CreateUserHist( plot_name , 200, -0.01,   0.01 );
       sprintf(plot_name, "EcalIsolation_2ndEle_LQ%d"        , lq_mass ); CreateUserHist( plot_name , 200,  0.0 ,  20.0  );
       sprintf(plot_name, "HcalIsolation_2ndEle_LQ%d"        , lq_mass ); CreateUserHist( plot_name , 200,  0.0 ,  20.0  );
       sprintf(plot_name, "TrkIsolation_2ndEle_LQ%d"         , lq_mass ); CreateUserHist( plot_name , 200,  0.0,    5.0  );
       sprintf(plot_name, "Energy_2ndEle_LQ%d"               , lq_mass ); CreateUserHist( plot_name , 200,  0.0 ,3000.0  );
       sprintf(plot_name, "HasMatchedPhot_2ndEle_LQ%d"       , lq_mass ); CreateUserHist( plot_name , 2,   -0.5 ,   1.5  );
       sprintf(plot_name, "HoE_2ndEle_LQ%d"                  , lq_mass ); CreateUserHist( plot_name , 200,  0.0 ,   0.05 );
       sprintf(plot_name, "LeadVtxDistXY_2ndEle_LQ%d"        , lq_mass ); CreateUserHist( plot_name , 200, -0.05,   0.05 );
       sprintf(plot_name, "LeadVtxDistZ_2ndEle_LQ%d"         , lq_mass ); CreateUserHist( plot_name , 200, -0.2 ,   0.2  );
       sprintf(plot_name, "MissingHits_2ndEle_LQ%d"          , lq_mass ); CreateUserHist( plot_name , 2  , -0.5,    1.5  );
       sprintf(plot_name, "Full5x5SigmaIEtaIEta_Barrel_2ndEle_LQ%d" , lq_mass ); CreateUserHist( plot_name , 200,  0.0,    0.02 );
       sprintf(plot_name, "Full5x5SigmaIEtaIEta_Endcap_2ndEle_LQ%d" , lq_mass ); CreateUserHist( plot_name , 200,  0.0,    0.1  );


       sprintf(plot_name, "EleChargeSum_LQ%d"        , lq_mass ); CreateUserHist( plot_name ,      3 , -2.5    , 2.5      );
       sprintf(plot_name, "sTfrac_Jet1_LQ%d"         , lq_mass ); CreateUserHist( plot_name ,    100 ,  0.0    , 1.0      );
       sprintf(plot_name, "sTfrac_Jet2_LQ%d"         , lq_mass ); CreateUserHist( plot_name ,    100 ,  0.0    , 1.0      );
       sprintf(plot_name, "sTfrac_Ele1_LQ%d"         , lq_mass ); CreateUserHist( plot_name ,    100 ,  0.0    , 1.0      );
       sprintf(plot_name, "sTfrac_Ele2_LQ%d"         , lq_mass ); CreateUserHist( plot_name ,    100 ,  0.0    , 1.0      );
       sprintf(plot_name, "sTfrac_Jet_LQ%d"          , lq_mass ); CreateUserHist( plot_name ,    100 ,  0.0    , 1.0      );
       sprintf(plot_name, "sTfrac_Ele_LQ%d"          , lq_mass ); CreateUserHist( plot_name ,    100 ,  0.0    , 1.0      );
       sprintf(plot_name, "nJet_LQ%d"                , lq_mass ); CreateUserHist( plot_name ,     10 , -0.5    , 9.5      );
       sprintf(plot_name, "Pt1stEle_LQ%d"               , lq_mass ); CreateUserHist( plot_name ,    100 ,  0.0    , 1000     );
       sprintf(plot_name, "Eta1stEle_LQ%d"           , lq_mass ); CreateUserHist( plot_name ,    100 , -5.0    , 5.0      );
       sprintf(plot_name, "Phi1stEle_LQ%d"           , lq_mass ); CreateUserHist( plot_name ,     60 , -3.1416 , +3.1416  );
       sprintf(plot_name, "Pt2ndEle_LQ%d"               , lq_mass ); CreateUserHist( plot_name ,    100 ,  0.0    , 1000     );
       sprintf(plot_name, "Eta2ndEle_LQ%d"           , lq_mass ); CreateUserHist( plot_name ,    100 , -5.0    , 5.0      );
       sprintf(plot_name, "Phi2ndEle_LQ%d"           , lq_mass ); CreateUserHist( plot_name ,     60 , -3.1416 , 3.1416   );
       sprintf(plot_name, "MET_LQ%d"                 , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 1000     );
       sprintf(plot_name, "Pt1stJet_LQ%d"            , lq_mass ); CreateUserHist( plot_name ,    100 ,  0.0    , 1000     );
       sprintf(plot_name, "Pt2ndJet_LQ%d"            , lq_mass ); CreateUserHist( plot_name ,    100 ,  0.0    , 1000     );
       sprintf(plot_name, "Eta1stJet_LQ%d"           , lq_mass ); CreateUserHist( plot_name ,    100 , -5.0    , 5.0      );
       sprintf(plot_name, "Eta2ndJet_LQ%d"           , lq_mass ); CreateUserHist( plot_name ,    100 , -5.0    , 5.0      );
       sprintf(plot_name, "Phi1stJet_LQ%d"           , lq_mass ); CreateUserHist( plot_name ,     60 , -3.1416 , 3.1416   );
       sprintf(plot_name, "Phi2ndJet_LQ%d"           , lq_mass ); CreateUserHist( plot_name ,     60 , -3.1416 , 3.1416   );
       sprintf(plot_name, "sTlep_LQ%d"               , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "sTjet_LQ%d"               , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "sT_zjj_LQ%d"              , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "Mjj_LQ%d"           , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "Meejj_LQ%d"               , lq_mass ); CreateUserHist( plot_name ,    400 ,  0.0    , 4000     );
       sprintf(plot_name, "Mejj_LQ%d"                , lq_mass ); CreateUserHist( plot_name ,    400 ,  0.0    , 4000     );
       sprintf(plot_name, "Meej_LQ%d"                , lq_mass ); CreateUserHist( plot_name ,    400 ,  0.0    , 4000     );
       sprintf(plot_name, "Ptj1j2j3_LQ%d"            , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "Ptj1j2_LQ%d"              , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "Ptj2j3_LQ%d"              , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "Ptj1j3_LQ%d"              , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "Ptee_Minus_Ptj1j2_LQ%d"   , lq_mass ); CreateUserHist( plot_name ,    200 , -500    ,  500     );
       sprintf(plot_name, "Ptee_Minus_Ptj1j2j3_LQ%d" , lq_mass ); CreateUserHist( plot_name ,    200 , -500    ,  500     );
       sprintf(plot_name, "Ptee_LQ%d"                , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "Me1j1_LQ%d"               , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "Me1j2_LQ%d"               , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "Me2j1_LQ%d"               , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "Me2j2_LQ%d"               , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "M_j1j3_LQ%d"              , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "M_j2j3_LQ%d"              , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "M_e1j3_LQ%d"              , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "M_e2j3_LQ%d"              , lq_mass ); CreateUserHist( plot_name ,    200 ,  0.0    , 2000     );
       sprintf(plot_name, "M_eejjj_LQ%d"             , lq_mass ); CreateUserHist( plot_name ,    500 ,  0.0    , 5000     );
       sprintf(plot_name, "nVertex_LQ%d"             , lq_mass ); CreateUserHist( plot_name ,    101 , -0.5    ,  100.5   );
       sprintf(plot_name, "MeeVsST_LQ%d"             , lq_mass ); CreateUserTH2D( plot_name ,    200 ,  0.0, 2000, 200, 0, 2000) ;
       sprintf(plot_name, "minDR_ZJet_LQ%d"          , lq_mass ); CreateUserHist( plot_name ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
       sprintf(plot_name, "DR_ZJet1_LQ%d"            , lq_mass ); CreateUserHist( plot_name ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
       sprintf(plot_name, "DR_ZJet2_LQ%d"            , lq_mass ); CreateUserHist( plot_name ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
       // checking electrons
       sprintf(plot_name, "SCEta_1stEle_LQ%d", lq_mass ); CreateUserHist( plot_name , 4000,0,10);
       sprintf(plot_name, "EleEta_1stEle_LQ%d", lq_mass ); CreateUserHist( plot_name , 4000,0,10);
       sprintf(plot_name, "SCEtaMinusEleEta_1stEle_LQ%d", lq_mass ); CreateUserHist( plot_name , 4000,0,10);
       sprintf(plot_name, "DeltaEtaTrkSC_Minus_SCEtaMinusEleEta_1stEle_LQ%d", lq_mass ); CreateUserHist( plot_name , 4000,0,10);
       sprintf(plot_name, "SCEta_2ndEle_LQ%d", lq_mass ); CreateUserHist( plot_name , 4000,0,10);
       sprintf(plot_name, "EleEta_2ndEle_LQ%d", lq_mass ); CreateUserHist( plot_name , 4000,0,10);
       sprintf(plot_name, "SCEtaMinusEleEta_2ndEle_LQ%d", lq_mass ); CreateUserHist( plot_name , 4000,0,10);
       sprintf(plot_name, "DeltaEtaTrkSC_Minus_SCEtaMinusEleEta_2ndEle_LQ%d", lq_mass ); CreateUserHist( plot_name , 4000,0,10);
       // muon kinematics
       sprintf(plot_name, "Pt1stMuon_LQ%d"               , lq_mass ); CreateUserHist( plot_name ,    100 ,  0.0    , 1000     );
       sprintf(plot_name, "Eta1stMuon_LQ%d"           , lq_mass ); CreateUserHist( plot_name ,    100 , -5.0    , 5.0      );
       sprintf(plot_name, "Phi1stMuon_LQ%d"           , lq_mass ); CreateUserHist( plot_name ,     60 , -3.1416 , +3.1416  );
       sprintf(plot_name, "Pt2ndMuon_LQ%d"               , lq_mass ); CreateUserHist( plot_name ,    100 ,  0.0    , 1000     );
       sprintf(plot_name, "Eta2ndMuon_LQ%d"           , lq_mass ); CreateUserHist( plot_name ,    100 , -5.0    , 5.0      );
       sprintf(plot_name, "Phi2ndMuon_LQ%d"           , lq_mass ); CreateUserHist( plot_name ,     60 , -3.1416 , 3.1416   );
     }
     // for SF at final selections
     CreateUserHist( "Mee_70_110_LQ300", 200, 60, 120 );
     CreateUserHist( "Mee_70_110_LQ600", 200, 60, 120 );
     CreateUserHist( "Mee_70_110_LQ800", 200, 60, 120 );
     CreateUserHist( "Mee_70_110_LQ900", 200, 60, 120 );
     CreateUserHist( "Mee_70_110_LQ1000", 200, 60, 120 );
   }

   //--------------------------------------------------------------------------
   // Tell the user how many entries we'll look at
   //--------------------------------------------------------------------------

   Long64_t nentries = GetTreeEntries();
   std::cout << "analysisClass::analysisClass(): nentries = " << nentries << std::endl;

   //--------------------------------------------------------------------------
   // Loop over the chain
   //--------------------------------------------------------------------------
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
     readerTools_->LoadEntry(jentry);
     //-----------------------------------------------------------------
     // Print progress
     //-----------------------------------------------------------------
     if(jentry < 10 || jentry%10000 == 0) std::cout << "analysisClass:Loop(): jentry = " << jentry << "/" << nentries << std::endl;
     //std::cout << "analysisClass:Loop(): jentry = " << jentry << "/" << nentries << std::endl;
     // run ls event
     unsigned int run = readerTools_->ReadValueBranch<UInt_t>("run");
     if(run==319077 || run==319310) continue;
     //XXX TEST
     //if(jentry!=1295 && jentry!=1586) continue;
     //if(jentry > 1000) continue;
     //if(run==319077) continue;
     //XXX TEST
     //float ls = readerTools_->ReadValueBranch<Float_t>("ls");
     //float event = readerTools_->ReadValueBranch<Float_t>("event");
     //std::cout << static_cast<unsigned int>(run) << " " << static_cast<unsigned int>(ls) << " " << static_cast<unsigned int>(event) << std::endl;


     //--------------------------------------------------------------------------
     // Reset the cuts
     //--------------------------------------------------------------------------

     resetCuts();

     //--------------------------------------------------------------------------
     // Do pileup re-weighting
     //--------------------------------------------------------------------------

     float pileup_weight = readerTools_->ReadValueBranch<Float_t>("puWeight");
     if ( isData() ) pileup_weight = 1.0;

     //--------------------------------------------------------------------------
     // Get information about gen-level reweighting (should be for Sherpa only)
     //--------------------------------------------------------------------------

     float gen_weight = readerTools_->ReadValueBranch<Float_t>("Weight");
     if ( isData() ) gen_weight = 1.0;
     //if ( isData && Ele2_ValidFrac > 998. ){
     //  gen_weight = 0.0;
     //  if      (  60.0 < M_e1e2 < 120. ) gen_weight = 0.61;
     //  else if ( 120.0 < M_e1e2 < 200. ) gen_weight = 0.42;
     //  else if ( 200.0 < M_e1e2        ) gen_weight = 0.42;
     //}

     //std::cout << "Gen weight = " << gen_weight << "; pileup_weight = " << pileup_weight << std::endl;

     //--------------------------------------------------------------------------
     // Get information about prefire reweighting
     //--------------------------------------------------------------------------
     float prefire_weight = 1.0;
     if(analysisYear < 2018 && hasBranch("PrefireWeight") && !isData())
       prefire_weight = readerTools_->ReadValueBranch<Float_t>("PrefireWeight");
       //prefire_weight = readerTools_->ReadValueBranch<Float_t>("L1PreFiringWeight_Nom");
     gen_weight*=prefire_weight;

     std::string current_file_name ( readerTools_->GetTree()->GetCurrentFile()->GetName());

     // SIC remove March 2018
     //// TopPt reweight
     //// only valid for powheg
     //if(current_file_name.find("TT_") != std::string::npos) {
     //  gen_weight*=TopPtWeight;
     //}

     //// apply PDF rescale for LQToDEle/LQToBEle 2016 only
     //if(analysisYear==2016) {
     //  if(current_file_name.find("LQToBEle") != std::string::npos || current_file_name.find("LQToDEle") != std::string::npos ) {
     //    gen_weight*=readerTools_->ReadArrayBranch<Float_t>("LHEPdfWeight", 0);
     //    //std::cout << "INFO: Applying LHEPdfWeight=" << readerTools_->ReadArrayBranch<Float_t>("LHEPdfWeight", 0) << " for run: " << run << " ls: " << ls << " event: " << event << std::endl;
     //  }
     //}

     //std::cout << "prefire weight = " << prefire_weight << std::endl;

     // Electron scale factors for MC only
     if(!isData()) {
       float recoHeepSF = 1.0;
       bool verbose = false;
       float recoSFEle1 = readerTools_->ReadValueBranch<Float_t>("Ele1_RecoSF");
       float recoSFEle2 = readerTools_->ReadValueBranch<Float_t>("Ele2_RecoSF");
       // HEEP ID
       float heepSFEle1 = readerTools_->ReadValueBranch<Float_t>("Ele1_HEEPSF");
       float heepSFEle2 = readerTools_->ReadValueBranch<Float_t>("Ele2_HEEPSF");
       // EGM loose ID
       float looseSFEle1 = readerTools_->ReadValueBranch<Float_t>("Ele1_EGMLooseIDSF");
       float looseSFEle2 = readerTools_->ReadValueBranch<Float_t>("Ele2_EGMLooseIDSF");
       // z vtx (2017)
       float zVtxSF =  readerTools_->ReadValueBranch<Float_t>("ZVtxSF");
       gen_weight*=zVtxSF;
       gen_weight*=recoSFEle1*recoSFEle2*looseSFEle1*looseSFEle2;
     }
     else {
       // no syst for data since no scale factor applied
       fillSystVariableWithValue("EleTrigSFUp", 1);
       fillSystVariableWithValue("EleTrigSFDown", 1);
     }
     // apply event trigger scale factor
     float trigSF = readerTools_->ReadValueBranch<Float_t>("EventTriggerScaleFactor");
     float trigSFErr = readerTools_->ReadValueBranch<Float_t>("EventTriggerScaleFactorErr");
     gen_weight*=trigSF;
     fillSystVariableWithValue("EleTrigSFUp", trigSF+trigSFErr);
     fillSystVariableWithValue("EleTrigSFDown", trigSF-trigSFErr);

     //--------------------------------------------------------------------------
     // Fill HLT
     //--------------------------------------------------------------------------
     bool passHLT = readerTools_->ReadValueBranch<bool>("PassTrigger");
     if ( isData() ) {
       passHLT = false;
       std::string current_file_name ( readerTools_->GetTree()->GetCurrentFile()->GetName());
       if(current_file_name.find("SinglePhoton") != std::string::npos) {
         if(analysisYear==2016) {
           if (readerTools_->ReadValueBranch<float>("H_Photon175") == 1) // take events triggered by Photon175 only plus those triggered by Photon175 AND Ele27/Ele115
             passHLT = true;
         }
         else {
           if (readerTools_->ReadValueBranch<float>("H_Photon200") == 1) // take events triggered by Photon200 only plus those triggered by Photon200 AND Ele35
             passHLT = true;
         }
       }
       else if(current_file_name.find("SingleElectron") != std::string::npos) {
         if(analysisYear==2016) {
           if (readerTools_->ReadValueBranch<float>("H_Photon175") != 1 &&
               //(readerTools_->ReadValueBranch<float>("H_Ele27_WPTight") == 1 || readerTools_->ReadValueBranch<float>("H_Ele115_CIdVT_GsfIdT") == 1) ) // take events triggered only by Ele27 OR Ele115
               //(readerTools_->ReadValueBranch<float>("H_Ele115_CIdVT_GsfIdT") == 1) ) // take events triggered only by Ele115
             (readerTools_->ReadValueBranch<float>("H_Ele27_WPTight") == 1) )
               passHLT = true;
         }
         else {
           if (readerTools_->ReadValueBranch<float>("H_Photon200") != 1 &&
               readerTools_->ReadValueBranch<float>("H_Ele35_WPTight") == 1 ) // take events triggered only by Ele35
             passHLT = true;
         }
       }
       else if(analysisYear==2018) {
         if (readerTools_->ReadValueBranch<float>("H_Photon200") == 1 ||
             //readerTools_->ReadValueBranch<float>("H_Ele32_WPTight") == 1 ||
             //readerTools_->ReadValueBranch<float>("H_Ele115_CIdVT_GsfIdT") == 1) // take events triggered by Photon200 OR Ele32 OR Ele115
             readerTools_->ReadValueBranch<float>("H_Ele32_WPTight") == 1) // take events triggered by Photon200 OR Ele32
           passHLT = true;
       }
     }
     fillVariableWithValue ( "PassHLT", passHLT, gen_weight * pileup_weight  ) ;

     //--------------------------------------------------------------------------
     // Calculate variables for trigger matching
     //--------------------------------------------------------------------------

     int nEle_hltMatched = 0.0;
     //FIXME reduced skim
     //if ( Ele1_hltEleSignalPt > 0.0 ) nEle_hltMatched++;
     //if ( Ele2_hltEleSignalPt > 0.0 ) nEle_hltMatched++;

     int nJet_hltMatched = 0.0;
     if ( readerTools_->ReadValueBranch<Float_t>("Jet1_hltJetPt") > 0.0 ) nJet_hltMatched++;
     if ( readerTools_->ReadValueBranch<Float_t>("Jet2_hltJetPt") > 0.0 ) nJet_hltMatched++;

     fillVariableWithValue("nEle_hltMatched",nEle_hltMatched, gen_weight * pileup_weight  );
     fillVariableWithValue("nJet_hltMatched",nJet_hltMatched, gen_weight * pileup_weight  );


     //--------------------------------------------------------------------------
     // First variable to fill just shows the "reweighting".  Always passes.
     //--------------------------------------------------------------------------

     // TEST
     //gen_weight = gen_weight > 0 ? 1.0 : -1.0;
     //pileup_weight = 1.0;
     fillVariableWithValue ( "Reweighting", 1, gen_weight * pileup_weight  );

     //--------------------------------------------------------------------------
     // Special treatment of inclusive W/Z
     //--------------------------------------------------------------------------
     //bool passGenWZPt = true;
     //// inclusive
     ////if(current_file_name.find("WJetsToLNu_ext1_amcatnloFXFX") != std::string::npos
     ////    || current_file_name.find("WJetsToLNu_amcatnloFXFX") != std::string::npos) {
     ////  if(GenW1_Pt > 120) passGenWZPt = false; // if W Pt > 120 GeV, cut it out
     ////}
     //if(current_file_name.find("DYJetsToLL_M-50_amcatnloFXFX") != std::string::npos) {
     //  if(GenZGamma1_Pt > 70) passGenWZPt = false; // if Z/gamma Pt > 70 GeV, cut it out
     //}
     //// first pt bin
     ////if(current_file_name.find("WJetsToLNu_Pt-100") != std::string::npos) {
     ////  if(GenW1_Pt <= 120) passGenWZPt = false;
     ////}
     //if(current_file_name.find("DYJetsToLL_Pt-50") != std::string::npos) {
     //  if(GenZGamma1_Pt <= 70) passGenWZPt = false;
     //}
     ////// testing
     ////if(current_file_name.find("WJetsToLNu_ext1_amcatnloFXFX") != std::string::npos
     ////    || current_file_name.find("WJetsToLNu_amcatnloFXFX") != std::string::npos) {
     ////  if(GenW1_Pt <= 100) passGenWZPt = false; // if W Pt > 100 GeV, cut it out
     ////}
     ////if(current_file_name.find("DYJetsToLL_M-50_amcatnloFXFX") != std::string::npos) {
     ////  if(GenZGamma1_Pt <= 100) passGenWZPt = false; // if Z/gamma Pt > 100 GeV, cut it out
     ////}
     //fillVariableWithValue("PassGenWZPt",passGenWZPt,gen_weight*pileup_weight);

     bool passLHECuts = true;
     // for jet-pt bin stitching
     //if(current_file_name.find("DYJetsToLL_M-50_amcatnloFXFX") != std::string::npos ||
     //    current_file_name.find("DYJetsToLL_M-50_newPMX_amcatnloFXFX") != std::string::npos ||
     //    current_file_name.find("DYJetsToLL_M-50_ext_amcatnloFXFX") != std::string::npos ||
     //    current_file_name.find("DYJetsToLL_M-50_ext_newPMX_amcatnloFXFX") != std::string::npos ||
     //    current_file_name.find("DYJetsToLL_M-50_ext1_amcatnloFXFX") != std::string::npos ||
     //    current_file_name.find("DYJetsToLL_M-50_ext1_newPMX_amcatnloFXFX") != std::string::npos ||
     //    current_file_name.find("DYJetsToLL_M-50_ext2_amcatnloFXFX") != std::string::npos ||
     //    current_file_name.find("DYJetsToLL_M-50_ext2_newPMX_amcatnloFXFX") != std::string::npos) {
     //  passLHECuts = false;
     //  if(readerTools_->ReadValueBranch<Float_t>("LHE_NpNLO") == 0) passLHECuts = true; // if zero jets, take it
     //  else if(readerTools_->ReadValueBranch<Float_t>("LHE_Vpt") < 50) passLHECuts = true; // if Z/gamma Pt < 50 GeV, take it
     //}
     // pt-binned sample stitching, Jul. 2022
     // see: https://cms-talk.web.cern.ch/t/bug-in-ul-pt-binned-dy-samples/11639
     if(current_file_name.find("DYJetsToLL_M-50_TuneCP5") != std::string::npos) {
       passLHECuts = false;
       if(readerTools_->ReadValueBranch<Float_t>("LHE_Vpt") == 0)
         passLHECuts = true; // if Z/gamma Pt == 0 GeV, take it
     }
     fillVariableWithValue("PassLHECuts",passLHECuts,gen_weight*pileup_weight);

     //--------------------------------------------------------------------------
     // Fill JSON variable
     //--------------------------------------------------------------------------
     fillVariableWithValue ("PassJSON", readerTools_->ReadValueBranch<Bool_t>("PassJSON"), gen_weight * pileup_weight);

     //--------------------------------------------------------------------------
     // Fill noise filters
     //--------------------------------------------------------------------------
     // see: https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
     // we filled these at skim time
     fillVariableWithValue("PassGlobalSuperTightHalo2016Filter" , readerTools_->ReadValueBranch<Bool_t>("PassGlobalSuperTightHalo2016Filter")     , gen_weight * pileup_weight);
     fillVariableWithValue("PassGoodVertices"                   , readerTools_->ReadValueBranch<Bool_t>("PassGoodVertices")                       , gen_weight * pileup_weight);
     fillVariableWithValue("PassHBHENoiseFilter"                , readerTools_->ReadValueBranch<Bool_t>("PassHBHENoiseFilter")                    , gen_weight * pileup_weight);
     fillVariableWithValue("PassHBHENoiseIsoFilter"             , readerTools_->ReadValueBranch<Bool_t>("PassHBHENoiseIsoFilter")                 , gen_weight * pileup_weight);
     // eBadScFilter not suggested for MC
     if(isData())
       fillVariableWithValue("PassBadEESupercrystalFilter"      , readerTools_->ReadValueBranch<Bool_t>("PassBadEESupercrystalFilter")            , gen_weight * pileup_weight);
     else
       fillVariableWithValue("PassBadEESupercrystalFilter"      , 1                                                                                , gen_weight * pileup_weight);
     fillVariableWithValue("PassEcalDeadCellTrigPrim"           , readerTools_->ReadValueBranch<Bool_t>("PassEcalDeadCellTrigPrim")               , gen_weight * pileup_weight);
     // not recommended
     //fillVariableWithValue("PassChargedCandidateFilter"         , int(readerTools_->ReadValueB<Float_t>("PassChargedCandidateFilter")            == 1), gen_weight * pileup_weight);
     fillVariableWithValue("PassBadPFMuonFilter"                , readerTools_->ReadValueBranch<Bool_t>("PassBadPFMuonFilter")                    , gen_weight * pileup_weight);
     // EcalBadCalibV2 for 2017, 2018
     if(analysisYear > 2016)
       fillVariableWithValue("PassEcalBadCalibFilter"         , readerTools_->ReadValueBranch<Bool_t>("PassEcalBadCalibFilter")               , gen_weight * pileup_weight);
     else
       fillVariableWithValue("PassEcalBadCalibFilter"         , 1                                                                                , gen_weight * pileup_weight);

     //--------------------------------------------------------------------------
     // Pass number of muons & electrons
     // --> Special consideration if ttbar is derived from data
     //--------------------------------------------------------------------------

     // Muons and electrons
     bool is_ttbar_from_data = false;
     //FIXME
     //if ( readerTools_->ReadValueBranch<Float_t>("Ele2_ValidFrac") > 998. ) is_ttbar_from_data = true;
     // NB: we are doing data-driven ttbar separately so this shouldn't be the case here

     int PassNEle = 0;
     // nEle_ptCut are ID'ed electrons passing the Pt cut in the skim
     int nEle_ptCut = readerTools_->ReadValueBranch<Int_t>("nEle_ptCut");
     //if ( !is_ttbar_from_data && nEle_ptCut == 2 ) PassNEle = 1;
     //if (  is_ttbar_from_data && nEle_ptCut == 2 ) PassNEle = 1;
     if ( !is_ttbar_from_data && nEle_ptCut >= 2 )
       PassNEle = 1;
     if (  is_ttbar_from_data && nEle_ptCut >= 2 )
       PassNEle = 1;

     int PassNMuon = 0;
     int nMuon_ptCut = readerTools_->ReadValueBranch<Int_t>("nMuon_ptCut");
     if ( !is_ttbar_from_data && nMuon_ptCut == 0 )
       PassNMuon = 1;
     if (  is_ttbar_from_data && nMuon_ptCut >  0 )
       PassNMuon = 1;
     // now check if there are no muons but gen muons passing pt/eta which should have passed ID but did not
     // correct by a factor of (1-effData)/(1-effMC) to evaluate uncertainty
     if(PassNMuon) // no ID'ed muons in event
     {
       double GenMu1_Pt =  readerTools_->ReadValueBranch<Float_t>("GenMu1_Pt");
       double GenMu1_Eta = readerTools_->ReadValueBranch<Float_t>("GenMu1_Eta");
       double GenMu2_Pt =  readerTools_->ReadValueBranch<Float_t>("GenMu2_Pt");
       double GenMu2_Eta = readerTools_->ReadValueBranch<Float_t>("GenMu2_Eta");
       double GenMu3_Pt =  readerTools_->ReadValueBranch<Float_t>("GenMu3_Pt");
       double GenMu3_Eta = readerTools_->ReadValueBranch<Float_t>("GenMu3_Eta");
       // check for gen muons which should have passed ID but did not
       // pt threshold is defined in highPt muon ID in MuonIDs
       if(GenMu1_Pt > 35.0 && fabs(GenMu1_Eta) <= 2.4) {
         gen_weight*=MuonScaleFactors::GetVetoMCDataEffRatio(GenMu1_Eta);
         //cout << "Found gen muon 1 with Pt: " << GenMu1_Pt << " and eta: " << GenMu1_Eta << endl;
         //cout << "\tCorrect by: " << MuonScaleFactors::GetVetoMCDataEffRatio(GenMu1_Eta) << endl;
       }
       if(GenMu2_Pt > 35.0 && fabs(GenMu2_Eta) <= 2.4) {
         gen_weight*=MuonScaleFactors::GetVetoMCDataEffRatio(GenMu2_Eta);
         //cout << "Found gen muon 2 with Pt: " << GenMu2_Pt << " and eta: " << GenMu2_Eta << endl;
         //cout << "\tCorrect by: " << MuonScaleFactors::GetVetoMCDataEffRatio(GenMu2_Eta) << endl;
       }
       if(GenMu3_Pt > 35.0 && fabs(GenMu3_Eta) <= 2.4) {
         gen_weight*=MuonScaleFactors::GetVetoMCDataEffRatio(GenMu3_Eta);
         //cout << "Found gen muon 3 with Pt: " << GenMu3_Pt << " and eta: " << GenMu3_Eta << endl;
         //cout << "\tCorrect by: " << MuonScaleFactors::GetVetoMCDataEffRatio(GenMu3_Eta) << endl;
       }
     }


     fillVariableWithValue("PassNEle" , PassNEle , gen_weight * pileup_weight);
     fillVariableWithValue("PassNMuon", PassNMuon, gen_weight * pileup_weight);

     //--------------------------------------------------------------------------
     // Calculate electron-jet pair mass values
     //--------------------------------------------------------------------------

     double M_ej_avg, M_ej_min, M_ej_max, M_ej_asym, M_eejj;
     double M_ej_avg_JER_Up, M_ej_min_JER_Up, M_ej_max_JER_Up, M_ej_asym_JER_Up;
     double M_ej_avg_JER_Dn, M_ej_min_JER_Dn, M_ej_max_JER_Dn, M_ej_asym_JER_Dn;
     double M_ej_avg_JES_Up, M_ej_min_JES_Up, M_ej_max_JES_Up, M_ej_asym_JES_Up;
     double M_ej_avg_JES_Dn, M_ej_min_JES_Dn, M_ej_max_JES_Dn, M_ej_asym_JES_Dn;
     double M_ej_avg_EER_Up, M_ej_min_EER_Up, M_ej_max_EER_Up, M_ej_asym_EER_Up;
     double M_ej_avg_EER_Dn, M_ej_min_EER_Dn, M_ej_max_EER_Dn, M_ej_asym_EER_Dn;
     double M_ej_avg_EES_Up, M_ej_min_EES_Up, M_ej_max_EES_Up, M_ej_asym_EES_Up;
     double M_ej_avg_EES_Dn, M_ej_min_EES_Dn, M_ej_max_EES_Dn, M_ej_asym_EES_Dn;

     int nEle_store = readerTools_->ReadValueBranch<Int_t>("nEle_store");
     int nJet_store = readerTools_->ReadValueBranch<Int_t>("nJet_store");
     float M_e1j1 = readerTools_->ReadValueBranch<Float_t>("M_e1j1");
     float M_e1j2 = readerTools_->ReadValueBranch<Float_t>("M_e1j2");
     float M_e2j1 = readerTools_->ReadValueBranch<Float_t>("M_e2j1");
     float M_e2j2 = readerTools_->ReadValueBranch<Float_t>("M_e2j2");
     float Pt_e1e2 = readerTools_->ReadValueBranch<Float_t>("Pt_e1e2");
     // systs
     float M_e1j1_EER_Up = readerTools_->ReadValueBranch<Float_t>("M_e1j1_EER_Up");
     float M_e1j2_EER_Up = readerTools_->ReadValueBranch<Float_t>("M_e1j2_EER_Up");
     float M_e2j1_EER_Up = readerTools_->ReadValueBranch<Float_t>("M_e2j1_EER_Up");
     float M_e2j2_EER_Up = readerTools_->ReadValueBranch<Float_t>("M_e2j2_EER_Up");
     float M_e1j1_EER_Dn = readerTools_->ReadValueBranch<Float_t>("M_e1j1_EER_Dn");
     float M_e1j2_EER_Dn = readerTools_->ReadValueBranch<Float_t>("M_e1j2_EER_Dn");
     float M_e2j1_EER_Dn = readerTools_->ReadValueBranch<Float_t>("M_e2j1_EER_Dn");
     float M_e2j2_EER_Dn = readerTools_->ReadValueBranch<Float_t>("M_e2j2_EER_Dn");
     float M_e1j1_EES_Up = readerTools_->ReadValueBranch<Float_t>("M_e1j1_EES_Up");
     float M_e1j2_EES_Up = readerTools_->ReadValueBranch<Float_t>("M_e1j2_EES_Up");
     float M_e2j1_EES_Up = readerTools_->ReadValueBranch<Float_t>("M_e2j1_EES_Up");
     float M_e2j2_EES_Up = readerTools_->ReadValueBranch<Float_t>("M_e2j2_EES_Up");
     float M_e1j1_EES_Dn = readerTools_->ReadValueBranch<Float_t>("M_e1j1_EES_Dn");
     float M_e1j2_EES_Dn = readerTools_->ReadValueBranch<Float_t>("M_e1j2_EES_Dn");
     float M_e2j1_EES_Dn = readerTools_->ReadValueBranch<Float_t>("M_e2j1_EES_Dn");
     float M_e2j2_EES_Dn = readerTools_->ReadValueBranch<Float_t>("M_e2j2_EES_Dn");
     float M_e1j1_JESTotal_Up = readerTools_->ReadValueBranch<Float_t>("M_e1j1_jesTotalup");
     float M_e1j2_JESTotal_Up = readerTools_->ReadValueBranch<Float_t>("M_e1j2_jesTotalup");
     float M_e2j1_JESTotal_Up = readerTools_->ReadValueBranch<Float_t>("M_e2j1_jesTotalup");
     float M_e2j2_JESTotal_Up = readerTools_->ReadValueBranch<Float_t>("M_e2j2_jesTotalup");
     float M_e1j1_JESTotal_Dn = readerTools_->ReadValueBranch<Float_t>("M_e1j1_jesTotaldown");
     float M_e1j2_JESTotal_Dn = readerTools_->ReadValueBranch<Float_t>("M_e1j2_jesTotaldown");
     float M_e2j1_JESTotal_Dn = readerTools_->ReadValueBranch<Float_t>("M_e2j1_jesTotaldown");
     float M_e2j2_JESTotal_Dn = readerTools_->ReadValueBranch<Float_t>("M_e2j2_jesTotaldown");
     float M_e1j1_JER_Up = readerTools_->ReadValueBranch<Float_t>("M_e1j1_jerup");
     float M_e1j2_JER_Up = readerTools_->ReadValueBranch<Float_t>("M_e1j2_jerup");
     float M_e2j1_JER_Up = readerTools_->ReadValueBranch<Float_t>("M_e2j1_jerup");
     float M_e2j2_JER_Up = readerTools_->ReadValueBranch<Float_t>("M_e2j2_jerup");
     float M_e1j1_JER_Dn = readerTools_->ReadValueBranch<Float_t>("M_e1j1_jerdown");
     float M_e1j2_JER_Dn = readerTools_->ReadValueBranch<Float_t>("M_e1j2_jerdown");
     float M_e2j1_JER_Dn = readerTools_->ReadValueBranch<Float_t>("M_e2j1_jerdown");
     float M_e2j2_JER_Dn = readerTools_->ReadValueBranch<Float_t>("M_e2j2_jerdown");

     if ( nEle_store >= 2 && nJet_store >= 2) {
       if ( fabs(M_e1j1-M_e2j2) < fabs(M_e1j2-M_e2j1) )  {
         M_ej_avg = (M_e1j1 + M_e2j2) / 2.0;
         if    ( M_e1j1 < M_e2j2 ) {
           M_ej_max = M_e2j2;
           M_ej_max_EER_Up = M_e2j2_EER_Up;
           M_ej_max_EER_Dn = M_e2j2_EER_Dn;
           M_ej_max_EES_Up = M_e2j2_EES_Up;
           M_ej_max_EES_Dn = M_e2j2_EES_Dn;
           M_ej_max_JER_Up = M_e2j2_JER_Up;
           M_ej_max_JER_Dn = M_e2j2_JER_Dn;
           M_ej_max_JES_Up = M_e2j2_JESTotal_Up;
           M_ej_max_JES_Dn = M_e2j2_JESTotal_Dn;
           M_ej_min = M_e1j1;
           M_ej_min_EER_Up = M_e1j1_EER_Up;
           M_ej_min_EER_Dn = M_e1j1_EER_Dn;
           M_ej_min_EES_Up = M_e1j1_EES_Up;
           M_ej_min_EES_Dn = M_e1j1_EES_Dn;
           M_ej_min_JER_Up = M_e1j1_JER_Up;
           M_ej_min_JER_Dn = M_e1j1_JER_Dn;
           M_ej_min_JES_Up = M_e1j1_JESTotal_Up;
           M_ej_min_JES_Dn = M_e1j1_JESTotal_Dn;
         }
         else {
           M_ej_max = M_e1j1;
           M_ej_max_EER_Up = M_e1j1_EER_Up;
           M_ej_max_EER_Dn = M_e1j1_EER_Dn;
           M_ej_max_EES_Up = M_e1j1_EES_Up;
           M_ej_max_EES_Dn = M_e1j1_EES_Dn;
           M_ej_max_JER_Up = M_e1j1_JER_Up;
           M_ej_max_JER_Dn = M_e1j1_JER_Dn;
           M_ej_max_JES_Up = M_e1j1_JESTotal_Up;
           M_ej_max_JES_Dn = M_e1j1_JESTotal_Dn;
           M_ej_min = M_e2j2;
           M_ej_min_EER_Up = M_e2j2_EER_Up;
           M_ej_min_EER_Dn = M_e2j2_EER_Dn;
           M_ej_min_EES_Up = M_e2j2_EES_Up;
           M_ej_min_EES_Dn = M_e2j2_EES_Dn;
           M_ej_min_JER_Up = M_e2j2_JER_Up;
           M_ej_min_JER_Dn = M_e2j2_JER_Dn;
           M_ej_min_JES_Up = M_e2j2_JESTotal_Up;
           M_ej_min_JES_Dn = M_e2j2_JESTotal_Dn;
         }
       }
       else {
         M_ej_avg = (M_e1j2 + M_e2j1) / 2.0;
         if    ( M_e1j2 < M_e2j1 ) {
           M_ej_max = M_e2j1;
           M_ej_max_EER_Up = M_e2j1_EER_Up;
           M_ej_max_EER_Dn = M_e2j1_EER_Dn;
           M_ej_max_EES_Up = M_e2j1_EES_Up;
           M_ej_max_EES_Dn = M_e2j1_EES_Dn;
           M_ej_max_JER_Up = M_e2j1_JER_Up;
           M_ej_max_JER_Dn = M_e2j1_JER_Dn;
           M_ej_max_JES_Up = M_e2j1_JESTotal_Up;
           M_ej_max_JES_Dn = M_e2j1_JESTotal_Dn;
           M_ej_min = M_e1j2;
           M_ej_min_EER_Up = M_e1j2_EER_Up;
           M_ej_min_EER_Dn = M_e1j2_EER_Dn;
           M_ej_min_EES_Up = M_e1j2_EES_Up;
           M_ej_min_EES_Dn = M_e1j2_EES_Dn;
           M_ej_min_JER_Up = M_e1j2_JER_Up;
           M_ej_min_JER_Dn = M_e1j2_JER_Dn;
           M_ej_min_JES_Up = M_e1j2_JESTotal_Up;
           M_ej_min_JES_Dn = M_e1j2_JESTotal_Dn;
         }
         else {
           M_ej_max = M_e1j2;
           M_ej_max_EER_Up = M_e1j2_EER_Up;
           M_ej_max_EER_Dn = M_e1j2_EER_Dn;
           M_ej_max_EES_Up = M_e1j2_EES_Up;
           M_ej_max_EES_Dn = M_e1j2_EES_Dn;
           M_ej_max_JER_Up = M_e1j2_JER_Up;
           M_ej_max_JER_Dn = M_e1j2_JER_Dn;
           M_ej_max_JES_Up = M_e1j2_JESTotal_Up;
           M_ej_max_JES_Dn = M_e1j2_JESTotal_Dn;
           M_ej_min = M_e2j1;
           M_ej_min_EER_Up = M_e2j1_EER_Up;
           M_ej_min_EER_Dn = M_e2j1_EER_Dn;
           M_ej_min_EES_Up = M_e2j1_EES_Up;
           M_ej_min_EES_Dn = M_e2j1_EES_Dn;
           M_ej_min_JER_Up = M_e2j1_JER_Up;
           M_ej_min_JER_Dn = M_e2j1_JER_Dn;
           M_ej_min_JES_Up = M_e2j1_JESTotal_Up;
           M_ej_min_JES_Dn = M_e2j1_JESTotal_Dn;
         }
       }
       M_ej_asym = (M_ej_max - M_ej_min)/(M_ej_max + M_ej_min);
       M_ej_asym_EER_Up = (M_ej_max_EER_Up - M_ej_min_EER_Up)/(M_ej_max_EER_Up + M_ej_min_EER_Up);
       M_ej_asym_EER_Dn = (M_ej_max_EER_Dn - M_ej_min_EER_Dn)/(M_ej_max_EER_Dn + M_ej_min_EER_Dn);
       M_ej_asym_EES_Up = (M_ej_max_EES_Up - M_ej_min_EES_Up)/(M_ej_max_EES_Up + M_ej_min_EES_Up);
       M_ej_asym_EES_Dn = (M_ej_max_EES_Dn - M_ej_min_EES_Dn)/(M_ej_max_EES_Dn + M_ej_min_EES_Dn);
       M_ej_asym_JER_Up = (M_ej_max_JER_Up - M_ej_min_JER_Up)/(M_ej_max_JER_Up + M_ej_min_JER_Up);
       M_ej_asym_JER_Dn = (M_ej_max_JER_Dn - M_ej_min_JER_Dn)/(M_ej_max_JER_Dn + M_ej_min_JER_Dn);
       M_ej_asym_JES_Up = (M_ej_max_JES_Up - M_ej_min_JES_Up)/(M_ej_max_JES_Up + M_ej_min_JES_Up);
       M_ej_asym_JES_Dn = (M_ej_max_JES_Dn - M_ej_min_JES_Dn)/(M_ej_max_JES_Dn + M_ej_min_JES_Dn);
     }

     double sT_zjj = Pt_e1e2 + readerTools_->ReadValueBranch<Float_t>("Jet1_Pt") + readerTools_->ReadValueBranch<Float_t>("Jet2_Pt");

     //--------------------------------------------------------------------------
     // Fill electron variables
     //--------------------------------------------------------------------------
     //double Ele1_PtHeep = readerTools_->ReadValueBranch<Float_t>("Ele1_PtHeep");
     //double Ele2_PtHeep = readerTools_->ReadValueBranch<Float_t>("Ele2_PtHeep");
     float Ele1_Pt = readerTools_->ReadValueBranch<Float_t>("Ele1_Pt");
     float Ele2_Pt = readerTools_->ReadValueBranch<Float_t>("Ele2_Pt");
     float Ele1_Eta = readerTools_->ReadValueBranch<Float_t>("Ele1_Eta");
     float Ele2_Eta = readerTools_->ReadValueBranch<Float_t>("Ele2_Eta");
     float Ele1_Phi = readerTools_->ReadValueBranch<Float_t>("Ele1_Phi");
     float Ele2_Phi = readerTools_->ReadValueBranch<Float_t>("Ele2_Phi");
     float Ele1_Pt_EER_Up = readerTools_->ReadValueBranch<Float_t>("Ele1_Pt_EER_Up");
     float Ele1_Pt_EER_Dn = readerTools_->ReadValueBranch<Float_t>("Ele1_Pt_EER_Dn");
     float Ele1_Pt_EES_Up = readerTools_->ReadValueBranch<Float_t>("Ele1_Pt_EES_Up");
     float Ele1_Pt_EES_Dn = readerTools_->ReadValueBranch<Float_t>("Ele1_Pt_EES_Dn");
     float Ele2_Pt_EER_Up = readerTools_->ReadValueBranch<Float_t>("Ele2_Pt_EER_Up");
     float Ele2_Pt_EER_Dn = readerTools_->ReadValueBranch<Float_t>("Ele2_Pt_EER_Dn");
     float Ele2_Pt_EES_Up = readerTools_->ReadValueBranch<Float_t>("Ele2_Pt_EES_Up");
     float Ele2_Pt_EES_Dn = readerTools_->ReadValueBranch<Float_t>("Ele2_Pt_EES_Dn");

     if ( nEle_store >= 1 ) {
       //fillVariableWithValue( "Ele1_PtHeep",            Ele1_PtHeep, gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "Ele1_Pt",            Ele1_Pt, gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "Ele1_Eta",            Ele1_Eta, gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "Ele1_Phi",            Ele1_Phi, gen_weight * pileup_weight  ) ;
       //fillVariableWithValue( "Ele1_AbsDeltaEtaEleTrk",
       //    fabs(Ele1_Eta-Ele1_TrkEta), gen_weight * pileup_weight );
     }
     if ( nEle_store >= 2 ) {
       //fillVariableWithValue( "Ele2_PtHeep",            Ele2_PtHeep, gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "Ele2_Pt",            Ele2_Pt, gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "Ele2_Eta",            Ele2_Eta, gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "Ele2_Phi",            Ele2_Phi, gen_weight * pileup_weight  ) ;
       //fillVariableWithValue( "Ele2_AbsDeltaEtaEleTrk",
       //    fabs(Ele2_Eta-Ele2_TrkEta), gen_weight * pileup_weight );
     }

     //--------------------------------------------------------------------------
     // Fill jet variables
     //--------------------------------------------------------------------------
     float Jet1_Pt = readerTools_->ReadValueBranch<Float_t>("Jet1_Pt");
     float Jet1_Eta = readerTools_->ReadValueBranch<Float_t>("Jet1_Eta");
     float Jet1_Phi = readerTools_->ReadValueBranch<Float_t>("Jet1_Phi");
     float Jet2_Pt = readerTools_->ReadValueBranch<Float_t>("Jet2_Pt");
     float Jet2_Phi = readerTools_->ReadValueBranch<Float_t>("Jet2_Phi");
     float Jet2_Eta = readerTools_->ReadValueBranch<Float_t>("Jet2_Eta");
     float Jet3_Pt = readerTools_->ReadValueBranch<Float_t>("Jet3_Pt");
     float Jet3_Phi = readerTools_->ReadValueBranch<Float_t>("Jet3_Phi");
     float Jet3_Eta = readerTools_->ReadValueBranch<Float_t>("Jet3_Eta");
     float Jet1_Pt_JER_Up = readerTools_->ReadValueBranch<Float_t>("Jet1_Pt_jerup");
     float Jet1_Pt_JER_Dn = readerTools_->ReadValueBranch<Float_t>("Jet1_Pt_jerdown");
     float Jet1_Pt_JES_Up = readerTools_->ReadValueBranch<Float_t>("Jet1_Pt_jesTotalup");
     float Jet1_Pt_JES_Dn = readerTools_->ReadValueBranch<Float_t>("Jet1_Pt_jesTotaldown");
     float Jet2_Pt_JER_Up = readerTools_->ReadValueBranch<Float_t>("Jet2_Pt_jerup");
     float Jet2_Pt_JER_Dn = readerTools_->ReadValueBranch<Float_t>("Jet2_Pt_jerdown");
     float Jet2_Pt_JES_Up = readerTools_->ReadValueBranch<Float_t>("Jet2_Pt_jesTotalup");
     float Jet2_Pt_JES_Dn = readerTools_->ReadValueBranch<Float_t>("Jet2_Pt_jesTotaldown");

     int nJet_ptCut = hasBranch("nJet_ptCut") ? readerTools_->ReadValueBranch<Int_t>("nJet_ptCut") : readerTools_->ReadValueBranch<Int_t>("nJet_store");
     float DR_Jet1Jet2 = readerTools_->ReadValueBranch<Float_t>("DR_Jet1Jet2");
     // Jets
     fillVariableWithValue("nJet", nJet_ptCut, gen_weight * pileup_weight );
     //if ( nJet_store >= 1 ) {
       fillVariableWithValue( "Jet1_Pt"    , Jet1_Pt     , gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "Jet1_Eta"   , Jet1_Eta    , gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "Jet1_Phi"   , Jet1_Phi    , gen_weight * pileup_weight  ) ;
     //}
     //if ( nJet_store >= 2 ) {
       fillVariableWithValue( "Jet2_Pt"    , Jet2_Pt     , gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "Jet2_Eta"   , Jet2_Eta    , gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "Jet2_Phi"   , Jet2_Phi    , gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "DR_Jet1Jet2", DR_Jet1Jet2 , gen_weight * pileup_weight  ) ;
     //}
       fillVariableWithValue( "Jet3_Pt"    , Jet3_Pt     , gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "Jet3_Eta"   , Jet3_Eta    , gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "Jet3_Phi"   , Jet3_Phi    , gen_weight * pileup_weight  ) ;

     //--------------------------------------------------------------------------
     // Fill DeltaR variables
     //--------------------------------------------------------------------------

     float DR_Ele1Jet1 = readerTools_->ReadValueBranch<Float_t>("DR_Ele1Jet1");
     float DR_Ele2Jet1 = readerTools_->ReadValueBranch<Float_t>("DR_Ele2Jet1");
     float DR_Ele1Jet2 = readerTools_->ReadValueBranch<Float_t>("DR_Ele1Jet2");
     float DR_Ele2Jet2 = readerTools_->ReadValueBranch<Float_t>("DR_Ele2Jet2");
     //if ( nEle_store >= 2 && nJet_store >= 1) {
       fillVariableWithValue( "DR_Ele1Jet1"  , DR_Ele1Jet1, gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "DR_Ele2Jet1"  , DR_Ele2Jet1 , gen_weight * pileup_weight  ) ;
       //if(nJet_store >= 2) {
         fillVariableWithValue( "DR_Ele1Jet2", DR_Ele1Jet2 , gen_weight * pileup_weight  ) ;
         fillVariableWithValue( "DR_Ele2Jet2", DR_Ele2Jet2 , gen_weight * pileup_weight  ) ;
       //}
     //}


     //--------------------------------------------------------------------------
     // Multi-object variables
     //--------------------------------------------------------------------------
     float sT_eejj = readerTools_->ReadValueBranch<Float_t>("sT_eejj");
     float M_e1e2 =  readerTools_->ReadValueBranch<Float_t>("M_e1e2");
     double M_e1e2_EER_Up =  readerTools_->ReadValueBranch<Float_t>("M_e1e2_EER_Up");
     double M_e1e2_EER_Dn =  readerTools_->ReadValueBranch<Float_t>("M_e1e2_EER_Dn");
     double M_e1e2_EES_Up =  readerTools_->ReadValueBranch<Float_t>("M_e1e2_EES_Up");
     double M_e1e2_EES_Dn =  readerTools_->ReadValueBranch<Float_t>("M_e1e2_EES_Dn");
     float PFMET_Type1_Pt = readerTools_->ReadValueBranch<Float_t>("PFMET_Type1_Pt");
     float PFMET_Type1_Phi = readerTools_->ReadValueBranch<Float_t>("PFMET_Type1_Phi");
     float MejMin = M_ej_min;
     float MejMax = M_ej_max;
     float Masym = M_ej_asym;
     float Meejj = GetMeejj( Ele1_Pt,  Ele2_Pt,  Jet1_Pt,  Jet2_Pt, Ele1_Eta,  Ele2_Eta,  Jet1_Eta,  Jet2_Eta, Ele1_Phi,  Ele2_Phi,  Jet1_Phi,  Jet2_Phi);
     float Meejj_EER_Up = GetMeejj( Ele1_Pt_EER_Up,  Ele2_Pt_EER_Up,  Jet1_Pt,  Jet2_Pt, Ele1_Eta,  Ele2_Eta,  Jet1_Eta,  Jet2_Eta, Ele1_Phi,  Ele2_Phi,  Jet1_Phi,  Jet2_Phi);
     float Meejj_EER_Dn = GetMeejj( Ele1_Pt_EER_Dn,  Ele2_Pt_EER_Dn,  Jet1_Pt,  Jet2_Pt, Ele1_Eta,  Ele2_Eta,  Jet1_Eta,  Jet2_Eta, Ele1_Phi,  Ele2_Phi,  Jet1_Phi,  Jet2_Phi);
     float Meejj_EES_Up = GetMeejj( Ele1_Pt_EES_Up,  Ele2_Pt_EES_Up,  Jet1_Pt,  Jet2_Pt, Ele1_Eta,  Ele2_Eta,  Jet1_Eta,  Jet2_Eta, Ele1_Phi,  Ele2_Phi,  Jet1_Phi,  Jet2_Phi);
     float Meejj_EES_Dn = GetMeejj( Ele1_Pt_EES_Dn,  Ele2_Pt_EES_Dn,  Jet1_Pt,  Jet2_Pt, Ele1_Eta,  Ele2_Eta,  Jet1_Eta,  Jet2_Eta, Ele1_Phi,  Ele2_Phi,  Jet1_Phi,  Jet2_Phi);
     float Meejj_JER_Up = GetMeejj( Ele1_Pt,  Ele2_Pt,  Jet1_Pt_JER_Up,  Jet2_Pt_JER_Up, Ele1_Eta,  Ele2_Eta,  Jet1_Eta,  Jet2_Eta, Ele1_Phi,  Ele2_Phi,  Jet1_Phi,  Jet2_Phi);
     float Meejj_JER_Dn = GetMeejj( Ele1_Pt,  Ele2_Pt,  Jet1_Pt_JER_Dn,  Jet2_Pt_JER_Dn, Ele1_Eta,  Ele2_Eta,  Jet1_Eta,  Jet2_Eta, Ele1_Phi,  Ele2_Phi,  Jet1_Phi,  Jet2_Phi);
     float Meejj_JES_Up = GetMeejj( Ele1_Pt,  Ele2_Pt,  Jet1_Pt_JES_Up,  Jet2_Pt_JES_Up, Ele1_Eta,  Ele2_Eta,  Jet1_Eta,  Jet2_Eta, Ele1_Phi,  Ele2_Phi,  Jet1_Phi,  Jet2_Phi);
     float Meejj_JES_Dn = GetMeejj( Ele1_Pt,  Ele2_Pt,  Jet1_Pt_JES_Dn,  Jet2_Pt_JES_Dn, Ele1_Eta,  Ele2_Eta,  Jet1_Eta,  Jet2_Eta, Ele1_Phi,  Ele2_Phi,  Jet1_Phi,  Jet2_Phi);

     if ( nEle_store >= 2 ) {
       fillVariableWithValue( "M_e1e2"     , M_e1e2 , gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "M_e1e2_bkgCR"     , M_e1e2 , gen_weight * pileup_weight  ) ;
       //fillVariableWithValue( "M_e1e2_opt" , M_e1e2 , gen_weight * pileup_weight  ) ;
       // for Ptee cut
       fillVariableWithValue( "Pt_e1e2"    , Pt_e1e2 , gen_weight * pileup_weight  ) ;

       fillVariableWithValue( "sT_eejj"    , sT_eejj , gen_weight * pileup_weight  ) ;
       fillVariableWithValue( "sT_eejj_bkgCR"    , sT_eejj , gen_weight * pileup_weight  ) ;
     }
     fillVariableWithValue( "M_e1j1", M_e1j1, gen_weight * pileup_weight  ) ;
     fillVariableWithValue( "M_e1j2", M_e1j2, gen_weight * pileup_weight  ) ;
     fillVariableWithValue( "M_e2j1", M_e2j1, gen_weight * pileup_weight  ) ;
     fillVariableWithValue( "M_e2j2", M_e2j2, gen_weight * pileup_weight  ) ;
     fillVariableWithValue( "Masym", Masym, gen_weight * pileup_weight  ) ;
     fillVariableWithValue( "MejMin", MejMin, gen_weight * pileup_weight  ) ;
     fillVariableWithValue( "MejMax", MejMax, gen_weight * pileup_weight  ) ;
     fillVariableWithValue( "Meejj", Meejj, gen_weight * pileup_weight  ) ;
     //fillVariableWithValue( "PFMET_opt", PFMET_Type1_Pt, gen_weight * pileup_weight  ) ;
     fillVariableWithValue( "PFMET_Type1_Pt", PFMET_Type1_Pt, gen_weight * pileup_weight  ) ;
     fillVariableWithValue( "PFMET_Type1_Phi", PFMET_Type1_Phi, gen_weight * pileup_weight  ) ;

     // Dummy variables
     fillVariableWithValue ("preselection", 1, gen_weight * pileup_weight );
     fillVariableWithValue ("trainingSelection", 1, gen_weight * pileup_weight );

     // systematics
     // Masym
     fillSystVariableWithValue("EERUp",   "Masym",   M_ej_asym_EER_Up);
     fillSystVariableWithValue("EERDown", "Masym",   M_ej_asym_EER_Dn);
     fillSystVariableWithValue("EESUp",   "Masym",   M_ej_asym_EES_Up);
     fillSystVariableWithValue("EESDown", "Masym",   M_ej_asym_EES_Dn);
     fillSystVariableWithValue("JERUp",   "Masym",   M_ej_asym_JER_Up);
     fillSystVariableWithValue("JERDown", "Masym",   M_ej_asym_JER_Dn);
     fillSystVariableWithValue("JESUp",   "Masym",   M_ej_asym_JES_Up);
     fillSystVariableWithValue("JESDown", "Masym",   M_ej_asym_JES_Dn);
     // Meejj
     fillSystVariableWithValue("EERUp",   "Meejj",   Meejj_EER_Up);
     fillSystVariableWithValue("EERDown", "Meejj",   Meejj_EER_Dn);
     fillSystVariableWithValue("EESUp",   "Meejj",   Meejj_EES_Up);
     fillSystVariableWithValue("EESDown", "Meejj",   Meejj_EES_Dn);
     fillSystVariableWithValue("JERUp",   "Meejj",   Meejj_JER_Up);
     fillSystVariableWithValue("JERDown", "Meejj",   Meejj_JER_Dn);
     fillSystVariableWithValue("JESUp",   "Meejj",   Meejj_JES_Up);
     fillSystVariableWithValue("JESDown", "Meejj",   Meejj_JES_Dn);
     // MejMax
     fillSystVariableWithValue("EERUp",   "MejMax",   M_ej_max_EER_Up);
     fillSystVariableWithValue("EERDown", "MejMax",   M_ej_max_EER_Dn);
     fillSystVariableWithValue("EESUp",   "MejMax",   M_ej_max_EES_Up);
     fillSystVariableWithValue("EESDown", "MejMax",   M_ej_max_EES_Dn);
     fillSystVariableWithValue("JERUp",   "MejMax",   M_ej_max_JER_Up);
     fillSystVariableWithValue("JERDown", "MejMax",   M_ej_max_JER_Dn);
     fillSystVariableWithValue("JESUp",   "MejMax",   M_ej_max_JES_Up);
     fillSystVariableWithValue("JESDown", "MejMax",   M_ej_max_JES_Dn);
     // MejMin
     fillSystVariableWithValue("EERUp",   "MejMin",   M_ej_min_EER_Up);
     fillSystVariableWithValue("EERDown", "MejMin",   M_ej_min_EER_Dn);
     fillSystVariableWithValue("EESUp",   "MejMin",   M_ej_min_EES_Up);
     fillSystVariableWithValue("EESDown", "MejMin",   M_ej_min_EES_Dn);
     fillSystVariableWithValue("JERUp",   "MejMin",   M_ej_min_JER_Up);
     fillSystVariableWithValue("JERDown", "MejMin",   M_ej_min_JER_Dn);
     fillSystVariableWithValue("JESUp",   "MejMin",   M_ej_min_JES_Up);
     fillSystVariableWithValue("JESDown", "MejMin",   M_ej_min_JES_Dn);
     //--------------------------------------------------------------------------
     // Fill final selection cuts
     //--------------------------------------------------------------------------

     //if(doFinalSelections)
     //{
     //  for (int i_lq_mass = 0; i_lq_mass < n_lq_mass; ++i_lq_mass ){
     //    int lq_mass = LQ_MASS[i_lq_mass];
     //    //sprintf(cut_name, "M_e1e2_LQ%d"  , lq_mass );
     //    //fillVariableWithValue ( cut_name, M_e1e2  , gen_weight * pileup_weight  ) ;
     //    //sprintf(cut_name, "sT_eejj_LQ%d" , lq_mass );
     //    //fillVariableWithValue ( cut_name, sT_eejj , gen_weight * pileup_weight  ) ;
     //    //sprintf(cut_name, "min_M_ej_LQ%d", lq_mass );
     //    //fillVariableWithValue ( cut_name, M_ej_min, gen_weight * pileup_weight  ) ;
     //    sprintf(cut_name, "BDTOutput_LQ%d", lq_mass );
     //    STDOUT("sethlog: getVariableValue for " << cut_name);
     //    fillVariableWithValue ( cut_name, getVariableValue(cut_name), gen_weight * pileup_weight  ) ;
     //    //fillSystVariableWithValue( "EER", cut_name, M_ej_min_EER);
     //    //fillSystVariableWithValue( "EESUp", cut_name, M_ej_min_EES_Up);
     //    //fillSystVariableWithValue( "EESDown", cut_name, M_ej_min_EES_Dn);
     //    //fillSystVariableWithValue( "JESUp", cut_name, M_ej_min_JES_Up);
     //    //fillSystVariableWithValue( "JESDown", cut_name, M_ej_min_JES_Dn);
     //    //fillSystVariableWithValue( "JERUp", cut_name, M_ej_min_JER_Up);
     //    //fillSystVariableWithValue( "JERDown", cut_name, M_ej_min_JER_Dn);
     //    // add Masym for test
     //    //sprintf(cut_name, "asym_M_ej_LQ%d", lq_mass );
     //    //fillVariableWithValue ( cut_name, M_ej_asym, gen_weight * pileup_weight  ) ;
     //    //
     //  }
     //}

     //--------------------------------------------------------------------------
     // Fill bjet variables
     //--------------------------------------------------------------------------
     // require at least 1 b-tagged jet for TTBar control region
     // require zero b-tagged jets for DYJets control region
     // and then apply the b-tag scale factors (2-SF in the veto case)
     // see: https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation
     // for using event weights, we follow: https://twiki.cern.ch/twiki/bin/view/CMS/BTagSFMethods#1c_Event_reweighting_using_scale

     double Jet1_btagDisc = readerTools_->ReadValueBranch<Float_t>("Jet1_btag"+btagAlgo);
     double Jet2_btagDisc = readerTools_->ReadValueBranch<Float_t>("Jet2_btag"+btagAlgo);
     double Jet3_btagDisc = readerTools_->ReadValueBranch<Float_t>("Jet3_btag"+btagAlgo);
     double Jet4_btagDisc = readerTools_->ReadValueBranch<Float_t>("Jet4_btag"+btagAlgo);
     double Jet5_btagDisc = readerTools_->ReadValueBranch<Float_t>("Jet5_btag"+btagAlgo);
     int Jet1_flavor = readerTools_->ReadValueBranch<Int_t>("Jet1_HadronFlavor");
     int Jet2_flavor = readerTools_->ReadValueBranch<Int_t>("Jet2_HadronFlavor");
     int Jet3_flavor = readerTools_->ReadValueBranch<Int_t>("Jet3_HadronFlavor");
     int Jet4_flavor = readerTools_->ReadValueBranch<Int_t>("Jet4_HadronFlavor");
     int Jet5_flavor = readerTools_->ReadValueBranch<Int_t>("Jet5_HadronFlavor");
     std::string sfSuffix = btagWP+btagAlgo;
     double Jet1_btagSF = Jet1_flavor==0 ? readerTools_->ReadValueBranch<Float_t>("Jet1_btagSF"+sfSuffix+"Incl") : readerTools_->ReadValueBranch<Float_t>("Jet1_btagSF"+sfSuffix+"Comb");
     double Jet2_btagSF = Jet2_flavor==0 ? readerTools_->ReadValueBranch<Float_t>("Jet2_btagSF"+sfSuffix+"Incl") : readerTools_->ReadValueBranch<Float_t>("Jet2_btagSF"+sfSuffix+"Comb");
     double Jet3_btagSF = Jet3_flavor==0 ? readerTools_->ReadValueBranch<Float_t>("Jet3_btagSF"+sfSuffix+"Incl") : readerTools_->ReadValueBranch<Float_t>("Jet3_btagSF"+sfSuffix+"Comb");
     double Jet4_btagSF = Jet4_flavor==0 ? readerTools_->ReadValueBranch<Float_t>("Jet4_btagSF"+sfSuffix+"Incl") : readerTools_->ReadValueBranch<Float_t>("Jet4_btagSF"+sfSuffix+"Comb");
     double Jet5_btagSF = Jet5_flavor==0 ? readerTools_->ReadValueBranch<Float_t>("Jet5_btagSF"+sfSuffix+"Incl") : readerTools_->ReadValueBranch<Float_t>("Jet5_btagSF"+sfSuffix+"Comb");

     float weightZeroBJets = 1.0;
     float weightAtLeastOneBJet = 1.0;
     float weightAtLeastTwoBJets = 1.0;
     float weightAtLeastTwoBJetsOneBtagBin = 1.0;
     float weightZeroBJetsBeyondLeadingTwo = 1.0;
     float weightAtLeastOneBJetBeyondLeadingTwo = 1.0;
     float weightZeroBJetsUpShift = 1.0;
     float weightAtLeastOneBJetUpShift = 1.0;
     float weightZeroBJetsDownShift = 1.0;
     float weightAtLeastOneBJetDownShift = 1.0;

     double discArray[5] = {Jet1_btagDisc, Jet2_btagDisc, Jet3_btagDisc, Jet4_btagDisc, Jet5_btagDisc};
     if(!isData())
     {
       float weightAtLeastTwoBJetsOneBtagBin = 0.0;
       // calculate and apply scale factors to MC only
       double sfArray[5] = {Jet1_btagSF, Jet2_btagSF, Jet3_btagSF, Jet4_btagSF, Jet5_btagSF };
       for(unsigned int iJet = 0; iJet < 5; ++iJet) {
         if (discArray[iJet] > btagCut) {
           weightZeroBJets*=(1-sfArray[iJet]);
           float tmpWeight = 1.0;
           for(unsigned int jJet = 0; jJet < 5; ++jJet) {
             if (discArray[jJet] > btagCut && jJet != iJet)
               tmpWeight*=(1-sfArray[jJet]);
           }
           weightAtLeastTwoBJetsOneBtagBin+=tmpWeight*sfArray[iJet];
         }
       }
       weightAtLeastOneBJet = 1 - weightZeroBJets;
       weightAtLeastTwoBJets = 1 - weightZeroBJets - weightAtLeastTwoBJetsOneBtagBin;
       //
       //if ( Jet3_btagDisc > btagCut ) weightZeroBJetsBeyondLeadingTwo*=(1-Jet3_btagSF);
       //if ( Jet4_btagDisc > btagCut ) weightZeroBJetsBeyondLeadingTwo*=(1-Jet4_btagSF);
       //if ( Jet5_btagDisc > btagCut ) weightZeroBJetsBeyondLeadingTwo*=(1-Jet5_btagSF);
       //weightAtLeastOneBJetBeyondLeadingTwo = 1 - weightZeroBJetsBeyondLeadingTwo;
       //
       //if ( Jet1_btagDisc > btagCut ) weightZeroBJetsUpShift*=(1-Jet1_btagSF);
       //if ( Jet2_btagDisc > btagCut ) weightZeroBJetsUpShift*=(1-Jet2_btagSF);
       //if ( Jet3_btagDisc > btagCut ) weightZeroBJetsUpShift*=(1-Jet3_btagSF);
       //if ( Jet4_btagDisc > btagCut ) weightZeroBJetsUpShift*=(1-Jet4_btagSF);
       //if ( Jet5_btagDisc > btagCut ) weightZeroBJetsUpShift*=(1-Jet5_btagSF);
       //weightAtLeastOneBJetUpShift = 1 - weightZeroBJetsUpShift;
       ////
       //if ( Jet1_btagDisc > btagCut ) weightZeroBJetsDownShift*=(1-Jet1_btagSF);
       //if ( Jet2_btagDisc > btagCut ) weightZeroBJetsDownShift*=(1-Jet2_btagSF);
       //if ( Jet3_btagDisc > btagCut ) weightZeroBJetsDownShift*=(1-Jet3_btagSF);
       //if ( Jet4_btagDisc > btagCut ) weightZeroBJetsDownShift*=(1-Jet4_btagSF);
       //if ( Jet5_btagDisc > btagCut ) weightZeroBJetsDownShift*=(1-Jet5_btagSF);
       //weightAtLeastOneBJetDownShift = 1 - weightZeroBJetsDownShift;
     }
     int nBJet_ptCut  = 0;
     int nBJet_ptCut_beyondLeadingTwo = 0;

     for(unsigned int iJet = 0; iJet < 5; ++iJet) {
       if (discArray[iJet] > btagCut)
         nBJet_ptCut++;
     }

     if ( Jet3_btagDisc > btagCut ) nBJet_ptCut_beyondLeadingTwo++;
     if ( Jet4_btagDisc > btagCut ) nBJet_ptCut_beyondLeadingTwo++;
     if ( Jet5_btagDisc > btagCut ) nBJet_ptCut_beyondLeadingTwo++;

     //std::cout << "INFO: weightAtLeastOneBJet=" << weightAtLeastOneBJet << "; while weightZeroBJets=" << weightZeroBJets << "; this event has " << nJet_store << " stored jets, with " <<
     // nBJet_medium_ptCut << " passing the medium Btag cut." << std::endl;

     //--------------------------------------------------------------------------
     // Evaluate the cuts
     //--------------------------------------------------------------------------

     evaluateCuts();

     //std::cout << "getVariableValue(\"PassNEle\")=" << getVariableValue("PassNEle") << "; passedCut(\"PassNEle\")=" << passedCut("PassNEle") << std::endl;
     //std::cout << "getVariableValue(\"asym_M_ej_LQ300\")=" << getVariableValue("asym_M_ej_LQ300") << "; passedCut(\"asym_M_ej_LQ300\")=" << passedCut("asym_M_ej_LQ300") << std::endl;
     //--------------------------------------------------------------------------
     // Did we at least pass the noise filtes?
     //--------------------------------------------------------------------------

     bool passed_minimum = ( passedAllPreviousCuts("PassEcalBadCalibFilter") && passedCut ("PassEcalBadCalibFilter"));

     //--------------------------------------------------------------------------
     // Did we pass preselection?
     //--------------------------------------------------------------------------

     bool passed_preselection = ( passedAllPreviousCuts("preselection") && passedCut ("preselection") );
     std::string preselectionCut = "preselection";

     //--------------------------------------------------------------------------
     // Are we in the region of interest?
     //--------------------------------------------------------------------------

     bool passed_region_of_interest = bool (
         passed_preselection && M_e1e2 > 170. && sT_eejj > 900.0
         );

     //--------------------------------------------------------------------------
     // Did we pass any final selection cuts?
     //--------------------------------------------------------------------------

     passed_vector.clear();
     if(doFinalSelections)
     {
       for (int i_lq_mass = 0; i_lq_mass < n_lq_mass; ++i_lq_mass ){
         int lq_mass = LQ_MASS[i_lq_mass];
         //sprintf(cut_name, "M_e1e2_LQ%d", lq_mass );
         //sprintf(cut_name, "min_M_ej_LQ%d", lq_mass ); // this is actually the last cut in the cut file...!
         // TODO FIXME the right way; hack for now
         sprintf(cut_name, "BDTOutput_LQ%d", lq_mass ); // this is actually the last cut in the cut file...!
         bool decision = bool ( passedAllPreviousCuts(cut_name) && passedCut (cut_name));
         passed_vector.push_back (decision);
       }
     }

     //--------------------------------------------------------------------------
     // Fill plots with no selection applied
     //--------------------------------------------------------------------------

     FillUserHist( "PileupWeight"   , pileup_weight );
     FillUserHist( "GeneratorWeight", gen_weight ) ;

     //--------------------------------------------------------------------------
     // Fill noise filter level plots
     //--------------------------------------------------------------------------

     int nVertex = readerTools_->ReadValueBranch<Int_t>("nVertex");
     if ( passed_minimum && isData() ){
       FillUserHist ("run_HLT", run );
       FillUserTProfile("run_vs_nvtx_HLT", run, nVertex, 1);
     }

     //--------------------------------------------------------------------------
     // Print if desired
     //--------------------------------------------------------------------------

     //if ( !isData() ) {
     //  unsigned int ls = readerTools_->ReadValueBranch<UInt_t>("ls");
     //  unsigned long long int event = readerTools_->ReadValueBranch<ULong64_t>("event");
     //  float recoSFEle1 = readerTools_->ReadValueBranch<Float_t>("Ele1_RecoSF");
     //  float recoSFEle2 = readerTools_->ReadValueBranch<Float_t>("Ele2_RecoSF");
     //  float looseSFEle1 = readerTools_->ReadValueBranch<Float_t>("Ele1_EGMLooseIDSF");
     //  float looseSFEle2 = readerTools_->ReadValueBranch<Float_t>("Ele2_EGMLooseIDSF");
     //  float trigSFEle1 = readerTools_->ReadValueBranch<Float_t>("Ele1_TrigSF");
     //  float trigSFEle2 = readerTools_->ReadValueBranch<Float_t>("Ele2_TrigSF");
     //  std::cout.precision(0);
     //  std::cout << fixed <<  "Run = " << run << ", event = " << event << ", ls = " << ls << std::endl;
     //  std::cout.precision(3);
     //  std::cout << fixed <<  "  Mej      = " << M_ej_avg << std::endl;
     //  std::cout << fixed <<  "  Mee      = " << M_e1e2 << std::endl;
     //  std::cout << fixed <<  "  sT       = " << sT_eejj << std::endl;
     //  std::cout << fixed <<  "  Ele1 Pt  = " << Ele1_Pt << "\t, Eta = " << Ele1_Eta << "\t, Phi = " << Ele1_Phi << std::endl;
     //  std::cout << fixed <<  "  Ele1 recoSF  = " << recoSFEle1 << "\t, looseSF = " << looseSFEle1 << "\t, trigSF = " << trigSFEle1 << std::endl;
     //  std::cout << fixed <<  "  Ele2 recoSF  = " << recoSFEle2 << "\t, looseSF = " << looseSFEle2 << "\t, trigSF = " << trigSFEle2 << std::endl;
     //  std::cout << fixed <<  "  Ele2 Pt  = " << Ele2_Pt << "\t, Eta = " << Ele2_Eta << "\t, Phi = " << Ele2_Phi << std::endl;
     //  std::cout << fixed <<  "  Jet1 Pt  = " << Jet1_Pt << "\t, Eta = " << Jet1_Eta << "\t, Phi = " << Jet1_Phi << std::endl;
     //  std::cout << fixed <<  "  Jet2 Pt  = " << Jet2_Pt << "\t, Eta = " << Jet2_Eta << "\t, Phi = " << Jet2_Phi << std::endl;
     //}

     //--------------------------------------------------------------------------
     // Determine what kind of event this is:
     // - EB-EB
     // - EB-EE
     // - EE-EE
     //--------------------------------------------------------------------------

     bool isEB1 = ( fabs(Ele1_Eta) < eleEta_bar_max  ) ;
     bool isEE1 = ( fabs(Ele1_Eta) > eleEta_end_min &&
         fabs(Ele1_Eta) < eleEta_end_max ) ;

     bool isEB2 = ( fabs(Ele2_Eta) < eleEta_bar_max  ) ;
     bool isEE2 = ( fabs(Ele2_Eta) > eleEta_end_min &&
         fabs(Ele2_Eta) < eleEta_end_max ) ;

     bool isEBEB = ( isEB1 && isEB2 ) ;
     bool isEBEE = ( ( isEB1 && isEE2 ) ||
         ( isEE1 && isEB2 ) );
     bool isEEEE = ( isEE1  && isEE2  );
     bool isEB   = ( isEBEB || isEBEE );

     //--------------------------------------------------------------------------
     // Fill background control region plots
     //--------------------------------------------------------------------------
     if(passed_preselection) {
       FillUserHist("Mee_BkgControlRegion"                    ,    M_e1e2,    pileup_weight * gen_weight , "preselection");
       if(nBJet_ptCut>=1)
         FillUserHist( "Mee_BkgControlRegion_gteOneBtaggedJet"      , M_e1e2,  pileup_weight * gen_weight * weightAtLeastOneBJet, "preselection" ) ;
       if(nBJet_ptCut>=2)
         FillUserHist( "Mee_BkgControlRegion_gteTwoBtaggedJets"      , M_e1e2,  pileup_weight * gen_weight * weightAtLeastTwoBJets, "preselection" ) ;
       if      ( isEB   ) FillUserHist( "Mee_EB_BkgControlRegion"  , M_e1e2, pileup_weight * gen_weight, "preselection" );
       if      ( isEBEB ) FillUserHist( "Mee_EBEB_BkgControlRegion", M_e1e2, pileup_weight * gen_weight, "preselection" );
       else if ( isEBEE ) FillUserHist( "Mee_EBEE_BkgControlRegion", M_e1e2, pileup_weight * gen_weight, "preselection" );
       else if ( isEEEE ) FillUserHist( "Mee_EEEE_BkgControlRegion", M_e1e2, pileup_weight * gen_weight, "preselection" );
       // scale factor dependence histos
       if ( nJet_ptCut == 2 )
         FillUserHist("Mee_NJetEq2_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       else if( nJet_ptCut == 3 )
         FillUserHist("Mee_NJetEq3_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       else if( nJet_ptCut == 4 )
         FillUserHist("Mee_NJetEq4_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       else if( nJet_ptCut == 5 )
         FillUserHist("Mee_NJetEq5_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       else if( nJet_ptCut == 6 )
         FillUserHist("Mee_NJetEq6_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       else if( nJet_ptCut == 7 )
         FillUserHist("Mee_NJetEq7_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       if ( nJet_ptCut >= 3 )
         FillUserHist("Mee_NJetGeq3_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       if ( nJet_ptCut >= 4 )
         FillUserHist("Mee_NJetGeq4_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj >= 300 && sT_eejj < 500)
         FillUserHist("Mee_sT300To500_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       else if (sT_eejj >= 500 && sT_eejj < 750)
         FillUserHist("Mee_sT500To750_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       else if (sT_eejj >= 750 && sT_eejj < 1250)
         FillUserHist("Mee_sT750To1250_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       else if (sT_eejj >= 1250)
         FillUserHist("Mee_sT1250ToInf_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       if (M_ej_min >= 100 && M_ej_min < 200)
         FillUserHist("Mee_MejMin100To200_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       else if (M_ej_min >= 200 && M_ej_min < 300)
         FillUserHist("Mee_MejMin200To300_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       else if (M_ej_min >= 300 && M_ej_min < 400)
         FillUserHist("Mee_MejMin300To400_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       else if (M_ej_min >= 400 && M_ej_min < 500)
         FillUserHist("Mee_MejMin400To500_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       else if (M_ej_min >= 500 && M_ej_min < 650)
         FillUserHist("Mee_MejMin500To650_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
       else if (M_ej_min >= 650)
         FillUserHist("Mee_MejMin650ToInf_BkgControlRegion", M_e1e2                         , pileup_weight * gen_weight );
     }

     //--------------------------------------------------------------------------
     // Fill preselection plots
     //--------------------------------------------------------------------------
     if ( passed_preselection ) {

       //// printing
       //unsigned int ls = readerTools_->ReadValueBranch<UInt_t>("ls");
       //unsigned long long int event = readerTools_->ReadValueBranch<ULong64_t>("event");
       //std::cout.precision(0);
       //std::cout << fixed << "Run = " << run << ", ls = " << ls << ", event = " << event << std::endl;
       //std::cout.precision(3);
       //std::cout << fixed <<  "  Mej      = " << M_ej_avg << std::endl;
       //std::cout << fixed <<  "  Mee      = " << M_e1e2 << std::endl;
       //std::cout << fixed <<  "  sT       = " << sT_eejj << std::endl;
       //std::cout << fixed <<  "  Ele1 Pt  = " << Ele1_Pt << "\t, Eta = " << Ele1_Eta << "\t, Phi = " << Ele1_Phi << std::endl;
       ////std::cout << fixed <<  "  Ele1 dPhi  = " << Ele1_DeltaPhiTrkSC << "\t, HoE = " << Ele1_HoE << "\t, sIetaIeta = " << Ele1_SigmaIEtaIEta << std::endl;
       //std::cout << fixed <<  "  Ele2 Pt  = " << Ele2_Pt << "\t, Eta = " << Ele2_Eta << "\t, Phi = " << Ele2_Phi << std::endl;
       //std::cout << fixed <<  "  Jet1 Pt  = " << Jet1_Pt << "\t, Eta = " << Jet1_Eta << "\t, Phi = " << Jet1_Phi << std::endl;
       //std::cout << fixed <<  "  Jet2 Pt  = " << Jet2_Pt << "\t, Eta = " << Jet2_Eta << "\t, Phi = " << Jet2_Phi << std::endl;
       //--------------------------------------------------------------------------
       // Recalculate some variables
       //--------------------------------------------------------------------------

       TLorentzVector e1, j1, e2, j2,j3, mu, met;
       TLorentzVector eejj, e1e2mu;
       TLorentzVector eej, ejj, ee;
       TLorentzVector e1Uncorr, e2Uncorr, eeUncorr;
       TLorentzVector e1j3, e2j3, j1j3, j2j3, j1j2, j1j2j3, eejjj;
       double Muon1_Pt = readerTools_->ReadValueBranch<Float_t>("Muon1_Pt");
       double Muon1_Eta = readerTools_->ReadValueBranch<Float_t>("Muon1_Eta");
       double Muon1_Phi = readerTools_->ReadValueBranch<Float_t>("Muon1_Phi");
       double Muon2_Pt = readerTools_->ReadValueBranch<Float_t>("Muon2_Pt");
       double Muon2_Eta = readerTools_->ReadValueBranch<Float_t>("Muon2_Eta");
       double Muon2_Phi = readerTools_->ReadValueBranch<Float_t>("Muon2_Phi");

       e1.SetPtEtaPhiM ( Ele1_Pt, Ele1_Eta, Ele1_Phi, 0.0 );
       e2.SetPtEtaPhiM ( Ele2_Pt, Ele2_Eta, Ele2_Phi, 0.0 );
       j1.SetPtEtaPhiM ( Jet1_Pt, Jet1_Eta, Jet1_Phi, 0.0 );
       j2.SetPtEtaPhiM ( Jet2_Pt, Jet2_Eta, Jet2_Phi, 0.0 );
       mu.SetPtEtaPhiM ( Muon1_Pt,Muon1_Eta,Muon1_Phi, 0.0 );
       met.SetPtEtaPhiM ( PFMET_Type1_Pt, 0.0, PFMET_Type1_Phi, 0.0 );

       eejj = e1 + e2 + j1 + j2 ;
       eej  = e1 + e2 + j1;
       ejj  = e1 + j1 + j2;
       ee   = e1 + e2;
       j1j2 = j1 + j2;

       e1Uncorr.SetPtEtaPhiM ( Ele1_Pt/readerTools_->ReadValueBranch<Float_t>("Ele1_ECorr"), Ele1_Eta, Ele1_Phi, 0.0 );
       e2Uncorr.SetPtEtaPhiM ( Ele2_Pt/readerTools_->ReadValueBranch<Float_t>("Ele2_ECorr"), Ele2_Eta, Ele2_Phi, 0.0 );
       eeUncorr = e1Uncorr + e2Uncorr;
       double M_e1e2Uncorr = eeUncorr.M();

       double min_DR_EleJet;
       double DR_Ele1Jet3;
       double DR_Ele2Jet3;
       double DR_Ele1Ele2 = e1.DeltaR( e2 );

       double M_eejj = eejj.M();
       double M_eej  = eej.M();
       double M_ejj  = ejj.M();

       double Pt_j1j2 = j1j2.Pt();
       double Pt_j1j3;
       double Pt_j2j3;
       double Pt_j1j2j3;

       double M_j1j3, M_j2j3;
       double M_e1j3, M_e2j3;
       double M_eejjj;

       double min_DeltaR_Zj = 999.;
       if ( ee.DeltaR ( j1 ) < min_DeltaR_Zj ) min_DeltaR_Zj = ee.DeltaR ( j1 );
       if ( ee.DeltaR ( j2 ) < min_DeltaR_Zj ) min_DeltaR_Zj = ee.DeltaR ( j2 );
       double DR_ZJ1 = ee.DeltaR ( j1 );
       double DR_ZJ2 = ee.DeltaR ( j2 );

       if ( nJet_ptCut > 2 ) {
         j3.SetPtEtaPhiM ( readerTools_->ReadValueBranch<Float_t>("Jet3_Pt"), readerTools_->ReadValueBranch<Float_t>("Jet3_Eta"), readerTools_->ReadValueBranch<Float_t>("Jet3_Phi"), 0.0 );

         e1j3 = e1 + j3;
         e2j3 = e2 + j3;
         j1j3 = j1 + j3;
         j2j3 = j2 + j3;
         j1j2j3 = j1 + j2 + j3;
         eejjj = e1 + e2 + j1 + j2 + j3;

         DR_Ele1Jet3 = e1.DeltaR( j3 );
         DR_Ele2Jet3 = e2.DeltaR( j3 );
         M_e1j3 = e1j3.M();
         M_e2j3 = e2j3.M();
         M_j1j3 = j1j3.M();
         M_j2j3 = j2j3.M();
         Pt_j1j3 = j1j3.Pt();
         Pt_j2j3 = j2j3.Pt();
         Pt_j1j2j3 = j1j2j3.Pt();
         M_eejjj = eejjj.M();
       }

       if ( DR_Ele1Jet1 < min_DR_EleJet ) min_DR_EleJet = DR_Ele1Jet1;
       if ( DR_Ele1Jet2 < min_DR_EleJet ) min_DR_EleJet = DR_Ele1Jet2;
       if ( DR_Ele2Jet1 < min_DR_EleJet ) min_DR_EleJet = DR_Ele2Jet1;
       if ( DR_Ele2Jet2 < min_DR_EleJet ) min_DR_EleJet = DR_Ele2Jet2;
       if (nJet_ptCut > 2 ) {
         if ( DR_Ele1Jet3 < min_DR_EleJet ) min_DR_EleJet = DR_Ele1Jet3;
         if ( DR_Ele2Jet3 < min_DR_EleJet ) min_DR_EleJet = DR_Ele2Jet3;
       }

       //--------------------------------------------------------------------------
       // Electron quality histograms (preselection)
       //--------------------------------------------------------------------------
       double Ele1_CorrIsolation        = readerTools_->ReadValueBranch<Float_t>("Ele1_CorrIsolation")      ;
       double Ele1_DeltaEtaTrkSC        = readerTools_->ReadValueBranch<Float_t>("Ele1_DeltaEtaTrkSC")      ;
       double Ele1_EcalIsolation        = readerTools_->ReadValueBranch<Float_t>("Ele1_EcalIsolation")      ;
       double Ele1_HcalIsolation        = readerTools_->ReadValueBranch<Float_t>("Ele1_HcalIsolation")      ;
       double Ele1_TrkIsolation         = readerTools_->ReadValueBranch<Float_t>("Ele1_TrkIsolation")       ;
       bool Ele1_HasMatchedPhot         = readerTools_->ReadValueBranch<Bool_t>("Ele1_HasMatchedPhot")     ;
       double Ele1_HoE                  = readerTools_->ReadValueBranch<Float_t>("Ele1_HoE")                ;
       double Ele1_LeadVtxDistXY        = readerTools_->ReadValueBranch<Float_t>("Ele1_LeadVtxDistXY")      ;
       double Ele1_LeadVtxDistZ         = readerTools_->ReadValueBranch<Float_t>("Ele1_LeadVtxDistZ")       ;
       int Ele1_MissingHits          = readerTools_->ReadValueBranch<Int_t>("Ele1_MissingHits")        ;
       double Ele1_SCEta                = readerTools_->ReadValueBranch<Float_t>("Ele1_SCEta");
       double Ele1_Full5x5SigmaIEtaIEta = readerTools_->ReadValueBranch<Float_t>("Ele1_Full5x5SigmaIEtaIEta");
       int Ele1_Charge               = readerTools_->ReadValueBranch<Int_t>("Ele1_Charge");
       //double Ele1_PtHeep               = readerTools_->ReadValueBranch<Float_t>("Ele1_PtHeep");

       FillUserHist("CorrIsolation_1stEle_PAS"       ,Ele1_CorrIsolation       , pileup_weight * gen_weight    );
       FillUserHist("DeltaEtaTrkSC_1stEle_PAS"       ,Ele1_DeltaEtaTrkSC       , pileup_weight * gen_weight    );
       FillUserHist("EcalIsolation_1stEle_PAS"       ,Ele1_EcalIsolation       , pileup_weight * gen_weight    );
       FillUserHist("HcalIsolation_1stEle_PAS"       ,Ele1_HcalIsolation       , pileup_weight * gen_weight    );
       FillUserHist("TrkIsolation_1stEle_PAS"        ,Ele1_TrkIsolation        , pileup_weight * gen_weight    );
       FillUserHist("HasMatchedPhot_1stEle_PAS"      ,Ele1_HasMatchedPhot      , pileup_weight * gen_weight    );
       FillUserHist("HoE_1stEle_PAS"                 ,Ele1_HoE                 , pileup_weight * gen_weight    );
       FillUserHist("LeadVtxDistXY_1stEle_PAS"       ,Ele1_LeadVtxDistXY       , pileup_weight * gen_weight    );
       FillUserHist("LeadVtxDistZ_1stEle_PAS"        ,Ele1_LeadVtxDistZ        , pileup_weight * gen_weight    );
       FillUserHist("MissingHits_1stEle_PAS"         ,Ele1_MissingHits         , pileup_weight * gen_weight    );
       if ( fabs(Ele1_Eta) < eleEta_bar ) {
         FillUserHist("Full5x5SigmaIEtaIEta_Barrel_1stEle_PAS", Ele1_Full5x5SigmaIEtaIEta                  , pileup_weight * gen_weight    );
       }
       else if ( fabs(Ele1_Eta) > eleEta_end1_min && fabs(Ele2_Eta) < eleEta_end2_max ){
         FillUserHist("Full5x5SigmaIEtaIEta_Endcap_1stEle_PAS", Ele1_Full5x5SigmaIEtaIEta                  , pileup_weight * gen_weight    );
       }
       FillUserHist("ECorrEle1_PAS", readerTools_->ReadValueBranch<Float_t>("Ele1_ECorr"), pileup_weight * gen_weight);
       FillUserHist("ECorrEle2_PAS", readerTools_->ReadValueBranch<Float_t>("Ele2_ECorr"), pileup_weight * gen_weight);

      double Ele2_CorrIsolation        = readerTools_->ReadValueBranch<Float_t>("Ele2_CorrIsolation")      ;
      double Ele2_DeltaEtaTrkSC        = readerTools_->ReadValueBranch<Float_t>("Ele2_DeltaEtaTrkSC")      ;
      double Ele2_EcalIsolation        = readerTools_->ReadValueBranch<Float_t>("Ele2_EcalIsolation")      ;
      double Ele2_HcalIsolation        = readerTools_->ReadValueBranch<Float_t>("Ele2_HcalIsolation")      ;
      double Ele2_TrkIsolation         = readerTools_->ReadValueBranch<Float_t>("Ele2_TrkIsolation")       ;
      bool Ele2_HasMatchedPhot         = readerTools_->ReadValueBranch<Bool_t>("Ele2_HasMatchedPhot")     ;
      double Ele2_HoE                  = readerTools_->ReadValueBranch<Float_t>("Ele2_HoE")                ;
      double Ele2_LeadVtxDistXY        = readerTools_->ReadValueBranch<Float_t>("Ele2_LeadVtxDistXY")      ;
      double Ele2_LeadVtxDistZ         = readerTools_->ReadValueBranch<Float_t>("Ele2_LeadVtxDistZ")       ;
      int Ele2_MissingHits          = readerTools_->ReadValueBranch<Int_t>("Ele2_MissingHits")        ;
      double Ele2_SCEta                = readerTools_->ReadValueBranch<Float_t>("Ele2_SCEta");
      double Ele2_Full5x5SigmaIEtaIEta = readerTools_->ReadValueBranch<Float_t>("Ele2_Full5x5SigmaIEtaIEta");
      int Ele2_Charge               = readerTools_->ReadValueBranch<Int_t>("Ele2_Charge");
      //double Ele2_PtHeep               = readerTools_->ReadValueBranch<Float_t>("Ele2_PtHeep");

       FillUserHist("CorrIsolation_2ndEle_PAS"       ,Ele2_CorrIsolation            , pileup_weight * gen_weight    );
       FillUserHist("DeltaEtaTrkSC_2ndEle_PAS"       ,Ele2_DeltaEtaTrkSC            , pileup_weight * gen_weight    );
       FillUserHist("EcalIsolation_2ndEle_PAS"       ,Ele2_EcalIsolation            , pileup_weight * gen_weight    );
       FillUserHist("HcalIsolation_2ndEle_PAS"       ,Ele2_HcalIsolation            , pileup_weight * gen_weight    );
       FillUserHist("TrkIsolation_2ndEle_PAS"        ,Ele2_TrkIsolation             , pileup_weight * gen_weight    );
       FillUserHist("HasMatchedPhot_2ndEle_PAS"      ,Ele2_HasMatchedPhot           , pileup_weight * gen_weight    );
       FillUserHist("HoE_2ndEle_PAS"                 ,Ele2_HoE                      , pileup_weight * gen_weight    );
       FillUserHist("LeadVtxDistXY_2ndEle_PAS"       ,Ele2_LeadVtxDistXY            , pileup_weight * gen_weight    );
       FillUserHist("LeadVtxDistZ_2ndEle_PAS"        ,Ele2_LeadVtxDistZ             , pileup_weight * gen_weight    );
       FillUserHist("MissingHits_2ndEle_PAS"         ,Ele2_MissingHits              , pileup_weight * gen_weight    );
       if ( fabs(Ele2_Eta) < eleEta_bar ) {
         FillUserHist("Full5x5SigmaIEtaIEta_Barrel_2ndEle_PAS", Ele2_Full5x5SigmaIEtaIEta                  , pileup_weight * gen_weight    );
       }
       else if ( fabs(Ele2_Eta) > eleEta_end1_min && fabs(Ele2_Eta) < eleEta_end2_max ){
         FillUserHist("Full5x5SigmaIEtaIEta_Endcap_2ndEle_PAS", Ele2_Full5x5SigmaIEtaIEta                  , pileup_weight * gen_weight    );
       }

       //--------------------------------------------------------------------------
       // Preselection histograms
       //--------------------------------------------------------------------------
       double M_j1j2 = readerTools_->ReadValueBranch<Float_t>("M_j1j2");

       FillUserHist( "Ptj1j2_PAS"           , Pt_j1j2                        , pileup_weight * gen_weight );
       FillUserHist( "Ptee_Minus_Ptj1j2_PAS", Pt_e1e2 - Pt_j1j2              , pileup_weight * gen_weight );
       //FillUserHist("ProcessID_PAS"         , ProcessID                      , pileup_weight * gen_weight );
       FillUserHist("minDR_EleJet_PAS"      , min_DR_EleJet                  , pileup_weight * gen_weight );
       FillUserHist("DR_Ele1Ele2_PAS"        , DR_Ele1Ele2                    , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("EleChargeSum_PAS"      , Ele1_Charge + Ele2_Charge      , pileup_weight * gen_weight );
       FillUserHist("nElectron_PAS"         , nEle_ptCut                     , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("nMuon_PAS"             , nMuon_ptCut                    , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("nJet_PAS"              , nJet_ptCut                     , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Pt1stEle_PAS"            , Ele1_Pt                        , pileup_weight * gen_weight, preselectionCut );
       //FillUserHist("PtHeep1stEle_PAS"        , Ele1_PtHeep                    , pileup_weight * gen_weight );
       FillUserHist("Eta1stEle_PAS"            , Ele1_Eta                       , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("SCEta1stEle_PAS"          , Ele1_SCEta                     , pileup_weight * gen_weight, preselectionCut );
       //FillUserHist("DeltaEtaEleTrk1stEle_Presel"       , fabs(Ele1_Eta-Ele1_TrkEta)                   , pileup_weight * gen_weight );
       FillUserHist("Phi1stEle_PAS"            , Ele1_Phi                       , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Pt2ndEle_PAS"            , Ele2_Pt                        , pileup_weight * gen_weight, preselectionCut );
       //FillUserHist("PtHeep2ndEle_PAS"        , Ele2_PtHeep                    , pileup_weight * gen_weight );
       FillUserHist("Eta2ndEle_PAS"            , Ele2_Eta                       , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("SCEta2ndEle_PAS"          , Ele2_SCEta                     , pileup_weight * gen_weight, preselectionCut );
       //FillUserHist("DeltaEtaEleTrk2ndEle_Presel"       , fabs(Ele2_Eta-Ele2_TrkEta)                   , pileup_weight * gen_weight );
       FillUserHist("Phi2ndEle_PAS"        , Ele2_Phi                       , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Charge1stEle_PAS"        , Ele1_Charge                    , pileup_weight * gen_weight );
       FillUserHist("Charge2ndEle_PAS"        , Ele2_Charge                    , pileup_weight * gen_weight );
       FillUserHist("MET_PAS"               , PFMET_Type1_Pt              , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("METPhi_PAS"        , PFMET_Type1_Phi             , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Pt1stJet_PAS"          , Jet1_Pt                        , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Pt2ndJet_PAS"          , Jet2_Pt                        , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Eta1stJet_PAS"         , Jet1_Eta                       , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Eta2ndJet_PAS"         , Jet2_Eta                       , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Phi1stJet_PAS"        , Jet1_Phi                       , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Phi2ndJet_PAS"        , Jet2_Phi                       , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("sTlep_PAS"             , Ele1_Pt + Ele2_Pt              , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("sTjet_PAS"             , Jet1_Pt + Jet2_Pt              , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("sT_PAS"                , sT_eejj                        , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("sT_zjj_PAS"            , sT_zjj                         , pileup_weight * gen_weight );
       FillUserHist("Mjj_PAS"            , M_j1j2                         , pileup_weight * gen_weight );
       FillUserHist("Mee_PAS"            , M_e1e2                         , pileup_weight * gen_weight, preselectionCut );
       FillUserHist( "MTenu_PAS"            , readerTools_->ReadValueBranch<Float_t>("MT_Ele1MET")                     , pileup_weight * gen_weight );
       FillUserHist("Me1j1_PAS"             , M_e1j1                         , pileup_weight * gen_weight, preselectionCut );
       // muon kinematics
       FillUserHist("Pt1stMuon_PAS"          , Muon1_Pt                        , pileup_weight * gen_weight );
       FillUserHist("Eta1stMuon_PAS"        , Muon1_Eta                       , pileup_weight * gen_weight );
       FillUserHist("Phi1stMuon_PAS"        , Muon1_Phi                       , pileup_weight * gen_weight );
       FillUserHist("Pt2ndMuon_PAS"          , Muon2_Pt                        , pileup_weight * gen_weight );
       FillUserHist("Eta2ndMuon_PAS"        , Muon2_Eta                       , pileup_weight * gen_weight );
       FillUserHist("Phi2ndMuon_PAS"        , Muon2_Phi                       , pileup_weight * gen_weight );
       // scale factor dependence histos
       if ( nJet_ptCut == 2 )
         FillUserHist("Mee_NJetEq2_PAS", M_e1e2                         , pileup_weight * gen_weight );
       else if( nJet_ptCut == 3 )
         FillUserHist("Mee_NJetEq3_PAS", M_e1e2                         , pileup_weight * gen_weight );
       else if( nJet_ptCut == 4 )
         FillUserHist("Mee_NJetEq4_PAS", M_e1e2                         , pileup_weight * gen_weight );
       else if( nJet_ptCut == 5 )
         FillUserHist("Mee_NJetEq5_PAS", M_e1e2                         , pileup_weight * gen_weight );
       else if( nJet_ptCut == 6 )
         FillUserHist("Mee_NJetEq6_PAS", M_e1e2                         , pileup_weight * gen_weight );
       else if( nJet_ptCut == 7 )
         FillUserHist("Mee_NJetEq7_PAS", M_e1e2                         , pileup_weight * gen_weight );
       //
       if ( nJet_ptCut >= 3 )
         FillUserHist("Mee_NJetGeq3_PAS", M_e1e2                         , pileup_weight * gen_weight );
       if ( nJet_ptCut >= 4 )
         FillUserHist("Mee_NJetGeq4_PAS", M_e1e2                         , pileup_weight * gen_weight );
       //
       if (sT_eejj >= 300 && sT_eejj < 500)
         FillUserHist("Mee_sT300To500_PAS", M_e1e2                         , pileup_weight * gen_weight );
       else if (sT_eejj >= 500 && sT_eejj < 750)
         FillUserHist("Mee_sT500To750_PAS", M_e1e2                         , pileup_weight * gen_weight );
       else if (sT_eejj >= 750 && sT_eejj < 1250)
         FillUserHist("Mee_sT750To1250_PAS", M_e1e2                         , pileup_weight * gen_weight );
       else if (sT_eejj >= 1250)
         FillUserHist("Mee_sT1250ToInf_PAS", M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 340)
         FillUserHist( "Mee_sT340_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 405)
         FillUserHist( "Mee_sT405_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 470)
         FillUserHist( "Mee_sT470_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 535)
         FillUserHist( "Mee_sT535_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 595)
         FillUserHist( "Mee_sT595_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 660)
         FillUserHist( "Mee_sT660_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 720)
         FillUserHist( "Mee_sT720_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 780)
         FillUserHist( "Mee_sT780_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 840)
         FillUserHist( "Mee_sT840_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 900)
         FillUserHist( "Mee_sT900_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 960)
         FillUserHist( "Mee_sT960_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1015)
         FillUserHist( "Mee_sT1015_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1075)
         FillUserHist( "Mee_sT1075_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1130)
         FillUserHist( "Mee_sT1130_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1190)
         FillUserHist( "Mee_sT1190_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1245)
         FillUserHist( "Mee_sT1245_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1300)
         FillUserHist( "Mee_sT1300_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1355)
         FillUserHist( "Mee_sT1355_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1410)
         FillUserHist( "Mee_sT1410_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1460)
         FillUserHist( "Mee_sT1460_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1515)
         FillUserHist( "Mee_sT1515_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1565)
         FillUserHist( "Mee_sT1565_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1615)
         FillUserHist( "Mee_sT1615_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1670)
         FillUserHist( "Mee_sT1670_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1720)
         FillUserHist( "Mee_sT1720_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1770)
         FillUserHist( "Mee_sT1770_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       if (sT_eejj > 1815)
         FillUserHist( "Mee_sT1815_PAS"                     ,M_e1e2                         , pileup_weight * gen_weight );
       //--------------------------------------------------------------------------
       // no b tags
       //--------------------------------------------------------------------------
       if((isData() && nBJet_ptCut==0) || !isData()) {
         FillUserHist("nElectron_noBtaggedJets"         , nEle_ptCut                     , pileup_weight * gen_weight );
         FillUserHist("nMuon_noBtaggedJets"             , nMuon_ptCut                    , pileup_weight * gen_weight );
         FillUserHist("nJet_noBtaggedJets"              , nJet_ptCut                     , pileup_weight * gen_weight );
         FillUserHist("Pt1stEle_noBtaggedJets"            , Ele1_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Eta1stEle_noBtaggedJets"            , Ele1_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Phi1stEle_noBtaggedJets"            , Ele1_Phi                       , pileup_weight * gen_weight );
         FillUserHist("Pt2ndEle_noBtaggedJets"            , Ele2_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Eta2ndEle_noBtaggedJets"            , Ele2_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Phi2ndEle_noBtaggedJets"        , Ele2_Phi                       , pileup_weight * gen_weight );
         FillUserHist("Charge1stEle_noBtaggedJets"        , Ele1_Charge                    , pileup_weight * gen_weight );
         FillUserHist("Charge2ndEle_noBtaggedJets"        , Ele2_Charge                    , pileup_weight * gen_weight );
         FillUserHist("MET_noBtaggedJets"               , PFMET_Type1_Pt              , pileup_weight * gen_weight );
         FillUserHist("METPhi_noBtaggedJets"        , PFMET_Type1_Phi             , pileup_weight * gen_weight );
         FillUserHist("Pt1stJet_noBtaggedJets"          , Jet1_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Pt2ndJet_noBtaggedJets"          , Jet2_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Eta1stJet_noBtaggedJets"         , Jet1_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Eta2ndJet_noBtaggedJets"         , Jet2_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Phi1stJet_noBtaggedJets"        , Jet1_Phi                       , pileup_weight * gen_weight );
         FillUserHist("Phi2ndJet_noBtaggedJets"        , Jet2_Phi                       , pileup_weight * gen_weight );
         FillUserHist("sTlep_noBtaggedJets"             , Ele1_Pt + Ele2_Pt              , pileup_weight * gen_weight );
         FillUserHist("sTjet_noBtaggedJets"             , Jet1_Pt + Jet2_Pt              , pileup_weight * gen_weight );
         FillUserHist("sT_noBtaggedJets"                , sT_eejj                        , pileup_weight * gen_weight );
         FillUserHist("sT_zjj_noBtaggedJets"            , sT_zjj                         , pileup_weight * gen_weight );
         FillUserHist("Mjj_noBtaggedJets"            , M_j1j2                         , pileup_weight * gen_weight );
         FillUserHist("Mee_noBtaggedJets"            , M_e1e2                         , pileup_weight * gen_weight );
         FillUserHist("MTenu_noBtaggedJets"            , readerTools_->ReadValueBranch<Float_t>("MT_Ele1MET")                     , pileup_weight * gen_weight );
         FillUserHist("Me1j1_noBtaggedJets"             , M_e1j1                         , pileup_weight * gen_weight );
         FillUserHist("Me1j2_noBtaggedJets"             , M_e1j2                         , pileup_weight * gen_weight );
         FillUserHist("Me2j1_noBtaggedJets"             , M_e2j1                         , pileup_weight * gen_weight );
         FillUserHist("Me2j2_noBtaggedJets"             , M_e2j2                         , pileup_weight * gen_weight );
         FillUserHist("Mej_selected_min_noBtaggedJets"             , M_e2j2                         , pileup_weight * gen_weight );
         FillUserHist("Mej_selected_max_noBtaggedJets"             , M_e2j2                         , pileup_weight * gen_weight );
         FillUserHist("Mej_minmax_noBtaggedJets"        , M_ej_min                       , pileup_weight * gen_weight );
         FillUserHist("Mej_minmax_noBtaggedJets"        , M_ej_max                       , pileup_weight * gen_weight );
         FillUserHist("Mej_selected_avg_noBtaggedJets"  , M_ej_avg                       , pileup_weight * gen_weight );
         FillUserHist("Mejj_noBtaggedJets"              , M_ejj                          , pileup_weight * gen_weight );
         FillUserHist("Meej_noBtaggedJets"              , M_eej                          , pileup_weight * gen_weight );
         FillUserHist("Meejj_noBtaggedJets"             , M_eejj                         , pileup_weight * gen_weight );

         FillUserHist( "Mee_PAS_noBtaggedJets"      , M_e1e2,  pileup_weight * gen_weight * weightZeroBJets ) ;
         if      ( isEBEB ) FillUserHist( "Mee_EBEB_PAS_noBtaggedJets"           , M_e1e2,  pileup_weight * gen_weight * weightZeroBJets );
         else if ( isEBEE ) FillUserHist( "Mee_EBEE_PAS_noBtaggedJets"           , M_e1e2,  pileup_weight * gen_weight * weightZeroBJets );
         else if ( isEEEE ) FillUserHist( "Mee_EEEE_PAS_noBtaggedJets"           , M_e1e2,  pileup_weight * gen_weight * weightZeroBJets );

         if (sT_eejj >= 300 && sT_eejj < 500)
           FillUserHist("Mee_sT300To500_PAS_noBtaggedJets", M_e1e2      , pileup_weight * gen_weight * weightZeroBJets );
         else if (sT_eejj >= 500 && sT_eejj < 750)
           FillUserHist("Mee_sT500To750_PAS_noBtaggedJets", M_e1e2      , pileup_weight * gen_weight * weightZeroBJets );
         else if (sT_eejj >= 750 && sT_eejj < 1250)
           FillUserHist("Mee_sT750To1250_PAS_noBtaggedJets", M_e1e2     , pileup_weight * gen_weight * weightZeroBJets );
         else if (sT_eejj >= 1250)
           FillUserHist("Mee_sT1250ToInf_PAS_noBtaggedJets", M_e1e2     , pileup_weight * gen_weight * weightZeroBJets );

         if (M_ej_min >= 100 && M_ej_min < 200)
           FillUserHist("Mee_MejMin100To200_PAS_noBtaggedJets", M_e1e2  , pileup_weight * gen_weight * weightZeroBJets );
         else if (M_ej_min >= 200 && M_ej_min < 300)
           FillUserHist("Mee_MejMin200To300_PAS_noBtaggedJets", M_e1e2  , pileup_weight * gen_weight * weightZeroBJets );
         else if (M_ej_min >= 300 && M_ej_min < 400)
           FillUserHist("Mee_MejMin300To400_PAS_noBtaggedJets", M_e1e2  , pileup_weight * gen_weight * weightZeroBJets );
         else if (M_ej_min >= 400 && M_ej_min < 500)
           FillUserHist("Mee_MejMin400To500_PAS_noBtaggedJets", M_e1e2  , pileup_weight * gen_weight * weightZeroBJets );
         else if (M_ej_min >= 500 && M_ej_min < 650)
           FillUserHist("Mee_MejMin500To650_PAS_noBtaggedJets", M_e1e2  , pileup_weight * gen_weight * weightZeroBJets );
         else if (M_ej_min >= 650)
           FillUserHist("Mee_MejMin650ToInf_PAS_noBtaggedJets", M_e1e2  , pileup_weight * gen_weight * weightZeroBJets );
       }
       if(nBJet_ptCut>=1) {
         FillUserHist("nElectron_gteOneBtaggedJet"         , nEle_ptCut                     , pileup_weight * gen_weight );
         FillUserHist("nMuon_gteOneBtaggedJet"             , nMuon_ptCut                    , pileup_weight * gen_weight );
         FillUserHist("nJet_gteOneBtaggedJet"              , nJet_ptCut                     , pileup_weight * gen_weight );
         FillUserHist("Pt1stEle_gteOneBtaggedJet"            , Ele1_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Eta1stEle_gteOneBtaggedJet"            , Ele1_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Phi1stEle_gteOneBtaggedJet"            , Ele1_Phi                       , pileup_weight * gen_weight );
         FillUserHist("Pt2ndEle_gteOneBtaggedJet"            , Ele2_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Eta2ndEle_gteOneBtaggedJet"            , Ele2_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Phi2ndEle_gteOneBtaggedJet"        , Ele2_Phi                       , pileup_weight * gen_weight );
         FillUserHist("Charge1stEle_gteOneBtaggedJet"        , Ele1_Charge                    , pileup_weight * gen_weight );
         FillUserHist("Charge2ndEle_gteOneBtaggedJet"        , Ele2_Charge                    , pileup_weight * gen_weight );
         FillUserHist("MET_gteOneBtaggedJet"               , PFMET_Type1_Pt              , pileup_weight * gen_weight );
         FillUserHist("METPhi_gteOneBtaggedJet"        , PFMET_Type1_Phi             , pileup_weight * gen_weight );
         FillUserHist("Pt1stJet_gteOneBtaggedJet"          , Jet1_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Pt2ndJet_gteOneBtaggedJet"          , Jet2_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Eta1stJet_gteOneBtaggedJet"         , Jet1_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Eta2ndJet_gteOneBtaggedJet"         , Jet2_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Phi1stJet_gteOneBtaggedJet"        , Jet1_Phi                       , pileup_weight * gen_weight );
         FillUserHist("Phi2ndJet_gteOneBtaggedJet"        , Jet2_Phi                       , pileup_weight * gen_weight );
         FillUserHist("sTlep_gteOneBtaggedJet"             , Ele1_Pt + Ele2_Pt              , pileup_weight * gen_weight );
         FillUserHist("sTjet_gteOneBtaggedJet"             , Jet1_Pt + Jet2_Pt              , pileup_weight * gen_weight );
         FillUserHist("sT_gteOneBtaggedJet"                , sT_eejj                        , pileup_weight * gen_weight );
         FillUserHist("sT_zjj_gteOneBtaggedJet"            , sT_zjj                         , pileup_weight * gen_weight );
         FillUserHist("Mjj_gteOneBtaggedJet"            , M_j1j2                         , pileup_weight * gen_weight );
         FillUserHist("Mee_gteOneBtaggedJet"            , M_e1e2                         , pileup_weight * gen_weight );
         FillUserHist("MTenu_gteOneBtaggedJet"            , readerTools_->ReadValueBranch<Float_t>("MT_Ele1MET")                     , pileup_weight * gen_weight );
         FillUserHist("Me1j1_gteOneBtaggedJet"             , M_e1j1                         , pileup_weight * gen_weight );
         FillUserHist("Me1j2_gteOneBtaggedJet"             , M_e1j2                         , pileup_weight * gen_weight );
         FillUserHist("Me2j1_gteOneBtaggedJet"             , M_e2j1                         , pileup_weight * gen_weight );
         FillUserHist("Me2j2_gteOneBtaggedJet"             , M_e2j2                         , pileup_weight * gen_weight );
         FillUserHist("Mej_selected_min_gteOneBtaggedJet"             , M_e2j2                         , pileup_weight * gen_weight );
         FillUserHist("Mej_selected_max_gteOneBtaggedJet"             , M_e2j2                         , pileup_weight * gen_weight );
         FillUserHist("Mej_minmax_gteOneBtaggedJet"        , M_ej_min                       , pileup_weight * gen_weight );
         FillUserHist("Mej_minmax_gteOneBtaggedJet"        , M_ej_max                       , pileup_weight * gen_weight );
         FillUserHist("Mej_selected_avg_gteOneBtaggedJet"  , M_ej_avg                       , pileup_weight * gen_weight );
         FillUserHist("Mejj_gteOneBtaggedJet"              , M_ejj                          , pileup_weight * gen_weight );
         FillUserHist("Meej_gteOneBtaggedJet"              , M_eej                          , pileup_weight * gen_weight );
         FillUserHist("Meejj_gteOneBtaggedJet"             , M_eejj                         , pileup_weight * gen_weight );

         FillUserHist( "Mee_PAS_gteOneBtaggedJet"      , M_e1e2,  pileup_weight * gen_weight * weightAtLeastOneBJet ) ;
         if      ( isEBEB ) FillUserHist( "Mee_EBEB_PAS_gteOneBtaggedJet"           , M_e1e2,  pileup_weight * gen_weight * weightAtLeastOneBJet );
         else if ( isEBEE ) FillUserHist( "Mee_EBEE_PAS_gteOneBtaggedJet"           , M_e1e2,  pileup_weight * gen_weight * weightAtLeastOneBJet );
         else if ( isEEEE ) FillUserHist( "Mee_EEEE_PAS_gteOneBtaggedJet"           , M_e1e2,  pileup_weight * gen_weight * weightAtLeastOneBJet );

         if (sT_eejj >= 300 && sT_eejj < 500)
           FillUserHist("Mee_sT300To500_PAS_gteOneBtaggedJet", M_e1e2      , pileup_weight * gen_weight * weightAtLeastOneBJet );
         else if (sT_eejj >= 500 && sT_eejj < 750)
           FillUserHist("Mee_sT500To750_PAS_gteOneBtaggedJet", M_e1e2      , pileup_weight * gen_weight * weightAtLeastOneBJet );
         else if (sT_eejj >= 750 && sT_eejj < 1250)
           FillUserHist("Mee_sT750To1250_PAS_gteOneBtaggedJet", M_e1e2     , pileup_weight * gen_weight * weightAtLeastOneBJet );
         else if (sT_eejj >= 1250)
           FillUserHist("Mee_sT1250ToInf_PAS_gteOneBtaggedJet", M_e1e2     , pileup_weight * gen_weight * weightAtLeastOneBJet );

         if (M_ej_min >= 100 && M_ej_min < 200)
           FillUserHist("Mee_MejMin100To200_PAS_gteOneBtaggedJet", M_e1e2  , pileup_weight * gen_weight * weightAtLeastOneBJet );
         else if (M_ej_min >= 200 && M_ej_min < 300)
           FillUserHist("Mee_MejMin200To300_PAS_gteOneBtaggedJet", M_e1e2  , pileup_weight * gen_weight * weightAtLeastOneBJet );
         else if (M_ej_min >= 300 && M_ej_min < 400)
           FillUserHist("Mee_MejMin300To400_PAS_gteOneBtaggedJet", M_e1e2  , pileup_weight * gen_weight * weightAtLeastOneBJet );
         else if (M_ej_min >= 400 && M_ej_min < 500)
           FillUserHist("Mee_MejMin400To500_PAS_gteOneBtaggedJet", M_e1e2  , pileup_weight * gen_weight * weightAtLeastOneBJet );
         else if (M_ej_min >= 500 && M_ej_min < 650)
           FillUserHist("Mee_MejMin500To650_PAS_gteOneBtaggedJet", M_e1e2  , pileup_weight * gen_weight * weightAtLeastOneBJet );
         else if (M_ej_min >= 650)
           FillUserHist("Mee_MejMin650ToInf_PAS_gteOneBtaggedJet", M_e1e2  , pileup_weight * gen_weight * weightAtLeastOneBJet );
       }
       if(nBJet_ptCut>=2) {
         FillUserHist("nElectron_gteTwoBtaggedJets"         , nEle_ptCut                     , pileup_weight * gen_weight );
         FillUserHist("nMuon_gteTwoBtaggedJets"             , nMuon_ptCut                    , pileup_weight * gen_weight );
         FillUserHist("nJet_gteTwoBtaggedJets"              , nJet_ptCut                     , pileup_weight * gen_weight );
         FillUserHist("Pt1stEle_gteTwoBtaggedJets"            , Ele1_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Eta1stEle_gteTwoBtaggedJets"            , Ele1_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Phi1stEle_gteTwoBtaggedJets"            , Ele1_Phi                       , pileup_weight * gen_weight );
         FillUserHist("Pt2ndEle_gteTwoBtaggedJets"            , Ele2_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Eta2ndEle_gteTwoBtaggedJets"            , Ele2_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Phi2ndEle_gteTwoBtaggedJets"        , Ele2_Phi                       , pileup_weight * gen_weight );
         FillUserHist("Charge1stEle_gteTwoBtaggedJets"        , Ele1_Charge                    , pileup_weight * gen_weight );
         FillUserHist("Charge2ndEle_gteTwoBtaggedJets"        , Ele2_Charge                    , pileup_weight * gen_weight );
         FillUserHist("MET_gteTwoBtaggedJets"               , PFMET_Type1_Pt              , pileup_weight * gen_weight );
         FillUserHist("METPhi_gteTwoBtaggedJets"        , PFMET_Type1_Phi             , pileup_weight * gen_weight );
         FillUserHist("Pt1stJet_gteTwoBtaggedJets"          , Jet1_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Pt2ndJet_gteTwoBtaggedJets"          , Jet2_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Eta1stJet_gteTwoBtaggedJets"         , Jet1_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Eta2ndJet_gteTwoBtaggedJets"         , Jet2_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Phi1stJet_gteTwoBtaggedJets"        , Jet1_Phi                       , pileup_weight * gen_weight );
         FillUserHist("Phi2ndJet_gteTwoBtaggedJets"        , Jet2_Phi                       , pileup_weight * gen_weight );
         FillUserHist("sTlep_gteTwoBtaggedJets"             , Ele1_Pt + Ele2_Pt              , pileup_weight * gen_weight );
         FillUserHist("sTjet_gteTwoBtaggedJets"             , Jet1_Pt + Jet2_Pt              , pileup_weight * gen_weight );
         FillUserHist("sT_gteTwoBtaggedJets"                , sT_eejj                        , pileup_weight * gen_weight );
         FillUserHist("sT_zjj_gteTwoBtaggedJets"            , sT_zjj                         , pileup_weight * gen_weight );
         FillUserHist("Mjj_gteTwoBtaggedJets"            , M_j1j2                         , pileup_weight * gen_weight );
         FillUserHist("Mee_gteTwoBtaggedJets"            , M_e1e2                         , pileup_weight * gen_weight );
         FillUserHist("MTenu_gteTwoBtaggedJets"            , readerTools_->ReadValueBranch<Float_t>("MT_Ele1MET")                     , pileup_weight * gen_weight );
         FillUserHist("Me1j1_gteTwoBtaggedJets"             , M_e1j1                         , pileup_weight * gen_weight );
         FillUserHist("Me1j2_gteTwoBtaggedJets"             , M_e1j2                         , pileup_weight * gen_weight );
         FillUserHist("Me2j1_gteTwoBtaggedJets"             , M_e2j1                         , pileup_weight * gen_weight );
         FillUserHist("Me2j2_gteTwoBtaggedJets"             , M_e2j2                         , pileup_weight * gen_weight );
         FillUserHist("Mej_selected_min_gteTwoBtaggedJets"             , M_e2j2                         , pileup_weight * gen_weight );
         FillUserHist("Mej_selected_max_gteTwoBtaggedJets"             , M_e2j2                         , pileup_weight * gen_weight );
         FillUserHist("Mej_minmax_gteTwoBtaggedJets"        , M_ej_min                       , pileup_weight * gen_weight );
         FillUserHist("Mej_minmax_gteTwoBtaggedJets"        , M_ej_max                       , pileup_weight * gen_weight );
         FillUserHist("Mej_selected_avg_gteTwoBtaggedJets"  , M_ej_avg                       , pileup_weight * gen_weight );
         FillUserHist("Mejj_gteTwoBtaggedJets"              , M_ejj                          , pileup_weight * gen_weight );
         FillUserHist("Meej_gteTwoBtaggedJets"              , M_eej                          , pileup_weight * gen_weight );
         FillUserHist("Meejj_gteTwoBtaggedJets"             , M_eejj                         , pileup_weight * gen_weight );

         FillUserHist( "Mee_PAS_gteTwoBtaggedJets"      , M_e1e2,  pileup_weight * gen_weight * weightAtLeastTwoBJets ) ;
         if      ( isEBEB ) FillUserHist( "Mee_EBEB_PAS_gteTwoBtaggedJets"           , M_e1e2,  pileup_weight * gen_weight * weightAtLeastTwoBJets );
         else if ( isEBEE ) FillUserHist( "Mee_EBEE_PAS_gteTwoBtaggedJets"           , M_e1e2,  pileup_weight * gen_weight * weightAtLeastTwoBJets );
         else if ( isEEEE ) FillUserHist( "Mee_EEEE_PAS_gteTwoBtaggedJets"           , M_e1e2,  pileup_weight * gen_weight * weightAtLeastTwoBJets );

         if (sT_eejj >= 300 && sT_eejj < 500)
           FillUserHist("Mee_sT300To500_PAS_gteTwoBtaggedJets", M_e1e2      , pileup_weight * gen_weight * weightAtLeastTwoBJets );
         else if (sT_eejj >= 500 && sT_eejj < 750)
           FillUserHist("Mee_sT500To750_PAS_gteTwoBtaggedJets", M_e1e2      , pileup_weight * gen_weight * weightAtLeastTwoBJets );
         else if (sT_eejj >= 750 && sT_eejj < 1250)
           FillUserHist("Mee_sT750To1250_PAS_gteTwoBtaggedJets", M_e1e2     , pileup_weight * gen_weight * weightAtLeastTwoBJets );
         else if (sT_eejj >= 1250)
           FillUserHist("Mee_sT1250ToInf_PAS_gteTwoBtaggedJets", M_e1e2     , pileup_weight * gen_weight * weightAtLeastTwoBJets );

         if (M_ej_min >= 100 && M_ej_min < 200)
           FillUserHist("Mee_MejMin100To200_PAS_gteTwoBtaggedJets", M_e1e2  , pileup_weight * gen_weight * weightAtLeastTwoBJets );
         else if (M_ej_min >= 200 && M_ej_min < 300)
           FillUserHist("Mee_MejMin200To300_PAS_gteTwoBtaggedJets", M_e1e2  , pileup_weight * gen_weight * weightAtLeastTwoBJets );
         else if (M_ej_min >= 300 && M_ej_min < 400)
           FillUserHist("Mee_MejMin300To400_PAS_gteTwoBtaggedJets", M_e1e2  , pileup_weight * gen_weight * weightAtLeastTwoBJets );
         else if (M_ej_min >= 400 && M_ej_min < 500)
           FillUserHist("Mee_MejMin400To500_PAS_gteTwoBtaggedJets", M_e1e2  , pileup_weight * gen_weight * weightAtLeastTwoBJets );
         else if (M_ej_min >= 500 && M_ej_min < 650)
           FillUserHist("Mee_MejMin500To650_PAS_gteTwoBtaggedJets", M_e1e2  , pileup_weight * gen_weight * weightAtLeastTwoBJets );
         else if (M_ej_min >= 650)
           FillUserHist("Mee_MejMin650ToInf_PAS_gteTwoBtaggedJets", M_e1e2  , pileup_weight * gen_weight * weightAtLeastTwoBJets );
       }
       ////
       //if (sT_eejj>2000)
       //  FillUserHist("Mee_sT2000_PAS"         ,M_e1e2                         , pileup_weight * gen_weight );
       //if (sT_eejj>926.316 && M_ej_min > 413.158 && M_e1e2 > 310.526) {
       //  FillUserHist("OptBinLQ600", M_e1e2, pileup_weight*gen_weight);
       //  FillUserHist("PtZforOptBin600",GenZGamma1_Pt, pileup_weight*gen_weight);
       //  FillUserHist("PtEEforOptBin600",Pt_e1e2, pileup_weight*gen_weight);
       //  FillUserHist("OptBinLQ600_noWeight", M_e1e2, pileup_weight*gen_weight);
       //  FillUserTH2D("PtEEVsZPtForOptBin600", Pt_e1e2, GenZGamma1_Pt, pileup_weight*gen_weight);
       //  //// printing
       //  //std::cout.precision(0);
       //  //std::cout << fixed <<  "Run = " << run << ", event = " << event << ", ls = " << ls << std::endl;
       //  //std::cout.precision(3);
       //  //std::cout << fixed <<  "  Mej      = " << M_ej_avg << std::endl;
       //  //std::cout << fixed <<  "  Mee      = " << M_e1e2 << std::endl;
       //  //std::cout << fixed <<  "  sT       = " << sT_enujj << std::endl;
       //  //std::cout << fixed <<  "  Ele1 Pt  = " << Ele1_Pt << "\t, Eta = " << Ele1_Eta << "\t, Phi = " << Ele1_Phi << std::endl;
       //  //std::cout << fixed <<  "  Ele1 dPhi  = " << Ele1_DeltaPhiTrkSC << "\t, HoE = " << Ele1_HoE << "\t, sIetaIeta = " << Ele1_SigmaIEtaIEta << std::endl;
       //  //std::cout << fixed <<  "  Ele2 Pt  = " << Ele2_Pt << "\t, Eta = " << Ele2_Eta << "\t, Phi = " << Ele2_Phi << std::endl;
       //  //std::cout << fixed <<  "  Jet1 Pt  = " << Jet1_Pt << "\t, Eta = " << Jet1_Eta << "\t, Phi = " << Jet1_Phi << std::endl;
       //  //std::cout << fixed <<  "  Jet2 Pt  = " << Jet2_Pt << "\t, Eta = " << Jet2_Eta << "\t, Phi = " << Jet2_Phi << std::endl;
       //}
       //if (sT_eejj>926.316 && M_ej_min > 534.211 && M_e1e2 > 239.474) {
       //  FillUserHist("OptBinLQ650", M_e1e2, pileup_weight*gen_weight);
       //  FillUserHist("OptBinLQ650_noWeight", M_e1e2);
       //}
       //if (sT_eejj>1105.26 && M_ej_min > 594.737 && M_e1e2 > 239.474) {
       //  FillUserHist("OptBinLQ700", M_e1e2, pileup_weight*gen_weight);
       //  FillUserHist("OptBinLQ700_noWeight", M_e1e2);
       //}
       //
       FillUserTH3D("OptimizationCutSpace",sT_eejj,M_ej_min,M_e1e2, pileup_weight*gen_weight);
       if (M_ej_min >= 100 && M_ej_min < 200)
         FillUserHist("Mee_MejMin100To200_PAS", M_e1e2                         , pileup_weight * gen_weight );
       else if (M_ej_min >= 200 && M_ej_min < 300)
         FillUserHist("Mee_MejMin200To300_PAS", M_e1e2                         , pileup_weight * gen_weight );
       else if (M_ej_min >= 300 && M_ej_min < 400)
         FillUserHist("Mee_MejMin300To400_PAS", M_e1e2                         , pileup_weight * gen_weight );
       else if (M_ej_min >= 400 && M_ej_min < 500)
         FillUserHist("Mee_MejMin400To500_PAS", M_e1e2                         , pileup_weight * gen_weight );
       else if (M_ej_min >= 500 && M_ej_min < 650)
         FillUserHist("Mee_MejMin500To650_PAS", M_e1e2                         , pileup_weight * gen_weight );
       else if (M_ej_min >= 650)
         FillUserHist("Mee_MejMin650ToInf_PAS", M_e1e2                         , pileup_weight * gen_weight );
       //
       if (Pt_e1e2 < 100)
         FillUserHist( "Mee_Ptee0To100_PAS"                       ,  Pt_e1e2 , pileup_weight * gen_weight );
       else if(Pt_e1e2 < 150 && Pt_e1e2 >= 100)
         FillUserHist( "Mee_Ptee100To150_PAS"                     ,  Pt_e1e2 , pileup_weight * gen_weight );
       else if(Pt_e1e2 < 200 && Pt_e1e2 >= 150)
         FillUserHist( "Mee_Ptee150To200_PAS"                     ,  Pt_e1e2 , pileup_weight * gen_weight );
       else if(Pt_e1e2 < 250 && Pt_e1e2 >= 200)
         FillUserHist( "Mee_Ptee200To250_PAS"                     ,  Pt_e1e2 , pileup_weight * gen_weight );
       else if(Pt_e1e2 < 300 && Pt_e1e2 >= 250)
         FillUserHist( "Mee_Ptee250To300_PAS"                     ,  Pt_e1e2 , pileup_weight * gen_weight );
       else if(Pt_e1e2 < 350 && Pt_e1e2 >= 300)
         FillUserHist( "Mee_Ptee300To350_PAS"                     ,  Pt_e1e2 , pileup_weight * gen_weight );
       else if(Pt_e1e2 < 400 && Pt_e1e2 >= 350)
         FillUserHist( "Mee_Ptee350To400_PAS"                     ,  Pt_e1e2 , pileup_weight * gen_weight );
       else
         FillUserHist( "Mee_Ptee400ToInf_PAS"                     ,  Pt_e1e2 , pileup_weight * gen_weight );
       FillUserHist("Me1j2_PAS"             , M_e1j2                         , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Me2j1_PAS"             , M_e2j1                         , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Me2j2_PAS"             , M_e2j2                         , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Ptee_PAS"              , Pt_e1e2                        , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("nVertex_PAS"           , nVertex                        , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("DR_Ele1Jet1_PAS"        , DR_Ele1Jet1                    , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("DR_Ele1Jet2_PAS"        , DR_Ele1Jet2                    , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("DR_Ele2Jet1_PAS"        , DR_Ele2Jet1                    , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("DR_Ele2Jet2_PAS"        , DR_Ele2Jet2                    , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("DR_Jet1Jet2_PAS"        , DR_Jet1Jet2                    , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Meejj_PAS"             , M_eejj                         , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Meej_PAS"              , M_eej                          , pileup_weight * gen_weight );
       FillUserHist("Mejj_PAS"              , M_ejj                          , pileup_weight * gen_weight );
       FillUserHist("minDR_ZJet_PAS"        , min_DeltaR_Zj                  , pileup_weight * gen_weight );
       FillUserHist("DR_ZJet1_PAS"          , DR_ZJ1                         , pileup_weight * gen_weight );
       FillUserHist("DR_ZJet2_PAS"          , DR_ZJ2                         , pileup_weight * gen_weight );
       FillUserHist("sTfrac_Jet1_PAS"       , Jet1_Pt / sT_eejj              , pileup_weight * gen_weight );
       FillUserHist("sTfrac_Jet2_PAS"       , Jet2_Pt / sT_eejj              , pileup_weight * gen_weight );
       FillUserHist("sTfrac_Ele1_PAS"       , Ele1_Pt / sT_eejj              , pileup_weight * gen_weight );
       FillUserHist("sTfrac_Ele2_PAS"       , Ele2_Pt / sT_eejj              , pileup_weight * gen_weight );
       FillUserHist("sTfrac_Jet_PAS"        , ( Jet1_Pt + Jet2_Pt ) / sT_eejj, pileup_weight * gen_weight );
       FillUserHist("sTfrac_Ele_PAS"        , ( Ele1_Pt + Ele2_Pt ) / sT_eejj, pileup_weight * gen_weight );
       FillUserHist("Mej_selected_avg_PAS"  , M_ej_avg                       , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Mej_selected_min_PAS"  , M_ej_min                       , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Mej_selected_max_PAS"  , M_ej_max                       , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Mej_minmax_PAS"        , M_ej_min                       , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Mej_minmax_PAS"        , M_ej_max                       , pileup_weight * gen_weight, preselectionCut );
       FillUserHist("Mej_asym_PAS"        , M_ej_asym                        , pileup_weight * gen_weight, preselectionCut );

       FillUserTH2D("MeeVsST_PAS" , M_e1e2, sT_eejj, pileup_weight * gen_weight );
       FillUserTH2D("MeeVsPtee_PAS" , M_e1e2, Pt_e1e2, pileup_weight * gen_weight );

       // checking electrons
       FillUserHist( "SCEta_1stEle_Presel",Ele1_SCEta, pileup_weight*gen_weight);
       FillUserHist( "EleEta_1stEle_Presel",Ele1_Eta,pileup_weight*gen_weight);
       FillUserHist( "DeltaEtaTrkSC_1stEle_Presel",Ele1_DeltaEtaTrkSC,pileup_weight*gen_weight);
       FillUserHist( "SCEtaMinusEleEta_1stEle_Presel",Ele1_SCEta-Ele1_Eta,pileup_weight*gen_weight);
       FillUserHist( "DeltaEtaTrkSC_Minus_SCEtaMinusEleEta_1stEle_Presel",Ele1_DeltaEtaTrkSC-(Ele1_SCEta-Ele1_Eta),pileup_weight*gen_weight);
       FillUserHist( "SCEta_2ndEle_Presel",Ele2_SCEta, pileup_weight*gen_weight);
       FillUserHist( "EleEta_2ndEle_Presel",Ele2_Eta,pileup_weight*gen_weight);
       FillUserHist( "DeltaEtaTrkSC_2ndEle_Presel",Ele2_DeltaEtaTrkSC,pileup_weight*gen_weight);
       FillUserHist( "SCEtaMinusEleEta_2ndEle_Presel",Ele2_SCEta-Ele2_Eta,pileup_weight*gen_weight);
       FillUserHist( "DeltaEtaTrkSC_Minus_SCEtaMinusEleEta_2ndEle_Presel",Ele2_DeltaEtaTrkSC-(Ele2_SCEta-Ele2_Eta),pileup_weight*gen_weight);
       //--------------------------------------------------------------------------
       // Mass-pairing histograms at preselection
       //--------------------------------------------------------------------------

       if ( fabs(M_e1j1-M_e2j2) < fabs(M_e1j2-M_e2j1) ) {
         FillUserHist("Me1j_selected_PAS"   , M_e1j1          , pileup_weight * gen_weight, preselectionCut);
         FillUserHist("Me2j_selected_PAS"   , M_e2j2          , pileup_weight * gen_weight, preselectionCut);
         FillUserTH2D("Me1jVsMe2j_selected" , M_e1j1  , M_e2j2, pileup_weight * gen_weight);
         FillUserTH2D("Me1jVsMe2j_rejected" , M_e1j2  , M_e2j1, pileup_weight * gen_weight);
       }
       else {
         FillUserHist("Me1j_selected_PAS"   , M_e1j2          , pileup_weight * gen_weight, preselectionCut);
         FillUserHist("Me2j_selected_PAS"   , M_e2j1          , pileup_weight * gen_weight, preselectionCut);
         FillUserTH2D("Me1jVsMe2j_selected" , M_e1j2  , M_e2j1, pileup_weight * gen_weight);
         FillUserTH2D("Me1jVsMe2j_rejected" , M_e1j1  , M_e2j2, pileup_weight * gen_weight);
       }

       //--------------------------------------------------------------------------
       // Preselection + data-only
       //--------------------------------------------------------------------------

       if ( isData() ) {
         FillUserHist("run_PAS"  , run );
         FillUserTProfile("run_vs_nvtx_PAS", run, nVertex, 1);
       }

       //--------------------------------------------------------------------------
       // Preselection + N(Jet) > 2
       //--------------------------------------------------------------------------

       if ( nJet_ptCut > 2 ){
         FillUserHist( "M_e1j3_PAS"  , M_e1j3, pileup_weight * gen_weight ) ;
         FillUserHist( "M_e2j3_PAS"  , M_e2j3, pileup_weight * gen_weight ) ;
         FillUserHist( "M_j1j3_PAS"  , M_j1j3, pileup_weight * gen_weight ) ;
         FillUserHist( "M_j2j3_PAS"  , M_j2j3, pileup_weight * gen_weight ) ;
         FillUserHist( "M_eejjj_PAS" , M_eejjj,pileup_weight * gen_weight ) ;

         FillUserHist( "Ptj1j2j3_PAS"            , Pt_j1j2j3           , pileup_weight * gen_weight );
         FillUserHist( "Ptj2j3_PAS"              , Pt_j2j3             , pileup_weight * gen_weight );
         FillUserHist( "Ptj1j3_PAS"              , Pt_j1j3             , pileup_weight * gen_weight );
         FillUserHist( "Ptee_Minus_Ptj1j2j3_PAS" , Pt_e1e2 - Pt_j1j2j3 , pileup_weight * gen_weight );
       }

       //--------------------------------------------------------------------------
       // Preselection + event type (EBEB, EEEB, EEEE, etc)
       //--------------------------------------------------------------------------

       if      ( isEB   ) FillUserHist( "Mee_EB_PAS"  , M_e1e2, pileup_weight * gen_weight, preselectionCut );
       if      ( isEBEB ) FillUserHist( "Mee_EBEB_PAS", M_e1e2, pileup_weight * gen_weight, preselectionCut );
       else if ( isEBEE ) FillUserHist( "Mee_EBEE_PAS", M_e1e2, pileup_weight * gen_weight, preselectionCut );
       else if ( isEEEE ) FillUserHist( "Mee_EEEE_PAS", M_e1e2, pileup_weight * gen_weight, preselectionCut );

       //--------------------------------------------------------------------------
       // Preselection + high ST plot
       //--------------------------------------------------------------------------

       if ( sT_eejj > 445. ) FillUserHist("Mee_PASandST445"   , M_e1e2  , pileup_weight * gen_weight ) ;

       //--------------------------------------------------------------------------
       // High M(ee) plots
       //--------------------------------------------------------------------------

       if ( M_e1e2  > 100. ) FillUserHist("sT_PASandMee100"   , sT_eejj , pileup_weight * gen_weight ) ;
       if ( M_e1e2  > 110. ) FillUserHist("sT_PASandMee110"   , sT_eejj , pileup_weight * gen_weight ) ;
       if ( M_e1e2  > 120. ) FillUserHist("sT_PASandMee120"   , sT_eejj , pileup_weight * gen_weight ) ;
       if ( M_e1e2  > 130. ) FillUserHist("sT_PASandMee130"   , sT_eejj , pileup_weight * gen_weight ) ;
       if ( M_e1e2  > 140. ) FillUserHist("sT_PASandMee140"   , sT_eejj , pileup_weight * gen_weight ) ;
       if ( M_e1e2  > 150. ) FillUserHist("sT_PASandMee150"   , sT_eejj , pileup_weight * gen_weight ) ;
       if ( M_e1e2  > 160. ) FillUserHist("sT_PASandMee160"   , sT_eejj , pileup_weight * gen_weight ) ;
       if ( M_e1e2  > 170. ) FillUserHist("sT_PASandMee170"   , sT_eejj , pileup_weight * gen_weight ) ;
       if ( M_e1e2  > 180. ) FillUserHist("sT_PASandMee180"   , sT_eejj , pileup_weight * gen_weight ) ;
       if ( M_e1e2  > 190. ) FillUserHist("sT_PASandMee190"   , sT_eejj , pileup_weight * gen_weight ) ;
       if ( M_e1e2  > 200. ) FillUserHist("sT_PASandMee200"   , sT_eejj , pileup_weight * gen_weight ) ;

       if ( M_e1e2 > 100. ) {

         FillUserHist("CorrIsolation_1stEle_PASandMee100"         , Ele1_CorrIsolation                  , pileup_weight * gen_weight    );
         FillUserHist("DeltaEtaTrkSC_1stEle_PASandMee100"         , Ele1_DeltaEtaTrkSC                  , pileup_weight * gen_weight    );
         FillUserHist("EcalIsolation_1stEle_PASandMee100"         , Ele1_EcalIsolation                  , pileup_weight * gen_weight    );
         FillUserHist("HcalIsolation_1stEle_PASandMee100"         , Ele1_HcalIsolation                  , pileup_weight * gen_weight    );
         FillUserHist("TrkIsolation_1stEle_PASandMee100"          , Ele1_TrkIsolation                   , pileup_weight * gen_weight    );
         FillUserHist("HasMatchedPhot_1stEle_PASandMee100"        , Ele1_HasMatchedPhot                 , pileup_weight * gen_weight    );
         FillUserHist("HoE_1stEle_PASandMee100"                   , Ele1_HoE                            , pileup_weight * gen_weight    );
         FillUserHist("LeadVtxDistXY_1stEle_PASandMee100"         , Ele1_LeadVtxDistXY                  , pileup_weight * gen_weight    );
         FillUserHist("LeadVtxDistZ_1stEle_PASandMee100"          , Ele1_LeadVtxDistZ                   , pileup_weight * gen_weight    );
         FillUserHist("MissingHits_1stEle_PASandMee100"           , Ele1_MissingHits                    , pileup_weight * gen_weight    );
         if ( fabs(Ele1_Eta) < eleEta_bar ) {
           FillUserHist("Full5x5SigmaIEtaIEta_Barrel_1stEle_PASandMee100", Ele1_Full5x5SigmaIEtaIEta                  , pileup_weight * gen_weight    );
         }
         else if ( fabs(Ele1_Eta) > eleEta_end1_min && fabs(Ele2_Eta) < eleEta_end2_max ){
           FillUserHist("Full5x5SigmaIEtaIEta_Endcap_1stEle_PASandMee100", Ele1_Full5x5SigmaIEtaIEta                  , pileup_weight * gen_weight    );
         }

         FillUserHist("CorrIsolation_2ndEle_PASandMee100"         , Ele2_CorrIsolation                  , pileup_weight * gen_weight    );
         FillUserHist("DeltaEtaTrkSC_2ndEle_PASandMee100"         , Ele2_DeltaEtaTrkSC                  , pileup_weight * gen_weight    );
         FillUserHist("EcalIsolation_2ndEle_PASandMee100"         , Ele2_EcalIsolation                  , pileup_weight * gen_weight    );
         FillUserHist("HcalIsolation_2ndEle_PASandMee100"         , Ele2_HcalIsolation                  , pileup_weight * gen_weight    );
         FillUserHist("TrkIsolation_2ndEle_PASandMee100"          , Ele2_TrkIsolation                   , pileup_weight * gen_weight    );
         FillUserHist("HasMatchedPhot_2ndEle_PASandMee100"        , Ele2_HasMatchedPhot                 , pileup_weight * gen_weight    );
         FillUserHist("HoE_2ndEle_PASandMee100"                   , Ele2_HoE                            , pileup_weight * gen_weight    );
         FillUserHist("LeadVtxDistXY_2ndEle_PASandMee100"         , Ele2_LeadVtxDistXY                  , pileup_weight * gen_weight    );
         FillUserHist("LeadVtxDistZ_2ndEle_PASandMee100"          , Ele2_LeadVtxDistZ                   , pileup_weight * gen_weight    );
         FillUserHist("MissingHits_2ndEle_PASandMee100"           , Ele2_MissingHits                    , pileup_weight * gen_weight    );
         if ( fabs(Ele2_Eta) < eleEta_bar ) {
           FillUserHist("Full5x5SigmaIEtaIEta_Barrel_2ndEle_PASandMee100", Ele2_Full5x5SigmaIEtaIEta                  , pileup_weight * gen_weight    );
         }
         else if ( fabs(Ele2_Eta) > eleEta_end1_min && fabs(Ele2_Eta) < eleEta_end2_max ){
           FillUserHist("Full5x5SigmaIEtaIEta_Endcap_2ndEle_PASandMee100", Ele2_Full5x5SigmaIEtaIEta                  , pileup_weight * gen_weight    );
         }

         FillUserHist("Ptee_PASandMee100"              , Pt_e1e2                        , pileup_weight * gen_weight );
         FillUserTH2D("MeeVsST_PASandMee100" , M_e1e2, sT_eejj, pileup_weight * gen_weight );
         FillUserHist("sT_zjj_PASandMee100"            , sT_zjj                         , pileup_weight * gen_weight );
         FillUserHist("nVertex_PASandMee100"           , nVertex                        , pileup_weight * gen_weight );
         FillUserHist("EleChargeSum_PASandMee100"      , Ele1_Charge + Ele2_Charge      , pileup_weight * gen_weight ) ;
         FillUserHist("nJet_PASandMee100"              , nJet_ptCut                     , pileup_weight * gen_weight ) ;
         FillUserHist("sTlep_PASandMee100"             , Ele1_Pt + Ele2_Pt              , pileup_weight * gen_weight ) ;
         FillUserHist("sTjet_PASandMee100"             , Jet1_Pt + Jet2_Pt              , pileup_weight * gen_weight ) ;
         FillUserHist("Mjj_PASandMee100"               , M_j1j2                         , pileup_weight * gen_weight ) ;
         FillUserHist("Me1j1_PASandMee100"             , M_e1j1                         , pileup_weight * gen_weight ) ;
         FillUserHist("Me1j2_PASandMee100"             , M_e1j2                         , pileup_weight * gen_weight ) ;
         FillUserHist("Me2j1_PASandMee100"             , M_e1j1                         , pileup_weight * gen_weight ) ;
         FillUserHist("Me2j2_PASandMee100"             , M_e1j2                         , pileup_weight * gen_weight ) ;
         FillUserHist("Pt1stEle_PASandMee100"          , Ele1_Pt                        , pileup_weight * gen_weight ) ;
         FillUserHist("Pt2ndEle_PASandMee100"          , Ele2_Pt                        , pileup_weight * gen_weight ) ;
         FillUserHist("Pt1stJet_PASandMee100"          , Jet1_Pt                        , pileup_weight * gen_weight ) ;
         FillUserHist("Pt2ndJet_PASandMee100"          , Jet2_Pt                        , pileup_weight * gen_weight ) ;
         FillUserHist("Mej_selected_avg_PASandMee100"  , M_ej_avg                       , pileup_weight * gen_weight ) ;
         FillUserHist("sTfrac_Jet1_PASandMee100"       , Jet1_Pt / sT_eejj              , pileup_weight * gen_weight ) ;
         FillUserHist("sTfrac_Jet2_PASandMee100"       , Jet2_Pt / sT_eejj              , pileup_weight * gen_weight ) ;
         FillUserHist("sTfrac_Ele1_PASandMee100"       , Ele1_Pt / sT_eejj              , pileup_weight * gen_weight ) ;
         FillUserHist("sTfrac_Ele2_PASandMee100"       , Ele2_Pt / sT_eejj              , pileup_weight * gen_weight ) ;
         FillUserHist("sTfrac_Jet_PASandMee100"        , ( Jet1_Pt + Jet2_Pt ) / sT_eejj, pileup_weight * gen_weight ) ;
         FillUserHist("sTfrac_Ele_PASandMee100"        , ( Ele1_Pt + Ele2_Pt ) / sT_eejj, pileup_weight * gen_weight ) ;
         FillUserHist("Ptj1j2_PASandMee100"            , Pt_j1j2                        , pileup_weight * gen_weight ) ;
         FillUserHist("Ptee_Minus_Ptj1j2_PASandMee100" , Pt_e1e2 - Pt_j1j2              , pileup_weight * gen_weight ) ;

         if ( nJet_ptCut > 2 ) {
           FillUserHist( "M_e1j3_PASandMee100" , M_e1j3, pileup_weight * gen_weight ) ;
           FillUserHist( "M_e2j3_PASandMee100" , M_e2j3, pileup_weight * gen_weight ) ;
           FillUserHist( "M_j1j3_PASandMee100" , M_j1j3, pileup_weight * gen_weight ) ;
           FillUserHist( "M_j2j3_PASandMee100" , M_j2j3, pileup_weight * gen_weight ) ;
           FillUserHist( "M_eejjj_PASandMee100", M_eejjj,pileup_weight * gen_weight ) ;
           FillUserHist( "Ptj1j2j3_PASandMee100"            , Pt_j1j2j3           , pileup_weight * gen_weight );
           FillUserHist( "Ptj2j3_PASandMee100"              , Pt_j2j3             , pileup_weight * gen_weight );
           FillUserHist( "Ptj1j3_PASandMee100"              , Pt_j1j3             , pileup_weight * gen_weight );
           FillUserHist( "Ptee_Minus_Ptj1j2j3_PASandMee100" , Pt_e1e2 - Pt_j1j2j3 , pileup_weight * gen_weight );
         }
       }

       //--------------------------------------------------------------------------
       // Preselection + M(ee) normalization region plots
       //--------------------------------------------------------------------------

       if ( M_e1e2 > 80.0 && M_e1e2 < 100.0 ){
         FillUserHist("Mee_80_100_Preselection", M_e1e2, pileup_weight * gen_weight ) ;
         if      ( isEBEB ) FillUserHist( "Mee_EBEB_80_100_PAS", M_e1e2, pileup_weight * gen_weight );
         else if ( isEBEE ) FillUserHist( "Mee_EBEE_80_100_PAS", M_e1e2, pileup_weight * gen_weight );
         else if ( isEEEE ) FillUserHist( "Mee_EEEE_80_100_PAS", M_e1e2, pileup_weight * gen_weight );
         if      ( isEB   ) FillUserHist( "Mee_EB_80_100_PAS"  , M_e1e2, pileup_weight * gen_weight );
       }

       if ( M_e1e2 > 70.0 && M_e1e2 < 110.0 ){
         FillUserHist("Mee_70_110_Preselection", M_e1e2, pileup_weight * gen_weight ) ;
         if ( sT_eejj > 600 ) FillUserHist("Mee_70_110_ST600_Preselection", M_e1e2, pileup_weight * gen_weight ) ;
         if      ( isEBEB ) {
           FillUserHist( "Mee_EBEB_70_110_PAS", M_e1e2, pileup_weight * gen_weight );
           FillUserHist( "Mee_EBEB_70_110_Uncorr_PAS", M_e1e2Uncorr, pileup_weight * gen_weight );
         }
         else if ( isEBEE ) FillUserHist( "Mee_EBEE_70_110_PAS", M_e1e2, pileup_weight * gen_weight );
         else if ( isEEEE ) FillUserHist( "Mee_EEEE_70_110_PAS", M_e1e2, pileup_weight * gen_weight );
         if      ( isEB   ) FillUserHist( "Mee_EB_70_110_PAS"  , M_e1e2, pileup_weight * gen_weight );

         //FillUserHist( "ProcessID_ZWindow", ProcessID, pileup_weight * gen_weight );
         //if ( ProcessID == 0 ) FillUserHist ( "Mee_70_110_Preselection_Process0", M_e1e2, pileup_weight * gen_weight );
         //if ( ProcessID == 1 ) FillUserHist ( "Mee_70_110_Preselection_Process1", M_e1e2, pileup_weight * gen_weight );
         //if ( ProcessID == 2 ) FillUserHist ( "Mee_70_110_Preselection_Process2", M_e1e2, pileup_weight * gen_weight );
         //if ( ProcessID == 3 ) FillUserHist ( "Mee_70_110_Preselection_Process3", M_e1e2, pileup_weight * gen_weight );
         //if ( ProcessID == 4 ) FillUserHist ( "Mee_70_110_Preselection_Process4", M_e1e2, pileup_weight * gen_weight );
       }

       //--------------------------------------------------------------------------
       // BDT preselection plots
       //--------------------------------------------------------------------------
       if(evaluateBDT) {
         for (int i_lq_mass = 0; i_lq_mass < n_lq_mass; ++i_lq_mass ){
           int lq_mass = LQ_MASS[i_lq_mass];
           sprintf(cut_name, "BDTOutput_LQ%d", lq_mass );
           float bdtOutput = getVariableValue(cut_name);
           sprintf(cut_name, "BDTOutput_TrainRegion_LQ%d", lq_mass );
           FillUserHist(cut_name, bdtOutput, gen_weight * pileup_weight );
           sprintf(cut_name, "BDTOutput_noWeight_TrainRegion_LQ%d", lq_mass );
           FillUserHist(cut_name, bdtOutput );
         }
       }

       //--------------------------------------------------------------------------
       // Region of interest plots
       //--------------------------------------------------------------------------

       if ( do_roi_plots && passed_region_of_interest ) {


         FillUserHist("CorrIsolation_1stEle_ROI"         , Ele1_CorrIsolation                  , pileup_weight * gen_weight    );
         FillUserHist("DeltaEtaTrkSC_1stEle_ROI"         , Ele1_DeltaEtaTrkSC                  , pileup_weight * gen_weight    );
         FillUserHist("EcalIsolation_1stEle_ROI"         , Ele1_EcalIsolation                  , pileup_weight * gen_weight    );
         FillUserHist("HcalIsolation_1stEle_ROI"         , Ele1_HcalIsolation                  , pileup_weight * gen_weight    );
         FillUserHist("TrkIsolation_1stEle_ROI"          , Ele1_TrkIsolation                   , pileup_weight * gen_weight    );
         FillUserHist("HasMatchedPhot_1stEle_ROI"        , Ele1_HasMatchedPhot                 , pileup_weight * gen_weight    );
         FillUserHist("HoE_1stEle_ROI"                   , Ele1_HoE                            , pileup_weight * gen_weight    );
         FillUserHist("LeadVtxDistXY_1stEle_ROI"         , Ele1_LeadVtxDistXY                  , pileup_weight * gen_weight    );
         FillUserHist("LeadVtxDistZ_1stEle_ROI"          , Ele1_LeadVtxDistZ                   , pileup_weight * gen_weight    );
         FillUserHist("MissingHits_1stEle_ROI"           , Ele1_MissingHits                    , pileup_weight * gen_weight    );
         if ( fabs(Ele1_Eta) < eleEta_bar ) {
           FillUserHist("SigmaIEtaIEta_Barrel_1stEle_ROI", Ele1_Full5x5SigmaIEtaIEta                  , pileup_weight * gen_weight    );
         }
         else if ( fabs(Ele1_Eta) > eleEta_end1_min && fabs(Ele2_Eta) < eleEta_end2_max ){
           FillUserHist("SigmaIEtaIEta_Endcap_1stEle_ROI", Ele1_Full5x5SigmaIEtaIEta                  , pileup_weight * gen_weight    );
         }

         FillUserHist("CorrIsolation_2ndEle_ROI"         , Ele2_CorrIsolation                  , pileup_weight * gen_weight    );
         FillUserHist("DeltaEtaTrkSC_2ndEle_ROI"         , Ele2_DeltaEtaTrkSC                  , pileup_weight * gen_weight    );
         FillUserHist("EcalIsolation_2ndEle_ROI"         , Ele2_EcalIsolation                  , pileup_weight * gen_weight    );
         FillUserHist("HcalIsolation_2ndEle_ROI"         , Ele2_HcalIsolation                  , pileup_weight * gen_weight    );
         FillUserHist("TrkIsolation_2ndEle_ROI"          , Ele2_TrkIsolation                   , pileup_weight * gen_weight    );
         FillUserHist("HasMatchedPhot_2ndEle_ROI"        , Ele2_HasMatchedPhot                 , pileup_weight * gen_weight    );
         FillUserHist("HoE_2ndEle_ROI"                   , Ele2_HoE                            , pileup_weight * gen_weight    );
         FillUserHist("LeadVtxDistXY_2ndEle_ROI"         , Ele2_LeadVtxDistXY                  , pileup_weight * gen_weight    );
         FillUserHist("LeadVtxDistZ_2ndEle_ROI"          , Ele2_LeadVtxDistZ                   , pileup_weight * gen_weight    );
         FillUserHist("MissingHits_2ndEle_ROI"           , Ele2_MissingHits                    , pileup_weight * gen_weight    );
         if ( fabs(Ele2_Eta) < eleEta_bar ) {
           FillUserHist("SigmaIEtaIEta_Barrel_2ndEle_ROI", Ele2_Full5x5SigmaIEtaIEta                  , pileup_weight * gen_weight    );
         }
         else if ( fabs(Ele2_Eta) > eleEta_end1_min && fabs(Ele2_Eta) < eleEta_end2_max ){
           FillUserHist("SigmaIEtaIEta_Endcap_2ndEle_ROI", Ele2_Full5x5SigmaIEtaIEta                  , pileup_weight * gen_weight    );
         }


         FillUserHist("Me1j1_ROI"           , M_e1j1                         , pileup_weight * gen_weight );
         FillUserHist("Me1j2_ROI"           , M_e1j2                         , pileup_weight * gen_weight );
         FillUserHist("Me2j1_ROI"           , M_e2j1                         , pileup_weight * gen_weight );
         FillUserHist("Me2j2_ROI"           , M_e2j2                         , pileup_weight * gen_weight );
         FillUserHist("Ptee_ROI"            , Pt_e1e2                        , pileup_weight * gen_weight );
         FillUserHist("Eta1stJet_ROI"       , Jet1_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Eta2ndJet_ROI"       , Jet2_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Eta1stEle_ROI"        , Ele1_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Eta2ndEle_ROI"        , Ele2_Eta                       , pileup_weight * gen_weight );
         FillUserHist("Phi1stJet_ROI"       , Jet1_Phi                       , pileup_weight * gen_weight );
         FillUserHist("Phi2ndJet_ROI"       , Jet2_Phi                       , pileup_weight * gen_weight );
         FillUserHist("Phi1stEle_ROI"        , Ele1_Phi                       , pileup_weight * gen_weight );
         FillUserHist("Phi2ndEle_ROI"        , Ele2_Phi                       , pileup_weight * gen_weight );
         FillUserTH2D("MeeVsST_ROI" , M_e1e2, sT_eejj, pileup_weight * gen_weight );
         FillUserHist("Mee_ROI"            , M_e1e2                         , pileup_weight * gen_weight );
         FillUserHist("sT_zjj_ROI"          , sT_zjj                         , pileup_weight * gen_weight );
         FillUserHist("nVertex_ROI"         , nVertex                        , pileup_weight * gen_weight );
         FillUserHist("nJet_ROI"            , nJet_ptCut                     , pileup_weight * gen_weight );
         FillUserHist("EleChargeSum_ROI"    , Ele1_Charge + Ele2_Charge      , pileup_weight * gen_weight );
         FillUserHist("Meejj_ROI"           , M_eejj                         , pileup_weight * gen_weight );
         FillUserHist("Meej_ROI"            , M_eej                          , pileup_weight * gen_weight );
         FillUserHist("Mejj_ROI"            , M_ejj                          , pileup_weight * gen_weight );
         FillUserHist("Mjj_ROI"             , M_j1j2                         , pileup_weight * gen_weight );
         FillUserHist("Mej_selected_avg_ROI", M_ej_avg                       , pileup_weight * gen_weight );
         FillUserHist("minDR_ZJet_ROI"      , min_DeltaR_Zj                  , pileup_weight * gen_weight );
         FillUserHist("DR_ZJet1_ROI"        , DR_ZJ1                         , pileup_weight * gen_weight );
         FillUserHist("DR_ZJet2_ROI"        , DR_ZJ2                         , pileup_weight * gen_weight );
         FillUserHist("MET_ROI"             , PFMET_Type1_Pt              , pileup_weight * gen_weight );
         FillUserHist("sT_ROI"              , sT_eejj                        , pileup_weight * gen_weight );
         FillUserHist("sTlep_ROI"           , Ele1_Pt + Ele2_Pt              , pileup_weight * gen_weight );
         FillUserHist("sTjet_ROI"           , Jet1_Pt + Jet2_Pt              , pileup_weight * gen_weight );
         FillUserHist("Pt1stEle_ROI"        , Ele1_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Pt2ndEle_ROI"        , Ele2_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Pt1stJet_ROI"        , Jet1_Pt                        , pileup_weight * gen_weight );
         FillUserHist("Pt2ndJet_ROI"        , Jet2_Pt                        , pileup_weight * gen_weight );
         FillUserHist( "sTfrac_Jet1_ROI"    , Jet1_Pt / sT_eejj              , pileup_weight * gen_weight );
         FillUserHist( "sTfrac_Jet2_ROI"    , Jet2_Pt / sT_eejj              , pileup_weight * gen_weight );
         FillUserHist( "sTfrac_Ele1_ROI"    , Ele1_Pt / sT_eejj              , pileup_weight * gen_weight );
         FillUserHist( "sTfrac_Ele2_ROI"    , Ele2_Pt / sT_eejj              , pileup_weight * gen_weight );
         FillUserHist( "sTfrac_Jet_ROI"     , ( Jet1_Pt + Jet2_Pt ) / sT_eejj, pileup_weight * gen_weight );
         FillUserHist( "sTfrac_Ele_ROI"     , ( Ele1_Pt + Ele2_Pt ) / sT_eejj, pileup_weight * gen_weight );
         FillUserHist("Ptj1j2_ROI"            , Pt_j1j2                        , pileup_weight * gen_weight ) ;
         FillUserHist("Ptee_Minus_Ptj1j2_ROI" , Pt_e1e2 - Pt_j1j2              , pileup_weight * gen_weight ) ;


         if ( nJet_ptCut > 2 ) {
           FillUserHist( "M_e1j3_ROI"  , M_e1j3,  pileup_weight * gen_weight ) ;
           FillUserHist( "M_e2j3_ROI"  , M_e2j3,  pileup_weight * gen_weight ) ;
           FillUserHist( "M_j1j3_ROI"  , M_j1j3,  pileup_weight * gen_weight ) ;
           FillUserHist( "M_j2j3_ROI"  , M_j2j3,  pileup_weight * gen_weight ) ;
           FillUserHist( "M_eejjj_ROI" , M_eejjj, pileup_weight * gen_weight ) ;
           FillUserHist( "Ptj1j2j3_ROI"            , Pt_j1j2j3           , pileup_weight * gen_weight );
           FillUserHist( "Ptj2j3_ROI"              , Pt_j2j3             , pileup_weight * gen_weight );
           FillUserHist( "Ptj1j3_ROI"              , Pt_j1j3             , pileup_weight * gen_weight );
           FillUserHist( "Ptee_Minus_Ptj1j2j3_ROI" , Pt_e1e2 - Pt_j1j2j3 , pileup_weight * gen_weight );
         }
       }

       //--------------------------------------------------------------------------
       // Final selection plots
       //--------------------------------------------------------------------------

       if(doFinalSelections)
       {
         for (int i_lq_mass = 0; i_lq_mass < n_lq_mass; ++i_lq_mass ){
           int  lq_mass = LQ_MASS      [i_lq_mass];
           bool pass    = passed_vector[i_lq_mass];
           if ( !pass ) continue;

           sprintf(plot_name, "GeneratorWeight_LQ%d"        , lq_mass ); FillUserHist ( plot_name, gen_weight        );
           sprintf(plot_name, "Mej_selected_avg_LQ%d"       , lq_mass ); FillUserHist ( plot_name, M_ej_avg          , pileup_weight * gen_weight );
           sprintf(plot_name, "Mej_selected_min_LQ%d"       , lq_mass ); FillUserHist ( plot_name, M_ej_min          , pileup_weight * gen_weight );
           sprintf(plot_name, "Mej_selected_max_LQ%d"       , lq_mass ); FillUserHist ( plot_name, M_ej_max          , pileup_weight * gen_weight );
           sprintf(plot_name, "Mej_minmax_LQ%d"             , lq_mass ); FillUserHist ( plot_name, M_ej_min          , pileup_weight * gen_weight );
           sprintf(plot_name, "Mej_minmax_LQ%d"             , lq_mass ); FillUserHist ( plot_name, M_ej_max          , pileup_weight * gen_weight );
           sprintf(plot_name, "sT_eejj_LQ%d"                , lq_mass ); FillUserHist ( plot_name, sT_eejj           , pileup_weight * gen_weight );
           sprintf(plot_name, "Mee_LQ%d"                    , lq_mass ); FillUserHist ( plot_name, M_e1e2            , pileup_weight * gen_weight );
           sprintf(plot_name, "DR_Ele1Jet1_LQ%d"            , lq_mass ); FillUserHist ( plot_name, DR_Ele1Jet1       , pileup_weight * gen_weight );
           sprintf(plot_name, "Mej_selected_min_vs_max_LQ%d", lq_mass ); FillUserTH2D ( plot_name, M_ej_min, M_ej_max, pileup_weight * gen_weight );


           sprintf(plot_name, "CorrIsolation_1stEle_LQ%d"      , lq_mass );   FillUserHist(plot_name,  Ele1_CorrIsolation             , pileup_weight * gen_weight );
           sprintf(plot_name, "DeltaEtaTrkSC_1stEle_LQ%d"      , lq_mass );   FillUserHist(plot_name,  Ele1_DeltaEtaTrkSC             , pileup_weight * gen_weight );
           sprintf(plot_name, "EcalIsolation_1stEle_LQ%d"      , lq_mass );   FillUserHist(plot_name,  Ele1_EcalIsolation             , pileup_weight * gen_weight );
           sprintf(plot_name, "HcalIsolation_1stEle_LQ%d"      , lq_mass );   FillUserHist(plot_name,  Ele1_HcalIsolation             , pileup_weight * gen_weight );
           sprintf(plot_name, "TrkIsolation_1stEle_LQ%d"       , lq_mass );   FillUserHist(plot_name,  Ele1_TrkIsolation              , pileup_weight * gen_weight );
           sprintf(plot_name, "HasMatchedPhot_1stEle_LQ%d"     , lq_mass );   FillUserHist(plot_name,  Ele1_HasMatchedPhot            , pileup_weight * gen_weight );
           sprintf(plot_name, "HoE_1stEle_LQ%d"                , lq_mass );   FillUserHist(plot_name,  Ele1_HoE                       , pileup_weight * gen_weight );
           sprintf(plot_name, "LeadVtxDistXY_1stEle_LQ%d"      , lq_mass );   FillUserHist(plot_name,  Ele1_LeadVtxDistXY             , pileup_weight * gen_weight );
           sprintf(plot_name, "LeadVtxDistZ_1stEle_LQ%d"       , lq_mass );   FillUserHist(plot_name,  Ele1_LeadVtxDistZ              , pileup_weight * gen_weight );
           sprintf(plot_name, "MissingHits_1stEle_LQ%d"        , lq_mass );   FillUserHist(plot_name,  Ele1_MissingHits               , pileup_weight * gen_weight );

           if ( fabs(Ele1_Eta) < eleEta_bar ) {
             sprintf(plot_name, "Full5x5SigmaIEtaIEta_Barrel_1stEle_LQ%d", lq_mass ); FillUserHist( plot_name , Ele1_Full5x5SigmaIEtaIEta , pileup_weight * gen_weight    );
           }
           else if ( fabs(Ele1_Eta) > eleEta_end1_min && fabs(Ele2_Eta) < eleEta_end2_max ){
             sprintf(plot_name, "Full5x5SigmaIEtaIEta_Endcap_1stEle_LQ%d", lq_mass ); FillUserHist( plot_name , Ele1_Full5x5SigmaIEtaIEta , pileup_weight * gen_weight    );
           }

           sprintf(plot_name, "CorrIsolation_2ndEle_LQ%d"      , lq_mass );   FillUserHist(plot_name,  Ele2_CorrIsolation             , pileup_weight * gen_weight );
           sprintf(plot_name, "DeltaEtaTrkSC_2ndEle_LQ%d"      , lq_mass );   FillUserHist(plot_name,  Ele2_DeltaEtaTrkSC             , pileup_weight * gen_weight );
           sprintf(plot_name, "EcalIsolation_2ndEle_LQ%d"      , lq_mass );   FillUserHist(plot_name,  Ele2_EcalIsolation             , pileup_weight * gen_weight );
           sprintf(plot_name, "HcalIsolation_2ndEle_LQ%d"      , lq_mass );   FillUserHist(plot_name,  Ele2_HcalIsolation             , pileup_weight * gen_weight );
           sprintf(plot_name, "TrkIsolation_2ndEle_LQ%d"       , lq_mass );   FillUserHist(plot_name,  Ele2_TrkIsolation              , pileup_weight * gen_weight );
           sprintf(plot_name, "HasMatchedPhot_2ndEle_LQ%d"     , lq_mass );   FillUserHist(plot_name,  Ele2_HasMatchedPhot            , pileup_weight * gen_weight );
           sprintf(plot_name, "HoE_2ndEle_LQ%d"                , lq_mass );   FillUserHist(plot_name,  Ele2_HoE                       , pileup_weight * gen_weight );
           sprintf(plot_name, "LeadVtxDistXY_2ndEle_LQ%d"      , lq_mass );   FillUserHist(plot_name,  Ele2_LeadVtxDistXY             , pileup_weight * gen_weight );
           sprintf(plot_name, "LeadVtxDistZ_2ndEle_LQ%d"       , lq_mass );   FillUserHist(plot_name,  Ele2_LeadVtxDistZ              , pileup_weight * gen_weight );
           sprintf(plot_name, "MissingHits_2ndEle_LQ%d"        , lq_mass );   FillUserHist(plot_name,  Ele2_MissingHits               , pileup_weight * gen_weight );

           if ( fabs(Ele2_Eta) < eleEta_bar ) {
             sprintf(plot_name, "Full5x5SigmaIEtaIEta_Barrel_2ndEle_LQ%d", lq_mass ); FillUserHist( plot_name , Ele2_Full5x5SigmaIEtaIEta , pileup_weight * gen_weight    );
           }
           else if ( fabs(Ele2_Eta) > eleEta_end2_min && fabs(Ele2_Eta) < eleEta_end2_max ){
             sprintf(plot_name, "Full5x5SigmaIEtaIEta_Endcap_2ndEle_LQ%d", lq_mass ); FillUserHist( plot_name , Ele2_Full5x5SigmaIEtaIEta , pileup_weight * gen_weight    );
           }

           sprintf(plot_name, "Me1j1_LQ%d"             , lq_mass ); FillUserHist( plot_name , M_e1j1                         , pileup_weight * gen_weight );
           sprintf(plot_name, "Me1j2_LQ%d"             , lq_mass ); FillUserHist( plot_name , M_e1j2                         , pileup_weight * gen_weight );
           sprintf(plot_name, "Me2j1_LQ%d"             , lq_mass ); FillUserHist( plot_name , M_e2j1                         , pileup_weight * gen_weight );
           sprintf(plot_name, "Me2j2_LQ%d"             , lq_mass ); FillUserHist( plot_name , M_e2j2                         , pileup_weight * gen_weight );
           sprintf(plot_name, "Ptee_LQ%d"              , lq_mass ); FillUserHist( plot_name , Pt_e1e2                        , pileup_weight * gen_weight );
           sprintf(plot_name, "Eta1stJet_LQ%d"         , lq_mass ); FillUserHist( plot_name , Jet1_Eta                       , pileup_weight * gen_weight );
           sprintf(plot_name, "Eta2ndJet_LQ%d"         , lq_mass ); FillUserHist( plot_name , Jet2_Eta                       , pileup_weight * gen_weight );
           sprintf(plot_name, "Eta1stEle_LQ%d"         , lq_mass ); FillUserHist( plot_name , Ele1_Eta                       , pileup_weight * gen_weight );
           sprintf(plot_name, "Eta2ndEle_LQ%d"         , lq_mass ); FillUserHist( plot_name , Ele2_Eta                       , pileup_weight * gen_weight );
           sprintf(plot_name, "Phi1stJet_LQ%d"         , lq_mass ); FillUserHist( plot_name , Jet1_Phi                       , pileup_weight * gen_weight );
           sprintf(plot_name, "Phi2ndJet_LQ%d"         , lq_mass ); FillUserHist( plot_name , Jet2_Phi                       , pileup_weight * gen_weight );
           sprintf(plot_name, "Phi1stEle_LQ%d"         , lq_mass ); FillUserHist( plot_name , Ele1_Phi                       , pileup_weight * gen_weight );
           sprintf(plot_name, "Phi2ndEle_LQ%d"         , lq_mass ); FillUserHist( plot_name , Ele2_Phi                       , pileup_weight * gen_weight );
           sprintf(plot_name, "MeeVsST_LQ%d"           , lq_mass ); FillUserTH2D( plot_name , M_e1e2, sT_eejj                , pileup_weight * gen_weight );
           sprintf(plot_name, "sT_zjj_LQ%d"            , lq_mass ); FillUserHist( plot_name , sT_zjj                         , pileup_weight * gen_weight );
           sprintf(plot_name, "nVertex_LQ%d"           , lq_mass ); FillUserHist( plot_name , nVertex                        , pileup_weight * gen_weight );
           sprintf(plot_name, "nJet_LQ%d"              , lq_mass ); FillUserHist( plot_name , nJet_ptCut                     , pileup_weight * gen_weight );
           sprintf(plot_name, "EleChargeSum_LQ%d"      , lq_mass ); FillUserHist( plot_name , Ele1_Charge + Ele2_Charge      , pileup_weight * gen_weight );
           sprintf(plot_name, "Meejj_LQ%d"             , lq_mass ); FillUserHist( plot_name , M_eejj                         , pileup_weight * gen_weight );
           sprintf(plot_name, "Meej_LQ%d"              , lq_mass ); FillUserHist( plot_name , M_eej                          , pileup_weight * gen_weight );
           sprintf(plot_name, "Mejj_LQ%d"              , lq_mass ); FillUserHist( plot_name , M_ejj                          , pileup_weight * gen_weight );
           sprintf(plot_name, "Mjj_LQ%d"               , lq_mass ); FillUserHist( plot_name , M_j1j2                         , pileup_weight * gen_weight );
           sprintf(plot_name, "minDR_ZJet_LQ%d"        , lq_mass ); FillUserHist( plot_name , min_DeltaR_Zj                  , pileup_weight * gen_weight );
           sprintf(plot_name, "DR_ZJet1_LQ%d"          , lq_mass ); FillUserHist( plot_name , DR_ZJ1                         , pileup_weight * gen_weight );
           sprintf(plot_name, "DR_ZJet2_LQ%d"          , lq_mass ); FillUserHist( plot_name , DR_ZJ2                         , pileup_weight * gen_weight );
           sprintf(plot_name, "MET_LQ%d"               , lq_mass ); FillUserHist( plot_name , PFMET_Type1_Pt              , pileup_weight * gen_weight );
           sprintf(plot_name, "sTlep_LQ%d"             , lq_mass ); FillUserHist( plot_name , Ele1_Pt + Ele2_Pt              , pileup_weight * gen_weight );
           sprintf(plot_name, "sTjet_LQ%d"             , lq_mass ); FillUserHist( plot_name , Jet1_Pt + Jet2_Pt              , pileup_weight * gen_weight );
           sprintf(plot_name, "Pt1stEle_LQ%d"          , lq_mass ); FillUserHist( plot_name , Ele1_Pt                        , pileup_weight * gen_weight );
           sprintf(plot_name, "Pt2ndEle_LQ%d"          , lq_mass ); FillUserHist( plot_name , Ele2_Pt                        , pileup_weight * gen_weight );
           sprintf(plot_name, "Pt1stJet_LQ%d"          , lq_mass ); FillUserHist( plot_name , Jet1_Pt                        , pileup_weight * gen_weight );
           sprintf(plot_name, "Pt2ndJet_LQ%d"          , lq_mass ); FillUserHist( plot_name , Jet2_Pt                        , pileup_weight * gen_weight );
           sprintf(plot_name, "sTfrac_Jet1_LQ%d"       , lq_mass ); FillUserHist( plot_name , Jet1_Pt / sT_eejj              , pileup_weight * gen_weight );
           sprintf(plot_name, "sTfrac_Jet2_LQ%d"       , lq_mass ); FillUserHist( plot_name , Jet2_Pt / sT_eejj              , pileup_weight * gen_weight );
           sprintf(plot_name, "sTfrac_Ele1_LQ%d"       , lq_mass ); FillUserHist( plot_name , Ele1_Pt / sT_eejj              , pileup_weight * gen_weight );
           sprintf(plot_name, "sTfrac_Ele2_LQ%d"       , lq_mass ); FillUserHist( plot_name , Ele2_Pt / sT_eejj              , pileup_weight * gen_weight );
           sprintf(plot_name, "sTfrac_Jet_LQ%d"        , lq_mass ); FillUserHist( plot_name , ( Jet1_Pt + Jet2_Pt ) / sT_eejj, pileup_weight * gen_weight );
           sprintf(plot_name, "sTfrac_Ele_LQ%d"        , lq_mass ); FillUserHist( plot_name , ( Ele1_Pt + Ele2_Pt ) / sT_eejj, pileup_weight * gen_weight );
           sprintf(plot_name, "Ptj1j2_LQ%d"            , lq_mass ); FillUserHist( plot_name , Pt_j1j2                        , pileup_weight * gen_weight );
           sprintf(plot_name, "Ptee_Minus_Ptj1j2_LQ%d" , lq_mass ); FillUserHist( plot_name , Pt_e1e2 - Pt_j1j2              , pileup_weight * gen_weight );
           // checking electrons
           sprintf(plot_name,"SCEta_1stEle_LQ%d" , lq_mass );                                FillUserHist(plot_name,Ele1_SCEta, pileup_weight*gen_weight);
           sprintf(plot_name,"EleEta_1stEle_LQ%d" , lq_mass );                               FillUserHist(plot_name,Ele1_Eta,pileup_weight*gen_weight);
           sprintf(plot_name,"DeltaEtaTrkSC_1stEle_LQ%d" , lq_mass );                        FillUserHist(plot_name,Ele1_DeltaEtaTrkSC,pileup_weight*gen_weight);
           sprintf(plot_name,"SCEtaMinusEleEta_1stEle_LQ%d" , lq_mass );                     FillUserHist(plot_name,Ele1_SCEta-Ele1_Eta,pileup_weight*gen_weight);
           sprintf(plot_name,"DeltaEtaTrkSC_Minus_SCEtaMinusEleEta_1stEle_LQ%d" , lq_mass ); FillUserHist(plot_name,Ele1_DeltaEtaTrkSC-(Ele1_SCEta-Ele1_Eta),pileup_weight*gen_weight);
           sprintf(plot_name,"SCEta_2ndEle_LQ%d" , lq_mass );                                FillUserHist(plot_name,Ele2_SCEta, pileup_weight*gen_weight);
           sprintf(plot_name,"EleEta_2ndEle_LQ%d" , lq_mass );                               FillUserHist(plot_name,Ele2_Eta,pileup_weight*gen_weight);
           sprintf(plot_name,"DeltaEtaTrkSC_2ndEle_LQ%d" , lq_mass );                        FillUserHist(plot_name,Ele2_DeltaEtaTrkSC,pileup_weight*gen_weight);
           sprintf(plot_name,"SCEtaMinusEleEta_2ndEle_LQ%d", lq_mass );                      FillUserHist(plot_name,Ele2_SCEta-Ele2_Eta,pileup_weight*gen_weight);
           sprintf(plot_name,"DeltaEtaTrkSC_Minus_SCEtaMinusEleEta_2ndEle_LQ%d" , lq_mass ); FillUserHist(plot_name,Ele2_DeltaEtaTrkSC-(Ele2_SCEta-Ele2_Eta),pileup_weight*gen_weight);
           // muon kinematics
           sprintf(plot_name, "Eta1stMuon_LQ%d"         , lq_mass ); FillUserHist( plot_name , Muon1_Eta                       , pileup_weight * gen_weight );
           sprintf(plot_name, "Eta2ndMuon_LQ%d"         , lq_mass ); FillUserHist( plot_name , Muon2_Eta                       , pileup_weight * gen_weight );
           sprintf(plot_name, "Phi1stMuon_LQ%d"         , lq_mass ); FillUserHist( plot_name , Muon1_Phi                       , pileup_weight * gen_weight );
           sprintf(plot_name, "Pt1stMuon_LQ%d"          , lq_mass ); FillUserHist( plot_name , Muon1_Pt                        , pileup_weight * gen_weight );
           sprintf(plot_name, "Pt2ndMuon_LQ%d"          , lq_mass ); FillUserHist( plot_name , Muon2_Pt                        , pileup_weight * gen_weight );

         } // End final selection

         if( hasCut("sT_eejj_LQ300") && passedCut("sT_eejj_LQ300") && passedCut("min_M_ej_LQ300"))
           FillUserHist("Mee_70_110_LQ300", M_e1e2 , pileup_weight * gen_weight );
         if( hasCut("sT_eejj_LQ600") && passedCut("sT_eejj_LQ600") && passedCut("min_M_ej_LQ600"))
           FillUserHist("Mee_70_110_LQ600", M_e1e2 , pileup_weight * gen_weight );
         if( hasCut("sT_eejj_LQ800") && passedCut("sT_eejj_LQ800") && passedCut("min_M_ej_LQ800"))
           FillUserHist("Mee_70_110_LQ800", M_e1e2 , pileup_weight * gen_weight );
         if( hasCut("sT_eejj_LQ900") && passedCut("sT_eejj_LQ900") && passedCut("min_M_ej_LQ900"))
           FillUserHist("Mee_70_110_LQ900", M_e1e2 , pileup_weight * gen_weight );
         if( hasCut("sT_eejj_LQ1000") && passedCut("sT_eejj_LQ1000") && passedCut("min_M_ej_LQ1000"))
           FillUserHist("Mee_70_110_LQ1000", M_e1e2 , pileup_weight * gen_weight );

       }

     } // End preselection
   } // End loop over events

   std::cout << "analysisClass::Loop() ends" <<std::endl;
}
