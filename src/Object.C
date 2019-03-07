#include "Object.h"
#include <cmath>

Object::~Object(){}

Object::Object():
  m_name ("NO_NAME"),
  m_collection(0),
  m_raw_index ( -1 ),
  m_trigObj_index (-1)
{}

Object::Object(const Object & o):
  m_name(o.m_name),
  m_collection(o.m_collection),
  m_raw_index(o.m_raw_index),
  m_trigObj_index ( o.m_trigObj_index )
{}

Object::Object(Collection & collection, short raw_index, Long64_t current_entry):
  m_name ("NO_NAME"),
  m_collection ( & collection ),
  m_raw_index (raw_index),
  m_trigObj_index (-1)
{}

Object::Object(Collection & collection, short raw_index, short trigObj_index, Long64_t current_entry):
  m_name ("NO_NAME"),
  m_collection ( & collection ),
  m_raw_index (raw_index),
  m_trigObj_index (trigObj_index)
{}

Object::Object(Collection & collection, short raw_index, const char* name, Long64_t current_entry):
  m_name (name),
  m_collection ( & collection ),
  m_raw_index (raw_index),
  m_trigObj_index (-1)
{}

Object::Object(Collection & collection, short raw_index, short trigObj_index, const char* name, Long64_t current_entry):
  m_name (name),
  m_collection ( & collection ),
  m_raw_index (raw_index),
  m_trigObj_index (trigObj_index)
{}

float Object::DeltaR( Object * other_object ) { 
  float deta = Eta() - other_object -> Eta();
  float dphi = DeltaPhi ( other_object );
  float dr = sqrt ( deta * deta + dphi * dphi );
  return dr;
}

float Object::DeltaPhi( Object * other_object ) { 
  float dphi = Phi_mpi_pi ( Phi() - other_object -> Phi() );
  return dphi;
}

float Object::DeltaPt( Object * other_object ) {
  return Pt() - other_object -> Pt();
}

float Object::Phi_mpi_pi ( float x ) {
  float PI = 3.14159265359;
  while ( x >=  PI ) x -= ( 2*PI );
  while ( x <  -PI ) x += ( 2*PI );
  return x;
}

bool Object::IsGenEBFiducial       () { return bool ( fabs(Eta()) < 1.4442 ); }
bool Object::IsGenEEFiducial       () { return bool ( ( fabs(Eta()) > 1.566 ) && ( fabs(Eta()) < 2.50 ) ); }
bool Object::IsGenElectronFiducial () { return ( IsGenEBFiducial() || IsGenEEFiducial() ); }
bool Object::IsMuonFiducial     () { return bool (fabs(Eta()) < 2.1); }
bool Object::IsNULL             () { return bool ( m_raw_index < 0 ); }

