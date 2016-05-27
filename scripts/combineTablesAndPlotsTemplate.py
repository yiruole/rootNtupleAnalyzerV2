#!/usr/bin/env python

#---Import
import sys
import string
from optparse import OptionParser
import os.path
from ROOT import *
import re
import math

from combineCommon import *

doProfiling=False
# for profiling
if doProfiling:
  from cProfile import Profile
  from pstats import Stats
  prof = Profile()
  prof.disable()  # i.e. don't time imports
  import time
  prof.enable()  # profiling back on
# for profiling


#---Run
# Turn off warning messages
gROOT.ProcessLine("gErrorIgnoreLevel=2001;")
#---Option Parser
#--- TODO: WHY PARSER DOES NOT WORK IN CMSSW ENVIRONMENT? ---#
usage = "usage: %prog [options] \nExample: \n./combineTablesTemplate.py -i /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config/inputListAllCurrent.txt -c analysisClass_genStudies -d /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/data/output -l 100 -x /home/santanas/Data/Leptoquarks/RootNtuples/V00-00-06_2008121_163513/xsection_pb_default.txt -o /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/data/output -s /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config/sampleListForMerging.txt"

parser = OptionParser(usage=usage)

parser.add_option("-i", "--inputList", dest="inputList",
                  help="list of all datasets to be used (full path required)",
                  metavar="LIST")

