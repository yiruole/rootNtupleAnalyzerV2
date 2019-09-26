#! /usr/bin/env python

import os
import sys
import string
import re
from optparse import OptionParser


def PrepareJobScript(outputname):
    with open(outputname,"w") as outputfile:
        outputfile.write("#!/bin/bash\n")
        # hardcoded root is a bit nasty FIXME
        outputfile.write('source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh\n')
        # ROOT likes HOME set
        outputfile.write('[ -z "$HOME" ] && export HOME='+os.getenv('HOME')+'\n')
        inputList = inputfilename.split('/')[-1]
        outputfile.write('./'+execName+' '+inputList+" "+cutfile.split('/')[-1]+" "+options.treeName+" "+outputPrefix+"_"+str(ijob)+" "+outputPrefix+"_"+str(ijob)+"\n")
        outputfile.write("mv -v "+outputPrefix+"_"+str(ijob)+".root"+" "+outputmain+"/output/"+"\n")
        outputfile.write("mv -v "+outputPrefix+"_"+str(ijob)+".dat"+" "+outputmain+"/output/"+"\n")
        if options.reducedSkim:
            outputfile.write("xrdcp -fs "+"\""+outputPrefix+"_"+str(ijob)+"_reduced_skim.root\" \""+options.eosHost+outputeosdir+"/"+dataset+"_"+str(ijob)+"_rsk.root\"\n")
        else:
            # flat skim
            outputfile.write("xrdcp -fs "+"\""+outputPrefix+"_"+str(ijob)+"_skim.root\" \""+options.eosHost+outputeosdir+"/"+dataset+"_"+str(ijob)+"_sk.root\"\n")


def WriteSubmitFile(condorFileName):
    with open(condorFileName,'w') as condorFile:
        condorFile.write('executable  = '+outputmain+'/src/submit_$(Process).sh\n')
        condorFile.write('N = '+str(ijobmax)+'\n')
        condorFile.write('output      = '+outputmain+'/output/$(Process).out\n')
        condorFile.write('error       = '+outputmain+'/error/$(Process).err\n')
        condorFile.write('log         = '+outputmain+'/log/$(Process).log\n')
        #http://batchdocs.web.cern.ch/batchdocs/local/submit.html
        condorFile.write('+JobFlavour = "'+options.queue+'"\n')
        # require CentOS7
        condorFile.write('requirements = (OpSysAndVer =?= "CentOS7")\n')
        # make sure the job finishes with exit code 0
        #condorFile.write('on_exit_remove = (ExitBySignal == False) && (ExitCode == 0)\n')
        condorFile.write('max_retries = 3\n')
        condorFile.write('should_transfer_files = YES\n')
        condorFile.write('transfer_output_files = ""\n')
        #condorFile.write('stream_output = True\n')
        #condorFile.write('stream_error = True\n')
        exePath = os.path.dirname(os.path.abspath(options.executable))
        condorFile.write('transfer_input_files = '+cutfile+','+options.executable+','+outputmain+'/input/input_$(Process).list,'+options.jsonFileName+'\n')
        condorFile.write('queue $(N)\n')


usage = "usage: %prog [options] \nExample: ./scripts/submit_batch.py -i HeepStudies_v1/MinimumBias__Commissioning10-SD_EG-v9__RECO_short.txt -c HeepStudies_v1/cutFile_HeepElectronStudiesV1.txt -o TestFrancesco/Mydataset -t rootTupleTree/tree -n 2 -q 1nh -d /eos/cms/store/user/eberry/"

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

#http://batchdocs.web.cern.ch/batchdocs/local/submit.html
parser.add_option("-q", "--queue", dest="queue",
                  help="name of the queue",
                  metavar="QUEUE")

parser.add_option("-d", "--eosDir", dest="eosDir",
                  help="full path of the eos directory for the skim output",
                  metavar="EOSDIR")

parser.add_option("-m", "--eosHost", dest="eosHost",
                  help="root:// MGM URL for the eos host for the skim output",
                  metavar="EOSHOST", default="root://eoscms.cern.ch/")

parser.add_option("-j", "--json", dest="jsonFileName",
                  help="json filename",
                  metavar="JSONFILE", default="")

parser.add_option("-e", "--exe", dest="executable",
                  help="executable",
                  metavar="EXECUTABLE", default="")

parser.add_option("-r", "--reducedSkim", dest="reducedSkim",
                  help="is this a reduced skim?",
                  metavar="REDUCEDSKIM",default=False,action="store_true")



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

execName = options.executable.split('/')[-1]
################################################
# write on local disk
################################################
os.system("mkdir -p "+outputmain)
os.system("mkdir -p "+outputmain+"/log/")
os.system("mkdir -p "+outputmain+"/error/")
os.system("mkdir -p "+outputmain+"/input/")
os.system("mkdir -p "+outputmain+"/src/")
os.system("mkdir -p "+outputmain+"/output/")
#os.system("mkdir -p "+outputmain+"/skim/")
#################################################
# output prefix
outputPrefix = string.split(outputmain,"/")[-1]
#################################################
# dataset
dataset = string.split(outputPrefix,"___")[-1]
################################################
# create eos dir
################################################
outputeosdir = options.eosDir    
outputeosdir = outputeosdir.rstrip('/') + '/' + dataset
os.system("/usr/bin/eos mkdir -p "+outputeosdir)
################################################
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

    # prepare the exec script
    outputname = outputmain+"/src/submit_"+str(ijob)+".sh"
    PrepareJobScript(outputname)

input.close()

# write condor submit file
condorFileName = outputmain+'/condorSubmit.sub'
WriteSubmitFile(condorFileName)

failedToSub = False
print 'submit jobs for',options.output.rstrip("/")
#FIXME don't cd and use absolute paths in the condor submission instead
oldDir = os.getcwd()
os.chdir(outputmain)
#os.system('condor_submit '+condorFileName)
exitCode = os.WEXITSTATUS(os.system('condor_submit '+condorFileName))
#print 'from condor_submit '+condorFileName+',got exit code='+str(exitCode)
if exitCode != 0:
    print '\exited with '+str(exitCode)+'; try to resubmit'
    exitCode = os.WEXITSTATUS(os.system('condor_submit '+condorFileName))
    if exitCode != 0:
        failedToSub = True
os.chdir(oldDir)
if failedToSub:
    exit(-1)

