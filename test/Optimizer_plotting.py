#!/usr/bin/env python

#---Import
import sys
import string
from optparse import OptionParser
import os.path
from ROOT import *
import re


#--- ROOT general options
gStyle.SetOptStat(0)
gStyle.SetPalette(1)
gStyle.SetCanvasBorderMode(0)
gStyle.SetFrameBorderMode(0)
gStyle.SetCanvasColor(kWhite)
gStyle.SetPadTickX(1);
gStyle.SetPadTickY(1);


#---Option Parser
#--- TODO: WHY PARSER DOES NOT WORK IN CMSSW ENVIRONMENT? ---#
usage = "usage: %prog [options] \nExample: ./Optimizer_plotting.py -i optimize_output.root"

parser = OptionParser(usage=usage)

parser.add_option("-i", "--inputRootFile", dest="inputRootFile",
                  help="the rootfile containing the histograms with optimization results",
                  metavar="INPUTROOTFILE")

(options, args) = parser.parse_args()

if len(sys.argv)<2:
    print usage
    sys.exit()


#---------

if(os.path.isfile(options.inputRootFile) == False):
    print "ERROR: file " + options.inputRootFile + " not found"
    print "exiting..."
    sys.exit()
inputfile = TFile(options.inputRootFile)
inputfile.ls()

#----------

h_optResults = TH1F()
h_optResults = inputfile.Get("srootsplusb")
#h_optResults = inputfile.Get("srootb")
#h_optResults = inputfile.Get("soverb")

plot1D = 1
plot2D = 0

if(plot1D):
    #### 2D histo template
    h1_value_x = TH1F()
    h1_value_x.SetBins(10,-0.5,9.5)
    
    for x in range(0, 10):
        thisBin = 5*100 + 7*10 + x   #DeltaPhi=x
        h1_value_x.SetBinContent(x+1,h_optResults.GetBinContent(thisBin))
        
    c1 = TCanvas()
    h1_value_x.Draw("HIST")
    #####


if(plot2D):
    #### 2D histo template
    h2_value_x_vs_y = TH2F()
    h2_value_x_vs_y.SetBins(10,-0.5,9.5,10,-0.5,9.5)
    
    for x in range(0, 10):
        for y in range(0, 10):
            thisBin = x*100 + y*10 + 3   #MT=x and ST=y
            #thisBin = 5*100 + x*10 + y   #ST=x and DeltaPhi=y
            h2_value_x_vs_y.SetBinContent(x+1,y+1,h_optResults.GetBinContent(thisBin))
            
    c1 = TCanvas()
    h2_value_x_vs_y.Draw("colz")
    #####



## Terminate the program
print "Press ENTER to terminate"
wait=raw_input()
