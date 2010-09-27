#!/usr/bin/env python

#---Import
import sys
import string
from optparse import OptionParser
import os.path
from ROOT import *
import re


#---Option Parser
#--- TODO: WHY PARSER DOES NOT WORK IN CMSSW ENVIRONMENT? ---#
usage = "usage: %prog [options] \nExample: \n./combinePlotsTemplate.py -i /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config/inputListAllCurrent.txt -c analysisClass_genStudies -d /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/data/output -l 100 -x /home/santanas/Data/Leptoquarks/RootNtuples/V00-00-06_2008121_163513/xsection_pb_default.txt -o /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/data/output -s /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config/sampleListForMerging.txt"

parser = OptionParser(usage=usage)

parser.add_option("-i", "--inputList", dest="inputList",
                  help="list of all datasets to be used (full path required)",
                  metavar="LIST")

parser.add_option("-c", "--code", dest="analysisCode",
                  help="name of the CODE.C code used to generate the rootfiles",
                  metavar="CODE")

parser.add_option("-d", "--inputDir", dest="inputDir",
                  help="the directory INDIR contains the rootfiles with the histograms to be combined (full path required)",
                  metavar="INDIR")

parser.add_option("-l", "--intLumi", dest="intLumi",
                  help="results are rescaled to the integrated luminosity INTLUMI (in pb-1)",
                  metavar="INTLUMI")

parser.add_option("-x", "--xsection", dest="xsection",
                  help="the file XSEC contains the cross sections (in pb) for all the datasets (full path required). Use -1 as cross section value for no-rescaling",
                  metavar="XSEC")

parser.add_option("-o", "--outputDir", dest="outputDir",
                  help="the directory OUTDIR contains the output of the program (full path required)",
                  metavar="OUTDIR")

parser.add_option("-s", "--sampleListForMerging", dest="sampleListForMerging",
                  help="put in the file SAMPLELIST the name of the sample with the associated strings which should  match with the dataset name (full path required)",
                  metavar="SAMPLELIST")

(options, args) = parser.parse_args()

if len(sys.argv)<14:
    print usage
    sys.exit()

#print options.analysisCode


#---Check if sampleListForMerging file exist
if(os.path.isfile(options.sampleListForMerging) == False):
    print "ERROR: file " + options.sampleListForMerging + " not found"
    print "exiting..."
    sys.exit()


#--- Declare histograms
dictSamples = {}

for l,line in enumerate( open( options.sampleListForMerging ) ):
    line = string.strip(line,"\n")
    print line
    
    for i,piece in enumerate(line.split()):
        print "i=", i , "  piece= " , piece
        if (i == 0):
            key = piece
            dictSamples[key] = []
        else:
            dictSamples[key].append(piece)

dictFinalHisto = {}

#--- functions

