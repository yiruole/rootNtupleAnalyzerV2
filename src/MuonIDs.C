#include <algorithm>
#include <cmath>

#include "Muon.h"
#include "IDTypes.h"

bool Muon::PassUserID (ID id, bool verbose){ 
  if      ( id == MUON_HIGH_PT_TRKRELISO03 ) return PassUserID_MuonHighPt_TrkRelIso03 ( verbose );
  else if ( id == MUON_TIGHT_PFISO04       ) return PassUserID_MuonTight_PFIso04 ( verbose );
  else if ( id == MUON_FIDUCIAL            ) return PassUserID_MuonFiducial      ( verbose );
  else return false;
}

// see: https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2
bool Muon::PassUserID_MuonHighPt_TrkRelIso03 ( bool verbose ){

  double trkRelIsoR03 = (TrkIsoR03SumPt) / Pt();
  
  bool pass_isGlobal      = bool ( IsGlobal()                   == 1   );
  bool pass_muonHits      = bool ( GlobalTrkValidHits()          > 0   );
  bool pass_stations      = bool ( StationMatches()              > 1   );
  // PtErr ?
  //The pT relative error of the muon best track is less than 30%
  // recoMu.muonBestTrack()->ptError()/recoMu.muonBestTrack()->pt() < 0.3
  // - we can use either the inner track or the global track pt error for the moment
  // use global for now
  bool pass_ptErr         = bool ( PtError()/Pt()                < 0.3 );
  bool pass_dxy           = bool ( fabs(BestTrackVtxDistXY())    < 0.2 );
  // [1] The most accurate way of computing this value is by using IPTools (example).
  // The dB() method of the pat::Muon uses the version in IPTools, so there are tiny differences
  //   between the values returned by dxy(vertex->position()) and dB(). 
  bool pass_dz            = bool ( fabs(BestTrackVtxDistZ ())    < 0.5 );
  bool pass_pixelHits     = bool ( TrkPixelHits()                > 0   );
  bool pass_trkLayers     = bool ( TrackLayersWithMeasurement()  > 5   );
  // tight
  bool pass_trkRelIsoR03_tight = bool ( trkRelIsoR03             < 0.05);
  // loose
  bool pass_trkRelIsoR03_loose = bool ( trkRelIsoR03             < 0.10);
  
  bool decision = (
      pass_isGlobal  && 
      pass_muonHits  && 
      pass_stations  && 
      pass_ptErr     &&
      pass_dxy       && 
      pass_dz        && 
      pass_pixelHits && 
      pass_trkLayers && 
      pass_trkRelIsoR03_tight
      );
  
  return decision;
}

// see: https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2
//   since Run I: changed PFISO cut from 0.12 to 0.15
bool Muon::PassUserID_MuonTight_PFIso04 ( bool verbose ){

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

