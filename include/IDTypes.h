#ifndef ELECTRON_ID_TYPES_H
#define ELECTRON_ID_TYPES_H

enum ID { 
  EGAMMA_VETO              = 0, 
  EGAMMA_LOOSE             = 1, 
  EGAMMA_MEDIUM            = 2, 
  EGAMMA_TIGHT             = 3, 
  HEEP61                   = 4,
  HEEP70                   = 5,
  HEEP70_2018              = 6,
  MVA                      = 7,
  ECAL_FIDUCIAL            = 8,
  		        
  MUON_HIGH_PT_TRKRELISO03 = 9,
  MUON_TIGHT_PFISO04TIGHT  = 10,
  MUON_FIDUCIAL            = 11,
  		        
  PFJET_LOOSE              = 12,
  PFJET_MEDIUM             = 13,
  PFJET_TIGHT              = 14,
  		           
  GEN_ELE_FROM_LQ          = 15,
  GEN_MUON_FROM_LQ         = 16,
  GEN_TAU_FROM_LQ          = 17,
  GEN_ELE_FIDUCIAL         = 18,
  GEN_MUON_FIDUCIAL        = 19,
  GEN_ELE_HARD_SCATTER     = 20,
  //GEN_ZGAMMA_HARD_SCATTER  = 21,
  //GEN_W_HARD_SCATTER       = 22,
  GEN_NU_FROM_W  	         = 23,
  //GEN_ELE_FROM_W  	       = 24,
  GEN_FROM_LQ              = 24,
  GEN_ELE_HARDPROCESS_FINALSTATE  	       = 25,
  GEN_LQ  	               = 26,
  GEN_TOP  	               = 27,
  GEN_STATUS62             = 28,
  GEN_NU_HARD_SCATTER      = 29,

  FAKE_RATE_HEEP_LOOSE     = 30,
  FAKE_RATE_VERY_LOOSE     = 32,
  FAKE_RATE_EGMLOOSE       = 34,
  FAKE_RATE_VERY_LOOSE_EGMLOOSE = 36,

  EGAMMA_BUILTIN_TIGHT     = 40,
  EGAMMA_BUILTIN_MEDIUM    = 41,
  EGAMMA_BUILTIN_LOOSE     = 42,
  EGAMMA_BUILTIN_VETO      = 43,
  HEEP70_MANUAL            = 44,

  HIGH_PT_MUON_TRKRELISO01 = 50, // keep for compatibility
  MUON_LOOSE_PFISO04LOOSE  = 51,
  MUON_LOOSE               = 52,

  GEN_MU_HARD_SCATTER      = 58,
  GEN_QUARK_HARD_SCATTER   = 59,
  GEN_QUARK_HARD_PROCESS   = 60,

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
