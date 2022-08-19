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

float Muon::PtError                 (){ return CocktailPtError(); } 
//float & Muon::EtaError                (){ return CocktailEtaError(); } 
//float & Muon::PhiError                (){ return CocktailPhiError(); } 
int Muon::Charge                  (){ return m_collection->ReadArrayBranch<Int_t>("Muon_charge", m_raw_index); } 
						   				   
float Muon::PFPt                    (){ return m_collection->ReadArrayBranch<Float_t>("Muon_pt",     m_raw_index); } 
float Muon::PFPtError               (){ return m_collection->ReadArrayBranch<Float_t>("Muon_ptErr",  m_raw_index); } 
float Muon::PFEta                    (){ return m_collection->ReadArrayBranch<Float_t>("Muon_eta",   m_raw_index); } 
//float & Muon::PFEtaError               (){ return -1.0; } 
float Muon::PFPhi                    (){ return m_collection->ReadArrayBranch<Float_t>("Muon_phi",   m_raw_index); } 
//float & Muon::PFPhiError               (){ return -1.0; } 

float Muon::CocktailPt              (){
  // for stock nano
  if(m_collection->HasBranch("Muon_tunepRelPt")) {
    return m_collection->ReadArrayBranch<Float_t>("Muon_tunepRelPt", m_raw_index)*m_collection->ReadArrayBranch<Float_t>("Muon_pt", m_raw_index);
  }
  else
    return -1.0;
  //// custom nano branch
  //return m_collection->ReadArrayBranch<Float_t>("Muon_ptTuneP", m_raw_index);
} 
float Muon::CocktailPtError         (){ return m_collection->ReadArrayBranch<Float_t>("Muon_ptErr",   m_raw_index); } 
float Muon::CocktailEta              (){ return m_collection->ReadArrayBranch<Float_t>("Muon_eta",    m_raw_index); } 
//float & Muon::CocktailEtaError         (){ return -1.0; } 
float Muon::CocktailPhi              (){ return m_collection->ReadArrayBranch<Float_t>("Muon_phi",    m_raw_index); } 
//float & Muon::CocktailPhiError         (){ return -1.0; } 
// Isolation variables				   				   
float Muon::TrkIso                    (){ return -999; } 
float Muon::TrkIsoR03SumPt            (){ return m_collection->ReadArrayBranch<Float_t>("Muon_tkRelIso", m_raw_index) * CocktailPt(); } 
//float Muon::PFIsoR04ChargedHadron     (){ return m_collection->ReadArrayBranch<Float_t>("") MuonPFIsoR04ChargedHadron      -> at ( m_raw_index ); } 
//float Muon::PFIsoR04NeutralHadron     (){ return m_collection->ReadArrayBranch<Float_t>("") MuonPFIsoR04NeutralHadron      -> at ( m_raw_index ); } 
//float Muon::PFIsoR04Photon            (){ return m_collection->ReadArrayBranch<Float_t>("") MuonPFIsoR04Photon             -> at ( m_raw_index ); } 
//float Muon::PFIsoR04PU                (){ return m_collection->ReadArrayBranch<Float_t>("") MuonPFIsoR04PU                 -> at ( m_raw_index ); } 
						   				   
// ID variables					                                      

bool    Muon::PassLooseId              (){ return m_collection->ReadArrayBranch<Bool_t>("Muon_looseId", m_raw_index); } 
bool    Muon::PassHighPtGlobalId       (){ return m_collection->ReadArrayBranch<UChar_t>("Muon_highPtId", m_raw_index)==2; } 
bool    Muon::IsGlobal                 (){ return m_collection->ReadArrayBranch<Bool_t>("Muon_isGlobal", m_raw_index); } 
bool    Muon::IsTracker                (){ return m_collection->ReadArrayBranch<Bool_t>("Muon_isTracker", m_raw_index); } 
bool    Muon::IsPFMuon                 (){ return m_collection->ReadArrayBranch<Bool_t>("Muon_isPFcand", m_raw_index); } 
float Muon::GlobalChi2                 (){ return -999; } 
int    Muon::GlobalTrkValidHits        (){ return -999; }  
int    Muon::StationMatches            (){ return m_collection->ReadArrayBranch<Int_t>("Muon_nStations", m_raw_index); } 
float Muon::BestTrackVtxDistXY         (){ return m_collection->ReadArrayBranch<Float_t>("Muon_dxy"    , m_raw_index); } 
float Muon::BestTrackVtxDistZ          (){ return m_collection->ReadArrayBranch<Float_t>("Muon_dz"     , m_raw_index); } 
int    Muon::TrkPixelHits              (){ return -999; } 
int    Muon::TrackLayersWithMeasurement(){ return m_collection->ReadArrayBranch<Int_t>("Muon_nTrackerLayers", m_raw_index); } 

std::ostream& operator<<(std::ostream& stream, Muon& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "  << object.Pt ()    << " +/- " << object.PtError() << ", "
	 << "Eta = " << object.Eta()    << ", "
	 << "Phi = " << object.Phi()    << ", "
   << "PassHighPtGlobalId = " << object.PassHighPtGlobalId() << ", "
   << "TrkIsoR03SumPt = " << object.TrkIsoR03SumPt() << ", "
   << "PassHighPtTrkRelIso03 = " << object.PassUserID(MUON_HIGH_PT_TRKRELISO03);
  return stream;
}
