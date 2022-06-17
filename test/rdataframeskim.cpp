#include "ROOT/RDataFrame.hxx"
#include "ROOT/RVec.hxx"

using RVecF = ROOT::RVec<float>;

std::vector<std::string> ColumnsToKeep(std::vector<std::string>&& allCols) {
  // see: https://cms-nanoaod-integration.web.cern.ch/integration/CMSSW_10_6_X/mc106Xul16_doc.html
  std::vector<std::string> objectsToKeep { "nElectron", "nGenJet", "nGenPart", "nJet", "nMuon", "nTrigObj"};
  objectsToKeep.insert(objectsToKeep.end(),
      {"Electron", "Flag", "GenJet", "GenMET", "GenPart", "Jet", "MET", "Muon", "Pileup", "fixedGridRho", "TrigObj", "event", "genWeight", "luminosityBlock", "run"}
      );
  objectsToKeep.insert(objectsToKeep.end(),
      {"HLT_Ele", "HLT_Photon"}
      );
  std::set<std::string> colsToKeep;
  for(auto colName : allCols) {
    for(auto substr : objectsToKeep) {
      //if(colName.find(substr) != std::string::npos)
      if(colName.find(substr) == 0) // prefix only
        colsToKeep.insert(colName);
    }
  }
  std::vector<std::string> colsToKeepVec;
  colsToKeepVec.reserve(colsToKeep.size());
  colsToKeepVec.insert(colsToKeepVec.end(), colsToKeep.begin(), colsToKeep.end());
  std::sort(colsToKeepVec.begin(), colsToKeepVec.end(), std::greater<std::string>());
  //for(auto colName : colsToKeepVec)
  //  std::cout << colName << ", ";
  //std::cout << std::endl;

  return colsToKeepVec;
}

