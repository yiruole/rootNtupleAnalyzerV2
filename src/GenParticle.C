#include "GenParticle.h"
#include "Object.h"
#include "IDTypes.h"

// Constructors
GenParticle::GenParticle():
  Object() {}

GenParticle::GenParticle(Collection& c, unsigned short i, short j, Long64_t current_entry ):
  Object(c,i,"GenParticle") {
  }

// Kinematic variables

float & GenParticle::Pt       (){ return m_collection->ReadArrayBranch<Float_t>("GenPart_pt")[m_raw_index]; }
float & GenParticle::Eta      (){ return m_collection->ReadArrayBranch<Float_t>("GenPart_eta")[m_raw_index]; } 
float & GenParticle::Phi      (){ return m_collection->ReadArrayBranch<Float_t>("GenPart_phi")[m_raw_index]; } 
float & GenParticle::Mass     (){ return m_collection->ReadArrayBranch<Float_t>("GenPart_mass")[m_raw_index]; } 

// ID variables		                                                       

int    GenParticle::PdgId       (){ return m_collection->ReadArrayBranch<Int_t>("GenPart_pdgId")[m_raw_index]; }
int    GenParticle::MotherIndex (){ return m_collection->ReadArrayBranch<Int_t>("GenPart_genPartIdxMother")[m_raw_index]; }
int    GenParticle::Status      (){ return m_collection->ReadArrayBranch<Int_t>("GenPart_status")[m_raw_index]; }
//int    GenParticle::NumDaughters(){ return m_collection -> GetData() -> GenPartNumDaught  -> at ( m_raw_index ); }
int    GenParticle::NumDaughters(){ return -1.0; }

//FIXME: parse from status flags
//bool GenParticle::IsHardProcess(){ return m_collection -> GetData() -> GenParticleIsHardProcess -> at ( m_raw_index ); }
//bool GenParticle::IsFromHardProcessFinalState(){ return m_collection -> GetData() -> GenParticleFromHardProcessFinalState -> at ( m_raw_index ); }
bool GenParticle::IsHardProcess(){ return true; }
bool GenParticle::IsFromHardProcessFinalState(){ return true; }

std::ostream& operator<<(std::ostream& stream, GenParticle& object) {
  stream << object.Name() << " " << ": "
	 << "PDG = "    << object.PdgId () << ", "
	 << "MotherIndex = "    << object.MotherIndex () << ", "
	 << "Num. daughters = " << object.NumDaughters () << ", "
	 << "Status = " << object.Status () << ", "
   << "IsHardProcess = " << object.IsHardProcess() << ", "
   << "IsFromHardProcessFinalState = " << object.IsFromHardProcessFinalState() << ", "
	 << "Pt = "     << object.Pt ()    << ", "
	 << "Eta = "    << object.Eta()    << ", "
	 << "Phi = "    << object.Phi()    << ", "
   << "Mass = "   << object.Mass();
  return stream;
}

