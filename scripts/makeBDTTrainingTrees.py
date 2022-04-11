#!/usr/bin/env python3
#
import os

from tmvaBDT import LoadChainFromTxtFile, GetSignalTotalEventsHist

import ROOT
from ROOT import TMVA, TFile, TString, TCut, TChain, TFileCollection, gROOT, gDirectory, gInterpreter, TEntryList, TH1D, TProfile, RDataFrame

gROOT.SetBatch()


# datasets
inputListBkgBase = "$LQANA/config/nanoV7_2016_analysisPreselSkims_egLoose_4feb2022/"
inputListQCDBase = "$LQANA/config/nanoV7_2016_pskQCDEEJJ_egLoose_24mar2022_comb/"
inputListSignalBase = inputListBkgBase
# preselection-skimmed background datasets
backgroundDatasetsDict = {
        # "ZJet_amcatnlo_ptBinned" if do2016 else "ZJet_jetAndPtBinned",
        "ZJet_amcatnlo_ptBinned" : [
            inputListBkgBase+"DYJetsToLL_Zpt-0To50_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"DYJetsToLL_Pt-50To100_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"DYJetsToLL_Pt-100To250_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"DYJetsToLL_Pt-250To400_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"DYJetsToLL_Pt-400To650_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"DYJetsToLL_Pt-650ToInf_amcatnloFXFX_pythia8.txt",
            ],
        "TTbar_powheg" : [
            inputListBkgBase+"TTTo2L2Nu_pythia8.txt",
            inputListBkgBase+"TTToHadronic_pythia8.txt",
            inputListBkgBase+"TTToSemiLeptonic_pythia8.txt",
            ],
        "QCDFakes_DATA" : [
            inputListQCDBase+"SinglePhoton_Run2016H-02Apr2020-v1.txt",
            inputListQCDBase+"SinglePhoton_Run2016G-02Apr2020-v1.txt",
            inputListQCDBase+"SinglePhoton_Run2016F-02Apr2020-v1.txt",
            inputListQCDBase+"SinglePhoton_Run2016E-02Apr2020-v1.txt",
            inputListQCDBase+"SinglePhoton_Run2016D-02Apr2020-v1.txt",
            inputListQCDBase+"SinglePhoton_Run2016C-02Apr2020-v1.txt",
            inputListQCDBase+"SinglePhoton_Run2016B-02Apr2020_ver2-v1.txt",
            ],
        "DIBOSON_nlo" : [
            inputListBkgBase+"WWTo4Q.txt",
            inputListBkgBase+"WWToLNuQQ.txt",
            inputListBkgBase+"WWTo2L2Nu.txt",
            inputListBkgBase+"ZZTo2L2Q_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"ZZTo4L_pythia8.txt",
            inputListBkgBase+"ZZTo2Q2Nu_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"ZZTo2L2Nu_pythia8.txt",
            inputListBkgBase+"WZTo1L3Nu_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WZTo3LNu_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WZTo1L1Nu2Q_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WZTo2L2Q_amcatnloFXFX_pythia8.txt",
            ],
        #"TRIBOSON" : [
        #    inputListBkgBase+"WWW_4F_pythia8.txt",
        #    inputListBkgBase+"WWZ_pythia8.txt",
        #    inputListBkgBase+"WZZ_pythia8.txt",
        #    inputListBkgBase+"ZZZ_pythia8.txt",
        #    ],
        #"TTW" : [
        #    inputListBkgBase+"TTWJetsToLNu_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"TTWJetsToQQ_amcatnloFXFX_pythia8.txt",
        #    ],
        #"TTZ" : [
        #    inputListBkgBase+"ttZJets_madgraphMLM.txt"
        #    ],
        "SingleTop" : [
            inputListBkgBase+"ST_tW_top_5f_inclusiveDecays_ext1_pythia8.txt",
            inputListBkgBase+"ST_tW_antitop_5f_inclusiveDecays_ext1_pythia8.txt",
            inputListBkgBase+"ST_t-channel_top_4f_inclusiveDecays.txt",
            inputListBkgBase+"ST_t-channel_antitop_4f_inclusiveDecays.txt",
            inputListBkgBase+"ST_s-channel_4f_InclusiveDecays_pythia8.txt",
            ],
        #"WJet_amcatnlo_jetBinned" : [
        #    inputListBkgBase+"WToLNu_0J_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"WToLNu_1J_backup_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"WToLNu_2J_amcatnloFXFX_pythia8.txt",
        #    ],
        "WJet_amcatnlo_ptBinned" : [
            inputListBkgBase+"WJetsToLNu_Wpt-0To50_ext1_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WJetsToLNu_Wpt-50To100_ext1_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WJetsToLNu_Pt-100To250_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WJetsToLNu_Pt-250To400_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WJetsToLNu_Pt-400To600_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WJetsToLNu_Pt-600ToInf_amcatnloFXFX_pythia8.txt",
            ],
        "PhotonJets_Madgraph" : [
            inputListBkgBase+"GJets_HT-40To100_madgraphMLM.txt",
            inputListBkgBase+"GJets_HT-100To200_madgraphMLM.txt",
            inputListBkgBase+"GJets_HT-200To400_madgraphMLM.txt",
            inputListBkgBase+"GJets_HT-400To600_madgraphMLM.txt",
            inputListBkgBase+"GJets_HT-600ToInf_madgraphMLM.txt",
            ],
}
allSignalDatasetsDict = {
        "LQToDEle_M-1700_pair" : [
            inputListSignalBase+"LQToDEle_M-1700_pair_pythia8.txt",
            ],
        "LQToDEle_M-1600_pair" : [
            inputListSignalBase+"LQToDEle_M-1600_pair_pythia8.txt",
            ],
        "LQToDEle_M-1500_pair" : [
            inputListSignalBase+"LQToDEle_M-1500_pair_pythia8.txt",
            ],
        "LQToDEle_M-1400_pair" : [
            inputListSignalBase+"LQToDEle_M-1400_pair_pythia8.txt",
            ],
        "LQToDEle_M-1200_pair" : [
            inputListSignalBase+"LQToDEle_M-1200_pair_pythia8.txt",
            ],
        "LQToDEle_M-300_pair" : [
            inputListSignalBase+"LQToDEle_M-300_pair_pythia8.txt",
            ],
}
mycuts = TCut("M_e1e2 > 200 && sT_eejj > 400")
mycutb = TCut("M_e1e2 > 200 && sT_eejj > 400")

