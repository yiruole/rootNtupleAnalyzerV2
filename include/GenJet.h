#ifndef GENJET_H
#define GENJET_H

#include "Object.h"
#include "IDTypes.h"
#include "Collection.h"

class GenJet : public Object { 

 public:

  GenJet();
  GenJet(Collection& c, unsigned short i, short j = 0, Long64_t current_entry = 0);
  
  // Kinematic variables

  float & Pt()  ;
  float & Eta() ;
  float & Phi() ;

  // IDs 

  bool PassUserID ( ID id, bool verbose = false ); 

 private:
  TLeaf* ptLeaf;
  TLeaf* etaLeaf;
  TLeaf* phiLeaf;
    
};

std::ostream& operator<< (std::ostream& stream, GenJet& object);

#endif
