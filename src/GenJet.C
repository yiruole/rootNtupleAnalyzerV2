#include "GenJet.h"
#include "Object.h"
#include "IDTypes.h"

// Constructors

GenJet::GenJet():
  Object(){}

GenJet::GenJet(Collection& c, unsigned short i, short j ):
  Object(c,i,"GenJet") {}

// Kinematic variables

double & GenJet::Pt  () { return m_collection -> GetData() -> GenJetPtAK4  -> at ( m_raw_index ); }
double & GenJet::Eta () { return m_collection -> GetData() -> GenJetEtaAK4 -> at ( m_raw_index ); } 
double & GenJet::Phi () { return m_collection -> GetData() -> GenJetPhiAK4 -> at ( m_raw_index ); } 

std::ostream& operator<<(std::ostream& stream, GenJet& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "  << object.Pt ()    << ", "
	 << "Eta = " << object.Eta()    << ", "
	 << "Phi = " << object.Phi();
  return stream;
}

