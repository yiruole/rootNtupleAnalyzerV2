#include <algorithm>
#include <cmath>

#include "PFJet.h"
#include "IDTypes.h"

// see: https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVRun2016
// Jan. 2017: updated |eta| > 2.7 regions with new variables
// but no medium working point defined

bool PFJet::PassUserID (ID id, bool verbose){ 
  if      ( id == PFJET_LOOSE  ) return PassUserID_PFJetLoose  (verbose);
  else if ( id == PFJET_TIGHT  ) return PassUserID_PFJetTight  (verbose);
  else return false;
}

bool PFJet::PassUserID_PFJetLoose ( bool verbose ){
  bool decision = JetID() & 0x1;
  return decision;
}


bool PFJet::PassUserID_PFJetTight ( bool verbose ){
  bool decision = (JetID() >> 1) & 0x1;
  return decision;
}
