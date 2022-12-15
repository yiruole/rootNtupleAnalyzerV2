#!/usr/bin/env python3
#
# see: https://github.com/lmoneta/tmva-tutorial/blob/master/notebooks/TMVA_Classification.ipynb
#      https://github.com/lmoneta/tmva-tutorial/blob/master/notebooks/TMVA_Reader_ManyMethods_py.ipynb

from array import array
from collections import OrderedDict
import numpy as np
import sys
import os
import math
import multiprocessing
import traceback

import ROOT
from ROOT import TMVA, TFile, TString, TCut, TChain, TFileCollection, gROOT, gDirectory, gInterpreter, TEntryList, TH1D, TProfile, RDataFrame

class Sample:
    def __init__(self, name, subSampleList, subSampleWeights):
        self.name = name
        self.subSamples = subSampleList
        self.subSampleWeights = subSampleWeights

####################################################################################################
# Configurables
####################################################################################################
variableList = [
    "sT_eejj",
    "PFMET_Type1_Pt",
    "PFMET_Type1_Phi",
    "M_e1e2",
    "M_e1j1",
    "M_e1j2",
    "M_e2j1",
    "M_e2j2",
    "Ele1_Pt",
    "Ele2_Pt",
    "Ele1_Eta",
    "Ele2_Eta",
    "Ele1_Phi",
    "Ele2_Phi",
    "Jet1_Pt",
    "Jet2_Pt",
    "Jet3_Pt",
    "Jet1_Eta",
    "Jet2_Eta",
    "Jet3_Eta",
    "Jet1_Phi",
    "Jet2_Phi",
    "Jet3_Phi",
    "DR_Ele1Jet1",
    "DR_Ele1Jet2",
    "DR_Ele2Jet1",
    "DR_Ele2Jet2",
    "DR_Jet1Jet2",
    "Masym",
    "MejMin",
    "MejMax",
    "Meejj",
    "mass"
]
# EGM Loose ID
#FIXME: trigSF1 and 2 shouldn't both be applied
eventWeightExpression = "Weight*PrefireWeight*puWeight*Ele1_RecoSF*Ele2_RecoSF*Ele1_TrigSF*Ele2_TrigSF*Ele1_EGMLooseIDSF*Ele2_EGMLooseIDSF"
# HEEP
#eventWeightExpression = "Weight*PrefireWeight*puWeight*Ele1_RecoSF*Ele2_RecoSF*Ele1_TrigSF*Ele2_TrigSF*Ele1_HEEPSF*Ele2_HEEPSF"
#
neededBranches = ["Weight", "PrefireWeight", "puWeight", "Ele1_RecoSF", "Ele2_RecoSF", "Ele1_TrigSF", "Ele2_TrigSF"]
neededBranches.extend(["run", "ls", "event"])
# loose
neededBranches.extend(["Ele1_EGMLooseIDSF", "Ele2_EGMLooseIDSF"])
# HEEP
# neededBranches.extend(["Ele1_HEEPSF", "Ele2_HEEPSF"])
neededBranches.extend(variableList)
# Apply additional cuts on the signal and background samples (can be different)
# mycuts = TCut()
# mycutb = TCut()
mycuts = TCut("M_e1e2 > 200 && sT_eejj > 400")
mycutb = TCut("M_e1e2 > 200 && sT_eejj > 400")
    
