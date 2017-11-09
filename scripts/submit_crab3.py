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
try:
  from CRABAPI.RawCommand import crabCommand
except ImportError:
  print
  print 'ERROR: Could not load CRABAPI.RawCommand.  Please source the crab3 setup:'
  print 'source /cvmfs/cms.cern.ch/crab3/crab.sh'
  exit(-1)

from httplib import HTTPException


def crabSubmit(config,crabDir,dryRun=False):
    maxRetries = 5
    for trial in xrange(0,maxRetries+1):
        if os.path.isdir ( workingDir+'crab_'+outputPrefix ):
          print 'remove already-existing crab project dir:',crabDir
          os.system('rm -rf '+workingDir+'crab_'+outputPrefix)
        try:
          if dryRun:
            print 'crabSubmit(): doing crab3 dryrun'
          #  crabCommand('submit',dryrun=dryRun,config = config)
          #else:
          #  #print "crabSubmit(): calling crabCommand('submit',config=config)"
          #  crabCommand('submit',config = config)
          crabCommand('submit',dryrun=dryRun,config = config)
        except HTTPException, hte:
          print '-----> there was a problem. see below.'
          print hte.headers
          #print 'Quitting here'
          #exit(-1)
          print 'WARN: Retrying submission;',maxRetries-trial,'attempts remain'
          continue
        # no exception, so we succeeded
        return
    # we finished the loop
    print 'ERROR: Tried',maxRetries,'times without success; quitting here'
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


usage = "usage: %prog [options] \nExample: ./scripts/submit_crab3.py -i HeepStudies_v1/MinimumBias__Commissioning10-SD_EG-v9__RECO_short.txt -c HeepStudies_v1/cutFile_HeepElectronStudiesV1.txt -o TestFrancesco/Mydataset -d /store/user/eberry/"

parser = OptionParser(usage=usage)

parser.add_option("-i", "--inputlist", dest="inputlist",
                  metavar="LIST")

parser.add_option("-c", "--cutfile", dest="cutfile",
                  metavar="CUTFILE")

parser.add_option("-o", "--output", dest="output",
                  metavar="OUTDIR")

parser.add_option("-t", "--treeName", dest="treeName",
                  metavar="TREENAME")

# splitting handled by crab3
#parser.add_option("-n", "--ijobmax", dest="ijobmax",
#                  help="max number of jobs, limited automatically to the number of files in inputlist",
#                  metavar="IJOBMAX")

parser.add_option("-d", "--eosDir", dest="eosDir",
                  metavar="EOSDIR")

# FIXME SIC: this doesn't work when using the API?
parser.add_option("-z", "--dryRun", dest="dryRun",
                  metavar="DRYRUN",default=False,action="store_true")

parser.add_option("-s", "--skim", dest="isSkimTask",
                  metavar="SKIMTASK",default=False,action="store_true")

parser.add_option("-r", "--reducedSkim", dest="isReducedSkimTask",
                  metavar="REDUCEDSKIMTASK",default=False,action="store_true")

parser.add_option("-l", "--overrideOutputLength", dest="overrideOutputLength",
                  metavar="OVERRIDEOUTPUTLENGTH",default=False,action="store_true")

parser.add_option("-f", "--cernT2Only", dest="submitCERNT2only",
                  metavar="submitCERNT2only",default=False,action="store_true")

parser.add_option("-j", "--inputFiles", dest="inputFiles",
                  metavar="inputFiles")



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
if outputLFN == None:
  print 'You must specify an output EOS directory; quitting'
  exit(-1)


#################################################
## make dirs on local disk
#################################################
#os.system("mkdir -p "+outputmain)
#os.system("mkdir -p "+outputmain+"/log/")
#os.system("mkdir -p "+outputmain+"/input/")
os.system("mkdir -p "+outputmain+"/src/")
#os.system("mkdir -p "+outputmain+"/output/")
##os.system("mkdir -p "+outputmain+"/skim/")

# output prefix
# (something like analysisClass_lq1_skim___TTJets_SemiLeptMGDecays_8TeV-madgraph__Summer12_DR53X-PU_S10_START53_V7A-v1__AODSIM )
outputPrefix = string.split(outputmain,"/")[-1].split('___')[-1]
outputPrefix = 'analysisClass___'+outputPrefix
if len(outputPrefix) > 100:
  print 'crab cannot handle requestName of more than 100 characters; ours has:',len(outputPrefix)
  print 'requestName was:',outputPrefix
  exit(-1)
