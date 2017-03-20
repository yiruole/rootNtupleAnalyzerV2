#ifndef HIGH_PT_MUON_H
#define HIGH_PT_MUON_H

#include "Object.h"
#include "IDTypes.h"
#include "Collection.h"

class HighPtMuon : public Object { 
  
 public:
  HighPtMuon ();
  HighPtMuon (Collection& c, unsigned int i, short j = 0);
  
  // Kinematic variables         

  float & Pt                      ();
  float & Eta                     ();
  float & Phi                     ();
  float   PtError                 ();
  float   Charge                  ();

  // IDs 

  bool   PassUserID ( ID id, bool verbose = false );
         
  // Isolation variables

  float TrkIso                    ();
  float PFIsoR04ChargedHadron     ();
  float PFIsoR04NeutralHadron     ();
  float PFIsoR04Photon            ();
  float PFIsoR04PU                ();
         
  // ID variables      
         
  int    IsGlobal                  ();
  int    IsPFMuon                  ();
  float GlobalChi2                ();
  int    GlobalTrkValidHits        (); 
  int    StationMatches            ();
  float BestTrackVtxDistXY        ();
  float BestTrackVtxDistZ         ();
  int    TrkPixelHits              ();
  int    TrackLayersWithMeasurement();
  
 private:

  bool PassUserID_HighPtMuon_TrackRelIso01 (bool verbose);
  bool PassUserID_MuonFiducial             (bool verbose);

  // work-around for cocktail muon bug
  
  short m_raw_index_alternate;
  bool m_isGlobal;

};

std::ostream& operator<< (std::ostream& stream, HighPtMuon& object);

#endif
