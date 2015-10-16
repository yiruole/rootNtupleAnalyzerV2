from CRABClient.UserUtilities import config
import os

outputPrefix='testingReducedSkimCrab3_v2'
outputLFN='/store/user/scooper/testingLQReducedSkimCrab3'
#scriptname=outputPrefix+'/submit_testingReducedSkimCrab3.sh'
scriptname='/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/RunII/lq_skim_2015/RootNtuple-v1-3-0-SingleEleLoose_SingleElectronOct05DataTEST/analysisClass_lq1_skim___SingleElectron/src/submit_SingleElectron.sh'
#cutfile=os.path.abspath('../../macros/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt')
cutfile='/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/RunII/lq_skim_2015/RootNtuple-v1-3-0-SingleEleLoose_SingleElectronOct05DataTEST//cutTable_lq1_skim_SingleEle_loose.txt'
#inputlist=os.getcwd()+'/config/LQToUE_BetaOne_RunIIMC_MINIAODSIM/LQToUE_M-600_BetaOne.txt'
inputlist='/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/RunII/lq_skim_2015/RootNtuple-v1-3-0-SingleEleLoose_SingleElectronOct05DataTEST//analysisClass_lq1_skim___SingleElectron/SingleElectron.txt'
dataset = 'LQToUE_BetaOne_RunIIMC_MINIAODSIM/LQToUE_M-600_BetaOne_TuneCUETP8M1_13TeV-pythia8__RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1__MINIAODSIM'

# now make the crab3 config
config = config()

config.General.requestName = outputPrefix+'crabpytest'
config.General.workArea = outputPrefix+'crabpytest'
config.General.transferOutputs = True
config.General.transferLogs = False

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'PSet.py' # apparently still need trivial PSet.py even if cmsRun is not used
# pass in cutfile and inputlist
config.JobType.inputFiles = [cutfile,inputlist,'main','FrameworkJobReport.xml']
# collect the output (root plots, dat, and skim)
config.JobType.outputFiles = [outputPrefix+'.root',outputPrefix+'.dat',outputPrefix+'_reduced_skim.root']

#config.Data.primaryDataset = dataset.split('__')[0]
#XXX FIXME for crab server bug
# https://hypernews.cern.ch/HyperNews/CMS/get/computing-tools/1035/1/1.html
config.Data.primaryDataset = '/SingleElectron/x/Y'
print 'using config.Data.primaryDataset=',config.Data.primaryDataset
#config.Data.userInputFiles = open(inputlist).readlines()
config.Data.userInputFiles = ['/store/group/phys_exotica/leptonsPlusJets/RootNtuple/RunII/scooper/v1-3-0/SingleElectron/LQ/151013_135314/0000/SingleElectron_1.root', '/store/group/phys_exotica/leptonsPlusJets/RootNtuple/RunII/scooper/v1-3-0/SingleElectron/LQ/151013_135314/0000/SingleElectron_2.root', '/store/group/phys_exotica/leptonsPlusJets/RootNtuple/RunII/scooper/v1-3-0/SingleElectron/LQ/151013_135314/0000/SingleElectron_3.root']
# convert to LFN
#config.Data.userInputFiles = [line.split('root://eoscms//eos/cms')[-1].rstrip() for line in open(inputlist)]
#config.Data.userInputFiles = open('testUserFilesList.txt').readlines()
#config.Data.userInputFiles = ['/store/user/scooper/LQ/RootNtuple/LQToUE_M-600_BetaOne_TuneCUETP8M1_13TeV-pythia8/crab_LQToUE_M-600_BetaOne_TuneCUETP8M1_13TeV-pythia8__RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1__MINIAODSIM/150820_153806/0000/LQToUE_M-600_BetaOne_TuneCUETP8M1_13TeV-pythia8__RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1__MINIAODSIM_1.root']
#config.Data.userInputFiles = ['srm://srm-eoscms.cern.ch:8443/srm/v2/server?SFN=/eos/cms/store/user/scooper/LQ/RootNtuple/LQToUE_M-600_BetaOne_TuneCUETP8M1_13TeV-pythia8/crab_LQToUE_M-600_BetaOne_TuneCUETP8M1_13TeV-pythia8__RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1__MINIAODSIM/150820_153806/0000/LQToUE_M-600_BetaOne_TuneCUETP8M1_13TeV-pythia8__RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1__MINIAODSIM_1.root']
#config.Data.userInputFiles = ['/store/data/Run2012B/SingleMu/AOD/13Jul2012-v1/0000/008DBED0-86D3-E111-AEDF-20CF3019DF17.root']
#config.Data.userInputFiles = ['/eos/cms/store/user/scooper/HCALSourcing/HCALSourceDataMonitor/P5_HBM_Sourcing_FebMar2014/hcalSourceDataMon.219029.root']
#print 'userInputFiles=',config.Data.userInputFiles
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1 # 1 file per job
config.Data.totalUnits = -1
config.Data.publication = False
config.Data.publishDataName = config.General.requestName
config.Data.outLFNDirBase = outputLFN

config.Site.storageSite = 'T2_CH_CERN'
config.Site.whitelist = ['T2_CH_CERN']

# some tricks
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/CRAB3AdvancedTutorial#Exercise_4_user_script
# user script
config.JobType.scriptExe = scriptname
# don't run cmsRun in the job (have to pass in template FrameworkJobReport.xml)
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/CRAB3Miscellaneous#Do_not_run_cmsRun_at_all_in_the
config.JobType.inputFiles += ['FrameworkJobReport.xml']

print 'using outLFNDirBase=',config.Data.outLFNDirBase
