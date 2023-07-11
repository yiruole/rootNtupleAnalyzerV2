from __future__ import print_function

from ROOT import (
    gROOT,
    TFile,
    TH1D,
    TCanvas,
    TColor,
    TLegend,
    kRed,
    kGreen,
    kAzure,
    kOrange,
    kGray,
    kViolet,
    kBlack,
    THStack,
    TRatioPlot,
    TPad,
    TLine,
)
import ROOT
import numpy as np
import copy
import ctypes
import sys
import os
import math

def MakeStackAndRatioPlot(histDict,histoKeysForStack):
    bkgHist = 0
    stack = THStack()
    dataHist = histDict["data"]
    for key in histoKeysForStack:
        hist = histDict["bkg"][key]
        stack.Add(hist)
        if not bkgHist:
            bkgHist = copy.deepcopy(hist)
        else:
            bkgHist.Add(hist)
    stack.SetMaximum(1e4)
    stack.SetMinimum(1)
    ratioPlot = copy.deepcopy(dataHist)
    ratioPlot.Divide(bkgHist)
    ratioPlot.SetTitle("")
    ratioPlot.SetStats(0)
    ratioPlot.GetYaxis().SetRangeUser(0,2)
    ratioPlot.GetYaxis().SetLabelSize(0.08)
    ratioPlot.GetYaxis().SetTitle("1P1F data / bkg.")
    ratioPlot.GetYaxis().SetTitleSize(0.06)
    ratioPlot.GetXaxis().SetLabelSize(0.08)
    ratioPlot.GetXaxis().SetTitleSize(0.08)
    return stack, ratioPlot

input_file = "$LQDATA/2016/qcdFRClosureTest/frClosureTest_2016pre_July23/FRCTCombined.root"
pdf_folder = "$LQDATA/2016/qcdFRClosureTest/frClosureTest_2016pre_July23/plots"

gROOT.SetBatch(True)

tfile = TFile.Open(input_file)
binsDict = {}
#generate ptBins
ptBins = [50]
#I want 50 GeV bins up to 500
binLowEdge = 50
ptRange1 = 500-50
for i in range(int(ptRange1/50)):
    binHighEdge = binLowEdge+50
    ptBins.append(binHighEdge)
    binLowEdge = binHighEdge
#and 100 GeV bins from 500 to 700
ptRange2 = 700-500
for i in range(int(ptRange2/100)):
    binHighEdge = binLowEdge+100
    ptBins.append(binHighEdge)
    binLowEdge = binHighEdge
#and end at 1000
ptBins.append(1000)
binsDict["Pt1stEle_PAS"] = ptBins
#Me1j1 bins
binLowEdge = 200
me1j1Bins = [50,200]
mejRange1 = 1300-200
for i in range(int(mejRange1/100)):
    binHighEdge = binLowEdge+100
    me1j1Bins.append(binHighEdge)
    binLowEdge = binHighEdge
me1j1Bins.append(1500)
me1j1Bins.append(1700)
me1j1Bins.append(2000)
binsDict["Me1j1_PAS"] = me1j1Bins
#Mee bins
meeBins = [110,200]
meeRange1 = 1300-200
binLowEdge = 200
for i in range(int(meeRange1/100)):
    binHighEdge = binLowEdge+100
    meeBins.append(binHighEdge)
    binLowEdge = binHighEdge
meeBins.append(1500)
meeBins.append(1700)
meeBins.append(2000)
binsDict["Mee_PAS"] = meeBins
#sT bins
sTBins = [200]
sTRange1 = 1200-200
binLowEdge = 200
for i in range(int(sTRange1/100)):
    binHighEdge = binLowEdge+100
    sTBins.append(binHighEdge)
    binLowEdge = binHighEdge
sTBins.append(1400)
sTBins.append(2000)
binsDict["sT_PAS"] = sTBins

