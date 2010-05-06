#!/usr/bin/env python

#---Import
import sys
import string
from optparse import OptionParser
import os.path
from ROOT import *
import re
import os.path
import ROOT

#--- ROOT general options
gStyle.SetOptStat(0)
gStyle.SetPalette(1)
gStyle.SetCanvasBorderMode(0)
gStyle.SetFrameBorderMode(0)
gStyle.SetCanvasColor(kWhite)
gStyle.SetPadTickX(1);
gStyle.SetPadTickY(1);
#--- TODO: WHY IT DOES NOT LOAD THE DEFAULT ROOTLOGON.C ? ---#

#---Option Parser
#--- TODO: WHY PARSER DOES NOT WORK IN CMSSW ENVIRONMENT? ---#
usage = "usage: %prog [options] \nExample: ./makeStackHistoTemplate.py -i ../data/output/analysisClass_template_plots.root -n cutHisto_allPreviousCuts__pT1stEle -x pT_1st_ele_\(GeV\) -y number_of_entries"

parser = OptionParser(usage=usage)

parser.add_option("-n", "--nameHisto", dest="nameHisto",
                  help="name of the histogram to be plotted",
                  metavar="NAMEHISTO")

parser.add_option("-i", "--inputRootFile", dest="inputRootFile",
                  help="the rootfile containing the histograms",
                  metavar="INPUTROOTFILE")

parser.add_option("-x", "--xAxisTitle", dest="xAxisTitle",
                  help="x axis title; words must be separated by _",
                  metavar="XAXISTITLE")

parser.add_option("-y", "--yAxisTitle", dest="yAxisTitle",
                  help="y axis title; words must be separated by _",
                  metavar="YAXISTITLE")

(options, args) = parser.parse_args()

if len(sys.argv)<8:
    print usage
    sys.exit()


xaxistitle = ""
yaxistitle = ""
for word in string.split(options.xAxisTitle,"_"):
    xaxistitle += word + " "
for word in string.split(options.yAxisTitle,"_"):
    yaxistitle += word + " "

#---Check input rootfile
if(os.path.isfile(options.inputRootFile) == False):
    print "ERROR: file " + options.inputRootFile + " not found"
    print "exiting..."
    sys.exit()
inputfile = TFile(options.inputRootFile)
inputfile.ls()

#---Open output rootfile
outputFileName = string.split(string.split(sys.argv[0],"/")[-1],".")[0] + "_" + options.nameHisto + ".root"
outputfile = TFile(outputFileName, "RECREATE")

#---Create legend
legend = TLegend(0.541735,0.625304,0.873977,0.868613);
legend.SetFillColor(kWhite);
legend.SetMargin(0.2);

#---Edit histograms taken from rootfile
rebin = 5

#LQtoUE_M400
histo_LQtoUE_M400 = TH1F()
prefix = "histo1D__"+ "LQ400" + "__" 
color = 4
fillStyle = 0
histo_LQtoUE_M400 = inputfile.Get(prefix + options.nameHisto)
if( not histo_LQtoUE_M400):
    print "ERROR: histo " + prefix + options.nameHisto + " not found in " + options.inputRootFile
    print "exiting..."
    sys.exit()
histo_LQtoUE_M400.SetFillStyle(fillStyle)
histo_LQtoUE_M400.SetLineColor(color)
histo_LQtoUE_M400.Rebin(rebin)

#VQQ
histo_VQQ = TH1F()
prefix = "histo1D__"+ "VQQ" + "__" 
color = 16
colorline = 1
fillStyle = 1001
histo_VQQ = inputfile.Get(prefix + options.nameHisto)
if( not histo_VQQ):
    print "ERROR: histo " + prefix + options.nameHisto + " not found in " + options.inputRootFile
    print "exiting..."
    sys.exit()
histo_VQQ.SetFillColor(color)
histo_VQQ.SetFillStyle(fillStyle)
histo_VQQ.SetLineColor(colorline);
histo_VQQ.SetLineWidth(2);
histo_VQQ.Rebin(rebin)


