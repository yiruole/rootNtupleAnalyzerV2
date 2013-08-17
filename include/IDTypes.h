#ifndef ELECTRON_ID_TYPES_H
#define ELECTRON_ID_TYPES_H

enum ID { 
  EGAMMA_VETO              = 0, 
  EGAMMA_LOOSE             = 1, 
  EGAMMA_MEDIUM            = 2, 
  EGAMMA_TIGHT             = 3, 
  HEEP                     = 4,
  HEEP_LOOSE               = 5,
  MVA                      = 6,
  ECAL_FIDUCIAL            = 7,
  		        
  HIGH_PT_MUON_TRKRELISO01 = 8,
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
  GEN_NU_FROM_W  	   = 22,
  GEN_ELE_FROM_W  	   = 23,
  GEN_ELE_FROM_DY  	   = 24,

  NULL_ID                  = 999
};

#endif
