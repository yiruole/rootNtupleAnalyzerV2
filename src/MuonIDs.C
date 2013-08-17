#include <algorithm>
#include <cmath>

#include "Muon.h"
#include "IDTypes.h"

bool Muon::PassUserID (ID id, bool verbose){ 
  if      ( id == MUON_TIGHT_PFISO04  ) return PassUserID_MuonTight_PFIso04 ( verbose );
  else if ( id == MUON_FIDUCIAL       ) return PassUserID_MuonFiducial      ( verbose );
  else return false;
}

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
  bool pass_pfiso04   = bool ( pfiso04                       < 0.12);
  
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