#VQQ_Z
histo_VQQ_Z = TH1F()
prefix = "histo1D__"+ "VQQ_Z" + "__" 
color = 1
colorline = 1
fillStyle = 1001
histo_VQQ_Z = inputfile.Get(prefix + options.nameHisto)
if( not histo_VQQ_Z):
    print "ERROR: histo " + prefix + options.nameHisto + " not found in " + options.inputRootFile
    print "exiting..."
    sys.exit()
histo_VQQ_Z.SetFillColor(color)
histo_VQQ_Z.SetFillStyle(fillStyle)
histo_VQQ_Z.SetLineColor(colorline);
histo_VQQ_Z.SetLineWidth(2);
histo_VQQ_Z.Rebin(rebin)


#VQQ_Z_QCD
#histo_VQQ_Z_QCD = TH1F()
#prefix = "histo1D__"+ "VQQ_Z_QCD" + "__" 
#color = 3
#colorline = 1
#fillStyle = 1001
#histo_VQQ_Z_QCD = inputfile.Get(prefix + options.nameHisto)
#if( not histo_VQQ_Z_QCD):
#    print "ERROR: histo " + prefix + options.nameHisto + " not found in " + options.inputRootFile
#    print "exiting..."
#    sys.exit()
#histo_VQQ_Z_QCD.SetFillColor(color)
#histo_VQQ_Z_QCD.SetFillStyle(fillStyle)
#histo_VQQ_Z_QCD.SetLineColor(colorline);
#histo_VQQ_Z_QCD.SetLineWidth(2);
#histo_VQQ_Z_QCD.Rebin(rebin)


#VQQ_W_Z_W
histo_VQQ_Z_W = TH1F()
prefix = "histo1D__"+ "VQQ_Z_W" + "__" 
color = 15
colorLine = 1
fillStyle = 1001
histo_VQQ_Z_W = inputfile.Get(prefix + options.nameHisto)
if( not histo_VQQ_Z_W):
    print "ERROR: histo " + prefix + options.nameHisto + " not found in " + options.inputRootFile
    print "exiting..."
    sys.exit()
histo_VQQ_Z_W.SetFillColor(color)
histo_VQQ_Z_W.SetFillStyle(fillStyle)
histo_VQQ_Z_W.SetLineColor(colorLine);
histo_VQQ_Z_W.SetLineWidth(2);
histo_VQQ_Z_W.Rebin(rebin)


#ALLBKG
histo_ALLBKG = TH1F()
prefix = "histo1D__"+ "ALLBKG" + "__" 
color = 2
fillStyle = 3003
histo_ALLBKG = inputfile.Get(prefix + options.nameHisto)
if( not histo_ALLBKG):
    print "ERROR: histo " + prefix + options.nameHisto + " not found in " + options.inputRootFile
    print "exiting..."
    sys.exit()
histo_ALLBKG.SetFillColor(color)
histo_ALLBKG.SetFillStyle(fillStyle)
histo_ALLBKG.SetLineColor(color);
histo_ALLBKG.SetLineWidth(2);
histo_ALLBKG.Rebin(rebin)


#SIGALLBKG
histo_SIGALLBKG = TH1F()
prefix = "histo1D__"+ "SIGALLBKG" + "__" 
color = 4
fillStyle = 0
histo_SIGALLBKG = inputfile.Get(prefix + options.nameHisto)
if( not histo_SIGALLBKG):
    print "ERROR: histo " + prefix + options.nameHisto + " not found in " + options.inputRootFile
    print "exiting..."
    sys.exit()
histo_SIGALLBKG.SetFillColor(color)
histo_SIGALLBKG.SetFillStyle(fillStyle)
histo_SIGALLBKG.SetLineColor(color);
histo_SIGALLBKG.SetLineWidth(2);
histo_SIGALLBKG.Rebin(rebin)


print "\n"
print "plotting " + options.nameHisto + " ..."


