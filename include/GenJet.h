#ifndef GENJET_H
#define GENJET_H

#include "Object.h"
#include "IDTypes.h"
#include "Collection.h"

class GenJet : public Object { 

 public:

  GenJet();
  GenJet(Collection& c, unsigned short i, short j = 0);
  
  // Kinematic variables

  double & Pt()  ;
  double & Eta() ;
  double & Phi() ;

  // IDs 

  bool PassUserID ( ID id, bool verbose = false ); 
    
};

std::ostream& operator<< (std::ostream& stream, GenJet& object);

#endif