#################################################
# dataset
dataset = string.split(outputPrefix,"___")[-1]
# at this point we only have one dataset
#################################################
# workingDir
#print 'outputmain=',outputmain
workingDir = outputmain[0:outputmain.rstrip('/').rfind('/')]
#print 'workingDir=',workingDir
workingDir+='/crab/'
if os.path.isdir ( workingDir+'crab_'+outputPrefix ):
  print 'NOT REMOVING ALREADY-EXISTING dir:',workingDir+'crab_'+outputPrefix
  exit(-1)
  print '-->removing already-existing crab project dir:',workingDir+'crab_'+outputPrefix
  os.system('rm -rf '+workingDir+'crab_'+outputPrefix)
os.system("mkdir -p "+workingDir)
crabDir = workingDir+'crab_'+outputPrefix
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

# make a copy of the input list for this dataset
if not os.path.isfile(outputmain+'/'+inputListName):
  if os.path.isfile(os.path.abspath(inputlist)):
    shutil.copy(os.path.abspath(inputlist),outputmain+'/'+inputListName)
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
# for skimming:
#   for the file splitting: crab will split the jobs and modify the process.source.fileNames list
#   here we read that out of the trivial cmsRun cfg, and put it into a local inputList.txt which is fed to main
#   (later we fill up userInputFiles by reading each file from the original inputList, which will allow crab to split them into separate jobs)
# for analysis:
#   we feed crab a nonsense input file (just the first on the list) per dataset
#   then we just run the analysis on the entire dataset here using the inputlist we passed in
#   this is costly if a single job/dataset fails
scriptname = outputmain+"/src/submit_"+dataset+".sh"
scriptfile = open(scriptname,"w")
scriptfile.write("""#!/bin/bash
echo "================= Dumping Input files ===================="
""")
scriptfile.write('python -c "import PSet; print \'\\n\'.join(list(PSet.process.source.fileNames))"\n')
if options.isSkimTask or options.isReducedSkimTask:
  scriptfile.write('echo "Put into '+inputListName+'"\n')
  scriptfile.write('python -c "import PSet; print \'\\n\'.join(list(PSet.process.source.fileNames))" > '+inputListName+'\n')
  scriptfile.write('echo "cat '+inputListName+':"\n')
  scriptfile.write('cat '+inputListName+'\n')
  scriptfile.write("./main "+inputListName+" "+cutfileName+" "+options.treeName+" "+outputFilePref+" "+outputFilePref+"\n")
else:
  # read the inputlist we pass to crab
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
# if we gave additional input files, feed them into the sandbox as well
# note that is read by the cutfile, which was modified in the 'launch' script to copy and then read from the input file in the working dir
additionalInputFiles = []
if len(options.inputFiles) > 0:
  additionalInputFiles = options.inputFiles.split(',')
  for f in additionalInputFiles:
    config.JobType.inputFiles.append(f)

# collect the output (root plots, dat, and skim)
config.JobType.outputFiles = [outputFilePref+'.root',outputFilePref+'.dat']
if options.isReducedSkimTask:
  config.JobType.outputFiles.append(outputFilePref+'_reduced_skim.root')
elif options.isSkimTask:
  config.JobType.outputFiles.append(outputFilePref+'_skim.root')

config.Data.outputPrimaryDataset = dataset.split('__')[0]

if options.isSkimTask or options.isReducedSkimTask:
  # read input list, convert to LFN
  config.Data.userInputFiles = [line.split('root://eoscms//eos/cms')[-1].rstrip() for line in open(inputlist)]
else:
  # just read the first file in, so crab thinks the dataset just has one file and just makes one job
  # but of course, main will run over all the root files
  # at some point, the analysis should be changed to support combining multiple jobs
  config.Data.userInputFiles = [open(inputlist).readline().rstrip()]
#config.Data.userInputFiles = [line.split('root://eoscms//eos/cms')[-1].rstrip() for line in open(inputlist)]

submitCERNT2only = options.submitCERNT2only
maxLengthPath = max(config.Data.userInputFiles, key=len)
if len(maxLengthPath) <= 255:
  print 'userInputFiles OK, longest path has:',len(maxLengthPath),'chars'
else:
  print
  print 'WARNING: found a file with length > 255 chars:\n"'+maxLengthPath+'"\nin userInputFiles (from inputlist); will try to reduce length and submit to CERN T2 only'
  config.Data.userInputFiles = [xrdPath.replace('cms-xrd-global.cern.ch//eos/cms','eoscms/') for xrdPath in config.Data.userInputFiles]
  submitCERNT2only = True
  # now check length again
  maxLengthPath = max(config.Data.userInputFiles, key=len)
  if len(maxLengthPath) > 255:
    print 'ERROR: found a file with length > 255 chars:\n"'+maxLengthPath+'"\nin userInputFiles (from inputlist) after trying to shorten it; crab3 cannot handle this; exiting'
    exit(-1)