#---Canvas
canvas = TCanvas()
canvas.SetLogy()
stackName = "stack_" + options.nameHisto
canvas.SetName(stackName)

histo_SIGALLBKG.GetYaxis().SetRangeUser(0.001,1000)
histo_SIGALLBKG.Draw("HIST")
histo_SIGALLBKG.SetStats(0)

#histo_ALLBKG.GetYaxis().SetRangeUser(0.001,1000)
histo_ALLBKG.Draw("HISTsame")
#histo_ALLBKG.SetStats(0)

histo_VQQ_Z_W.Draw("HISTsame")

histo_VQQ_Z.Draw("HISTsame")

histo_VQQ.Draw("HISTsame")

#histo_LQtoUE_M400.Scale(100)
histo_LQtoUE_M400.Draw("HISTsame")

#histo_LQtoUE_M400.Draw("same")

histo_SIGALLBKG.GetXaxis().SetTitle(xaxistitle)
histo_SIGALLBKG.GetYaxis().SetTitle(yaxistitle)
histo_SIGALLBKG.GetXaxis().SetTitleSize(0.05);
histo_SIGALLBKG.GetXaxis().SetLabelSize(0.045);
histo_SIGALLBKG.GetYaxis().SetTitleSize(0.05);
histo_SIGALLBKG.GetYaxis().SetLabelSize(0.045);


#---random generation of one pseudo-experiment
#gRandom.SetSeed(34343437);
gRandom.SetSeed(34343431);
histo_pseudoData = TH1F()
nbins_SIGALLBKG = histo_SIGALLBKG.GetXaxis().GetNbins()
min_SIGALLBKG = histo_SIGALLBKG.GetXaxis().GetXmin()
max_SIGALLBKG = histo_SIGALLBKG.GetXaxis().GetXmax()
integral_SIGALLBKG = int(histo_SIGALLBKG.Integral())
histo_pseudoData.SetBins(nbins_SIGALLBKG,min_SIGALLBKG,max_SIGALLBKG)
histo_pseudoData.FillRandom(histo_SIGALLBKG,integral_SIGALLBKG)
histo_pseudoData.SetMarkerStyle(20)
histo_pseudoData.SetMarkerSize(1)
histo_pseudoData.SetMarkerColor(1)
histo_pseudoData.Draw("Esame")

#---Filling legend
legend.AddEntry(histo_pseudoData,"e\\nujj pseudo-data (100/pb)","p");
legend.AddEntry(histo_SIGALLBKG,"LQ + \\bar{LQ} \\rightarrow eq + \\nuq","f");
#legend.AddEntry(histo_SIGALLBKG,"LQ + \\bar{LQ} \\rightarrow eq + \\nuq X 100","f");
legend.AddEntry(histo_ALLBKG,"t\\bar{t}","f");
legend.AddEntry(histo_VQQ_Z_W,"W + jets","f");
legend.AddEntry(histo_VQQ_Z,"Z/\\gamma + jets","f");
legend.AddEntry(histo_VQQ,"VQQ","f");
#legend.AddEntry(histo_LQtoUE_M400,"LQtoUE_M400","p");
legend.Draw()

#---Draw CMS preliminary
l = TLatex()
l.SetTextAlign(12)
l.SetTextSize(0.06)
l.SetTextFont(62)
l.SetNDC()
l.DrawLatex(0.13,0.85,"CMS Preliminary")

#---Redraw axis
gPad.RedrawAxis()
gPad.Modified()
canvas.Update()

#---Write
histo_SIGALLBKG.Write()
histo_ALLBKG.Write()
histo_VQQ_Z_W.Write()
histo_VQQ_Z.Write()
histo_VQQ_Z.Write()
histo_VQQ.Write()
histo_LQtoUE_M400.Write()
legend.Write()
canvas.Write()
#canvas.SaveAs(stackName + ".gif")
#canvas.SaveAs(stackName + ".eps")

print "writing " + outputFileName + " ..."

## Terminate the program
print "Press ENTER to terminate"
wait=raw_input()

inputfile.Close()
outputfile.Close()