####################################################################################################
# datasets
#inputListBkgBase = os.getenv("LQANA")+"/config/rdfDatasetInputLists_mee200st400_allLQ/{}/"
#inputListQCDBase = os.getenv("LQANA")+"/config/rdfDatasetInputLists_mee200st400_allLQ/{}/"
inputListBkgBase = os.getenv("LQANA")+"/config/bdt/inputList_bdtTraining_eejj_finalSels_egLoose_6dec2022_mee200st400_allLQ/{}/"
inputListQCDBase = inputListBkgBase 
# HEEP
# inputListBkgBase = "$LQANA/config/nanoV7_2016_analysisPreselSkims_heep_2sep2021/"
# inputListQCDBase = "$LQANA/config/nanoV7_2016_pskQCDEEJJ_heep_6apr2022_comb/"
# preselection-skimmed background datasets
#FIXME: comment out datasets with zero events; should handle this a bit better
#       this came from the fact that the makeBDTTrainingTrees script doesn't write out files for trees with zero entries
backgroundDatasetsDict = {
        # "ZJet_amcatnlo_ptBinned" if do2016 else "ZJet_jetAndPtBinned",
        "ZJet_amcatnlo_ptBinned" : [
            #FIXME: add inclusive stitched here; need to apply LHE cut in PSK step
            inputListBkgBase+"DYJetsToLL_LHEFilterPtZ-0To50_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"DYJetsToLL_LHEFilterPtZ-100To250_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"DYJetsToLL_LHEFilterPtZ-250To400_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"DYJetsToLL_LHEFilterPtZ-400To650_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"DYJetsToLL_LHEFilterPtZ-50To100_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"DYJetsToLL_LHEFilterPtZ-650ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            ],
        "TTbar_powheg" : [
            inputListBkgBase+"TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_APV.txt",
            inputListBkgBase+"TTToHadronic_TuneCP5_13TeV-powheg-pythia8_APV.txt",
            inputListBkgBase+"TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_APV.txt",
            ],
        "QCDFakes_DATA" : [
            #inputListQCDBase+"SinglePhoton_Run2016B-ver1_HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016B-ver2_HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016C-HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016D-HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016E-HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016F-HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            ],
        "DIBOSON_nlo" : [
            #inputListBkgBase+"WWTo4Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"WWTo1L1Nu2Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_APV.txt",
            inputListBkgBase+"ZZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"ZZTo4L_TuneCP5_13TeV_powheg_pythia8_APV.txt",
            #inputListBkgBase+"ZZTo2Nu2Q_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"ZZTo2L2Nu_TuneCP5_13TeV_powheg_pythia8_APV.txt",
            inputListBkgBase+"WZTo1L3Nu_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            #inputListBkgBase+"WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"WZTo3LNu_mllmin4p0_TuneCP5_13TeV-powheg-pythia8_APV.txt",
            inputListBkgBase+"WZTo1L1Nu2Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"WZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            ],
        "TRIBOSON" : [
            inputListBkgBase+"WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8_APV.txt",
            inputListBkgBase+"WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8_APV.txt",
            inputListBkgBase+"WZZ_TuneCP5_13TeV-amcatnlo-pythia8_APV.txt",
            inputListBkgBase+"ZZZ_TuneCP5_13TeV-amcatnlo-pythia8_APV.txt",
            ],
        "TTW" : [
            inputListBkgBase+"TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_APV.txt",
            inputListBkgBase+"TTWJetsToQQ_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_APV.txt",
            ],
        "TTZ" : [
            inputListBkgBase+"ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8_APV.txt"
            ],
        "SingleTop" : [
            inputListBkgBase+"ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8_APV.txt",
            inputListBkgBase+"ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8_APV.txt",
            inputListBkgBase+"ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8_APV.txt",
            inputListBkgBase+"ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8_APV.txt",
            inputListBkgBase+"ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8_APV.txt",
            ],
        "WJet_amcatnlo_jetBinned" : [
            #inputListBkgBase+"WJetsToLNu_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"WJetsToLNu_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"WJetsToLNu_2J_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            ],
        # "WJet_amcatnlo_ptBinned" : [
        #     inputListBkgBase+"WJetsToLNu_Wpt-0To50_ext1_amcatnloFXFX_pythia8.txt",
        #     inputListBkgBase+"WJetsToLNu_Wpt-50To100_ext1_amcatnloFXFX_pythia8.txt",
        #     inputListBkgBase+"WJetsToLNu_Pt-100To250_amcatnloFXFX_pythia8.txt",
        #     inputListBkgBase+"WJetsToLNu_Pt-250To400_amcatnloFXFX_pythia8.txt",
        #     inputListBkgBase+"WJetsToLNu_Pt-400To600_amcatnloFXFX_pythia8.txt",
        #     inputListBkgBase+"WJetsToLNu_Pt-600ToInf_amcatnloFXFX_pythia8.txt",
        #     ],
        "PhotonJets_Madgraph" : [
            #inputListBkgBase+"GJets_HT-40To100_madgraphMLM.txt",
            #inputListBkgBase+"GJets_DR-0p4_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8_APV.txt",
            inputListBkgBase+"GJets_DR-0p4_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8_APV.txt",
            inputListBkgBase+"GJets_DR-0p4_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_APV.txt",
            inputListBkgBase+"GJets_DR-0p4_HT-600ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_APV.txt",
            ],
}
# these are the same as what comes out of combinePlots.py (i.e., in the log file)
# TODO: need a better way to handle these, since we have one per MC dataset per era
# these are the numbers for 2016preVFP
backgroundDatasetsWeightsTimesOneThousand = {
        # "WJet_amcatnlo_jetBinned" : [0.339337935899, 0.172310335826, 0.0213606587798],
        "DYJetsToLL_LHEFilterPtZ-0To50" : 0.021726730863031958,
        "DYJetsToLL_LHEFilterPtZ-50To100" : 0.025064604525446715,
        "DYJetsToLL_LHEFilterPtZ-100To250" : 0.07211723680772729,
        "DYJetsToLL_LHEFilterPtZ-250To400" : 0.3631713593571083,
        "DYJetsToLL_LHEFilterPtZ-400To650" : 2.7640426378581,
        "DYJetsToLL_LHEFilterPtZ-650ToInf" : 2.6009925367576185,
        "TTTo2L2Nu" : 0.5422378354048237,
        "TTToHadronic" : 0.2057141832229361,
        "TTToSemiLeptonic" : 0.15263263511758648,
        "WWTo4Q" : 0.6031769551957746,
        "WWTo1L1Nu2Q" : 0.5765899794274886,
        "WWTo2L2Nu" : 7.098486588699867,
        "ZZTo2Q2L" : 0.8148904888893352,
        "ZZTo4L" : 0.3924880722370425,
        "ZZTo2Q2Nu" : 4.741912907584,
        "ZZTo2L2Nu" : 1.156611399883397,
        "WZTo1L3Nu" : 9.556878431787064,
        "WZTo3LNu" : 1.2480885221564577,
        "WZTo1L1Nu2Q" : 3.1988189341324067,
        "WZTo2Q2L" : 0.8332744398078211,
        "ST_tW_top_5f_NoFullyHadronicDecays" : 6.54023482395406,
        "ST_tW_antitop_5f_NoFullyHadronicDecays" : 6.770595340491985,
        "ST_t-channel_top_5f_InclusiveDecays" : 0.3888019701337022,
        "ST_t-channel_antitop_5f_InclusiveDecays" : 0.8914813248256295,
        "ST_s-channel_4f_leptonDecays" : 3.531858580867974,
        "WJetsToLNu_0J" : 0.11534942487801471,
        "WJetsToLNu_1J" : 0.022149605942692937,
        "WJetsToLNu_2J" : 0.030243327737861578,
        #"WJetsToLNu_Wpt-0To50" : ,
        #"WJetsToLNu_Wpt-50To100" : ,
        #"WJetsToLNu_Pt-100To250" : ,
        #"WJetsToLNu_Pt-250To400" : ,
        #"WJetsToLNu_Pt-400To600" : ,
        #"WJetsToLNu_Pt-600ToInf" : ,
        #"GJets_HT-40To100_madgraphMLM" : ,
        "GJets_DR-0p4_HT-100To200" : 19363.224190483783,
        "GJets_DR-0p4_HT-200To400" : 1500.595696952784,
        "GJets_DR-0p4_HT-400To600" : 595.9989369170503,
        "GJets_DR-0p4_HT-600ToInf" : 204.73599765017784,
        "WWW_4F" : 3.7565470916392854,
        "WWZ" : 3.8430110810408156,
        "WZZ" : 3.609874928733453,
        "ZZZ" : 3.6753630353517175,
        "TTWJetsToLNu" : 4.417684294295639,
        "TTWJetsToQQ" : 46.303705837605165,
        "ttZJets" : 0.6715438141903278,
        "SinglePhoton_Run2016H-02Apr2020-v1" : 1000.0,
        "SinglePhoton_Run2016G-02Apr2020-v1" : 1000.0,
        "SinglePhoton_Run2016F-02Apr2020-v1" : 1000.0,
        "SinglePhoton_Run2016E-02Apr2020-v1" : 1000.0,
        "SinglePhoton_Run2016D-02Apr2020-v1" : 1000.0,
        "SinglePhoton_Run2016C-02Apr2020-v1" : 1000.0,
        "SinglePhoton_Run2016B-02Apr2020_ver2-v1" : 1000.0,
        "SinglePhoton_Run2016B-ver2_HIPM_UL2016_MiniAODv2_NanoAODv9-v2" : 1000.0,
        "SinglePhoton_Run2016C-HIPM_UL2016_MiniAODv2_NanoAODv9-v2" : 1000.0,
        "SinglePhoton_Run2016D-HIPM_UL2016_MiniAODv2_NanoAODv9-v2" : 1000.0,
        "SinglePhoton_Run2016E-HIPM_UL2016_MiniAODv2_NanoAODv9-v2" : 1000.0,
        "SinglePhoton_Run2016F-HIPM_UL2016_MiniAODv2_NanoAODv9-v2" : 1000.0,
}
inputListSignalBase = inputListBkgBase
signalNameTemplate = "LQToDEle_M-{}_pair_bMassZero_TuneCP2_13TeV-madgraph-pythia8_APV"
allSignalDatasetsDict = {}
massList = list(range(300, 3100, 100))
massList.extend([3500, 4000])
for mass in massList:
    signalName = signalNameTemplate.format(mass)
    allSignalDatasetsDict[signalName] = [inputListSignalBase+signalName+".txt"]
allSignalDatasetsWeightsTimesOneThousand = {
        "LQToDEle_M-2000_pair" : 100.32078465133672,
        "LQToDEle_M-1900_pair" : 107.72178754828693,
        "LQToDEle_M-1800_pair" : 116.72402114444189,
        "LQToDEle_M-1700_pair" : 124.00613950112923,
        "LQToDEle_M-1600_pair" : 129.7489507060356,
        "LQToDEle_M-1500_pair" : 135.92343625640598,
        "LQToDEle_M-1400_pair" : 140.87231556094815,
        "LQToDEle_M-1300_pair" : 144.73563520740947,
        "LQToDEle_M-1200_pair" : 146.30880607495675,
        "LQToDEle_M-1100_pair" : 148.6728586083759,
        "LQToDEle_M-1000_pair" : 151.53234516258746,
        "LQToDEle_M-900_pair" : 150.03888045676996,
        "LQToDEle_M-800_pair" : 149.74910520889452,
        "LQToDEle_M-700_pair" : 149.21704401503297,
        "LQToDEle_M-600_pair" : 149.42342186166195,
        "LQToDEle_M-500_pair" : 146.66723622777104,
        "LQToDEle_M-400_pair" : 148.62651103075146,
        "LQToDEle_M-300_pair" : 146.31523345814628,
}
result_list = []
logString = "INFO: running {} parallel jobs for {} separate LQ masses requested..."


def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)
    sys.stdout.write("\r"+logString.format(jobCount, len(lqMassesToUse)))
    sys.stdout.write("\t"+str(len(result_list))+" jobs done")
    sys.stdout.flush()


def FindWeight(fullDatasetName, weightsDict):
    for key in weightsDict.keys():
        if key in fullDatasetName:
            return weightsDict[key]
        elif key in fullDatasetName.replace("_APV", ""):
            return weightsDict[key]
    raise RuntimeError("Could not find matching key in weightsDict for dataset={}; also tried {}. keys in dict {}".format(fullDatasetName, fullDatasetName.replace("_APV", ""), weightsDict.keys()))


def LoadChainFromTxtFile(txtFile):
    if not os.path.isfile(txtFile):
        raise RuntimeError("File {} does not exist!".format(txtFile))
    fc = TFileCollection("dum","",txtFile)
    if fc.GetNFiles() <= 0:
        raise RuntimeError("Got <= 0 files loaded into the TFileCollection for {}!".format(txtFile))
    ch = TChain("rootTupleTree/tree")
    ch.AddFileInfoList(fc.GetList())
    # ch.SetBranchStatus("*", 0)
    # for branchName in neededBranches:
    #     ch.SetBranchStatus(branchName, 1)
    if ch.GetEntries() <= 0:
        print("WARNING: Got <= 0 entries for dataset={}; returning None!".format(txtFile))
        return None
    else:
        print("INFO: Got {} entries for dataset={}".format(ch.GetEntries(), txtFile))
    return ch


def LoadDatasets(datasetDict, weightsTimes1kDict, neededBranches, signal=False, loader=None, lqMass=None, nLQPoints=1):
    nTotEvents = 0
    if loader is None:
        totalTChain = TChain("rootTupleTree/tree")
    for key, value in datasetDict.items():
        print("Loading tree for dataset={}; signal={}".format(key, signal))
        if isinstance(value, list):
            # print(value)
            nSampleTotEvents = 0
            for count, txtFile in enumerate(value):
                # print("Add file={} to collection".format(txtFile))
                txtFile = txtFile.format(lqMass)
                ch = LoadChainFromTxtFile(txtFile)
                if ch is None:
                    continue
                nSampleTotEvents+=ch.GetEntries()
                #weight = weightsTimes1kDict[os.path.basename(txtFile).replace(".txt", "")]/1000.0
                weight = FindWeight(os.path.basename(txtFile).replace(".txt", ""), weightsTimes1kDict)/1000.0
                if loader is not None:
                    if signal:
                        loader.AddSignalTree    ( ch, weight )
                    else:
                        loader.AddBackgroundTree( ch, weight/nLQPoints )
                    print("Loaded tree from file {} with {} events.".format(txtFile, ch.GetEntries()))
                else:
                    totalTChain.Add(ch)
            print("Loaded tree for sample {} with {} entries.".format(key, nSampleTotEvents))
            nTotEvents+=nSampleTotEvents
        else:
            txtFile = value
            txtFile = txtFile.format(lqMass)
            ch = LoadChainFromTxtFile(txtFile)
            if ch is None:
                continue
            nSampleTotEvents = ch.GetEntries()
            #weight = weightsTimes1kDict[os.path.basename(txtFile).replace(".txt", "")]/1000.0
            weight = FindWeight(os.path.basename(txtFile).replace(".txt", ""), weightsTimes1kDict)/1000.0
            if loader is not None:
                if signal:
                    loader.AddSignalTree    ( ch, weight )
                else:
                    loader.AddBackgroundTree( ch, weight/nLQPoints )
            else:
                totalTChain.Add(ch)
            print("Loaded tree for sample {} with {} entries.".format(key, nSampleTotEvents))
            nTotEvents+=nSampleTotEvents
    print("Total: loaded tree with {} entries.".format(nTotEvents))
    sys.stdout.flush()
    if loader is None:
        return totalTChain


def TrainBDT(args):
    lqMassToUse = args[0]
    # just one use the single LQ signal specified by mass just above
    try:
        signalDatasetsDict = {}
        signalDatasetsWeightsTimesOneThousand = {}
        signalDatasetName = signalNameTemplate.format(lqMassToUse)
        #for key in allSignalDatasetsDict:
        #    if signalNameTemplate.format(lqMassToUse) == key:
        #        signalDatasetsDict[key] = allSignalDatasetsDict[key]
        #        signalDatasetsWeightsTimesOneThousand[key] = allSignalDatasetsWeightsTimesOneThousand[key]
        signalDatasetsDict[signalDatasetName] = allSignalDatasetsDict[signalDatasetName]
        signalDatasetsWeightsTimesOneThousand[signalDatasetName] = allSignalDatasetsWeightsTimesOneThousand[signalDatasetName]
        print(signalDatasetsDict)
        print(signalDatasetsWeightsTimesOneThousand)
        
        outputFile = TFile.Open("TMVA_ClassificationOutput_"+signalDatasetName+".root", "RECREATE")
        
        TMVA.Tools.Instance()
        factory = TMVA.Factory("TMVAClassification_"+signalDatasetName, outputFile, "!V:ROC:!Silent:Color:DrawProgressBar:AnalysisType=Classification")
        
        loader = TMVA.DataLoader("dataset")
        LoadDatasets(backgroundDatasetsDict, backgroundDatasetsWeightsTimesOneThousand, neededBranches, signal=False, loader=loader, lqMass=lqMassToUse)
        LoadDatasets(signalDatasetsDict, signalDatasetsWeightsTimesOneThousand, neededBranches, signal=True, loader=loader, lqMass=lqMassToUse)
        
        #  Set individual event weights (the variables must exist in the original TTree)
        # if(analysisYear < 2018 && hasBranch("PrefireWeight") && !isData()) --> prefire weight
        loader.SetBackgroundWeightExpression( eventWeightExpression )
        loader.SetSignalWeightExpression( eventWeightExpression )
        
        # define variables
        #loader.AddVariable( "myvar1 := var1+var2", 'F' )
        #loader.AddVariable( "myvar2 := var1-var2", "Expression 2", "", 'F' )
        #loader.AddVariable( "var3",                "Variable 3", "units", 'F' )
        #loader.AddVariable( "var4",                "Variable 4", "units", 'F' )
        #
        #loader.AddSpectator( "spec1 := var1*2",  "Spectator 1", "units", 'F' )
        #loader.AddSpectator( "spec2 := var1*3",  "Spectator 2", "units", 'F' )
        for var in variableList:
            loader.AddVariable(var, "F")
        
        # Tell the factory how to use the training and testing events
        #
        # If no numbers of events are given, half of the events in the tree are used
        # for training, and the other half for testing:
        # loader.PrepareTrainingAndTestTree( mycuts, mycutb, "V:SplitMode=random:NormMode=None:VerboseLevel=Debug" )
        # loader.PrepareTrainingAndTestTree( mycuts, mycutb, "!V:SplitMode=random:NormMode=NumEvents" )
        # loader.PrepareTrainingAndTestTree( mycuts, mycutb, "V:SplitMode=random:NormMode=EqualNumEvents:VerboseLevel=Debug" )
        loader.PrepareTrainingAndTestTree( mycuts, mycutb, "V:SplitMode=random:NormMode=EqualNumEvents" )
        # To also specify the number of testing events, use:
        # loader.PrepareTrainingAndTestTree( mycut,
        #                                         "NSigTrain=3000:NBkgTrain=3000:NSigTest=3000:NBkgTest=3000:SplitMode=Random:!V" )
        # loader.PrepareTrainingAndTestTree( mycuts, mycutb,
        #                                     "nTrain_Signal=4000:nTrain_Background=2000:SplitMode=Random:NormMode=NumEvents:!V" )
        
        # Boosted Decision Trees
        # factory.BookMethod(loader,TMVA.Types.kBDT, "BDT",
        #         "V:NTrees=400:MinNodeSize=2.5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20" )
        # factory.BookMethod(loader,TMVA.Types.kBDT, "BDT",
        #         "!V:NTrees=800:MinNodeSize=2.5%:MaxDepth=2:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20" )
        factory.BookMethod(loader, TMVA.Types.kBDT, "BDTG",
                # "!H:!V:NTrees=400:MinNodeSize=2.5%:MaxDepth=1:BoostType=Grad:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20:NegWeightTreatment=Pray" )
                # "!H:!V:NTrees=400:MinNodeSize=2.5%:MaxDepth=1:BoostType=Grad:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20:NegWeightTreatment=IgnoreNegWeightsInTraining" )
                "!H:!V:BoostType=Grad:DoBoostMonitor:NegWeightTreatment=IgnoreNegWeightsInTraining:SeparationType=GiniIndex:NTrees=850:MinNodeSize=2.5%:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=3:CreateMVAPdfs:NbinsMVAPdf=20" )  # LQ2
                # "!H:!V:BoostType=Grad:DoBoostMonitor:NegWeightTreatment=Pray:SeparationType=GiniIndex:NTrees=850:MinNodeSize=2.5%:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=3:CreateMVAPdfs:NbinsMVAPdf=20" )  # LQ2 but use neg. weights in training
        
        factory.TrainAllMethods()
        factory.TestAllMethods()
        factory.EvaluateAllMethods()
        
        c1 = factory.GetROCCurve(loader)
        # c1.Draw()
        c1.Write("rocCurve_lqm"+str(lqMassToUse)+".png")
        
        outputFile.Close()
    except Exception as e:
        print("ERROR: exception in TrainBDT for lqMass={}".format(lqMassToUse))
        traceback.print_exc()
        raise e

    return True


def TrainParametrizedBDT(lqMassList):
   outputFile = TFile.Open("TMVA_ClassificationOutput.root", "RECREATE")
   
   TMVA.Tools.Instance()
   factory = TMVA.Factory("TMVAClassification", outputFile, "!V:ROC:!Silent:Color:DrawProgressBar:AnalysisType=Classification")
   
   loader = TMVA.DataLoader("dataset")
   for lqMass in lqMassList:
       LoadDatasets(backgroundDatasetsDict, backgroundDatasetsWeightsTimesOneThousand, neededBranches, signal=False, loader=loader, lqMass=lqMass, nLQPoints=len(lqMassList))
       signalDatasetName = signalNameTemplate.format(lqMass)
       signalDatasetsDict = {}
       signalDatasetsWeightsTimesOneThousand = {}
       signalDatasetsDict[signalDatasetName] = allSignalDatasetsDict[signalDatasetName]
       #signalDatasetsWeightsTimesOneThousand[signalDatasetName] = FindWeight(signalDatasetName, allSignalDatasetsWeightsTimesOneThousand)
       #LoadDatasets(signalDatasetsDict, signalDatasetsWeightsTimesOneThousand, neededBranches, signal=True, loader=loader, lqMass=lqMass)
       LoadDatasets(signalDatasetsDict, allSignalDatasetsWeightsTimesOneThousand, neededBranches, signal=True, loader=loader, lqMass=lqMass)
   
   #  Set individual event weights (the variables must exist in the original TTree)
   # if(analysisYear < 2018 && hasBranch("PrefireWeight") && !isData()) --> prefire weight
   loader.SetBackgroundWeightExpression( eventWeightExpression )
   loader.SetSignalWeightExpression( eventWeightExpression )
   
   for var in variableList:
       loader.AddVariable(var, "F")
   
   loader.PrepareTrainingAndTestTree( mycuts, mycutb, "V:SplitMode=random:NormMode=EqualNumEvents" )
   factory.BookMethod(loader, TMVA.Types.kBDT, "BDTG",
           "!H:!V:BoostType=Grad:DoBoostMonitor:NegWeightTreatment=IgnoreNegWeightsInTraining:SeparationType=GiniIndex:NTrees=850:MinNodeSize=2.5%:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=3:CreateMVAPdfs:NbinsMVAPdf=20" )  # LQ2
   
   factory.TrainAllMethods()
   factory.TestAllMethods()
   factory.EvaluateAllMethods()
   
   c1 = factory.GetROCCurve(loader)
   # c1.Draw()
   c1.Write("rocCurve.png")
   
   outputFile.Close()


def GetSignalTotalEventsHist(lqMassToUse, signalDict):
    signalDatasetName = signalNameTemplate.format(lqMassToUse)
    txtFiles = signalDict[signalDatasetName]
    # profName = "EventsPassingCuts_unscaled"
    hist = None
    histName = "savedHists/EventCounter"
    tfiles = []
    for count, txtFile in enumerate(txtFiles):
        txtFile = txtFile.format(lqMassToUse)
        with open(os.path.expandvars(txtFile), "r") as theTxtFile:
            for line in theTxtFile:
                line = line.strip()
                # print("GetSignalTotalEventsHist() Opening file='{}'".format(line))
                tfile = TFile.Open(os.path.expandvars(line))
                tfiles.append(tfile)
                unscaledEvtsHist = tfile.Get(histName)
                if not unscaledEvtsHist or unscaledEvtsHist.ClassName() != "TH1D":
                    unscaledEvtsHist = tfile.Get("EventCounter")
                    if unscaledEvtsHist.ClassName() != "TH1D":
                        raise RuntimeError("Expected class TH1D for object names {} but class is '{}' instead.".format(histName, unscaledEvtsHist.ClassName()))
                unscaledEvtsHist.SetDirectory(0)
                if hist is None:
                    hist = unscaledEvtsHist
                else:
                    hist.Add(unscaledEvtsHist)
    for tfile in tfiles:
        tfile.Close()
    return hist


def GetSignalTotalEvents(lqMassToUse):
    hist = GetSignalTotalEventsHist(lqMassToUse, allSignalDatasetsDict)
    # for TProfiles
    # unscaledTotalEvts = prof.GetBinContent(1)*prof.GetBinEntries(1)
    unscaledTotalEvts = hist.GetBinContent(1)
    return unscaledTotalEvts


def GetSignalSumWeights(lqMassToUse):
    hist = GetSignalTotalEventsHist(lqMassToUse, allSignalDatasetsDict)
    # for TProfiles
    # unscaledTotalEvts = prof.GetBinContent(1)*prof.GetBinEntries(1)
    sumWeights = hist.GetBinContent(3)
    return sumWeights


def EvaluateFigureOfMerit(nS, nB, efficiency, bkgEnts, figureOfMerit):
    # see: https://twiki.cern.ch/twiki/bin/view/CMS/FigureOfMerit
    # and https://arxiv.org/pdf/physics/0702156.pdf [1]
    try:
        # s/sqrt(s+b)
        # value = nS / ( math.sqrt ( nS + nB ) )
        if bkgEnts != 0:
            tau = bkgEnts / nB
        # switch to asymptotic formula
        # NB: this approximation doesn't work well with nB < ~ 5 events
        if figureOfMerit == "asymptotic":
            value = math.sqrt(2 * ((nS + nB) * math.log(1 + nS / nB) - nS))
        elif figureOfMerit == "punzi":
            # punzi
            a = 2  # nSigmasExclusion
            b = 5  # nSigmasDiscovery
            # value = efficiency / (nSigmas / 2.0 + math.sqrt(nB))
            smin = a**2/8 + 9*b**2/13 + a*math.sqrt(nB) + (b/2)*math.sqrt(b**2 + 4*a*math.sqrt(nB) + 4*nB)
            value = efficiency / smin
        elif figureOfMerit == "zbi":
            value = RooStats.NumberCountingUtils.BinomialWithTauExpZ(nS, nB, tau)
        elif figureOfMerit == "zpl":  # [1], eqn. 25
            nOff = bkgEnts
            nOn = nS + nB
            nTot = nOff + nOn
            value = math.sqrt(2)*math.sqrt(nOn*math.log(nOn*(1+tau)/nTot) + nOff*math.log(nOff*(1+tau)/(nTot*tau)))
        else:
            raise RuntimeError("Evaluation of '{}' as figure of merit is not implemented".format(figureOfMerit))
    except ZeroDivisionError:
        value = -999
    except ValueError:
        print("WARNING: had a domain error calculating the value with nS=", nS, "and nB=", nB)
        value = -999
    return value


def OptimizeBDTCut(args):
    bdtWeightFileName, lqMassToUse = args
    try:
        signalDatasetsDict = {}
        signalDatasetsWeightsTimesOneThousand = {}
        signalDatasetName = signalNameTemplate.format(lqMassToUse)
        signalDatasetsDict[signalDatasetName] = allSignalDatasetsDict[signalDatasetName]
        #signalDatasetsWeightsTimesOneThousand[signalDatasetName] = allSignalDatasetsWeightsTimesOneThousand[signalDatasetName]
        signalDatasetsWeightsTimesOneThousand[signalDatasetName] = FindWeight(signalDatasetName, allSignalDatasetsWeightsTimesOneThousand)
        print(signalDatasetsDict)
        print(signalDatasetsWeightsTimesOneThousand)
        TMVA.Tools.Instance()
        reader = TMVA.Reader("!Color:!Silent")
        varValueDict = {}
        for var in neededBranches:
            varValueDict[var] = array("f", [0])
        for var in variableList:
            reader.AddVariable(var, varValueDict[var])
        name = "BDTG"
        methodNames = [name]
        print("name={}, bdtWeightFileName={}".format(name, bdtWeightFileName))
        reader.BookMVA(name, bdtWeightFileName )

        hname = "hsig_" + name
        htitle = "Classifier Output for " + name
        hsig = TH1D(hname,htitle,10000,-1,1)
        hname = "hbkg_" + name
        #hbkg = ROOT.RDF.TH1DModel(hname,htitle,10000,-1,1)

        gInterpreter.ProcessLine(('''
        TMVA::Experimental::RReader BDT{}("{}");
        computeBDT{} = TMVA::Experimental::Compute<{}, float>(BDT{});
        ''').format(lqMassToUse, bdtWeightFileName, lqMassToUse, len(variableList), lqMassToUse))
        sys.stdout.flush()
        sys.stderr.flush()
        # backgrounds
        histName = "BDTOutputTotalBackground"
        bkgTotal = TH1D(histName, histName, 10000, -1, 1)
        bkgHists = []
        bkgTotIntegralOverCut = 0
        cutValForIntegral = 0.986
        for sample in backgroundDatasetsDict.keys():
            bkgSampleIntegralOverCut = 0
            bkgSampleIntegral = 0
            for idx, txtFile in enumerate(backgroundDatasetsDict[sample]):
                tchainBkg = LoadChainFromTxtFile(txtFile.format(lqMassToUse))
                if tchainBkg is None:
                    continue
                df = RDataFrame(tchainBkg)
                df = df.Filter(mycutb.GetTitle())  # will work for expressions valid in C++
                if "mass" in variableList:
                    df = df.Define("massInt", str(lqMassToUse))
                    df = df.Redefine("mass", "Numba::GetMassFloat(massInt)")
                # df = df.Define('BDTv', ROOT.computeBDT, ROOT.BDT.GetVariableNames())
                df = df.Define('BDTv', getattr(ROOT, "computeBDT{}".format(lqMassToUse)), getattr(ROOT, "BDT{}".format(lqMassToUse)).GetVariableNames())
                df = df.Define('BDT', 'BDTv[0]')
                df = df.Define('eventWeight', eventWeightExpression)
                histName = "BDTVal_{}_{}".format(sample, idx)
                hbkg = TH1D(histName, histName, 10000, -1, 1)
                histBkg = df.Histo1D(ROOT.RDF.TH1DModel(hbkg), "BDT", "eventWeight")
                #bkgWeight = backgroundDatasetsWeightsTimesOneThousand[os.path.basename(txtFile).replace(".txt", "")]/1000.0
                bkgWeight = FindWeight(os.path.basename(txtFile).replace(".txt", ""), backgroundDatasetsWeightsTimesOneThousand)/1000.0
                histBkg.Scale(bkgWeight)
                bkgTotal.Add(histBkg.GetPtr())
                #h = df.Histo1D(hbkg, "BDT", "eventWeight")
                #h.Draw()
                bkgIntegral = df.Sum("eventWeight").GetValue()*bkgWeight
                bkgIntegralOverCut = df.Filter("BDT > {}".format(cutValForIntegral)).Sum("eventWeight").GetValue()*bkgWeight
                bkgEntriesOverCut = df.Filter("BDT > {}".format(cutValForIntegral)).Count().GetValue()
                print("subsample={}, bkgWeight={}".format(txtFile, bkgWeight))
                print("subsample={}, entries = {}, integral unweighted = {}, integral weighted = {}".format(txtFile, histBkg.GetPtr().GetEntries(), histBkg.GetPtr().Integral()/bkgWeight, histBkg.GetPtr().Integral()))
                print("subsample={}, df entries = {}, df integral unweighted = {}, df integral weighted = {}".format(txtFile, df.Count().GetValue(), df.Sum("eventWeight").GetValue(), df.Sum("eventWeight").GetValue()*bkgWeight))
                print("subsample={}, entries with BDT > {} = {}, integral unweighted = {}, integral weighted = {}".format(txtFile, cutValForIntegral, bkgEntriesOverCut, bkgIntegralOverCut/bkgWeight, bkgIntegralOverCut))
                sys.stdout.flush()
                # print some entries
                cols = ROOT.vector('string')()
                cols.push_back("run")
                cols.push_back("event")
                cols.push_back("ls")
                cols.push_back("eventWeight")
                cols.push_back("BDT")
                d2 = df.Display(cols)
                d2.Print()
                # if "photon" in txtFile.lower() and bkgIntegralOverCut > 0:
                #     cols = ROOT.vector('string')()
                #     cols.push_back("run")
                #     cols.push_back("ls")
                #     cols.push_back("event")
                #     cols.push_back("BDT")
                #     cols.push_back("eventWeight")
                #     display = df.Filter("BDT > {}".format(cutValForIntegral)).Display(cols, 20)
                #     print("subsample={}, entries over BDT cut unweighted = {}".format(txtFile, display.Print()))
                #     sys.stdout.flush()
                bkgTotIntegralOverCut += bkgIntegralOverCut
                bkgSampleIntegralOverCut += bkgIntegralOverCut
                bkgSampleIntegral += bkgIntegral
            print("sample={}, events = {}".format(sample, bkgSampleIntegral))
            print("sample={}, events over BDT cut = {}".format(sample, bkgSampleIntegralOverCut))
            sys.stdout.flush()
            print()
            sys.stdout.flush()
        print("bkgIntegralOverCut={}".format(bkgIntegralOverCut))
        sys.stdout.flush()

        # signal
        tchainSig = LoadDatasets(signalDatasetsDict, signalDatasetsWeightsTimesOneThousand, neededBranches, signal=True, loader=None, lqMass=lqMassToUse)
        dfSig = RDataFrame(tchainSig)
        dfSig = dfSig.Filter(mycuts.GetTitle())  # will work for expressions valid in C++
        # dfSig = dfSig.Define('BDTv', ROOT.computeBDT, ROOT.BDT.GetVariableNames())
        dfSig = dfSig.Define('BDTv', getattr(ROOT, "computeBDT{}".format(lqMassToUse)), getattr(ROOT, "BDT{}".format(lqMassToUse)).GetVariableNames())
        dfSig = dfSig.Define('BDT', 'BDTv[0]')
        dfSig = dfSig.Define('eventWeight', eventWeightExpression)
        histSig = dfSig.Histo1D(ROOT.RDF.TH1DModel(hsig), "BDT", "eventWeight")
        signalWeight = signalDatasetsWeightsTimesOneThousand[signalDatasetName]/1000.0
        histSig.Scale(signalWeight)

        # print some entries
        # cols = ROOT.vector('string')()
        # cols.push_back("BDT")
        # cols.push_back("eventWeight")
        # d2 = dfSig.Display(cols)
        # d2.Print()
        print("totalSignal=", histSig.Integral())
        print("totalBackground=", bkgTotal.Integral())

        # now optimize
        #totalSignalEventsUnscaled = GetSignalTotalEvents(lqMassToUse)
        sumWeights = GetSignalSumWeights(lqMassToUse)
        fomValueToCutInfoDict = {}
        for iBin in range(1, hbkg.GetNbinsX()+1):
            nS = histSig.Integral(iBin, hsig.GetNbinsX())
            efficiency = nS/(signalWeight*sumWeights)
            nB = bkgTotal.Integral(iBin, hbkg.GetNbinsX())
            cutVal = histSig.GetBinLowEdge(iBin)
            # if nB < 3:
            # if nS < 5:
            #      fomValueToCutInfoDict[iBin] = [-1.0, cutVal, nS, efficiency, nB]
            #      continue
            fom = EvaluateFigureOfMerit(nS, nB, efficiency, 0, "punzi")
            #fomValueToCutInfoDict[fom] = [cutVal, nS, nB, efficiency]
            fomValueToCutInfoDict[iBin] = [fom, cutVal, nS, efficiency, nB]
        # cutVals = np.linspace(-1, 1, 10000)
        # for i in range(len(cutVals)-1):
        #     cutVal = cutVals[i]
        #     nB = df.Filter("BDT > {}".format(cutVal)).Sum("eventWeight").GetValue()
        #     nS = dfSig.Filter("BDT > {}".format(cutVal)).Sum("eventWeight").GetValue()
        #     efficiency = nS/totalSignalEventsUnscaled #FIXME?
        #     fom = EvaluateFigureOfMerit(nS, nB, efficiency, 0, "punzi")
        #     fomValueToCutInfoDict[fom] = [cutVal, nS, nB, efficiency]
        # sortedDict = OrderedDict(sorted(fomValueToCutInfoDict.items(), key=lambda t: t[0], reverse=True))
        sortedDict = OrderedDict(sorted(fomValueToCutInfoDict.items(), key=lambda t: float(t[1][0]), reverse=True))
        # idx = 0
        # for key, value in sortedDict.items():
        #     print("FOM: ibin={} with FOM={}, cutVal={}, nS={}, eff={}, nB={}".format(key, *value))
        #     if idx > 100:
        #         break
        #     idx+=1
        # now the max FOM value should be the first entry
        maxVal = next(iter(sortedDict.items()))
        #print("max FOM: {} with cutVal={}, nS={}, eff={}, nB={}".format(maxVal[0], *maxVal[1]))
        print("For lqMass={}, max FOM: ibin={} with FOM={}, cutVal={}, nS={}, eff={}, nB={}".format(lqMassToUse, maxVal[0], *maxVal[1]))
        # testVals=list(fomValueToCutInfoDict.items())
        # testVal=testVals[9949]
        # print("test FOM: ibin={} with FOM={}, cutVal={}, nS={}, eff={}, nB={}".format(testVal[0], *testVal[1]))
        # testVal=testVals[9948]
        # print("test FOM: ibin={} with FOM={}, cutVal={}, nS={}, eff={}, nB={}".format(testVal[0], *testVal[1]))
        # testVal=testVals[9950]
        # print("test FOM: ibin={} with FOM={}, cutVal={}, nS={}, eff={}, nB={}".format(testVal[0], *testVal[1]))
    except Exception as e:
        print("ERROR: exception in OptimizeBDTCut for lqMass={}".format(lqMassToUse))
        traceback.print_exc()
        raise e

    return True


@ROOT.Numba.Declare(["int"], "float")
def GetMassFloat(mass):
    return float(mass)


####################################################################################################
# Run
####################################################################################################
if __name__ == "__main__":
    gROOT.SetBatch()
    train = False
    optimize = True
    parallelize = True
    parametrized = True
    # lqMassesToUse = [1400, 1500, 1600, 1700]
    lqMassesToUse = list(range(1000, 2100, 100))
    # lqMassesToUse = list(range(300, 2100, 100))
    #lqMassesToUse = [300, 600, 900, 1200]
    #FIXME this should take the output of the training part
    # weightFile = os.getenv("LQANA")+"/versionsOfAnalysis/2016/nanoV7/eejj/mar24_2022_egLoose_BDT_qcd/train_14-17/dataset/weights/TMVAClassification_LQToDEle_M-{}_pair_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/baselineNoMasym/dataset/weights/TMVAClassification_LQToDEle_M-{}_pair_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/masymResult/dataset/weights/TMVAClassification_LQToDEle_M-{}_pair_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/removeMinv/dataset/weights/TMVAClassification_LQToDEle_M-{}_pair_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/lookAtMejs/dataset/weights/TMVAClassification_LQToDEle_M-{}_pair_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/removeMET/dataset/weights/TMVAClassification_LQToDEle_M-{}_pair_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/parametrizedBDT1400/dataset/weights/TMVAClassification_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/noMass1400/dataset/weights/TMVAClassification_LQToDEle_M-1400_pair_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/noParam1400olderTrees/dataset/weights/TMVAClassification_LQToDEle_M-1400_pair_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/redoBaseline/dataset/weights/TMVAClassification_LQToDEle_M-{}_pair_pythia8_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/redoParametrizedBDT1400and1500/dataset/weights/TMVAClassification_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/dedicatedBDTs1400to1700/dataset/weights/TMVAClassification_LQToDEle_M-{}_pair_pythia8_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/dedicatedBDTs1400to1700_3bkgEvts/dataset/weights/TMVAClassification_LQToDEle_M-{}_pair_pythia8_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/parametrizedBDTs1400to1700_3bkgEvts/dataset/weights/TMVAClassification_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/redoAgain_dedicatedBDTs/dataset/weights/TMVAClassification_LQToDEle_M-{}_pair_pythia8_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/redoAgain_parametrizedBDT1400to1700/dataset/weights/TMVAClassification_BDTG.weights.xml"
    # weightFile = "/tmp/scooper/parametrizedBDT300to2000/dataset/weights/TMVAClassification_BDTG.weights.xml"
    #weightFile = os.getenv("LQANA")+"/versionsOfOptimization/nanoV7/2016/bdt/egmLooseIDWithQCD/redoAgain_dedicatedBDTs/dataset/weights/TMVAClassification_LQToDEle_M-{}_pair_pythia8_BDTG.weights.xml"
    weightFile = os.getenv("LQANA")+"/versionsOfAnalysis/2016/eejj/eejj_1dec2022_preselOnly_eleSFsTrigSFsLead_ele27AndPhoton175_fromPSK_2016preVFP/bdt/dataset/weights/TMVAClassification_BDTG.weights.xml"
    
    if train:
        if parametrized:
            TrainParametrizedBDT(lqMassesToUse)
        else:
            if parallelize:
                # ncores = multiprocessing.cpu_count()
                ncores = 4  # only use 4 parallel jobs to be nice
                pool = multiprocessing.Pool(ncores)
                jobCount = 0
                for mass in lqMassesToUse:
                    try:
                        pool.apply_async(TrainBDT, [[mass]], callback=log_result)
                        jobCount += 1
                    except KeyboardInterrupt:
                        print("\n\nCtrl-C detected: Bailing.")
                        pool.terminate()
                        exit(-1)
                    except Exception as e:
                        print("ERROR: caught exception in job for LQ mass: {}; exiting".format(mass))
                        traceback.print_exc()
                        exit(-2)
                
                # now close the pool and wait for jobs to finish
                pool.close()
                sys.stdout.write(logString.format(jobCount, len(lqMassesToUse)))
                sys.stdout.write("\t"+str(len(result_list))+" jobs done")
                sys.stdout.flush()
                pool.join()
                # check results?
                if len(result_list) < jobCount:
                    raise RuntimeError("ERROR: {} jobs had errors. Exiting.".format(jobCount-len(result_list)))
            else:
                for mass in lqMassesToUse:
                    TrainBDT([mass])
    
    if optimize:
        if parallelize:
            # ncores = multiprocessing.cpu_count()
            ncores = 4  # only use 4 parallel jobs to be nice
            pool = multiprocessing.Pool(ncores)
            jobCount = 0
            for mass in lqMassesToUse:
                try:
                    pool.apply_async(OptimizeBDTCut, [[weightFile.format(mass), mass]], callback=log_result)
                    jobCount += 1
                except KeyboardInterrupt:
                    print("\n\nCtrl-C detected: Bailing.")
                    pool.terminate()
                    exit(-1)
                except Exception as e:
                    print("ERROR: caught exception in job for LQ mass: {}; exiting".format(mass))
                    traceback.print_exc()
                    exit(-2)
            
            # now close the pool and wait for jobs to finish
            pool.close()
            sys.stdout.write(logString.format(jobCount, len(lqMassesToUse)))
            sys.stdout.write("\t"+str(len(result_list))+" jobs done")
            sys.stdout.flush()
            pool.join()
            # check results?
            if len(result_list) < jobCount:
                raise RuntimeError("ERROR: {} jobs had errors. Exiting.".format(jobCount-len(result_list)))
        else:
            for mass in lqMassesToUse:
                OptimizeBDTCut([weightFile.format(mass), mass])
