#include <bitset>

#include "GenParticle.h"
#include "Object.h"
#include "IDTypes.h"

// Constructors
GenParticle::GenParticle():
  Object() {}

GenParticle::GenParticle(Collection& c, unsigned short i, short j):
  Object(c,i,"GenParticle") {
  }

// Kinematic variables

float GenParticle::Mass     (){ return m_collection->ReadArrayBranch<Float_t>("GenPart_mass",m_raw_index); } 

// ID variables		                                                       

int    GenParticle::PdgId       (){ return m_collection->ReadArrayBranch<Int_t>("GenPart_pdgId",m_raw_index); }
int    GenParticle::MotherIndex (){ return m_collection->ReadArrayBranch<Int_t>("GenPart_genPartIdxMother",m_raw_index); }
int    GenParticle::Status      (){ return m_collection->ReadArrayBranch<Int_t>("GenPart_status",m_raw_index); }
//int    GenParticle::NumDaughters(){ return m_collection -> GetData() -> GenPartNumDaught  -> at ( m_raw_index ); }
int    GenParticle::NumDaughters(){ return -1.0; }

int    GenParticle::StatusFlags() { return m_collection->ReadArrayBranch<Int_t>("GenPart_statusFlags",m_raw_index); }

bool GenParticle::IsHardProcess(){ return (m_collection->ReadArrayBranch<Int_t>("GenPart_statusFlags",m_raw_index) >> 7) & 0x1; }
bool GenParticle::IsFromHardProcess(){ return (m_collection->ReadArrayBranch<Int_t>("GenPart_statusFlags",m_raw_index) >> 8) & 0x1; }
bool GenParticle::IsFromHardProcessFinalState(){ return IsFromHardProcess() && (Status()==1); }

std::ostream& operator<<(std::ostream& stream, GenParticle& object) {
  stream << object.Name() << " " << ": "
	 << "PDG = "    << object.PdgId () << ", "
	 << "MotherIndex = "    << object.MotherIndex () << ", "
	 << "Num. daughters = " << object.NumDaughters () << ", "
	 << "Status = " << object.Status () << ", "
   //<< "StatusFlags = " << std::bitset<32>(object.StatusFlags()) << ", "
   << "IsHardProcess = " << object.IsHardProcess() << ", "
   << "IsFromHardProcessFinalState = " << object.IsFromHardProcessFinalState() << ", "
	 << "Pt = "     << object.Pt ()    << ", "
	 << "Eta = "    << object.Eta()    << ", "
	 << "Phi = "    << object.Phi()    << ", "
   << "Mass = "   << object.Mass();
  return stream;
}

