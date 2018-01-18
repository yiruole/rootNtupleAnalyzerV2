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

  float & Pt                      ();
  float & PtError                 ();
  float & Eta                     ();
  float & Phi                     ();
  float   Charge                  ();

  float & CocktailPt              ();
  float & CocktailPtError         ();

  // IDs 

  bool   PassUserID ( ID id, bool verbose = false );
         
  // Isolation variables

  float TrkIso                    ();
  float TrkIsoR03SumPt            ();
//  float PFIsoR04ChargedHadron     ();
//  float PFIsoR04NeutralHadron     ();
//  float PFIsoR04Photon            ();
//  float PFIsoR04PU                ();
         
  // ID variables      
         
  int    IsGlobal                  ();
  int    IsTracker                 ();
  int    IsPFMuon                  ();
  float GlobalChi2                 ();
  int    GlobalTrkValidHits        (); 
  int    StationMatches            ();
  float BestTrackVtxDistXY         ();
  float BestTrackVtxDistZ          ();
  int    TrkPixelHits              ();
  int    TrackLayersWithMeasurement();
  
 private:

  bool PassUserID_MuonHighPt_TrkRelIso03  (bool verbose);
  bool PassUserID_MuonTight_PFIso04Tight  (bool verbose);
  bool PassUserID_MuonFiducial            (bool verbose);
  bool PassUserID_MuonLoose_PFIso04Loose  (bool verbose);

};

std::ostream& operator<< (std::ostream& stream, Muon& object);

#endif
