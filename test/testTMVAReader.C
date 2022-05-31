#include "TTreeReader.h"
#include "TTreeReaderValue.h"
#include "TChain.h"
#include "TFileCollection.h"
#include <TMVA/Tools.h>
#include <TMVA/Reader.h>

void testTMVAReader() {
  TChain ch("rootTupleTree/tree");
  TFileCollection fc("dum","","/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/config/nanoV7_2016_pskQCDEEJJ_egLoose_24mar2022_comb/SinglePhoton_Run2016B-02Apr2020_ver2-v1.txt");
  ch.AddFileInfoList(fc.GetList());

  TTreeReader myReader(&ch);
  TTreeReaderValue<Float_t> reader_sT_eejj = {myReader, "sT_eejj"};
  TTreeReaderValue<Float_t> reader_PFMET_Type1_Pt = {myReader, "PFMET_Type1_Pt"};
  TTreeReaderValue<Float_t> reader_PFMET_Type1_Phi = {myReader, "PFMET_Type1_Phi"};
  TTreeReaderValue<Float_t> reader_Me1e2 = {myReader, "M_e1e2"};
  TTreeReaderValue<Float_t> reader_Me1j1 = {myReader, "M_e1j1"};
  TTreeReaderValue<Float_t> reader_Me1j2 = {myReader, "M_e1j2"};
  TTreeReaderValue<Float_t> reader_Me2j1 = {myReader, "M_e2j1"};
  TTreeReaderValue<Float_t> reader_Me2j2 = {myReader, "M_e2j2"};
  TTreeReaderValue<Float_t> reader_Ele1_Pt = {myReader, "Ele1_Pt" };
  TTreeReaderValue<Float_t> reader_Ele2_Pt = {myReader, "Ele2_Pt" };
  TTreeReaderValue<Float_t> reader_Ele1_Eta  = {myReader,"Ele1_Eta"};
  TTreeReaderValue<Float_t> reader_Ele2_Eta  = {myReader,"Ele2_Eta"};
  TTreeReaderValue<Float_t> reader_Ele1_Phi  = {myReader,"Ele1_Phi"};
  TTreeReaderValue<Float_t> reader_Ele2_Phi  = {myReader,"Ele2_Phi"};
  TTreeReaderValue<Float_t> reader_Jet1_Pt = {myReader, "Jet1_Pt" };
  TTreeReaderValue<Float_t> reader_Jet2_Pt = {myReader, "Jet2_Pt" };
  TTreeReaderValue<Float_t> reader_Jet3_Pt = {myReader, "Jet3_Pt" };
  TTreeReaderValue<Float_t> reader_Jet1_Eta = {myReader,"Jet1_Eta" };
  TTreeReaderValue<Float_t> reader_Jet2_Eta = {myReader,"Jet2_Eta" };
  TTreeReaderValue<Float_t> reader_Jet3_Eta = {myReader,"Jet3_Eta" };
  TTreeReaderValue<Float_t> reader_Jet1_Phi = {myReader,"Jet1_Phi" };
  TTreeReaderValue<Float_t> reader_Jet2_Phi = {myReader,"Jet2_Phi" };
  TTreeReaderValue<Float_t> reader_Jet3_Phi = {myReader,"Jet3_Phi" };
  TTreeReaderValue<Float_t> reader_DR_Ele1Jet1 = {myReader, "DR_Ele1Jet1"};
  TTreeReaderValue<Float_t> reader_DR_Ele1Jet2 = {myReader, "DR_Ele1Jet2"};
  TTreeReaderValue<Float_t> reader_DR_Ele2Jet1 = {myReader, "DR_Ele2Jet1"};
  TTreeReaderValue<Float_t> reader_DR_Ele2Jet2 = {myReader, "DR_Ele2Jet2"};
  TTreeReaderValue<Float_t> reader_DR_Jet1Jet2 = {myReader, "DR_Jet1Jet2"};
  TTreeReaderValue<Float_t> reader_run = {myReader, "run"};
  TTreeReaderValue<Float_t> reader_ls = {myReader, "ls"};
  TTreeReaderValue<Float_t> reader_event = {myReader, "event"};
  float sT_eejj, M_e1e2, M_e1j1, M_e1j2, M_e2j1, M_e2j2, Ele1_Pt, Ele2_Pt, Jet1_Pt, Jet2_Pt;
  float PFMET_Type1_Pt, PFMET_Type1_Phi;
  float Ele1_Eta, Ele2_Eta, Ele1_Phi, Ele2_Phi;
  float Jet1_Eta, Jet2_Eta, Jet1_Phi, Jet2_Phi;
  float Jet3_Eta, Jet3_Phi, Jet3_Pt;
  float DR_Ele1Jet1, DR_Ele1Jet2, DR_Ele2Jet1, DR_Ele2Jet2, DR_Jet1Jet2;
  float run,ls, event;
  TMVA::Tools::Instance();
  TMVA::Reader reader( "!Color:!Silent" );
  reader.AddVariable( "sT_eejj", &sT_eejj);
  reader.AddVariable( "PFMET_Type1_Pt", &PFMET_Type1_Pt);
  reader.AddVariable( "PFMET_Type1_Phi", &PFMET_Type1_Phi);
  reader.AddVariable( "M_e1e2", &M_e1e2);
  reader.AddVariable( "M_e1j1", &M_e1j1);
  reader.AddVariable( "M_e1j2", &M_e1j2);
  reader.AddVariable( "M_e2j1", &M_e2j1);
  reader.AddVariable( "M_e2j2", &M_e2j2);
  reader.AddVariable( "Ele1_Pt", &Ele1_Pt);
  reader.AddVariable( "Ele2_Pt", &Ele2_Pt);
  reader.AddVariable( "Ele1_Eta", &Ele1_Eta);
  reader.AddVariable( "Ele2_Eta", &Ele2_Eta);
  reader.AddVariable( "Ele1_Phi", &Ele1_Phi);
  reader.AddVariable( "Ele2_Phi", &Ele2_Phi);
  reader.AddVariable( "Jet1_Pt", &Jet1_Pt);
  reader.AddVariable( "Jet2_Pt", &Jet2_Pt);
  reader.AddVariable( "Jet3_Pt", &Jet3_Pt);
  reader.AddVariable( "Jet1_Eta", &Jet1_Eta);
  reader.AddVariable( "Jet2_Eta", &Jet2_Eta);
  reader.AddVariable( "Jet3_Eta", &Jet3_Eta);
  reader.AddVariable( "Jet1_Phi", &Jet1_Phi);
  reader.AddVariable( "Jet2_Phi", &Jet2_Phi);
  reader.AddVariable( "Jet3_Phi", &Jet3_Phi);
  reader.AddVariable( "DR_Ele1Jet1", &DR_Ele1Jet1);
  reader.AddVariable( "DR_Ele1Jet2", &DR_Ele1Jet2);
  reader.AddVariable( "DR_Ele2Jet1", &DR_Ele2Jet1);
  reader.AddVariable( "DR_Ele2Jet2", &DR_Ele2Jet2);
  reader.AddVariable( "DR_Jet1Jet2", &DR_Jet1Jet2);
  reader.BookMVA("BDT", "/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/versionsOfAnalysis/2016/nanoV7/eejj/mar24_2022_egLoose_BDT_qcd/train_14-17/dataset/weights/TMVAClassification_LQToDEle_M-1400_pair_BDTG.weights.xml" );


  while (myReader.Next()) {
   sT_eejj         =   *reader_sT_eejj;
   PFMET_Type1_Pt  =   *reader_PFMET_Type1_Pt;
   PFMET_Type1_Phi =   *reader_PFMET_Type1_Phi;
   M_e1e2          =   *reader_Me1e2;
   M_e1j1          =   *reader_Me1j1;
   M_e1j2          =   *reader_Me1j2;
   M_e2j1          =   *reader_Me2j1;
   M_e2j2          =   *reader_Me2j2;
   Ele1_Pt         = *reader_Ele1_Pt;
   Ele2_Pt         = *reader_Ele2_Pt;
   Ele1_Eta        = *reader_Ele1_Eta;
   Ele2_Eta        = *reader_Ele2_Eta;
   Ele1_Phi        = *reader_Ele1_Phi;
   Ele2_Phi        = *reader_Ele2_Phi;
   Jet1_Pt         = *reader_Jet1_Pt;
   Jet2_Pt         = *reader_Jet2_Pt;
   Jet3_Pt         = *reader_Jet3_Pt;
   Jet1_Eta        = *reader_Jet1_Eta;
   Jet2_Eta        = *reader_Jet2_Eta;
   Jet3_Eta        = *reader_Jet3_Eta;
   Jet1_Phi        = *reader_Jet1_Phi;
   Jet2_Phi        = *reader_Jet2_Phi;
   Jet3_Phi        = *reader_Jet3_Phi;
   DR_Ele1Jet1     = *reader_DR_Ele1Jet1;
   DR_Ele1Jet2     = *reader_DR_Ele1Jet2;
   DR_Ele2Jet1     = *reader_DR_Ele2Jet1;
   DR_Ele2Jet2     = *reader_DR_Ele2Jet2;
   DR_Jet1Jet2     = *reader_DR_Jet1Jet2;
   run             = *reader_run;
   ls              = *reader_ls;
   event           = *reader_event;

   auto bdtOutput = reader.EvaluateMVA("BDT");
   if(bdtOutput > 0.986)
     std::cout << "Found event with BDToutput > 0.986: BDToutput=" << bdtOutput << ", run=" << run << ", ls=" << ls << ", event=" << static_cast<unsigned int>(event) <<std::endl;
  }
}
