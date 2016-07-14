#!/usr/bin/env python

from optparse import OptionParser
import os,sys, errno, time

try:
  from WMCore.DataStructs.LumiList import LumiList
except ImportError:
  print
  print 'ERROR: Could not load WMCore.DataStructs.LumiList.  Please source the crab3 setup:'
  print 'source /cvmfs/cms.cern.ch/crab3/crab.sh'
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


# Union
originalLumiList1 = LumiList(filename='runData2015D_newOct30Lumis_singleElectron/v1-4-0_2015Nov03_120403/crab_SingleElectron__Run2015D-PromptReco-v4/results/lumiSummary.json')
originalLumiList2 = LumiList(filename='runData2015D_singleElectron/v1-4-0_2015Oct25_093223/crab_SingleElectron__Run2015D-05Oct2015-v1/results/lumiSummary.json')
originalLumiList3 = LumiList(filename='runData2015D_singleElectron/v1-4-0_2015Oct25_093223/crab_SingleElectron__Run2015D-PromptReco-v4/results/lumiSummary.json')
unionLumiList = originalLumiList1 | originalLumiList2 | originalLumiList3
#newLumiList.writeJSON('my_lumi_mask.json')

## Difference
##originalLumiList1 = LumiList(filename='my_lumi_mask.json')
## 2.11/fb
#goldenJsonLumiList = LumiList(filename='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON.txt')
#nov17LumiList = goldenJsonLumiList - unionLumiList
#nov17LumiList.writeJSON('newLumisNov17_lumi_mask.json')

# new Nov17 lumis
originalLumiList4 = LumiList(filename='runData2015D_newNov13Lumis_singleElectron/v1-4-0_2015Nov17_105129/crab_SingleElectron__Run2015D-PromptReco-v4/results/lumiSummary.json')
unionLumiList = originalLumiList1 | originalLumiList2 | originalLumiList3 | originalLumiList4
unionLumiList.writeJSON('newestLumisProcessed.json')