parser.add_option("-c", "--code", dest="analysisCode",
                  help="name of the CODE.C code used to generate the rootfiles (which is the beginning of the root file names before ___)",
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

parser.add_option("-t", "--tablesOnly", action="store_true",dest="tablesOnly",default=False,
                  help="only combine tables, do not do plots",
                  metavar="TABLESONLY")

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

#---Check if xsection file exist
if(os.path.isfile(options.xsection) == False):
    print "ERROR: file " + options.xsection + " not found"
    print "exiting..."
    sys.exit()

print 'Launched like:'
for arg in sys.argv:
  print '\t'+arg

xsectionDict = ParseXSectionFile(options.xsection)
#print 'Dataset      XSec'
#for key,value in xsectionDict.iteritems():
#  print key,'  ',value

dictSamples = GetSamplesToCombineDict(options.sampleListForMerging)
dictSamplesPiecesAdded = {}
for key in dictSamples.iterkeys():
  dictSamplesPiecesAdded[key] = []

#--- Declare efficiency tables
dictFinalTables = {}
#--- Declare histograms
dictFinalHisto = {}

# check to make sure we have xsections for all samples
for lin in open( options.inputList ):
    lin = string.strip(lin,"\n")
    if lin.startswith('#'):
      continue
    dataset_fromInputList = string.split( string.split(lin, "/" )[-1], ".")[0]
    ### XXX FIXME special hacks for datasets
    #if dataset_fromInputList.endswith('_reduced_skim'):
    #  dataset_fromInputList = dataset_fromInputList[0:dataset_fromInputList.find('_reduced_skim')]
    ###XXX FIXME
    ### special hack for handling repated madgraphMLM samples
    ##if dataset_fromInputList.endswith('_madgraphMLM'):
    ##  dataset_fromInputList = dataset_fromInputList[0:dataset_fromInputList.find('_madgraphMLM')]
    ###XXX FIXME
    ### special hack for handling repated amcatnloFXFX samples
    ##elif dataset_fromInputList.endswith('_amcatnloFXFX'):
    ##  dataset_fromInputList = dataset_fromInputList[0:dataset_fromInputList.find('_amcatnloFXFX')]
    #if dataset_fromInputList.endswith('_pythia8'):
    #  dataset_fromInputList = dataset_fromInputList[0:dataset_fromInputList.find('_pythia8')]
    ##if '__' in dataset_fromInputList:
    ##  dataset_fromInputList = dataset_fromInputList[0:dataset_fromInputList.find('__')]

    #xsection_val = lookupXSection(dataset_fromInputList,xsectionDict)
    xsection_val = lookupXSection(SanitizeDatasetNameFromInputList(dataset_fromInputList),xsectionDict)

#---Loop over datasets in the inputlist
print
for lin in open( options.inputList ):

    lin = string.strip(lin,"\n")
    #print 'lin=',lin
    if lin.startswith('#'):
      continue
    
    dataset_fromInputList = string.split( string.split(lin, "/" )[-1], ".")[0]
    # strip off the slashes and the .txt at the end
    # so this will look like 'TTJets_DiLept_reduced_skim'
    print SanitizeDatasetNameFromInputList(dataset_fromInputList) + " ... ",
    #print SanitizeDatasetNameFromInputList(dataset_fromInputList),dataset_fromInputList,
    sys.stdout.flush()

    inputRootFile = options.inputDir + "/" + options.analysisCode + "___" + dataset_fromInputList + ".root"
    inputDataFile = options.inputDir + "/" + options.analysisCode + "___" + dataset_fromInputList + ".dat"

    #---Check if .root and .dat file exist
    if(os.path.isfile(inputRootFile) == False):
        print "ERROR: file " + inputRootFile + " not found"
        print "exiting..."
        sys.exit()
    #else:
    #  print 'opened file:',inputRootFile


    if(os.path.isfile(inputDataFile) == False):
        print "ERROR: file " + inputDataFile + " not found"
        print "exiting..."
        sys.exit()
    #else:
    #    print 'opened file:',inputDataFile

    #---Find xsection correspondent to the current dataset
    #dataset_fromInputList = SanitizeDatasetNameFromInputList(dataset_fromInputList)
    xsection_val = lookupXSection(SanitizeDatasetNameFromInputList(dataset_fromInputList),xsectionDict)
    #xsection_val = lookupXSection(dataset_fromInputList,xsectionDict)
    #this is the current cross section
    #print dataset_fromInputList,xsection_val

    #---Read .dat table for current dataset
    data={}
    column=[]
    lineCounter = int(0)

    #print 'opening:',inputDataFile
    for j,line in enumerate( open( inputDataFile ) ):

        if( re.search("^###", line) ):
            continue

        line = string.strip(line,"\n")
        #print "---> lineCounter: " , lineCounter
        #print line

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
    Ntot = float(data[0]['N'])
    #print 'Ntot=',Ntot

    #---Calculate weight
    #Ntot = int(data[0]['N'])
    Ntot = float(data[0]['N'])
    #XXX FIXME for amc@NLO need to multiple by sum of weights
    if( xsection_val == "-1" ):
        weight = 1.0
        plotWeight = 1.0
        xsection_X_intLumi = Ntot
    else:
        xsection_X_intLumi = float(xsection_val) * float(options.intLumi)
        if( Ntot == 0 ):
            weight = float(0)
        else:
            weight = xsection_X_intLumi / Ntot 
        #XXX HACKs for AMC@NLO
        if re.search('amcatnlo',dataset_fromInputList,re.IGNORECASE):
          if re.search('dyjetstoll',dataset_fromInputList,re.IGNORECASE):
            weight*=1.49
          elif re.search('wjetstolnu',dataset_fromInputList,re.IGNORECASE):
            weight*=1.46
          elif re.search('ttjets',dataset_fromInputList,re.IGNORECASE):
            weight*=3.02
        plotWeight = weight/1000.0
    print "xsection: " + xsection_val,
    print "weight(x1000): " + str(weight) + " = " + str(xsection_X_intLumi) + "/" + str(Ntot)
    
    #---Create new table using weight
    newtable={}
    
    for j,line in enumerate( data ):
        if(j == 0):
            newtable[int(j)]={'variableName': data[j]['variableName'],
                              'min1': "-",
                              'max1': "-",
                              'min2': "-",
                              'max2': "-",
                              'N': ( Ntot * weight ),
                              'errN': int(0),
                              'Npass': ( Ntot * weight ),
                              'errNpass': int(0),
                              }

        else:
            #print 'data[j]=',data[j]
            N = ( float(data[j]['N']) * weight )
            errN = ( float(data[j-1]["errEffAbs"]) * xsection_X_intLumi )
            #print data[j]['variableName']
            #print "errN: " , errN
            if(str(errN) == "nan"):
                errN = 0
                
                #            if( float(N) > 0 and float(errN) > 0 ):
                #                errRelN = errN / N 
                #            else:
                #                errRelN = float(0)
            
            Npass = ( float(data[j]['Npass']) * weight) 
            errNpass = ( float(data[j]["errEffAbs"]) * xsection_X_intLumi )
            #print "errNPass " , errNpass
            #print ""
            if(str(errNpass) == "nan"):
                errNpass = 0

                #            if( float(Npass) > 0 and float(errNpass) > 0 ):
                #                errRelNpass = errNpass / Npass
                #            else:
                #                errRelNpass = float(0)
            
            newtable[int(j)]={'variableName': data[j]['variableName'],
                              'min1': data[j]['min1'],
                              'max1': data[j]['max1'],
                              'min2': data[j]['min2'],
                              'max2': data[j]['max2'],
                              'N':         N,
                              'errN':      errN,
                              'Npass':     Npass,
                              'errNpass':  errNpass,
                              }

            #print newtable

    if not options.tablesOnly:
      #---Combine histograms using PYROOT
      file = TFile(inputRootFile)
      nHistos = int( file.GetListOfKeys().GetEntries() )
      #print "nHistos: " , nHistos, "\n"
      #print 'list of keys in this rootfile:',file.GetListOfKeys()


    #---Combine tables and plots from different datasets
    
    # loop over samples defined in sampleListForMerging
    for sample,pieceList in dictSamples.iteritems():
        #print "look at sample named:",sample

        # init if needed
        if not sample in dictFinalTables:
            dictFinalTables[sample] = {}
        if not sample in dictFinalHisto:
            dictFinalHisto[sample] = {}

        toBeUpdated = False
        #matchingPiece = dataset_fromInputList
        matchingPiece = SanitizeDatasetNameFromInputList(dataset_fromInputList)
        if matchingPiece in pieceList:
            toBeUpdated = True
        # if no match, maybe the dataset in the input list ends with "_reduced_skim", so try to match without that
        elif matchingPiece.endswith('_reduced_skim'):
            matchingPieceNoRSK = matchingPiece[0:matchingPiece.find('_reduced_skim')]
            if matchingPieceNoRSK in pieceList:
                toBeUpdated = True
                matchingPiece = matchingPieceNoRSK
        if toBeUpdated:
            UpdateTable(newtable,dictFinalTables[sample])
            dictSamplesPiecesAdded[sample].append(matchingPiece)

        if not options.tablesOnly:
          # loop over histograms in rootfile
          for h in range(0, nHistos):
              histoName = file.GetListOfKeys()[h].GetName()
              htemp = file.Get(histoName)

              #
              #temporary
              #
              if "TDir" in htemp.__repr__():
                  #print 'Getting optimizer hist!'
                  htemp = file.Get(histoName + "/optimizer")
                  #print 'entries:',htemp.GetEntries()

              #thanks Riccardo
              # init histo if needed
              if not h in dictFinalHisto[sample]:
                  if "TH2" in htemp.__repr__():
                      dictFinalHisto[sample][h] = TH2F()
                      dictFinalHisto[sample][h].SetName("histo2D__" + sample + "__" + histoName )
                      dictFinalHisto[sample][h].SetBins(htemp.GetNbinsX(), htemp.GetXaxis().GetXmin(), htemp.GetXaxis().GetXmax(),htemp.GetNbinsY(),htemp.GetYaxis().GetBinLowEdge(1),htemp.GetYaxis().GetBinUpEdge(htemp.GetNbinsY()))
                      #continue

                  else:
                      dictFinalHisto[sample][h] = TH1F()
                      dictFinalHisto[sample][h].SetName("histo1D__" + sample + "__" + histoName )
                      dictFinalHisto[sample][h].SetBins(htemp.GetNbinsX(), htemp.GetXaxis().GetXmin(), htemp.GetXaxis().GetXmax(),)
              if toBeUpdated:
                  if not htemp:
                    print 'failed to get histo named:',histoName,'from file:',file.GetName()
                  if not dictFinalHisto[sample][h].Add(htemp, plotWeight):
                    print 'ERROR: Failed adding',htemp.GetName(),'to',dictFinalHisto[sample][h].GetName()

    #---End of the loop over datasets---#

# validation of combining pieces
for sample,pieceList in dictSamples.iteritems():
  piecesAdded = dictSamplesPiecesAdded[sample]
  if set(piecesAdded) != set(pieceList):
    print
    #print 'ERROR: for sample',sample,'the pieces added were:'
    #print sorted(piecesAdded)
    print 'ERROR: for sample',sample+', the following pieces requested in sampleListForMerging were not added:'
    print list(set(piecesAdded).symmetric_difference(set(pieceList)))
    print '\twhile the pieces indicated as part of the sample were:'
    print sorted(pieceList)
    print '\tand the pieces added were:'
    print sorted(piecesAdded)
    print '\tRefusing to proceed.'
    exit(-1)

if not os.path.isdir(options.outputDir):
  os.makedirs(options.outputDir)

outputTableFile = open(options.outputDir + "/" + options.analysisCode + "_tables.dat",'w')

for S,sample in enumerate( dictSamples ):
    #print "current sample is: ", sample
    #print dictFinalTables[sample]

    #---Create final tables 
    CalculateEfficiency(dictFinalTables[sample])
    #--- Write tables
    WriteTable(dictFinalTables[sample], sample, outputTableFile)

outputTableFile.close

# write histos
if not options.tablesOnly:
  outputTfile = TFile( options.outputDir + "/" + options.analysisCode + "_plots.root","RECREATE")
  
  # get total hists
  nHistos = sum(len(x) for x in dictFinalHisto.itervalues())
  maxSteps = 50
  if nHistos < maxSteps:
    steps = nHistos
  else:
    steps = maxSteps
  
  print 'Writing histos:'
  progressString = '0% ['+' '*steps+'] 100%'
  print progressString,
  print '\b'*(len(progressString)-3),
  sys.stdout.flush()
  
  nForProgress = 0
  for sample in dictFinalHisto:
      for n, histo in enumerate ( dictFinalHisto[sample] ):
          if (nForProgress % (nHistos/steps))==0:
              print '\b.',
              sys.stdout.flush()
          dictFinalHisto[sample][histo].Write()
          nForProgress+=1
  
  print '\b] 100%'
  
  outputTfile.Close()
  print "output plots at: " + options.outputDir + "/" + options.analysisCode + "_plots.root"

print "output tables at: ", options.outputDir + "/" + options.analysisCode + "_tables.dat"

#---TODO: CREATE LATEX TABLE (PYTEX?) ---#

## for profiling
if doProfiling:
  prof.disable()  # don't profile the generation of stats
  prof.dump_stats('mystats.stats')
  with open('mystats_output.txt', 'wt') as output:
    stats = Stats('mystats.stats', stream=output)
    stats.sort_stats('cumulative', 'time')
    stats.print_stats()