etaRegs = ["_BB","_BE","_EE",""]
#get histos
variable_names = ["Pt1stEle_PAS","Me1j1_PAS","Mee_PAS","sT_PAS"]
histDict = {}
for region in etaRegs:
    histDict[region] = {}
    for var in variable_names:
        histDict[region][var] = {}
        histDict[region][var]["bkg"] = {}
        histDict[region][var]["bkg"]["fakeRate"] = tfile.Get("histo1D__QCDFakes_DATA2F__"+var+region)
        histDict[region][var]["data"] = tfile.Get("histo1D__QCDFakes_DATA1P1F__"+var+region)
        histDict[region][var]["bkg"]["MCOnly"] = tfile.Get("histo1D__MCTotal__"+var+region)
#mcSamples = ["ZJet_amcatnlo_ptBinned_IncStitch", "WJet_amcatnlo_Inc", "TTbar_powheg", "SingleTop", "PhotonJets_Madgraph", "DIBOSON_nlo"]
#mcSamples = ["ZJet_amcatnlo_ptBinned_IncStitch", "WJet_amcatnlo_jetBinned_lte1Jet", "TTbar_powheg", "SingleTop", "PhotonJets_Madgraph", "DIBOSON_nlo"]
#mcSamples = ["ZJet_amcatnlo_ptBinned_IncStitch", "WJet_amcatnlo_jetBinned", "TTbar_powheg", "SingleTop", "PhotonJets_Madgraph", "DIBOSON_nlo"]
#mcSamples = ["ZJet_amcatnlo_ptBinned_IncStitch", "WJetHT", "TTbar_powheg", "SingleTop", "PhotonJets_Madgraph", "DIBOSON_nlo"]
mcSamples = ["ZJet_amcatnlo_ptBinned_IncStitch", "WJetSherpa", "TTbar_powheg", "SingleTop", "PhotonJets_Madgraph", "DIBOSON_nlo"]
mcShortNames = ["ZJets", "WJets", "TTBar", "ST", "GJets", "Diboson"]
allBkgNames = ["ZJets", "WJets", "TTBar", "ST", "GJets", "Diboson","fakeRate"]
allBkgNamesNoW = ["ZJets","TTBar", "ST", "GJets", "Diboson","fakeRate"]
mcShortNamesNoW = ["ZJets", "TTBar", "ST", "GJets", "Diboson"]
colors = [kRed, kViolet+6, 600, kGreen, kAzure+1, kOrange-3,kGray+1]

for index, sample in enumerate(mcSamples):
    for region in etaRegs:
        for variableName in variable_names:
            histo = tfile.Get("histo1D__"+sample+"__"+variableName+region)
            histDict[region][variableName]["bkg"][mcShortNames[index]] = histo

#set colors and style
for region in etaRegs:
    for var in variable_names:
        histDict[region][var]["data"].SetLineWidth(2)
        for index, name in enumerate(allBkgNames):
            histo = histDict[region][var]["bkg"][name]
            histo.SetLineColor(colors[index])
            histo.SetFillColor(colors[index])
            histo.SetMarkerColor(colors[index])
            histo.SetLineWidth(2)
            histo.SetStats(0)

#print(histDict)
#rebin histos
histDictRebinned = {}
for region in etaRegs:
    histDictRebinned[region] = {}
    for var in variable_names:
        histDictRebinned[region][var] = {}
        bins = binsDict[var]
        #print("rebinning: ",var," Bins: ",bins)
        histDictRebinned[region][var]["data"] = histDict[region][var]["data"].Rebin(len(bins)-1,"data_rebinned",np.array(bins, dtype = float))
        #histDictRebinned[region][var]["data"] = copy.deepcopy(histDict[region][var]["data"])
        #histDictRebinned[region][var]["data"].Rebin(4)
        histDictRebinned[region][var]["bkg"] = {}
        histDictRebinned[region][var]["bkg"]["MCOnly"] = histDict[region][var]["bkg"]["MCOnly"].Rebin(len(bins)-1,"data_rebinned",np.array(bins, dtype = float))
        #histDictRebinned[region][var]["bkg"]["MCOnly"] = copy.deepcopy(histDict[region][var]["bkg"]["MCOnly"])
        #histDictRebinned[region][var]["bkg"]["MCOnly"].Rebin(4)
        for name in allBkgNames:
            histDictRebinned[region][var]["bkg"][name] = histDict[region][var]["bkg"][name].Rebin(len(bins)-1,name+"_rebinned",np.array(bins, dtype = float))
            #histDictRebinned[region][var]["bkg"][name] = copy.deepcopy(histDict[region][var]["bkg"][name])
            #histDictRebinned[region][var]["bkg"][name].Rebin(4)

