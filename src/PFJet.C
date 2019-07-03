#include "PFJet.h"
#include "Object.h"
#include "IDTypes.h"
#include <math.h>

PFJet::PFJet ():
  Object ()
{}

PFJet::PFJet (Collection& c, unsigned int i, short j):
  Object ( c,i, "PFJet" )
{}
                                     
float PFJet::Energy                     () { return -1.0; }
//FIXME
float PFJet::JECUnc		                  () { return -1.0; }
                                     
float PFJet::NeutralHadronEnergyFraction() { return m_collection->ReadArrayBranch<Float_t>("Jet_neHEF" ,m_raw_index); } 
float PFJet::NeutralEmEnergyFraction    () { return m_collection->ReadArrayBranch<Float_t>("Jet_neEmEF",m_raw_index); } 
int    PFJet::NeutralHadronMultiplicity  () { -1; }
int    PFJet::NeutralMultiplicity        () { -1; }
int    PFJet::NConstituents              () { return m_collection->ReadArrayBranch<Int_t>("Jet_nConstituents"  , m_raw_index); } 
float PFJet::ChargedHadronEnergyFraction() { return m_collection->ReadArrayBranch<Float_t>("Jet_chHEF"         , m_raw_index); } 
int    PFJet::ChargedMultiplicity        () { -1; } 
float PFJet::ChargedEmEnergyFraction    () { return m_collection->ReadArrayBranch<Float_t>("Jet_chEmEF"        , m_raw_index); } 

int PFJet::JetID() { return m_collection->ReadArrayBranch<Int_t>("Jet_jetId",m_raw_index); }
//float PFJet::CombinedSecondaryVertexBTag() { return m_collection->ReadArrayBranch<Float_t>("") PFJetCombinedSecondaryVertexBTagAK4CHS  -> at ( m_raw_index ); }
float PFJet::CombinedInclusiveSecondaryVertexBTag() { return m_collection->ReadArrayBranch<Float_t>("Jet_btagCSVV2",m_raw_index); }
float PFJet::CombinedMVABTag() { return m_collection->ReadArrayBranch<Float_t>("Jet_btagCMVA",m_raw_index); }
//FIXME or Jet_btagDeepFlavB ?
float PFJet::DeepCSVBTag() { return m_collection->ReadArrayBranch<Float_t>("Jet_btagDeepB",m_raw_index); }

// Energy resolution scale factors
// see: https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetResolution
float PFJet::EnergyResScaleFactor (){ 
  return -1.0;
  //return m_collection->ReadArrayBranch<Float_t>("") PFJetJERResSFAK4CHS -> at ( m_raw_index );
  //float fabs_eta = fabs ( Eta () );
  //if      ( fabs_eta > 0.0 && fabs_eta <= 0.5 ) return 1.109;
  //else if ( fabs_eta > 0.5 && fabs_eta <= 0.8 ) return 1.138;
  //else if ( fabs_eta > 0.8 && fabs_eta <= 1.1 ) return 1.114;
  //else if ( fabs_eta > 1.1 && fabs_eta <= 1.3 ) return 1.123;
  //else if ( fabs_eta > 1.3 && fabs_eta <= 1.7 ) return 1.084;
  //else if ( fabs_eta > 1.7 && fabs_eta <= 1.9 ) return 1.082;
  //else if ( fabs_eta > 1.9 && fabs_eta <= 2.1 ) return 1.140;
  //else if ( fabs_eta > 2.1 && fabs_eta <= 2.3 ) return 1.067;
  //else if ( fabs_eta > 2.3 && fabs_eta <= 2.5 ) return 1.177;
  //else if ( fabs_eta > 2.5 && fabs_eta <= 2.8 ) return 1.364;
  //else if ( fabs_eta > 2.8 && fabs_eta <= 3.0 ) return 1.857;
  //else if ( fabs_eta > 3.0 && fabs_eta <= 3.2 ) return 1.328;
  //else                                          return 1.16;
}

// see: https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetResolution
float PFJet::EnergyResScaleError  (){ 
  float fabs_eta = fabs ( Eta () );
  if      ( fabs_eta > 0.0 && fabs_eta <= 0.5 ) return 0.008;
  else if ( fabs_eta > 0.5 && fabs_eta <= 0.8 ) return 0.013;
  else if ( fabs_eta > 0.8 && fabs_eta <= 1.1 ) return 0.013;
  else if ( fabs_eta > 1.1 && fabs_eta <= 1.3 ) return 0.024;
  else if ( fabs_eta > 1.3 && fabs_eta <= 1.7 ) return 0.011;
  else if ( fabs_eta > 1.7 && fabs_eta <= 1.9 ) return 0.035;
  else if ( fabs_eta > 1.9 && fabs_eta <= 2.1 ) return 0.047;
  else if ( fabs_eta > 2.1 && fabs_eta <= 2.3 ) return 0.053;
  else if ( fabs_eta > 2.3 && fabs_eta <= 2.5 ) return 0.041;
  else if ( fabs_eta > 2.5 && fabs_eta <= 2.8 ) return 0.039;
  else if ( fabs_eta > 2.8 && fabs_eta <= 3.0 ) return 0.071;
  else if ( fabs_eta > 3.0 && fabs_eta <= 3.2 ) return 0.022;
  else                                          return 0.029;
}

// JES uncertainties already in the ntuple
float PFJet::EnergyScaleFactor (){ 
  return JECUnc();
}

float PFJet::EnergyRes(){
  //return m_collection->ReadArrayBranch<Float_t>("") PFJetJERResAK4CHS -> at ( m_raw_index );
  return -1.0;
}

std::ostream& operator<<(std::ostream& stream, PFJet& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "  << object.Pt ()    << ", "
	 << "Eta = " << object.Eta()    << ", "
	 << "Phi = " << object.Phi();
  return stream;
}
