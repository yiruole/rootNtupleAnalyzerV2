#include "Muon.h"
#include "Object.h"
#include "IDTypes.h"

Muon::Muon():
  Object()
{}

Muon::Muon (Collection& c, unsigned int i, short j, Long64_t current_entry ):
  Object ( c,i, "Muon" )
{}


// Kinematic variables

float & Muon::Pt                      (){ return CocktailPt(); } 
float & Muon::PtError                 (){ return CocktailPtError(); } 
float & Muon::Eta                     (){ return CocktailEta(); } 
//float & Muon::EtaError                (){ return CocktailEtaError(); } 
float & Muon::Phi                     (){ return CocktailPhi(); } 
//float & Muon::PhiError                (){ return CocktailPhiError(); } 
float   Muon::Charge                  (){ return m_collection -> GetData() -> Muon_charge            [m_raw_index]; } 
						   				   
float & Muon::PFPt                    (){ return m_collection -> GetData() -> Muon_pt                [m_raw_index]; } 
float & Muon::PFPtError               (){ return m_collection -> GetData() -> Muon_ptErr             [m_raw_index]; } 
float & Muon::PFEta                    (){ return m_collection -> GetData() -> Muon_eta              [m_raw_index]; } 
//float & Muon::PFEtaError               (){ return -1.0; } 
float & Muon::PFPhi                    (){ return m_collection -> GetData() -> Muon_phi              [m_raw_index]; } 
//float & Muon::PFPhiError               (){ return -1.0; } 

float & Muon::CocktailPt              (){ return m_collection -> GetData() -> Muon_ptTuneP           [m_raw_index]; } 
float & Muon::CocktailPtError         (){ return m_collection -> GetData() -> Muon_ptErr             [m_raw_index]; } 
float & Muon::CocktailEta              (){ return m_collection -> GetData() -> Muon_eta              [m_raw_index]; } 
//float & Muon::CocktailEtaError         (){ return -1.0; } 
float & Muon::CocktailPhi              (){ return m_collection -> GetData() -> Muon_phi              [m_raw_index]; } 
//float & Muon::CocktailPhiError         (){ return -1.0; } 
// Isolation variables				   				   
//FIXME not available?
float Muon::TrkIso                    (){ return -999; } 
float Muon::TrkIsoR03SumPt            (){ return -999; } 
//float Muon::PFIsoR04ChargedHadron     (){ return m_collection -> GetData() -> MuonPFIsoR04ChargedHadron      -> at ( m_raw_index ); } 
//float Muon::PFIsoR04NeutralHadron     (){ return m_collection -> GetData() -> MuonPFIsoR04NeutralHadron      -> at ( m_raw_index ); } 
//float Muon::PFIsoR04Photon            (){ return m_collection -> GetData() -> MuonPFIsoR04Photon             -> at ( m_raw_index ); } 
//float Muon::PFIsoR04PU                (){ return m_collection -> GetData() -> MuonPFIsoR04PU                 -> at ( m_raw_index ); } 
						   				   
// ID variables					                                      
						   				   
int    Muon::IsGlobal                  (){ return false; } 
int    Muon::IsTracker                 (){ return false; } 
int    Muon::IsPFMuon                  (){ return m_collection -> GetData() -> Muon_isPFcand [m_raw_index]; } 
float Muon::GlobalChi2                 (){ return -999; } 
int    Muon::GlobalTrkValidHits        (){ return -999; }  
int    Muon::StationMatches            (){ return m_collection -> GetData() -> Muon_nStations[m_raw_index]; } 
float Muon::BestTrackVtxDistXY         (){ return m_collection -> GetData() -> Muon_dxy      [m_raw_index]; } 
float Muon::BestTrackVtxDistZ          (){ return m_collection -> GetData() -> Muon_dz       [m_raw_index]; } 
int    Muon::TrkPixelHits              (){ return -999; } 
int    Muon::TrackLayersWithMeasurement(){ return m_collection -> GetData() -> Muon_nTrackerLayers [m_raw_index]; } 

std::ostream& operator<<(std::ostream& stream, Muon& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "  << object.Pt ()    << " +/- " << object.PtError() << ", "
	 << "Eta = " << object.Eta()    << ", "
	 << "Phi = " << object.Phi();
  return stream;
}