void rdataframeskim() {
   ROOT::EnableImplicitMT(); // have to disable for Display()

   std::string filePath = "/tmp/scooper/8B218654-0767-E344-AF41-8EE3E0D10019.root";
   ROOT::RDataFrame df("Events", filePath.c_str());
   //ROOT::RDataFrame df("Events", "root://xrootd-cms.infn.it//store/mc/RunIISummer20UL16NanoAODv9/DYJetsToLL_LHEFilterPtZ-0To50_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_v17-v1/2430000/8820A566-8764-4C41-8C64-852C8D050E36.root");

   //auto df_vLooseEle = df_nElectrons.Filter("Sum((Electron_hoe*Electron_eCorr) < 0.15 && (Electron_pt/Electron_eCorr) > 10) > 0", "At least one electron passing EGM VLoose FakeRate ID and Pt > 10 GeV");
   //auto df_vLooseEle = df.Define("vLooseElectron", "(Electron_hoe*Electron_eCorr) < 0.15 && (Electron_pt/Electron_eCorr) > 10");
   auto df_vLooseEleDef = df.Define("vLooseElectrons", "(Electron_hoe*Electron_eCorr) < 0.15 && (Electron_pt/Electron_eCorr) > 10");
   auto df_vLooseEle = df_vLooseEleDef.Filter("Sum(vLooseElectrons) > 0", "At least one electron passing EGM VLoose FakeRate ID and Pt > 10 GeV");
   //auto df_electronID = df_vLooseEle.Filter("Sum(Electron_cutBased > 1 && Electron_pt > 35) > 0", "At least one electron passing EGamma loose ID with Pt > 35 GeV");
   auto df_electronIDDef = df_vLooseEle.Define("EGMLooseElectrons", "(Electron_cutBased > 1 && Electron_pt > 35) > 0");
   auto df_electronID = df_electronIDDef.Filter("Sum(EGMLooseElectrons) > 0", "At least one electron passing EGamma loose ID with Pt > 35 GeV");
   //auto df_electronPt = df_electronID.Filter("All(Electron_pt>35)", "Electron Pt > 35 GeV");
   auto df_electronPt = df_electronID.Filter("Electron_pt[0]>35", "Lead electron Pt > 35 GeV");

   //// redefine electrons
   //for(auto colName : df_electronPt.GetColumnNames()) {
   //  if(colName.find("Electron") == 0) {  // prefix match
   //    df_electronPt = df_electronPt.Redefine(colName, colName+"[EGMLooseElectrons]");
   //  }
   //}
   //df_electronPt = df_electronPt.Redefine("nElectron", "Sum(EGMLooseElectrons)");

   //// Muons
   //auto df_muons = df_electronPt;

   //// Jets
   ////auto cutPt = [](RVecD &pxs, RVecD &pys, RVecD &Es) {
   ////  auto all_pts = sqrt(pxs * pxs + pys * pys);
   ////  auto good_pts = all_pts[Es > 200.];
   ////  return good_pts;
   ////};
   //auto minDeltaR = [](RVecF &jetEta, RVecF &jetPhi, RVecF &electronEta, RVecF &electronPhi) {
   //  std::vector<float> deltaRs;
   //  for(unsigned int iJet = 0; iJet < jetEta.size(); ++iJet) {
   //    float minDR = 1000;
   //    for(unsigned int iLep = 0; iLep < electronEta.size(); ++iLep) {
   //      float thisDR = ROOT::VecOps::DeltaR(jetEta[iJet], electronEta[iLep], jetPhi[iJet], electronPhi[iLep]);
   //      if(thisDR < minDR)
   //        minDR = thisDR;
   //    }
   //    deltaRs.emplace_back(minDR);
   //  }
   //  RVecF myRVec(deltaRs.data(), deltaRs.size());
   //  return myRVec;
   //};

   ////auto df_deltaREJ = df_muons.Define("idx", "Combinations(Electron_phi, 1)")
   ////    //.Define("drEJ", "DeltaR(Take(Jet_eta, idx[0]), Take(Electron_eta, idx[1]), Take(Jet_phi, idx[0]), Take(Electron_phi, idx[1]))")
   ////    .Define("drEJ", "DeltaR(Jet_eta, Take(Electron_eta, idx[0]), Jet_phi, Take(Electron_phi, idx[0]))")
   ////    .Define("minIdx", "ArgMin(abs(drEJ))")
   ////    .Define("drEJMin", "drEJ[minIdx]");
   //auto df_deltaREJ = df_muons.Define("Jet_drEJMin", minDeltaR, {"Jet_eta", "Jet_phi", "Electron_eta", "Electron_phi"});
   //// see: https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetID
   //auto df_pfJetIDDef = df_deltaREJ.Define("TightPFJets", "Jet_jetId >= 2 && abs(Jet_eta) <= 2.4 && Jet_drEJMin >= 0.3");
   //// redefine jets
   //for(auto colName : df_pfJetIDDef.GetColumnNames()) {
   //  if(colName.find("Jet") == 0) {  // prefix match
   //    df_pfJetIDDef = df_pfJetIDDef.Redefine(colName, colName+"[TightPFJets]");
   //  }
   //}
   //df_pfJetIDDef = df_pfJetIDDef.Redefine("nJet", "Sum(TightPFJets)");
   //

   //auto df_final = df_pfJetIDDef;
   auto df_final = df_electronPt;
   auto report = df_final.Report();
   report->Print();
   std::string treeName = "Events";
   std::string outFileName = "testSkim.root";
   df_final.Snapshot(treeName, outFileName, ColumnsToKeep(df_final.GetColumnNames()));

   // include the Runs tree
   TFile* treeFile = TFile::Open(filePath.c_str());
   TTree* tree = treeFile->Get<TTree>("Runs");
   TFile* outputFile = new TFile(outFileName.c_str(), "update");
   outputFile->cd();
   tree->Write();
   outputFile->Close();
   treeFile->Close();
}
