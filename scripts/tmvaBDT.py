#!/usr/bin/env python3
from __future__ import print_function

# see: https://github.com/lmoneta/tmva-tutorial/blob/master/notebooks/TMVA_Classification.ipynb

from ROOT import TMVA, TFile, TString, TCut, TChain, TFileCollection, gROOT

gROOT.SetBatch()

def LoadDatasets(datasetDict, loader, neededBranches, signal=False):
    nTotEvents = 0
    for key, value in datasetDict.items():
        print("Loading tree for dataset={}; signal={}".format(key, signal))
        if isinstance(value, list):
            # print(value)
            nSampleTotEvents = 0
            for count, txtFile in enumerate(value):
                # print("Add file={} to collection".format(txtFile))
                fc = TFileCollection("dum","",txtFile)
                if fc.GetNFiles() <= 0:
                    raise RuntimeError("Got <= 0 files loaded into the TFileCollection!")
                ch = TChain("rootTupleTree/tree")
                ch.AddFileInfoList(fc.GetList())
                ch.SetBranchStatus("*", 0)
                nSampleTotEvents+=ch.GetEntries()
                for branchName in neededBranches:
                    ch.SetBranchStatus(branchName, 1)
                if ch.GetEntries() <= 0:
                    print("WARNING: Got <= 0 entries for dataset={}; skipping!".format(txtFile))
                    continue
                if signal:
                    weight = signalDatasetsWeightsTimesOneThousand[key][count]/1000.0
                    loader.AddSignalTree    ( ch, weight )
                else:
                    weight = backgroundDatasetsWeightsTimesOneThousand[key][count]/1000.0
                    loader.AddBackgroundTree( ch, weight )
                print("Loaded tree from file {} with {} events.".format(txtFile, ch.GetEntries()))
            print("Loaded tree for sample {} with {} entries.".format(key, nSampleTotEvents))
            nTotEvents+=nSampleTotEvents
        else:
            fc = TFileCollection("dum","",value)
            if fc.GetNFiles() <= 0:
                raise RuntimeError("Got <= 0 files loaded into the TFileCollection!")
            ch = TChain("rootTupleTree/tree")
            ch.AddFileInfoList(fc.GetList())
            ch.SetBranchStatus("*", 0)
            nSampleTotEvents = ch.GetEntries()
            for branchName in neededBranches:
                ch.SetBranchStatus(branchName, 1)
            # backgroundDatasetsTrees[key] = ch
            if signal:
                weight = signalDatasetsWeightsTimesOneThousand[key]/1000.0
                loader.AddSignalTree    ( ch, weight )
            else:
                weight = backgroundDatasetsWeightsTimesOneThousand[key]/1000.0
                loader.AddBackgroundTree( ch, weight )
            print("Loaded tree for sample {} with {} entries.".format(key, nSampleTotEvents))
            nTotEvents+=nSampleTotEvents
    print("Total: loaded tree with {} entries.".format(nTotEvents))


