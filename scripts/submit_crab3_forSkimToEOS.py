#!/usr/bin/env python

import os
import sys
import string
import re
from optparse import OptionParser
import shutil
try:
  from CRABClient.UserUtilities import config, getUsernameFromSiteDB
except ImportError:
  print
  print 'ERROR: Could not load CRABClient.UserUtilities.  Please source the crab3 setup:'
  print 'source /cvmfs/cms.cern.ch/crab3/crab.sh'
  exit(-1)

from CRABAPI.RawCommand import crabCommand
from httplib import HTTPException


def crabSubmit(config,dryRun=False):
    try:
      if dryRun:
        print 'doing crab3 dryrun'
        crabCommand('submit','dryrun',config = config)
      else:
        crabCommand('submit',config = config)
    except HTTPException, hte:
      print '-----> there was a problem. see below.'
      print hte.headers
      print 'quit here'
      exit(-1)
    
def validateOptions(options):
  error = ''
  if options.inputlist is None:
    error = 'no input list found'
  elif options.cutfile is None:
    error = 'no cutfile found'
  elif options.output is None:
    error = 'no output directory found'

  if len(error) > 0:
    print
    print 'ERROR with specified options:',
    print error
    parser.print_help()
    exit(-1)


usage = "usage: %prog [options] \nExample: ./scripts/submit_crab3_forSkimToEOS.py -i HeepStudies_v1/MinimumBias__Commissioning10-SD_EG-v9__RECO_short.txt -c HeepStudies_v1/cutFile_HeepElectronStudiesV1.txt -o TestFrancesco/Mydataset -d /store/user/eberry/"

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
                  help="name of the root tree; defaults to rootTupleTree/tree",
                  metavar="TREENAME")

# splitting handled by crab3
#parser.add_option("-n", "--ijobmax", dest="ijobmax",
#                  help="max number of jobs, limited automatically to the number of files in inputlist",
#                  metavar="IJOBMAX")

parser.add_option("-d", "--eosDir", dest="eosDir",
                  help="eos directory for the output; defaults to /store/group/phys_exotica/leptonsPlusJets/RootNtuple_skim/RunII/USERNAME/",
                  metavar="EOSDIR")

# FIXME SIC: this doesn't work when using the API?
parser.add_option("-r", "--dryrun", dest="dryRun",
                  help="dry run crab instead of full submit",
                  metavar="DRYRUN",default=False,action="store_true")

(options, args) = parser.parse_args()

validateOptions(options)

# default values
if options.treeName is None:
  options.treeName = 'rootTupleTree/tree'

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

outputLFN = None
if options.eosDir is not None:
  outputeosdir = options.eosDir    
  if outputeosdir.startswith('/eos/cms'):
    outputLFN = outputeosdir.split('/eos/cms')[-1]
  else:
    outputLFN = outputeosdir

#################################################
## make dirs on local disk
#################################################
#os.system("mkdir -p "+outputmain)
#os.system("mkdir -p "+outputmain+"/log/")
#os.system("mkdir -p "+outputmain+"/input/")
os.system("mkdir -p "+outputmain+"/src/")
#os.system("mkdir -p "+outputmain+"/output/")
##os.system("mkdir -p "+outputmain+"/skim/")
# don't do this
#################################################
## create castor dir
#################################################
##os.system("/afs/cern.ch/project/eos/installation/pro/bin/eos.select mkdir -p "+outputeosdir)
##################################################

# output prefix
# (something like analysisClass_lq1_skim___TTJets_SemiLeptMGDecays_8TeV-madgraph__Summer12_DR53X-PU_S10_START53_V7A-v1__AODSIM )
outputPrefix = string.split(outputmain,"/")[-1]
#################################################
# dataset
dataset = string.split(outputPrefix,"___")[-1]
# at this point we only have one dataset
#################################################
# workingDir
workingDir = outputmain[0:outputmain.rstrip('/').rfind('/')]
workingDir+='/crab/'
os.system("mkdir -p "+workingDir)
#print 'workingDir:',workingDir

