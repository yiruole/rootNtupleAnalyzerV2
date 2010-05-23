#! /usr/bin/env python
import os
import sys
import string
from optparse import OptionParser
import os.path

usage = "usage: %prog [options] \nExample: ./scripts/submit_batch.py -i HeepStudies_v1/MinimumBias__Commissioning10-SD_EG-v9__RECO_short.txt -c HeepStudies_v1/cutFile_HeepElectronStudiesV1.txt -o TestFrancesco/Mydataset -t rootTupleTree/tree -n 2 -q 1nh"

parser = OptionParser(usage=usage)

parser.add_option("-i", "--inputlist", dest="inputlist",
                  help="list of all datasets to be used",
                  metavar="LIST")

parser.add_option("-c", "--cutfile", dest="cutfile",
                  help="name of the cut file",
                  metavar="CUTFILE")

parser.add_option("-o", "--output", dest="output",
                  help="the directory OUTDIR contains the output of the program",
                  metavar="OUTDIR")

parser.add_option("-t", "--treeName", dest="treeName",
                  help="name of the root tree",
                  metavar="TREENAME")

parser.add_option("-n", "--ijobmax", dest="ijobmax",
                  help="max number of jobs",
                  metavar="IJOBMAX")

parser.add_option("-q", "--queue", dest="queue",
                  help="name of the queue (choose among cmst3 8nm 1nh 8nh 1nd 1nw)",
                  metavar="QUEUE")


(options, args) = parser.parse_args()

if len(sys.argv)<12:
    print usage
    sys.exit()


################################################
# to write on local disks
################################################
outputmain = options.output

os.system("mkdir -p "+options.output)
os.system("mkdir -p "+options.output+"/log/")
os.system("mkdir -p "+options.output+"/input/")
os.system("mkdir -p "+options.output+"/src/")
outputroot = outputmain+"/output/"
os.system("mkdir -p "+outputroot)

## output Prefix
outputPrefix = string.split(options.output,"/")[-1]
#print outputPrefix
#sys.exit()

################################################
#look for the current directory
################################################
os.system("\\rm tmp.log")
os.system("echo $PWD > tmp.log")
tmp = open("tmp.log")
pwd = tmp.readline()
tmp.close()
os.system("\\rm tmp.log")
#################################################
numfiles = reduce(lambda x,y: x+1, file(options.inputlist).xreadlines(), 0)
filesperjob = numfiles/int(options.ijobmax)
filesperjob = filesperjob
extrafiles  = numfiles%int(options.ijobmax)
input = open(options.inputlist)
######################################
for ijob in range(int(options.ijobmax)):
    # prepare the list file
    inputfilename = options.output+"/input/input_"+str(ijob)+".list"
    inputfile = open(inputfilename,'w')
    # if it is a normal job get filesperjob lines
    if ijob != (int(options.ijobmax)-1):
        for line in range(filesperjob):
            ntpfile = input.readline()
            if ntpfile != '':
                inputfile.write(ntpfile)
            continue
    else:
        # if it is the last job get ALL remaining lines
        ntpfile = input.readline()
        while ntpfile != '':
            inputfile.write(ntpfile)
            ntpfile = input.readline()
            continue
    inputfile.close()

    # prepare the script to run
    outputname = options.output+"/src/submit_"+str(ijob)+".src"
    outputfile = open(outputname,'w')
    outputfile.write('#!/bin/bash\n')
    outputfile.write('cd '+pwd)
    outputfile.write('./main '+inputfilename+" "+options.cutfile+" "+ options.treeName + " "+ outputroot+outputPrefix+"_"+str(ijob)+" "+outputroot+outputPrefix+"_"+str(ijob)+"\n") 
    outputfile.close
    os.system("echo bsub -q "+options.queue+" -o "+options.output+"/log/"+outputPrefix+"_"+str(ijob)+".log source "+pwd[:-1]+"/"+outputname)
    os.system("bsub -q "+options.queue+" -o "+options.output+"/log/"+outputPrefix+"_"+str(ijob)+".log source "+pwd[:-1]+"/"+outputname)
    ijob = ijob+1
    continue
