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
        "WJet_amcatnlo_jetBinned" : [
            inputListBkgBase+"WToLNu_0J_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WToLNu_1J_backup_amcatnloFXFX_pythia8.txt",
            inputListBkgBase+"WToLNu_2J_amcatnloFXFX_pythia8.txt",
            ],
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
allSignalDatasetsDict = {}
signalNameTemplate = "LQToDEle_M-{}_pair_pythia8"
massList = list(range(300, 3100, 100))
massList.extend([3500, 4000])
massList.remove(2500)  # for 2016
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
outputTFileDir = "root://eosuser.cern.ch//eos/user/s/scooper/LQ/NanoV7/2016/analysis/bdtTraining_eejj_finalSels_egLoose_4feb2022_mee200st400_allLQ"
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
