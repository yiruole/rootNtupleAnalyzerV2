import FWCore.ParameterSet.Config as cms

process = cms.Process('TEST')

#process.source = cms.Source("EmptySource")
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring())
process.maxEvents = cms.untracked.PSet(
  input = cms.untracked.int32(1)
)
