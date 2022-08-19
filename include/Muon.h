#ifndef MUON_H
#define MUON_H

#include "Object.h"
#include "IDTypes.h"
#include "Collection.h"

class Muon : public Object { 
  
 public:
  Muon ();
  Muon (Collection& c, unsigned int i, short j = 0, Long64_t current_entry = 0);
  
  // Kinematic variables         

  float PtError                 (); // this is cocktail/TuneP, the one we want by default
  //float & EtaError                (); // this is cocktail/TuneP, the one we want by default
  //float & PhiError                (); // this is cocktail/TuneP, the one we want by default

  float PFPt                    ();
  float PFPtError               ();
  float PFEta                   ();
  float PFEtaError              ();
  float PFPhi                   ();
  float PFPhiError              ();

  float CocktailEta             ();
  //float & CocktailEtaError        ();
  float CocktailPhi             ();
  //float & CocktailPhiError        ();
  float CocktailPt              ();
  float CocktailPtError         ();

  int   Charge                  ();


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
         
  bool    PassLooseId               ();
  bool    PassHighPtGlobalId        ();
  bool    IsGlobal                  ();
  bool    IsTracker                 ();
  bool    IsPFMuon                  ();
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
  bool PassUserID_MuonLoose               (bool verbose);

};

std::ostream& operator<< (std::ostream& stream, Muon& object);

#endif
