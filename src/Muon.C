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

float & Muon::Pt                      (){ return CocktailPt(); } 
float & Muon::PtError                 (){ return CocktailPtError(); } 
float & Muon::Eta                     (){ return CocktailEta(); } 
float & Muon::EtaError                (){ return CocktailEtaError(); } 
float & Muon::Phi                     (){ return CocktailPhi(); } 
float & Muon::PhiError                (){ return CocktailPhiError(); } 
float   Muon::Charge                  (){ return m_collection -> GetData() -> MuonCharge                     -> at ( m_raw_index ); } 
						   				   
float & Muon::PFPt                    (){ return m_collection -> GetData() -> MuonPt                 -> at ( m_raw_index ); } 
float & Muon::PFPtError               (){ return m_collection -> GetData() -> MuonPtError            -> at ( m_raw_index ); } 
float & Muon::PFEta                    (){ return m_collection -> GetData() -> MuonEta                 -> at ( m_raw_index ); } 
float & Muon::PFEtaError               (){ return m_collection -> GetData() -> MuonEtaError            -> at ( m_raw_index ); } 
float & Muon::PFPhi                    (){ return m_collection -> GetData() -> MuonPhi                 -> at ( m_raw_index ); } 
float & Muon::PFPhiError               (){ return m_collection -> GetData() -> MuonPhiError            -> at ( m_raw_index ); } 

float & Muon::CocktailPt              (){ return m_collection -> GetData() -> MuonCocktailPt                 -> at ( m_raw_index ); } 
float & Muon::CocktailPtError         (){ return m_collection -> GetData() -> MuonCocktailPtError            -> at ( m_raw_index ); } 
float & Muon::CocktailEta              (){ return m_collection -> GetData() -> MuonCocktailEta                 -> at ( m_raw_index ); } 
float & Muon::CocktailEtaError         (){ return m_collection -> GetData() -> MuonCocktailEtaError            -> at ( m_raw_index ); } 
float & Muon::CocktailPhi              (){ return m_collection -> GetData() -> MuonCocktailPhi                 -> at ( m_raw_index ); } 
float & Muon::CocktailPhiError         (){ return m_collection -> GetData() -> MuonCocktailPhiError            -> at ( m_raw_index ); } 
// Isolation variables				   				   
						   				   
float Muon::TrkIso                    (){ return m_collection -> GetData() -> MuonTrkIso                     -> at ( m_raw_index ); } 
float Muon::TrkIsoR03SumPt            (){ return m_collection -> GetData() -> MuonTrackerIsoSumPT            -> at ( m_raw_index ); } 
//float Muon::PFIsoR04ChargedHadron     (){ return m_collection -> GetData() -> MuonPFIsoR04ChargedHadron      -> at ( m_raw_index ); } 
//float Muon::PFIsoR04NeutralHadron     (){ return m_collection -> GetData() -> MuonPFIsoR04NeutralHadron      -> at ( m_raw_index ); } 
//float Muon::PFIsoR04Photon            (){ return m_collection -> GetData() -> MuonPFIsoR04Photon             -> at ( m_raw_index ); } 
//float Muon::PFIsoR04PU                (){ return m_collection -> GetData() -> MuonPFIsoR04PU                 -> at ( m_raw_index ); } 
						   				   
// ID variables					                                      
						   				   
int    Muon::IsGlobal                  (){ return m_collection -> GetData() -> MuonIsGlobal                   -> at ( m_raw_index ); } 
int    Muon::IsTracker                 (){ return m_collection -> GetData() -> MuonIsTracker                  -> at ( m_raw_index ); } 
int    Muon::IsPFMuon                  (){ return m_collection -> GetData() -> MuonIsPF                       -> at ( m_raw_index ); } 
float Muon::GlobalChi2                 (){ return m_collection -> GetData() -> MuonGlobalChi2                 -> at ( m_raw_index ); } 
int    Muon::GlobalTrkValidHits        (){ return m_collection -> GetData() -> MuonGlobalTrkValidHits         -> at ( m_raw_index ); }  
int    Muon::StationMatches            (){ return m_collection -> GetData() -> MuonStationMatches             -> at ( m_raw_index ); } 
float Muon::BestTrackVtxDistXY         (){ return m_collection -> GetData() -> MuonBestTrackVtxDistXY         -> at ( m_raw_index ); } 
float Muon::BestTrackVtxDistZ          (){ return m_collection -> GetData() -> MuonBestTrackVtxDistZ          -> at ( m_raw_index ); } 
int    Muon::TrkPixelHits              (){ return m_collection -> GetData() -> MuonTrkPixelHits               -> at ( m_raw_index ); } 
int    Muon::TrackLayersWithMeasurement(){ return m_collection -> GetData() -> MuonTrackLayersWithMeasurement -> at ( m_raw_index ); } 

std::ostream& operator<<(std::ostream& stream, Muon& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "  << object.Pt ()    << " +/- " << object.PtError() << ", "
	 << "Eta = " << object.Eta()    << ", "
	 << "Phi = " << object.Phi();
  return stream;
}