####################################################################################################
# Run
####################################################################################################
if __name__ == "__main__":
    allSamplesDict = dict()
    #allSamplesDict.update(backgroundDatasetsDict)
    allSamplesDict.update(allSignalDatasetsDict)
    for sample in allSamplesDict.keys():
        for idx, txtFile in enumerate(allSamplesDict[sample]):
            tchainBkg = LoadChainFromTxtFile(txtFile)
            if tchainBkg is None:
                continue
            datasetName = os.path.basename(txtFile).strip(".txt")
            df = RDataFrame(tchainBkg)
            # df = df.Filter(mycutb.GetTitle())  # will work for expressions valid in C++
            # df = df.Define('BDT', 'BDTv[0]')
            # tfilepath = "/tmp/scooper/{}.root".format(datasetName)
            tfilepath = "root://eosuser.cern.ch//eos/user/s/scooper/LQ/NanoV7/2016/analysis/bdtTraining_eejj_finalSels_egLoose_4feb2022/{}.root".format(datasetName)
            print("Writing snapshot to:", tfilepath)
            df.Snapshot("rootTupleTree/tree", tfilepath)
            if sample in allSignalDatasetsDict.keys():
                mass = int(sample[sample.find("M")+2:sample.rfind("_")])
                eventCounterHist = GetSignalTotalEventsHist(mass, allSignalDatasetsDict)
                tfile = TFile(tfilepath, "update")
                tfile.cd()
                eventCounterHist.Write()

