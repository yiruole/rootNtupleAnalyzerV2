#!/usr/bin/env python

from optparse import OptionParser
import os,sys, errno, time

try:
  from WMCore.DataStructs.LumiList import LumiList
except ImportError:
  print
  print 'ERROR: Could not load WMCore.DataStructs.LumiList.  Please source the crab3 setup:'
  print 'source /cvmfs/cms.cern.ch/crab3/crab_light.sh'
  exit(-1)


##--------------------------------------------------------------------------------
## Parse options
##--------------------------------------------------------------------------------
#
#usage = "usage: %prog [options] \nExample: python ./scripts/lumiMaskOps.py <options>"
#
#parser = OptionParser(usage=usage)
#
#parser.add_option("-i", "--inputlist", dest="inputlist",
#                  help="list of all lumi mask jsons to be used",
#                  metavar="LIST")
#
#parser.add_option("-o", "--output", dest="outputDir",
#                  help="the directory OUTDIR contains the output of the program",
#                  metavar="OUTDIR")
#
#parser.add_option("-n", "--treeName", dest="treeName",
#                  help="name of the root tree; defaults to rootTupleTree/tree",
#                  metavar="TREENAME")
#
#parser.add_option("-c", "--cutfile", dest="cutfile",
#                  help="name of the cut file",
#                  metavar="CUTFILE")
#
#
#(options, args) = parser.parse_args()

# first add up the passed JSONs for the processed lumis
# for now, we simply pass a list of the processed lumi JSONs on the command line
lumiLists = []
#print sys.argv
for i,json in enumerate(sys.argv):
  if i==0:
    # this is the name of this script
    continue
  print 'INFO: Add lumi json:',json,'to unionLumiList'
  lumiLists.append(LumiList(filename=json))

# Union
unionLumiJSONFilename = 'calcDataPileup_allProcessedLumis.json'
unionLumiList = LumiList()
for ll in lumiLists:
  unionLumiList = unionLumiList | ll
unionLumiList.writeJSON(unionLumiJSONFilename)
print
print 'INFO: unionLumiList saved in:',unionLumiJSONFilename

## Difference
#nov17LumiList = goldenJsonLumiList - unionLumiList


# generate the pileup files
processedLumis=unionLumiJSONFilename
pileupJSON='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/PileUp/pileup_latest.txt'
minBiasXsec=69000
minBiasXsecUncert = 0.05 #5%
pileupHistoRootFile='Pileup_SingleElectron__Run2015D_all_XXX.root'

# if minBiasXsecUncert < 0, just do central xsec pileup file only
if minBiasXsecUncert > 0:
  minBiasXsecs = [minBiasXsec,(1+minBiasXsecUncert)*minBiasXsec,(1-minBiasXsecUncert)*minBiasXsec]
  histoFileMarker = ['central','up','down']
else:
  minBiasXsecs = [minBiasXsec]
  histoFileMarker = ['central']

for i,xsec in enumerate(minBiasXsecs):
  command='pileupCalc.py -i '+unionLumiJSONFilename
  command+=' --inputLumiJSON '+pileupJSON
  command+=' --calcMode true'
  command+=' --minBiasXsec '+str(xsec)
  command+=' --maxPileupBin 80 --numPileupBins 80'
  command+=' '+pileupHistoRootFile.replace('XXX',histoFileMarker[i])
  print 'INFO: run command:'
  print
  print '\t'+command
  os.system(command)
