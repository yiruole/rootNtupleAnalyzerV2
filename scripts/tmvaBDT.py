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
# datasets -- preselection skims
# inputListBkgBase = "$LQANA/config/nanoV7_2016_analysisPreselSkims_egLoose_4feb2022/"
# inputListQCDBase = "$LQANA/config/nanoV7_2016_pskQCDEEJJ_egLoose_24mar2022_comb/"
# inputListBkgBase = "/tmp/scooper/rdfDatasetInputLists_mee200st400_masym/"
# inputListQCDBase = "/tmp/scooper/rdfDatasetInputLists_mee200st400_masym/"
# inputListBkgBase = "/tmp/scooper/rdfDatasetInputLists_mee200st400_mejs/"
# inputListQCDBase = "/tmp/scooper/rdfDatasetInputLists_mee200st400_mejs/"
# inputListBkgBase = "/tmp/scooper/rdfDatasetInputLists_mee200st400_mejs_varList/{}/"
# inputListQCDBase = "/tmp/scooper/rdfDatasetInputLists_mee200st400_mejs_varList/{}/"
# inputListBkgBase = "/tmp/scooper/rdfDatasetInputLists_mee200st400_allLQ/{}/"
# inputListQCDBase = "/tmp/scooper/rdfDatasetInputLists_mee200st400_allLQ/{}/"
inputListBkgBase = os.getenv("LQANA")+"/config/rdfDatasetInputLists_mee200st400_allLQ/{}/"
inputListQCDBase = os.getenv("LQANA")+"/config/rdfDatasetInputLists_mee200st400_allLQ/{}/"
# HEEP
# inputListBkgBase = "$LQANA/config/nanoV7_2016_analysisPreselSkims_heep_2sep2021/"
# inputListQCDBase = "$LQANA/config/nanoV7_2016_pskQCDEEJJ_heep_6apr2022_comb/"
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
            #FIXME: commented out datasets with zero events; should handle this a bit better
            #       this came from the fact that the makeBDTTrainingTrees script doesn't write out files for trees with zero entries
            #inputListBkgBase+"WWTo4Q.txt",
            inputListBkgBase+"WWToLNuQQ.txt",
            inputListBkgBase+"WWTo2L2Nu.txt",
            inputListBkgBase+"ZZTo2L2Q_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"ZZTo4L_pythia8.txt",
            #inputListBkgBase+"ZZTo2Q2Nu_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"ZZTo2L2Nu_pythia8.txt",
            inputListBkgBase+"WZTo1L3Nu_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WZTo3LNu_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WZTo1L1Nu2Q_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WZTo2L2Q_amcatnloFXFX_pythia8.txt",
            ],
        "TRIBOSON" : [
            inputListBkgBase+"WWW_4F_pythia8.txt",
            inputListBkgBase+"WWZ_pythia8.txt",
            inputListBkgBase+"WZZ_pythia8.txt",
            inputListBkgBase+"ZZZ_pythia8.txt",
            ],
        "TTW" : [
            inputListBkgBase+"TTWJetsToLNu_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"TTWJetsToQQ_amcatnloFXFX_pythia8.txt",
            ],
        "TTZ" : [
            inputListBkgBase+"ttZJets_madgraphMLM.txt"
            ],
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
            #inputListBkgBase+"WJetsToLNu_Wpt-0To50_ext1_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WJetsToLNu_Wpt-50To100_ext1_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WJetsToLNu_Pt-100To250_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WJetsToLNu_Pt-250To400_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WJetsToLNu_Pt-400To600_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WJetsToLNu_Pt-600ToInf_amcatnloFXFX_pythia8.txt",
            ],
        "PhotonJets_Madgraph" : [
            #inputListBkgBase+"GJets_HT-40To100_madgraphMLM.txt",
            #inputListBkgBase+"GJets_HT-100To200_madgraphMLM.txt",
            inputListBkgBase+"GJets_HT-200To400_madgraphMLM.txt",
            inputListBkgBase+"GJets_HT-400To600_madgraphMLM.txt",
            inputListBkgBase+"GJets_HT-600ToInf_madgraphMLM.txt",
            ],
}
backgroundDatasetsWeightsTimesOneThousand = {
        # "WJet_amcatnlo_jetBinned" : [0.339337935899, 0.172310335826, 0.0213606587798],
        "DYJetsToLL_Zpt-0To50_amcatnloFXFX_pythia8" : 0.33620511942,
        "DYJetsToLL_Pt-50To100_amcatnloFXFX_pythia8" : 0.114625534835,
        "DYJetsToLL_Pt-100To250_amcatnloFXFX_pythia8" : 0.188510053163,
        "DYJetsToLL_Pt-250To400_amcatnloFXFX_pythia8" : 0.795115450687,
        "DYJetsToLL_Pt-400To650_amcatnloFXFX_pythia8" : 11.2325005129,
        "DYJetsToLL_Pt-650ToInf_amcatnloFXFX_pythia8" : 11.1756034925,
        "TTTo2L2Nu_pythia8" : 0.585547131056,
        "TTToHadronic_pythia8" : 0.572359028863,
        "TTToSemiLeptonic_pythia8" : 0.36631937923,
        "WWTo4Q" : 856.651276021,
        "WWToLNuQQ" : 207.201072147,
        "WWTo2L2Nu" : 198.802581291,
        "ZZTo2L2Q_amcatnloFXFX_pythia8" : 1.47221360112,
        "ZZTo4L_pythia8" : 0.475809997084,
        "ZZTo2Q2Nu_amcatnloFXFX_pythia8" : 0.728060423014,
        "ZZTo2L2Nu_pythia8" : 0.382723130896,
        "WZTo1L3Nu_amcatnloFXFX_pythia8" : 11.6251013241,
        "WZTo3LNu_amcatnloFXFX_pythia8" : 1.93599141046,
        "WZTo1L1Nu2Q_amcatnloFXFX_pythia8" : 0.910176137249,
        "WZTo2L2Q_amcatnloFXFX_pythia8" : 0.859835380036,
        "ST_tW_top_5f_inclusiveDecays_ext1_pythia8" : 184.936486294,
        "ST_tW_antitop_5f_inclusiveDecays_ext1_pythia8" : 185.462933288,
        "ST_t-channel_top_4f_inclusiveDecays" : 71.7704250605,
        "ST_t-channel_antitop_4f_inclusiveDecays" : 73.4648859745,
        "ST_s-channel_4f_InclusiveDecays_pythia8" : 12.2784973443,
        "WJetsToLNu_Wpt-0To50_ext1_amcatnloFXFX_pythia8" : 0.121230487882,
        "WJetsToLNu_Wpt-50To100_ext1_amcatnloFXFX_pythia8" : 0.197285449115,
        "WJetsToLNu_Pt-100To250_amcatnloFXFX_pythia8" : 0.145778733507,
        "WJetsToLNu_Pt-250To400_amcatnloFXFX_pythia8" : 1.4234006515,
        "WJetsToLNu_Pt-400To600_amcatnloFXFX_pythia8" : 9.54412611451,
        "WJetsToLNu_Pt-600ToInf_amcatnloFXFX_pythia8" : 9.17993794712,
        "GJets_HT-40To100_madgraphMLM" : 79724.6223759,
        "GJets_HT-100To200_madgraphMLM" : 32792.3855087,
        "GJets_HT-200To400_madgraphMLM" : 4027.44663672,
        "GJets_HT-400To600_madgraphMLM" : 1945.01356701,
        "GJets_HT-600ToInf_madgraphMLM" : 669.263854243,
        "WWW_4F_pythia8" : 149.598485516,
        "WWZ_pythia8" : 143.827579157,
        "WZZ_pythia8" : 145.307050001,
        "ZZZ_pythia8" : 143.285693969,
        "TTWJetsToLNu_amcatnloFXFX_pythia8" : 3.71148010247,
        "TTWJetsToQQ_amcatnloFXFX_pythia8" : 23.1528859117,
        "ttZJets_madgraphMLM" : 0.933902239753,
        "SinglePhoton_Run2016H-02Apr2020-v1" : 1000.0,
        "SinglePhoton_Run2016G-02Apr2020-v1" : 1000.0,
        "SinglePhoton_Run2016F-02Apr2020-v1" : 1000.0,
        "SinglePhoton_Run2016E-02Apr2020-v1" : 1000.0,
        "SinglePhoton_Run2016D-02Apr2020-v1" : 1000.0,
        "SinglePhoton_Run2016C-02Apr2020-v1" : 1000.0,
        "SinglePhoton_Run2016B-02Apr2020_ver2-v1" : 1000.0,
}
inputListSignalBase = inputListBkgBase
signalNameTemplate = "LQToDEle_M-{}_pair_pythia8"
allSignalDatasetsDict = {}
massList = list(range(300, 3100, 100))
massList.extend([3500, 4000])
for mass in massList:
    signalName = signalNameTemplate.format(mass)
    allSignalDatasetsDict[signalName] = [inputListSignalBase+signalName+".txt"]
