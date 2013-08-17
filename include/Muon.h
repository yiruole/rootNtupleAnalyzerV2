#ifndef MUON_H
#define MUON_H

#include "Object.h"
#include "IDTypes.h"
#include "Collection.h"

class Muon : public Object { 
  
 public:
  Muon ();
  Muon (Collection& c, unsigned int i, short j = 0);
  
  // Kinematic variables         

  double & Pt                      ();
  double & Eta                     ();
  double & Phi                     ();
  double   Charge                  ();

  // IDs 

  bool   PassUserID ( ID id, bool verbose = false );
         
  // Isolation variables

  double TrkIso                    ();
  double PFIsoR04ChargedHadron     ();
  double PFIsoR04NeutralHadron     ();
  double PFIsoR04Photon            ();
  double PFIsoR04PU                ();
         
  // ID variables      
         
  int    IsGlobal                  ();
  int    IsPFMuon                  ();
  double GlobalChi2                ();
  int    GlobalTrkValidHits        (); 
  int    StationMatches            ();
  double BestTrackVtxDistXY        ();
  double BestTrackVtxDistZ         ();
  int    TrkPixelHits              ();
  int    TrackLayersWithMeasurement();
  
 private:

  bool PassUserID_MuonTight_PFIso04 (bool verbose);
  bool PassUserID_MuonFiducial      (bool verbose);

};

std::ostream& operator<< (std::ostream& stream, Muon& object);

#endif
