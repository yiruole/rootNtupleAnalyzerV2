#!/usr/bin/env python3
#
import os
import sys
import math
import multiprocessing
import traceback

from tmvaBDT import LoadChainFromTxtFile, GetSignalTotalEventsHist

import ROOT
from ROOT import TMVA, TFile, TString, TCut, TChain, TFileCollection, gROOT, gDirectory, gInterpreter, TEntryList, TH1D, TProfile, RDataFrame, TLorentzVector

gROOT.SetBatch()

result_list = []
logString = "INFO: running {} parallel jobs for {} separate LQ masses requested..."

@ROOT.Numba.Declare(["float","float","float","float"], "float")
def CalcMAsym(M_e1j1, M_e2j2, M_e1j2, M_e2j1):
    if math.fabs(M_e1j1-M_e2j2) < math.fabs(M_e1j2-M_e2j1):
        if M_e1j1 < M_e2j2:
           M_ej_max = M_e2j2
           M_ej_min = M_e1j1
        else:
           M_ej_max = M_e1j1
           M_ej_min = M_e2j2
    else:
        if M_e1j2 < M_e2j1:
           M_ej_max = M_e2j1
           M_ej_min = M_e1j2
        else:
           M_ej_max = M_e1j2
           M_ej_min = M_e2j1
    masym = (M_ej_max-M_ej_min)/(M_ej_max+M_ej_min)
    return masym


@ROOT.Numba.Declare(["float","float","float","float"], "float")
def CalcMejMax(M_e1j1, M_e2j2, M_e1j2, M_e2j1):
    if math.fabs(M_e1j1-M_e2j2) < math.fabs(M_e1j2-M_e2j1):
        if M_e1j1 < M_e2j2:
           M_ej_max = M_e2j2
        else:
           M_ej_max = M_e1j1
    else:
        if M_e1j2 < M_e2j1:
           M_ej_max = M_e2j1
        else:
           M_ej_max = M_e1j2
    return M_ej_max


@ROOT.Numba.Declare(["float","float","float","float"], "float")
def CalcMejMin(M_e1j1, M_e2j2, M_e1j2, M_e2j1):
    if math.fabs(M_e1j1-M_e2j2) < math.fabs(M_e1j2-M_e2j1):
        if M_e1j1 < M_e2j2:
           M_ej_min = M_e1j1
        else:
           M_ej_min = M_e2j2
    else:
        if M_e1j2 < M_e2j1:
           M_ej_min = M_e1j2
        else:
           M_ej_min = M_e2j1
    return M_ej_min


# imported from BDT script
#@ROOT.Numba.Declare(["int"], "float")
#def GetMassFloat(mass):
#    return float(mass)


ROOT.gInterpreter.Declare('''
       float CalcMeejj(float Ele1_Pt, float Ele1_Eta, float Ele1_Phi, float Ele2_Pt, float Ele2_Eta, float Ele2_Phi,
           float Jet1_Pt, float Jet1_Eta, float Jet1_Phi, float Jet2_Pt, float Jet2_Eta, float Jet2_Phi) {
         TLorentzVector e1, j1, e2, j2, eejj;
         e1.SetPtEtaPhiM ( Ele1_Pt, Ele1_Eta, Ele1_Phi, 0.0 );
         e2.SetPtEtaPhiM ( Ele2_Pt, Ele2_Eta, Ele2_Phi, 0.0 );
         j1.SetPtEtaPhiM ( Jet1_Pt, Jet1_Eta, Jet1_Phi, 0.0 );
         j2.SetPtEtaPhiM ( Jet2_Pt, Jet2_Eta, Jet2_Phi, 0.0 );
         eejj = e1 + e2 + j1 + j2; 
         return eejj.M();
       }
''')


def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)
    sys.stdout.write("\r"+logString.format(jobCount, len(massList)))
    sys.stdout.write("\t"+str(len(result_list))+" jobs done")
    sys.stdout.flush()


def ProcessDataset(args):
    txtFile, mass, branchesToSave = args
    try:
        tchainBkg = LoadChainFromTxtFile(txtFile)
        if tchainBkg is None:
            return True
        df = RDataFrame(tchainBkg)
        df = df.Filter(mycutb.GetTitle())  # will work for expressions valid in C++
        df = df.Define("Masym", "Numba::CalcMAsym(M_e1j1, M_e2j2, M_e1j2, M_e2j1)")
        df = df.Define("MejMax", "Numba::CalcMejMax(M_e1j1, M_e2j2, M_e1j2, M_e2j1)")
        df = df.Define("MejMin", "Numba::CalcMejMin(M_e1j1, M_e2j2, M_e1j2, M_e2j1)")
        df = df.Define("Meejj", "CalcMeejj(Ele1_Pt, Ele1_Eta, Ele1_Phi, Ele2_Pt, Ele2_Eta, Ele2_Phi,Jet1_Pt, Jet1_Eta, Jet1_Phi, Jet2_Pt, Jet2_Eta, Jet2_Phi)")
        df = df.Define("massInt", str(mass))
        df = df.Define("mass", "Numba::GetMassFloat(massInt)")
        datasetName = os.path.basename(txtFile).replace(".txt", "")
        tfilepath = outputTFileDir+"/{}/{}.root".format(mass, datasetName)
        print("Writing snapshot to:", tfilepath)
        df.Snapshot("rootTupleTree/tree", tfilepath, branchesToSave)
        if signalNameTemplate.format(mass) in tfilepath:
            eventCounterHist = GetSignalTotalEventsHist(mass, allSignalDatasetsDict)
            tfile = TFile(tfilepath, "update")
            tfile.cd()
            eventCounterHist.Write()
            tfile.Close()
    except Exception as e:
        print("ERROR: exception in ProcessDataset for txtFile={}, mass={}".format(txtFile, mass))
        traceback.print_exc()
        raise e
    return True


