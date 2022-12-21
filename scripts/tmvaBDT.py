#!/usr/bin/env python3
#
# see: https://github.com/lmoneta/tmva-tutorial/blob/master/notebooks/TMVA_Classification.ipynb
#      https://github.com/lmoneta/tmva-tutorial/blob/master/notebooks/TMVA_Reader_ManyMethods_py.ipynb

from array import array
from collections import OrderedDict
import sys
import os
import math
import multiprocessing
import traceback
import copy

from combineCommon import ParseXSectionFile, lookupXSection

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
#inputListBkgBase = os.getenv("LQANA")+"/config/bdt/inputList_bdtTraining_eejj_finalSels_egLoose_6dec2022_mee200st400_allLQ/{}/"
inputListBkgBase = os.getenv("LQANA")+"/config/bdt/inputList_UL16postVFP_bdtTraining_eejj_finalSels_egLoose_19dec2022_mee200st400_allLQ/{}/"
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
            inputListBkgBase+"DYJetsToLL_LHEFilterPtZ-0To50_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            inputListBkgBase+"DYJetsToLL_LHEFilterPtZ-100To250_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            inputListBkgBase+"DYJetsToLL_LHEFilterPtZ-250To400_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            inputListBkgBase+"DYJetsToLL_LHEFilterPtZ-400To650_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            inputListBkgBase+"DYJetsToLL_LHEFilterPtZ-50To100_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            inputListBkgBase+"DYJetsToLL_LHEFilterPtZ-650ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            ],
        "TTbar_powheg" : [
            inputListBkgBase+"TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8.txt",
            inputListBkgBase+"TTToHadronic_TuneCP5_13TeV-powheg-pythia8.txt",
            inputListBkgBase+"TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8.txt",
            ],
        "DIBOSON_nlo" : [
            #inputListBkgBase+"WWTo4Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            inputListBkgBase+"WWTo1L1Nu2Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            inputListBkgBase+"WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8.txt",
            inputListBkgBase+"ZZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            inputListBkgBase+"ZZTo4L_TuneCP5_13TeV_powheg_pythia8.txt",
            #inputListBkgBase+"ZZTo2Nu2Q_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            inputListBkgBase+"ZZTo2L2Nu_TuneCP5_13TeV_powheg_pythia8.txt",
            inputListBkgBase+"WZTo1L3Nu_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            #inputListBkgBase+"WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            inputListBkgBase+"WZTo3LNu_mllmin4p0_TuneCP5_13TeV-powheg-pythia8.txt",
            inputListBkgBase+"WZTo1L1Nu2Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            inputListBkgBase+"WZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            ],
        "TRIBOSON" : [
            inputListBkgBase+"WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8.txt",
            inputListBkgBase+"WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8.txt",
            inputListBkgBase+"WZZ_TuneCP5_13TeV-amcatnlo-pythia8.txt",
            inputListBkgBase+"ZZZ_TuneCP5_13TeV-amcatnlo-pythia8.txt",
            ],
        "TTW" : [
            inputListBkgBase+"TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8.txt",
            inputListBkgBase+"TTWJetsToQQ_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8.txt",
            ],
        "TTZ" : [
            inputListBkgBase+"ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8.txt"
            ],
        "SingleTop" : [
            inputListBkgBase+"ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8.txt",
            inputListBkgBase+"ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8.txt",
            inputListBkgBase+"ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8.txt",
            inputListBkgBase+"ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8.txt",
            inputListBkgBase+"ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8.txt",
            ],
        "WJet_amcatnlo_jetBinned" : [
            #inputListBkgBase+"WJetsToLNu_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            inputListBkgBase+"WJetsToLNu_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
            inputListBkgBase+"WJetsToLNu_2J_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt",
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
            #inputListBkgBase+"GJets_DR-0p4_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8.txt",
            inputListBkgBase+"GJets_DR-0p4_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8.txt",
            inputListBkgBase+"GJets_DR-0p4_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8.txt",
            inputListBkgBase+"GJets_DR-0p4_HT-600ToInf_TuneCP5_13TeV-madgraphMLM-pythia8.txt",
            ],
}
qcdFakes2016pre = {
        "QCDFakes_DATA" : [
            #inputListQCDBase+"SinglePhoton_Run2016B-ver1_HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016B-ver2_HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016C-HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016D-HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016E-HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016F-HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            ]
}
qcdFakes2016post = {
        "QCDFakes_DATA" : [
            inputListQCDBase+"SinglePhoton_Run2016H-UL2016_MiniAODv2_NanoAODv9-v1.txt",
            inputListQCDBase+"SinglePhoton_Run2016G-UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016F-UL2016_MiniAODv2_NanoAODv9-v1.txt",
            ]
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


def CalcWeight(fullDatasetName, intLumi, sumWeights):
    fullDatasetName = fullDatasetName.replace("_APV", "")
    xsec = float(lookupXSection(fullDatasetName))
    if xsec > 0:
        return intLumi*xsec/sumWeights
    else:
        return 1.0  # in the case of data


def LoadChainFromTxtFile(txtFile, console=None):
    txtFile = os.path.expandvars(txtFile)
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
        logString = "WARNING: Got <= 0 entries for dataset={}; returning None!".format(txtFile)
        if console is not None:
            console.print(logString)
        print(logString)
        return None
    else:
        logString = "INFO: Got {} entries for dataset={}".format(ch.GetEntries(), txtFile)
        if console is not None:
            console.print(logString)
        print(logString)
    return ch


def LoadDatasets(datasetDict, neededBranches, signal=False, loader=None, lqMass=None, nLQPoints=1):
    nTotEvents = 0
    if loader is None:
        totalTChain = TChain("rootTupleTree/tree")
    for key, value in datasetDict.items():
        print("Loading tree for dataset={}; signal={}".format(key, signal))
        if isinstance(value, list):
            # print(value)
            nSampleTotEvents = 0
            for count, txtFile in enumerate(value):
                txtFile = txtFile.format(lqMass)
                ch = LoadChainFromTxtFile(txtFile)
                if ch is None:
                    continue
                nSampleTotEvents+=ch.GetEntries()
                datasetName = os.path.basename(txtFile).replace(".txt", "")
                sumWeights = GetBackgroundSumWeights(datasetName, txtFile)
                weight = CalcWeight(datasetName, intLumi, sumWeights)
                print("Add file={} with weight*1000={} to collection".format(txtFile, weight*1000))
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
            datasetName = os.path.basename(txtFile).replace(".txt", "")
            sumWeights = GetBackgroundSumWeights(datasetName, txtFile)
            weight = CalcWeight(datasetName, intLumi, sumWeights)
            print("Add file={} with weight*1000={} to collection".format(txtFile, weight*1000))
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
        signalDatasetName = signalNameTemplate.format(lqMassToUse)
        signalDatasetsDict[signalDatasetName] = allSignalDatasetsDict[signalDatasetName]
        print(signalDatasetsDict)
        
        outputFile = TFile.Open("TMVA_ClassificationOutput_"+signalDatasetName+".root", "RECREATE")
        
        TMVA.Tools.Instance()
        factory = TMVA.Factory("TMVAClassification_"+signalDatasetName, outputFile, "!V:ROC:!Silent:Color:DrawProgressBar:AnalysisType=Classification")
        
        loader = TMVA.DataLoader("dataset")
        LoadDatasets(backgroundDatasetsDict, neededBranches, signal=False, loader=loader, lqMass=lqMassToUse)
        LoadDatasets(signalDatasetsDict, neededBranches, signal=True, loader=loader, lqMass=lqMassToUse)
        
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
       LoadDatasets(backgroundDatasetsDict, neededBranches, signal=False, loader=loader, lqMass=lqMass, nLQPoints=len(lqMassList))
       signalDatasetName = signalNameTemplate.format(lqMass)
       signalDatasetsDict = {}
       signalDatasetsDict[signalDatasetName] = allSignalDatasetsDict[signalDatasetName]
       LoadDatasets(signalDatasetsDict, neededBranches, signal=True, loader=loader, lqMass=lqMass)
   
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


def GetTotalEventsHist(lqMassToUse, signalDict, signalNameTemplate):
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
                tfile = TFile.Open(os.path.expandvars(line))
                tfiles.append(tfile)
                unscaledEvtsHist = tfile.Get(histName)
                if not unscaledEvtsHist or unscaledEvtsHist.ClassName() != "TH1D":
                    unscaledEvtsHist = tfile.Get("EventCounter")
                    if unscaledEvtsHist.ClassName() != "TH1D":
                        raise RuntimeError("Expected class TH1D for object names {} but class is '{}' instead.".format(histName, unscaledEvtsHist.ClassName()))
                if hist is None:
                    hist = copy.deepcopy(unscaledEvtsHist)
                else:
                    hist.Add(unscaledEvtsHist)
    for tfile in tfiles:
        tfile.Close()
    return hist


def GetSignalTotalEvents(lqMassToUse):
    hist = GetTotalEventsHist(lqMassToUse, allSignalDatasetsDict, signalNameTemplate)
    # for TProfiles
    # unscaledTotalEvts = prof.GetBinContent(1)*prof.GetBinEntries(1)
    unscaledTotalEvts = hist.GetBinContent(1)
    return unscaledTotalEvts


def GetSignalSumWeights(lqMassToUse):
    hist = GetTotalEventsHist(lqMassToUse, allSignalDatasetsDict, signalNameTemplate)
    # for TProfiles
    # unscaledTotalEvts = prof.GetBinContent(1)*prof.GetBinEntries(1)
    sumWeights = hist.GetBinContent(3)
    return sumWeights


def GetBackgroundSumWeights(sampleName, txtFile):
    hist = GetTotalEventsHist(0, {sampleName: [txtFile]}, sampleName)
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
    bdtWeightFileName, lqMassToUse, sharedOptValsDict = args
    try:
        signalDatasetsDict = {}
        signalDatasetName = signalNameTemplate.format(lqMassToUse)
        signalDatasetsDict[signalDatasetName] = allSignalDatasetsDict[signalDatasetName]
        print(signalDatasetsDict)
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
                txtFile = txtFile.format(lqMassToUse)
                #tchainBkg = LoadChainFromTxtFile(txtFile.format(lqMassToUse))
                tchainBkg = LoadChainFromTxtFile(txtFile)
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
                #bkgWeight = FindWeight(os.path.basename(txtFile).replace(".txt", ""), backgroundDatasetsWeightsTimesOneThousand)/1000.0
                datasetName = os.path.basename(txtFile).replace(".txt", "")
                sumWeights = GetBackgroundSumWeights(datasetName, txtFile)
                bkgWeight = CalcWeight(datasetName, intLumi, sumWeights)
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
                #cols = ROOT.vector('string')()
                #cols.push_back("run")
                #cols.push_back("event")
                #cols.push_back("ls")
                #cols.push_back("eventWeight")
                #cols.push_back("BDT")
                #d2 = df.Display(cols)
                #d2.Print()
                #
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
        tchainSig = LoadDatasets(signalDatasetsDict, neededBranches, signal=True, loader=None, lqMass=lqMassToUse)
        dfSig = RDataFrame(tchainSig)
        dfSig = dfSig.Filter(mycuts.GetTitle())  # will work for expressions valid in C++
        # dfSig = dfSig.Define('BDTv', ROOT.computeBDT, ROOT.BDT.GetVariableNames())
        dfSig = dfSig.Define('BDTv', getattr(ROOT, "computeBDT{}".format(lqMassToUse)), getattr(ROOT, "BDT{}".format(lqMassToUse)).GetVariableNames())
        dfSig = dfSig.Define('BDT', 'BDTv[0]')
        dfSig = dfSig.Define('eventWeight', eventWeightExpression)
        histSig = dfSig.Histo1D(ROOT.RDF.TH1DModel(hsig), "BDT", "eventWeight")
        #datasetName = os.path.basename(txtFile).replace(".txt", "")
        sumWeights = GetSignalSumWeights(lqMassToUse)
        signalWeight = CalcWeight(signalDatasetName, intLumi, sumWeights)
        #signalWeight = signalDatasetsWeightsTimesOneThousand[signalDatasetName]/1000.0
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
        #sumWeights = GetSignalSumWeights(lqMassToUse)
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
        #print("For lqMass={}, max FOM: ibin={} with FOM={}, cutVal={}, nS={}, eff={}, nB={}".format(lqMassToUse, maxVal[0], *maxVal[1]))
        # testVals=list(fomValueToCutInfoDict.items())
        # testVal=testVals[9949]
        # print("test FOM: ibin={} with FOM={}, cutVal={}, nS={}, eff={}, nB={}".format(testVal[0], *testVal[1]))
        # testVal=testVals[9948]
        # print("test FOM: ibin={} with FOM={}, cutVal={}, nS={}, eff={}, nB={}".format(testVal[0], *testVal[1]))
        # testVal=testVals[9950]
        # print("test FOM: ibin={} with FOM={}, cutVal={}, nS={}, eff={}, nB={}".format(testVal[0], *testVal[1]))
        valList = [maxVal[0]]
        valList.extend(maxVal[1])
        sharedOptValsDict[lqMassToUse] = valList
    except Exception as e:
        print("ERROR: exception in OptimizeBDTCut for lqMass={}".format(lqMassToUse))
        traceback.print_exc()
        raise e

    return True


@ROOT.Numba.Declare(["int"], "float")
def GetMassFloat(mass):
    return float(mass)


def PrintBDTCuts(optValsDict):
    for mass, valList in optValsDict.items():
        print("For lqMass={}, max FOM: ibin={} with FOM={}, cutVal={}, nS={}, eff={}, nB={}".format(mass, *valList))
    sortedDict = OrderedDict(sorted(optValsDict.items(), key=lambda t: float(t[1][2])))
    for mass, valList in sortedDict.items():
        print("#"+114*"-")
        print("# LQ M {} optimization".format(mass))
        print("#"+114*"-")
        print("BDTOutput_LQ{}                         {}                +inf 		-		-	2	10000 -1 1".format(mass, round(valList[2], 4)))


####################################################################################################
# Run
####################################################################################################
if __name__ == "__main__":
    gROOT.SetBatch()
    year = "2016postVFP"
    train = False
    optimize = True
    parallelize = True
    parametrized = True
    # lqMassesToUse = [1400, 1500, 1600, 1700]
    lqMassesToUse = list(range(1000, 2100, 100))
    # lqMassesToUse = list(range(300, 2100, 100))
    signalNameTemplate = "LQToDEle_M-{}_pair_bMassZero_TuneCP2_13TeV-madgraph-pythia8"
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
    #
    #weightFile = os.getenv("LQANA")+"/versionsOfAnalysis/2016/eejj/eejj_1dec2022_preselOnly_eleSFsTrigSFsLead_ele27AndPhoton175_fromPSK_2016postVFP/bdt/dataset/weights/TMVAClassification_BDTG.weights.xml"
    weightFile = os.getenv("LQANA")+"/versionsOfAnalysis/2016/eejj/eejj_1dec2022_preselOnly_eleSFsTrigSFsLead_ele27AndPhoton175_fromPSK_2016postVFP/bdt/dataset/weights/TMVAClassification_BDTG.weights.xml"
    
    xsectionFile = os.getenv("LQANA")+"/versionsOfAnalysis/2016/eejj/eejj_1dec2022_preselOnly_eleSFsTrigSFsLead_ele27AndPhoton175_fromPSK_2016postVFP/xsection_13TeV_2022_Mee_BkgControlRegion_gteTwoBtaggedJets_TTbar_Mee_BkgControlRegion_DYJets.txt"
    ParseXSectionFile(xsectionFile)

    if year == "2016preVFP":
        intLumi = 19501.601622
        for dataset in backgroundDatasetsDict.keys():
            if "QCDFakes_DATA" in dataset:
                continue
            backgroundDatasetsDict[dataset] = [txtFile.replace(".txt", "_APV.txt") for txtFile in backgroundDatasetsDict[dataset]]
        backgroundDatasetsDict.update(qcdFakes2016pre)
        signalNameTemplate+="_APV"
    elif year == "2016postVFP":
        intLumi = 16812.151722
        backgroundDatasetsDict.update(qcdFakes2016post)
    elif year == "2017":
        intLumi = 41540  #FIXME
    elif year == "2018":
        intLumi = 59399  #FIXME
    else:
        raise RuntimeError("Did not understand 'year' parameter whose value is {}; must be one of 2016preVFP, 2016postVFP, 2017, 2018".format(year))

    inputListSignalBase = inputListBkgBase
    allSignalDatasetsDict = {}
    massList = list(range(300, 3100, 100))
    massList.extend([3500, 4000])
    for mass in massList:
        signalName = signalNameTemplate.format(mass)
        allSignalDatasetsDict[signalName] = [inputListSignalBase+signalName+".txt"]

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
            manager = multiprocessing.Manager()
            dictOptValues = manager.dict()
            # ncores = multiprocessing.cpu_count()
            ncores = 4  # only use 4 parallel jobs to be nice
            pool = multiprocessing.Pool(ncores)
            jobCount = 0
            for mass in lqMassesToUse:
                try:
                    pool.apply_async(OptimizeBDTCut, [[weightFile.format(mass), mass, dictOptValues]], callback=log_result)
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
                dictOptValues = {}
                OptimizeBDTCut([weightFile.format(mass), mass, dictOptValues])
        PrintBDTCuts(dictOptValues)
