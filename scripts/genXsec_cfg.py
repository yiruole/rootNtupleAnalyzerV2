import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
from dbs.apis.dbsClient import DbsApi
from dbs.exceptions.dbsClientException import dbsClientException

options = VarParsing ('analysis')
options.register ('dataset',
                  'test',
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.string,
                  "Full name/path of dataset")

options.parseArguments()

datasetpath = options.dataset
if datasetpath=='test':
    print 'ERROR: must specify full dataset name of NANOAODSIM dataset: dataset=/Primary/Secondary/NANOAODSIM'
    print 'Exiting.'
    print
    exit(-1)
print 'DBS: query for parent of dataset='+datasetpath+'...',

try:
    api = DbsApi(url = 'https://cmsweb.cern.ch/dbs/prod/global/DBSReader/')
    parents = api.listDatasetParents(dataset=datasetpath)
except dbsClientException, ex:
    print
    print "Caught API Exception %s: %s "  % (ex.name,ex)
    exit(-1)

#for parent in parents:
#    print parent
if len(parents) > 1:
    print
    print 'ERROR: got multiple parents for dataset:'
    for parent in parents:
        print parent['parent_dataset']
    print 'ERROR: not sure how to continue.'
    exit(-2)

print 'Done'
parentDataset = parents[0]['parent_dataset']
print 'DBS: Found parent dataset='+parentDataset
print 'DBS: query for files dataset...',

try:
    api = DbsApi(url = 'https://cmsweb.cern.ch/dbs/prod/global/DBSReader/')
    #dbsFiles = api.listFiles(dataset=datasetpath)
    dbsFiles = api.listFiles(dataset=parentDataset)
except dbsClientException, ex:
    print
    print "Caught API Exception %s: %s "  % (ex.name,ex)
    exit(-3)

print 'Done'
#for dbsFile in dbsFiles:
#    print dbsFile['logical_file_name']
# get first ten LFNs
firstTenFiles = [dbsFile['logical_file_name'] for dbsFile in dbsFiles]
if len(firstTenFiles) > 10:
    firstTenFiles = firstTenFiles[:10]
print 'INFO: using first',len(firstTenFiles),'out of',len(dbsFiles),'files in parent dataset as input to GenXSecAnalyzer'
print 'Run.'
print

process = cms.Process('XSec')

process.maxEvents = cms.untracked.PSet(
        input = cms.untracked.int32(options.maxEvents)
        )

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 10000

maxEvents = cms.untracked.PSet(input = cms.untracked.int32(5000000) )
secFiles = cms.untracked.vstring() 
process.source = cms.Source ("PoolSource",
        fileNames = cms.untracked.vstring(firstTenFiles),
        #fileNames = cms.untracked.vstring(options.inputFiles), 
        #fileNames = cms.untracked.vstring(

        #    '/store/mc/RunIISummer16MiniAODv2/GJets_Pt-20To100_13TeV-sherpa/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/F87154C7-C4CC-E611-BB3D-5065F3819221.root',
        #    '/store/mc/RunIISummer16MiniAODv2/GJets_Pt-20To100_13TeV-sherpa/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/5051D169-93CA-E611-8E9D-70106F4D2638.root',
        #    '/store/mc/RunIISummer16MiniAODv2/GJets_Pt-20To100_13TeV-sherpa/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/48EF5369-A3CA-E611-AEC2-00266CFFC51C.root',
        #    '/store/mc/RunIISummer16MiniAODv2/GJets_Pt-20To100_13TeV-sherpa/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/B405219B-A9CA-E611-83AC-1866DAEB5C74.root',
        #    '/store/mc/RunIISummer16MiniAODv2/GJets_Pt-20To100_13TeV-sherpa/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/CA4241ED-ACCA-E611-9CD1-002590E7D5A6.root',
        #    '/store/mc/RunIISummer16MiniAODv2/GJets_Pt-20To100_13TeV-sherpa/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/62F771CE-C4CC-E611-BA3B-C4346BC076D0.root',
        #    '/store/mc/RunIISummer16MiniAODv2/GJets_Pt-20To100_13TeV-sherpa/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/50CB01C0-C7CC-E611-802E-002590E7D7EA.root',
        #    '/store/mc/RunIISummer16MiniAODv2/GJets_Pt-20To100_13TeV-sherpa/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/E0B49C85-89CC-E611-AC60-00259073E382.root',
        #    '/store/mc/RunIISummer16MiniAODv2/GJets_Pt-20To100_13TeV-sherpa/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/AC6EE796-C5CC-E611-B281-00259074AE7A.root',
        #    '/store/mc/RunIISummer16MiniAODv2/GJets_Pt-20To100_13TeV-sherpa/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/120000/20560A41-C0CC-E611-BCA8-0CC47A537688.root',

        #  ),

            secondaryFileNames = secFiles)
process.xsec = cms.EDAnalyzer("GenXSecAnalyzer")

process.ana = cms.Path(process.xsec)
process.schedule = cms.Schedule(process.ana)