config.Data.splitting = 'FileBased'
#config.Data.unitsPerJob = 5 # 5 files per job
config.Data.unitsPerJob = 10 # 10 files per job
config.Data.totalUnits = -1
config.Data.publication = False
if options.isSkimTask or options.isReducedSkimTask:
  config.Data.outputDatasetTag = 'Skim'
else:
  config.Data.outputDatasetTag = 'Ana'
# notes on how the output will be stored: see https://twiki.cern.ch/twiki/bin/view/CMSPublic/Crab3DataHandling
#  <lfn-prefix>/<primary-dataset>/<publication-name>/<time-stamp>/<counter>[/log]/<file-name> 
#   LFNDirBase /                 / requestName      / stuff automatically done   / outputFilePref_999.root
# defaults
#if options.isSkimTask or options.isReducedSkimTask:
#  config.Data.outLFNDirBase = '/store/group/phys_exotica/leptonsPlusJets/RootNtuple_skim/'
#else:
#  config.Data.outLFNDirBase = '/store/user/scooper/LQ/Ana/2015/'
#config.Data.outLFNDirBase = '/store/group/phys_exotica/leptonsPlusJets/RootNtuple_skim/RunII/%s/' % (getUsernameFromSiteDB())
#config.Data.outLFNDirBase = '/store/user/%s/' % (getUsernameFromSiteDB())
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

storagePath=config.Data.outLFNDirBase+config.Data.outputPrimaryDataset+'/'+config.Data.outputDatasetTag+'/'+'YYMMDD_hhmmss/0000/'+outputFilePref
if options.isReducedSkimTask:
  storagePath+='_reduced_skim_999.root'
elif options.isSkimTask:
  storagePath+='_skim_999.root'
else:
  storagePath+='_999.root'
#print 'will store (example):',storagePath
#print '\twhich has length:',len(storagePath)
if len(storagePath) > 255:
  print
  print 'warning: we might have a problem with output path lengths too long (if we want to run crab over these).'
  print 'example output will look like:'
  print storagePath
  print 'which has length:',len(storagePath)
  if options.isReducedSkimTask and not options.overrideOutputLength:
    # for skims, we might run crab over them, so don't allow this
    print 'cowardly refusing to submit the jobs; exiting'
    exit(-2)
  else:
    print 'proceeding anyway'
else:
  print 'example output will look like:'
  print storagePath
  print 'ok, output files will have length about:',len(storagePath),'chars'

config.Site.storageSite = 'T2_CH_CERN'
# run jobs at other sites
config.Data.ignoreLocality = True
# make more expansive whitelist for skims
# for analysis, just run at CERN+few others
if submitCERNT2only:
  config.Site.whitelist = ['T2_CH_CERN']
else:
  if options.isSkimTask or options.isReducedSkimTask:
    config.Site.whitelist = ['T2_CH_*','T2_FR_*','T2_IT_*','T2_DE_*','T2_ES_*','T2_BE_*','T2_PL_*','T2_UK_*','T2_FI_*','T2_GR_*','T2_HU_*','T2_PT_*']
  else:
    config.Site.whitelist = ['T2_CH_CERN','T2_FR_*','T2_IT_*','T2_DE_*','T2_ES_*','T2_BE_*','T2_UK_*',]
# default crab server blacklist
config.Site.blacklist = ['T2_CH_CSCS', 'T2_UK_SGrid_RALPP', 'T2_FR_GRIF_LLR', 'T2_BE_UCL', 'T2_FR_IPHC', 'T2_DE_DESY', 'T2_IT_Legnaro', 'T2_CH_CERN_AI', 'T2_UK_London_Brunel', 'T2_CH_CSCS_HPC', 'T2_IT_Pisa', 'T2_GR_Ioannina', 'T2_CH_CERN_HLT', 'T2_FR_GRIF_IRFU', 'T2_IT_Bari', 'T2_IT_Rome', 'T2_FR_CCIN2P3', 'T2_ES_CIEMAT', 'T2_PL_Warsaw', 'T2_HU_Budapest', 'T2_DE_RWTH', 'T2_PT_NCG_Lisbon', 'T2_PL_Swierk']
# my own additions based on failing jobs
config.Site.blacklist.extend(['T2_ES_IFCA', 'T2_EE_Estonia'])

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
#print 'submit!'

crabSubmit(config,crabDir,options.dryRun)

