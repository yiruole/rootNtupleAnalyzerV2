#include <bitset>

#include "LHEParticle.h"
#include "Object.h"
#include "IDTypes.h"

// Constructors
LHEParticle::LHEParticle():
  Object() {}

LHEParticle::LHEParticle(Collection& c, unsigned short i, short j):
  Object(c,i,"LHEPart") {
  }

// Kinematic variables
float LHEParticle::Mass      (){ return m_collection->ReadArrayBranch<Float_t>("LHEPart_mass",m_raw_index); } 
float LHEParticle::IncomingPz(){ return m_collection->ReadArrayBranch<Float_t>("LHEPart_incomingpz",m_raw_index); } 
int LHEParticle::Spin      (){ return m_collection->ReadArrayBranch<Int_t>("LHEPart_spin",m_raw_index); } 

// ID variables		                                                       
int    LHEParticle::PdgId       (){ return m_collection->ReadArrayBranch<Int_t>("LHEPart_pdgId",m_raw_index); }
int    LHEParticle::Status      (){ return m_collection->ReadArrayBranch<Int_t>("LHEPart_status",m_raw_index); }


std::ostream& operator<<(std::ostream& stream, LHEParticle& object) {
  stream << object.Name() << " " << ": "
    << "idx = " << object.GetRawIndex() << ", "
	 << "PDG = "    << object.PdgId () << ", "
	 << "Status = " << object.Status () << ", "
	 << "Pt = "     << object.Pt ()    << ", "
	 << "Eta = "    << object.Eta()    << ", "
	 << "Phi = "    << object.Phi()    << ", "
	 << "Spin = "    << object.Spin()    << ", "
	 << "IncomingPz = "    << object.IncomingPz()    << ", "
   << "Mass = "   << object.Mass();
  return stream;
}

