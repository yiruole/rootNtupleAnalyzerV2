#include <algorithm>
#include <cmath>
#include <iostream>

#include "LHEParticle.h"
#include "Collection.h"

bool LHEParticle::PassUserID (ID id, bool verbose){ 
  if      ( id == LHE_ELECTRON         ) { return PassUserID_LHEElectron     (verbose); }
  else return false;
}

bool LHEParticle::PassUserID_LHEElectron (bool verbose){
  if ( abs(PdgId())  != 11         ) return false;
  return true;
}
