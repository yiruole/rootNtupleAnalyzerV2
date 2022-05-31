{
  float sT_eejj, M_e1e2, M_e1j1, M_e1j2, M_e2j1, M_e2j2, Ele1_Pt, Ele2_Pt, Jet1_Pt, Jet2_Pt;
  float PFMET_Type1_Pt, PFMET_Type1_Phi;
  float Ele1_Eta, Ele2_Eta, Ele1_Phi, Ele2_Phi;
  float Jet1_Eta, Jet2_Eta, Jet1_Phi, Jet2_Phi;
  float Jet3_Eta, Jet3_Phi, Jet3_Pt;
  float DR_Ele1Jet1, DR_Ele1Jet2, DR_Ele2Jet1, DR_Ele2Jet2, DR_Jet1Jet2;

  TMVA::Tools::Instance();
  TString methodName = "BDT";

  TChain ch("rootTupleTree/tree");
  TFileCollection fc("dum","","$LQANA/config/nanoV7_2016_analysisPreselSkims_egLoose_4feb2022/DYJetsToLL_Pt-650ToInf_amcatnloFXFX_pythia8.txt");
  ch.AddFileInfoList(fc.GetList());

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

  TString weightfile = "/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/versionsOfOptimization/nanoV7/2016/eejj_31jan_egmLooseID_investigateBDT/lq1500_ignoreNegWeights/dataset/weights/TMVAClassification_BDTG.weights.xml";
  reader.BookMVA( methodName, weightfile );

  auto h1 = new TH1D("h1","",200,-2,2);
  auto h1weighted = new TH1D("h1weighted","",200,-2,2);
  auto h2 = new TH1D("h2","Classifier Output on Signal Events",200,-2,2);
  std::vector<float> vout;
  std::vector<float> vout2;

  auto readEvents = [&](TTree & tree, TH1 & histoUnweighted, TH1 & histoWeighted) {
    float pileup_weight, weight, prefire_weight;
    float ele1RecoSF, ele1TrigSF, ele1IDSF;
    float ele2RecoSF, ele2TrigSF, ele2IDSF;
    tree.SetBranchAddress("puWeight", &pileup_weight);
    tree.SetBranchAddress("Weight", &weight);
    tree.SetBranchAddress("PrefireWeight", &prefire_weight);
    tree.SetBranchAddress("Ele1_RecoSF", &ele1RecoSF);
    tree.SetBranchAddress("Ele1_TrigSF", &ele1TrigSF);
    tree.SetBranchAddress("Ele1_EGMLooseIDSF", &ele1IDSF);
    tree.SetBranchAddress("Ele2_RecoSF", &ele2RecoSF);
    tree.SetBranchAddress("Ele2_TrigSF", &ele2TrigSF);
    tree.SetBranchAddress("Ele2_EGMLooseIDSF", &ele2IDSF);

    tree.SetBranchAddress("sT_eejj",&sT_eejj);
    tree.SetBranchAddress( "PFMET_Type1_Pt", &PFMET_Type1_Pt);
    tree.SetBranchAddress( "PFMET_Type1_Phi", &PFMET_Type1_Phi);
    tree.SetBranchAddress( "M_e1e2", &M_e1e2);
    tree.SetBranchAddress( "M_e1j1", &M_e1j1);
    tree.SetBranchAddress( "M_e1j2", &M_e1j2);
    tree.SetBranchAddress( "M_e2j1", &M_e2j1);
    tree.SetBranchAddress( "M_e2j2", &M_e2j2);
    tree.SetBranchAddress( "Ele1_Pt", &Ele1_Pt);
    tree.SetBranchAddress( "Ele2_Pt", &Ele2_Pt);
    tree.SetBranchAddress( "Ele1_Eta", &Ele1_Eta);
    tree.SetBranchAddress( "Ele2_Eta", &Ele2_Eta);
    tree.SetBranchAddress( "Ele1_Phi", &Ele1_Phi);
    tree.SetBranchAddress( "Ele2_Phi", &Ele2_Phi);
    tree.SetBranchAddress( "Jet1_Pt", &Jet1_Pt);
    tree.SetBranchAddress( "Jet2_Pt", &Jet2_Pt);
    tree.SetBranchAddress( "Jet3_Pt", &Jet3_Pt);
    tree.SetBranchAddress( "Jet1_Eta", &Jet1_Eta);
    tree.SetBranchAddress( "Jet2_Eta", &Jet2_Eta);
    tree.SetBranchAddress( "Jet3_Eta", &Jet3_Eta);
    tree.SetBranchAddress( "Jet1_Phi", &Jet1_Phi);
    tree.SetBranchAddress( "Jet2_Phi", &Jet2_Phi);
    tree.SetBranchAddress( "Jet3_Phi", &Jet3_Phi);
    tree.SetBranchAddress( "DR_Ele1Jet1", &DR_Ele1Jet1);
    tree.SetBranchAddress( "DR_Ele1Jet2", &DR_Ele1Jet2);
    tree.SetBranchAddress( "DR_Ele2Jet1", &DR_Ele2Jet1);
    tree.SetBranchAddress( "DR_Ele2Jet2", &DR_Ele2Jet2);
    tree.SetBranchAddress( "DR_Jet1Jet2", &DR_Jet1Jet2);
    vout.clear(); 
    vout.resize(tree.GetEntries());
    for (Long64_t ievt=0; ievt < tree.GetEntries();ievt++) {

      if (ievt%10000 == 0) std::cout << "--- ... Processing event: " << ievt << std::endl;

      tree.GetEntry(ievt);

      auto output = reader.EvaluateMVA(methodName);

      histoUnweighted.Fill(output);
      histoWeighted.Fill(output, pileup_weight*weight*prefire_weight*ele1RecoSF*ele1TrigSF*ele1IDSF*ele2RecoSF*ele2TrigSF*ele2IDSF);
      vout[ievt] = output;  
    }
  };

  // read events and fill histogram
  readEvents(ch, *h1, *h1weighted);

  std::vector<float> bkg_result = vout;

  h1->Draw();
  gPad->Draw();
  TCanvas c2;
  c2.cd();
  h1weighted->Draw();
  gPad->Draw();


}
