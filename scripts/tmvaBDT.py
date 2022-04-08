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

gROOT.SetBatch()


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
]
eventWeightExpression = "Weight*PrefireWeight*puWeight*Ele1_RecoSF*Ele2_RecoSF*Ele1_TrigSF*Ele2_TrigSF*Ele1_EGMLooseIDSF*Ele2_EGMLooseIDSF"
# HEEP
# loader.SetBackgroundWeightExpression( "Weight*PrefireWeight*puWeight*Ele1_RecoSF*Ele2_RecoSF*Ele1_TrigSF*Ele2_TrigSF*Ele1_HEEPSF*Ele2_HEEPSF" )
neededBranches = ["Weight", "PrefireWeight", "puWeight", "Ele1_RecoSF", "Ele2_RecoSF", "Ele1_TrigSF", "Ele2_TrigSF"]
neededBranches.extend(["run", "ls", "event"])
neededBranches.extend(["Ele1_EGMLooseIDSF", "Ele2_EGMLooseIDSF"])
neededBranches.extend(["Ele1_HEEPSF", "Ele2_HEEPSF"])
neededBranches.extend(["sT_eejj", "M_e1e2", "M_e1j1", "M_e1j2", "M_e2j1","M_e2j2"])
neededBranches.extend(["Ele1_Pt", "Ele2_Pt", "Jet1_Pt", "Jet2_Pt", "Jet3_Pt", "Ele1_Eta", "Ele2_Eta", "Jet1_Eta", "Jet2_Eta", "Jet3_Eta"])
neededBranches.extend(["Ele1_Phi", "Ele2_Phi", "Ele3_Phi", "Jet1_Phi", "Jet2_Phi", "Jet3_Phi"])
neededBranches.extend(["PFMET_Type1_Pt", "PFMET_Type1_Phi", "DR_Ele1Jet1", "DR_Ele1Jet2", "DR_Ele2Jet1", "DR_Ele2Jet2", "DR_Jet1Jet2"])
# Apply additional cuts on the signal and background samples (can be different)
# mycuts = TCut()
# mycutb = TCut()
mycuts = TCut("M_e1e2 > 200 && sT_eejj > 400")
mycutb = TCut("M_e1e2 > 200 && sT_eejj > 400")
    
