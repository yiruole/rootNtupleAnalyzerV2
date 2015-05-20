#include "GenParticle.h"
#include "Object.h"
#include "IDTypes.h"

// Constructors
GenParticle::GenParticle():
  Object() {}

GenParticle::GenParticle(Collection& c, unsigned short i, short j ):
  Object(c,i,"GenParticle") {}

// Kinematic variables

double & GenParticle::Pt       (){ return m_collection -> GetData() -> GenParticlePt         -> at ( m_raw_index ); }
double & GenParticle::Eta      (){ return m_collection -> GetData() -> GenParticleEta        -> at ( m_raw_index ); } 
double & GenParticle::Phi      (){ return m_collection -> GetData() -> GenParticlePhi        -> at ( m_raw_index ); } 
double & GenParticle::Mass     (){ return m_collection -> GetData() -> GenParticleMass       -> at ( m_raw_index ); } 

// ID variables		                                                       

int    GenParticle::PdgId      (){ return m_collection -> GetData() -> GenParticlePdgId      -> at ( m_raw_index ); }
int    GenParticle::MotherIndex(){ return m_collection -> GetData() -> GenParticleMotherIndex-> at ( m_raw_index ); }
int    GenParticle::Status     (){ return m_collection -> GetData() -> GenParticleStatus     -> at ( m_raw_index ); }

std::ostream& operator<<(std::ostream& stream, GenParticle& object) {
  stream << object.Name() << " " << ": "
	 << "PDG = "    << object.PdgId () << ", "
	 << "Status = " << object.Status () << ", "
	 << "Pt = "     << object.Pt ()    << ", "
	 << "Eta = "    << object.Eta()    << ", "
	 << "Phi = "    << object.Phi()    << ", "
   << "Mass = "   << object.Mass();
  return stream;
}

