#ifndef PFJET_H
#define PFJET_H

#include "Object.h"
#include "IDTypes.h"
#include "Collection.h"

class PFJet : public Object { 
 public:
  PFJet ();
  PFJet (Collection& collection, unsigned int index, short j = 0);

  // Energy resolution scale factors
  float EnergyResFromCorrection(const correction::Correction* correction) override;
  float EnergyResScaleFactorFromCorrection(const correction::Correction* correction, const std::string& variation) override;
  float EnergyRes();
  float EnergyResScaleError();
  float EnergyResScaleFactor();
  float EnergyScaleFactor();
  
  // IDs 
  
  bool   PassUserID ( ID id, bool verbose = false ) override;
  int    JetID();
  
  // ID variables
  
  int    HadronFlavor();
  float NeutralHadronEnergyFraction ();
  float NeutralEmEnergyFraction     ();
  int    NConstituents               ();
  float ChargedHadronEnergyFraction ();
  float ChargedEmEnergyFraction     ();
  
  // BTag variables
  
  float DeepCSVBTag();
  float DeepJetBTag();
  
  float QuarkGluonLikelihood();
  int NElectrons();
  int NMuons();
  int MatchedGenJetIndex();
  int MatchedElectron1Index();
  int MatchedElectron2Index();

  float FixedGridRhoAll();

 private:
  bool PassUserID_PFJetLoose (bool verbose);
  bool PassUserID_PFJetMedium(bool verbose);
  bool PassUserID_PFJetTight (bool verbose);

};

std::ostream& operator<< (std::ostream& stream, PFJet& object);

#endif
