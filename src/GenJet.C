#include "GenJet.h"
#include "Object.h"
#include "IDTypes.h"

// Constructors

GenJet::GenJet():
  Object(){}

GenJet::GenJet(Collection& c, unsigned short i, short j ):
  Object(c,i,"GenJet") {}

// Kinematic variables

float & GenJet::Pt  () { return m_collection -> GetData() -> GenJet_pt [m_raw_index]; }
float & GenJet::Eta () { return m_collection -> GetData() -> GenJet_eta[m_raw_index]; } 
float & GenJet::Phi () { return m_collection -> GetData() -> GenJet_phi[m_raw_index]; } 

std::ostream& operator<<(std::ostream& stream, GenJet& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "  << object.Pt ()    << ", "
	 << "Eta = " << object.Eta()    << ", "
	 << "Phi = " << object.Phi();
  return stream;
}