# splitting handled by crab3
#numfiles = len(file(inputlist).readlines())
#ijobmax=int(options.ijobmax)
#if ijobmax > numfiles:
#    ijobmax=numfiles
#filesperjob = int(numfiles/ijobmax)
#if numfiles%ijobmax!=0:
#    filesperjob = filesperjob+1
#    ijobmax = int(numfiles/filesperjob)
#    if numfiles%filesperjob!=0:
#        ijobmax = ijobmax+1
##################################################
#input = open(inputlist)
##################################################
#for ijob in range(ijobmax):
# prepare the list file
#inputfilename = outputmain+"/input/input_"+str(ijob)+".list"
#inputfile = open(inputfilename,"w")
#for i in range(filesperjob):
#    line = input.readline()
#    if line != "":
#        inputfile.write(line)
#    continue
#inputfile.close()

# get just the file names, to be read from local pwd sandbox on grid node
cutfileName = cutfile.split('/')[-1]
inputListName = inputlist.split('/')[-1]
#TODO JSON 

# make a copy of the input list for this dataset
if not os.path.isfile(outputmain+'/'+inputListName):
  if os.path.isfile(os.path.abspath(inputlist)):
    shutil.copy2(os.path.abspath(inputlist),outputmain+'/'+inputListName)
  else:
    print 'could not find file:',os.path.abspath(inputlist)
    exit(-1)
inputlist = outputmain+'/'+inputListName
# already done in launch_crab3 script
## same for cutfile
#if not os.path.isfile(outputmain+'/'+cutfile):
#  shutil.copy2(cutfile,outputmain+'/'+cutfile)

# cut down output file name
# (something like TTJets_SemiLeptMGDecays_8TeV-madgraph__Summer12_DR53X-PU_S10_START53_V7A-v1__AODSIM )
outputFilePref = outputPrefix[outputPrefix.find('___')+3:]
# make the script (run by CRAB3)
scriptname = outputmain+"/src/submit_"+dataset+".sh"
scriptfile = open(scriptname,"w")
scriptfile.write("""#!/bin/bash
echo "================= Dumping Input files ===================="
""")
scriptfile.write('python -c "import PSet; print \'\\n\'.join(list(PSet.process.source.fileNames))"\n')
scriptfile.write('echo "Put into '+inputListName+'"\n')
scriptfile.write('python -c "import PSet; print \'\\n\'.join(list(PSet.process.source.fileNames))" > '+inputListName+'\n')
scriptfile.write('echo "cat '+inputListName+':"\n')
scriptfile.write('cat '+inputListName+'\n')
scriptfile.write("./main "+inputListName+" "+cutfileName+" "+options.treeName+" "+outputFilePref+" "+outputFilePref+"\n")
#scriptfile.write("# localoutputdirectory="+workingDir+"\n")
# define our own exit code for crab; see: https://twiki.cern.ch/twiki/bin/view/CMSPublic/CRAB3Miscellaneous#Define_your_own_exit_code_and_ex
scriptfile.write("""
# At the end of the script modify the FJR
exitCode=$?
exitMessage="My arbitrary exit message"
errorType="My arbitrary error type"

if [ -e FrameworkJobReport.xml ]
then
    cat << EOF > FrameworkJobReport.xml.tmp
<FrameworkJobReport>
<FrameworkError ExitStatus="$exitCode" Type="$errorType" >
$exitMessage
</FrameworkError>
EOF
    tail -n+2 FrameworkJobReport.xml >> FrameworkJobReport.xml.tmp
    mv FrameworkJobReport.xml.tmp FrameworkJobReport.xml
else
    cat << EOF > FrameworkJobReport.xml
<FrameworkJobReport>
<FrameworkError ExitStatus="$exitCode" Type="$errorType" >
$exitMessage
</FrameworkError>
</FrameworkJobReport>
EOF
fi
""")
scriptfile.close()


#print 'outputPrefix:',outputPrefix
#TODO: Define better path names (which are also short enough)

# now make the crab3 config
config = config()

config.General.requestName = outputPrefix
config.General.workArea = workingDir
config.General.transferOutputs = True
config.General.transferLogs = False

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'scripts/PSet.py' # apparently still need trivial PSet.py even if cmsRun is not used
# pass in cutfile, inputlist, and the binary
config.JobType.inputFiles = [cutfile,inputlist,'main']
# collect the output (root plots, dat, and skim)
config.JobType.outputFiles = [outputFilePref+'.root',outputFilePref+'.dat',outputFilePref+'_reduced_skim.root']

