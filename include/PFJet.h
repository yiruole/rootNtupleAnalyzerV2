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
  
  float Energy  ();
  float JECUnc  ();
  
  // Energy resolution scale factors

  float EnergyRes            ();
  float EnergyResScaleFactor ();
  float EnergyResScaleError  ();
  float EnergyScaleFactor    ();
  
  // IDs 
  
  bool   PassUserID ( ID id, bool verbose = false );
  int    JetID();
  
  // ID variables
  
  float NeutralHadronEnergyFraction ();
  float NeutralEmEnergyFraction     ();
  int    NeutralHadronMultiplicity   ();
  int    NeutralMultiplicity         ();
  int    NConstituents               ();
  float ChargedHadronEnergyFraction ();
  int    ChargedMultiplicity         ();
  float ChargedEmEnergyFraction     ();
  
  // BTag variables
  
  //float CombinedSecondaryVertexBTag ();
  float CombinedInclusiveSecondaryVertexBTag();
  float CombinedMVABTag();
  float DeepCSVBTag();
  
 private:
  bool PassUserID_PFJetLoose (bool verbose);
  bool PassUserID_PFJetMedium(bool verbose);
  bool PassUserID_PFJetTight (bool verbose);

};

std::ostream& operator<< (std::ostream& stream, PFJet& object);

#endif