####################################################################################################
# datasets
inputListBkgBase = "$LQANA/config/nanoV7_2016_analysisPreselSkims_egLoose_4feb2022/"
# inputListBkgBase = "$LQANA/config/nanoV7_2016_analysisPreselSkims_heep_2sep2021/"
inputListQCDBase = "$LQANA/config/nanoV7_2016_pskQCDEEJJ_egLoose_24mar2022_comb/"
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
backgroundDatasetsWeightsTimesOneThousand = {
        "ZJet_amcatnlo_ptBinned" : [0.33620511942, 0.114625534835, 0.188510053163, 0.795115450687, 11.2325005129, 11.1756034925],
        "TTbar_powheg" : [0.585547131056, 0.572359028863, 0.36631937923],
        "DIBOSON_nlo" : [856.651276021, 207.201072147, 198.802581291, 1.47221360112, 0.475809997084, 0.728060423014, 0.382723130896, 11.6251013241, 1.93599141046, 0.910176137249, 0.859835380036],
        "TRIBOSON" : [149.598485516, 143.827579157, 145.307050001, 143.285693969],
        "TTW" : [3.71148010247, 23.1528859117],
        "TTZ" : [0.933902239753],
        "SingleTop" : [184.936486294, 185.462933288, 71.7704250605, 73.4648859745, 12.2784973443],
        "WJet_amcatnlo_jetBinned" : [0.339337935899, 0.172310335826, 0.0213606587798],
        "WJet_amcatnlo_ptBinned" : [0.121230487882, 0.197285449115, 0.145778733507, 1.4234006515, 9.54412611451, 9.17993794712],
        "PhotonJets_Madgraph" : [79724.6223759, 32792.3855087, 4027.44663672, 1945.01356701, 669.263854243],
        "QCDFakes_DATA" : [1000.0]*7,  # i.e., weight=1
}
inputListSignalBase = inputListBkgBase
signalNameTemplate = "LQToDEle_M-{}_pair"
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
allSignalDatasetsWeightsTimesOneThousand = {
        "LQToDEle_M-1700_pair" : [0.0423445802],
        "LQToDEle_M-1600_pair" : [0.07639671],
        "LQToDEle_M-1500_pair" : [0.140885576],
        "LQToDEle_M-1400_pair" : [0.26362245],
        "LQToDEle_M-1200_pair" : [0.96553964],
        "LQToDEle_M-300_pair" : [6027.09068],
        # "LQToDEle_M-1700_pair" : [1.0],
        # "LQToDEle_M-1600_pair" : [1.0],
        # "LQToDEle_M-1500_pair" : [1.0],
        # "LQToDEle_M-1400_pair" : [1.0],
        # "LQToDEle_M-1200_pair" : [1.0],
        # "LQToDEle_M-300_pair" : [1.0],
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
        raise RuntimeError("Got <= 0 files loaded into the TFileCollection!")
    ch = TChain("rootTupleTree/tree")
    ch.AddFileInfoList(fc.GetList())
    ch.SetBranchStatus("*", 0)
    for branchName in neededBranches:
        ch.SetBranchStatus(branchName, 1)
    if ch.GetEntries() <= 0:
        print("WARNING: Got <= 0 entries for dataset={}; returning None!".format(txtFile))
        return None
    else:
        print("INFO: Got {} entries for dataset={}".format(ch.GetEntries(), txtFile))
    return ch


def LoadDatasets(datasetDict, weightsTimes1kDict, neededBranches, signal=False, loader=None):
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
                ch = LoadChainFromTxtFile(txtFile)
                if ch is None:
                    continue
                nSampleTotEvents+=ch.GetEntries()
                weight = weightsTimes1kDict[key][count]/1000.0
                if loader is not None:
                    if signal:
                        loader.AddSignalTree    ( ch, weight )
                    else:
                        loader.AddBackgroundTree( ch, weight )
                    print("Loaded tree from file {} with {} events.".format(txtFile, ch.GetEntries()))
                else:
                    totalTChain.Add(ch)
            print("Loaded tree for sample {} with {} entries.".format(key, nSampleTotEvents))
            nTotEvents+=nSampleTotEvents
        else:
            txtFile = value
            ch = LoadChainFromTxtFile(txtFile)
            if ch is None:
                continue
            nSampleTotEvents = ch.GetEntries()
            weight = weightsTimes1kDict[key][count]/1000.0
            if loader is not None:
                if signal:
                    loader.AddSignalTree    ( ch, weight )
                else:
                    loader.AddBackgroundTree( ch, weight )
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
        LoadDatasets(backgroundDatasetsDict, backgroundDatasetsWeightsTimesOneThousand, neededBranches, signal=False, loader=loader)
        LoadDatasets(signalDatasetsDict, signalDatasetsWeightsTimesOneThousand, neededBranches, signal=True, loader=loader)
        
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


def GetSignalTotalEvents(lqMassToUse):
    signalDatasetName = signalNameTemplate.format(lqMassToUse)
    txtFiles = allSignalDatasetsDict[signalDatasetName]
    # profName = "EventsPassingCuts_unscaled"
    hist = None
    histName = "savedHists/EventCounter"
    tfiles = []
    for count, txtFile in enumerate(txtFiles):
        with open(os.path.expandvars(txtFile), "r") as theTxtFile:
            for line in theTxtFile:
                line = line.strip()
                # print("Opening file='{}'".format(line))
                tfile = TFile.Open(os.path.expandvars(line))
                tfiles.append(tfile)
                unscaledEvtsHist = tfile.Get(histName)
                if unscaledEvtsHist.ClassName() != "TH1D":
                    raise RuntimeError("Excepted class TH1D for object names {} but class is '{}' instead.".format(histName, unscaledEvtsHist.ClassName()))
                if hist is None:
                    hist = unscaledEvtsHist
                else:
                    hist.Add(unscaledEvtsHist)
    # for TProfiles
    # unscaledTotalEvts = prof.GetBinContent(1)*prof.GetBinEntries(1)
    unscaledTotalEvts = hist.GetBinContent(1)
    for tfile in tfiles:
        tfile.Close()
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
            for idx, txtFile in enumerate(backgroundDatasetsDict[sample]):
                tchainBkg = LoadChainFromTxtFile(txtFile)
                if tchainBkg is None:
                    continue
                df = RDataFrame(tchainBkg)
                df = df.Filter(mycutb.GetTitle())  # will work for expressions valid in C++
                # df = df.Define('BDTv', ROOT.computeBDT, ROOT.BDT.GetVariableNames())
                df = df.Define('BDTv', getattr(ROOT, "computeBDT{}".format(lqMassToUse)), getattr(ROOT, "BDT{}".format(lqMassToUse)).GetVariableNames())
                df = df.Define('BDT', 'BDTv[0]')
                df = df.Define('eventWeight', eventWeightExpression)
                histName = "BDTVal_{}_{}".format(sample, idx)
                hbkg = TH1D(histName, histName, 10000, -1, 1)
                histBkg = df.Histo1D(ROOT.RDF.TH1DModel(hbkg), "BDT", "eventWeight")
                bkgWeight = backgroundDatasetsWeightsTimesOneThousand[sample][idx]/1000.0
                histBkg.Scale(bkgWeight)
                bkgTotal.Add(histBkg.GetPtr())
                #h = df.Histo1D(hbkg, "BDT", "eventWeight")
                #h.Draw()
                bkgIntegralOverCut = df.Filter("BDT > {}".format(cutValForIntegral)).Sum("eventWeight").GetValue()*bkgWeight
                bkgEntriesOverCut = df.Filter("BDT > {}".format(cutValForIntegral)).Count().GetValue()
                print("subsample={}, entries with BDT > {} = {}, integral unweighted = {}, integral weighted = {}".format(txtFile, cutValForIntegral, bkgEntriesOverCut, bkgIntegralOverCut/bkgWeight, bkgIntegralOverCut))
                sys.stdout.flush()
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
            print("sample={}, entries over BDT cut = {}".format(sample, bkgSampleIntegralOverCut))
            sys.stdout.flush()
            print()
            sys.stdout.flush()
        print("bkgIntegralOverCut={}".format(bkgIntegralOverCut))
        sys.stdout.flush()

        # signal
        tchainSig = LoadDatasets(signalDatasetsDict, signalDatasetsWeightsTimesOneThousand, neededBranches, signal=True, loader=None)
        dfSig = RDataFrame(tchainSig)
        dfSig = dfSig.Filter(mycuts.GetTitle())  # will work for expressions valid in C++
        # dfSig = dfSig.Define('BDTv', ROOT.computeBDT, ROOT.BDT.GetVariableNames())
        dfSig = dfSig.Define('BDTv', getattr(ROOT, "computeBDT{}".format(lqMassToUse)), getattr(ROOT, "BDT{}".format(lqMassToUse)).GetVariableNames())
        dfSig = dfSig.Define('BDT', 'BDTv[0]')
        dfSig = dfSig.Define('eventWeight', eventWeightExpression)
        histSig = dfSig.Histo1D(ROOT.RDF.TH1DModel(hsig), "BDT", "eventWeight")
        signalWeight = signalDatasetsWeightsTimesOneThousand[signalDatasetName][0]/1000.0
        histSig.Scale(signalWeight)

        # print some entries
        # cols = ROOT.vector('string')()
        # cols.push_back("BDT")
        # cols.push_back("eventWeight")
        # d2 = dfSig.Display(cols)
        # d2.Print()

        # now optimize
        totalSignalEventsUnscaled = GetSignalTotalEvents(lqMassToUse)
        fomValueToCutInfoDict = {}
        for iBin in range(1, hbkg.GetNbinsX()+1):
            nS = histSig.Integral(iBin, hsig.GetNbinsX())
            nB = bkgTotal.Integral(iBin, hbkg.GetNbinsX())
            efficiency = nS/(signalWeight*totalSignalEventsUnscaled)  #FIXME?
            fom = EvaluateFigureOfMerit(nS, nB, efficiency, 0, "punzi")
            cutVal = histSig.GetBinLowEdge(iBin)
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
        sortedDict = OrderedDict(sorted(fomValueToCutInfoDict.items(), key=lambda t: t[1][0], reverse=True))
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


####################################################################################################
# Run
####################################################################################################
train = False
optimize = True
parallelize = False
lqMassesToUse = [1400, 1500, 1600, 1700]
# lqMassesToUse = [1400]
weightFile = os.getenv("LQANA")+"/versionsOfAnalysis/2016/nanoV7/eejj/mar24_2022_egLoose_BDT_qcd/train_14-17/dataset/weights/TMVAClassification_LQToDEle_M-{}_pair_BDTG.weights.xml"

if train:
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
            # OptimizeBDTCut(os.getenv("LQANA")+"/versionsOfAnalysis/2016/nanoV7/eejj/mar24_2022_egLoose_BDT_qcd/lqm1700/dataset/weights/TMVAClassification_LQToDEle_M-1700_pair_BDTG.weights.xml", 1700)
            # OptimizeBDTCut(os.getenv("LQANA")+"/versionsOfOptimization/nanoV7/2016/eejj_feb18_egmLooseID_BDT/mee200sT400/lqm1700/dataset/weights/TMVAClassification_BDTG.weights.xml", 1700)
            # OptimizeBDTCut(os.getenv("LQANA")+"/versionsOfOptimization/nanoV7/2016/eejj_feb18_egmLooseID_BDT/mee200sT400/lqm1500/dataset/weights/TMVAClassification_BDTG.weights.xml", 1500)
            # OptimizeBDTCut(os.getenv("LQANA")+"/versionsOfAnalysis/2016/nanoV7/eejj/mar24_2022_egLoose_BDT_qcd/lqm1500/dataset/weights/TMVAClassification_LQToDEle_M-1500_pair_BDTG.weights.xml", 1500)
            # OptimizeBDTCut(os.getenv("LQANA")+"/versionsOfAnalysis/2016/nanoV7/eejj/mar24_2022_egLoose_BDT_qcd/lqm1500_jet3etaPhi/dataset/weights/TMVAClassification_LQToDEle_M-1500_pair_BDTG.weights.xml", 1500)
            OptimizeBDTCut([weightFile.format(mass), mass])
