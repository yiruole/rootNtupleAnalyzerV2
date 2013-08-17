#include <algorithm>
#include <cmath>

#include "HighPtMuon.h"
#include "IDTypes.h"

bool HighPtMuon::PassUserID (ID id, bool verbose){ 
  if      ( id == HIGH_PT_MUON_TRKRELISO01  ) return PassUserID_HighPtMuon_TrackRelIso01 ( verbose );
  else if ( id == MUON_FIDUCIAL             ) return PassUserID_MuonFiducial             ( verbose );
  else return false;
}

bool HighPtMuon::PassUserID_HighPtMuon_TrackRelIso01 ( bool verbose ){

  double pfiso04 = ( PFIsoR04ChargedHadron() + std::max (0., PFIsoR04NeutralHadron() + PFIsoR04Photon() - ( 0.5 * PFIsoR04PU() ))) / Pt();
  
  bool pass_isGlobal  = bool ( IsGlobal()                   == 1   );
  bool pass_muonHits  = bool ( GlobalTrkValidHits()          > 0   );
  bool pass_stations  = bool ( StationMatches()              > 1   );
  bool pass_dxy       = bool ( fabs(BestTrackVtxDistXY())    < 0.2 );
  bool pass_dz        = bool ( fabs(BestTrackVtxDistZ ())    < 0.5 );
  bool pass_pixelHits = bool ( TrkPixelHits()                > 0   );
  bool pass_trkLayers = bool ( TrackLayersWithMeasurement()  > 5   );
  bool pass_ptError   = bool ( PtError() / Pt ()             < 0.3 );  
  bool pass_trkRelIso = bool ( TrkIso() / Pt()               < 0.1 );
  
  bool decision = ( pass_isGlobal  && 
		    pass_muonHits  && 
		    pass_stations  && 
		    pass_dxy       && 
		    pass_dz        && 
		    pass_pixelHits && 
		    pass_trkLayers && 
		    pass_ptError   && 
		    pass_trkRelIso   );
  
  return decision;
}

bool HighPtMuon::PassUserID_MuonFiducial ( bool verbose ) {
  if ( IsMuonFiducial() ) return true;
  else return false;
}