#---Loop over datasets
print "\n"
for n, lin in enumerate( open( options.inputList ) ):

    lin = string.strip(lin,"\n")
    #print lin
    
    dataset_mod = string.split( string.split(lin, "/" )[-1], ".")[0]
    print "\n" + str(n) + " " + dataset_mod + " ... "

    inputRootFile = options.inputDir + "/" + options.analysisCode + "___" + dataset_mod + ".root"
    inputDataFile = options.inputDir + "/" + options.analysisCode + "___" + dataset_mod + ".dat"

    #print inputRootFile
    #print inputDataFile

    #---Check if .root and .dat file exist
    if(os.path.isfile(inputRootFile) == False):
        print "ERROR: file " + inputRootFile + " not found in " + options.inputDir
        print "exiting..."
        sys.exit()

    if(os.path.isfile(inputDataFile) == False):
        print "ERROR: file " + inputDataFile + " not found in " + options.inputDir
        print "exiting..."
        sys.exit()

    #---Find xsection correspondent to the current dataset
    if(os.path.isfile(options.xsection) == False):
        print "ERROR: file " + options.xsection + " not found"
        print "exiting..."
        sys.exit()

    for lin1 in open( options.xsection ):

        lin1 = string.strip(lin1,"\n")

        (dataset , xsection_val) = string.split(lin1)
        #print dataset + " " + xsection_val

        dataset_mod_1 = dataset[1:].replace('/','__')
        #print dataset_mod_1 + " " + xsection_val

        if(dataset_mod_1 == dataset_mod):
            xsectionIsFound = True
            break

    if(xsectionIsFound == False):
        print "ERROR: xsection for dataset" + dataset + " not found in " + options.xsection
        print "exiting..."
        sys.exit()
        
    #this is the current cross section
    #print xsection_val

    #---Read .dat table for current dataset
    data={}
    column=[]
    lineCounter = int(0)
    
    for j,line in enumerate( open( inputDataFile ) ):

        if( re.search("^###", line) ):
            continue

        line = string.strip(line,"\n")
        #print "---> lineCounter: " , lineCounter
        print line
        
        if lineCounter == 0:
            for i,piece in enumerate(line.split()):
                column.append(piece)
        else:
            for i,piece in enumerate(line.split()):
                if i == 0:
                    data[int(piece)] = {}
                    row = int(piece)
                else:
                    data[row][ column[i] ] = piece
                    #print data[row][ column[i] ] 

        lineCounter = lineCounter+1

    # example
    #Ntot = int(data[0]['N'])
    #print Ntot

    #---Calculate weight
    #Ntot = int(data[0]['N'])
    Ntot = float(data[0]['N'])
    if( xsection_val == "-1" ):
        weight = 1.0
        xsection_X_intLumi = Ntot
    else:
        xsection_X_intLumi = float(xsection_val) * float(options.intLumi)
        if( Ntot == 0 ):
            weight = float(0)
        else:
            weight = xsection_X_intLumi / Ntot 
    print "weight: " + str(weight)
    
    #---Combine histograms using PYROOT
    file = TFile(inputRootFile)
    nHistos = int( file.GetListOfKeys().GetEntries() )
    #print "nHistos: " , nHistos, "\n"

    # loop over samples
    for S,sample in enumerate( dictSamples ):
        #print "current sample is : " , sample

        if( n == 0): 
            dictFinalHisto[sample] = {}

        # loop over histograms in rootfile
        for h in range(0, nHistos):
            histoName = file.GetListOfKeys()[h].GetName()
            htemp = file.Get(histoName)

            #
            #temporary
            #
            if "TDir" in htemp.__repr__():
                htemp = file.Get(histoName + "/optimizer")

            #thanks Riccardo
            if(n == 0):
                if "TH2" in htemp.__repr__():
                    dictFinalHisto[sample][h] = TH2F()
                    dictFinalHisto[sample][h].SetName("histo2D__" + sample + "__" + histoName )
                    dictFinalHisto[sample][h].SetBins(htemp.GetNbinsX(), htemp.GetXaxis().GetXmin(), htemp.GetXaxis().GetXmax(),htemp.GetNbinsY(),htemp.GetYaxis().GetBinLowEdge(1),htemp.GetYaxis().GetBinUpEdge(htemp.GetNbinsY()))
                    #continue

                else:
                    dictFinalHisto[sample][h] = TH1F()
                    dictFinalHisto[sample][h].SetName("histo1D__" + sample + "__" + histoName )
                    dictFinalHisto[sample][h].SetBins(htemp.GetNbinsX(), htemp.GetXaxis().GetXmin(), htemp.GetXaxis().GetXmax(),)

            #print "current histo is : " , dictFinalHisto[sample][h].GetName()

            #update histo

            #print "dataset strings in this sample"
            toBeUpdated = False
            for mS, matchString in enumerate (dictSamples[sample]):
                #print matchString
                if( re.search(matchString, dataset_mod) ):
                    #print "toBeUpdated"
                    toBeUpdated = True
                    break
            #print toBeUpdated
            if(toBeUpdated):
                dictFinalHisto[sample][h].Add(htemp, weight)

    #print "--> TEST <--"
    #for S,sample in enumerate( dictSamples ):
        #print "--> current sample: " + sample
        #print dictFinalHisto[sample] 
    
    #---End of the loop over datasets---#

print "\n"

outputTfile = TFile( options.outputDir + "/" + options.analysisCode + "_plots.root","RECREATE")

for sample in ( dictFinalHisto ):
    for h, histo in enumerate ( dictFinalHisto[sample] ):
        print "writing histo: " , dictFinalHisto[sample][histo].GetName()
        dictFinalHisto[sample][histo].Write()

outputTfile.Close()

print "output plots at: " + options.outputDir + "/" + options.analysisCode + "_plots.root"
