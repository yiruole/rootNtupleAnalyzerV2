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
  m_trigObj_index ( o.m_trigObj_index ),
  m_pt(o.Pt()),
  m_eta(o.Eta()),
  m_phi(o.Phi())
{}

//// in principle, could initP4 here, but only in derived class methods
//Object::Object(Collection & collection, short raw_index):
//  m_name ("NO_NAME"),
//  m_collection ( & collection ),
//  m_raw_index (raw_index),
//  m_trigObj_index (-1)
//{}
//
//// in principle, could initP4 here, but only in derived class methods
//Object::Object(Collection & collection, short raw_index, short trigObj_index):
//  m_name ("NO_NAME"),
//  m_collection ( & collection ),
//  m_raw_index (raw_index),
//  m_trigObj_index (trigObj_index)
//{}

Object::Object(Collection & collection, short raw_index, const char* name):
  m_name (name),
  m_collection ( & collection ),
  m_raw_index (raw_index),
  m_trigObj_index (-1) {
    initP4();
}

Object::Object(Collection & collection, short raw_index, short trigObj_index, const char* name):
  m_name (name),
  m_collection ( & collection ),
  m_raw_index (raw_index),
  m_trigObj_index (trigObj_index) {
    initP4();
}

void Object::initP4() {
  std::string name = Name();
  bool uncorrectPt = false;
  if(name=="PFJet")
    name = "Jet";
  else if(name=="GenParticle")
    name = "GenPart";
  else if(name=="HLTriggerObject")
    name = "TrigObj";
  else if(name=="LooseElectron") {
    name = "Electron";
    uncorrectPt = true;
  }
  m_pt = m_collection->ReadArrayBranch<Float_t>(name+"_pt",m_raw_index);
  m_originalPt = m_pt;
  m_eta = m_collection->ReadArrayBranch<Float_t>(name+"_eta",m_raw_index);
  m_phi = m_collection->ReadArrayBranch<Float_t>(name+"_phi",m_raw_index);
  if(name=="Muon")
    m_pt = m_collection->ReadArrayBranch<Float_t>("Muon_tunepRelPt", m_raw_index)*m_collection->ReadArrayBranch<Float_t>("Muon_pt", m_raw_index);
  if(uncorrectPt)
    m_pt/=m_collection->ReadArrayBranch<Float_t>(name+"_eCorr",m_raw_index);
}

float Object::DeltaR( Object * other_object ) { 
  float deta = Eta() - other_object -> Eta();
  float dphi = DeltaPhi ( other_object );
  float dr = sqrt ( deta * deta + dphi * dphi );
  return dr;
}

float Object::DeltaPhi( Object * other_object ) { 
  return reduceRange(Phi() - other_object -> Phi() );
}

float Object::DeltaPt( Object * other_object ) {
  return Pt() - other_object -> Pt();
}

bool Object::IsGenEBFiducial       () { return bool ( fabs(Eta()) < 1.4442 ); }
bool Object::IsGenEEFiducial       () { return bool ( ( fabs(Eta()) > 1.566 ) && ( fabs(Eta()) < 2.50 ) ); }
bool Object::IsGenElectronFiducial () { return ( IsGenEBFiducial() || IsGenEEFiducial() ); }
bool Object::IsMuonFiducial     () { return bool (fabs(Eta()) < 2.1); }
bool Object::IsNULL             () { return bool ( m_raw_index < 0 ); }

// reduce to [-pi,pi]
template <typename T>
constexpr T Object::reduceRange(T x) {
  constexpr T o2pi = 1. / (2. * M_PI);
  if (std::abs(x) <= T(M_PI))
    return x;
  T n = std::round(x * o2pi);
  return x - n * T(2. * M_PI);
}

