#!/usr/bin/env python

#---Import
import sys
import string
from optparse import OptionParser
import os.path
from ROOT import *
import re
import commands

#---Option Parser
#--- TODO: WHY PARSER DOES NOT WORK IN CMSSW ENVIRONMENT? ---#
usage = "usage: %prog [options] \nExample: \n python getMassList.py -i \"/data/santanas/Results/dijets_PhysicsDST/117pb-1_JECL123Res__Fall11MC_JECL123__06_02_2012/finalResults_DATA_*.log\" -m PrintPFDiJetMass -o MassList_DATA.txt"

parser = OptionParser(usage=usage)

parser.add_option("-i", "--inputList", dest="inputList",
                  help="list of all da files",
                  metavar="LIST")

parser.add_option("-m", "--matchString", dest="matchString",
                  help="the matching string",
                  metavar="MATCH")

parser.add_option("-o", "--outputFile", dest="outputFile",
                  help="the outputfile",
                  metavar="OUTDIR")

(options, args) = parser.parse_args()

if len(sys.argv)<6:
    print usage
    sys.exit()


#############################################################

file_string = options.inputList
outputDataFile = options.outputFile
outputMassFile = open(outputDataFile,'w')   

status, output = commands.getstatusoutput( "grep " + options.matchString + " " + file_string )
list_files = string.split( output, "\n")
print "Selected Events : " + str(len(list_files))
for i,line in enumerate(list_files):
    #print line
    massValue = string.split( line, " ")[1]
    #print massValue
    print >> outputMassFile, massValue
#print list_files

