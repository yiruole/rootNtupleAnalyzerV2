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



def FindBestCuts(signals, bgs, lumi):

    sighist=None
    bghist=None
    nbins=None # need to get nbins first

    # Find nbins from the first 'optimizer' plot found in the signal
    for s in signals.keys():
        theFile=TFile(s,"READ")
        hist=theFile.Get("Optimizer/optimizer")
        nbins=hist.GetNbinsX()
        if (nbins<>None):
            break

    # We have to simply store the contents of this histograms because pyROOT doesn't
    # seem to do well with Cloned histograms.  (Clone copies get attached to the input file,
    # and then disappear when the input file is closed)
    sigvals=[]
    bgvals=[]
    for i in range(0,nbins):
        sigvals.append(0)
        bgvals.append(0)

    totalsignal=0
    for s in signals.keys():
        if not os.path.isfile(s):
            print "ERROR:  File %s does not seem to exist"%s
            continue
        theFile=TFile(s,"READ")
        hist=theFile.Get("Optimizer/optimizer")
        eventhist=theFile.Get("EventsPassingCuts")
        # Scale by cross section and luminosity
        # (Use the cross section of the 'raw' data prior to selection;
        #  the normalization uses the total number of events stored in bin
        #  1 of eventhist)
        hist.Scale(signals[s]*lumi/eventhist.GetBinContent(1))
        totalsignal=totalsignal+signals[s]*lumi
        for i in range(0,nbins):
            sigvals[i]=sigvals[i]+hist.GetBinContent(i+1)
        theFile.Close()

    totalbg=0
    for s in bgs.keys():
        if not os.path.isfile(s):
            print "ERROR:  File %s does not seem to exist"%s
            continue
        theFile=TFile(s,"READ")
        hist=theFile.Get("Optimizer/optimizer")
        eventhist=theFile.Get("EventsPassingCuts")
        # Scale by cross section and luminosity
        # (Use the cross section of the 'raw' data prior to selection;
        #  the normalization uses the total number of events stored in bin
        #  1 of eventhist)
        hist.Scale(bgs[s]*lumi/eventhist.GetBinContent(1))
        totalbg=totalbg+bgs[s]*lumi
        for i in range(0,nbins):
            bgvals[i]=bgvals[i]+hist.GetBinContent(i+1)
        theFile.Close()

    outfile = TFile("optimumCuts.root","RECREATE")
    sighist=TH1F("sighist","signal histogram",nbins,0,nbins)
    bghist=TH1F("bghist","bg histogram",nbins,0,nbins)
    SoverB=TH1F("SoverB","S over B",nbins,0,nbins)
    SoverSqrtB=TH1F("SoverSqrtB","S over sqrt(B)",nbins,0,nbins)
    SoverSqrtBplusS=TH1F("SoverSqrtBplusS","S over sqrt(B+S)",nbins,0,nbins)

    for i in range(1,nbins+1):
        sighist.SetBinContent(i,sigvals[i-1])
        bghist.SetBinContent(i,bgvals[i-1])
        if (bghist.GetBinContent(i)>0):
            SoverB.SetBinContent(i,sighist.GetBinContent(i)/bghist.GetBinContent(i))
            SoverSqrtB.SetBinContent(i,sighist.GetBinContent(i)/pow(bghist.GetBinContent(i),0.5))
        elif (sighist.GetBinContent(i)>0):
            SoverSqrtBplusS.SetBinContent(i,sighist.GetBinContent(i)/pow(bghist.GetBinContent(i)+sighist.GetBinContent(i),0.5))
    
    sighist.Write()
    bghist.Write()
    SoverB.Write()
    SoverSqrtB.Write()
    SoverSqrtBplusS.Write()

    print "Maximum S/B value of %.3f at cut # %i"%(SoverB.GetMaximum(),SoverB.GetMaximumBin()-1)
    print "\tSignal efficiency = %.3f"%(sighist.GetBinContent(SoverB.GetMaximumBin()-1)/totalsignal)
    print "Maximum S/sqrt(B) value of %.3f at cut # %i"%(SoverSqrtB.GetMaximum(),
                                                         SoverSqrtB.GetMaximumBin())
    print "\tSignal efficiency = %.3f"%(sighist.GetBinContent(SoverSqrtB.GetMaximumBin()-1)/totalsignal)
    print "Maximum S/sqrt(S+B) value of %.3f at cut # %i"%(SoverSqrtBplusS.GetMaximum(),
                                                           SoverSqrtBplusS.GetMaximumBin())
    print "\tSignal efficiency = %.3f"%(sighist.GetBinContent(SoverSqrtBplusS.GetMaximumBin()-1)/totalsignal)
    outfile.Close()



if __name__=="__main__":

    # get input information from command line
    parser=OptionParser()
    parser.add_option("-s", "--signal",
                      action="append",dest="signal",
                      type="string",
                      help="signal input file(s)")
    parser.add_option("-b", "--bg",
                      action="append",
                      dest="bg",
                      type="string",
                      help="background input file(s)")
    parser.add_option("-x","--sigxsec",
                      action="append",dest="signalxsec",
                      type="float",
                      help="signal cross section")
    parser.add_option("-y","--bgxsec",
                      action="append",dest="bgxsec",
                      type="float",
                      help="bg cross section")
    parser.add_option("-l","-L","--lumi",
                      action="store",type="float",
                      dest="lumi", default=1.,
                      help = "integrated luminosity (inverse units of cross-section)")
    parser.add_option("-f","--file",
                      action="store",
                      dest="file",
                      help="read input files, cross-sections from a file (not yet implemented)")
    (options,args)=parser.parse_args()

    # Add code here to read information from a file at some point

    # Check that signal, bg, and xsections are all provided
    if (options.signal==None):
        print "ERROR:  No signal provided"
        sys.exit()
    elif (options.signalxsec==None):
        print "ERROR:  No signal cross section provided"
        sys.exit()
    elif (options.bg==None):
        print "ERROR:  No bg provided"
        sys.exit()
    elif (options.bgxsec==None):
        print "ERROR:  No bg cross section provided"
        sys.exit()

    # Check that number of signal inputs match number of signal xsections provided 
    if (len (options.signal) <> len(options.signalxsec)):
        print "ERROR:  A total of %i signal inputs were provided, but %i cross sections"%(len(options.signal),len(options.signalxsec))
        print "You must provide one cross section value for every signal input"
        sys.exit()

    # Check # of bg files, xsecs
    if (len (options.bg) <> len(options.bgxsec)):
        print "ERROR:  A total of %i bg inputs were provided, but %i cross sections"%(len(options.bg),len(options.bgxsec))
        print "You must provide one cross section value for every bg input"
        sys.exit()
        
    # Create dictionaries that use file names as keys, and cross-sections as values
    signals={}
    bgs={}
    for i in range(len(options.signal)):
        signals[options.signal[i]]=options.signalxsec[i]
    for i in range(len(options.bg)):
        bgs[options.bg[i]]=options.bgxsec[i]

    # Run the "FindBestCuts" algorithm
    FindBestCuts(signals, bgs, options.lumi)