# datasets
inputListBkgBase = "$LQANA/config/inputListsPSKEEJJ_UL16preVFP_1dec2022/"
inputListQCDBase = "$LQANA/config/inputListsPSKQCD_egmloose_UL16preVFP_5dec2022/"
inputListSignalBase = inputListBkgBase
#is2016preVFP = True  #FIXME: handle pre/post 2016
# preselection-skimmed background datasets
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
            inputListQCDBase+"SinglePhoton_Run2016B-ver1_HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016B-ver2_HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016C-HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016D-HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016E-HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            inputListQCDBase+"SinglePhoton_Run2016F-HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt",
            ],
        "DIBOSON_nlo" : [
            inputListBkgBase+"WWTo4Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"WWTo1L1Nu2Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_APV.txt",
            inputListBkgBase+"ZZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
            inputListBkgBase+"ZZTo4L_TuneCP5_13TeV_powheg_pythia8_APV.txt",
            inputListBkgBase+"ZZTo2Nu2Q_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
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
            inputListBkgBase+"WJetsToLNu_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt",
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
            inputListBkgBase+"GJets_DR-0p4_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8_APV.txt",
            inputListBkgBase+"GJets_DR-0p4_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8_APV.txt",
            inputListBkgBase+"GJets_DR-0p4_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_APV.txt",
            inputListBkgBase+"GJets_DR-0p4_HT-600ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_APV.txt",
            ],
}
allSignalDatasetsDict = {}
signalNameTemplate = "LQToDEle_M-{}_pair_bMassZero_TuneCP2_13TeV-madgraph-pythia8_APV"
massList = list(range(300, 3100, 100))
massList.extend([3500, 4000])
# massList = [300]
for mass in massList:
    signalName = signalNameTemplate.format(mass)
    allSignalDatasetsDict[signalName] = [inputListSignalBase+signalName+".txt"]
# mycuts = TCut("M_e1e2 > 200 && sT_eejj > 400")
mycutb = TCut("M_e1e2 > 200 && sT_eejj > 400")

####################################################################################################
# Run
####################################################################################################
parallelize = True
outputTFileDir = "root://eosuser.cern.ch//eos/user/s/scooper/LQ/ultralegacy/2016preVFP/analysis/bdtTraining_eejj_finalSels_egLoose_6dec2022_mee200st400_allLQ"
branchesToSave = [
        "run",
        "ls",
        "event",
        "Weight",
        "PrefireWeight",
        "puWeight",
        "Ele1_RecoSF",
        "Ele2_RecoSF",
        "Ele1_TrigSF",
        "Ele2_TrigSF",
        "Ele1_EGMLooseIDSF",
        "Ele2_EGMLooseIDSF",
        "Ele1_HEEPSF",
        "Ele2_HEEPSF",
        "sT_eejj",
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
        "PFMET_Type1_Pt",
        "PFMET_Type1_Phi",
        "M_e1e2",
        "M_e1j1",
        "M_e1j2",
        "M_e2j1",
        "M_e2j2",
        "Masym",
        "MejMin",
        "MejMax",
        "Meejj",
        "mass"
]
if __name__ == "__main__":

        if parallelize:
            # ncores = multiprocessing.cpu_count()
            ncores = 4  # only use 4 parallel jobs to be nice
            pool = multiprocessing.Pool(ncores)
            jobCount = 0
            for signalSample in allSignalDatasetsDict.keys():
                for idx, txtFile in enumerate(allSignalDatasetsDict[signalSample]):
                    mass = int(signalSample[signalSample.find("M")+2:signalSample.find("_", signalSample.find("M"))])
                    #tfilepath = ProcessDataset(txtFile, mass, branchesToSave)
                    try:
                        pool.apply_async(ProcessDataset, [[txtFile, mass, branchesToSave]], callback=log_result)
                        jobCount += 1
                    except KeyboardInterrupt:
                        print("\n\nCtrl-C detected: Bailing.")
                        pool.terminate()
                        exit(-1)
                    except Exception as e:
                        print("ERROR: caught exception in job for LQ mass: {}; exiting".format(mass))
                        traceback.print_exc()
                        exit(-2)
                    for bkgSample in backgroundDatasetsDict.keys():
                        for bkgTxtFile in backgroundDatasetsDict[bkgSample]:
                            try:
                                pool.apply_async(ProcessDataset, [[bkgTxtFile, mass, branchesToSave]], callback=log_result)
                                jobCount += 1
                            except KeyboardInterrupt:
                                print("\n\nCtrl-C detected: Bailing.")
                                pool.terminate()
                                exit(-1)
                            except Exception as e:
                                print("ERROR: caught exception in job for LQ mass: {}; exiting".format(mass))
                                traceback.print_exc()
                                exit(-2)
                            # ProcessDataset(bkgTxtFile, mass, branchesToSave)
            
            # now close the pool and wait for jobs to finish
            pool.close()
            sys.stdout.write(logString.format(jobCount, len(massList)))
            sys.stdout.write("\t"+str(len(result_list))+" jobs done")
            sys.stdout.flush()
            pool.join()
            # check results?
            if len(result_list) < jobCount:
                print("ERROR: {} jobs had errors. Exiting.".format(jobCount-len(result_list)))
                exit(-2)
