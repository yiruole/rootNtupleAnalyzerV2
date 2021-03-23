import FWCore.ParameterSet.Config as cms
process = cms.Process('PartListDrawer')

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 0

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1) )
secFiles = cms.untracked.vstring() 

process.source = cms.Source ("PoolSource",
        #fileNames = cms.untracked.vstring(options.inputFiles), 
        fileNames = cms.untracked.vstring(
            # 'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/005ED0EB-79F1-E611-B6DA-02163E011C2B.root',
            # 'file:/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleAnalyzerV2/scratch/pickedEvents.root'
            # '/store/mc/RunIISummer16MiniAODv2/WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/120000/0AF0207B-EFBE-E611-B4BE-0CC47A7FC858.root'
            # "/store/mc/RunIISummer16MiniAODv2/WJetsToLNu_Pt-100To250_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/00261BBA-B7D2-E611-96AF-141877410340.root"
            # '/store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/90000/B0E7C5FB-1426-E711-AC8B-002590200AD0.root'
            '/store/mc/RunIISummer16MiniAODv3/LQToDEle_M-1500_pair_TuneCUETP8M1_13TeV-madgraph-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/260000/18F23621-7D01-EB11-8AF6-00259075D72E.root',
            '/store/mc/RunIISummer16MiniAODv3/LQToDEle_M-1500_pair_TuneCUETP8M1_13TeV-madgraph-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/260000/2003A67F-8201-EB11-89F0-0CC47A4C8E5E.root',
            '/store/mc/RunIISummer16MiniAODv3/LQToDEle_M-1500_pair_TuneCUETP8M1_13TeV-madgraph-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/260000/22F3C8F7-7C01-EB11-A8C1-1C34DA7C6586.root',
            '/store/mc/RunIISummer16MiniAODv3/LQToDEle_M-1500_pair_TuneCUETP8M1_13TeV-madgraph-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/260000/32F1FF0C-7D01-EB11-B252-0CC47AFF2A6E.root',
            '/store/mc/RunIISummer16MiniAODv3/LQToDEle_M-1500_pair_TuneCUETP8M1_13TeV-madgraph-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/260000/3C189140-8C01-EB11-80EB-00259073E39C.root',
            '/store/mc/RunIISummer16MiniAODv3/LQToDEle_M-1500_pair_TuneCUETP8M1_13TeV-madgraph-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/260000/3C216608-7D01-EB11-B42B-001E675A6D10.root',
            '/store/mc/RunIISummer16MiniAODv3/LQToDEle_M-1500_pair_TuneCUETP8M1_13TeV-madgraph-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/260000/90D23E1B-7D01-EB11-A6A9-0242AC130002.root',
            '/store/mc/RunIISummer16MiniAODv3/LQToDEle_M-1500_pair_TuneCUETP8M1_13TeV-madgraph-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/260000/B4BD0216-7D01-EB11-96CD-0CC47A13D0BC.root',
            '/store/mc/RunIISummer16MiniAODv3/LQToDEle_M-1500_pair_TuneCUETP8M1_13TeV-madgraph-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/260000/DAD80126-7D01-EB11-8A27-782BCB536C8E.root',
            '/store/mc/RunIISummer16MiniAODv3/LQToDEle_M-1500_pair_TuneCUETP8M1_13TeV-madgraph-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/260000/F01CF91A-7D01-EB11-9CE6-FA163E3687CF.root',
            '/store/mc/RunIISummer16MiniAODv3/LQToDEle_M-1500_pair_TuneCUETP8M1_13TeV-madgraph-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/260000/FCF99111-7D01-EB11-9949-A0369F310120.root',

        ),
        #eventsToProcess = cms.untracked.VEventRange('1:1764962-1:1764962',),
        #eventsToProcess = cms.untracked.VEventRange('1:93773619-1:93773619',),
        eventsToProcess = cms.untracked.VEventRange('1:5:851-1:5:851',),

            secondaryFileNames = secFiles)


process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.printTree = cms.EDAnalyzer("ParticleListDrawer",
        maxEventsToPrint = cms.untracked.int32(10),
        printVertex = cms.untracked.bool(False),
        printOnlyHardInteraction = cms.untracked.bool(False), # Print only status=3 particles. This will not work for Pythia8, which does not have any such particles.
        src = cms.InputTag("prunedGenParticles")
)

process.path = cms.Path(process.printTree)
process.schedule = cms.Schedule(process.path)

