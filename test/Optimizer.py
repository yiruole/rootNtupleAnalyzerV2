#!/usr/bin/env python

from optparse import OptionParser
import string
import sys
import os
from array import array

try:
    print "Importing ROOT...",
    from ROOT import *
    print "Done!"
except:
    print "Cannot import pyROOT!"
    print "Try setting up a CMSSW release area first!"
    sys.exit()


class Optimizer:

    def __init__(self,args=[]):
        # Add **kw arguments when I figure out how to  pass optparse options to class
        self.signal=None
        self.bg=None # allow for lists of BG?

        self.debug=False
        self.mychoice=[]
        for i in args:
            try:
                self.mychoice.append(string.atoi(i))
            except:
                print "Error; argument %s is not an integer!"%i

        self.hist_sig=None
        self.hist_bg=None
        
    def RunCode(self):
        # Check that files exist
        if (self.signal==None):
            print "Sorry, no signal file specified!"
            return
        if (self.bg==None):
            print "Sorry, no bg file specified!"
            return
        if not os.path.isfile(self.signal):
            print "Sorry, can't find signal file '%s'"%self.signal
            return
        if not os.path.isfile(self.bg):
            print "Sorry, can't find bg file '%s'"%self.bg
            return
        
        theFile=TFile(self.signal,"READ")

        # Pick histogram/distribution to optimize (signal)
        choice=""
        chosen=False
        counter=0
        keys=theFile.GetListOfKeys()
        while (chosen==False):  # break once choice is made
            print "Choose directory/file  value:"
            print "Value\t\tname"
            print "-----\t\t-----"
            for i in range(len(keys)):
                print "%s\t\t%s"%(i, keys[i].GetName())
            value=-1
            if (counter<len(self.mychoice)):
                value=self.mychoice[counter]
            # Allow for user input (and revision in the case where command-line input was out of range)
            while value not in range(len(keys)):
                value=input("\nEnter value choice:  ")
                if (value <0):
                    print "Exiting..."
                    sys.exit()

            choice=os.path.join(choice,keys[value].GetName()) # add directory/histogram name to choice
            if not keys[value].IsFolder(): # choice is not a subdirectory; assume it's a histogram
                chosen=True
                self.hist_sig=gDirectory.Get(keys[value].GetName()) # get the histogram
            else:
                counter=counter+1
                # move to new folder, get a list of its contents
                gDirectory.cd(keys[value].GetName())
                gDirectory.Get(keys[value].GetName())
                keys=gDirectory.GetListOfKeys()

        if (self.hist_sig==None):
            print "Sorry, unable to read histogram %s from signal file %s "%(choice, self.signal)


        # Pick histogram/distribution to optimize (background)
        bgfile=TFile(self.bg,"READ")
        choice=""
        chosen=False
        counter=0
        keys=bgfile.GetListOfKeys()
        while (chosen==False):  # break once choice is made
            print "Choose directory/file  value:"
            print "Value\t\tname"
            print "-----\t\t-----"
            for i in range(len(keys)):
                print "%s\t\t%s"%(i, keys[i].GetName())
            value=-1
            if (counter<len(self.mychoice)):
                value=self.mychoice[counter]
            # Allow for user input (and revision in the case where command-line input was out of range)
            while value not in range(len(keys)):
                value=input("\nEnter value choice:  ")
                if (value <0):
                    print "Exiting..."
                    sys.exit()

            choice=os.path.join(choice,keys[value].GetName()) # add directory/histogram name to choice
            if not keys[value].IsFolder(): # choice is not a subdirectory; assume it's a histogram
                chosen=True
                self.hist_bg=gDirectory.Get(keys[value].GetName()) # get the histogram
            else:
                counter=counter+1
                # move to new folder, get a list of its contents
                gDirectory.cd(keys[value].GetName())
                gDirectory.Get(keys[value].GetName())
                keys=gDirectory.GetListOfKeys()

        if (self.hist_bg==None):
            print "Sorry, unable to read histogram %s from background file %s "%(choice, self.bg)

        print "Running optimize on histogram %s"%choice
        self.Optimize()
        return

    def Optimize(self):
        self.myfile=TFile("optimize_output.root","RECREATE") # new output file

        # Renormalize histograms to expected luminosity yields
        self.hist_sig.Sumw2()
        self.hist_bg.Sumw2()

        # Need to assume same histogram binning for both at this point
        cutthresh=self.hist_sig.GetBinLowEdge(1) 

        Xbins=self.hist_sig.GetNbinsX()
        Xmin=self.hist_sig.GetXaxis().GetXmin()
        Xmax=self.hist_sig.GetXaxis().GetXmax()

        h_mysig=TH1F("signal","signal",Xbins,Xmin,Xmax)  
        h_mybg=TH1F("bg","bg",Xbins,Xmin,Xmax)

        h_mysig.Add(self.hist_sig)
        h_mybg.Add(self.hist_bg)

        h_SoB=TH1F("soverb","s/b vs cut",Xbins,Xmin,Xmax)
        h_SoB.Sumw2()
        h_SB=TH1F("srootb","s/pow(b,0.5) vs cut",Xbins,Xmin,Xmax)
        h_SB.Sumw2()
        h_SSB=TH1F("srootsplusb","s/pow(s+b,0.5) vs cut",Xbins,Xmin,Xmax)
        h_SSB.Sumw2()

        # Set up values for maximizing S/sqrt(B), S/sqrt(B+S)
        SoB=OptVal()
        SB=OptVal()
        SSB=OptVal()

        # loop over bins
        for i in range(1,Xbins+1):
            print "bin: %.0f"%i
            # Default checks signal, bg greater than threshold bin "i"
            sig=self.hist_sig.GetBinContent(i)
            bg =self.hist_bg.GetBinContent(i)

            if (bg>0):
                # Calculate S/B
                value=sig/bg
                h_SoB.SetBinContent(i,value)
                SoB.eval(value,i)

                # Calculate S/sqrt(B)
                value=sig/pow(bg,0.5)
                h_SB.SetBinContent(i,value)
                SB.eval(value,i)
                
            if (sig+bg>0):
                # Calculate S/sqrt(S+B)
                value=sig/(pow(sig+bg,0.5))
                h_SSB.SetBinContent(i,value)
                SSB.eval(value,i)

        # Dump out optimized cut information
        print "\n\nOptimized cuts (assuming value > CUT): "
        print "S/B:\t\t\t%.3f\t\t at bin \t\t %.0f"%(SoB.maxval,SoB.maxbin)
        print "S/pow(B,0.5):\t\t%.3f\t\t at bin \t\t %.0f"%(SB.maxval,SB.maxbin)
        print "S/pow(S+B,0.5):\t\t%.3f\t\t at bin \t\t %.0f"%(SSB.maxval,SSB.maxbin)

        self.myfile.Write()
        self.myfile.Close()

        return
    
class OptVal:
    def __init__(self):
        self.maxval=-9999
        self.maxbin=-9999

    def eval(self,value,bin):
        if (value>self.maxval):
            self.maxval=value
            self.maxbin=bin
            return True
        return False
##############################################

if __name__=="__main__":

    parser=OptionParser()
    parser.add_option("-s","--signal",
                      action="store",dest="signal",default=None,
                      help="signal input file")
    parser.add_option("-b","--bg",
                      action="store",dest="bg",default=None,
                      help="background input file")
    parser.add_option("-v","--verbose",
                      action="store_true",dest="debug",default=False,
                      help="print debug statements")
    (options,args)=parser.parse_args()
    x=Optimizer(args)
    x.signal=options.signal
    x.bg=options.bg
    x.debug=options.debug
    x.RunCode()  # Checks for files, runs optimization

