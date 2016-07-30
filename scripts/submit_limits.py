#! /usr/bin/env python
import os
import sys
import string
import re
from optparse import OptionParser
import stat

usage = "usage: %prog [options] \nExample: ./scripts/submit_batch.py -i HeepStudies_v1/MinimumBias__Commissioning10-SD_EG-v9__RECO_short.txt -c HeepStudies_v1/cutFile_HeepElectronStudiesV1.txt -o TestFrancesco/Mydataset -t rootTupleTree/tree -n 2 -q 1nh"

parser = OptionParser(usage=usage)

#parser.add_option("-i", "--inputlist", dest="inputlist",
#                  help="list of all datasets to be used",
#                  metavar="LIST")
#
#parser.add_option("-c", "--cutfile", dest="cutfile",
#                  help="name of the cut file",
#                  metavar="CUTFILE")
#
#parser.add_option("-o", "--output", dest="output",
#                  help="the directory OUTDIR contains the output of the program",
#                  metavar="OUTDIR")
#
#parser.add_option("-t", "--treeName", dest="treeName",
#                  help="name of the root tree",
#                  metavar="TREENAME")
#
#parser.add_option("-n", "--ijobmax", dest="ijobmax",
#                  help="max number of jobs, limited automatically to the number of files in inputlist",
#                  metavar="IJOBMAX")
#
#parser.add_option("-q", "--queue", dest="queue",
#                  help="name of the queue (choose among cmst3 8nm 1nh 8nh 1nd 1nw)",
#                  metavar="QUEUE")
#
#
#(options, args) = parser.parse_args()
#
#if len(sys.argv)<12:
#    print usage
#    sys.exit()
#
#################################################
pwd = os.getcwd()
#
#outputmain = options.output.rstrip("/")
#if not re.search("^/", outputmain):
#    outputmain = pwd + "/" + outputmain
#
#inputlist = options.inputlist
#if not re.search("^/", inputlist):
#    inputlist = pwd + "/" + inputlist
#
#cutfile = options.cutfile
#if not re.search("^/", cutfile):
#    cutfile = pwd + "/" + cutfile

outputmain = pwd+'/'+'jul29_freqLimit_test'
datacard = ''
#massPoints = [i*50 for i in range(4,31)]
massPoints = [600,750,800]
#queue = '8nh'
queue = '1nd'
exe = 'RunStatsBasicCLs2.py'

################################################
# write on local disk
################################################
os.system("mkdir -p "+outputmain)
os.system("mkdir -p "+outputmain+"/log/")
os.system("mkdir -p "+outputmain+"/input/")
os.system("mkdir -p "+outputmain+"/src/")
os.system("mkdir -p "+outputmain+"/output/")
os.system("mkdir -p "+outputmain+"/skim/")
#################################################
# output prefix
outputPrefix = string.split(outputmain,"/")[-1]
# check if we are in the right dir
filesThisDir = [f for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]
if not exe in filesThisDir:
    print 'ERROR: could not find',exe,'in current directory. Please executive in directory where',exe,'is present'
    exit(-1)

for massPoint in massPoints:

    # prepare the script to run
    outputname = outputmain+"/src/submit_"+str(massPoint)+".sh"
    outputfile = open(outputname,"w")
    outputfile.write("#!/bin/bash\n")
    outputfile.write("cd "+pwd+"\n")
    #if "amd64" in os.getenv ("SCRAM_ARCH"): outputfile.write(". /afs/cern.ch/sw/lcg/external/gcc/4.3.2/x86_64-slc5/setup.sh\n")
    outputfile.write("source /afs/cern.ch/cms/cmsset_default.sh\n")
    outputfile.write("eval `scramv1 runtime -sh`\n")
    #outputfile.write("./main "+inputfilename+" "+cutfile+" "+options.treeName+" "+outputmain+"/output/"+outputPrefix+"_"+str(ijob)+" "+outputmain+"/output/"+outputPrefix+"_"+str(ijob)+"\n")
    #outputfile.write("mv -v "+outputmain+"/output/"+outputPrefix+"_"+str(ijob)+"_skim.root"+" "+outputmain+"/skim/"+dataset+"_"+str(ijob)+".root\n")
    outputfile.write("python "+exe+" --do_BetaOne -c LimitTest --doFullHybridCLs --Asymptotic_Only --fullHybridMass "+str(massPoint))
    outputfile.close
    # make it executable
    st = os.stat(outputname)
    os.chmod(outputname, st.st_mode | stat.S_IEXEC)
    #print    ("bsub -q "+options.queue+" -o "+outputmain+"/log/"+outputPrefix+"_"+str(ijob)+".log source "+outputname)
    #os.system("bsub -q "+options.queue+" -o "+outputmain+"/log/"+outputPrefix+"_"+str(ijob)+".log source "+outputname)
    print    ("bsub -q "+queue+" -o "+outputmain+"/log/"+outputPrefix+"_"+str(massPoint)+".log "+outputname)
    os.system("bsub -q "+queue+" -o "+outputmain+"/log/"+outputPrefix+"_"+str(massPoint)+".log "+outputname)