config.Data.outputPrimaryDataset = dataset.split('__')[0]

# read input list, convert to LFN
config.Data.userInputFiles = [line.split('root://eoscms//eos/cms')[-1].rstrip() for line in open(inputlist)]
#print 'userInputFiles=',config.Data.userInputFiles
# check length of input files
maxLengthPath = max(config.Data.userInputFiles, key=len)
if len(maxLengthPath) <= 255:
  print 'userInputFiles OK, longest path has:',len(maxLengthPath),'chars'
else:
  print
  print 'ERROR: found a file with length > 255 chars:\n"'+maxLengthPath+'"\nin userInputFiles (from inputlist); crab3 cannot handle this; exiting'
  exit(-1)
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1 # 1 file per job
config.Data.totalUnits = -1
config.Data.publication = False
config.Data.outputDatasetTag = 'LQSkim'
# notes on how the output will be stored: see https://twiki.cern.ch/twiki/bin/view/CMSPublic/Crab3DataHandling
#  <lfn-prefix>/<primary-dataset>/<publication-name>/<time-stamp>/<counter>[/log]/<file-name> 
#   LFNDirBase /                 / requestName      / stuff automatically done   / outputFilePref_999.root
config.Data.outLFNDirBase = '/store/group/phys_exotica/leptonsPlusJets/RootNtuple_skim/RunII/'
#config.Data.outLFNDirBase = '/store/group/phys_exotica/leptonsPlusJets/RootNtuple_skim/RunII/%s/' % (getUsernameFromSiteDB())
#config.Data.outLFNDirBase = '/store/user/%s/' % (getUsernameFromSiteDB())
if outputLFN is not None:
  if not outputLFN.startswith('/store'):
    print
    print 'ERROR: eosDir must start with /store and you specified:',outputLFN
    print 'quit'
    exit(-1)
  # add username if not already -- don't do this for now
  #if not getUsernameFromSiteDB() in outputLFN:
  #  outputLFN.rstrip('/')
  #  config.Data.outLFNDirBase = outputLFN+'/%s/' % (getUsernameFromSiteDB())
  #else:
  #  config.Data.outLFNDirBase = outputLFN
  config.Data.outLFNDirBase = outputLFN
if not config.Data.outLFNDirBase[-1]=='/':
  config.Data.outLFNDirBase+='/'
print 'Using outLFNDirBase:',config.Data.outLFNDirBase

storagePath=config.Data.outLFNDirBase+config.Data.outputPrimaryDataset+'/'+config.Data.outputDatasetTag+'/'+'YYMMDD_hhmmss/0000/'+outputFilePref+'_reduced_skim_999.root'
#print 'will store (example):',storagePath
#print '\twhich has length:',len(storagePath)
if len(storagePath) > 255:
  print
  print 'warning: we might have a problem with output path lengths too long (if we want to run crab over these).'
  print 'example output will look like:'
  print storagePath
  print 'which has length:',len(storagePath)
  print 'proceeding anyway'
  #print 'cowardly refusing to submit the jobs; exiting'
  #exit(-2)
else:
  print 'example output will look like:'
  print storagePath
  print 'ok, output files will have length about:',len(storagePath),'chars'

config.Site.storageSite = 'T2_CH_CERN'
config.Site.whitelist = ['T2_CH_CERN']

# some tricks
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/CRAB3AdvancedTutorial#Exercise_4_user_script
# user script
config.JobType.scriptExe = scriptname
# don't run cmsRun in the job (pass in template FrameworkJobReport.xml)
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/CRAB3Miscellaneous#Do_not_run_cmsRun_at_all_in_the
config.JobType.inputFiles += ['scripts/FrameworkJobReport.xml']

## print out config object
#attrs = vars(config)
#print ', '.join("%s: %s" % item for item in attrs.items())
#exit(-1)

#print 'using outLFNDirBase=',config.Data.outLFNDirBase
print 'submit!'

crabSubmit(config,options.dryRun)

