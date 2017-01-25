#include <algorithm>
#include <cmath>

#include "PFJet.h"
#include "IDTypes.h"

// see: https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVRun2016
// Jan. 2017: updated |eta| > 2.7 regions with new variables
// but no medium working point defined

bool PFJet::PassUserID (ID id, bool verbose){ 
  if      ( id == PFJET_LOOSE  ) return PassUserID_PFJetLoose  (verbose);
  else if ( id == PFJET_MEDIUM ) return PassUserID_PFJetMedium (verbose);
  else if ( id == PFJET_TIGHT  ) return PassUserID_PFJetTight  (verbose);
  else return false;
}

bool PFJet::PassUserID_PFJetLoose ( bool verbose ){
  
  bool decision = false;

  if ( fabs ( Eta() ) < 2.7 ) {
    bool pass_neutralhadFraction  = bool ( NeutralHadronEnergyFraction () < 0.99 );
    bool pass_neutralEMFraction   = bool ( NeutralEmEnergyFraction     () < 0.99 );
    bool pass_nConstituents       = bool ( NConstituents               () > 1    );
    bool pass_chargedHadFraction  = true;
    bool pass_chargedMultiplicity = true;
    bool pass_chargedEMFraction   = true;
    if( fabs ( Eta() ) < 2.4 ) {
      pass_chargedHadFraction  = bool ( ChargedHadronEnergyFraction() > 0.0  );
      pass_chargedMultiplicity = bool ( ChargedMultiplicity        () > 0    );
      pass_chargedEMFraction   = bool ( ChargedEmEnergyFraction    () < 0.99 );
    }
    decision = (
        pass_neutralhadFraction  && 
        pass_neutralEMFraction   && 
        pass_nConstituents       &&
        pass_chargedHadFraction  && 
        pass_chargedMultiplicity && 
        pass_chargedEMFraction );
  }
  else if ( fabs ( Eta() ) <= 3.0 && fabs ( Eta() ) > 2.7) {
    bool pass_neutralEMFraction      = bool ( NeutralEmEnergyFraction    () > 0.01 );
    bool pass_neutralhadFraction     = bool ( NeutralHadronEnergyFraction() < 0.98 );
    bool pass_neutralMultiplicity    = bool ( NeutralMultiplicity        () > 2 );
    decision = (
        pass_neutralEMFraction      &&
        pass_neutralhadFraction     &&
        pass_neutralMultiplicity );
  }
  else if ( fabs ( Eta() ) > 3.0 ) {
    bool pass_neutralEMFraction      = bool ( NeutralEmEnergyFraction    () < 0.90 );
    bool pass_neutralMultiplicity    = bool ( NeutralMultiplicity() > 10 );
    decision = (
        pass_neutralEMFraction &&
        pass_neutralMultiplicity );
  }

  return decision;
  
}

// NB: this working point doesn't seem to be maintained
bool PFJet::PassUserID_PFJetMedium( bool verbose ){
  
  bool pass_chargedHadFraction_central  = true;
  bool pass_chargedEMFraction_central   = true;
  bool pass_chargedMultiplicity_central = true;
  bool pass_neutralhadFraction          = bool ( NeutralHadronEnergyFraction () < 0.95 );
  bool pass_neutralEMFraction           = bool ( NeutralEmEnergyFraction     () < 0.95 );
  bool pass_nConstituents               = bool ( NConstituents               () > 1    );
  
  if ( fabs ( Eta() ) < 2.4 ) {
    pass_chargedHadFraction_central = bool ( ChargedHadronEnergyFraction() > 0.0  );
    pass_chargedMultiplicity_central= bool ( ChargedMultiplicity        () > 0    );
    pass_chargedEMFraction_central  = bool ( ChargedEmEnergyFraction    () < 0.99 );
  }
  
  bool decision = ( pass_chargedHadFraction_central  && 
		    pass_chargedEMFraction_central   && 
		    pass_chargedMultiplicity_central && 
		    pass_neutralhadFraction          && 
		    pass_neutralEMFraction           && 
		    pass_nConstituents                );

  return decision;

}

bool PFJet::PassUserID_PFJetTight ( bool verbose ){
  
  bool decision = false;

  if ( fabs ( Eta() ) < 2.7 ) {
    bool pass_neutralhadFraction  = bool ( NeutralHadronEnergyFraction () < 0.90 );
    bool pass_neutralEMFraction   = bool ( NeutralEmEnergyFraction     () < 0.90 );
    bool pass_nConstituents       = bool ( NConstituents               () > 1    );
    bool pass_chargedHadFraction  = true;
    bool pass_chargedMultiplicity = true;
    bool pass_chargedEMFraction   = true;
    if( fabs ( Eta() ) < 2.4 ) {
      pass_chargedHadFraction  = bool ( ChargedHadronEnergyFraction() > 0.0  );
      pass_chargedMultiplicity = bool ( ChargedMultiplicity        () > 0    );
      pass_chargedEMFraction   = bool ( ChargedEmEnergyFraction    () < 0.99 );
    }
    decision = (
        pass_neutralhadFraction  && 
        pass_neutralEMFraction   && 
        pass_nConstituents       &&
        pass_chargedHadFraction  && 
        pass_chargedMultiplicity && 
        pass_chargedEMFraction );
  }
  else if ( fabs ( Eta() ) <= 3.0 && fabs ( Eta() ) > 2.7) {
    bool pass_neutralEMFraction      = bool ( NeutralEmEnergyFraction    () > 0.01 );
    bool pass_neutralhadFraction     = bool ( NeutralHadronEnergyFraction() < 0.98 );
    bool pass_neutralMultiplicity    = bool ( NeutralMultiplicity        () > 2 );
    decision = (
        pass_neutralEMFraction      &&
        pass_neutralhadFraction     &&
        pass_neutralMultiplicity );
  }
  else if ( fabs ( Eta() ) > 3.0 ) {
    bool pass_neutralEMFraction      = bool ( NeutralEmEnergyFraction    () < 0.90 );
    bool pass_neutralMultiplicity    = bool ( NeutralMultiplicity() > 10 );
    decision = (
        pass_neutralEMFraction &&
        pass_neutralMultiplicity );
  }

  return decision;

}
