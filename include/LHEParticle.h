#ifndef LHEPARTICLE_H
#define LHEPARTICLE_H

#include "Object.h"
#include "IDTypes.h"
#include "Collection.h"

#include <TLeaf.h>

class LHEParticle : public Object { 

 public:

  LHEParticle();
  LHEParticle(Collection& c, unsigned short i, short j = 0);
  
  // Kinematic variables
  float Mass();
  float IncomingPz();
  int Spin();

  // IDs 
  bool PassUserID ( ID id, bool verbose = false); 
  
  // ID variables  
  int PdgId       ();
  int Status      ();

 private:
  
  bool PassUserID_LHEElectron            (bool verbose);

};

std::ostream& operator<< (std::ostream& stream, LHEParticle& object);

#endif