#make background MC plots. One set as is and one rebinned, for all eta regions
c1 = TCanvas()
c1.SetGridy()
c1.SetLogy()
c2 = TCanvas()
c2.SetGridy()
c2.SetLogy()
for reg in etaRegs:
    for var in variable_names:
        varPieces = var.split("_")
        axisTitle = varPieces[0] + " (GeV)"
        l = TLegend(0.5,0.7,0.8,0.9)
        c1.cd()
        for i,name in enumerate(mcShortNames):
            histo = histDict[reg][var]["bkg"][name]
            if i==0:
                histCopy = copy.deepcopy(histo)
                histCopy.GetXaxis().SetTitle(axisTitle)
                if "st" in var.lower():
                    histCopy.GetXaxis().SetRangeUser(150,2000)
                elif "mee" in var.lower():
                    histCopy.GetXaxis().SetRangeUser(50,2000)
                elif "me1j1" in var.lower():
                    histCopy.GetXaxis().SetRangeUser(0,2000)
                else:
                    histCopy.GetXaxis().SetRangeUser(0,1000)
                histCopy.Draw()
            else:
                histo.Draw("same")
            l.AddEntry(histo,name,"lp")
            l.Draw("same")
        c1.Print(pdf_folder+"/"+var+"/mcHists_"+var+reg+".pdf")
        c2.cd()
        for i,name in enumerate(mcShortNames):
            histo2 = histDictRebinned[reg][var]["bkg"][name]
            #histo.Rebin(2)
            if i==0:
                hist2Copy = copy.deepcopy(histo2)
                hist2Copy.GetXaxis().SetTitle(axisTitle)
                if "st" in var.lower():
                    hist2Copy.GetXaxis().SetRangeUser(150,2000)
                elif "mee" in var.lower():
                    hist2Copy.GetXaxis().SetRangeUser(50,2000)
                elif "me1j1" in var.lower():
                    hist2Copy.GetXaxis().SetRangeUser(0,2000)
                else:
                    hist2Copy.GetXaxis().SetRangeUser(0,1000)
                hist2Copy.Draw()
            else:
                histo2.Draw("same")
        l.Draw("same")
        c2.Print(pdf_folder+"/"+var+"/mcHistsRebinned_"+var+reg+".pdf")

#make stack and ratio plots
stackAllBkg = {}
ratioAllBkg = {}
for reg in etaRegs:
    stackAllBkg[reg] = {}
    ratioAllBkg[reg] = {}
    for var in variable_names:
        stackAllBkg[reg][var],ratioAllBkg[reg][var] = MakeStackAndRatioPlot(histDictRebinned[reg][var], allBkgNames)

#make canvas, pads and legend
c = TCanvas()
c.SetLogy()
fPads1 = TPad("p1","",0.00,0.3,0.99,0.99)
fPads2 = TPad("p2","",0.00,0.00,0.99,0.301)
fPads1.SetFillColor(0)
fPads1.SetLineColor(0)
fPads2.SetFillColor(0)
fPads2.SetLineColor(0)
fPads1.SetBottomMargin(1e-2)
fPads2.SetTopMargin(3e-2)
fPads2.SetBottomMargin(3e-1)
fPads1.SetLogy()
fPads2.SetGridy()
fPads1.Draw()
fPads2.Draw()
leg = TLegend(0.6,0.6,0.9,0.9)
#Note: it doesn't matter which eta region and var name I use to make the legend bc it's the same samples for all of them
for name in allBkgNames:
    histo = histDictRebinned[""]["Pt1stEle_PAS"]["bkg"][name]
    leg.AddEntry(histo,name,"lp")
