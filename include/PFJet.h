#ifndef PFJET_H
#define PFJET_H

#include "Object.h"
#include "IDTypes.h"
#include "Collection.h"

class PFJet : public Object { 
 public:
  PFJet ();
  PFJet (Collection& collection, unsigned int index, short j = 0);

  // Kinematic variables
  
  double & Pt    ();
  double & Eta   (); 
  double & Phi   (); 
  double Energy  ();
  double JECUnc  ();
  
  // Energy resolution scale factors

  double EnergyResScaleFactor ();
  double EnergyResScaleError  ();
  double EnergyScaleFactor    ();
  
  // IDs 
  
  bool   PassUserID ( ID id, bool verbose = false );
  
  // ID variables
  
  double NeutralHadronEnergyFraction ();
  double NeutralEmEnergyFraction     ();
  int    NConstituents               ();
  double ChargedHadronEnergyFraction ();
  int    ChargedMultiplicity         ();
  double ChargedEmEnergyFraction     ();
  
  // BTag variables
  
  double CombinedSecondaryVertexBTag ();
  
 private:
  bool PassUserID_PFJetLoose (bool verbose);
  bool PassUserID_PFJetMedium(bool verbose);
  bool PassUserID_PFJetTight (bool verbose);

};

std::ostream& operator<< (std::ostream& stream, PFJet& object);

#endif