allSignalDatasetsWeightsTimesOneThousand = {
        "LQToDEle_M-2000_pair_pythia8" : 0.0074746828,
        "LQToDEle_M-1900_pair_pythia8" : 0.0131129752,
        "LQToDEle_M-1800_pair_pythia8" : 0.0247234163522,
        "LQToDEle_M-1700_pair_pythia8" : 0.0423445802,
        "LQToDEle_M-1600_pair_pythia8" : 0.07639671,
        "LQToDEle_M-1500_pair_pythia8" : 0.140885576,
        "LQToDEle_M-1400_pair_pythia8" : 0.26362245,
        "LQToDEle_M-1300_pair_pythia8" : 0.501492394,
        "LQToDEle_M-1200_pair_pythia8" : 0.96553964,
        "LQToDEle_M-1100_pair_pythia8" : 1.93394864,
        "LQToDEle_M-1000_pair_pythia8" : 3.9561301,
        "LQToDEle_M-900_pair_pythia8" : 8.536346,
        "LQToDEle_M-800_pair_pythia8" : 19.4189010101,
        "LQToDEle_M-700_pair_pythia8" : 46.7285420202,
        "LQToDEle_M-600_pair_pythia8" : 125.387504098,
        "LQToDEle_M-500_pair_pythia8" : 359.38734,
        "LQToDEle_M-400_pair_pythia8" : 1300.53742,
        "LQToDEle_M-300_pair_pythia8" : 6027.09068,
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


def LoadChainFromTxtFile(txtFile):
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
                weight = weightsTimes1kDict[os.path.basename(txtFile).replace(".txt", "")]/1000.0
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
            weight = weightsTimes1kDict[os.path.basename(txtFile).replace(".txt", "")]/1000.0
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
       signalDatasetsWeightsTimesOneThousand[signalDatasetName] = allSignalDatasetsWeightsTimesOneThousand[signalDatasetName]
       LoadDatasets(signalDatasetsDict, signalDatasetsWeightsTimesOneThousand, neededBranches, signal=True, loader=loader, lqMass=lqMass)
   
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
        signalDatasetsWeightsTimesOneThousand[signalDatasetName] = allSignalDatasetsWeightsTimesOneThousand[signalDatasetName]
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
                bkgWeight = backgroundDatasetsWeightsTimesOneThousand[os.path.basename(txtFile).replace(".txt", "")]/1000.0
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
        totalSignalEventsUnscaled = GetSignalTotalEvents(lqMassToUse)
        fomValueToCutInfoDict = {}
        for iBin in range(1, hbkg.GetNbinsX()+1):
            nS = histSig.Integral(iBin, hsig.GetNbinsX())
            efficiency = nS/(signalWeight*totalSignalEventsUnscaled)  #FIXME?
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
    train = True
    optimize = True
    parallelize = True
    parametrized = False
    # lqMassesToUse = [1400, 1500, 1600, 1700]
    # lqMassesToUse = list(range(1000, 2100, 100))
    # lqMassesToUse = list(range(300, 2100, 100))
    lqMassesToUse = [300, 600, 900, 1200]
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
    weightFile = os.getenv("LQANA")+"/versionsOfOptimization/nanoV7/2016/bdt/egmLooseIDWithQCD/redoAgain_dedicatedBDTs/dataset/weights/TMVAClassification_LQToDEle_M-{}_pair_pythia8_BDTG.weights.xml"
    
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
                    print("ERROR: {} jobs had errors. Exiting.".format(jobCount-len(result_list)))
                    exit(-2)
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
                print("ERROR: {} jobs had errors. Exiting.".format(jobCount-len(result_list)))
                exit(-2)
        else:
            for mass in lqMassesToUse:
                OptimizeBDTCut([weightFile.format(mass), mass])
