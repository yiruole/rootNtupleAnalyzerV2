#include "GenJet.h"
#include "Object.h"
#include "IDTypes.h"

// Constructors

GenJet::GenJet():
  Object(){}

GenJet::GenJet(Collection& c, unsigned short i, short j ):
  Object(c,i,"GenJet") {}

// Kinematic variables

double & GenJet::Pt  () { return m_collection -> GetData() -> GenJetPtAK5  -> at ( m_raw_index ); }
double & GenJet::Eta () { return m_collection -> GetData() -> GenJetEtaAK5 -> at ( m_raw_index ); } 
double & GenJet::Phi () { return m_collection -> GetData() -> GenJetPhiAK5 -> at ( m_raw_index ); } 

std::ostream& operator<<(std::ostream& stream, GenJet& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "  << object.Pt ()    << ", "
	 << "Eta = " << object.Eta()    << ", "
	 << "Phi = " << object.Phi();
  return stream;
}

