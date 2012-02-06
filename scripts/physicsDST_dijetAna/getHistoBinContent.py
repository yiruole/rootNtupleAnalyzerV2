#!/usr/bin/env python

##############################################################################
## DONT'T MODIFY WITHIN "# %%%%%%% BEGIN %%%%%%%"  and "# %%%%%%% END %%%%%%%"
##############################################################################

#---Import
import sys
import string
from optparse import OptionParser
import os.path
from ROOT import *
import re
import ROOT
from array import array
import copy


#--- ROOT general options
gROOT.SetBatch(kFALSE);
gStyle.SetOptStat(0)
gStyle.SetPalette(1)
gStyle.SetCanvasBorderMode(0)
gStyle.SetFrameBorderMode(0)
gStyle.SetCanvasColor(kWhite)
gStyle.SetPadTickX(1);
gStyle.SetPadTickY(1);
gStyle.SetPadTopMargin(0.08);
gStyle.SetPadBottomMargin(0.12);
#gStyle.SetTitleSize(0.05, "XYZ");
#--- TODO: WHY IT DOES NOT LOAD THE DEFAULT ROOTLOGON.C ? ---#

#--- Define functions

# %%%%%%% BEGIN %%%%%%%     

def GetFile(filename):
    file = TFile(filename)
    if( not file):
        print "ERROR: file " + filename + " not found"
        print "exiting..."
        sys.exit()
    return file

def GetHisto( histoName , file , scale = 1 ):
    file.cd()
    histo = file.Get( histoName )
    if( not histo ):
        print "ERROR: histo " + histoName + " not found in " + file.GetName()
        print "exiting..."
        sys.exit()
    new = copy.deepcopy(histo)
    if(scale!=1):
        new.Scale(scale)
    return new

#---Option Parser
#--- TODO: WHY PARSER DOES NOT WORK IN CMSSW ENVIRONMENT? ---#
usage = "usage: %prog [options] \nExample: \n python getHistoBinContent.py -i \"/data/santanas/Results/dijets_PhysicsDST/117pb-1_JECL123Res__Fall11MC_JECL123__06_02_2012/finalResults_QstarToJJ_M-500_qg.root\" -n M_PFJet1PFJet2_shifted_1"

parser = OptionParser(usage=usage)

parser.add_option("-i", "--inputFile", dest="inputFile",
                  help="input file",
                  metavar="FILE")

parser.add_option("-n", "--histo", dest="histo",
                  help="the histogram",
                  metavar="HISTO")

(options, args) = parser.parse_args()

if len(sys.argv)<4:
    print usage
    sys.exit()

#############################################################

file = GetFile(options.inputFile)
#file.ls()
nameOriginal = string.split( string.split(options.inputFile, "/")[-1] , ".root")[0]
name = string.replace(nameOriginal,"-","_") 
#print name
histogram = GetHisto( options.histo , file )
#histogram.Draw()

print "double " + name + "_" +options.histo + " [50] = {" , 
for bin in range( 1 , histogram.GetNbinsX()+1 ):
    #print histogram.GetBinContent(bin)
    if( bin == histogram.GetNbinsX() ):
        print str(histogram.GetBinContent(bin)) + "};" 
        #print >> outputMassFile, str(histogram.GetBinContent(bin)) + "}" 
    else:
        print str(histogram.GetBinContent(bin)) + ", " ,
        #print >> outputMassFile, str(histogram.GetBinContent(bin)) + ", " ,
        
## Terminate the program
#print "Press ENTER to terminate"
#wait=raw_input()
