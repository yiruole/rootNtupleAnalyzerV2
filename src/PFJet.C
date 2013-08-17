#include "PFJet.h"
#include "Object.h"
#include "IDTypes.h"
#include <math.h>

PFJet::PFJet ():
  Object ()
{}

PFJet::PFJet (Collection& c, unsigned int i, short j ):
  Object ( c,i, "PFJet" )
{}
                                     
double & PFJet::Pt                       () { return m_collection -> GetData() -> PFJetPt                           -> at ( m_raw_index ); } 
double & PFJet::Eta                      () { return m_collection -> GetData() -> PFJetEta                          -> at ( m_raw_index ); } 
double & PFJet::Phi                      () { return m_collection -> GetData() -> PFJetPhi                          -> at ( m_raw_index ); } 
double PFJet::Energy                     () { return m_collection -> GetData() -> PFJetEnergy                       -> at ( m_raw_index ); }
double PFJet::JECUnc		         () { return m_collection -> GetData() -> PFJetJECUnc                       -> at ( m_raw_index ); }
                                     
double PFJet::NeutralHadronEnergyFraction() { return m_collection -> GetData() -> PFJetNeutralHadronEnergyFraction  -> at ( m_raw_index ); } 
double PFJet::NeutralEmEnergyFraction    () { return m_collection -> GetData() -> PFJetNeutralEmEnergyFraction      -> at ( m_raw_index ); } 
int    PFJet::NConstituents              () { return m_collection -> GetData() -> PFJetNConstituents                -> at ( m_raw_index ); } 
double PFJet::ChargedHadronEnergyFraction() { return m_collection -> GetData() -> PFJetChargedHadronEnergyFraction  -> at ( m_raw_index ); } 
int    PFJet::ChargedMultiplicity        () { return m_collection -> GetData() -> PFJetChargedMultiplicity          -> at ( m_raw_index ); } 
double PFJet::ChargedEmEnergyFraction    () { return m_collection -> GetData() -> PFJetChargedEmEnergyFraction      -> at ( m_raw_index ); } 

double PFJet::CombinedSecondaryVertexBTag() { return m_collection -> GetData() -> PFJetCombinedSecondaryVertexBTag  -> at ( m_raw_index ); }

// Energy resolution scale factors

double PFJet::EnergyResScaleFactor (){ 
  double fabs_eta = fabs ( Eta () );
  if      ( fabs_eta > 0.0 && fabs_eta <= 0.5 ) return 1.052;
  else if ( fabs_eta > 0.5 && fabs_eta <= 1.1 ) return 1.057;
  else if ( fabs_eta > 1.1 && fabs_eta <= 1.7 ) return 1.096;
  else if ( fabs_eta > 1.7 && fabs_eta <= 2.3 ) return 1.134;
  else                                          return 1.288;
}

double PFJet::EnergyResScaleError  (){ 
  double fabs_eta = fabs ( Eta () );
  if      ( fabs_eta > 0.0 && fabs_eta <= 0.5 ) return 0.063;
  else if ( fabs_eta > 0.5 && fabs_eta <= 1.1 ) return 0.057;
  else if ( fabs_eta > 1.1 && fabs_eta <= 1.7 ) return 0.065;
  else if ( fabs_eta > 1.7 && fabs_eta <= 2.3 ) return 0.094;
  else                                          return 0.200;
}

double PFJet::EnergyScaleFactor (){ 
  return JECUnc();
}

std::ostream& operator<<(std::ostream& stream, PFJet& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "  << object.Pt ()    << ", "
	 << "Eta = " << object.Eta()    << ", "
	 << "Phi = " << object.Phi();
  return stream;
}
