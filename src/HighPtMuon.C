#include "HighPtMuon.h"
#include "Object.h"
#include "IDTypes.h"

HighPtMuon::HighPtMuon():
  Object(),
  m_raw_index_alternate(0)
{}

HighPtMuon::HighPtMuon (Collection& c, unsigned int i, short j  ):
  Object     ( c,i, "HighPtMuon" ),
  m_isGlobal ( m_collection -> GetData() -> MuonIsGlobal -> at ( i ) == 0 )
{
  if ( m_raw_index == 0 && !m_isGlobal ){
    m_raw_index_alternate = -1;
  }
  else { 
    m_raw_index_alternate = m_raw_index;
    for ( int raw_index = 0; raw_index < i; ++raw_index ){ 
      if ( m_collection -> GetData() -> MuonIsGlobal -> at ( raw_index ) == 0 ){
	m_raw_index_alternate--;
      }
    }
  }
}

// Kinematic variables

double & HighPtMuon::Pt                      (){ return (m_isGlobal ? m_collection -> GetData() -> MuonCocktailPt      -> at ( m_raw_index_alternate ) : m_collection -> GetData() -> MuonPt      -> at ( m_raw_index ) ); } // OK
double & HighPtMuon::Eta                     (){ return (m_isGlobal ? m_collection -> GetData() -> MuonCocktailEta     -> at ( m_raw_index_alternate ) : m_collection -> GetData() -> MuonEta     -> at ( m_raw_index ) ); } // OK
double & HighPtMuon::Phi                     (){ return (m_isGlobal ? m_collection -> GetData() -> MuonCocktailPhi     -> at ( m_raw_index_alternate ) : m_collection -> GetData() -> MuonPhi     -> at ( m_raw_index ) ); } // OK
double   HighPtMuon::Charge                  (){ return (m_isGlobal ? m_collection -> GetData() -> MuonCocktailCharge  -> at ( m_raw_index_alternate ) : m_collection -> GetData() -> MuonCharge  -> at ( m_raw_index ) ); } // OK
double   HighPtMuon::PtError                 (){ return (m_isGlobal ? m_collection -> GetData() -> MuonCocktailPtError -> at ( m_raw_index_alternate ) : m_collection -> GetData() -> MuonPtError -> at ( m_raw_index ) ); } // OK
						   				   
// Isolation variables				   				   
						   				   
double HighPtMuon::TrkIso                    (){ return m_collection -> GetData() -> MuonTrkIso                     -> at ( m_raw_index ); } // No change
double HighPtMuon::PFIsoR04ChargedHadron     (){ return m_collection -> GetData() -> MuonPFIsoR04ChargedHadron      -> at ( m_raw_index ); } // No change
double HighPtMuon::PFIsoR04NeutralHadron     (){ return m_collection -> GetData() -> MuonPFIsoR04NeutralHadron      -> at ( m_raw_index ); } // No change
double HighPtMuon::PFIsoR04Photon            (){ return m_collection -> GetData() -> MuonPFIsoR04Photon             -> at ( m_raw_index ); } // No change
double HighPtMuon::PFIsoR04PU                (){ return m_collection -> GetData() -> MuonPFIsoR04PU                 -> at ( m_raw_index ); } // No change
						   				   
// ID variables					                                      
						   				   
int    HighPtMuon::IsGlobal                  (){ return m_collection -> GetData() -> MuonIsGlobal                   -> at ( m_raw_index ); } // OK
int    HighPtMuon::IsPFMuon                  (){ return m_collection -> GetData() -> MuonIsPF                       -> at ( m_raw_index ); } // OK
double HighPtMuon::GlobalChi2                (){ return m_collection -> GetData() -> MuonCocktailGlobalChi2         -> at ( m_raw_index ); } // OK
int    HighPtMuon::GlobalTrkValidHits        (){ return m_collection -> GetData() -> MuonGlobalTrkValidHits         -> at ( m_raw_index ); } // No change (but wrong?)
int    HighPtMuon::StationMatches            (){ return m_collection -> GetData() -> MuonStationMatches             -> at ( m_raw_index ); } // No change (but wrong?)
double HighPtMuon::BestTrackVtxDistXY        (){ return m_collection -> GetData() -> MuonBestTrackVtxDistXY         -> at ( m_raw_index ); } // No change (but wrong?)
double HighPtMuon::BestTrackVtxDistZ         (){ return m_collection -> GetData() -> MuonBestTrackVtxDistZ          -> at ( m_raw_index ); } // No change (but wrong?)
int    HighPtMuon::TrkPixelHits              (){ return m_collection -> GetData() -> MuonTrkPixelHits               -> at ( m_raw_index ); } // No change (but wrong?)
int    HighPtMuon::TrackLayersWithMeasurement(){ return m_collection -> GetData() -> MuonTrackLayersWithMeasurement -> at ( m_raw_index ); } // No change (but wrong?)

std::ostream& operator<<(std::ostream& stream, HighPtMuon& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "  << object.Pt ()    << ", "
	 << "Eta = " << object.Eta()    << ", "
	 << "Phi = " << object.Phi();
  return stream;
}