leg.AddEntry(histDictRebinned[""]["Pt1stEle_PAS"]["data"],"1P1F data","lp")

#draw stack and ratio plots
for reg in etaRegs:
    for var in variable_names:
        varPieces = var.split("_")
        axisTitle = varPieces[0] + " (GeV)"
        fPads1.cd()
        stackAllBkg[reg][var].SetTitle(var+reg)
        stackAllBkg[reg][var].Draw("hist")
        histDictRebinned[reg][var]["data"].Draw("same")
        #histDict[reg]["data"].Draw("same")
        leg.Draw("same")

        fPads2.cd()
        ratioAllBkg[reg][var].GetXaxis().SetTitle(axisTitle)
        ratioAllBkg[reg][var].Draw()
        line = TLine(0,1,2000,1)
        line.Draw("same")
        line.SetLineStyle(5)
        line.SetLineColorAlpha(13, 0.5)
        c.Print(pdf_folder+"/"+var+"/stack_plot_"+var+reg+".pdf")
    #c.Print(pdf_folder+"/stack_plot"+reg+"_not_rebinned.pdf")
#make the same stack/ratio plot without the 2F data added in
#fPads1.cd()
#fPads1.SetLogy()
#stackMCOnly.Draw("hist")
#histDict["rebinned"]["data"].Draw("same")
#fPads2.cd()
#fPads2.SetGridy()
#ratioMCOnly.Draw()
#line.Draw("same")
#c.Print(pdf_folder+"/stack_plot_without2F.pdf")

#make mc sub plot
c = TCanvas()
c.cd()
c.SetGridy()
c.SetLogy()
for reg in etaRegs:
    for var in variable_names:
        varPieces = var.split("_")
        axisTitle = varPieces[0] +" (GeV)"
        histoMCSub = histDictRebinned[reg][var]["data"] - histDictRebinned[reg][var]["bkg"]["MCOnly"]
        #histoMCSub = histDict[reg]["data"] - histDict[reg]["bkg"]["MCOnly"]
        histoFR = histDictRebinned[reg][var]["bkg"]["fakeRate"]
        #histoFR = histDict[reg]["bkg"]["fakeRate"]
        histoMCSub.SetStats(0)
        if "gte" in pdf_folder.lower(): #gte 1Jet has more stats so I need a bigger range here since I don't do this one log scale
            histoMCSub.GetYaxis().SetRangeUser(-4000,4000)
        else:
            histoMCSub.GetYaxis().SetRangeUser(0.1,1e4)
        l = TLegend(0.6,0.7,0.9,0.9)
        l.AddEntry(histoMCSub,"data - MC 1P1F region","lp")
        l.AddEntry(histoFR,"prediction by fake rate","lp")
        histoMCSub.GetXaxis().SetTitle(axisTitle)
        histoMCSub.Draw()
        histoFR.Draw("same")
        l.Draw("same")
        c.Print(pdf_folder+"/"+var+"/mcSub_fr_comparison_logScale_"+var+reg+".pdf")
    #c.Print(pdf_folder+"/mcSub_fr_comparison"+reg+"_not_rebinned.pdf")
#make plot of just FR prediction by itself for comparison w the AN
c = TCanvas()
c.cd()
c.SetLogy()
c.SetGridy()
oldPtBins = [50,100,150,220,300,400,500,600,800,1000]
histoFR = histDict[""]["Pt1stEle_PAS"]["bkg"]["fakeRate"].Rebin(len(oldPtBins)-1,"FR_with_old_ptBins",np.array(oldPtBins,dtype = float))
histoFR.SetStats(0)
histoFR.GetYaxis().SetRangeUser(0.1,1e5)
histoFR.GetXaxis().SetTitle("Pt1stEle (GeV)")
histoFR.Draw()
c.Print(pdf_folder+"/Pt1stEle_PAS/fakeRatePrediction.pdf")
