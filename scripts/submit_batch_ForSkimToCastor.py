#! /usr/bin/env python
import os
import sys
import string
import re
from optparse import OptionParser

usage = "usage: %prog [options] \nExample: ./scripts/submit_batch.py -i HeepStudies_v1/MinimumBias__Commissioning10-SD_EG-v9__RECO_short.txt -c HeepStudies_v1/cutFile_HeepElectronStudiesV1.txt -o TestFrancesco/Mydataset -t rootTupleTree/tree -n 2 -q 1nh -d /castor/cern.ch/user/s/santanas/LQ/Ntuples"

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
                  help="max number of jobs, limited automatically to the number of files in inputlist",
                  metavar="IJOBMAX")

parser.add_option("-q", "--queue", dest="queue",
                  help="name of the queue (choose among cmst3 8nm 1nh 8nh 1nd 1nw)",
                  metavar="QUEUE")

parser.add_option("-d", "--castorDir", dest="castorDir",
                  help="full path of the castor directory for the skim output",
                  metavar="CASTORDIR")


(options, args) = parser.parse_args()

if len(sys.argv)<14:
    print usage
    sys.exit()

################################################
pwd = os.getcwd()

outputmain = options.output.rstrip("/")
if not re.search("^/", outputmain):
    outputmain = pwd + "/" + outputmain

inputlist = options.inputlist
if not re.search("^/", inputlist):
    inputlist = pwd + "/" + inputlist

cutfile = options.cutfile
if not re.search("^/", cutfile):
    cutfile = pwd + "/" + cutfile

outputcastordir = options.castorDir    
################################################
# write on local disk
################################################
os.system("mkdir -p "+outputmain)
os.system("mkdir -p "+outputmain+"/log/")
os.system("mkdir -p "+outputmain+"/input/")
os.system("mkdir -p "+outputmain+"/src/")
os.system("mkdir -p "+outputmain+"/output/")
#os.system("mkdir -p "+outputmain+"/skim/")
################################################
# create castor dir
################################################
os.system("rfmkdir -p "+outputcastordir)
#################################################
# output prefix
outputPrefix = string.split(outputmain,"/")[-1]
#################################################
# dataset
dataset = string.split(outputPrefix,"___")[-1]
#################################################
numfiles = len(file(inputlist).readlines())
ijobmax=int(options.ijobmax)
if ijobmax > numfiles:
    ijobmax=numfiles
filesperjob = int(numfiles/ijobmax)
if numfiles%ijobmax!=0:
    filesperjob = filesperjob+1
    ijobmax = int(numfiles/filesperjob)
    if numfiles%filesperjob!=0:
        ijobmax = ijobmax+1
#################################################
input = open(inputlist)
#################################################
for ijob in range(ijobmax):
    # prepare the list file
    inputfilename = outputmain+"/input/input_"+str(ijob)+".list"
    inputfile = open(inputfilename,"w")
    for i in range(filesperjob):
        line = input.readline()
        if line != "":
            inputfile.write(line)
        continue
    inputfile.close()

    # prepare the script to run
    outputname = outputmain+"/src/submit_"+str(ijob)+".src"
    outputfile = open(outputname,"w")
    outputfile.write("#!/bin/bash\n")
    outputfile.write("cd "+pwd+"\n")
    if "amd64" in os.getenv ("SCRAM_ARCH"): outputfile.write(". /afs/cern.ch/sw/lcg/external/gcc/4.3.2/x86_64-slc5/setup.sh\n")
    outputfile.write("./main "+inputfilename+" "+cutfile+" "+options.treeName+" "+"$WORKDIR/"+outputPrefix+"_"+str(ijob)+" "+"$WORKDIR/"+outputPrefix+"_"+str(ijob)+"\n")
    outputfile.write("mv -v "+"$WORKDIR/"+outputPrefix+"_"+str(ijob)+".root"+" "+outputmain+"/output/"+"\n")
    outputfile.write("mv -v "+"$WORKDIR/"+outputPrefix+"_"+str(ijob)+".dat"+" "+outputmain+"/output/"+"\n")
    outputfile.write("rfcp "+"$WORKDIR/"+outputPrefix+"_"+str(ijob)+"_reduced_skim.root"+" "+outputcastordir+"/"+dataset+"_"+str(ijob)+".root\n")
    ### outputfile.write("rfcp "+"$WORKDIR/"+outputPrefix+"_"+str(ijob)+"_skim.root"+" "+outputcastordir+"/"+dataset+"_"+str(ijob)+".root\n")
    #    outputfile.write("./main "+inputfilename+" "+cutfile+" "+options.treeName+" "+outputmain+"/output/"+outputPrefix+"_"+str(ijob)+" "+outputmain+"/output/"+outputPrefix+"_"+str(ijob)+"\n")
    #    outputfile.write("mv -v "+outputmain+"/output/"+outputPrefix+"_"+str(ijob)+"_skim.root"+" "+outputmain+"/skim/"+dataset+"_"+str(ijob)+".root\n")
    outputfile.close
    print    ("bsub -q "+options.queue+" -o "+outputmain+"/log/"+outputPrefix+"_"+str(ijob)+".log source "+outputname)
    os.system("bsub -q "+options.queue+" -o "+outputmain+"/log/"+outputPrefix+"_"+str(ijob)+".log source "+outputname)
