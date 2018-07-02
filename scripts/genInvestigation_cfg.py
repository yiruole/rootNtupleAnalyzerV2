import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('analysis')
options.parseArguments()
process = cms.Process('XSec')

genParticlesLabel = 'prunedGenParticles'

process.hardProcessElectrons = cms.EDFilter("CandViewSelector",
        src = cms.InputTag(genParticlesLabel),
        cut = cms.string("abs(pdgId) == 11 && isHardProcess()")
)

process.hardProcessNeutrinos = cms.EDFilter("CandViewSelector",
        src = cms.InputTag(genParticlesLabel),
        cut = cms.string("(abs(pdgId)==12 || abs(pdgId)==14 || abs(pdgId)==16) && isHardProcess()")
)

process.hardProcessQuarks = cms.EDFilter("CandViewSelector",
        src = cms.InputTag(genParticlesLabel),
        cut = cms.string("abs(pdgId)>=1 && abs(pdgId)<=6 && isHardProcess() && pt > 0")
)


process.eleNumberFilter = cms.EDFilter("CandViewCountFilter",
    src = cms.InputTag("hardProcessElectrons"),
    minNumber = cms.uint32(1)
)

process.nuNumberFilter = cms.EDFilter("CandViewCountFilter",
    src = cms.InputTag("hardProcessNeutrinos"),
    minNumber = cms.uint32(1)
)

process.qNumberFilter = cms.EDFilter("CandViewCountFilter",
    src = cms.InputTag("hardProcessQuarks"),
    minNumber = cms.uint32(2)
)

process.options = cms.untracked.PSet(
    wantSummary      = cms.untracked.bool(True)
    #allowUnscheduled  = cms.untracked.bool(True)
)

#process.maxEvents = cms.untracked.PSet(
#        input = cms.untracked.int32(options.maxEvents)
#        )

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 5000

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(100000) )
secFiles = cms.untracked.vstring() 
process.source = cms.Source ("PoolSource",
        fileNames = cms.untracked.vstring(
          #'file:/tmp/scooper/file.root'
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/80000/448E499F-34D7-E611-A9F2-24BE05CE1E11.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/80000/5C4E9529-36D7-E611-A87D-24BE05CE1E11.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/80000/420322A6-37D7-E611-8BB3-24BE05CE1E11.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/80000/B4833A34-5DD7-E611-9ADF-A0369F301924.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/546E888D-C1D7-E611-B5B3-0CC47A0AD48A.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/FA46BEA1-C1D7-E611-8A2A-FA163EECA31F.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/C0E3226C-C1D7-E611-B02D-02163E0176C6.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/98BC8D82-C1D7-E611-8317-0CC47AD99148.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/80000/CA504FBD-72D7-E611-A248-008CFA197904.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/80000/C20FAD5D-72D7-E611-AAE7-FA163EB20BDE.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/80000/64F2336B-72D7-E611-B6CA-ECF4BBE16468.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/A0A62080-C1D7-E611-887F-0025905A613C.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/348A6DEC-C2D7-E611-A260-549F3525C380.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/80000/207FFF5B-72D7-E611-9033-0025905A48EC.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/80000/64C76F50-72D7-E611-9F71-0CC47A78A45A.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/80000/7E60C384-73D7-E611-9D82-90B11C0BD910.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/D2C6839D-C1D7-E611-B1C5-001E67DDBEDA.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/80000/BAB5967F-73D7-E611-AEF5-A4BF01013F29.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/6EFE3B71-C1D7-E611-A957-001E673985D4.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/2604F57C-C1D7-E611-9889-008CFA1974A0.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/80000/94FF0769-72D7-E611-97AB-002590E39D52.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/80000/14ABCCC3-72D7-E611-B6C2-002590D9D9DA.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/285EEBCC-60D7-E611-92EB-A0000420FE80.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/BC34ECAF-6CD7-E611-8F7E-A0000420FE80.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/20457CC1-74D7-E611-A445-24BE05CE2E81.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/242B665D-82D7-E611-89D8-5065F3818271.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/30E37A7D-84D7-E611-B497-A0000420FE80.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/5C6E0FEE-86D7-E611-8D90-E0071B749C80.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/EE06CEDD-9ED7-E611-AFBA-E0071B7AC770.root',
#'/store/mc/RunIISummer16MiniAODv2/WZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/A8B84A69-C1D7-E611-831F-5065F382B2D1.root',

'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/A4B7417D-5DCC-E611-97E5-0CC47A4C8EE8.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/8A4267CC-90CC-E611-A491-001E67E6F918.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/301511EE-62CA-E611-81C4-001E67F120A8.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/30BC386A-68CA-E611-B4C4-00266CFFCCBC.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/70018D1D-86CA-E611-93D9-001E67F120AD.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/A05A5A21-86CA-E611-88C2-6CC2173BC0A0.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/3296E4BF-A3CA-E611-8AF7-00266CFFCB14.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/264FAAB2-79CB-E611-BE25-001E67F336E0.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/048163EE-43CA-E611-9FA1-002590FD5A4C.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/F2F071F2-46CA-E611-BD8A-0CC47A57D164.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/E2203A4F-2ECB-E611-874B-002590D9D8B4.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/DABB2BFD-03C8-E611-ACFC-008CFAF5592A.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/4C9D420B-22C8-E611-8FFA-70106F4A9248.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/6431AE2A-19CC-E611-B0C6-00259073E3D0.root',
'/store/mc/RunIISummer16MiniAODv2/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/60000/A84D4939-53C9-E611-8202-90B11C04FAC6.root',
          ),
            secondaryFileNames = secFiles)
#process.xsec = cms.EDAnalyzer("GenXSecAnalyzer")

#process.ana = cms.Path(process.xsec)
#process.schedule = cms.Schedule(process.ana)

process.ana = cms.Path(process.hardProcessElectrons*process.hardProcessNeutrinos*process.hardProcessQuarks*process.eleNumberFilter*process.nuNumberFilter*process.qNumberFilter)
process.output = cms.OutputModule("PoolOutputModule",
                                  outputCommands = cms.untracked.vstring('drop *','keep *_*gen*_*_*','keep *_*Gen*_*_*'),
                                  fileName       = cms.untracked.string ("Output_amcAtNLO.root"),
                                  SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring('ana')),
)
process.outpath  = cms.EndPath (process.output)
