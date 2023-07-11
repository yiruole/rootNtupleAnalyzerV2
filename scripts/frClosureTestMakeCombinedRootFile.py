
from __future__ import print_function

from ROOT import (
    gROOT,
    TFile,
    TH1D,
    TCanvas,
    TColor,
    TLegend
)
import ROOT
import numpy as np
import copy
import ctypes
import sys
import os
import math

#runs on the output of combinePlots for 1P1F and 2F. Copies the histos you need for the closure test into a single ROOT file. Also adds all the MC together to make an MC total histo, and puts that in the output file too.
input_file2F = "$LQDATA/2016/qcdFRClosureTest/frClosureTest_2016pre_summer23/2F/withEtaRegs/output_cutTable_lq_QCD_FakeRateClosureTest/analysisClass_lq_QCD_FakeRateClosureTest_plots.root"
input_file1P1F = "$LQDATA/2016/qcdFRClosureTest/frClosureTest_2016pre_July23/1P1F/output_cutTable_lq_QCD_FakeRateClosureTest/analysisClass_lq_QCD_FakeRateClosureTest_plots.root"
output_name = "$LQDATA/2016/qcdFRClosureTest/frClosureTest_2016pre_July23/FRCTCombined.root"

#run
gROOT.SetBatch(True)

output_file = TFile(output_name,"recreate")
variableNameList = ["Pt1stEle_PAS","Me1j1_PAS","Mee_PAS","sT_PAS"]
histoNameData = "histo1D__QCDFakes_DATA__"
#both eles barrel, one barrel one endcap, both eles endcap
etaRegions = ["_BB","_BE","_EE",""]
fileList = [input_file2F, input_file1P1F]

#mcSamples = ["ZJet_amcatnlo_ptBinned_IncStitch", "WJet_amcatnlo_Inc","WJet_amcatnlo_jetBinned_lte1Jet", "TTbar_powheg", "SingleTop", "PhotonJets_Madgraph", "DIBOSON_nlo"]
#mcSamples = ["ZJet_amcatnlo_ptBinned_IncStitch","WJet_amcatnlo_jetBinned_lte1Jet", "TTbar_powheg", "SingleTop", "PhotonJets_Madgraph", "DIBOSON_nlo"]
#mcSamples = ["ZJet_amcatnlo_ptBinned_IncStitch","WJet_amcatnlo_jetBinned", "TTbar_powheg", "SingleTop", "PhotonJets_Madgraph", "DIBOSON_nlo"]
#mcSamples = ["ZJet_amcatnlo_ptBinned_IncStitch","WJetHT", "TTbar_powheg", "SingleTop", "PhotonJets_Madgraph", "DIBOSON_nlo"]
mcSamples = ["ZJet_amcatnlo_ptBinned_IncStitch","WJetSherpa", "TTbar_powheg", "SingleTop", "PhotonJets_Madgraph", "DIBOSON_nlo"]
histoNamesMC = []
for name in mcSamples:
    histoNamesMC.append("histo1D__"+name+"__")

for filename in fileList:
    tfile = TFile.Open(filename)
    print("opening "+filename)
    for variableName in variableNameList:
        for region in etaRegions:
            histoData = tfile.Get(histoNameData+variableName+region)    
            output_file.cd()
            if "1P1F" in filename:
                histoData.SetName("histo1D__QCDFakes_DATA1P1F__"+variableName+region)
                histoMCTotal = 0
                for name in histoNamesMC:
                    histo = tfile.Get(name + variableName+region)
                    print("writing histo "+histo.GetName())
                    histo.Write()
                    if not histoMCTotal:
                        histoMCTotal = copy.deepcopy(histo)
                        histoMCTotal.SetName("histo1D__MCTotal__"+variableName+region)
                    else:
                        histoMCTotal.Add(histo)
                print("writing histo "+histoMCTotal.GetName())
                histoMCTotal.Write()
            elif "2F" in filename:
                histoData.SetName("histo1D__QCDFakes_DATA2F__"+variableName+region)
            else:
                print("cannot determine region (2F or 1P1F) from filename")
                break
            print("writing histo "+histoData.GetName())
            histoData.Write()
print("histos written to "+output_name)
