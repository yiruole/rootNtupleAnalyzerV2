#define analysisClass_cxx
#include "analysisClass.h"
#include <TH2.h>
#include <TH1F.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TLorentzVector.h>
#include <TVector2.h>
#include <TVector3.h>
// for fake rate
#include "QCDFakeRate.h"
// for prescales
//#include "Run2PhotonTriggerPrescales.h"
#include "PrescaleProvider.h"
#include <set>

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

  // LQ650 only 2012
  //const int n_lq_mass = 1;
  //int LQ_MASS[n_lq_mass] = { 650 };

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
  // Get pre-cut values
  //--------------------------------------------------------------------------
  // eta boundaries

  double eleEta_bar            = getPreCutValue1("eleEta_bar");
  double eleEta_end1_min       = getPreCutValue1("eleEta_end1");
  double eleEta_end1_max       = getPreCutValue2("eleEta_end1");
  double eleEta_end2_min       = getPreCutValue1("eleEta_end2");
  double eleEta_end2_max       = getPreCutValue2("eleEta_end2");

  // prescales
  //Run2PhotonTriggerPrescales run2PhotonTriggerPrescales;
	PrescaleProvider psProv("/afs/cern.ch/user/s/scooper/work/public/Leptoquarks/ul-analysis-inputs/prescales/2016/triggerData2016");

  //--------------------------------------------------------------------------
  // Analysis year
  //--------------------------------------------------------------------------
  string analysisYear = getPreCutString1("AnalysisYear");
  int analysisYearInt = -1;
  if(analysisYear.find("2016") != string::npos)
      analysisYearInt = 2016;
  else
    analysisYearInt = stoi(analysisYear);

  //--------------------------------------------------------------------------
  // electron ID
  //--------------------------------------------------------------------------
  std::string electronIDType     = getPreCutString1("electronIDType");
  if(electronIDType != "HEEP" && electronIDType != "EGMLoose") {
    STDOUT("electronIDType=" << electronIDType << " is unknown! Please implement it in the analysisClass code. Exiting.");
    exit(-5);
  }

  //--------------------------------------------------------------------------
  // QCD Fake Rate loading part
  //--------------------------------------------------------------------------
  std::string qcdFileName = getPreCutString1("QCDFakeRateFilename");
  std::vector<std::string> regionVec;
  if(analysisYearInt < 2018)
    regionVec = {"2Jet_TrkIsoHEEP7vsHLTPt_PAS"};
  else
    regionVec = {
      "Bar_pre319077_2Jet",
      "End1_pre319077_2Jet",
      "End2_pre319077_2Jet",
      "Bar_noHEM_post319077_2Jet",
      "End1_noHEM_post319077_2Jet",
      "End2_noHEM_post319077_2Jet",
      "Bar_HEMonly_post319077_2Jet",
      "End1_HEMonly_post319077_2Jet",
      "End2_HEMonly_post319077_2Jet"};
  QCDFakeRate qcdFR(qcdFileName, "fr2D_", regionVec, true); // look up from hist

  std::string qcdCalcType  = getPreCutString1("QCDCalcType");
  bool doSingleFR = false;
  if(qcdCalcType == "single")
    doSingleFR = true;
  else if(qcdCalcType != "double")
    throw runtime_error("Could not understand value in cut file for precut QCDCalcType: " + qcdCalcType);
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

  CreateUserTH1D( "EventCount"            ,    1    , 0      , 1	 );

  CreateUserTH1D( "FakeRateEffective"     ,    50   , 0      , 1	 );
  CreateUserTH1D( "FakeRateEffective_PassNEle"     ,    50   , 0      , 1	 );
  CreateUserTH1D( "MinPrescale"           ,    1000 , 0      , 1000	 );

  CreateUserTH1D( "M_j1j3_PAS"            ,    200 , 0       , 2000	 );
  CreateUserTH1D( "M_j2j3_PAS"            ,    200 , 0       , 2000	 );
  CreateUserTH1D( "M_e1j3_PAS"            ,    200 , 0       , 2000	 );
  CreateUserTH1D( "M_e2j3_PAS"            ,    200 , 0       , 2000	 );
  CreateUserTH1D( "M_eejjj_PAS"           ,    500 , 0       , 5000	 );

  CreateUserTH1D( "M_j1j3_PASandMee100"   ,    200 , 0       , 2000	 );
  CreateUserTH1D( "M_j2j3_PASandMee100"   ,    200 , 0       , 2000	 );
  CreateUserTH1D( "M_e1j3_PASandMee100"   ,    200 , 0       , 2000	 );
  CreateUserTH1D( "M_e2j3_PASandMee100"   ,    200 , 0       , 2000	 );
  CreateUserTH1D( "M_eejjj_PASandMee100"  ,    500 , 0       , 5000	 );


  CreateUserTH1D( "sTfrac_Jet1_PAS"       ,   100  ,  0.0    , 1.0      );
  CreateUserTH1D( "sTfrac_Jet2_PAS"       ,   100  ,  0.0    , 1.0      );
  CreateUserTH1D( "sTfrac_Ele1_PAS"       ,   100  ,  0.0    , 1.0      );
  CreateUserTH1D( "sTfrac_Ele2_PAS"       ,   100  ,  0.0    , 1.0      );
  CreateUserTH1D( "sTfrac_Jet_PAS"        ,   100  ,  0.0    , 1.0      );
  CreateUserTH1D( "sTfrac_Ele_PAS"        ,   100  ,  0.0    , 1.0      );
  CreateUserTH1D( "sTfrac_Jet1_PASandMee100"       ,   100  ,  0.0    , 1.0      );
  CreateUserTH1D( "sTfrac_Jet2_PASandMee100"       ,   100  ,  0.0    , 1.0      );
  CreateUserTH1D( "sTfrac_Ele1_PASandMee100"       ,   100  ,  0.0    , 1.0      );
  CreateUserTH1D( "sTfrac_Ele2_PASandMee100"       ,   100  ,  0.0    , 1.0      );
  CreateUserTH1D( "sTfrac_Jet_PASandMee100"        ,   100  ,  0.0    , 1.0      );
  CreateUserTH1D( "sTfrac_Ele_PASandMee100"        ,   100  ,  0.0    , 1.0      );
  CreateUserTH1D( "nElectron_PAS"         ,    5   , -0.5    , 4.5      );
  CreateUserTH1D( "nMuon_PAS"             ,    5   , -0.5    , 4.5      );
  CreateUserTH1D( "nJet_PAS"              ,    10  , -0.5    , 9.5      );
  CreateUserTH1D( "nJet_PASandMee100"        ,    10  , -0.5    , 9.5      );
  CreateUserTH1D( "Pt1stEle_PAS"	   , 	100 , 0       , 1000     );
  CreateUserTH1D( "Pt1stEle_PASandMee100" , 	100 , 0       , 1000     );
  CreateUserTH1D( "Eta1stEle_PAS"	   , 	100 , -5      , 5	 );
  CreateUserTH1D( "SCEta1stEle_PAS"	   , 	100 , -5      , 5	 );
  CreateUserTH1D( "DeltaEtaEleTrk1stEle_Presel", 400, -0.5,   0.5 );
  CreateUserTH1D( "Phi1stEle_PAS"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Pt2ndEle_PAS"	   , 	300 , 0       , 3000     );
  CreateUserTH1D( "Pt2ndEle_PASandMee100" , 	300 , 0       , 3000     );
  CreateUserTH1D( "Eta2ndEle_PAS"	   , 	100 , -5      , 5	 );
  CreateUserTH1D( "SCEta2ndEle_PAS"	   , 	100 , -5      , 5	 );
  CreateUserTH1D( "DeltaEtaEleTrk2ndEle_Presel", 400, -0.5,   0.5 );
  CreateUserTH1D( "Phi2ndEle_PAS"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Charge1stEle_PAS"	   , 	2   , -1.0001 , 1.0001	 );
  CreateUserTH1D( "Charge2ndEle_PAS"	   , 	2   , -1.0001 , 1.0001	 );
  CreateUserTH1D( "EleChargeSum_PAS"         ,    3   , -2.5    , 2.5  );
  CreateUserTH1D( "EleChargeSum_PASandMee100",    3   , -2.5    , 2.5  );
  CreateUserTH1D( "MET_PAS"               ,    200 , 0       , 1000	 );
  CreateUserTH1D( "METPhi_PAS"		   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Pt1stJet_PAS"          ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Pt2ndJet_PAS"          ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Pt1stJet_PASandMee100" ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Pt2ndJet_PASandMee100" ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Eta1stJet_PAS"         ,    100 , -5      , 5	 );
  CreateUserTH1D( "Eta2ndJet_PAS"         ,    100 , -5      , 5	 );
  CreateUserTH1D( "Phi1stJet_PAS"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Phi2ndJet_PAS"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "sTlep_PAS"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sTjet_PAS"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sTlep_PASandMee100"    ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sTjet_PASandMee100"    ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_PAS"                ,    300   , 0       , 3000	 );
  CreateUserTH1D( "sT_zjj_PAS"            ,    300   , 0       , 3000	  );
  CreateUserTH1D( "sT_zjj_PASandMee100"   ,    300   , 0       , 3000	  );
  CreateUserTH1D( "sT_PASandMee100"       ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_PASandMee110"       ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_PASandMee120"       ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_PASandMee130"       ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_PASandMee140"       ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_PASandMee150"       ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_PASandMee160"       ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_PASandMee170"       ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_PASandMee180"       ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_PASandMee190"       ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_PASandMee200"       ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Mjj_PAS"		   ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Mjj_PASandMee100"	   ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Mee_PAS"		   ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "Mee_PASandST445"       ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "MTenu_PAS"             ,    200 , 0       , 1000	 );
  CreateUserTH1D( "Me1j1_PAS"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me1j1_PASandMee100"    ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me1j2_PAS"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me2j1_PAS"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me2j2_PAS"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me1j_selected_PAS"     ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me2j_selected_PAS"     ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_selected_min_PAS"  ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_selected_max_PAS"  ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_asym_PAS"          ,    50  , 0       , 1   );
  CreateUserTH1D( "Mej_minmax_PAS"        ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_selected_avg_PAS"  ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_selected_avg_PASandMee100"  ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mejj_PAS"              ,    400 , 0       , 4000     );
  CreateUserTH1D( "Meej_PAS"              ,    400 , 0       , 4000     );
  CreateUserTH1D( "Meejj_PAS"             ,    400 , 0       , 4000     );
  // muon kinematics
  CreateUserTH1D( "Pt1stMuon_PAS"	   , 	100 , 0       , 1000     );
  CreateUserTH1D( "Eta1stMuon_PAS"	   , 	100 , -5      , 5	 );
  CreateUserTH1D( "Phi1stMuon_PAS"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Pt2ndMuon_PAS"	   , 	300 , 0       , 3000     );
  CreateUserTH1D( "Eta2ndMuon_PAS"	   , 	100 , -5      , 5	 );
  CreateUserTH1D( "Phi2ndMuon_PAS"	   , 	60  , -3.1416 , +3.1416	 );


  CreateUserTH1D( "Ptj1j2j3_PAS"                    ,    400 , 0       , 4000     );
  CreateUserTH1D( "Ptj1j2_PAS"                      ,    400 , 0       , 4000     );
  CreateUserTH1D( "Ptj2j3_PAS"                      ,    400 , 0       , 4000     );
  CreateUserTH1D( "Ptj1j3_PAS"                      ,    400 , 0       , 4000     );

  CreateUserTH1D( "Ptee_Minus_Ptj1j2_PAS"           ,    200 , -500    , 500      );
  CreateUserTH1D( "Ptee_Minus_Ptj1j2j3_PAS"         ,    200 , -500    , 500      );


  CreateUserTH1D( "Ptj1j2j3_PASandMee100"           ,    200 , 0       , 2000     );
  CreateUserTH1D( "Ptj1j2_PASandMee100"             ,    200 , 0       , 2000     );
  CreateUserTH1D( "Ptj2j3_PASandMee100"             ,    200 , 0       , 2000     );
  CreateUserTH1D( "Ptj1j3_PASandMee100"             ,    200 , 0       , 2000     );

  CreateUserTH1D( "Ptee_Minus_Ptj1j2_PASandMee100"  ,    200 , -500    , 500      );
  CreateUserTH1D( "Ptee_Minus_Ptj1j2j3_PASandMee100",    200 , -500    , 500      );





  CreateUserTH1D( "Ptee_PAS"              ,    200 , 0       , 2000     );
  CreateUserTH1D( "Ptee_PASandMee100"     ,    200 , 0       , 2000     );


  CreateUserTH1D( "nVertex_PAS"                     ,    101   , -0.5   , 100.5	 ) ;
  CreateUserTH1D( "nVertex_PASandMee100"            ,    101   , -0.5   , 100.5	 ) ;

  CreateUserTH1D( "DR_Ele1Jet1_PAS"	   , 	getHistoNBins("DR_Ele1Jet1"), getHistoMin("DR_Ele1Jet1"), getHistoMax("DR_Ele1Jet1")     ) ;
  CreateUserTH1D( "DR_Ele1Jet2_PAS"	   , 	getHistoNBins("DR_Ele1Jet2"), getHistoMin("DR_Ele1Jet2"), getHistoMax("DR_Ele1Jet2")     ) ;
  CreateUserTH1D( "DR_Ele2Jet1_PAS"	   , 	getHistoNBins("DR_Ele2Jet1"), getHistoMin("DR_Ele2Jet1"), getHistoMax("DR_Ele2Jet1")     ) ;
  CreateUserTH1D( "DR_Ele2Jet2_PAS"	   , 	getHistoNBins("DR_Ele2Jet2"), getHistoMin("DR_Ele2Jet2"), getHistoMax("DR_Ele2Jet2")     ) ;
  CreateUserTH1D( "DR_Jet1Jet2_PAS"	   , 	getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
  CreateUserTH1D( "DR_Ele1Ele2_PAS"	   , 	getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
  CreateUserTH1D( "minDR_EleJet_PAS"	   , 	getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
  CreateUserTH1D( "minDR_ZJet_PAS"        ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;

  CreateUserTH1D( "DR_ZJet1_PAS"        ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
  CreateUserTH1D( "DR_ZJet2_PAS"        ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;


  CreateUserTH2D( "Me1jVsMe2j_selected",     200, 0, 2000, 200, 0, 2000) ;
  CreateUserTH2D( "Me1jVsMe2j_rejected",     200, 0, 2000, 200, 0, 2000) ;


  CreateUserTH2D( "MeeVsST_PAS"                 ,     200, 0, 2000, 200, 0, 2000) ;
  CreateUserTH2D( "MeeVsST_PASandMee100"        ,     200, 0, 2000, 200, 0, 2000) ;


  CreateUserTH1D( "Mee_80_100_Preselection", 200, 60, 120 );
  CreateUserTH1D( "Mee_70_110_Preselection", 200, 60, 120 );
  CreateUserTH1D( "Mee_70_110_ST600_Preselection", 200, 60, 120 );

  CreateUserTH1D( "Mee_EBEB_PAS"		   ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "Mee_EBEE_PAS"		   ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "Mee_EEEE_PAS"		   ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "Mee_EB_PAS" 		   ,    60 , 60       , 120	 );
  CreateUserTH1D( "Mee_End2End2_PAS" 		   ,    60 , 60       , 120	 );

  CreateUserTH1D( "Mee_EBEB_80_100_PAS"	   ,    60 , 60       , 120	 );
  CreateUserTH1D( "Mee_EBEE_80_100_PAS"	   ,    60 , 60       , 120	 );
  CreateUserTH1D( "Mee_EEEE_80_100_PAS"	   ,    60 , 60       , 120	 );
  CreateUserTH1D( "Mee_EB_80_100_PAS" 	     	   ,    60 , 60       , 120	 );

  CreateUserTH1D( "Mee_EBEB_70_110_PAS"	   ,    60 , 60       , 120	 );
  CreateUserTH1D( "Mee_EBEE_70_110_PAS"	   ,    60 , 60       , 120	 );
  CreateUserTH1D( "Mee_EEEE_70_110_PAS"	   ,    60 , 60       , 120	 );
  CreateUserTH1D( "Mee_EB_70_110_PAS" 	     	   ,    60 , 60       , 120	 );

  CreateUserTH1D( "PileupWeight"   , 100, -10, 10 );
  CreateUserTH1D( "GeneratorWeight", 100, -2.0 , 2.0 );

  CreateUserTH1D("CorrIsolation_1stEle_PAS"                 , 200,-25.0 ,  25.0  ); CreateUserTH1D("CorrIsolation_2ndEle_PAS"                 , 200,-25.0 ,  25.0  );
  CreateUserTH1D("DeltaEtaTrkSC_1stEle_PAS"                 , 200, -0.01,   0.01 ); CreateUserTH1D("DeltaEtaTrkSC_2ndEle_PAS"                 , 200, -0.01,   0.01 );
  CreateUserTH1D("EcalIsolation_1stEle_PAS"                 , 200,  0.0 ,  20.0  ); CreateUserTH1D("EcalIsolation_2ndEle_PAS"                 , 200,  0.0 ,  20.0  );
  CreateUserTH1D("HcalIsolation_1stEle_PAS"                 , 200,  0.0 ,  20.0  ); CreateUserTH1D("HcalIsolation_2ndEle_PAS"                 , 200,  0.0 ,  20.0  );
  CreateUserTH1D("TrkIsolation_1stEle_PAS"                  , 200,  0.0,    5.0  ); CreateUserTH1D("TrkIsolation_2ndEle_PAS"                  , 200,  0.0,    5.0  );
  CreateUserTH1D("HasMatchedPhot_1stEle_PAS"                , 2,   -0.5 ,   1.5  ); CreateUserTH1D("HasMatchedPhot_2ndEle_PAS"                , 2,   -0.5 ,   1.5  );
  CreateUserTH1D("HoE_1stEle_PAS"                           , 200,  0.0 ,   0.05 ); CreateUserTH1D("HoE_2ndEle_PAS"                           , 200,  0.0 ,   0.05 );
  CreateUserTH1D("LeadVtxDistXY_1stEle_PAS"                 , 200, -0.05,   0.05 ); CreateUserTH1D("LeadVtxDistXY_2ndEle_PAS"                 , 200, -0.05,   0.05 );
  CreateUserTH1D("LeadVtxDistZ_1stEle_PAS"                  , 200, -0.2 ,   0.2  ); CreateUserTH1D("LeadVtxDistZ_2ndEle_PAS"                  , 200, -0.2 ,   0.2  );
  CreateUserTH1D("MissingHits_1stEle_PAS"                   , 2  , -0.5,    1.5  ); CreateUserTH1D("MissingHits_2ndEle_PAS"                   , 2  , -0.5,    1.5  );
  CreateUserTH1D("Full5x5SigmaIEtaIEta_Barrel_1stEle_PAS"   , 200,  0.0,    0.04 ); CreateUserTH1D("Full5x5SigmaIEtaIEta_Barrel_2ndEle_PAS"   , 200,  0.0,    0.04 );
  CreateUserTH1D("Full5x5SigmaIEtaIEta_Endcap_1stEle_PAS"   , 200,  0.0,    0.1  ); CreateUserTH1D("Full5x5SigmaIEtaIEta_Endcap_2ndEle_PAS"   , 200,  0.0,    0.1  );

  CreateUserTH1D("CorrIsolation_1stEle_PASandMee100"        , 200,-25.0 ,  25.0  ); CreateUserTH1D("CorrIsolation_2ndEle_PASandMee100"        , 200,-25.0 ,  25.0  );
  CreateUserTH1D("DeltaEtaTrkSC_1stEle_PASandMee100"        , 200, -0.01,   0.01 ); CreateUserTH1D("DeltaEtaTrkSC_2ndEle_PASandMee100"        , 200, -0.01,   0.01 );
  CreateUserTH1D("EcalIsolation_1stEle_PASandMee100"        , 200,  0.0 ,  20.0  ); CreateUserTH1D("EcalIsolation_2ndEle_PASandMee100"        , 200,  0.0 ,  20.0  );
  CreateUserTH1D("HcalIsolation_1stEle_PASandMee100"        , 200,  0.0 ,  20.0  ); CreateUserTH1D("HcalIsolation_2ndEle_PASandMee100"        , 200,  0.0 ,  20.0  );
  CreateUserTH1D("TrkIsolation_1stEle_PASandMee100"         , 200,  0.0,    5.0  ); CreateUserTH1D("TrkIsolation_2ndEle_PASandMee100"         , 200,  0.0,    5.0  );
  CreateUserTH1D("HasMatchedPhot_1stEle_PASandMee100"       , 2,   -0.5 ,   1.5  ); CreateUserTH1D("HasMatchedPhot_2ndEle_PASandMee100"       , 2,   -0.5 ,   1.5  );
  CreateUserTH1D("HoE_1stEle_PASandMee100"                  , 200,  0.0 ,   0.05 ); CreateUserTH1D("HoE_2ndEle_PASandMee100"                  , 200,  0.0 ,   0.05 );
  CreateUserTH1D("LeadVtxDistXY_1stEle_PASandMee100"        , 200, -0.05,   0.05 ); CreateUserTH1D("LeadVtxDistXY_2ndEle_PASandMee100"        , 200, -0.05,   0.05 );
  CreateUserTH1D("LeadVtxDistZ_1stEle_PASandMee100"         , 200, -0.2 ,   0.2  ); CreateUserTH1D("LeadVtxDistZ_2ndEle_PASandMee100"         , 200, -0.2 ,   0.2  );
  CreateUserTH1D("MissingHits_1stEle_PASandMee100"          , 2  , -0.5,    1.5  ); CreateUserTH1D("MissingHits_2ndEle_PASandMee100"          , 2  , -0.5,    1.5  );
  CreateUserTH1D("Full5x5SigmaIEtaIEta_Barrel_1stEle_PASandMee100" , 200,  0.0,    0.02 ); CreateUserTH1D("Full5x5SigmaIEtaIEta_Barrel_2ndEle_PASandMee100" , 200,  0.0,    0.02 );
  CreateUserTH1D("Full5x5SigmaIEtaIEta_Endcap_1stEle_PASandMee100" , 200,  0.0,    0.1  ); CreateUserTH1D("Full5x5SigmaIEtaIEta_Endcap_2ndEle_PASandMee100" , 200,  0.0,    0.1  );

  if(do_roi_plots) {
    CreateUserTH1D( "M_j1j3_ROI"            ,    200 , 0       , 2000	 );
    CreateUserTH1D( "M_j2j3_ROI"            ,    200 , 0       , 2000	 );
    CreateUserTH1D( "M_e1j3_ROI"            ,    200 , 0       , 2000	 );
    CreateUserTH1D( "M_e2j3_ROI"            ,    200 , 0       , 2000	 );
    CreateUserTH1D( "M_eejjj_ROI"           ,    500 , 0       , 5000	 );
    CreateUserTH1D( "sTfrac_Jet1_ROI"       ,   100  ,  0.0    , 1.0      );
    CreateUserTH1D( "sTfrac_Jet2_ROI"       ,   100  ,  0.0    , 1.0      );
    CreateUserTH1D( "sTfrac_Ele1_ROI"       ,   100  ,  0.0    , 1.0      );
    CreateUserTH1D( "sTfrac_Ele2_ROI"       ,   100  ,  0.0    , 1.0      );
    CreateUserTH1D( "sTfrac_Jet_ROI"        ,   100  ,  0.0    , 1.0      );
    CreateUserTH1D( "sTfrac_Ele_ROI"        ,   100  ,  0.0    , 1.0      );
    CreateUserTH1D( "nJet_ROI"              ,    10  , -0.5    , 9.5      );
    CreateUserTH1D( "Pt1stEle_ROI"	   , 	100 , 0       , 1000     );
    CreateUserTH1D( "Pt2ndEle_ROI"	   , 	300 , 0       , 3000     );
    CreateUserTH1D( "EleChargeSum_ROI"         ,    3   , -2.5    , 2.5  );
    CreateUserTH1D( "MET_ROI"               ,    200 , 0       , 1000	 );
    CreateUserTH1D( "Pt1stJet_ROI"          ,    200 , 0       , 2000	 );
    CreateUserTH1D( "Pt2ndJet_ROI"          ,    200 , 0       , 2000	 );
    CreateUserTH1D( "sTlep_ROI"             ,    200 , 0       , 2000	 );
    CreateUserTH1D( "sTjet_ROI"             ,    200 , 0       , 2000	 );
    CreateUserTH1D( "sT_zjj_ROI"                      ,    200   , 0       , 2000	  );
    CreateUserTH1D( "sT_ROI"                ,    200 , 0       , 2000	 );
    CreateUserTH1D( "Mjj_ROI"		   ,    200 , 0       , 2000	 );
    CreateUserTH1D( "Mee_ROI"		   ,    200 , 0       , 2000	 );
    CreateUserTH1D( "Me1j1_ROI"             ,    200 , 0       , 2000	 );
    CreateUserTH1D( "Mej_selected_avg_ROI"  ,    200 , 0       , 2000     );
    CreateUserTH1D( "Meejj_ROI"             ,    400 , 0       , 4000     );
    CreateUserTH1D( "Mejj_ROI"              ,    400 , 0       , 4000     );
    CreateUserTH1D( "Meej_ROI"              ,    400 , 0       , 4000     );
    CreateUserTH1D( "Eta1stJet_ROI"                   ,    100   , -5      , 5	  );
    CreateUserTH1D( "Eta2ndJet_ROI"                   ,    100   , -5      , 5	  );
    CreateUserTH1D( "Eta1stEle_ROI"	             , 	100    , -5      , 5	  );
    CreateUserTH1D( "Eta2ndEle_ROI"	             , 	100    , -5      , 5	  );

    CreateUserTH1D( "Phi1stJet_ROI"	             , 	 60    , -3.1416 , +3.1416  );
    CreateUserTH1D( "Phi2ndJet_ROI"	             , 	 60    , -3.1416 , +3.1416  );
    CreateUserTH1D( "Phi1stEle_ROI"	             , 	 60    , -3.1416 , +3.1416  );
    CreateUserTH1D( "Phi2ndEle_ROI"	             , 	 60    , -3.1416 , +3.1416  );
    CreateUserTH1D( "Ptj1j2j3_ROI"                    ,    200 , 0       , 2000     );
    CreateUserTH1D( "Ptj1j2_ROI"                      ,    200 , 0       , 2000     );
    CreateUserTH1D( "Ptj2j3_ROI"                      ,    200 , 0       , 2000     );
    CreateUserTH1D( "Ptj1j3_ROI"                      ,    200 , 0       , 2000     );
    CreateUserTH1D( "Ptee_Minus_Ptj1j2_ROI"           ,    200 , -500    , 500      );
    CreateUserTH1D( "Ptee_Minus_Ptj1j2j3_ROI"         ,    200 , -500    , 500      );
    CreateUserTH1D( "Ptee_ROI"              ,    200 , 0       , 2000     );
    CreateUserTH1D( "nVertex_ROI"                     ,    101   , -0.5   , 100.5	 ) ;
    CreateUserTH1D( "minDR_ZJet_ROI"        ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
    CreateUserTH1D( "DR_ZJet1_ROI"        ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
    CreateUserTH2D( "MeeVsST_ROI"                 ,     200, 0, 2000, 200, 0, 2000) ;
    CreateUserTH1D( "DR_ZJet2_ROI"        ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
    CreateUserTH1D("CorrIsolation_1stEle_ROI"                 , 200,-25.0 ,  25.0  ); CreateUserTH1D("CorrIsolation_2ndEle_ROI"                 , 200,-25.0 ,  25.0  );
    CreateUserTH1D("DeltaEtaTrkSC_1stEle_ROI"                 , 200, -0.01,   0.01 ); CreateUserTH1D("DeltaEtaTrkSC_2ndEle_ROI"                 , 200, -0.01,   0.01 );
    CreateUserTH1D("E1x5OverE5x5_1stEle_ROI"                  , 200,  0.0 ,   2.0  ); CreateUserTH1D("E1x5OverE5x5_2ndEle_ROI"                  , 200,  0.0 ,   2.0  );
    CreateUserTH1D("E2x5OverE5x5_1stEle_ROI"                  , 200,  0.0 ,   2.0  ); CreateUserTH1D("E2x5OverE5x5_2ndEle_ROI"                  , 200,  0.0 ,   2.0  );
    CreateUserTH1D("EcalIsolation_1stEle_ROI"                 , 200,  0.0 ,  20.0  ); CreateUserTH1D("EcalIsolation_2ndEle_ROI"                 , 200,  0.0 ,  20.0  );
    CreateUserTH1D("HcalIsolation_1stEle_ROI"                 , 200,  0.0 ,  20.0  ); CreateUserTH1D("HcalIsolation_2ndEle_ROI"                 , 200,  0.0 ,  20.0  );
    CreateUserTH1D("TrkIsolation_1stEle_ROI"                  , 200,  0.0,    5.0  ); CreateUserTH1D("TrkIsolation_2ndEle_ROI"                  , 200,  0.0,    5.0  );
    CreateUserTH1D("HasMatchedPhot_1stEle_ROI"                , 2,   -0.5 ,   1.5  ); CreateUserTH1D("HasMatchedPhot_2ndEle_ROI"                , 2,   -0.5 ,   1.5  );
    CreateUserTH1D("HoE_1stEle_ROI"                           , 200,  0.0 ,   0.05 ); CreateUserTH1D("HoE_2ndEle_ROI"                           , 200,  0.0 ,   0.05 );
    CreateUserTH1D("LeadVtxDistXY_1stEle_ROI"                 , 200, -0.05,   0.05 ); CreateUserTH1D("LeadVtxDistXY_2ndEle_ROI"                 , 200, -0.05,   0.05 );
    CreateUserTH1D("LeadVtxDistZ_1stEle_ROI"                  , 200, -0.2 ,   0.2  ); CreateUserTH1D("LeadVtxDistZ_2ndEle_ROI"                  , 200, -0.2 ,   0.2  );
    CreateUserTH1D("MissingHits_1stEle_ROI"                   , 2  , -0.5,    1.5  ); CreateUserTH1D("MissingHits_2ndEle_ROI"                   , 2  , -0.5,    1.5  );
    CreateUserTH1D("SigmaIEtaIEta_Barrel_1stEle_ROI"          , 200,  0.0,    0.02 ); CreateUserTH1D("SigmaIEtaIEta_Barrel_2ndEle_ROI"          , 200,  0.0,    0.02 );
    CreateUserTH1D("SigmaIEtaIEta_Endcap_1stEle_ROI"          , 200,  0.0,    0.1  ); CreateUserTH1D("SigmaIEtaIEta_Endcap_2ndEle_ROI"          , 200,  0.0,    0.1  );
  }

  // for scale factor dependence studies
  CreateUserTH1D( "Mee_NJetEq2_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetEq3_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetEq4_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetEq5_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetEq6_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetEq7_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetGeq3_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetGeq4_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_sT300To500_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_sT500To750_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_sT750To1250_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_sT1250ToInf_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_MejMin100To200_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_MejMin200To300_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_MejMin300To400_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_MejMin400To500_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_MejMin500To650_PAS"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_MejMin650ToInf_PAS"		             ,    200   , 0       , 2000	  );
   // with zero B-tags
   CreateUserTH1D( "Mee_PAS_noBtaggedJets"		       ,    2000 , 0       , 2000	 );
   CreateUserTH1D( "Mee_EBEB_PAS_noBtaggedJets"		   ,    2000 , 0       , 2000	 );
   CreateUserTH1D( "Mee_EBEE_PAS_noBtaggedJets"		   ,    2000 , 0       , 2000	 );
   CreateUserTH1D( "Mee_EEEE_PAS_noBtaggedJets"		   ,    2000 , 0       , 2000	 );
   CreateUserTH1D( "Mee_sT300To500_PAS_noBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_sT500To750_PAS_noBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_sT750To1250_PAS_noBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_sT1250ToInf_PAS_noBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin100To200_PAS_noBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin200To300_PAS_noBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin300To400_PAS_noBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin400To500_PAS_noBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin500To650_PAS_noBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin650ToInf_PAS_noBtaggedJets"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "nElectron_noBtaggedJets"         ,    5   , -0.5    , 4.5      );
  CreateUserTH1D( "nMuon_noBtaggedJets"             ,    5   , -0.5    , 4.5      );
  CreateUserTH1D( "nJet_noBtaggedJets"              ,    10  , -0.5    , 9.5      );
  CreateUserTH1D( "Pt1stEle_noBtaggedJets"	   , 	100 , 0       , 1000     );
  CreateUserTH1D( "Eta1stEle_noBtaggedJets"	   , 	100 , -5      , 5	 );
  CreateUserTH1D( "Phi1stEle_noBtaggedJets"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Pt2ndEle_noBtaggedJets"	   , 	300 , 0       , 3000     );
  CreateUserTH1D( "Eta2ndEle_noBtaggedJets"	   , 	100 , -5      , 5	 );
  CreateUserTH1D( "Phi2ndEle_noBtaggedJets"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Charge1stEle_noBtaggedJets"	   , 	2   , -1.0001 , 1.0001	 );
  CreateUserTH1D( "Charge2ndEle_noBtaggedJets"	   , 	2   , -1.0001 , 1.0001	 );
  CreateUserTH1D( "MET_noBtaggedJets"               ,    200 , 0       , 1000	 );
  CreateUserTH1D( "METPhi_noBtaggedJets"		   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Pt1stJet_noBtaggedJets"          ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Pt2ndJet_noBtaggedJets"          ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Eta1stJet_noBtaggedJets"         ,    100 , -5      , 5	 );
  CreateUserTH1D( "Eta2ndJet_noBtaggedJets"         ,    100 , -5      , 5	 );
  CreateUserTH1D( "Phi1stJet_noBtaggedJets"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Phi2ndJet_noBtaggedJets"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "sTlep_noBtaggedJets"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sTjet_noBtaggedJets"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_noBtaggedJets"                ,    300   , 0       , 3000	 );
  CreateUserTH1D( "sT_zjj_noBtaggedJets"            ,    300   , 0       , 3000	  );
  CreateUserTH1D( "Mjj_noBtaggedJets"		   ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Mee_noBtaggedJets"		   ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "MTenu_noBtaggedJets"             ,    200 , 0       , 1000	 );
  CreateUserTH1D( "Me1j1_noBtaggedJets"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me1j2_noBtaggedJets"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me2j1_noBtaggedJets"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me2j2_noBtaggedJets"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Mej_selected_min_noBtaggedJets"  ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_selected_max_noBtaggedJets"  ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_minmax_noBtaggedJets"        ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_selected_avg_noBtaggedJets"  ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mejj_noBtaggedJets"              ,    400 , 0       , 4000     );
  CreateUserTH1D( "Meej_noBtaggedJets"              ,    400 , 0       , 4000     );
  CreateUserTH1D( "Meejj_noBtaggedJets"             ,    400 , 0       , 4000     );
   // with >= 1 B-tags
   CreateUserTH1D( "Mee_PAS_gteOneBtaggedJet"		       ,    2000 , 0       , 2000	 );
   CreateUserTH1D( "Mee_EBEB_PAS_gteOneBtaggedJet"		   ,    2000 , 0       , 2000	 );
   CreateUserTH1D( "Mee_EBEE_PAS_gteOneBtaggedJet"		   ,    2000 , 0       , 2000	 );
   CreateUserTH1D( "Mee_EEEE_PAS_gteOneBtaggedJet"		   ,    2000 , 0       , 2000	 );
   CreateUserTH1D( "Mee_sT300To500_PAS_gteOneBtaggedJet"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_sT500To750_PAS_gteOneBtaggedJet"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_sT750To1250_PAS_gteOneBtaggedJet"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_sT1250ToInf_PAS_gteOneBtaggedJet"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin100To200_PAS_gteOneBtaggedJet"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin200To300_PAS_gteOneBtaggedJet"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin300To400_PAS_gteOneBtaggedJet"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin400To500_PAS_gteOneBtaggedJet"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin500To650_PAS_gteOneBtaggedJet"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin650ToInf_PAS_gteOneBtaggedJet"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "nElectron_gteOneBtaggedJet"         ,    5   , -0.5    , 4.5      );
  CreateUserTH1D( "nMuon_gteOneBtaggedJet"             ,    5   , -0.5    , 4.5      );
  CreateUserTH1D( "nJet_gteOneBtaggedJet"              ,    10  , -0.5    , 9.5      );
  CreateUserTH1D( "Pt1stEle_gteOneBtaggedJet"	   , 	100 , 0       , 1000     );
  CreateUserTH1D( "Eta1stEle_gteOneBtaggedJet"	   , 	100 , -5      , 5	 );
  CreateUserTH1D( "Phi1stEle_gteOneBtaggedJet"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Pt2ndEle_gteOneBtaggedJet"	   , 	300 , 0       , 3000     );
  CreateUserTH1D( "Eta2ndEle_gteOneBtaggedJet"	   , 	100 , -5      , 5	 );
  CreateUserTH1D( "Phi2ndEle_gteOneBtaggedJet"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Charge1stEle_gteOneBtaggedJet"	   , 	2   , -1.0001 , 1.0001	 );
  CreateUserTH1D( "Charge2ndEle_gteOneBtaggedJet"	   , 	2   , -1.0001 , 1.0001	 );
  CreateUserTH1D( "MET_gteOneBtaggedJet"               ,    200 , 0       , 1000	 );
  CreateUserTH1D( "METPhi_gteOneBtaggedJet"		   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Pt1stJet_gteOneBtaggedJet"          ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Pt2ndJet_gteOneBtaggedJet"          ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Eta1stJet_gteOneBtaggedJet"         ,    100 , -5      , 5	 );
  CreateUserTH1D( "Eta2ndJet_gteOneBtaggedJet"         ,    100 , -5      , 5	 );
  CreateUserTH1D( "Phi1stJet_gteOneBtaggedJet"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Phi2ndJet_gteOneBtaggedJet"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "sTlep_gteOneBtaggedJet"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sTjet_gteOneBtaggedJet"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_gteOneBtaggedJet"                ,    300   , 0       , 3000	 );
  CreateUserTH1D( "sT_zjj_gteOneBtaggedJet"            ,    300   , 0       , 3000	  );
  CreateUserTH1D( "Mjj_gteOneBtaggedJet"		   ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Mee_gteOneBtaggedJet"		   ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "MTenu_gteOneBtaggedJet"             ,    200 , 0       , 1000	 );
  CreateUserTH1D( "Me1j1_gteOneBtaggedJet"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me1j2_gteOneBtaggedJet"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me2j1_gteOneBtaggedJet"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me2j2_gteOneBtaggedJet"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Mej_selected_min_gteOneBtaggedJet"  ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_selected_max_gteOneBtaggedJet"  ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_minmax_gteOneBtaggedJet"        ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_selected_avg_gteOneBtaggedJet"  ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mejj_gteOneBtaggedJet"              ,    400 , 0       , 4000     );
  CreateUserTH1D( "Meej_gteOneBtaggedJet"              ,    400 , 0       , 4000     );
  CreateUserTH1D( "Meejj_gteOneBtaggedJet"             ,    400 , 0       , 4000     );
   // with >= 2 B-tags
   CreateUserTH1D( "Mee_PAS_gteTwoBtaggedJets"		       ,    2000 , 0       , 2000	 );
   CreateUserTH1D( "Mee_EBEB_PAS_gteTwoBtaggedJets"		   ,    2000 , 0       , 2000	 );
   CreateUserTH1D( "Mee_EBEE_PAS_gteTwoBtaggedJets"		   ,    2000 , 0       , 2000	 );
   CreateUserTH1D( "Mee_EEEE_PAS_gteTwoBtaggedJets"		   ,    2000 , 0       , 2000	 );
   CreateUserTH1D( "Mee_sT300To500_PAS_gteTwoBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_sT500To750_PAS_gteTwoBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_sT750To1250_PAS_gteTwoBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_sT1250ToInf_PAS_gteTwoBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin100To200_PAS_gteTwoBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin200To300_PAS_gteTwoBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin300To400_PAS_gteTwoBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin400To500_PAS_gteTwoBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin500To650_PAS_gteTwoBtaggedJets"		             ,    200   , 0       , 2000	  );
   CreateUserTH1D( "Mee_MejMin650ToInf_PAS_gteTwoBtaggedJets"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "nElectron_gteTwoBtaggedJets"         ,    5   , -0.5    , 4.5      );
  CreateUserTH1D( "nMuon_gteTwoBtaggedJets"             ,    5   , -0.5    , 4.5      );
  CreateUserTH1D( "nJet_gteTwoBtaggedJets"              ,    10  , -0.5    , 9.5      );
  CreateUserTH1D( "Pt1stEle_gteTwoBtaggedJets"	   , 	100 , 0       , 1000     );
  CreateUserTH1D( "Eta1stEle_gteTwoBtaggedJets"	   , 	100 , -5      , 5	 );
  CreateUserTH1D( "Phi1stEle_gteTwoBtaggedJets"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Pt2ndEle_gteTwoBtaggedJets"	   , 	300 , 0       , 3000     );
  CreateUserTH1D( "Eta2ndEle_gteTwoBtaggedJets"	   , 	100 , -5      , 5	 );
  CreateUserTH1D( "Phi2ndEle_gteTwoBtaggedJets"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Charge1stEle_gteTwoBtaggedJets"	   , 	2   , -1.0001 , 1.0001	 );
  CreateUserTH1D( "Charge2ndEle_gteTwoBtaggedJets"	   , 	2   , -1.0001 , 1.0001	 );
  CreateUserTH1D( "MET_gteTwoBtaggedJets"               ,    200 , 0       , 1000	 );
  CreateUserTH1D( "METPhi_gteTwoBtaggedJets"		   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Pt1stJet_gteTwoBtaggedJets"          ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Pt2ndJet_gteTwoBtaggedJets"          ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Eta1stJet_gteTwoBtaggedJets"         ,    100 , -5      , 5	 );
  CreateUserTH1D( "Eta2ndJet_gteTwoBtaggedJets"         ,    100 , -5      , 5	 );
  CreateUserTH1D( "Phi1stJet_gteTwoBtaggedJets"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "Phi2ndJet_gteTwoBtaggedJets"	   , 	60  , -3.1416 , +3.1416	 );
  CreateUserTH1D( "sTlep_gteTwoBtaggedJets"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sTjet_gteTwoBtaggedJets"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "sT_gteTwoBtaggedJets"                ,    300   , 0       , 3000	 );
  CreateUserTH1D( "sT_zjj_gteTwoBtaggedJets"            ,    300   , 0       , 3000	  );
  CreateUserTH1D( "Mjj_gteTwoBtaggedJets"		   ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Mee_gteTwoBtaggedJets"		   ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "MTenu_gteTwoBtaggedJets"             ,    200 , 0       , 1000	 );
  CreateUserTH1D( "Me1j1_gteTwoBtaggedJets"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me1j2_gteTwoBtaggedJets"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me2j1_gteTwoBtaggedJets"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Me2j2_gteTwoBtaggedJets"             ,    200 , 0       , 2000	 );
  CreateUserTH1D( "Mej_selected_min_gteTwoBtaggedJets"  ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_selected_max_gteTwoBtaggedJets"  ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_minmax_gteTwoBtaggedJets"        ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mej_selected_avg_gteTwoBtaggedJets"  ,    200 , 0       , 2000     );
  CreateUserTH1D( "Mejj_gteTwoBtaggedJets"              ,    400 , 0       , 4000     );
  CreateUserTH1D( "Meej_gteTwoBtaggedJets"              ,    400 , 0       , 4000     );
  CreateUserTH1D( "Meejj_gteTwoBtaggedJets"             ,    400 , 0       , 4000     );

  // bkg control region plots
  CreateUserTH1D( "Mee_BkgControlRegion"		            ,    2000   , 0       , 2000	  );
  CreateUserTH1D( "Mee_BkgControlRegion_gteOneBtaggedJet"		       ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "Mee_BkgControlRegion_gteTwoBtaggedJets"		       ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "Mee_EB_BkgControlRegion"		   ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "Mee_EBEB_BkgControlRegion"		   ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "Mee_EBEE_BkgControlRegion"		   ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "Mee_EEEE_BkgControlRegion"		   ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "Mee_End2End2_BkgControlRegion"		   ,    2000 , 0       , 2000	 );
  CreateUserTH1D( "Mee_NJetEq2_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetEq3_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetEq4_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetEq5_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetEq6_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetEq7_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetGeq3_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_NJetGeq4_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_sT300To500_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_sT500To750_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_sT750To1250_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_sT1250ToInf_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_MejMin100To200_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_MejMin200To300_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_MejMin300To400_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_MejMin400To500_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_MejMin500To650_BkgControlRegion"		             ,    200   , 0       , 2000	  );
  CreateUserTH1D( "Mee_MejMin650ToInf_BkgControlRegion"		             ,    200   , 0       , 2000	  );

  // 3D opt cut space
  CreateUserTH3D( "OptimizationCutSpace", 200, 0, 2000, 200, 0, 2000, 200, 0, 2000);


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

  for (int i_lq_mass = 0; i_lq_mass < n_lq_mass ; ++i_lq_mass ) {
    int lq_mass = LQ_MASS[i_lq_mass];
    sprintf(plot_name, "Mej_selected_avg_LQ%d"       , lq_mass ); CreateUserTH1D ( plot_name, 60  , 0 , 3000 );
    sprintf(plot_name, "Mej_selected_min_LQ%d"       , lq_mass ); CreateUserTH1D ( plot_name, 60  , 0 , 3000 );
    sprintf(plot_name, "Mej_selected_max_LQ%d"       , lq_mass ); CreateUserTH1D ( plot_name, 60  , 0 , 3000 );
    sprintf(plot_name, "Mej_minmax_LQ%d"             , lq_mass ); CreateUserTH1D ( plot_name, 60  , 0 , 3000 );
    sprintf(plot_name, "sT_eejj_LQ%d"                , lq_mass ); CreateUserTH1D ( plot_name, 30  , 0 , 3000 );
    sprintf(plot_name, "Mee_LQ%d"                    , lq_mass ); CreateUserTH1D ( plot_name, 40  , 0 , 2000 );
    sprintf(plot_name, "Mej_selected_min_vs_max_LQ%d", lq_mass ); CreateUserTH2D ( plot_name, 150  , 0 , 3000, 150  , 0 , 3000 );
    sprintf(plot_name, "DR_Ele1Jet1_LQ%d"            , lq_mass ); CreateUserTH1D ( plot_name,
        getHistoNBins("DR_Ele1Jet1"),
        getHistoMin  ("DR_Ele1Jet1"),
        getHistoMax  ("DR_Ele1Jet1"));

    sprintf(plot_name, "CorrIsolation_1stEle_LQ%d"        , lq_mass ); CreateUserTH1D( plot_name , 200,-25.0 ,  25.0  );
    sprintf(plot_name, "DeltaEtaTrkSC_1stEle_LQ%d"        , lq_mass ); CreateUserTH1D( plot_name , 200, -0.01,   0.01 );
    sprintf(plot_name, "EcalIsolation_1stEle_LQ%d"        , lq_mass ); CreateUserTH1D( plot_name , 200,  0.0 ,  20.0  );
    sprintf(plot_name, "HcalIsolation_1stEle_LQ%d"        , lq_mass ); CreateUserTH1D( plot_name , 200,  0.0 ,  20.0  );
    sprintf(plot_name, "TrkIsolation_1stEle_LQ%d"         , lq_mass ); CreateUserTH1D( plot_name , 200,  0.0,    5.0  );
    sprintf(plot_name, "HasMatchedPhot_1stEle_LQ%d"       , lq_mass ); CreateUserTH1D( plot_name , 2,   -0.5 ,   1.5  );
    sprintf(plot_name, "HoE_1stEle_LQ%d"                  , lq_mass ); CreateUserTH1D( plot_name , 200,  0.0 ,   0.05 );
    sprintf(plot_name, "LeadVtxDistXY_1stEle_LQ%d"        , lq_mass ); CreateUserTH1D( plot_name , 200, -0.05,   0.05 );
    sprintf(plot_name, "LeadVtxDistZ_1stEle_LQ%d"         , lq_mass ); CreateUserTH1D( plot_name , 200, -0.2 ,   0.2  );
    sprintf(plot_name, "MissingHits_1stEle_LQ%d"          , lq_mass ); CreateUserTH1D( plot_name , 2  , -0.5,    1.5  );
    sprintf(plot_name, "Full5x5SigmaIEtaIEta_Barrel_1stEle_LQ%d" , lq_mass ); CreateUserTH1D( plot_name , 200,  0.0,    0.02 );
    sprintf(plot_name, "Full5x5SigmaIEtaIEta_Endcap_1stEle_LQ%d" , lq_mass ); CreateUserTH1D( plot_name , 200,  0.0,    0.1  );

    sprintf(plot_name, "CorrIsolation_2ndEle_LQ%d"        , lq_mass ); CreateUserTH1D( plot_name , 200,-25.0 ,  25.0  );
    sprintf(plot_name, "DeltaEtaTrkSC_2ndEle_LQ%d"        , lq_mass ); CreateUserTH1D( plot_name , 200, -0.01,   0.01 );
    sprintf(plot_name, "EcalIsolation_2ndEle_LQ%d"        , lq_mass ); CreateUserTH1D( plot_name , 200,  0.0 ,  20.0  );
    sprintf(plot_name, "HcalIsolation_2ndEle_LQ%d"        , lq_mass ); CreateUserTH1D( plot_name , 200,  0.0 ,  20.0  );
    sprintf(plot_name, "TrkIsolation_2ndEle_LQ%d"         , lq_mass ); CreateUserTH1D( plot_name , 200,  0.0,    5.0  );
    sprintf(plot_name, "HasMatchedPhot_2ndEle_LQ%d"       , lq_mass ); CreateUserTH1D( plot_name , 2,   -0.5 ,   1.5  );
    sprintf(plot_name, "HoE_2ndEle_LQ%d"                  , lq_mass ); CreateUserTH1D( plot_name , 200,  0.0 ,   0.05 );
    sprintf(plot_name, "LeadVtxDistXY_2ndEle_LQ%d"        , lq_mass ); CreateUserTH1D( plot_name , 200, -0.05,   0.05 );
    sprintf(plot_name, "LeadVtxDistZ_2ndEle_LQ%d"         , lq_mass ); CreateUserTH1D( plot_name , 200, -0.2 ,   0.2  );
    sprintf(plot_name, "MissingHits_2ndEle_LQ%d"          , lq_mass ); CreateUserTH1D( plot_name , 2  , -0.5,    1.5  );
    sprintf(plot_name, "Full5x5SigmaIEtaIEta_Barrel_2ndEle_LQ%d" , lq_mass ); CreateUserTH1D( plot_name , 200,  0.0,    0.02 );
    sprintf(plot_name, "Full5x5SigmaIEtaIEta_Endcap_2ndEle_LQ%d" , lq_mass ); CreateUserTH1D( plot_name , 200,  0.0,    0.1  );

    sprintf(plot_name, "EleChargeSum_LQ%d"        , lq_mass ); CreateUserTH1D( plot_name ,      3 , -2.5    , 2.5      );
    sprintf(plot_name, "sTfrac_Jet1_LQ%d"         , lq_mass ); CreateUserTH1D( plot_name ,    100 ,  0.0    , 1.0      );
    sprintf(plot_name, "sTfrac_Jet2_LQ%d"         , lq_mass ); CreateUserTH1D( plot_name ,    100 ,  0.0    , 1.0      );
    sprintf(plot_name, "sTfrac_Ele1_LQ%d"         , lq_mass ); CreateUserTH1D( plot_name ,    100 ,  0.0    , 1.0      );
    sprintf(plot_name, "sTfrac_Ele2_LQ%d"         , lq_mass ); CreateUserTH1D( plot_name ,    100 ,  0.0    , 1.0      );
    sprintf(plot_name, "sTfrac_Jet_LQ%d"          , lq_mass ); CreateUserTH1D( plot_name ,    100 ,  0.0    , 1.0      );
    sprintf(plot_name, "sTfrac_Ele_LQ%d"          , lq_mass ); CreateUserTH1D( plot_name ,    100 ,  0.0    , 1.0      );
    sprintf(plot_name, "nJet_LQ%d"                , lq_mass ); CreateUserTH1D( plot_name ,     10 , -0.5    , 9.5      );
    sprintf(plot_name, "Pt1stEle_LQ%d"	           , lq_mass ); CreateUserTH1D( plot_name ,    100 ,  0.0    , 1000     );
    sprintf(plot_name, "Eta1stEle_LQ%d"           , lq_mass ); CreateUserTH1D( plot_name ,    100 , -5.0    , 5.0      );
    sprintf(plot_name, "Phi1stEle_LQ%d"           , lq_mass ); CreateUserTH1D( plot_name ,     60 , -3.1416 , +3.1416  );
    sprintf(plot_name, "Pt2ndEle_LQ%d"	           , lq_mass ); CreateUserTH1D( plot_name ,    100 ,  0.0    , 1000     );
    sprintf(plot_name, "Eta2ndEle_LQ%d"           , lq_mass ); CreateUserTH1D( plot_name ,    100 , -5.0    , 5.0      );
    sprintf(plot_name, "Phi2ndEle_LQ%d"           , lq_mass ); CreateUserTH1D( plot_name ,     60 , -3.1416 , 3.1416   );
    sprintf(plot_name, "MET_LQ%d"                 , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 1000     );
    sprintf(plot_name, "Pt1stJet_LQ%d"            , lq_mass ); CreateUserTH1D( plot_name ,    100 ,  0.0    , 1000     );
    sprintf(plot_name, "Pt2ndJet_LQ%d"            , lq_mass ); CreateUserTH1D( plot_name ,    100 ,  0.0    , 1000     );
    sprintf(plot_name, "Eta1stJet_LQ%d"           , lq_mass ); CreateUserTH1D( plot_name ,    100 , -5.0    , 5.0      );
    sprintf(plot_name, "Eta2ndJet_LQ%d"           , lq_mass ); CreateUserTH1D( plot_name ,    100 , -5.0    , 5.0      );
    sprintf(plot_name, "Phi1stJet_LQ%d"           , lq_mass ); CreateUserTH1D( plot_name ,     60 , -3.1416 , 3.1416   );
    sprintf(plot_name, "Phi2ndJet_LQ%d"           , lq_mass ); CreateUserTH1D( plot_name ,     60 , -3.1416 , 3.1416   );
    sprintf(plot_name, "sTlep_LQ%d"               , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "sTjet_LQ%d"               , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "sT_zjj_LQ%d"              , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "Mjj_LQ%d"		   , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "Meejj_LQ%d"               , lq_mass ); CreateUserTH1D( plot_name ,    400 ,  0.0    , 4000     );
    sprintf(plot_name, "Mejj_LQ%d"                , lq_mass ); CreateUserTH1D( plot_name ,    400 ,  0.0    , 4000     );
    sprintf(plot_name, "Meej_LQ%d"                , lq_mass ); CreateUserTH1D( plot_name ,    400 ,  0.0    , 4000     );
    sprintf(plot_name, "Ptj1j2j3_LQ%d"            , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "Ptj1j2_LQ%d"              , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "Ptj2j3_LQ%d"              , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "Ptj1j3_LQ%d"              , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "Ptee_Minus_Ptj1j2_LQ%d"   , lq_mass ); CreateUserTH1D( plot_name ,    200 , -500    ,  500     );
    sprintf(plot_name, "Ptee_Minus_Ptj1j2j3_LQ%d" , lq_mass ); CreateUserTH1D( plot_name ,    200 , -500    ,  500     );
    sprintf(plot_name, "Ptee_LQ%d"                , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "Me1j1_LQ%d"               , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "Me1j2_LQ%d"               , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "Me2j1_LQ%d"               , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "Me2j2_LQ%d"               , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "M_j1j3_LQ%d"              , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "M_j2j3_LQ%d"              , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "M_e1j3_LQ%d"              , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "M_e2j3_LQ%d"              , lq_mass ); CreateUserTH1D( plot_name ,    200 ,  0.0    , 2000     );
    sprintf(plot_name, "M_eejjj_LQ%d"             , lq_mass ); CreateUserTH1D( plot_name ,    500 ,  0.0    , 5000     );
    sprintf(plot_name, "nVertex_LQ%d"             , lq_mass ); CreateUserTH1D( plot_name ,    101 , -0.5    ,  100.5   );
    sprintf(plot_name, "MeeVsST_LQ%d"             , lq_mass ); CreateUserTH2D( plot_name ,    200 ,  0.0, 2000, 200, 0, 2000) ;
    sprintf(plot_name, "minDR_ZJet_LQ%d"          , lq_mass ); CreateUserTH1D( plot_name ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
    sprintf(plot_name, "DR_ZJet1_LQ%d"            , lq_mass ); CreateUserTH1D( plot_name ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
    sprintf(plot_name, "DR_ZJet2_LQ%d"            , lq_mass ); CreateUserTH1D( plot_name ,    getHistoNBins("DR_Jet1Jet2"), getHistoMin("DR_Jet1Jet2"), getHistoMax("DR_Jet1Jet2")     ) ;
    // muon kinematics
    sprintf(plot_name, "Pt1stMuon_LQ%d"	           , lq_mass ); CreateUserTH1D( plot_name ,    100 ,  0.0    , 1000     );
    sprintf(plot_name, "Eta1stMuon_LQ%d"           , lq_mass ); CreateUserTH1D( plot_name ,    100 , -5.0    , 5.0      );
    sprintf(plot_name, "Phi1stMuon_LQ%d"           , lq_mass ); CreateUserTH1D( plot_name ,     60 , -3.1416 , +3.1416  );
    sprintf(plot_name, "Pt2ndMuon_LQ%d"	           , lq_mass ); CreateUserTH1D( plot_name ,    100 ,  0.0    , 1000     );
    sprintf(plot_name, "Eta2ndMuon_LQ%d"           , lq_mass ); CreateUserTH1D( plot_name ,    100 , -5.0    , 5.0      );
    sprintf(plot_name, "Phi2ndMuon_LQ%d"           , lq_mass ); CreateUserTH1D( plot_name ,     60 , -3.1416 , 3.1416   );

  }
  // for SF at final selections
  CreateUserTH1D( "Mee_70_110_LQ300", 200, 60, 120 );
  CreateUserTH1D( "Mee_70_110_LQ600", 200, 60, 120 );
  CreateUserTH1D( "Mee_70_110_LQ800", 200, 60, 120 );
  CreateUserTH1D( "Mee_70_110_LQ900", 200, 60, 120 );
  CreateUserTH1D( "Mee_70_110_LQ1000", 200, 60, 120 );


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

    //--------------------------------------------------------------------------
    // Tricky part: refine Weight branch for data only
    //--------------------------------------------------------------------------
    float weight = 1.0;
    if(isData())
      resetSkimTreeBranchAddress("Weight", &weight);

    //------------------------------------------------------------------
    // Print progress
    //------------------------------------------------------------------
    if(jentry < 10 || jentry%5000 == 0) std::cout << "analysisClass::Loop(): jentry = " << jentry << "/" << nentries << std::endl;
    unsigned int run = readerTools_->ReadValueBranch<UInt_t>("run");
    if(run==319077 || run==319310) continue;
    //if(run>300000) continue;
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
    if(analysisYearInt < 2018 && hasBranch("PrefireWeight") && !isData())
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
    //if(analysisYearInt==2016) {
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
      gen_weight*=recoSFEle1*recoSFEle2*heepSFEle1*heepSFEle2;
    }

    // run ls event
  //  unsigned int run = readerTools_->ReadValueBranch<UInt_t>("run");
    unsigned int ls = readerTools_->ReadValueBranch<UInt_t>("ls");
    unsigned long long int event = readerTools_->ReadValueBranch<ULong64_t>("event");
    //--------------------------------------------------------------------------
    // Find the right prescale for this event
    //--------------------------------------------------------------------------

    double min_prescale = 1;
    bool passTrigger = false;

    float hltPhoton1Pt = readerTools_->ReadValueBranch<Float_t>("Ele1_MatchedHLTriggerObjectPt");
    float hltPhoton2Pt = readerTools_->ReadValueBranch<Float_t>("Ele2_MatchedHLTriggerObjectPt");
    float hltPhotonPt = hltPhoton1Pt > hltPhoton2Pt ? hltPhoton1Pt : hltPhoton2Pt;

    std::string triggerName = "";

    if ( hltPhotonPt > 0.0 ) {
      if(analysisYearInt==2016) {
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon22")   > 0.1 && hltPhotonPt >= 22.  && hltPhotonPt < 30. ) { passTrigger = true; triggerName = "Photon22"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon30")   > 0.1 && hltPhotonPt >= 30.  && hltPhotonPt < 36. ) { passTrigger = true; triggerName = "Photon30"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon36")   > 0.1 && hltPhotonPt >= 36.  && hltPhotonPt < 50. ) { passTrigger = true; triggerName = "Photon36"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon50")   > 0.1 && hltPhotonPt >= 50.  && hltPhotonPt < 75. ) { passTrigger = true; triggerName = "Photon50"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon75")   > 0.1 && hltPhotonPt >= 75.  && hltPhotonPt < 90. ) { passTrigger = true; triggerName = "Photon75"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon90")   > 0.1 && hltPhotonPt >= 90.  && hltPhotonPt < 120.) { passTrigger = true; triggerName = "Photon90"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon120")  > 0.1 && hltPhotonPt >= 120. && hltPhotonPt < 175.) { passTrigger = true; triggerName = "Photon120"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon175")  > 0.1 && hltPhotonPt >= 175.) { passTrigger = true; triggerName = "Photon175"; }
      }
      else if(analysisYearInt==2017) {
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon25")   > 0.1 && hltPhotonPt >= 25.  && hltPhotonPt < 33. ) { passTrigger = true; triggerName = "Photon25"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon33")   > 0.1 && hltPhotonPt >= 33.  && hltPhotonPt < 50. ) { passTrigger = true; triggerName = "Photon33"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon50")   > 0.1 && hltPhotonPt >= 50.  && hltPhotonPt < 75. ) { passTrigger = true; triggerName = "Photon50"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon75")   > 0.1 && hltPhotonPt >= 75.  && hltPhotonPt < 90. ) { passTrigger = true; triggerName = "Photon75"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon90")   > 0.1 && hltPhotonPt >= 90.  && hltPhotonPt < 120.) { passTrigger = true; triggerName = "Photon90"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon120")  > 0.1 && hltPhotonPt >= 120. && hltPhotonPt < 150.) { passTrigger = true; triggerName = "Photon120"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon150")  > 0.1 && hltPhotonPt >= 150. && hltPhotonPt < 175.) { passTrigger = true; triggerName = "Photon150"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon175")  > 0.1 && hltPhotonPt >= 175. && hltPhotonPt < 200.) { passTrigger = true; triggerName = "Photon175"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon200")  > 0.1 && hltPhotonPt >= 200.) { passTrigger = true; triggerName = "Photon200"; }
      }
      else if(analysisYearInt==2018) {
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon33")   > 0.1 && hltPhotonPt >= 33.  && hltPhotonPt < 50. ) { passTrigger = true; triggerName = "Photon33"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon50")   > 0.1 && hltPhotonPt >= 50.  && hltPhotonPt < 75. ) { passTrigger = true; triggerName = "Photon50"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon75")   > 0.1 && hltPhotonPt >= 75.  && hltPhotonPt < 90. ) { passTrigger = true; triggerName = "Photon75"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon90")   > 0.1 && hltPhotonPt >= 90.  && hltPhotonPt < 120.) { passTrigger = true; triggerName = "Photon90"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon120")  > 0.1 && hltPhotonPt >= 120. && hltPhotonPt < 150.) { passTrigger = true; triggerName = "Photon120"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon150")  > 0.1 && hltPhotonPt >= 150. && hltPhotonPt < 175.) { passTrigger = true; triggerName = "Photon150"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon175")  > 0.1 && hltPhotonPt >= 175. && hltPhotonPt < 200.) { passTrigger = true; triggerName = "Photon175"; }
        if ( readerTools_->ReadValueBranch<Float_t>("H_Photon200")  > 0.1 && hltPhotonPt >= 200.) { passTrigger = true; triggerName = "Photon200"; }
      }
    }
    if(isData() && passTrigger) {
      //min_prescale = run2PhotonTriggerPrescales.LookupPrescale(analysisYear,triggerName);
      int hltPrescale = psProv.hltPrescale("HLT_"+triggerName+"_v", run, ls);
      int l1Prescale = 1;
      std::string l1Seed = "";
      if(triggerName == "Photon22") {
        l1Seed = "L1_SingleEG18";
        l1Prescale = psProv.l1Prescale(l1Seed, run, ls);
      }
      else if(triggerName == "Photon25" || triggerName == "Photon30" || triggerName == "Photon36") {
        l1Seed = "L1_SingleEG26";
        l1Prescale = psProv.l1Prescale(l1Seed, run, ls);
      }
      else if(triggerName == "Photon33") {
        l1Seed = "L1_SingleEG26er2p5";
        l1Prescale = psProv.l1Prescale(l1Seed, run, ls);
      }
      else if(triggerName == "Photon50" || triggerName == "Photon75" || triggerName == "Photon90" || triggerName == "Photon120" ||
          triggerName == "Photon150" || (analysisYearInt > 2016 && triggerName == "Photon175") ) {
        //int eg34Prescale = psProv.l1Prescale("L1_SingleEG34", run, ls);
        l1Seed = "L1_SingleEG40";
        if(analysisYearInt == 2018)
          l1Seed = "SingleEG42er2p5";
        l1Prescale = psProv.l1Prescale(l1Seed, run, ls);
      }
      else if(analysisYearInt == 2016 && triggerName == "Photon175") {
        l1Prescale = 1;
        hltPrescale = 1;
      }
      if(l1Prescale <= 0 || hltPrescale <= 0)
        std::cout << "INFO: " << triggerName << ": l1 seed = " << l1Seed << " has prescale = " << l1Prescale << "; hlt prescale = " << hltPrescale <<
          "; run = " << run << " ls = " << ls << "; psColumn = " << psProv.getRunInfo(run)->psColumn(ls) << "; l1 menu=" << psProv.getRunInfo(run)->l1Menu() <<
          "; hlt menu=" << psProv.getRunInfo(run)->hltMenu() << "; trig mode=" << psProv.getRunInfo(run)->triggerMode() << std::endl;
      //assert(l1Prescale > 0);
      //assert(hltPrescale > 0);
      min_prescale = l1Prescale * hltPrescale;
      //if(hltPhotonPt < 100)
      //  std::cout << "INFO: found prescale " << min_prescale << " for trigger name " << triggerName << " with hltPhotonPt = " << hltPhotonPt << ", for year: " << analysisYear << std::endl;
      if(min_prescale <= 0)
        passTrigger = false;
    }
    //else {
    //  std::vector<std::string> triggerNames {"H_Photon22", "H_Photon30", "H_Photon36", "H_Photon50", "H_Photon75", "H_Photon90", "H_Photon120", "H_Photon175"};
    //  std::cout << "Photon with highest hltPt = " << hltPhotonPt << " did not pass any of the single photon triggers. run: " << run << " ls: " << ls << " event: " << event << std::endl;
    //  for(const auto& trigName : triggerNames)
    //    std::cout << "\t" << trigName << " --> " << readerTools_->ReadValueBranch<Float_t>(trigName) << std::endl;
    //
    //}
    ///XXX SIC TEST FIXME to remove trigger and prescale requirements
    //passTrigger=1;
    //if ( H_Photon22   > 0.1 ) { passTrigger = 1; min_prescale = H_Photon22  ; }
    //if ( H_Photon30   > 0.1 ) { passTrigger = 1; min_prescale = H_Photon30  ; }
    //if ( H_Photon36   > 0.1 ) { passTrigger = 1; min_prescale = H_Photon36  ; }
    //if ( H_Photon50   > 0.1 ) { passTrigger = 1; min_prescale = H_Photon50  ; }
    //if ( H_Photon75   > 0.1 ) { passTrigger = 1; min_prescale = H_Photon75  ; }
    //if ( H_Photon90   > 0.1 ) { passTrigger = 1; min_prescale = H_Photon90  ; }
    //if ( H_Photon120  > 0.1 ) { passTrigger = 1; min_prescale = H_Photon120 ; }
    //if ( H_Photon175  > 0.1 ) { passTrigger = 1; min_prescale = H_Photon175 ; }
    //min_prescale=1.0;

    //// test output
    //std::cout << "Ele1_hltPhotonPt: " << Ele1_hltPhotonPt << std::endl;
    //std::cout << "Ele2_hltPhotonPt: " << readerTools_->ReadValueBranch<Float_t>("Ele2_hltPhotonPt") << std::endl;
    //std::cout << "PassTrigger? " << passTrigger << "; prescale of H_Photon22 = " << readerTools_->ReadValueBranch<Float_t>("H_Photon22")  << "; min_prescale=" << min_prescale << std::endl;
    //std::cout << "PassTrigger? " << passTrigger << "; prescale of H_Photon30 = " << readerTools_->ReadValueBranch<Float_t>("H_Photon30")  << "; min_prescale=" << min_prescale << std::endl;
    //std::cout << "PassTrigger? " << passTrigger << "; prescale of H_Photon36 = " << readerTools_->ReadValueBranch<Float_t>("H_Photon36")  << "; min_prescale=" << min_prescale << std::endl;
    //std::cout << "PassTrigger? " << passTrigger << "; prescale of H_Photon50 = " << readerTools_->ReadValueBranch<Float_t>("H_Photon50")  << "; min_prescale=" << min_prescale << std::endl;
    //std::cout << "PassTrigger? " << passTrigger << "; prescale of H_Photon75 = " << readerTools_->ReadValueBranch<Float_t>("H_Photon75")  << "; min_prescale=" << min_prescale << std::endl;
    //std::cout << "PassTrigger? " << passTrigger << "; prescale of H_Photon90 = " << readerTools_->ReadValueBranch<Float_t>("H_Photon90")  << "; min_prescale=" << min_prescale << std::endl;
    //std::cout << "PassTrigger? " << passTrigger << "; prescale of H_Photon120= " << readerTools_->ReadValueBranch<Float_t>("H_Photon120") << "; min_prescale=" << min_prescale << std::endl;
    //std::cout << "PassTrigger? " << passTrigger << "; prescale of H_Photon175= " << readerTools_->ReadValueBranch<Float_t>("H_Photon175") << "; min_prescale=" << min_prescale << std::endl;
    //// test output
    //--------------------------------------------------------------------------
    // Fill HLT -- analysis trigger
    //--------------------------------------------------------------------------
    //bool passTrigger = readerTools_->ReadValueBranch<bool>("PassTrigger");
    //if ( isData() ) {
    //  passTrigger = false;
    //  std::string current_file_name ( readerTools_->GetTree()->GetCurrentFile()->GetName());
    //  if(current_file_name.find("SinglePhoton") != std::string::npos) {
    //    if(analysisYearInt==2016) {
    //      if (readerTools_->ReadValueBranch<float>("H_Photon175") == 1) // take events triggered by Photon175 only plus those triggered by Photon175 AND Ele27/Ele115
    //        passTrigger = true;
    //    }
    //    else {
    //      if (readerTools_->ReadValueBranch<float>("H_Photon200") == 1) // take events triggered by Photon200 only plus those triggered by Photon200 AND Ele35
    //        passTrigger = true;
    //    }
    //  }
    //  else if(current_file_name.find("SingleElectron") != std::string::npos) {
    //    if(analysisYearInt==2016) {
    //      if (readerTools_->ReadValueBranch<float>("H_Photon175") != 1 &&
    //          //(readerTools_->ReadValueBranch<float>("H_Ele27_WPTight") == 1 || readerTools_->ReadValueBranch<float>("H_Ele115_CIdVT_GsfIdT") == 1) ) // take events triggered only by Ele27 OR Ele115
    //          //(readerTools_->ReadValueBranch<float>("H_Ele115_CIdVT_GsfIdT") == 1) ) // take events triggered only by Ele115
    //        (readerTools_->ReadValueBranch<float>("H_Ele27_WPTight") == 1) )
    //          passTrigger = true;
    //    }
    //    else {
    //      if (readerTools_->ReadValueBranch<float>("H_Photon200") != 1 &&
    //          readerTools_->ReadValueBranch<float>("H_Ele35_WPTight") == 1 ) // take events triggered only by Ele35
    //        passTrigger = true;
    //    }
    //  }
    //  else if(analysisYearInt==2018) {
    //    if (readerTools_->ReadValueBranch<float>("H_Photon200") == 1 ||
    //        //readerTools_->ReadValueBranch<float>("H_Ele32_WPTight") == 1 ||
    //        //readerTools_->ReadValueBranch<float>("H_Ele115_CIdVT_GsfIdT") == 1) // take events triggered by Photon200 OR Ele32 OR Ele115
    //      readerTools_->ReadValueBranch<float>("H_Ele32_WPTight") == 1) // take events triggered by Photon200 OR Ele32
    //        passTrigger = true;
    //  }
    //}

    //--------------------------------------------------------------------------
    // Make this a QCD fake rate calculation
    //--------------------------------------------------------------------------
    float Ele1_SCEta = readerTools_->ReadValueBranch<Float_t>("Ele1_SCEta");
    float Ele2_SCEta = readerTools_->ReadValueBranch<Float_t>("Ele2_SCEta");
    float Ele3_SCEta = readerTools_->ReadValueBranch<Float_t>("Ele3_SCEta");
    //float Ele1_PtHeep = readerTools_->ReadValueBranch<Float_t>("Ele1_PtHeep");
    //float Ele2_PtHeep = readerTools_->ReadValueBranch<Float_t>("Ele2_PtHeep");
    float Ele1_Pt = readerTools_->ReadValueBranch<Float_t>("Ele1_Pt");
    float Ele2_Pt = readerTools_->ReadValueBranch<Float_t>("Ele2_Pt");
    float Ele3_Pt = readerTools_->ReadValueBranch<Float_t>("Ele3_Pt");
    float Ele1_Phi = readerTools_->ReadValueBranch<Float_t>("Ele1_Phi");
    float Ele2_Phi = readerTools_->ReadValueBranch<Float_t>("Ele2_Phi");
    float Ele3_Phi = readerTools_->ReadValueBranch<Float_t>("Ele3_Phi");

    double fakeRate1 = -1;
    double fakeRate2 = -1;
    double fakeRate3 = -1;
    if(analysisYearInt < 2018) {
      fakeRate1 = qcdFR.GetFakeRate(Ele1_Pt, "2Jet", Ele1_SCEta);
      fakeRate2 = qcdFR.GetFakeRate(Ele2_Pt, "2Jet", Ele2_SCEta);
      fakeRate3 = qcdFR.GetFakeRate(Ele3_Pt, "2Jet", Ele3_SCEta);
    }
    else {
      fakeRate1 = qcdFR.GetFakeRate(Ele1_Pt, Ele1_SCEta, Ele1_Phi, run);
      fakeRate2 = qcdFR.GetFakeRate(Ele2_Pt, Ele2_SCEta, Ele2_Phi, run);
      fakeRate3 = qcdFR.GetFakeRate(Ele3_Pt, Ele3_SCEta, Ele3_Phi, run);
    }

    //--------------------------------------------------------------------------
    // Finally have the effective fake rate
    //--------------------------------------------------------------------------
    std::string idSuffix = "PassHEEPID";
    if(electronIDType == "EGMLoose")
      idSuffix = "PassEGMLooseID";
    int nEle_store = readerTools_->ReadValueBranch<Int_t>("nEle_store");
    int nEle_ptCut = readerTools_->ReadValueBranch<Int_t>("nEle_ptCut");
    bool Ele1_PassID = nEle_store >= 1 ? readerTools_->ReadValueBranch<Bool_t>("Ele1_"+idSuffix) : false;
    bool Ele2_PassID = nEle_store >= 2 ? readerTools_->ReadValueBranch<Bool_t>("Ele2_"+idSuffix) : false;
    bool Ele3_PassID = nEle_store >= 3 ? readerTools_->ReadValueBranch<Bool_t>("Ele3_"+idSuffix) : false;
    bool passIDRequirements = false;
    std::set<int> electronIndicesUsed;

    double fakeRateEffective = 0;
    if(doSingleFR) {
      if(Ele1_PassID) {
        if(nEle_store >= 2 && !Ele2_PassID) {
          passIDRequirements = true;
          fakeRateEffective += fakeRate2/(1-fakeRate2);
          electronIndicesUsed.insert(1);
          electronIndicesUsed.insert(2);
        }
        if(nEle_store >= 3 && !Ele3_PassID) {
          passIDRequirements = true;
          fakeRateEffective += fakeRate3/(1-fakeRate3);
          electronIndicesUsed.insert(1);
          electronIndicesUsed.insert(3);
        }
      }
      if(Ele2_PassID) {
        if(!Ele1_PassID) {
          passIDRequirements = true;
          fakeRateEffective += fakeRate1/(1-fakeRate1);
          electronIndicesUsed.insert(2);
          electronIndicesUsed.insert(1);
        }
        if(nEle_store >= 3 && !Ele3_PassID) {
          passIDRequirements = true;
          fakeRateEffective += fakeRate3/(1-fakeRate3);
          electronIndicesUsed.insert(2);
          electronIndicesUsed.insert(3);
        }
      }
      if(Ele3_PassID) {
        if(!Ele1_PassID) {
          passIDRequirements = true;
          fakeRateEffective += fakeRate1/(1-fakeRate1);
          electronIndicesUsed.insert(3);
          electronIndicesUsed.insert(1);
        }
        if(!Ele2_PassID) {
          passIDRequirements = true;
          fakeRateEffective += fakeRate2/(1-fakeRate2);
          electronIndicesUsed.insert(3);
          electronIndicesUsed.insert(2);
        }
      }
    }
    else {
      fakeRateEffective = fakeRate1/(1-fakeRate1);
      passIDRequirements = !Ele1_PassID && !Ele2_PassID;
      if(nEle_store >= 2) {
        fakeRateEffective *= fakeRate2/(1-fakeRate2);
      }
      electronIndicesUsed.insert(1);
      electronIndicesUsed.insert(2);
      //XXX do we consider electron 3 here?
    }
    int indexOfHighestPtEleUsed = 1;
    int indexOfSecondHighestPtEleUsed = 2;
    if(passIDRequirements) {
      indexOfHighestPtEleUsed = *electronIndicesUsed.begin();
      indexOfSecondHighestPtEleUsed = *std::next(electronIndicesUsed.begin(), 1);
    }
    std::string ele1KeyName = "Ele"+to_string(indexOfHighestPtEleUsed);
    std::string ele2KeyName = "Ele"+to_string(indexOfSecondHighestPtEleUsed);

    //if(1-fakeRate1 <= 0)
    //{
    //  cout << "ERROR: Found fakeRate1: " << fakeRate1 << " for SCEta=" << Ele1_SCEta << " SCEt="
    //    << Ele1_SCEnergy/cosh(Ele1_SCEta) << "=" << Ele1_SCEnergy << "/" <<
    //    cosh(Ele1_SCEta) << endl;
    //}
    //FIXME: add error on fake rate as well
    // double eFakeRateEffective = fakeRateEffective * sqrt (  ( eFakeRate1 / fakeRate1 ) * ( eFakeRate1 / fakeRate1 ) +
    //					     ( eFakeRate2 / fakeRate2 ) * ( eFakeRate2 / fakeRate2 ) );
    double eFakeRateEffective = 0.0;

    weight = fakeRateEffective * min_prescale;
    // now, for the rest of the code, for MC, put the appropriate weights in the min_prescale
    if(!isData())
      min_prescale = gen_weight*pileup_weight;

    //--------------------------------------------------------------------------
    // What kind of event is this?
    //   - Barrel
    //   - Endcap 1 (eta < 2.0)
    //   - Endcap 2 (eta > 2.0)
    //--------------------------------------------------------------------------

    bool ele1_isBarrel  = false;
    bool ele1_isEndcap1 = false;
    bool ele1_isEndcap2 = false;
    bool ele2_isBarrel  = false;
    bool ele2_isEndcap1 = false;
    bool ele2_isEndcap2 = false;

    // redefine eta/phi/pt
    Ele1_SCEta = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_SCEta");
    Ele2_SCEta = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_SCEta");
    //Ele1_PtHeep = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_PtHeep");
    //Ele2_PtHeep = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_PtHeep");
    Ele1_Pt = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_Pt");
    Ele2_Pt = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_Pt");
    Ele1_Phi = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_Phi");
    Ele2_Phi = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_Phi");
    float Ele1_Eta = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_Eta");
    float Ele2_Eta = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_Eta");

    if( fabs( Ele1_Eta  ) < eleEta_bar )        ele1_isBarrel  = true;
    if( fabs( Ele1_Eta  ) > eleEta_end1_min &&
        fabs( Ele1_Eta  ) < eleEta_end1_max )   ele1_isEndcap1 = true;
    if( fabs( Ele1_Eta  ) > eleEta_end2_min &&
        fabs( Ele1_Eta  ) < eleEta_end2_max )   ele1_isEndcap2 = true;

    if( fabs( Ele2_Eta  ) < eleEta_bar )        ele2_isBarrel  = true;
    if( fabs( Ele2_Eta  ) > eleEta_end1_min &&
        fabs( Ele2_Eta  ) < eleEta_end1_max )   ele2_isEndcap1 = true;
    if( fabs( Ele2_Eta  ) > eleEta_end2_min &&
        fabs( Ele2_Eta  ) < eleEta_end2_max )   ele2_isEndcap2 = true;

    bool ele1_isEndcap = ( ele1_isEndcap1 || ele1_isEndcap2 ) ;
    bool isEnd2_1 = ( fabs(Ele1_Eta) > eleEta_end2_min &&
        fabs(Ele1_Eta) < eleEta_end2_max ) ;
    bool ele2_isEndcap = ( ele2_isEndcap1 || ele2_isEndcap2 ) ;
    bool isEnd2_2 = ( fabs(Ele2_Eta) > eleEta_end2_min &&
        fabs(Ele2_Eta) < eleEta_end2_max ) ;

    bool isEBEB = ( ele1_isBarrel && ele2_isBarrel ) ;
    bool isEBEE = ( ( ele1_isBarrel && ele2_isEndcap ) ||
        ( ele2_isBarrel && ele1_isEndcap ) );
    bool isEEEE = ( ele1_isEndcap && ele2_isEndcap ) ;
    bool isEB   = ( isEBEB || isEBEE ) ;
    bool isEnd2End2 = isEnd2_1 && isEnd2_2;

    //--------------------------------------------------------------------------
    // Fill variables
    //--------------------------------------------------------------------------
    FillUserTH1D("EventCount"           , 1                   , 1   );
    FillUserTH1D("FakeRateEffective"    , fakeRateEffective);
    FillUserTH1D("MinPrescale"          , min_prescale     );
    //if(fakeRateEffective * min_prescale != 1.0)
    //  std::cout << "!!!!!THIS EVENT HAD fakeRateEffective * min_prescale != 1.0: " << fakeRateEffective * min_prescale << std::endl;
    //if(fakeRateEffective >= 1) {
    //  std::cout << "!!!!!EVENT " << jentry << " HAD fakeRateEffective = " << fakeRateEffective << " and min_prescale = " << min_prescale << std::endl;
    //  std::cout.precision(0);
    //  std::cout << fixed <<  "Run = " << run << ", event = " << event << ", ls = " << ls << std::endl;
    //  std::cout.precision(2);
    //  cout << "\tFound fakeRate1: " << fakeRate1 << " for SCEta=" << Ele1_SCEta << " SCEt="
    //    << Ele1_SCEnergy/cosh(Ele1_SCEta) << "=" << Ele1_SCEnergy << "/" <<
    //    cosh(Ele1_SCEta) << endl;
    //  cout << "\tFound fakeRate2: " << fakeRate2 << " for SCEta=" << Ele2_SCEta << " SCEt="
    //    << Ele2_SCEnergy/cosh(Ele2_SCEta) << "=" << Ele2_SCEnergy << "/" <<
    //    cosh(Ele2_SCEta) << endl;
    //}
    //if(min_prescale != 1.0) {
    //  std::cout << "!!!!!EVENT " << jentry << " HAD fakeRateEffective=" << fakeRateEffective << " and min_prescale != 1.0: " << min_prescale << "; Ele1_hltPhotonPt=" << Ele1_hltPhotonPt <<  std::endl;
    //  std::cout.precision(0);
    //  std::cout << fixed <<  "Run = " << run << ", event = " << event << ", ls = " << ls << std::endl;
    //  std::cout.precision(2);
    //  std::cout << "\tEle1_hltPhotonPt: " << Ele1_hltPhotonPt << std::endl;
    //  std::cout << "\tEle2_hltPhotonPt: " << readerTools_->ReadValueBranch<Float_t>("Ele2_hltPhotonPt") << std::endl;
    //  std::cout << "\tEle1_Pt: " << readerTools_->ReadValueBranch<Float_t>("Ele1_Pt") << "; Ele1_Eta: " << readerTools_->ReadValueBranch<Float_t>("Ele1_Eta") << std::endl;
    //  std::cout << "\tEle2_Pt: " << readerTools_->ReadValueBranch<Float_t>("Ele2_Pt") << "; Ele2_Eta: " << readerTools_->ReadValueBranch<Float_t>("Ele2_Eta") << std::endl;
    //  std::cout << "\tPassTrigger? " << passTrigger << "; prescale of H_Photon22 = " << readerTools_->ReadValueBranch<Float_t>("H_Photon22")  << "; min_prescale=" << min_prescale << std::endl;
    //  std::cout << "\tPassTrigger? " << passTrigger << "; prescale of H_Photon30 = " << readerTools_->ReadValueBranch<Float_t>("H_Photon30")  << "; min_prescale=" << min_prescale << std::endl;
    //  std::cout << "\tPassTrigger? " << passTrigger << "; prescale of H_Photon36 = " << readerTools_->ReadValueBranch<Float_t>("H_Photon36")  << "; min_prescale=" << min_prescale << std::endl;
    //  std::cout << "\tPassTrigger? " << passTrigger << "; prescale of H_Photon50 = " << readerTools_->ReadValueBranch<Float_t>("H_Photon50")  << "; min_prescale=" << min_prescale << std::endl;
    //  std::cout << "\tPassTrigger? " << passTrigger << "; prescale of H_Photon75 = " << readerTools_->ReadValueBranch<Float_t>("H_Photon75")  << "; min_prescale=" << min_prescale << std::endl;
    //  std::cout << "\tPassTrigger? " << passTrigger << "; prescale of H_Photon90 = " << readerTools_->ReadValueBranch<Float_t>("H_Photon90")  << "; min_prescale=" << min_prescale << std::endl;
    //  std::cout << "\tPassTrigger? " << passTrigger << "; prescale of H_Photon120= " << readerTools_->ReadValueBranch<Float_t>("H_Photon120") << "; min_prescale=" << min_prescale << std::endl;
    //  std::cout << "\tPassTrigger? " << passTrigger << "; prescale of H_Photon175= " << readerTools_->ReadValueBranch<Float_t>("H_Photon175") << "; min_prescale=" << min_prescale << std::endl;
    //}

    // reweighting
    fillVariableWithValue ( "Reweighting", 1, fakeRateEffective * min_prescale ) ;

    // LHE cuts
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
    fillVariableWithValue("PassLHECuts",passLHECuts, fakeRateEffective * min_prescale);

    // JSON variable
    fillVariableWithValue ("PassJSON", readerTools_->ReadValueBranch<Bool_t>("PassJSON"), fakeRateEffective * min_prescale);

    //--------------------------------------------------------------------------
    // Fill noise filters
    //--------------------------------------------------------------------------
    // see: https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
    // we filled these at skim time
    fillVariableWithValue("PassGlobalSuperTightHalo2016Filter" , readerTools_->ReadValueBranch<Bool_t>("PassGlobalSuperTightHalo2016Filter")     , fakeRateEffective * min_prescale);
    fillVariableWithValue("PassGoodVertices"                   , readerTools_->ReadValueBranch<Bool_t>("PassGoodVertices")                       , fakeRateEffective * min_prescale);
    fillVariableWithValue("PassHBHENoiseFilter"                , readerTools_->ReadValueBranch<Bool_t>("PassHBHENoiseFilter")                    , fakeRateEffective * min_prescale);
    fillVariableWithValue("PassHBHENoiseIsoFilter"             , readerTools_->ReadValueBranch<Bool_t>("PassHBHENoiseIsoFilter")                 , fakeRateEffective * min_prescale);
    // eBadScFilter not suggested for MC
    if(isData())
      fillVariableWithValue("PassBadEESupercrystalFilter"      , readerTools_->ReadValueBranch<Bool_t>("PassBadEESupercrystalFilter")            , fakeRateEffective * min_prescale);
    else
      fillVariableWithValue("PassBadEESupercrystalFilter"      , 1                                                                                , fakeRateEffective * min_prescale);
    fillVariableWithValue("PassEcalDeadCellTrigPrim"           , readerTools_->ReadValueBranch<Bool_t>("PassEcalDeadCellTrigPrim")               , fakeRateEffective * min_prescale);
    // not recommended
    //fillVariableWithValue("PassChargedCandidateFilter"         , int(readerTools_->ReadValueB<Float_t>("PassChargedCandidateFilter")            == 1), fakeRateEffective * min_prescale);
    fillVariableWithValue("PassBadPFMuonFilter"                , readerTools_->ReadValueBranch<Bool_t>("PassBadPFMuonFilter")                    , fakeRateEffective * min_prescale);
    // EcalBadCalibV2 for 2017, 2018
    if(analysisYearInt > 2016)
      fillVariableWithValue("PassEcalBadCalibV2Filter"         , readerTools_->ReadValueBranch<Bool_t>("PassEcalBadCalibV2Filter")               , fakeRateEffective * min_prescale);
    else
      fillVariableWithValue("PassEcalBadCalibV2Filter"         , 1                                                                                , fakeRateEffective * min_prescale);

    // Electrons
    int PassNEle = 0;
    //if ( nEle_ptCut == 2 ) PassNEle = 1;
    if ( nEle_ptCut >= 2 ) PassNEle = 1;
    // we only look at events that have at least two loose electrons with pT > 35 GeV

    //FIXME fix the counting to avoid the below
    //// nEle_store is the number of loose eles with pt>10
    //if(nEle_store==3)
    //{
    //  // if 3 stored, 2 leads must pass Pt cut and third must fail
    //  if(Ele3_Pt<50 && Ele1_Pt>=50 && Ele2_Pt>=50)
    //    PassNEle=1;
    //}
    //else if(nEle_store==2)
    //{
    //  // if 2 stored, OK
    //  if(Ele1_Pt>=50 && Ele2_Pt>=50)
    //      PassNEle=1;
    //}

    double M_ej_avg = 0;
    double M_ej_min = 0;
    double M_ej_max = 0;
    double M_ej_asym = 0;

    // Muons
    int nMuon_ptCut = readerTools_->ReadValueBranch<Int_t>("nMuon_ptCut");
    double Muon1_Pt = readerTools_->ReadValueBranch<Float_t>("Muon1_Pt");
    double Muon1_Eta = readerTools_->ReadValueBranch<Float_t>("Muon1_Eta");
    double Muon1_Phi = readerTools_->ReadValueBranch<Float_t>("Muon1_Phi");
    int PassNMuon = 0;
    if ( nMuon_ptCut == 0 ) PassNMuon = 1;

    fillVariableWithValue ( "PassHLT"                        , passTrigger             , fakeRateEffective * min_prescale ) ;
    fillVariableWithValue("nEle_hltMatched",-1, fakeRateEffective * min_prescale ) ;
    fillVariableWithValue("nJet_hltMatched",-1, fakeRateEffective * min_prescale ) ;


    // Jets
    int nJet_ptCut = readerTools_->ReadValueBranch<Int_t>("nJet_ptCut");
    int nJet_store = readerTools_->ReadValueBranch<Int_t>("nJet_store");
    float Jet1_Pt = readerTools_->ReadValueBranch<Float_t>("Jet1_Pt");
    float Jet1_Eta = readerTools_->ReadValueBranch<Float_t>("Jet1_Eta");
    float Jet1_Phi = readerTools_->ReadValueBranch<Float_t>("Jet1_Phi");
    float Jet2_Pt = readerTools_->ReadValueBranch<Float_t>("Jet2_Pt");
    float Jet2_Eta = readerTools_->ReadValueBranch<Float_t>("Jet2_Eta");
    float Jet2_Phi = readerTools_->ReadValueBranch<Float_t>("Jet2_Phi");
    float DR_Jet1Jet2 = readerTools_->ReadValueBranch<Float_t>("DR_Jet1Jet2");
    float Jet3_Pt = readerTools_->ReadValueBranch<Float_t>("Jet3_Pt");
    float Jet3_Eta = readerTools_->ReadValueBranch<Float_t>("Jet3_Eta");
    float Jet3_Phi = readerTools_->ReadValueBranch<Float_t>("Jet3_Phi");
    fillVariableWithValue(   "nJet"                          , nJet_ptCut      , fakeRateEffective * min_prescale ) ;
    if ( nJet_store >= 1 ) {
      fillVariableWithValue( "Jet1_Pt"                       , Jet1_Pt         , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "Jet1_Pt_skim"                  , Jet1_Pt         , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "Jet1_Eta"                      , Jet1_Eta        , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "Jet1_Phi"                      , Jet1_Phi        , fakeRateEffective * min_prescale ) ;
    }

    //--------------------------------------------------------------------------
    // Recalculate some variables
    //--------------------------------------------------------------------------

    TLorentzVector e1, j1, e2, j2,j3, mu, met;
    TLorentzVector eejj, e1e2mu;
    TLorentzVector eej, ejj, ee;
    TLorentzVector e1j3, e2j3, j1j3, j2j3, j1j2, j1j2j3, eejjj;
    TLorentzVector e1j1, e1j2, e2j1, e2j2;

    e1.SetPtEtaPhiM ( Ele1_Pt, Ele1_Eta, Ele1_Phi, 0.0 );
    e2.SetPtEtaPhiM ( Ele2_Pt, Ele2_Eta, Ele2_Phi, 0.0 );
    j1.SetPtEtaPhiM ( Jet1_Pt, Jet1_Eta, Jet1_Phi, 0.0 );
    j2.SetPtEtaPhiM ( Jet2_Pt, Jet2_Eta, Jet2_Phi, 0.0 );
    mu.SetPtEtaPhiM ( Muon1_Pt, Muon1_Eta, Muon1_Phi, 0.0 );
    float PFMET_Type1_Pt = readerTools_->ReadValueBranch<Float_t>("PFMET_Type1_Pt");
    float PFMET_Type1_Phi = readerTools_->ReadValueBranch<Float_t>("PFMET_Type1_Phi");
    met.SetPtEtaPhiM ( PFMET_Type1_Pt, 0.0, PFMET_Type1_Phi, 0.0 );

    eejj = e1 + e2 + j1 + j2 ;
    eej  = e1 + e2 + j1;
    ejj  = e1 + j1 + j2;
    ee   = e1 + e2;
    j1j2 = j1 + j2;
    e1j1  = e1 + j1;
    e1j2  = e1 + j2;
    e2j1  = e2 + j1;
    e2j2  = e2 + j2;

    double min_DR_EleJet;
    double DR_Ele1Jet3;
    double DR_Ele2Jet3;
    double DR_Ele1Ele2 = e1.DeltaR( e2 );

    double M_eejj = eejj.M();
    double M_eej  = eej.M();
    double M_ejj  = ejj.M();
    double M_e1e2 = ee.M();
    double M_e1j1 = e1j1.M();
    double M_e1j2 = e1j2.M();
    double M_e2j1 = e2j1.M();
    double M_e2j2 = e2j1.M();
    double MT_Ele1MET = sqrt ( 2.0 * e1.Pt() * met.Pt() * ( 1.0 - cos ( met.DeltaPhi(e1))));

    double Pt_j1j2 = j1j2.Pt();
    double Pt_j1j3;
    double Pt_j2j3;
    double Pt_j1j2j3;
    double Pt_e1e2 = ee.Pt();

    double M_j1j3, M_j2j3;
    double M_e1j3, M_e2j3;
    double M_eejjj;

    double min_DeltaR_Zj = 999.;
    if ( ee.DeltaR ( j1 ) < min_DeltaR_Zj ) min_DeltaR_Zj = ee.DeltaR ( j1 );
    if ( ee.DeltaR ( j2 ) < min_DeltaR_Zj ) min_DeltaR_Zj = ee.DeltaR ( j2 );
    double DR_ZJ1 = ee.DeltaR ( j1 );
    double DR_ZJ2 = ee.DeltaR ( j2 );

    if ( nJet_ptCut > 2 ) {
      j3.SetPtEtaPhiM ( Jet3_Pt, Jet3_Eta, Jet3_Phi, 0.0 );

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
    // calc Meejj
    float Meejj = eejj.M();

    double sT_zjj = Pt_e1e2 + Jet1_Pt + Jet2_Pt;
    double sT_eejj = e1.Pt() + e2.Pt() + j1.Pt() + j2.Pt();

    // Muons
    fillVariableWithValue(   "PassNMuon"                     , PassNMuon               , fakeRateEffective * min_prescale ) ;

    // Electrons
    fillVariableWithValue(   "PassIDRequirements"            , passIDRequirements      , fakeRateEffective * min_prescale ) ;
    fillVariableWithValue(   "PassNEle"                      , PassNEle                , fakeRateEffective * min_prescale ) ;
    bool Ele1_PassHEEPEta = readerTools_->ReadValueBranch<Bool_t>(ele1KeyName+"_PassHEEPGsfEleSCEtaMultiRangeCut");
    bool Ele2_PassHEEPEta = readerTools_->ReadValueBranch<Bool_t>(ele2KeyName+"_PassHEEPGsfEleSCEtaMultiRangeCut");
    if ( nEle_store >= 1 ) {
      fillVariableWithValue( "Ele1_Pt"                       , Ele1_Pt            , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "Ele1_Pt_skim"                  , Ele1_Pt            , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "Ele1_Eta",            Ele1_Eta, fakeRateEffective * min_prescale  ) ;
      fillVariableWithValue( "Ele1_Phi",            Ele1_Phi, fakeRateEffective * min_prescale  ) ;
      //fillVariableWithValue( "Ele1_PassHEEPSCEtaCut"                      , Ele1_PassHEEPEta            , fakeRateEffective * min_prescale ) ;
    }
    if ( nEle_store >= 2 ) {
      fillVariableWithValue( "Ele2_Pt"                       , Ele2_Pt            , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "Ele2_Pt_skim"                  , Ele2_Pt            , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "Ele2_Eta",            Ele2_Eta, fakeRateEffective * min_prescale  ) ;
      fillVariableWithValue( "Ele2_Phi",            Ele2_Phi, fakeRateEffective * min_prescale  ) ;
      //fillVariableWithValue( "Ele2_PassHEEPSCEtaCut"                      , Ele2_PassHEEPEta            , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "Pt_e1e2"                       , Pt_e1e2             , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "Pt_e1e2_skim"                       , Pt_e1e2             , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "M_e1e2"                        , M_e1e2                  , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "M_e1e2_skim"                        , M_e1e2                  , fakeRateEffective * min_prescale ) ;
      //fillVariableWithValue( "M_e1e2_opt"                    , M_e1e2                  , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "M_e1e2_bkgCR"     , M_e1e2 , fakeRateEffective * min_prescale ) ;
    }

    // DeltaR
    float DR_Ele1Jet1 = readerTools_->ReadValueBranch<Float_t>("DR_"+ele1KeyName+"Jet1");
    float DR_Ele2Jet1 = readerTools_->ReadValueBranch<Float_t>("DR_"+ele2KeyName+"Jet1");
    float DR_Ele1Jet2 = readerTools_->ReadValueBranch<Float_t>("DR_"+ele1KeyName+"Jet2");
    float DR_Ele2Jet2 = readerTools_->ReadValueBranch<Float_t>("DR_"+ele2KeyName+"Jet2");
    if ( nEle_store >= 2 && nJet_store >= 1) {
      fillVariableWithValue( "DR_Ele1Jet1"                   , DR_Ele1Jet1             , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "DR_Ele2Jet1"                   , DR_Ele2Jet1             , fakeRateEffective * min_prescale ) ;
      if(nJet_store >= 2) {
        fillVariableWithValue( "DR_Ele1Jet2"                 , DR_Ele1Jet2             , fakeRateEffective * min_prescale ) ;
        fillVariableWithValue( "DR_Ele2Jet2"                 , DR_Ele2Jet2             , fakeRateEffective * min_prescale ) ;
      }
    }

    // sT
    float MejMin = M_ej_min;
    float MejMax = M_ej_max;
    float Masym = M_ej_asym;

    if ( DR_Ele1Jet1 < min_DR_EleJet ) min_DR_EleJet = DR_Ele1Jet1;
    if ( DR_Ele1Jet2 < min_DR_EleJet ) min_DR_EleJet = DR_Ele1Jet2;
    if ( DR_Ele2Jet1 < min_DR_EleJet ) min_DR_EleJet = DR_Ele2Jet1;
    if ( DR_Ele2Jet2 < min_DR_EleJet ) min_DR_EleJet = DR_Ele2Jet2;
    if (nJet_ptCut > 2 ) {
      if ( DR_Ele1Jet3 < min_DR_EleJet ) min_DR_EleJet = DR_Ele1Jet3;
      if ( DR_Ele2Jet3 < min_DR_EleJet ) min_DR_EleJet = DR_Ele2Jet3;
    }

    //--------------------------------------------------------------------------
    // Calculate electron-jet pair mass values
    //--------------------------------------------------------------------------
    if ( nJet_store >= 2 ) {
      fillVariableWithValue( "Jet2_Pt"                       , Jet2_Pt         , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "Jet2_Pt_skim"                  , Jet2_Pt         , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "Jet2_Eta"                      , Jet2_Eta        , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "Jet2_Phi"                      , Jet2_Phi        , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "DR_Jet1Jet2"                   , DR_Jet1Jet2             , fakeRateEffective * min_prescale ) ;
      if ( nEle_store >= 2 && nJet_store >= 2) {
        if ( fabs(M_e1j1-M_e2j2) < fabs(M_e1j2-M_e2j1) )  {
          M_ej_avg = (M_e1j1 + M_e2j2) / 2.0;
          if    ( M_e1j1 < M_e2j2 ) { M_ej_min = M_e1j1; M_ej_max = M_e2j2; }
          else                      { M_ej_min = M_e2j2; M_ej_max = M_e1j1; }
        }
        else {
          M_ej_avg = (M_e1j2 + M_e2j1) / 2.0;
          if    ( M_e1j2 < M_e2j1 ) { M_ej_min = M_e1j2; M_ej_max = M_e2j1; }
          else                      { M_ej_min = M_e2j1; M_ej_max = M_e1j2; }
        }
        // compute Mej_asym
        M_ej_asym = (M_ej_max - M_ej_min)/(M_ej_max + M_ej_min);
      }
    }
    fillVariableWithValue( "Jet3_Pt"    , Jet3_Pt     , fakeRateEffective * min_prescale  ) ;
    fillVariableWithValue( "Jet3_Eta"   , Jet3_Eta    , fakeRateEffective * min_prescale  ) ;
    fillVariableWithValue( "Jet3_Phi"   , Jet3_Phi    , fakeRateEffective * min_prescale  ) ;
    if ( nEle_store >= 2 && nJet_store >= 2) {
      // SIC recompute sT using PtHeep. FIXME: this is now being done in skims
      //sT_eejj = Ele1_PtHeep+Ele2_PtHeep+Jet1_Pt+Jet2_Pt;
      fillVariableWithValue( "sT_eejj"                       , sT_eejj                 , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "sT_eejj_bkgCR"    , sT_eejj , fakeRateEffective * min_prescale ) ;
      fillVariableWithValue( "sT_eejj_skim"    , sT_eejj , fakeRateEffective * min_prescale ) ;
    }
    fillVariableWithValue( "M_e1j1", M_e1j1, fakeRateEffective * min_prescale  ) ;
    fillVariableWithValue( "M_e1j2", M_e1j2, fakeRateEffective * min_prescale  ) ;
    fillVariableWithValue( "M_e2j1", M_e2j1, fakeRateEffective * min_prescale  ) ;
    fillVariableWithValue( "M_e2j2", M_e2j2, fakeRateEffective * min_prescale  ) ;
    fillVariableWithValue( "Masym", Masym, fakeRateEffective * min_prescale  ) ;
    fillVariableWithValue( "MejMin", MejMin, fakeRateEffective * min_prescale  ) ;
    fillVariableWithValue( "MejMax", MejMax, fakeRateEffective * min_prescale  ) ;
    fillVariableWithValue( "Meejj", Meejj, fakeRateEffective * min_prescale  ) ;
    //fillVariableWithValue( "PFMET_opt", PFMET_Type1_Pt, fakeRateEffective * min_prescale  ) ;
    fillVariableWithValue( "PFMET_Type1_Pt", PFMET_Type1_Pt,  fakeRateEffective * min_prescale ) ;
    fillVariableWithValue( "PFMET_Type1_Phi", PFMET_Type1_Phi, fakeRateEffective * min_prescale ) ;

    // Dummy variables
    fillVariableWithValue ("skim_selection", 1, fakeRateEffective * min_prescale );
    fillVariableWithValue ("preselection", 1, fakeRateEffective * min_prescale );
    fillVariableWithValue ("trainingSelection", 1, fakeRateEffective * min_prescale );


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

    //--------------------------------------------------------------------------
    // Did we at least pass the noise filtes?
    //--------------------------------------------------------------------------

    bool passed_minimum = ( passedAllPreviousCuts("PassEcalBadCalibV2Filter") && passedCut ("PassEcalBadCalibV2Filter"));

    //--------------------------------------------------------------------------
    // Did we make it to the background control region?
    //--------------------------------------------------------------------------
    bool bkgControlRegion = passedAllPreviousCuts("M_e1e2_bkgCR") && passedCut("M_e1e2_bkgCR");

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

    FillUserTH1D( "PileupWeight"   , -1.0 );
    FillUserTH1D( "GeneratorWeight", -1.0 );

    bool passed_nele = ( passedAllPreviousCuts("PassNEle") && passedCut ("PassNEle") );
    if(passed_nele)
    {
      FillUserTH1D("FakeRateEffective_PassNEle"    , fakeRateEffective);
      //if(fakeRateEffective < 4e-4)
      //{
      //  std::cout << "!!!!!THIS EVENT PASSING NELE_PTCUT HAD fakeRateEffective = " << fakeRateEffective << std::endl;
      //  std::cout << "\tFound fakeRate1: " << fakeRate1 << " for SCEta=" << Ele1_SCEta << " Pt=" << Ele1_Pt << " --> term1=" << fakeRate1/(1-fakeRate1) << std::endl;
      //  std::cout << "\tFound fakeRate2: " << fakeRate2 << " for SCEta=" << Ele2_SCEta << " Pt=" << Ele2_Pt << " --> term2=" << fakeRate2/(1-fakeRate2) << std::endl;
      //}
    }

    //--------------------------------------------------------------------------
    // Fill background control region plots
    //--------------------------------------------------------------------------
    if(bkgControlRegion) {
      FillUserTH1D("Mee_BkgControlRegion"	                ,    M_e1e2,    fakeRateEffective * min_prescale , "M_e1e2_bkgCR");
      if(nBJet_ptCut>=1)
        FillUserTH1D( "Mee_BkgControlRegion_gteOneBtaggedJet"      , M_e1e2,  fakeRateEffective * min_prescale * weightAtLeastOneBJet, "M_e1e2_bkgCR" ) ;
      if(nBJet_ptCut>=2)
        FillUserTH1D( "Mee_BkgControlRegion_gteTwoBtaggedJets"      , M_e1e2,  fakeRateEffective * min_prescale * weightAtLeastTwoBJets, "M_e1e2_bkgCR" ) ;
      if      ( isEB   ) FillUserTH1D( "Mee_EB_BkgControlRegion"  , M_e1e2, fakeRateEffective * min_prescale, "M_e1e2_bkgCR" );
      if      ( isEBEB ) FillUserTH1D( "Mee_EBEB_BkgControlRegion", M_e1e2, fakeRateEffective * min_prescale, "M_e1e2_bkgCR" );
      else if ( isEBEE ) FillUserTH1D( "Mee_EBEE_BkgControlRegion", M_e1e2, fakeRateEffective * min_prescale, "M_e1e2_bkgCR" );
      else if ( isEEEE ) FillUserTH1D( "Mee_EEEE_BkgControlRegion", M_e1e2, fakeRateEffective * min_prescale, "M_e1e2_bkgCR" );
      if      ( isEnd2End2 ) FillUserHist( "Mee_End2End2_BkgControlRegion", M_e1e2, fakeRateEffective * min_prescale, "M_e1e2_bkgCR" );
      // scale factor dependence histos
      if ( nJet_ptCut == 2 )
        FillUserTH1D("Mee_NJetEq2_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      else if( nJet_ptCut == 3 )
        FillUserTH1D("Mee_NJetEq3_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      else if( nJet_ptCut == 4 )
        FillUserTH1D("Mee_NJetEq4_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      else if( nJet_ptCut == 5 )
        FillUserTH1D("Mee_NJetEq5_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      else if( nJet_ptCut == 6 )
        FillUserTH1D("Mee_NJetEq6_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      else if( nJet_ptCut == 7 )
        FillUserTH1D("Mee_NJetEq7_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      if ( nJet_ptCut >= 3 )
        FillUserTH1D("Mee_NJetGeq3_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      if ( nJet_ptCut >= 4 )
        FillUserTH1D("Mee_NJetGeq4_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      if (sT_eejj >= 300 && sT_eejj < 500)
        FillUserTH1D("Mee_sT300To500_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      else if (sT_eejj >= 500 && sT_eejj < 750)
        FillUserTH1D("Mee_sT500To750_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      else if (sT_eejj >= 750 && sT_eejj < 1250)
        FillUserTH1D("Mee_sT750To1250_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      else if (sT_eejj >= 1250)
        FillUserTH1D("Mee_sT1250ToInf_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      if (M_ej_min >= 100 && M_ej_min < 200)
        FillUserTH1D("Mee_MejMin100To200_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      else if (M_ej_min >= 200 && M_ej_min < 300)
        FillUserTH1D("Mee_MejMin200To300_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      else if (M_ej_min >= 300 && M_ej_min < 400)
        FillUserTH1D("Mee_MejMin300To400_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      else if (M_ej_min >= 400 && M_ej_min < 500)
        FillUserTH1D("Mee_MejMin400To500_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      else if (M_ej_min >= 500 && M_ej_min < 650)
        FillUserTH1D("Mee_MejMin500To650_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
      else if (M_ej_min >= 650)
        FillUserTH1D("Mee_MejMin650ToInf_BkgControlRegion", M_e1e2                         , fakeRateEffective * min_prescale );
    }

    //--------------------------------------------------------------------------
    // Fill preselection plots
    //--------------------------------------------------------------------------

    if ( passed_preselection ) {
      //XXX SIC DEBUG
      //if(hltPhotonPt < 100) {
      //  std::cout << "INFO: found prescale " << min_prescale << " for trigger name " << triggerName << " with hltPhotonPt = " << hltPhotonPt << ", for year: " << analysisYear << std::endl;
      //  std::cout << "The weight of this event: fakeRateEffective=" << fakeRateEffective << " x min_prescale=" << min_prescale << " = " << fakeRateEffective*min_prescale << std::endl;
      //  std::cout << "run: " << run << " ls: " << ls << " event: " << event << ", file = " << current_file_name << std::endl;
      //}
      //
      //std::cout << "We have electrons which look like (ptHEEP,eta,phi): (" << Ele1_PtHeep << "," << Ele1_Eta << "," << Ele1_Phi << "); FR = " << qcdFakeRate.GetFakeRate(Ele1_Eta,Ele2_PtHeep) << std::endl;
      //std::cout << "We have electrons which look like (pt,eta,phi): (" << Ele1_Pt << "," << Ele1_Eta << "," << Ele1_Phi << "); FR = " << qcdFakeRate.GetFakeRate(Ele1_Eta,Ele2_Pt) << std::endl;
      //std::cout << "Used fake rate=" << fakeRate1 << std::endl;
      ////float fakeRate2 = qcdFakeRate.GetFakeRate(Ele2_Eta,Ele2_PtHeep);
      //std::cout << "We have electrons which look like (pt,eta,phi): (" << Ele2_Pt << "," << Ele2_Eta << "," << Ele2_Phi << ")" << std::endl;
      //if(nEle_store > 2)
      //  std::cout << "We have electrons which look like (pt,eta,phi): (" << Ele3_Pt << "," << Ele3_Eta << "," << Ele3_Phi << ")" << std::endl;

      //--------------------------------------------------------------------------
      // Electron quality histograms (preselection)
      //--------------------------------------------------------------------------
      double Ele1_CorrIsolation        = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_CorrIsolation");
      double Ele1_DeltaEtaTrkSC        = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_DeltaEtaTrkSC");
      double Ele1_EcalIsolation        = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_EcalIsolation");
      double Ele1_HcalIsolation        = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_HcalIsolation");
      double Ele1_TrkIsolation         = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_TrkIsolation");
      bool Ele1_HasMatchedPhot         = readerTools_->ReadValueBranch<Bool_t>(ele1KeyName+"_HasMatchedPhot");
      double Ele1_HoE                  = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_HoE");
      double Ele1_LeadVtxDistXY        = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_LeadVtxDistXY");
      double Ele1_LeadVtxDistZ         = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_LeadVtxDistZ");
      int Ele1_MissingHits          = readerTools_->ReadValueBranch<Int_t>(ele1KeyName+"_MissingHits")        ;
      double Ele1_SCEta                = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_SCEta");
      double Ele1_Full5x5SigmaIEtaIEta = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_Full5x5SigmaIEtaIEta");
      int Ele1_Charge               = readerTools_->ReadValueBranch<Int_t>(ele1KeyName+"_Charge");
      //double Ele1_PtHeep               = readerTools_->ReadValueBranch<Float_t>(ele1KeyName+"_PtHeep");

      FillUserTH1D("CorrIsolation_1stEle_PAS"         , Ele1_CorrIsolation                  , min_prescale * fakeRateEffective   );
      FillUserTH1D("DeltaEtaTrkSC_1stEle_PAS"         , Ele1_DeltaEtaTrkSC                  , min_prescale * fakeRateEffective   );
      FillUserTH1D("EcalIsolation_1stEle_PAS"         , Ele1_EcalIsolation                  , min_prescale * fakeRateEffective   );
      FillUserTH1D("HcalIsolation_1stEle_PAS"         , Ele1_HcalIsolation                  , min_prescale * fakeRateEffective   );
      FillUserTH1D("TrkIsolation_1stEle_PAS"          , Ele1_TrkIsolation                   , min_prescale * fakeRateEffective   );
      FillUserTH1D("HasMatchedPhot_1stEle_PAS"        , Ele1_HasMatchedPhot                 , min_prescale * fakeRateEffective   );
      FillUserTH1D("HoE_1stEle_PAS"                   , Ele1_HoE                            , min_prescale * fakeRateEffective   );
      FillUserTH1D("LeadVtxDistXY_1stEle_PAS"         , Ele1_LeadVtxDistXY                  , min_prescale * fakeRateEffective   );
      FillUserTH1D("LeadVtxDistZ_1stEle_PAS"          , Ele1_LeadVtxDistZ                   , min_prescale * fakeRateEffective   );
      FillUserTH1D("MissingHits_1stEle_PAS"           , Ele1_MissingHits                    , min_prescale * fakeRateEffective   );
      if ( fabs(Ele1_SCEta) < eleEta_bar ) {
        FillUserTH1D("Full5x5SigmaIEtaIEta_Barrel_1stEle_PAS", Ele1_Full5x5SigmaIEtaIEta                  , min_prescale * fakeRateEffective   );
      }
      else if ( fabs(Ele1_SCEta) > eleEta_end1_min && fabs(Ele2_SCEta) < eleEta_end2_max ){
        FillUserTH1D("Full5x5SigmaIEtaIEta_Endcap_1stEle_PAS", Ele1_Full5x5SigmaIEtaIEta    , min_prescale * fakeRateEffective   );
      }

      double Ele2_CorrIsolation        = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_CorrIsolation");
      double Ele2_DeltaEtaTrkSC        = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_DeltaEtaTrkSC");
      double Ele2_EcalIsolation        = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_EcalIsolation");
      double Ele2_HcalIsolation        = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_HcalIsolation");
      double Ele2_TrkIsolation         = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_TrkIsolation");
      bool Ele2_HasMatchedPhot         = readerTools_->ReadValueBranch<Bool_t>(ele2KeyName+"_HasMatchedPhot")     ;
      double Ele2_HoE                  = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_HoE");
      double Ele2_LeadVtxDistXY        = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_LeadVtxDistXY");
      double Ele2_LeadVtxDistZ         = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_LeadVtxDistZ");
      int Ele2_MissingHits          = readerTools_->ReadValueBranch<Int_t>(ele2KeyName+"_MissingHits")        ;
      double Ele2_Full5x5SigmaIEtaIEta = readerTools_->ReadValueBranch<Float_t>(ele2KeyName+"_Full5x5SigmaIEtaIEta");
      int Ele2_Charge               = readerTools_->ReadValueBranch<Int_t>(ele2KeyName+"_Charge");

      FillUserTH1D("CorrIsolation_2ndEle_PAS"         , Ele2_CorrIsolation                  , min_prescale * fakeRateEffective   );
      FillUserTH1D("DeltaEtaTrkSC_2ndEle_PAS"         , Ele2_DeltaEtaTrkSC                  , min_prescale * fakeRateEffective   );
      FillUserTH1D("EcalIsolation_2ndEle_PAS"         , Ele2_EcalIsolation                  , min_prescale * fakeRateEffective   );
      FillUserTH1D("HcalIsolation_2ndEle_PAS"         , Ele2_HcalIsolation                  , min_prescale * fakeRateEffective   );
      FillUserTH1D("TrkIsolation_2ndEle_PAS"          , Ele2_TrkIsolation                   , min_prescale * fakeRateEffective   );
      FillUserTH1D("HasMatchedPhot_2ndEle_PAS"        , Ele2_HasMatchedPhot                 , min_prescale * fakeRateEffective   );
      FillUserTH1D("HoE_2ndEle_PAS"                   , Ele2_HoE                            , min_prescale * fakeRateEffective   );
      FillUserTH1D("LeadVtxDistXY_2ndEle_PAS"         , Ele2_LeadVtxDistXY                  , min_prescale * fakeRateEffective   );
      FillUserTH1D("LeadVtxDistZ_2ndEle_PAS"          , Ele2_LeadVtxDistZ                   , min_prescale * fakeRateEffective   );
      FillUserTH1D("MissingHits_2ndEle_PAS"           , Ele2_MissingHits                    , min_prescale * fakeRateEffective   );
      if ( fabs(Ele2_SCEta) < eleEta_bar ) {
        FillUserTH1D("Full5x5SigmaIEtaIEta_Barrel_2ndEle_PAS", Ele2_Full5x5SigmaIEtaIEta    , min_prescale * fakeRateEffective   );
      }
      else if ( fabs(Ele2_SCEta) > eleEta_end1_min && fabs(Ele2_SCEta) < eleEta_end2_max ){
        FillUserTH1D("Full5x5SigmaIEtaIEta_Endcap_2ndEle_PAS", Ele2_Full5x5SigmaIEtaIEta    , min_prescale * fakeRateEffective   );
      }

      //--------------------------------------------------------------------------
      // Preselection histograms
      //--------------------------------------------------------------------------
      double M_j1j2 = readerTools_->ReadValueBranch<Float_t>("M_j1j2");
      double Muon2_Pt = readerTools_->ReadValueBranch<Float_t>("Muon2_Pt");
      double Muon2_Eta = readerTools_->ReadValueBranch<Float_t>("Muon2_Eta");
      double Muon2_Phi = readerTools_->ReadValueBranch<Float_t>("Muon2_Phi");
      int nVertex = readerTools_->ReadValueBranch<Int_t>("nVertex");

      FillUserTH1D( "Ptj1j2_PAS"           , Pt_j1j2                        , min_prescale * fakeRateEffective ) ;
      FillUserTH1D( "Ptee_Minus_Ptj1j2_PAS", Pt_e1e2 - Pt_j1j2              , min_prescale * fakeRateEffective ) ;

      FillUserTH1D("minDR_EleJet_PAS"     , min_DR_EleJet                      , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("DR_Ele1Ele2_PAS"	   , DR_Ele1Ele2                        , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("EleChargeSum_PAS"     , Ele1_Charge + Ele2_Charge, min_prescale * fakeRateEffective ) ;

      FillUserTH1D("nElectron_PAS"        , nEle_ptCut                    , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("nMuon_PAS"            , nMuon_ptCut                        , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("nJet_PAS"             , nJet_ptCut                 , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Pt1stEle_PAS"	   , Ele1_Pt                       , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Eta1stEle_PAS"	   , Ele1_Eta                      , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("SCEta1stEle_PAS"	   , Ele1_SCEta                      , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Phi1stEle_PAS"	   , Ele1_Phi                      , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Pt2ndEle_PAS"	   , Ele2_Pt                       , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Eta2ndEle_PAS"	   , Ele2_Eta                      , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("SCEta2ndEle_PAS"	   , Ele2_SCEta                      , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Phi2ndEle_PAS"	   , Ele2_Phi                      , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Charge1stEle_PAS"	   , Ele1_Charge                   , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Charge2ndEle_PAS"	   , Ele2_Charge                   , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("MET_PAS"              , PFMET_Type1_Pt                  , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("METPhi_PAS"	   , PFMET_Type1_Phi                 , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Pt1stJet_PAS"         , Jet1_Pt                    , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Pt2ndJet_PAS"         , Jet2_Pt                    , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Eta1stJet_PAS"        , Jet1_Eta                   , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Eta2ndJet_PAS"        , Jet2_Eta                   , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Phi1stJet_PAS"	   , Jet1_Phi                   , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Phi2ndJet_PAS"	   , Jet2_Phi                   , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("sTlep_PAS"            , Ele1_Pt + Ele2_Pt        , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("sTjet_PAS"            , Jet1_Pt + Jet2_Pt  , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("sT_PAS"               , sT_eejj                            , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("sT_zjj_PAS"           , sT_zjj                             , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Mjj_PAS"		   , M_j1j2                             , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Mee_PAS"		   , M_e1e2                             , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("MTenu_PAS"            , MT_Ele1MET                         , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Me1j1_PAS"            , M_e1j1                             , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Me1j2_PAS"            , M_e1j2                             , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Me2j1_PAS"            , M_e2j1                             , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Me2j2_PAS"            , M_e2j2                             , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Ptee_PAS"             , Pt_e1e2                            , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("nVertex_PAS"          , nVertex                            , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("DR_Ele1Jet1_PAS"	   , DR_Ele1Jet1                        , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("DR_Ele1Jet2_PAS"	   , DR_Ele1Jet2                        , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("DR_Ele2Jet1_PAS"	   , DR_Ele2Jet1                        , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("DR_Ele2Jet2_PAS"	   , DR_Ele2Jet2                        , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("DR_Jet1Jet2_PAS"	   , DR_Jet1Jet2                        , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Meejj_PAS"            , M_eejj                             , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Meej_PAS"             , M_eej                              , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Mejj_PAS"             , M_ejj                              , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("minDR_ZJet_PAS"       , min_DeltaR_Zj                      , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("DR_ZJet1_PAS"         , DR_ZJ1                             , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("DR_ZJet2_PAS"         , DR_ZJ2                             , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Mej_selected_avg_PAS" , M_ej_avg                           , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Mej_selected_min_PAS" , M_ej_min                           , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Mej_selected_max_PAS" , M_ej_max                           , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Mej_minmax_PAS"       , M_ej_min                           , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Mej_minmax_PAS"       , M_ej_max                           , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Mej_asym_PAS"         , M_ej_asym                        , min_prescale * fakeRateEffective );
      // muon kinematics
      FillUserTH1D("Pt1stMuon_PAS"	   , Muon1_Pt                       , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Eta1stMuon_PAS"	   , Muon1_Eta                      , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Phi1stMuon_PAS"	   , Muon1_Phi                      , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Pt2ndMuon_PAS"	   , Muon2_Pt                       , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Eta2ndMuon_PAS"	   , Muon2_Eta                      , min_prescale * fakeRateEffective ) ;
      FillUserTH1D("Phi2ndMuon_PAS"	   , Muon2_Phi                      , min_prescale * fakeRateEffective ) ;

      FillUserTH2D("MeeVsST_PAS" , M_e1e2, sT_eejj, min_prescale * fakeRateEffective ) ;
      // scale factor dependence histos
      if ( nJet_ptCut == 2 )
        FillUserTH1D("Mee_NJetEq2_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      else if( nJet_ptCut == 3 )
        FillUserTH1D("Mee_NJetEq3_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      else if( nJet_ptCut == 4 )
        FillUserTH1D("Mee_NJetEq4_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      else if( nJet_ptCut == 5 )
        FillUserTH1D("Mee_NJetEq5_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      else if( nJet_ptCut == 6 )
        FillUserTH1D("Mee_NJetEq6_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      else if( nJet_ptCut == 7 )
        FillUserTH1D("Mee_NJetEq7_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      //
      if ( nJet_ptCut >= 3 )
        FillUserTH1D("Mee_NJetGeq3_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      if ( nJet_ptCut >= 4 )
        FillUserTH1D("Mee_NJetGeq4_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      //
      if (sT_eejj >= 300 && sT_eejj < 500)
        FillUserTH1D("Mee_sT300To500_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      else if (sT_eejj >= 500 && sT_eejj < 750)
        FillUserTH1D("Mee_sT500To750_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      else if (sT_eejj >= 750 && sT_eejj < 1250)
        FillUserTH1D("Mee_sT750To1250_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      else if (sT_eejj >= 1250)
        FillUserTH1D("Mee_sT1250ToInf_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      //
      if (M_ej_min >= 100 && M_ej_min < 200)
        FillUserTH1D("Mee_MejMin100To200_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      else if (M_ej_min >= 200 && M_ej_min < 300)
        FillUserTH1D("Mee_MejMin200To300_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      else if (M_ej_min >= 300 && M_ej_min < 400)
        FillUserTH1D("Mee_MejMin300To400_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      else if (M_ej_min >= 400 && M_ej_min < 500)
        FillUserTH1D("Mee_MejMin400To500_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      else if (M_ej_min >= 500 && M_ej_min < 650)
        FillUserTH1D("Mee_MejMin500To650_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      else if (M_ej_min >= 650)
        FillUserTH1D("Mee_MejMin650ToInf_PAS", M_e1e2                         , min_prescale * fakeRateEffective );
      //--------------------------------------------------------------------------
      // no b tags
      //--------------------------------------------------------------------------
      if((isData() && nBJet_ptCut==0) || !isData()) {
        FillUserTH1D("nElectron_noBtaggedJets"        , nEle_ptCut                    , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("nMuon_noBtaggedJets"            , nMuon_ptCut                        , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("nJet_noBtaggedJets"             , nJet_ptCut                 , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt1stEle_noBtaggedJets"	   , Ele1_Pt                       , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Eta1stEle_noBtaggedJets"	   , Ele1_Eta                      , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Phi1stEle_noBtaggedJets"	   , Ele1_Phi                      , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt2ndEle_noBtaggedJets"	   , Ele2_Pt                       , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Eta2ndEle_noBtaggedJets"	   , Ele2_Eta                      , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Phi2ndEle_noBtaggedJets"	   , Ele2_Phi                      , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Charge1stEle_noBtaggedJets"	   , Ele1_Charge                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Charge2ndEle_noBtaggedJets"	   , Ele2_Charge                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("MET_noBtaggedJets"              , PFMET_Type1_Pt                  , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("METPhi_noBtaggedJets"	   , PFMET_Type1_Phi                 , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt1stJet_noBtaggedJets"         , Jet1_Pt                    , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt2ndJet_noBtaggedJets"         , Jet2_Pt                    , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Eta1stJet_noBtaggedJets"        , Jet1_Eta                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Eta2ndJet_noBtaggedJets"        , Jet2_Eta                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Phi1stJet_noBtaggedJets"	   , Jet1_Phi                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Phi2ndJet_noBtaggedJets"	   , Jet2_Phi                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sTlep_noBtaggedJets"            , Ele1_Pt + Ele2_Pt        , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sTjet_noBtaggedJets"            , Jet1_Pt + Jet2_Pt  , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sT_noBtaggedJets"               , sT_eejj                            , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sT_zjj_noBtaggedJets"           , sT_zjj                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mjj_noBtaggedJets"		   , M_j1j2                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mee_noBtaggedJets"		   , M_e1e2                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("MTenu_noBtaggedJets"            , MT_Ele1MET                         , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Me1j1_noBtaggedJets"            , M_e1j1                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Me1j2_noBtaggedJets"            , M_e1j2                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Me2j1_noBtaggedJets"            , M_e2j1                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Me2j2_noBtaggedJets"            , M_e2j2                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_selected_min_noBtaggedJets" , M_ej_min                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_selected_max_noBtaggedJets" , M_ej_max                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_minmax_noBtaggedJets"       , M_ej_min                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_minmax_noBtaggedJets"       , M_ej_max                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_selected_avg_noBtaggedJets" , M_ej_avg                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mejj_noBtaggedJets"             , M_ejj                              , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Meej_noBtaggedJets"             , M_eej                              , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Meejj_noBtaggedJets"            , M_eejj                             , min_prescale * fakeRateEffective ) ;

        FillUserTH1D( "Mee_PAS_noBtaggedJets"      , M_e1e2,  min_prescale * fakeRateEffective * weightZeroBJets ) ;
        if      ( isEBEB ) FillUserTH1D( "Mee_EBEB_PAS_noBtaggedJets"		   , M_e1e2,  min_prescale * fakeRateEffective * weightZeroBJets );
        else if ( isEBEE ) FillUserTH1D( "Mee_EBEE_PAS_noBtaggedJets"		   , M_e1e2,  min_prescale * fakeRateEffective * weightZeroBJets );
        else if ( isEEEE ) FillUserTH1D( "Mee_EEEE_PAS_noBtaggedJets"		   , M_e1e2,  min_prescale * fakeRateEffective * weightZeroBJets );

        if (sT_eejj >= 300 && sT_eejj < 500)
          FillUserTH1D("Mee_sT300To500_PAS_noBtaggedJets", M_e1e2      , min_prescale * fakeRateEffective * weightZeroBJets );
        else if (sT_eejj >= 500 && sT_eejj < 750)
          FillUserTH1D("Mee_sT500To750_PAS_noBtaggedJets", M_e1e2      , min_prescale * fakeRateEffective * weightZeroBJets );
        else if (sT_eejj >= 750 && sT_eejj < 1250)
          FillUserTH1D("Mee_sT750To1250_PAS_noBtaggedJets", M_e1e2     , min_prescale * fakeRateEffective * weightZeroBJets );
        else if (sT_eejj >= 1250)
          FillUserTH1D("Mee_sT1250ToInf_PAS_noBtaggedJets", M_e1e2     , min_prescale * fakeRateEffective * weightZeroBJets );

        if (M_ej_min >= 100 && M_ej_min < 200)
          FillUserTH1D("Mee_MejMin100To200_PAS_noBtaggedJets", M_e1e2  , min_prescale * fakeRateEffective * weightZeroBJets );
        else if (M_ej_min >= 200 && M_ej_min < 300)
          FillUserTH1D("Mee_MejMin200To300_PAS_noBtaggedJets", M_e1e2  , min_prescale * fakeRateEffective * weightZeroBJets );
        else if (M_ej_min >= 300 && M_ej_min < 400)
          FillUserTH1D("Mee_MejMin300To400_PAS_noBtaggedJets", M_e1e2  , min_prescale * fakeRateEffective * weightZeroBJets );
        else if (M_ej_min >= 400 && M_ej_min < 500)
          FillUserTH1D("Mee_MejMin400To500_PAS_noBtaggedJets", M_e1e2  , min_prescale * fakeRateEffective * weightZeroBJets );
        else if (M_ej_min >= 500 && M_ej_min < 650)
          FillUserTH1D("Mee_MejMin500To650_PAS_noBtaggedJets", M_e1e2  , min_prescale * fakeRateEffective * weightZeroBJets );
        else if (M_ej_min >= 650)
          FillUserTH1D("Mee_MejMin650ToInf_PAS_noBtaggedJets", M_e1e2  , min_prescale * fakeRateEffective * weightZeroBJets );
      }
      if(nBJet_ptCut>=1) {
        FillUserTH1D("nElectron_gteOneBtaggedJet"        , nEle_ptCut                    , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("nMuon_gteOneBtaggedJet"            , nMuon_ptCut                        , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("nJet_gteOneBtaggedJet"             , nJet_ptCut                 , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt1stEle_gteOneBtaggedJet"	   , Ele1_Pt                       , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Eta1stEle_gteOneBtaggedJet"	   , Ele1_Eta                      , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Phi1stEle_gteOneBtaggedJet"	   , Ele1_Phi                      , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt2ndEle_gteOneBtaggedJet"	   , Ele2_Pt                       , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Eta2ndEle_gteOneBtaggedJet"	   , Ele2_Eta                      , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Phi2ndEle_gteOneBtaggedJet"	   , Ele2_Phi                      , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Charge1stEle_gteOneBtaggedJet"	   , Ele1_Charge                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Charge2ndEle_gteOneBtaggedJet"	   , Ele2_Charge                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("MET_gteOneBtaggedJet"              , PFMET_Type1_Pt                  , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("METPhi_gteOneBtaggedJet"	   , PFMET_Type1_Phi                 , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt1stJet_gteOneBtaggedJet"         , Jet1_Pt                    , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt2ndJet_gteOneBtaggedJet"         , Jet2_Pt                    , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Eta1stJet_gteOneBtaggedJet"        , Jet1_Eta                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Eta2ndJet_gteOneBtaggedJet"        , Jet2_Eta                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Phi1stJet_gteOneBtaggedJet"	   , Jet1_Phi                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Phi2ndJet_gteOneBtaggedJet"	   , Jet2_Phi                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sTlep_gteOneBtaggedJet"            , Ele1_Pt + Ele2_Pt        , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sTjet_gteOneBtaggedJet"            , Jet1_Pt + Jet2_Pt  , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sT_gteOneBtaggedJet"               , sT_eejj                            , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sT_zjj_gteOneBtaggedJet"           , sT_zjj                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mjj_gteOneBtaggedJet"		   , M_j1j2                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mee_gteOneBtaggedJet"		   , M_e1e2                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("MTenu_gteOneBtaggedJet"            , MT_Ele1MET                         , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Me1j1_gteOneBtaggedJet"            , M_e1j1                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Me1j2_gteOneBtaggedJet"            , M_e1j2                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Me2j1_gteOneBtaggedJet"            , M_e2j1                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Me2j2_gteOneBtaggedJet"            , M_e2j2                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_selected_min_gteOneBtaggedJet" , M_ej_min                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_selected_max_gteOneBtaggedJet" , M_ej_max                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_minmax_gteOneBtaggedJet"       , M_ej_min                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_minmax_gteOneBtaggedJet"       , M_ej_max                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_selected_avg_gteOneBtaggedJet" , M_ej_avg                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mejj_gteOneBtaggedJet"             , M_ejj                              , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Meej_gteOneBtaggedJet"             , M_eej                              , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Meejj_gteOneBtaggedJet"            , M_eejj                             , min_prescale * fakeRateEffective ) ;

        FillUserTH1D( "Mee_PAS_gteOneBtaggedJet"      , M_e1e2,  min_prescale * fakeRateEffective * weightAtLeastOneBJet ) ;
        if      ( isEBEB ) FillUserTH1D( "Mee_EBEB_PAS_gteOneBtaggedJet"		   , M_e1e2,  min_prescale * fakeRateEffective * weightAtLeastOneBJet );
        else if ( isEBEE ) FillUserTH1D( "Mee_EBEE_PAS_gteOneBtaggedJet"		   , M_e1e2,  min_prescale * fakeRateEffective * weightAtLeastOneBJet );
        else if ( isEEEE ) FillUserTH1D( "Mee_EEEE_PAS_gteOneBtaggedJet"		   , M_e1e2,  min_prescale * fakeRateEffective * weightAtLeastOneBJet );

        if (sT_eejj >= 300 && sT_eejj < 500)
          FillUserTH1D("Mee_sT300To500_PAS_gteOneBtaggedJet", M_e1e2      , min_prescale * fakeRateEffective * weightAtLeastOneBJet );
        else if (sT_eejj >= 500 && sT_eejj < 750)
          FillUserTH1D("Mee_sT500To750_PAS_gteOneBtaggedJet", M_e1e2      , min_prescale * fakeRateEffective * weightAtLeastOneBJet );
        else if (sT_eejj >= 750 && sT_eejj < 1250)
          FillUserTH1D("Mee_sT750To1250_PAS_gteOneBtaggedJet", M_e1e2     , min_prescale * fakeRateEffective * weightAtLeastOneBJet );
        else if (sT_eejj >= 1250)
          FillUserTH1D("Mee_sT1250ToInf_PAS_gteOneBtaggedJet", M_e1e2     , min_prescale * fakeRateEffective * weightAtLeastOneBJet );

        if (M_ej_min >= 100 && M_ej_min < 200)
          FillUserTH1D("Mee_MejMin100To200_PAS_gteOneBtaggedJet", M_e1e2  , min_prescale * fakeRateEffective * weightAtLeastOneBJet );
        else if (M_ej_min >= 200 && M_ej_min < 300)
          FillUserTH1D("Mee_MejMin200To300_PAS_gteOneBtaggedJet", M_e1e2  , min_prescale * fakeRateEffective * weightAtLeastOneBJet );
        else if (M_ej_min >= 300 && M_ej_min < 400)
          FillUserTH1D("Mee_MejMin300To400_PAS_gteOneBtaggedJet", M_e1e2  , min_prescale * fakeRateEffective * weightAtLeastOneBJet );
        else if (M_ej_min >= 400 && M_ej_min < 500)
          FillUserTH1D("Mee_MejMin400To500_PAS_gteOneBtaggedJet", M_e1e2  , min_prescale * fakeRateEffective * weightAtLeastOneBJet );
        else if (M_ej_min >= 500 && M_ej_min < 650)
          FillUserTH1D("Mee_MejMin500To650_PAS_gteOneBtaggedJet", M_e1e2  , min_prescale * fakeRateEffective * weightAtLeastOneBJet );
        else if (M_ej_min >= 650)
          FillUserTH1D("Mee_MejMin650ToInf_PAS_gteOneBtaggedJet", M_e1e2  , min_prescale * fakeRateEffective * weightAtLeastOneBJet );
      }
      if(nBJet_ptCut>=2) {
        FillUserTH1D("nElectron_gteTwoBtaggedJets"        , nEle_ptCut                    , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("nMuon_gteTwoBtaggedJets"            , nMuon_ptCut                        , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("nJet_gteTwoBtaggedJets"             , nJet_ptCut                 , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt1stEle_gteTwoBtaggedJets"	   , Ele1_Pt                       , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Eta1stEle_gteTwoBtaggedJets"	   , Ele1_Eta                      , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Phi1stEle_gteTwoBtaggedJets"	   , Ele1_Phi                      , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt2ndEle_gteTwoBtaggedJets"	   , Ele2_Pt                       , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Eta2ndEle_gteTwoBtaggedJets"	   , Ele2_Eta                      , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Phi2ndEle_gteTwoBtaggedJets"	   , Ele2_Phi                      , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Charge1stEle_gteTwoBtaggedJets"	   , Ele1_Charge                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Charge2ndEle_gteTwoBtaggedJets"	   , Ele2_Charge                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("MET_gteTwoBtaggedJets"              , PFMET_Type1_Pt                  , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("METPhi_gteTwoBtaggedJets"	   , PFMET_Type1_Phi                 , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt1stJet_gteTwoBtaggedJets"         , Jet1_Pt                    , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt2ndJet_gteTwoBtaggedJets"         , Jet2_Pt                    , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Eta1stJet_gteTwoBtaggedJets"        , Jet1_Eta                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Eta2ndJet_gteTwoBtaggedJets"        , Jet2_Eta                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Phi1stJet_gteTwoBtaggedJets"	   , Jet1_Phi                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Phi2ndJet_gteTwoBtaggedJets"	   , Jet2_Phi                   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sTlep_gteTwoBtaggedJets"            , Ele1_Pt + Ele2_Pt        , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sTjet_gteTwoBtaggedJets"            , Jet1_Pt + Jet2_Pt  , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sT_gteTwoBtaggedJets"               , sT_eejj                            , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sT_zjj_gteTwoBtaggedJets"           , sT_zjj                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mjj_gteTwoBtaggedJets"		   , M_j1j2                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mee_gteTwoBtaggedJets"		   , M_e1e2                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("MTenu_gteTwoBtaggedJets"            , MT_Ele1MET                         , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Me1j1_gteTwoBtaggedJets"            , M_e1j1                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Me1j2_gteTwoBtaggedJets"            , M_e1j2                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Me2j1_gteTwoBtaggedJets"            , M_e2j1                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Me2j2_gteTwoBtaggedJets"            , M_e2j2                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_selected_min_gteTwoBtaggedJets" , M_ej_min                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_selected_max_gteTwoBtaggedJets" , M_ej_max                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_minmax_gteTwoBtaggedJets"       , M_ej_min                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_minmax_gteTwoBtaggedJets"       , M_ej_max                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_selected_avg_gteTwoBtaggedJets" , M_ej_avg                           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mejj_gteTwoBtaggedJets"             , M_ejj                              , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Meej_gteTwoBtaggedJets"             , M_eej                              , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Meejj_gteTwoBtaggedJets"            , M_eejj                             , min_prescale * fakeRateEffective ) ;

        FillUserTH1D( "Mee_PAS_gteTwoBtaggedJets"      , M_e1e2,  min_prescale * fakeRateEffective * weightAtLeastTwoBJets ) ;
        if      ( isEBEB ) FillUserTH1D( "Mee_EBEB_PAS_gteTwoBtaggedJets"		   , M_e1e2,  min_prescale * fakeRateEffective * weightAtLeastTwoBJets );
        else if ( isEBEE ) FillUserTH1D( "Mee_EBEE_PAS_gteTwoBtaggedJets"		   , M_e1e2,  min_prescale * fakeRateEffective * weightAtLeastTwoBJets );
        else if ( isEEEE ) FillUserTH1D( "Mee_EEEE_PAS_gteTwoBtaggedJets"		   , M_e1e2,  min_prescale * fakeRateEffective * weightAtLeastTwoBJets );

        if (sT_eejj >= 300 && sT_eejj < 500)
          FillUserTH1D("Mee_sT300To500_PAS_gteTwoBtaggedJets", M_e1e2      , min_prescale * fakeRateEffective * weightAtLeastTwoBJets );
        else if (sT_eejj >= 500 && sT_eejj < 750)
          FillUserTH1D("Mee_sT500To750_PAS_gteTwoBtaggedJets", M_e1e2      , min_prescale * fakeRateEffective * weightAtLeastTwoBJets );
        else if (sT_eejj >= 750 && sT_eejj < 1250)
          FillUserTH1D("Mee_sT750To1250_PAS_gteTwoBtaggedJets", M_e1e2     , min_prescale * fakeRateEffective * weightAtLeastTwoBJets );
        else if (sT_eejj >= 1250)
          FillUserTH1D("Mee_sT1250ToInf_PAS_gteTwoBtaggedJets", M_e1e2     , min_prescale * fakeRateEffective * weightAtLeastTwoBJets );

        if (M_ej_min >= 100 && M_ej_min < 200)
          FillUserTH1D("Mee_MejMin100To200_PAS_gteTwoBtaggedJets", M_e1e2  , min_prescale * fakeRateEffective * weightAtLeastTwoBJets );
        else if (M_ej_min >= 200 && M_ej_min < 300)
          FillUserTH1D("Mee_MejMin200To300_PAS_gteTwoBtaggedJets", M_e1e2  , min_prescale * fakeRateEffective * weightAtLeastTwoBJets );
        else if (M_ej_min >= 300 && M_ej_min < 400)
          FillUserTH1D("Mee_MejMin300To400_PAS_gteTwoBtaggedJets", M_e1e2  , min_prescale * fakeRateEffective * weightAtLeastTwoBJets );
        else if (M_ej_min >= 400 && M_ej_min < 500)
          FillUserTH1D("Mee_MejMin400To500_PAS_gteTwoBtaggedJets", M_e1e2  , min_prescale * fakeRateEffective * weightAtLeastTwoBJets );
        else if (M_ej_min >= 500 && M_ej_min < 650)
          FillUserTH1D("Mee_MejMin500To650_PAS_gteTwoBtaggedJets", M_e1e2  , min_prescale * fakeRateEffective * weightAtLeastTwoBJets );
        else if (M_ej_min >= 650)
          FillUserTH1D("Mee_MejMin650ToInf_PAS_gteTwoBtaggedJets", M_e1e2  , min_prescale * fakeRateEffective * weightAtLeastTwoBJets );
      }
      FillUserTH3D("OptimizationCutSpace",sT_eejj,M_ej_min,M_e1e2, min_prescale * fakeRateEffective );

      //--------------------------------------------------------------------------
      // Mass-pairing histograms at preselection
      //--------------------------------------------------------------------------

      if ( fabs(M_e1j1-M_e2j2) < fabs(M_e1j2-M_e2j1) )  {
        FillUserTH1D("Me1j_selected_PAS"   , M_e1j1,         min_prescale * fakeRateEffective );
        FillUserTH1D("Me2j_selected_PAS"   , M_e2j2,         min_prescale * fakeRateEffective );
        FillUserTH2D("Me1jVsMe2j_selected" , M_e1j1, M_e2j2, min_prescale * fakeRateEffective );
        FillUserTH2D("Me1jVsMe2j_rejected" , M_e1j2, M_e2j1, min_prescale * fakeRateEffective );
      }
      else {
        FillUserTH1D("Me1j_selected_PAS"   , M_e1j2,         min_prescale * fakeRateEffective );
        FillUserTH1D("Me2j_selected_PAS"   , M_e2j1,         min_prescale * fakeRateEffective );
        FillUserTH2D("Me1jVsMe2j_selected" , M_e1j2, M_e2j1, min_prescale * fakeRateEffective );
        FillUserTH2D("Me1jVsMe2j_rejected" , M_e1j1, M_e2j2, min_prescale * fakeRateEffective );
      }

      //--------------------------------------------------------------------------
      // Preselection + N(Jet) > 2
      //--------------------------------------------------------------------------

      if ( nJet_ptCut > 2 ){
        FillUserTH1D( "M_e1j3_PAS"  , M_e1j3, min_prescale * fakeRateEffective  );
        FillUserTH1D( "M_e2j3_PAS"  , M_e2j3, min_prescale * fakeRateEffective  );
        FillUserTH1D( "M_j1j3_PAS"  , M_j1j3, min_prescale * fakeRateEffective  );
        FillUserTH1D( "M_j2j3_PAS"  , M_j2j3, min_prescale * fakeRateEffective  );
        FillUserTH1D( "M_eejjj_PAS" , M_eejjj,min_prescale * fakeRateEffective  );

        FillUserTH1D( "Ptj1j2j3_PAS"            , Pt_j1j2j3           , min_prescale * fakeRateEffective ) ;
        FillUserTH1D( "Ptj2j3_PAS"              , Pt_j2j3             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D( "Ptj1j3_PAS"              , Pt_j1j3             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D( "Ptee_Minus_Ptj1j2j3_PAS" , Pt_e1e2 - Pt_j1j2j3 , min_prescale * fakeRateEffective ) ;
      }

      //--------------------------------------------------------------------------
      // Preselection + event type (EBEB, EEEB, EEEE, etc)
      //--------------------------------------------------------------------------

      if      ( isEB   ) FillUserTH1D( "Mee_EB_PAS"  , M_e1e2, min_prescale * fakeRateEffective  );
      if      ( isEBEB ) FillUserTH1D( "Mee_EBEB_PAS", M_e1e2, min_prescale * fakeRateEffective  );
      else if ( isEBEE ) FillUserTH1D( "Mee_EBEE_PAS", M_e1e2, min_prescale * fakeRateEffective  );
      else if ( isEEEE ) FillUserTH1D( "Mee_EEEE_PAS", M_e1e2, min_prescale * fakeRateEffective  );
      if      ( isEnd2End2 ) FillUserTH1D( "Mee_End2End2_PAS", M_e1e2, min_prescale * fakeRateEffective );

      //--------------------------------------------------------------------------
      // Preselection + high ST plot
      //--------------------------------------------------------------------------

      if ( sT_eejj > 445. ) FillUserTH1D( "Mee_PASandST445", M_e1e2, min_prescale * fakeRateEffective ) ;

      //--------------------------------------------------------------------------
      // High M(ee) plots
      //--------------------------------------------------------------------------

      if ( M_e1e2 > 100. ) FillUserTH1D("sT_PASandMee100"   , sT_eejj , min_prescale * fakeRateEffective  );
      if ( M_e1e2 > 110. ) FillUserTH1D("sT_PASandMee110"   , sT_eejj , min_prescale * fakeRateEffective  );
      if ( M_e1e2 > 120. ) FillUserTH1D("sT_PASandMee120"   , sT_eejj , min_prescale * fakeRateEffective  );
      if ( M_e1e2 > 130. ) FillUserTH1D("sT_PASandMee130"   , sT_eejj , min_prescale * fakeRateEffective  );
      if ( M_e1e2 > 140. ) FillUserTH1D("sT_PASandMee140"   , sT_eejj , min_prescale * fakeRateEffective  );
      if ( M_e1e2 > 150. ) FillUserTH1D("sT_PASandMee150"   , sT_eejj , min_prescale * fakeRateEffective  );
      if ( M_e1e2 > 160. ) FillUserTH1D("sT_PASandMee160"   , sT_eejj , min_prescale * fakeRateEffective  );
      if ( M_e1e2 > 170. ) FillUserTH1D("sT_PASandMee170"   , sT_eejj , min_prescale * fakeRateEffective  );
      if ( M_e1e2 > 180. ) FillUserTH1D("sT_PASandMee180"   , sT_eejj , min_prescale * fakeRateEffective  );
      if ( M_e1e2 > 190. ) FillUserTH1D("sT_PASandMee190"   , sT_eejj , min_prescale * fakeRateEffective  );
      if ( M_e1e2 > 200. ) FillUserTH1D("sT_PASandMee200"   , sT_eejj , min_prescale * fakeRateEffective  );


      if ( M_e1e2 > 100. ) {

        FillUserTH1D("CorrIsolation_1stEle_PASandMee100"         , Ele1_CorrIsolation                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("DeltaEtaTrkSC_1stEle_PASandMee100"         , Ele1_DeltaEtaTrkSC                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("EcalIsolation_1stEle_PASandMee100"         , Ele1_EcalIsolation                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("HcalIsolation_1stEle_PASandMee100"         , Ele1_HcalIsolation                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("TrkIsolation_1stEle_PASandMee100"          , Ele1_TrkIsolation                   , min_prescale * fakeRateEffective   );
        FillUserTH1D("HasMatchedPhot_1stEle_PASandMee100"        , Ele1_HasMatchedPhot                 , min_prescale * fakeRateEffective   );
        FillUserTH1D("HoE_1stEle_PASandMee100"                   , Ele1_HoE                            , min_prescale * fakeRateEffective   );
        FillUserTH1D("LeadVtxDistXY_1stEle_PASandMee100"         , Ele1_LeadVtxDistXY                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("LeadVtxDistZ_1stEle_PASandMee100"          , Ele1_LeadVtxDistZ                   , min_prescale * fakeRateEffective   );
        FillUserTH1D("MissingHits_1stEle_PASandMee100"           , Ele1_MissingHits                    , min_prescale * fakeRateEffective   );
        if ( fabs(Ele1_SCEta) < eleEta_bar ) {
          FillUserTH1D("Full5x5SigmaIEtaIEta_Barrel_1stEle_PASandMee100", Ele1_Full5x5SigmaIEtaIEta    , min_prescale * fakeRateEffective   );
        }
        else if ( fabs(Ele1_SCEta) > eleEta_end1_min && fabs(Ele2_SCEta) < eleEta_end2_max ){
          FillUserTH1D("Full5x5SigmaIEtaIEta_Endcap_1stEle_PASandMee100", Ele1_Full5x5SigmaIEtaIEta    , min_prescale * fakeRateEffective   );
        }

        FillUserTH1D("CorrIsolation_2ndEle_PASandMee100"         , Ele2_CorrIsolation                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("DeltaEtaTrkSC_2ndEle_PASandMee100"         , Ele2_DeltaEtaTrkSC                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("EcalIsolation_2ndEle_PASandMee100"         , Ele2_EcalIsolation                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("HcalIsolation_2ndEle_PASandMee100"         , Ele2_HcalIsolation                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("TrkIsolation_2ndEle_PASandMee100"          , Ele2_TrkIsolation                   , min_prescale * fakeRateEffective   );
        FillUserTH1D("HasMatchedPhot_2ndEle_PASandMee100"        , Ele2_HasMatchedPhot                 , min_prescale * fakeRateEffective   );
        FillUserTH1D("HoE_2ndEle_PASandMee100"                   , Ele2_HoE                            , min_prescale * fakeRateEffective   );
        FillUserTH1D("LeadVtxDistXY_2ndEle_PASandMee100"         , Ele2_LeadVtxDistXY                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("LeadVtxDistZ_2ndEle_PASandMee100"          , Ele2_LeadVtxDistZ                   , min_prescale * fakeRateEffective   );
        FillUserTH1D("MissingHits_2ndEle_PASandMee100"           , Ele2_MissingHits                    , min_prescale * fakeRateEffective   );
        if ( fabs(Ele2_SCEta) < eleEta_bar ) {
          FillUserTH1D("Full5x5SigmaIEtaIEta_Barrel_2ndEle_PASandMee100", Ele2_Full5x5SigmaIEtaIEta    , min_prescale * fakeRateEffective   );
        }
        else if ( fabs(Ele2_SCEta) > eleEta_end1_min && fabs(Ele2_SCEta) < eleEta_end2_max ){
          FillUserTH1D("Full5x5SigmaIEtaIEta_Endcap_2ndEle_PASandMee100", Ele2_Full5x5SigmaIEtaIEta    , min_prescale * fakeRateEffective   );
        }

        FillUserTH1D("Me1j1_PASandMee100"           , M_e1j1                              , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Ptee_PASandMee100"            , Pt_e1e2                             , min_prescale * fakeRateEffective ) ;
        FillUserTH2D("MeeVsST_PASandMee100" , M_e1e2, sT_eejj, min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sT_zjj_PASandMee100"          , sT_zjj                              , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("nVertex_PASandMee100"         , nVertex                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sT_PASandMee100"              , sT_eejj                             , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("EleChargeSum_PASandMee100"    , Ele1_Charge + Ele2_Charge , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("nJet_PASandMee100"            , nJet_ptCut                  , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sTlep_PASandMee100"           , Ele1_Pt    + Ele2_Pt      , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sTjet_PASandMee100"           , Jet1_Pt + Jet2_Pt   , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mjj_PASandMee100"             , M_j1j2                              , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt1stEle_PASandMee100"        , Ele1_Pt                        , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt2ndEle_PASandMee100"        , Ele2_Pt                        , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt1stJet_PASandMee100"        , Jet1_Pt                     , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Pt2ndJet_PASandMee100"        , Jet2_Pt                     , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Mej_selected_avg_PASandMee100", M_ej_avg                            , min_prescale * fakeRateEffective ) ;

        FillUserTH1D("sTfrac_Jet1_PASandMee100"     , Jet1_Pt / sT_eejj                       , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sTfrac_Jet2_PASandMee100"     , Jet2_Pt / sT_eejj                       , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sTfrac_Ele1_PASandMee100"     , Ele1_Pt / sT_eejj                          , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sTfrac_Ele2_PASandMee100"     , Ele2_Pt / sT_eejj                          , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sTfrac_Jet_PASandMee100"      , ( Jet1_Pt + Jet2_Pt ) / sT_eejj , min_prescale * fakeRateEffective ) ;
        FillUserTH1D("sTfrac_Ele_PASandMee100"      , ( Ele1_Pt + Ele2_Pt ) / sT_eejj       , min_prescale * fakeRateEffective ) ;

        FillUserTH1D("Ptj1j2_PASandMee100"            , Pt_j1j2                        ,  min_prescale * fakeRateEffective ) ;
        FillUserTH1D("Ptee_Minus_Ptj1j2_PASandMee100" , Pt_e1e2 - Pt_j1j2              ,  min_prescale * fakeRateEffective ) ;

        if ( nJet_ptCut > 2 ) {
          FillUserTH1D( "M_j1j3_PASandMee100" , M_j1j3, min_prescale * fakeRateEffective ) ;
          FillUserTH1D( "M_j2j3_PASandMee100" , M_j2j3, min_prescale * fakeRateEffective ) ;
          FillUserTH1D( "M_e1j3_PASandMee100" , M_e1j3, min_prescale * fakeRateEffective ) ;
          FillUserTH1D( "M_e2j3_PASandMee100" , M_e2j3, min_prescale * fakeRateEffective ) ;
          FillUserTH1D( "M_eejjj_PASandMee100", M_eejjj,min_prescale * fakeRateEffective ) ;

          FillUserTH1D( "Ptj1j2j3_PASandMee100"            , Pt_j1j2j3           , min_prescale * fakeRateEffective ) ;
          FillUserTH1D( "Ptj2j3_PASandMee100"              , Pt_j2j3             , min_prescale * fakeRateEffective ) ;
          FillUserTH1D( "Ptj1j3_PASandMee100"              , Pt_j1j3             , min_prescale * fakeRateEffective ) ;
          FillUserTH1D( "Ptee_Minus_Ptj1j2j3_PASandMee100" , Pt_e1e2 - Pt_j1j2j3 , min_prescale * fakeRateEffective ) ;
        }
      }

      //--------------------------------------------------------------------------
      // Preselection + M(ee) normalization region plots
      //--------------------------------------------------------------------------

      if ( M_e1e2 > 80.0 && M_e1e2 < 100.0 ){
        FillUserTH1D("Mee_80_100_Preselection", M_e1e2, min_prescale * fakeRateEffective ) ;
        if      ( isEBEB ) FillUserTH1D( "Mee_EBEB_80_100_PAS", M_e1e2, min_prescale * fakeRateEffective  );
        else if ( isEBEE ) FillUserTH1D( "Mee_EBEE_80_100_PAS", M_e1e2, min_prescale * fakeRateEffective  );
        else if ( isEEEE ) FillUserTH1D( "Mee_EEEE_80_100_PAS", M_e1e2, min_prescale * fakeRateEffective  );
        if      ( isEB   ) FillUserTH1D( "Mee_EB_80_100_PAS"  , M_e1e2, min_prescale * fakeRateEffective  );
      }

      if ( M_e1e2 > 70.0 && M_e1e2 < 110.0 ){
        FillUserTH1D("Mee_70_110_Preselection", M_e1e2, min_prescale * fakeRateEffective ) ;
        if ( sT_eejj > 600 ) 	 FillUserTH1D("Mee_70_110_ST600_Preselection", M_e1e2, min_prescale * fakeRateEffective ) ;
        if      ( isEBEB ) FillUserTH1D( "Mee_EBEB_70_110_PAS", M_e1e2, min_prescale * fakeRateEffective  );
        else if ( isEBEE ) FillUserTH1D( "Mee_EBEE_70_110_PAS", M_e1e2, min_prescale * fakeRateEffective  );
        else if ( isEEEE ) FillUserTH1D( "Mee_EEEE_70_110_PAS", M_e1e2, min_prescale * fakeRateEffective  );
        if      ( isEB   ) FillUserTH1D( "Mee_EB_70_110_PAS"  , M_e1e2, min_prescale * fakeRateEffective  );
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
          FillUserHist(cut_name, bdtOutput, min_prescale * fakeRateEffective );
          sprintf(cut_name, "BDTOutput_noWeight_TrainRegion_LQ%d", lq_mass );
          FillUserHist(cut_name, bdtOutput );
        }
      }

      //--------------------------------------------------------------------------
      // Region of interest plots
      //--------------------------------------------------------------------------

      if ( do_roi_plots && passed_region_of_interest ) {

        FillUserTH1D("CorrIsolation_1stEle_ROI"         , Ele1_CorrIsolation                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("DeltaEtaTrkSC_1stEle_ROI"         , Ele1_DeltaEtaTrkSC                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("EcalIsolation_1stEle_ROI"         , Ele1_EcalIsolation                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("HcalIsolation_1stEle_ROI"         , Ele1_HcalIsolation                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("TrkIsolation_1stEle_ROI"          , Ele1_TrkIsolation                   , min_prescale * fakeRateEffective   );
        FillUserTH1D("HasMatchedPhot_1stEle_ROI"        , Ele1_HasMatchedPhot                 , min_prescale * fakeRateEffective   );
        FillUserTH1D("HoE_1stEle_ROI"                   , Ele1_HoE                            , min_prescale * fakeRateEffective   );
        FillUserTH1D("LeadVtxDistXY_1stEle_ROI"         , Ele1_LeadVtxDistXY                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("LeadVtxDistZ_1stEle_ROI"          , Ele1_LeadVtxDistZ                   , min_prescale * fakeRateEffective   );
        FillUserTH1D("MissingHits_1stEle_ROI"           , Ele1_MissingHits                    , min_prescale * fakeRateEffective   );
        if ( fabs(Ele1_SCEta) < eleEta_bar ) {
          FillUserTH1D("SigmaIEtaIEta_Barrel_1stEle_ROI", Ele1_Full5x5SigmaIEtaIEta                  , min_prescale * fakeRateEffective   );
        }
        else if ( fabs(Ele1_SCEta) > eleEta_end1_min && fabs(Ele2_SCEta) > eleEta_end2_max ){
          FillUserTH1D("SigmaIEtaIEta_Endcap_1stEle_ROI", Ele1_Full5x5SigmaIEtaIEta                  , min_prescale * fakeRateEffective   );
        }

        FillUserTH1D("CorrIsolation_2ndEle_ROI"         , Ele2_CorrIsolation                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("DeltaEtaTrkSC_2ndEle_ROI"         , Ele2_DeltaEtaTrkSC                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("EcalIsolation_2ndEle_ROI"         , Ele2_EcalIsolation                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("HcalIsolation_2ndEle_ROI"         , Ele2_HcalIsolation                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("TrkIsolation_2ndEle_ROI"          , Ele2_TrkIsolation                   , min_prescale * fakeRateEffective   );
        FillUserTH1D("HasMatchedPhot_2ndEle_ROI"        , Ele2_HasMatchedPhot                 , min_prescale * fakeRateEffective   );
        FillUserTH1D("HoE_2ndEle_ROI"                   , Ele2_HoE                            , min_prescale * fakeRateEffective   );
        FillUserTH1D("LeadVtxDistXY_2ndEle_ROI"         , Ele2_LeadVtxDistXY                  , min_prescale * fakeRateEffective   );
        FillUserTH1D("LeadVtxDistZ_2ndEle_ROI"          , Ele2_LeadVtxDistZ                   , min_prescale * fakeRateEffective   );
        FillUserTH1D("MissingHits_2ndEle_ROI"           , Ele2_MissingHits                    , min_prescale * fakeRateEffective   );
        if ( fabs(Ele2_Eta) < eleEta_bar ) {
          FillUserTH1D("SigmaIEtaIEta_Barrel_2ndEle_ROI", Ele2_Full5x5SigmaIEtaIEta                  , min_prescale * fakeRateEffective   );
        }
        else if ( fabs(Ele2_Eta) > eleEta_end1_min && fabs(Ele2_Eta) < eleEta_end2_max ){
          FillUserTH1D("SigmaIEtaIEta_Endcap_2ndEle_ROI", Ele2_Full5x5SigmaIEtaIEta                  , min_prescale * fakeRateEffective   );
        }

        FillUserTH1D("Me1j1_ROI"           , M_e1j1                                         , min_prescale * fakeRateEffective );
        FillUserTH1D("Ptee_ROI"            , Pt_e1e2                                        , min_prescale * fakeRateEffective );
        FillUserTH1D("Eta1stJet_ROI"       , Jet1_Eta                               , min_prescale * fakeRateEffective );
        FillUserTH1D("Eta2ndJet_ROI"       , Jet2_Eta                               , min_prescale * fakeRateEffective );
        FillUserTH1D("Eta1stEle_ROI"	    , Ele1_SCEta                                  , min_prescale * fakeRateEffective );
        FillUserTH1D("Eta2ndEle_ROI"	    , Ele2_SCEta                                  , min_prescale * fakeRateEffective );
        FillUserTH1D("Phi1stJet_ROI"       , Jet1_Phi                               , min_prescale * fakeRateEffective );
        FillUserTH1D("Phi2ndJet_ROI"       , Jet2_Phi                               , min_prescale * fakeRateEffective );
        FillUserTH1D("Phi1stEle_ROI"	    , Ele1_Phi                                  , min_prescale * fakeRateEffective );
        FillUserTH1D("Phi2ndEle_ROI"	    , Ele2_Phi                                  , min_prescale * fakeRateEffective );
        FillUserTH2D("MeeVsST_ROI"         , M_e1e2                                , sT_eejj, min_prescale * fakeRateEffective );
        FillUserTH1D("Mee_ROI"		    , M_e1e2                                         , min_prescale * fakeRateEffective );
        FillUserTH1D("sT_zjj_ROI"          , sT_zjj                                         , min_prescale * fakeRateEffective );
        FillUserTH1D("nVertex_ROI"         , nVertex                                        , min_prescale * fakeRateEffective );
        FillUserTH1D("EleChargeSum_ROI"    , Ele1_Charge + Ele2_Charge            , min_prescale * fakeRateEffective );
        FillUserTH1D("nJet_ROI"            , nJet_ptCut                             , min_prescale * fakeRateEffective );
        FillUserTH1D("Mej_selected_avg_ROI", M_ej_avg                                       , min_prescale * fakeRateEffective );
        FillUserTH1D("Meejj_ROI"           , M_eejj                                         , min_prescale * fakeRateEffective );
        FillUserTH1D("Meej_ROI"            , M_eej                                          , min_prescale * fakeRateEffective );
        FillUserTH1D("Mejj_ROI"            , M_ejj                                          , min_prescale * fakeRateEffective );
        FillUserTH1D("minDR_ZJet_ROI"      , min_DeltaR_Zj                                  , min_prescale * fakeRateEffective );
        FillUserTH1D("DR_ZJet1_ROI"        , DR_ZJ1                                         , min_prescale * fakeRateEffective );
        FillUserTH1D("DR_ZJet2_ROI"        , DR_ZJ2                                         , min_prescale * fakeRateEffective );
        FillUserTH1D("MET_ROI"             , PFMET_Type1_Pt                              , min_prescale * fakeRateEffective );
        FillUserTH1D("Mjj_ROI"             , M_j1j2                                         , min_prescale * fakeRateEffective );
        FillUserTH1D("sT_ROI"              , sT_eejj                                        , min_prescale * fakeRateEffective );
        FillUserTH1D("sTlep_ROI"           , Ele1_Pt    + Ele2_Pt                 , min_prescale * fakeRateEffective );
        FillUserTH1D("sTjet_ROI"           , Jet1_Pt + Jet2_Pt              , min_prescale * fakeRateEffective );
        FillUserTH1D("Pt1stEle_ROI"        , Ele1_Pt                                   , min_prescale * fakeRateEffective );
        FillUserTH1D("Pt2ndEle_ROI"        , Ele2_Pt                                   , min_prescale * fakeRateEffective );
        FillUserTH1D("Pt1stJet_ROI"        , Jet1_Pt                                , min_prescale * fakeRateEffective );
        FillUserTH1D("Pt2ndJet_ROI"        , Jet2_Pt                                , min_prescale * fakeRateEffective );
        FillUserTH1D("sTfrac_Jet1_ROI"     , Jet1_Pt / sT_eejj                      , min_prescale * fakeRateEffective );
        FillUserTH1D("sTfrac_Jet2_ROI"     , Jet2_Pt / sT_eejj                      , min_prescale * fakeRateEffective );
        FillUserTH1D("sTfrac_Ele1_ROI"     , Ele1_Pt / sT_eejj                         , min_prescale * fakeRateEffective );
        FillUserTH1D("sTfrac_Ele2_ROI"     , Ele2_Pt / sT_eejj                         , min_prescale * fakeRateEffective );
        FillUserTH1D("sTfrac_Jet_ROI"      , ( Jet1_Pt + Jet2_Pt ) / sT_eejj, min_prescale * fakeRateEffective );
        FillUserTH1D("sTfrac_Ele_ROI"      , ( Ele1_Pt + Ele2_Pt )       / sT_eejj, min_prescale * fakeRateEffective );
        FillUserTH1D("Ptj1j2_ROI"            , Pt_j1j2                                      , min_prescale * fakeRateEffective );
        FillUserTH1D("Ptee_Minus_Ptj1j2_ROI" , Pt_e1e2 - Pt_j1j2                            , min_prescale * fakeRateEffective );

        if ( nJet_ptCut > 2 ) {
          FillUserTH1D( "M_e1j3_ROI" , M_e1j3, min_prescale * fakeRateEffective ) ;
          FillUserTH1D( "M_e2j3_ROI" , M_e2j3, min_prescale * fakeRateEffective ) ;
          FillUserTH1D( "M_j1j3_ROI" , M_j1j3, min_prescale * fakeRateEffective ) ;
          FillUserTH1D( "M_j2j3_ROI" , M_j2j3, min_prescale * fakeRateEffective ) ;
          FillUserTH1D( "M_eejjj_ROI", M_eejjj,min_prescale * fakeRateEffective ) ;
          FillUserTH1D( "Ptj1j2j3_ROI"            , Pt_j1j2j3           , min_prescale * fakeRateEffective );
          FillUserTH1D( "Ptj2j3_ROI"              , Pt_j2j3             , min_prescale * fakeRateEffective );
          FillUserTH1D( "Ptj1j3_ROI"              , Pt_j1j3             , min_prescale * fakeRateEffective );
          FillUserTH1D( "Ptee_Minus_Ptj1j2j3_ROI" , Pt_e1e2 - Pt_j1j2j3 , min_prescale * fakeRateEffective );
        }
      }

      //--------------------------------------------------------------------------
      // Final selection plots
      //--------------------------------------------------------------------------

      if(doFinalSelections)
      {
        for (int i_lq_mass = 0; i_lq_mass < n_lq_mass; ++i_lq_mass ){
          int lq_mass = LQ_MASS[i_lq_mass];
          bool pass = passed_vector[i_lq_mass];
          if ( !pass ) continue;

          sprintf(plot_name, "Mej_selected_avg_LQ%d"       , lq_mass ); FillUserTH1D ( plot_name, M_ej_avg          , min_prescale * fakeRateEffective);
          sprintf(plot_name, "Mej_selected_min_LQ%d"       , lq_mass ); FillUserTH1D ( plot_name, M_ej_min          , min_prescale * fakeRateEffective);
          sprintf(plot_name, "Mej_selected_max_LQ%d"       , lq_mass ); FillUserTH1D ( plot_name, M_ej_max          , min_prescale * fakeRateEffective);
          sprintf(plot_name, "Mej_minmax_LQ%d"             , lq_mass ); FillUserTH1D ( plot_name, M_ej_min          , min_prescale * fakeRateEffective);
          sprintf(plot_name, "Mej_minmax_LQ%d"             , lq_mass ); FillUserTH1D ( plot_name, M_ej_max          , min_prescale * fakeRateEffective);
          sprintf(plot_name, "sT_eejj_LQ%d"                , lq_mass ); FillUserTH1D ( plot_name, sT_eejj           , min_prescale * fakeRateEffective);
          sprintf(plot_name, "Mee_LQ%d"                    , lq_mass ); FillUserTH1D ( plot_name, M_e1e2            , min_prescale * fakeRateEffective);
          sprintf(plot_name, "DR_Ele1Jet1_LQ%d"            , lq_mass ); FillUserTH1D ( plot_name, DR_Ele1Jet1       , min_prescale * fakeRateEffective);
          sprintf(plot_name, "Mej_selected_min_vs_max_LQ%d", lq_mass ); FillUserTH2D ( plot_name, M_ej_min, M_ej_max, min_prescale * fakeRateEffective);

          sprintf(plot_name, "CorrIsolation_1stEle_LQ%d"      , lq_mass );   FillUserTH1D(plot_name,  Ele1_CorrIsolation             , min_prescale * fakeRateEffective );
          sprintf(plot_name, "DeltaEtaTrkSC_1stEle_LQ%d"      , lq_mass );   FillUserTH1D(plot_name,  Ele1_DeltaEtaTrkSC             , min_prescale * fakeRateEffective );
          sprintf(plot_name, "EcalIsolation_1stEle_LQ%d"      , lq_mass );   FillUserTH1D(plot_name,  Ele1_EcalIsolation             , min_prescale * fakeRateEffective );
          sprintf(plot_name, "HcalIsolation_1stEle_LQ%d"      , lq_mass );   FillUserTH1D(plot_name,  Ele1_HcalIsolation             , min_prescale * fakeRateEffective );
          sprintf(plot_name, "TrkIsolation_1stEle_LQ%d"       , lq_mass );   FillUserTH1D(plot_name,  Ele1_TrkIsolation              , min_prescale * fakeRateEffective );
          sprintf(plot_name, "HasMatchedPhot_1stEle_LQ%d"     , lq_mass );   FillUserTH1D(plot_name,  Ele1_HasMatchedPhot            , min_prescale * fakeRateEffective );
          sprintf(plot_name, "HoE_1stEle_LQ%d"                , lq_mass );   FillUserTH1D(plot_name,  Ele1_HoE                       , min_prescale * fakeRateEffective );
          sprintf(plot_name, "LeadVtxDistXY_1stEle_LQ%d"      , lq_mass );   FillUserTH1D(plot_name,  Ele1_LeadVtxDistXY             , min_prescale * fakeRateEffective );
          sprintf(plot_name, "LeadVtxDistZ_1stEle_LQ%d"       , lq_mass );   FillUserTH1D(plot_name,  Ele1_LeadVtxDistZ              , min_prescale * fakeRateEffective );
          sprintf(plot_name, "MissingHits_1stEle_LQ%d"        , lq_mass );   FillUserTH1D(plot_name,  Ele1_MissingHits               , min_prescale * fakeRateEffective );

          if ( fabs(Ele1_Eta) < eleEta_bar ) {
            sprintf(plot_name, "Full5x5SigmaIEtaIEta_Barrel_1stEle_LQ%d", lq_mass ); FillUserTH1D( plot_name , Ele1_Full5x5SigmaIEtaIEta , min_prescale * fakeRateEffective    );
          }
          else if ( fabs(Ele1_Eta) > eleEta_end1_min && fabs(Ele2_Eta) < eleEta_end2_max ){
            sprintf(plot_name, "Full5x5SigmaIEtaIEta_Endcap_1stEle_LQ%d", lq_mass ); FillUserTH1D( plot_name , Ele1_Full5x5SigmaIEtaIEta , min_prescale * fakeRateEffective    );
          }

          sprintf(plot_name, "CorrIsolation_2ndEle_LQ%d"      , lq_mass );   FillUserTH1D(plot_name,  Ele2_CorrIsolation             , min_prescale * fakeRateEffective );
          sprintf(plot_name, "DeltaEtaTrkSC_2ndEle_LQ%d"      , lq_mass );   FillUserTH1D(plot_name,  Ele2_DeltaEtaTrkSC             , min_prescale * fakeRateEffective );
          sprintf(plot_name, "EcalIsolation_2ndEle_LQ%d"      , lq_mass );   FillUserTH1D(plot_name,  Ele2_EcalIsolation             , min_prescale * fakeRateEffective );
          sprintf(plot_name, "HcalIsolation_2ndEle_LQ%d"      , lq_mass );   FillUserTH1D(plot_name,  Ele2_HcalIsolation             , min_prescale * fakeRateEffective );
          sprintf(plot_name, "TrkIsolation_2ndEle_LQ%d"       , lq_mass );   FillUserTH1D(plot_name,  Ele2_TrkIsolation              , min_prescale * fakeRateEffective );
          sprintf(plot_name, "HasMatchedPhot_2ndEle_LQ%d"     , lq_mass );   FillUserTH1D(plot_name,  Ele2_HasMatchedPhot            , min_prescale * fakeRateEffective );
          sprintf(plot_name, "HoE_2ndEle_LQ%d"                , lq_mass );   FillUserTH1D(plot_name,  Ele2_HoE                       , min_prescale * fakeRateEffective );
          sprintf(plot_name, "LeadVtxDistXY_2ndEle_LQ%d"      , lq_mass );   FillUserTH1D(plot_name,  Ele2_LeadVtxDistXY             , min_prescale * fakeRateEffective );
          sprintf(plot_name, "LeadVtxDistZ_2ndEle_LQ%d"       , lq_mass );   FillUserTH1D(plot_name,  Ele2_LeadVtxDistZ              , min_prescale * fakeRateEffective );
          sprintf(plot_name, "MissingHits_2ndEle_LQ%d"        , lq_mass );   FillUserTH1D(plot_name,  Ele2_MissingHits               , min_prescale * fakeRateEffective );

          if ( fabs(Ele2_Eta) < eleEta_bar ) {
            sprintf(plot_name, "Full5x5SigmaIEtaIEta_Barrel_2ndEle_LQ%d", lq_mass ); FillUserTH1D( plot_name , Ele2_Full5x5SigmaIEtaIEta , min_prescale * fakeRateEffective    );
          }
          else if ( fabs(Ele2_Eta) > eleEta_end2_min && fabs(Ele2_Eta) < eleEta_end2_max ){
            sprintf(plot_name, "Full5x5SigmaIEtaIEta_Endcap_2ndEle_LQ%d", lq_mass ); FillUserTH1D( plot_name , Ele2_Full5x5SigmaIEtaIEta , min_prescale * fakeRateEffective    );
          }

          sprintf(plot_name, "Me1j1_LQ%d"             , lq_mass ); FillUserTH1D( plot_name , M_e1j1                                         , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Me1j2_LQ%d"             , lq_mass ); FillUserTH1D( plot_name , M_e1j2                                         , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Me2j1_LQ%d"             , lq_mass ); FillUserTH1D( plot_name , M_e2j1                                         , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Me2j2_LQ%d"             , lq_mass ); FillUserTH1D( plot_name , M_e2j2                                         , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Ptee_LQ%d"              , lq_mass ); FillUserTH1D( plot_name , Pt_e1e2                                        , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Eta1stJet_LQ%d"         , lq_mass ); FillUserTH1D( plot_name , Jet1_Eta                               , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Eta2ndJet_LQ%d"         , lq_mass ); FillUserTH1D( plot_name , Jet2_Eta                               , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Eta1stEle_LQ%d"         , lq_mass ); FillUserTH1D( plot_name , Ele1_Eta                                  , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Eta2ndEle_LQ%d"         , lq_mass ); FillUserTH1D( plot_name , Ele2_Eta                                  , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Phi1stJet_LQ%d"         , lq_mass ); FillUserTH1D( plot_name , Jet1_Phi                               , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Phi2ndJet_LQ%d"         , lq_mass ); FillUserTH1D( plot_name , Jet2_Phi                               , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Phi1stEle_LQ%d"         , lq_mass ); FillUserTH1D( plot_name , Ele1_Phi                                  , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Phi2ndEle_LQ%d"         , lq_mass ); FillUserTH1D( plot_name , Ele2_Phi                                  , min_prescale * fakeRateEffective );
          sprintf(plot_name, "MeeVsST_LQ%d"           , lq_mass ); FillUserTH2D( plot_name , M_e1e2, sT_eejj                                , min_prescale * fakeRateEffective );
          sprintf(plot_name, "sT_zjj_LQ%d"            , lq_mass ); FillUserTH1D( plot_name , sT_zjj                                         , min_prescale * fakeRateEffective );
          sprintf(plot_name, "nVertex_LQ%d"           , lq_mass ); FillUserTH1D( plot_name , nVertex                                        , min_prescale * fakeRateEffective );
          sprintf(plot_name, "nJet_LQ%d"              , lq_mass ); FillUserTH1D( plot_name , nJet_ptCut                             , min_prescale * fakeRateEffective );
          sprintf(plot_name, "EleChargeSum_LQ%d"      , lq_mass ); FillUserTH1D( plot_name , Ele1_Charge + Ele2_Charge            , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Meejj_LQ%d"             , lq_mass ); FillUserTH1D( plot_name , M_eejj                                         , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Meej_LQ%d"              , lq_mass ); FillUserTH1D( plot_name , M_eej                                          , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Mejj_LQ%d"              , lq_mass ); FillUserTH1D( plot_name , M_ejj                                          , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Mjj_LQ%d"               , lq_mass ); FillUserTH1D( plot_name , M_j1j2                                         , min_prescale * fakeRateEffective );
          sprintf(plot_name, "minDR_ZJet_LQ%d"        , lq_mass ); FillUserTH1D( plot_name , min_DeltaR_Zj                                  , min_prescale * fakeRateEffective );
          sprintf(plot_name, "DR_ZJet1_LQ%d"          , lq_mass ); FillUserTH1D( plot_name , DR_ZJ1                                         , min_prescale * fakeRateEffective );
          sprintf(plot_name, "DR_ZJet2_LQ%d"          , lq_mass ); FillUserTH1D( plot_name , DR_ZJ2                                         , min_prescale * fakeRateEffective );
          sprintf(plot_name, "MET_LQ%d"               , lq_mass ); FillUserTH1D( plot_name , PFMET_Type1_Pt                              , min_prescale * fakeRateEffective );
          sprintf(plot_name, "sTlep_LQ%d"             , lq_mass ); FillUserTH1D( plot_name , Ele1_Pt + Ele2_Pt                    , min_prescale * fakeRateEffective );
          sprintf(plot_name, "sTjet_LQ%d"             , lq_mass ); FillUserTH1D( plot_name , Jet1_Pt + Jet2_Pt              , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Pt1stEle_LQ%d"          , lq_mass ); FillUserTH1D( plot_name , Ele1_Pt                                   , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Pt2ndEle_LQ%d"          , lq_mass ); FillUserTH1D( plot_name , Ele2_Pt                                   , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Pt1stJet_LQ%d"          , lq_mass ); FillUserTH1D( plot_name , Jet1_Pt                                , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Pt2ndJet_LQ%d"          , lq_mass ); FillUserTH1D( plot_name , Jet2_Pt                                , min_prescale * fakeRateEffective );
          sprintf(plot_name, "sTfrac_Jet1_LQ%d"       , lq_mass ); FillUserTH1D( plot_name , Jet1_Pt / sT_eejj                      , min_prescale * fakeRateEffective );
          sprintf(plot_name, "sTfrac_Jet2_LQ%d"       , lq_mass ); FillUserTH1D( plot_name , Jet2_Pt / sT_eejj                      , min_prescale * fakeRateEffective );
          sprintf(plot_name, "sTfrac_Ele1_LQ%d"       , lq_mass ); FillUserTH1D( plot_name , Ele1_Pt / sT_eejj                         , min_prescale * fakeRateEffective );
          sprintf(plot_name, "sTfrac_Ele2_LQ%d"       , lq_mass ); FillUserTH1D( plot_name , Ele2_Pt / sT_eejj                         , min_prescale * fakeRateEffective );
          sprintf(plot_name, "sTfrac_Jet_LQ%d"        , lq_mass ); FillUserTH1D( plot_name , ( Jet1_Pt + Jet2_Pt ) / sT_eejj, min_prescale * fakeRateEffective );
          sprintf(plot_name, "sTfrac_Ele_LQ%d"        , lq_mass ); FillUserTH1D( plot_name , ( Ele1_Pt + Ele2_Pt ) / sT_eejj      , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Ptj1j2_LQ%d"            , lq_mass ); FillUserTH1D( plot_name , Pt_j1j2                                        , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Ptee_Minus_Ptj1j2_LQ%d" , lq_mass ); FillUserTH1D( plot_name , Pt_e1e2 - Pt_j1j2                              , min_prescale * fakeRateEffective );
          // muon kinematics
          sprintf(plot_name, "Pt1stMuon_LQ%d"          , lq_mass ); FillUserTH1D( plot_name , Muon1_Pt                                   , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Pt2ndMuon_LQ%d"          , lq_mass ); FillUserTH1D( plot_name , Muon2_Pt                                   , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Eta1stMuon_LQ%d"         , lq_mass ); FillUserTH1D( plot_name , Muon1_Eta                                  , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Eta2ndMuon_LQ%d"         , lq_mass ); FillUserTH1D( plot_name , Muon2_Eta                                  , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Phi1stMuon_LQ%d"         , lq_mass ); FillUserTH1D( plot_name , Muon1_Phi                                  , min_prescale * fakeRateEffective );
          sprintf(plot_name, "Phi2ndMuon_LQ%d"         , lq_mass ); FillUserTH1D( plot_name , Muon2_Phi                                  , min_prescale * fakeRateEffective );

        } // End final selection

        if( hasCut("sT_eejj_LQ300") && passedCut("sT_eejj_LQ300") && passedCut("min_M_ej_LQ300"))
          FillUserTH1D("Mee_70_110_LQ300", M_e1e2 , min_prescale * fakeRateEffective );
        if( hasCut("sT_eejj_LQ600") && passedCut("sT_eejj_LQ600") && passedCut("min_M_ej_LQ600"))
          FillUserTH1D("Mee_70_110_LQ600", M_e1e2 , min_prescale * fakeRateEffective );
        if( hasCut("sT_eejj_LQ800") && passedCut("sT_eejj_LQ800") && passedCut("min_M_ej_LQ800"))
          FillUserTH1D("Mee_70_110_LQ800", M_e1e2 , min_prescale * fakeRateEffective );
        if( hasCut("sT_eejj_LQ900") && passedCut("sT_eejj_LQ900") && passedCut("min_M_ej_LQ900"))
          FillUserTH1D("Mee_70_110_LQ900", M_e1e2 , min_prescale * fakeRateEffective );
        if( hasCut("sT_eejj_LQ1000") && passedCut("sT_eejj_LQ1000") && passedCut("min_M_ej_LQ1000"))
          FillUserTH1D("Mee_70_110_LQ1000", M_e1e2 , min_prescale * fakeRateEffective );

      } // End do final selections

    } // End preselection
  } // End loop over events

  std::cout << "analysisClass::Loop() ends" <<std::endl;
}
