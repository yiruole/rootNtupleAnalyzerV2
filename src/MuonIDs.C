#include <algorithm>
#include <cmath>

#include "Muon.h"
#include "IDTypes.h"

bool Muon::PassUserID (ID id, bool verbose){ 
  if      ( id == MUON_HIGH_PT_TRKRELISO03 ) return PassUserID_MuonHighPt_TrkRelIso03 ( verbose );
  else if ( id == MUON_TIGHT_PFISO04TIGHT  ) return PassUserID_MuonTight_PFIso04Tight ( verbose );
  else if ( id == MUON_LOOSE_PFISO04LOOSE  ) return PassUserID_MuonLoose_PFIso04Loose ( verbose );
  else if ( id == MUON_FIDUCIAL            ) return PassUserID_MuonFiducial      ( verbose );
  else return false;
}

// see: https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2
bool Muon::PassUserID_MuonHighPt_TrkRelIso03 ( bool verbose ){

  // Checked against Dave's definition: Jan. 30 2016

  // All non-global muons have cocktail Pt of -1 in the ntuples
  bool pass_isGlobalAndPt = bool ( CocktailPt()                    > 35 );
  bool pass_eta           = bool ( fabs(Eta())                     < 2.1);
  bool pass_muonHits      = bool ( GlobalTrkValidHits()            >= 1   );
  bool pass_stations      = bool ( StationMatches()                > 1   );
  bool pass_dxy           = bool ( fabs(BestTrackVtxDistXY())      < 0.2 );
  // [1] The most accurate way of computing this value is by using IPTools (example).
  // The dB() method of the pat::Muon uses the version in IPTools, so there are tiny differences
  //   between the values returned by dxy(vertex->position()) and dB(). 
  bool pass_dz            = bool ( fabs(BestTrackVtxDistZ ())      < 0.5 );
  bool pass_pixelHits     = bool ( TrkPixelHits()                  > 0   );
  bool pass_trkLayers     = bool ( TrackLayersWithMeasurement()    > 5   );
  bool pass_ptErr         = bool ( CocktailPtError()/CocktailPt()  < 0.3 );

  double trkRelIsoR03 = (TrkIsoR03SumPt()) / CocktailPt();
  // tight
  bool pass_trkRelIsoR03_tight = bool ( trkRelIsoR03             < 0.05);
  // loose
  bool pass_trkRelIsoR03_loose = bool ( trkRelIsoR03             < 0.10);
  
  bool decision = (
      pass_isGlobalAndPt  && 
      pass_eta       &&
      pass_muonHits  && 
      pass_stations  && 
      pass_dxy       && 
      pass_dz        && 
      pass_pixelHits && 
      pass_trkLayers && 
      pass_ptErr     &&
      pass_trkRelIsoR03_loose
      );
  
  return decision;
}

// see: https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2
//   since Run I: changed PFISO cut from 0.12 to 0.15
bool Muon::PassUserID_MuonTight_PFIso04Tight ( bool verbose ){

  double pfiso04 = ( PFIsoR04ChargedHadron() + std::max (0., PFIsoR04NeutralHadron() + PFIsoR04Photon() - ( 0.5 * PFIsoR04PU() ))) / Pt();
  
  bool pass_isGlobal  = bool ( IsGlobal()                   == 1   );
  bool pass_isPF      = bool ( IsPFMuon()                   == 1   );
  bool pass_chi2      = bool ( GlobalChi2 ()                 < 10. );
  bool pass_muonHits  = bool ( GlobalTrkValidHits()          > 0   );
  bool pass_stations  = bool ( StationMatches()              > 1   );
  bool pass_dxy       = bool ( fabs(BestTrackVtxDistXY())    < 0.2 );
  bool pass_dz        = bool ( fabs(BestTrackVtxDistZ ())    < 0.5 );
  bool pass_pixelHits = bool ( TrkPixelHits()                > 0   );
  bool pass_trkLayers = bool ( TrackLayersWithMeasurement()  > 5   );
  bool pass_pfiso04   = bool ( pfiso04                       < 0.15);
  
  bool decision = ( pass_isGlobal  && 
		    pass_isPF      && 
		    pass_chi2      && 
		    pass_muonHits  && 
		    pass_stations  && 
		    pass_dxy       && 
		    pass_dz        && 
		    pass_pixelHits && 
		    pass_trkLayers && 
		    pass_pfiso04   );
  
  return decision;
}

bool Muon::PassUserID_MuonFiducial ( bool verbose ) {
  if ( IsMuonFiducial() ) return true;
  else return false;
}

// see: https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2
bool Muon::PassUserID_MuonLoose_PFIso04Loose ( bool verbose ){
  bool pass_isGlobal   = bool ( IsGlobal()                   == 1   );
  bool pass_isTracker  = bool ( IsTracker()                  == 1   );
  bool pass_isPF       = bool ( IsPFMuon()                   == 1   );

  double pfiso04 = ( PFIsoR04ChargedHadron() + std::max (0., PFIsoR04NeutralHadron() + PFIsoR04Photon() - ( 0.5 * PFIsoR04PU() ))) / Pt();
  bool pass_pfiso04   = bool ( pfiso04                       < 0.25); // loose iso
  
  bool decision = (pass_isGlobal || pass_isTracker) &&
    pass_isPF &&
    pass_pfiso04;

  return decision;
}

