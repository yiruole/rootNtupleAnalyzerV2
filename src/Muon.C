#include "Muon.h"
#include "Object.h"
#include "IDTypes.h"

Muon::Muon():
  Object()
{}

Muon::Muon (Collection& c, unsigned int i, short j  ):
  Object ( c,i, "Muon" )
{}


// Kinematic variables

double & Muon::Pt                      (){ return m_collection -> GetData() -> MuonPt                         -> at ( m_raw_index ); } 
double & Muon::PtError                 (){ return m_collection -> GetData() -> MuonPtError                    -> at ( m_raw_index ); } 
double & Muon::Eta                     (){ return m_collection -> GetData() -> MuonEta                        -> at ( m_raw_index ); } 
double & Muon::Phi                     (){ return m_collection -> GetData() -> MuonPhi                        -> at ( m_raw_index ); } 
double   Muon::Charge                  (){ return m_collection -> GetData() -> MuonCharge                     -> at ( m_raw_index ); } 
						   				   
// Isolation variables				   				   
						   				   
double Muon::TrkIso                    (){ return m_collection -> GetData() -> MuonTrkIso                     -> at ( m_raw_index ); } 
double Muon::TrkIsoR03SumPt            (){ return m_collection -> GetData() -> MuonTrackerIsoSumPT            -> at ( m_raw_index ); } 
double Muon::PFIsoR04ChargedHadron     (){ return m_collection -> GetData() -> MuonPFIsoR04ChargedHadron      -> at ( m_raw_index ); } 
double Muon::PFIsoR04NeutralHadron     (){ return m_collection -> GetData() -> MuonPFIsoR04NeutralHadron      -> at ( m_raw_index ); } 
double Muon::PFIsoR04Photon            (){ return m_collection -> GetData() -> MuonPFIsoR04Photon             -> at ( m_raw_index ); } 
double Muon::PFIsoR04PU                (){ return m_collection -> GetData() -> MuonPFIsoR04PU                 -> at ( m_raw_index ); } 
						   				   
// ID variables					                                      
						   				   
int    Muon::IsGlobal                  (){ return m_collection -> GetData() -> MuonIsGlobal                   -> at ( m_raw_index ); } 
int    Muon::IsPFMuon                  (){ return m_collection -> GetData() -> MuonIsPF                       -> at ( m_raw_index ); } 
double Muon::GlobalChi2                (){ return m_collection -> GetData() -> MuonGlobalChi2                 -> at ( m_raw_index ); } 
int    Muon::GlobalTrkValidHits        (){ return m_collection -> GetData() -> MuonGlobalTrkValidHits         -> at ( m_raw_index ); }  
int    Muon::StationMatches            (){ return m_collection -> GetData() -> MuonStationMatches             -> at ( m_raw_index ); } 
double Muon::BestTrackVtxDistXY        (){ return m_collection -> GetData() -> MuonBestTrackVtxDistXY         -> at ( m_raw_index ); } 
double Muon::BestTrackVtxDistZ         (){ return m_collection -> GetData() -> MuonBestTrackVtxDistZ          -> at ( m_raw_index ); } 
int    Muon::TrkPixelHits              (){ return m_collection -> GetData() -> MuonTrkPixelHits               -> at ( m_raw_index ); } 
int    Muon::TrackLayersWithMeasurement(){ return m_collection -> GetData() -> MuonTrackLayersWithMeasurement -> at ( m_raw_index ); } 

std::ostream& operator<<(std::ostream& stream, Muon& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "  << object.Pt ()    << ", "
	 << "Eta = " << object.Eta()    << ", "
	 << "Phi = " << object.Phi();
  return stream;
}
