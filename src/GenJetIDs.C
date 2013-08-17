#include <algorithm>
#include <cmath>

#include "GenJet.h"
#include "Collection.h"
#include "IDTypes.h"

bool GenJet::PassUserID (ID id, bool verbose) { 
  if ( verbose ) std::cout << "\t" << "all GenJets do not pass ID" << std::endl;
  return false;
}
