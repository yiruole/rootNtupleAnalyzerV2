#ifndef ELECTRON_ID_TYPES_H
#define ELECTRON_ID_TYPES_H

enum ID { 
  EGAMMA_VETO              = 0, 
  EGAMMA_LOOSE             = 1, 
  EGAMMA_MEDIUM            = 2, 
  EGAMMA_TIGHT             = 3, 
  HEEP60                   = 4,
  HEEP51                   = 5,
  MVA                      = 6,
  ECAL_FIDUCIAL            = 7,
  		        
  MUON_HIGH_PT_TRKRELISO03 = 8,
  MUON_TIGHT_PFISO04       = 9,
  MUON_FIDUCIAL            = 10,
  		        
  PFJET_LOOSE              = 11,
  PFJET_MEDIUM             = 12,
  PFJET_TIGHT              = 13,
  		           
  GEN_ELE_FROM_LQ          = 14,
  GEN_MUON_FROM_LQ         = 15,
  GEN_TAU_FROM_LQ          = 16,
  GEN_ELE_FIDUCIAL         = 17,
  GEN_MUON_FIDUCIAL        = 18,
  GEN_ELE_HARD_SCATTER     = 19,
  GEN_ZGAMMA_HARD_SCATTER  = 20,
  GEN_W_HARD_SCATTER       = 21,
  GEN_NU_FROM_W  	         = 22,
  GEN_ELE_FROM_W  	       = 23,
  GEN_ELE_FROM_DY  	       = 24,
  GEN_LQ  	               = 25,

  FAKE_RATE_HEEP_LOOSE     = 30,

  EGAMMA_BUILTIN_TIGHT     = 40,
  EGAMMA_BUILTIN_MEDIUM    = 41,
  EGAMMA_BUILTIN_LOOSE     = 42,
  EGAMMA_BUILTIN_VETO      = 43,

  // HLT
  // Taken from: https://github.com/cms-sw/cmssw/blob/CMSSW_7_5_X/DataFormats/HLTReco/interface/TriggerTypeDefs.h
  TRIGGER_PHOTON           = 81,
  TRIGGER_ELECTRON         = 82,
  TRIGGER_MUON             = 83,
  TRIGGER_TAU              = 84,
  TRIGGER_JET              = 85,

  NULL_ID                  = 999
};

#endif