####################################################################################################
# Configurables
####################################################################################################
inputListBkgBase = "$LQANA/config/nanoV7_2016_analysisPreselSkims_egLoose_4feb2022/"
# inputListBkgBase = "$LQANA/config/nanoV7_2016_analysisPreselSkims_heep_2sep2021/"
inputListQCDBase = "$LQANA/config/nanoV7_2016_pskQCDEEJJ_egLoose_24mar2022_comb/"
# preselection-skimmed background datasets
backgroundDatasetsDict = {
        # "ZJet_amcatnlo_ptBinned" if do2016 else "ZJet_jetAndPtBinned",
        #"ZJet_amcatnlo_ptBinned" : [
        #    inputListBkgBase+"DYJetsToLL_Zpt-0To50_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"DYJetsToLL_Pt-50To100_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"DYJetsToLL_Pt-100To250_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"DYJetsToLL_Pt-250To400_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"DYJetsToLL_Pt-400To650_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"DYJetsToLL_Pt-650ToInf_amcatnloFXFX_pythia8.txt",
        #    ],
        #"TTbar_powheg" : [
        #    inputListBkgBase+"TTTo2L2Nu_pythia8.txt",
        #    inputListBkgBase+"TTToHadronic_pythia8.txt",
        #    inputListBkgBase+"TTToSemiLeptonic_pythia8.txt",
        #    ],
        "QCDFakes_DATA" : [
            inputListQCDBase+"SinglePhoton_Run2016H-02Apr2020-v1.txt",
        #    inputListQCDBase+"SinglePhoton_Run2016G-02Apr2020-v1.txt",
        #    inputListQCDBase+"SinglePhoton_Run2016F-02Apr2020-v1.txt",
        #    inputListQCDBase+"SinglePhoton_Run2016E-02Apr2020-v1.txt",
        #    inputListQCDBase+"SinglePhoton_Run2016D-02Apr2020-v1.txt",
        #    inputListQCDBase+"SinglePhoton_Run2016C-02Apr2020-v1.txt",
        #    inputListQCDBase+"SinglePhoton_Run2016B-02Apr2020_ver2-v1.txt",
            ],
        #"DIBOSON_nlo" : [
        #    inputListBkgBase+"WWTo4Q.txt",
        #    inputListBkgBase+"WWToLNuQQ.txt",
        #    inputListBkgBase+"WWTo2L2Nu.txt",
        #    inputListBkgBase+"ZZTo2L2Q_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"ZZTo4L_pythia8.txt",
        #    inputListBkgBase+"ZZTo2Q2Nu_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"ZZTo2L2Nu_pythia8.txt",
        #    inputListBkgBase+"WZTo1L3Nu_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"WZTo3LNu_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"WZTo1L1Nu2Q_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"WZTo2L2Q_amcatnloFXFX_pythia8.txt",
        #    ],
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
        #"SingleTop" : [
        #    inputListBkgBase+"ST_tW_top_5f_inclusiveDecays_ext1_pythia8.txt",
        #    inputListBkgBase+"ST_tW_antitop_5f_inclusiveDecays_ext1_pythia8.txt",
        #    inputListBkgBase+"ST_t-channel_top_4f_inclusiveDecays.txt",
        #    inputListBkgBase+"ST_t-channel_antitop_4f_inclusiveDecays.txt",
        #    inputListBkgBase+"ST_s-channel_4f_InclusiveDecays_pythia8.txt",
        #    ],
        #"WJet_amcatnlo_jetBinned" : [
        #    inputListBkgBase+"WToLNu_0J_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"WToLNu_1J_backup_amcatnloFXFX_pythia8.txt",
        #    inputListBkgBase+"WToLNu_2J_amcatnloFXFX_pythia8.txt",
        #    ],
        #"PhotonJets_Madgraph" : [
        #   inputListBkgBase+"GJets_HT-40To100_madgraphMLM.txt",
        #   inputListBkgBase+"GJets_HT-100To200_madgraphMLM.txt",
        #   inputListBkgBase+"GJets_HT-200To400_madgraphMLM.txt",
        #   inputListBkgBase+"GJets_HT-400To600_madgraphMLM.txt",
        #   inputListBkgBase+"GJets_HT-600ToInf_madgraphMLM.txt",
        #   ],
}
# for key, value in backgroundDatasetsDict.items():
#     for idx, item in enumerate(value):
#         backgroundDatasetsDict[key][idx] = inputListBase+item
backgroundDatasetsWeightsTimesOneThousand = {
        "ZJet_amcatnlo_ptBinned" : [0.33620511942, 0.114625534835, 0.188510053163, 0.795115450687, 11.2325005129, 11.1756034925],
        "TTbar_powheg" : [0.585547131056, 0.572359028863, 0.36631937923],
        # "QCDFakes_DATA",
        "DIBOSON_nlo" : [856.651276021, 207.201072147, 198.802581291, 1.47221360112, 0.475809997084, 0.728060423014, 0.382723130896, 11.6251013241, 1.93599141046, 0.910176137249, 0.859835380036],
        "TRIBOSON" : [149.598485516, 143.827579157, 145.307050001, 143.285693969],
        "TTW" : [3.71148010247, 23.1528859117],
        "TTZ" : [0.933902239753],
        "SingleTop" : [184.936486294, 185.462933288, 71.7704250605, 73.4648859745, 12.2784973443],
        "WJet_amcatnlo_jetBinned" : [0.339337935899, 0.172310335826, 0.0213606587798],
        "PhotonJets_Madgraph" : [79724.6223759, 32792.3855087, 4027.44663672, 1945.01356701, 669.263854243],
        "QCDFakes_DATA" : [1000.0]*7,
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
# for key, value in allSignalDatasetsDict.items():
#     for idx, item in enumerate(value):
#         allSignalDatasetsDict[key][idx] = inputListBase+item
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
lqMassToUse = 1700
# just one use the single LQ signal specified by mass just above
signalDatasetsDict = {}
signalDatasetsWeightsTimesOneThousand = {}
for key in allSignalDatasetsDict:
    if signalNameTemplate.format(lqMassToUse) == key:
        signalDatasetsDict[key] = allSignalDatasetsDict[key]
        signalDatasetsWeightsTimesOneThousand[key] = allSignalDatasetsWeightsTimesOneThousand[key]
print(signalDatasetsDict)
print(signalDatasetsWeightsTimesOneThousand)

outputFile = TFile.Open("TMVA_ClassificationOutput.root", "RECREATE")

TMVA.Tools.Instance()
factory = TMVA.Factory("TMVAClassification", outputFile, "!V:ROC:!Silent:Color:DrawProgressBar:AnalysisType=Classification")

neededBranches = ["Weight", "PrefireWeight", "puWeight", "Ele1_RecoSF", "Ele2_RecoSF", "Ele1_TrigSF", "Ele2_TrigSF"]
# loose
neededBranches.extend(["Ele1_EGMLooseIDSF", "Ele2_EGMLooseIDSF"])
# HEEP
# neededBranches.extend(["Ele1_HEEPSF", "Ele2_HEEPSF"])
neededBranches.extend(["sT_eejj", "M_e*", "Ele1_Pt", "Ele2_Pt", "Jet1_Pt", "Jet2_Pt", "Jet3_Pt", "Ele1_Eta", "Ele2_Eta", "Jet1_Eta", "Jet2_Eta", "Jet3_Eta"])
neededBranches.extend(["Ele1_Phi", "Ele2_Phi", "Ele3_Phi", "Jet1_Phi", "Jet2_Phi", "Jet3_Phi"])
neededBranches.extend(["PFMET_Type1*", "DR_*"])
loader = TMVA.DataLoader("dataset")
LoadDatasets(backgroundDatasetsDict, loader, neededBranches)
LoadDatasets(signalDatasetsDict, loader, neededBranches, signal=True)

#  Set individual event weights (the variables must exist in the original TTree)
# if(analysisYear < 2018 && hasBranch("PrefireWeight") && !isData()) --> prefire weight
loader.SetBackgroundWeightExpression( "Weight*PrefireWeight*puWeight*Ele1_RecoSF*Ele2_RecoSF*Ele1_TrigSF*Ele2_TrigSF*Ele1_EGMLooseIDSF*Ele2_EGMLooseIDSF" )
loader.SetSignalWeightExpression( "Weight*PrefireWeight*puWeight*Ele1_RecoSF*Ele2_RecoSF*Ele1_TrigSF*Ele2_TrigSF*Ele1_EGMLooseIDSF*Ele2_EGMLooseIDSF" )
# HEEP
# loader.SetBackgroundWeightExpression( "Weight*PrefireWeight*puWeight*Ele1_RecoSF*Ele2_RecoSF*Ele1_TrigSF*Ele2_TrigSF*Ele1_HEEPSF*Ele2_HEEPSF" )
# loader.SetSignalWeightExpression( "Weight*PrefireWeight*puWeight*Ele1_RecoSF*Ele2_RecoSF*Ele1_TrigSF*Ele2_TrigSF*Ele1_HEEPSF*Ele2_HEEPSF" )

# define variables
#loader.AddVariable( "myvar1 := var1+var2", 'F' )
#loader.AddVariable( "myvar2 := var1-var2", "Expression 2", "", 'F' )
#loader.AddVariable( "var3",                "Variable 3", "units", 'F' )
#loader.AddVariable( "var4",                "Variable 4", "units", 'F' )
#
#loader.AddSpectator( "spec1 := var1*2",  "Spectator 1", "units", 'F' )
#loader.AddSpectator( "spec2 := var1*3",  "Spectator 2", "units", 'F' )
loader.AddVariable( "sT_eejj", "F")
loader.AddVariable( "PFMET_Type1_Pt", "F")
loader.AddVariable( "PFMET_Type1_Phi", "F")
loader.AddVariable( "M_e1e2", "F")
loader.AddVariable( "M_e1j1", "F")
loader.AddVariable( "M_e1j2", "F")
loader.AddVariable( "M_e2j1", "F")
loader.AddVariable( "M_e2j2", "F")
loader.AddVariable( "Ele1_Pt", "F")
loader.AddVariable( "Ele2_Pt", "F")
loader.AddVariable( "Ele1_Eta", "F")
loader.AddVariable( "Ele2_Eta", "F")
loader.AddVariable( "Ele1_Phi", "F")
loader.AddVariable( "Ele2_Phi", "F")
loader.AddVariable( "Jet1_Pt", "F")
loader.AddVariable( "Jet2_Pt", "F")
loader.AddVariable( "Jet3_Pt", "F")
loader.AddVariable( "Jet1_Eta", "F")
loader.AddVariable( "Jet2_Eta", "F")
#loader.AddVariable( "Jet3_Eta", "F")
loader.AddVariable( "Jet1_Phi", "F")
loader.AddVariable( "Jet2_Phi", "F")
#loader.AddVariable( "Jet3_Phi", "F")
loader.AddVariable( "DR_Ele1Jet1", "F")
loader.AddVariable( "DR_Ele1Jet2", "F")
loader.AddVariable( "DR_Ele2Jet1", "F")
loader.AddVariable( "DR_Ele2Jet2", "F")
loader.AddVariable( "DR_Jet1Jet2", "F")

# Apply additional cuts on the signal and background samples (can be different)
mycuts = TCut()
mycutb = TCut()
# mycuts = TCut("M_e1e2 > 100")  # for example: TCut mycuts = "abs(var1)<0.5 && abs(var2-0.5)<1";
# mycutb = TCut("M_e1e2 > 100")  # for example: TCut mycutb = "abs(var1)<0.5";
mycuts = TCut("M_e1e2 > 200 && sT_eejj > 400")
mycutb = TCut("M_e1e2 > 200 && sT_eejj > 400")

# Tell the factory how to use the training and testing events
#
# If no numbers of events are given, half of the events in the tree are used
# for training, and the other half for testing:
# loader.PrepareTrainingAndTestTree( mycuts, mycutb, "V:SplitMode=random:NormMode=None:VerboseLevel=Debug" )
# loader.PrepareTrainingAndTestTree( mycuts, mycutb, "!V:SplitMode=random:NormMode=NumEvents" )
loader.PrepareTrainingAndTestTree( mycuts, mycutb, "V:SplitMode=random:NormMode=EqualNumEvents:VerboseLevel=Debug" )
# loader.PrepareTrainingAndTestTree( mycuts, mycutb, "V:SplitMode=random:NormMode=EqualNumEvents" )
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
c1.Write("rocCurve.png")

outputFile.Close()
