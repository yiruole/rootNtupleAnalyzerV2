#include <algorithm>
#include <cmath>

#include "Electron.h"
#include "IDTypes.h"

bool Electron::PassUserID (ID id, bool verbose){ 
  if      ( id == HEEP60                ) return PassUserID_BuiltIn_HEEPv6p0  ();
  else if ( id == HEEP51                ) return PassUserID_HEEP              (verbose);
  else if ( id == EGAMMA_BUILTIN_TIGHT  ) return PassUserID_BuiltIn_EGamma    (EGAMMA_TIGHT );
  else if ( id == EGAMMA_BUILTIN_MEDIUM ) return PassUserID_BuiltIn_EGamma    (EGAMMA_MEDIUM);
  else if ( id == EGAMMA_BUILTIN_LOOSE  ) return PassUserID_BuiltIn_EGamma    (EGAMMA_LOOSE );
  else if ( id == EGAMMA_BUILTIN_VETO   ) return PassUserID_BuiltIn_EGamma    (EGAMMA_VETO  );
  else if ( id == EGAMMA_TIGHT          ) return PassUserID_EGamma            (EGAMMA_TIGHT , verbose);
  else if ( id == EGAMMA_MEDIUM         ) return PassUserID_EGamma            (EGAMMA_MEDIUM, verbose);
  else if ( id == EGAMMA_LOOSE          ) return PassUserID_EGamma            (EGAMMA_LOOSE , verbose);
  else if ( id == EGAMMA_VETO           ) return PassUserID_EGamma            (EGAMMA_VETO  , verbose);
  else if ( id == MVA                   ) return PassUserID_MVA               (verbose);
  else if ( id == ECAL_FIDUCIAL         ) return PassUserID_ECALFiducial      (verbose);
  else if ( id == FAKE_RATE_HEEP_LOOSE  ) return PassUserID_FakeRateLooseID(verbose);
  else return false;
}

bool Electron::PassUserID_ECALFiducial (bool verbose){
  if ( IsEBFiducial() || IsEEFiducial() ) return true;
  else return false;
}

bool Electron::PassUserID_BuiltIn_HEEPv6p0 (){
  return PassHEEPID();
}


bool Electron::PassUserID_HEEP (bool verbose){
  // See: https://twiki.cern.ch/twiki/bin/viewauth/CMS/HEEPElectronIdentificationRun2
  // apply cuts manually based on variables here
  // this is version 5.1

  //----------------------------------------------------------------------
  //  Bools that are the same whether barrel or endcap
  //----------------------------------------------------------------------
  
  bool pass_et            = bool ( PtHeep()              >  35.0 );
  bool pass_ecalDriven    = bool ( EcalSeed()        == 1    );
  bool pass_deltaPhi      = bool ( fabs (DeltaPhi()) <  0.06 ); // dPhiSCTrkAtVtx
  bool pass_trkIsolation  = bool ( TrkIsoDR03()      <  5.0  );
  bool pass_missingHits   = bool ( MissingHits()     <= 1    );

  //----------------------------------------------------------------------
  // Bools that depend on barrel vs. endcap
  //----------------------------------------------------------------------
  
  bool pass_deltaEtaSeed  = false;
  bool pass_sigmaIEtaIEta = false;
  bool pass_shape         = false;
  bool pass_shape1        = false;
  bool pass_shape2        = false;
  bool pass_caloIsolation = false;
  bool pass_dxy           = false;
  bool pass_hoe           = false;
  
  double caloIsolation = EcalIsoDR03() + HcalIsoD1DR03();
  
  //----------------------------------------------------------------------
  // Barrel electrons
  //----------------------------------------------------------------------
  
  if ( fabs(SCEta()) < 1.4442 ){
    pass_deltaEtaSeed      = bool ( fabs(DeltaEtaSeed() )     < 0.004 );
    pass_hoe               = bool ( HoE()            < 2/SCEnergy() + 0.05 );
    pass_sigmaIEtaIEta     = true;
    pass_shape1            = bool ( Full5x5E1x5OverE5x5()        > 0.83  );
    pass_shape2            = bool ( Full5x5E2x5OverE5x5()        > 0.94  );
    pass_shape             = bool ( pass_shape1 || pass_shape2    );
    pass_caloIsolation     = bool ( caloIsolation < ( 2.0 + ( 0.03 * Pt() ) + (0.28 * RhoForHEEP() ) ) );
    pass_dxy               = bool ( fabs(LeadVtxDistXY()) < 0.02  );
  }
  
  //----------------------------------------------------------------------
  // Endcap electrons
  //----------------------------------------------------------------------
  
  else if ( fabs(SCEta()) > 1.566 && fabs(SCEta()) < 2.5 ){ 
    pass_deltaEtaSeed      = bool ( fabs (DeltaEtaSeed())     < 0.006 );
    pass_hoe               = bool ( HoE()            < 12.5/SCEnergy() + 0.05 );
    pass_sigmaIEtaIEta     = bool ( Full5x5SigmaIEtaIEta()       < 0.03  );
    pass_shape             = true;
    if   ( Pt()  < 50 ) {
      pass_caloIsolation = bool ( caloIsolation < ( 2.5 + 
						    ( 0.28 * RhoForHEEP() ) ) );
    }
    else                { 
      pass_caloIsolation = bool ( caloIsolation < ( 2.5 + 
						    ( 0.28 * RhoForHEEP() ) + 
						    ( 0.03 * (Pt() - 50.0 ) ) ) );
    }
    pass_dxy               = bool ( fabs(LeadVtxDistXY()) < 0.05  );
  }

  bool decision = (pass_et            && 
		   pass_ecalDriven    && 
		   pass_deltaEtaSeed  && 
		   pass_deltaPhi      && 
		   pass_hoe           && 
		   pass_sigmaIEtaIEta && 
		   pass_shape         && 
		   pass_dxy           && 
		   pass_missingHits   && 
		   pass_trkIsolation  && 
		   pass_caloIsolation ); 

  if ( verbose ) {
    if ( decision ) std::cout << "Electron #" << m_raw_index << " PASS HEEPID" << std::endl;
    else { 
      std::cout << "Electron #" << m_raw_index << " FAIL HEEPID" << std::endl;
      if ( !pass_et            ) std::cout << "\tfail et            " << std::endl;
      if ( !pass_ecalDriven    ) std::cout << "\tfail ecalDriven    " << std::endl;
      if ( !pass_deltaEtaSeed  ) std::cout << "\tfail deltaEtaSeed  " << std::endl;
      if ( !pass_deltaPhi      ) std::cout << "\tfail deltaPhi      " << std::endl;
      if ( !pass_hoe           ) std::cout << "\tfail hoe           " << std::endl;
      if ( !pass_sigmaIEtaIEta ) std::cout << "\tfail sigmaIEtaIEta " << std::endl;
      if ( !pass_shape         ) std::cout << "\tfail shape         " << std::endl;
      if ( !pass_dxy           ) std::cout << "\tfail dxy           " << std::endl;
      if ( !pass_missingHits   ) std::cout << "\tfail missingHits   " << std::endl;
      if ( !pass_trkIsolation  ) std::cout << "\tfail trkIsolation  " << std::endl;
      if ( !pass_caloIsolation ) std::cout << "\tfail caloIsolation " << std::endl;
    }
  }
  
  return decision;
}

bool Electron::PassUserID_BuiltIn_EGamma (ID id){
  switch(id) {
    case EGAMMA_VETO:
      return PassEGammaIDVeto(); 
    case EGAMMA_LOOSE:
      return PassEGammaIDLoose();
    case EGAMMA_MEDIUM:
      return PassEGammaIDMedium();
    case EGAMMA_TIGHT:
      return PassEGammaIDTight();
    default:
      return false;
  }
}

bool Electron::PassUserID_EGamma ( ID id, bool verbose ){

  //----------------------------------------------------------------------
  // Barrel electron cut values
  //----------------------------------------------------------------------
  // See: https://twiki.cern.ch/twiki/bin/viewauth/CMS/CutBasedElectronIdentificationRun2
  double l_b_f5x5sieie   [4] = {0.011100, 0.010557, 0.010399, 0.010181 };
  double l_b_dEtaIn      [4] = {0.016315, 0.012442, 0.007641, 0.006574 };
  double l_b_dPhiIn      [4] = {0.252044, 0.072624, 0.032643, 0.022868 };
  double l_b_hoe         [4] = {0.345843, 0.121476, 0.060662, 0.037553 };
  double l_b_pfRelIso    [4] = {0.164369, 0.120026, 0.097213, 0.074355 };
  double l_b_ooemoop     [4] = {0.248070, 0.221803, 0.153897, 0.131191 };
  double l_b_d0          [4] = {0.060279, 0.022664, 0.011811, 0.009924 };
  double l_b_dZ          [4] = {0.800538, 0.173670, 0.070775, 0.015310 };
  int    l_b_missHits    [4] = {2,   1,   1,   1}; 

  //----------------------------------------------------------------------
  // Endcap electron cut values
  //----------------------------------------------------------------------
  double l_e_f5x5sieie   [4] = {0.033987,  0.032602,  0.029524,  0.028766 };
  double l_e_dEtaIn      [4] = {0.010671,  0.010654,  0.009285,  0.005681 };
  double l_e_dPhiIn      [4] = {0.245263,  0.145129,  0.042447,  0.032046 };
  double l_e_hoe         [4] = {0.134691,  0.131862,  0.104263,  0.081902 };
  double l_e_pfRelIso    [4] = {0.212604,  0.162914,  0.116708,  0.090185 };
  double l_e_ooemoop     [4] = {0.157160,  0.142283,  0.137468,  0.106055 };
  double l_e_d0          [4] = {0.273097,  0.097358,  0.051682,  0.027261 };
  double l_e_dZ          [4] = {0.885860,  0.198444,  0.180720,  0.147154 };
  int    l_e_missHits    [4] = {3,   1,   1,   1}; 
  
  
  //----------------------------------------------------------------------
  // Bools that depend on barrel vs. endcap
  //----------------------------------------------------------------------

  bool   pass_full5x5SigmaIetaIeta = false;
  bool   pass_deltaEta             = false;
  bool   pass_deltaPhi             = false;
  bool   pass_hoe                  = false;
  bool   pass_pfIsoWBetaOverPt     = false;
  bool   pass_ooEmooP              = false;
  bool   pass_vtxDistXY            = false; // aka d0
  bool   pass_vtxDistZ             = false;
  bool   pass_missingHits          = false;
  bool   pass_convVeto             = false;

  //----------------------------------------------------------------------
  // Define EGamma ep parameter
  //----------------------------------------------------------------------
  const float ecal_energy_inverse = 1.0/EcalEnergy();
  const float eSCoverP = ESuperClusterOverP();
  const float ooEmooP = std::abs(1.0 - eSCoverP)*ecal_energy_inverse;

  //----------------------------------------------------------------------
  // Define DeltaBeta PF Isolation
  //----------------------------------------------------------------------
  double ptCutoff = 20.0;
  double deltaBetaConstant = 0.5;
  bool relativeIso = true;
  //
  const float chad = PFChargedHadronIso03();
  const float nhad = PFNeutralHadronIso03();
  const float pho = PFPhotonIso03();
  const float puchad = PFPUIso03();
  float iso = chad + std::max(0.0, nhad + pho - deltaBetaConstant*puchad);
  if(relativeIso) iso /= Pt();
  
  //----------------------------------------------------------------------
  // Barrel electron test
  //----------------------------------------------------------------------

  if ( fabs(SCEta()) < 1.479 ){
    pass_full5x5SigmaIetaIeta = bool ( Full5x5SigmaIEtaIEta() < l_b_f5x5sieie [ id ] );
    pass_deltaEta             = bool ( fabs(DeltaEta())       < l_b_dEtaIn    [ id ] );
    pass_deltaPhi             = bool ( fabs(DeltaPhi())       < l_b_dPhiIn    [ id ] );
    pass_hoe                  = bool ( HoE()                  < l_b_hoe       [ id ] );
    pass_pfIsoWBetaOverPt     = bool ( ooEmooP                < l_b_ooemoop   [ id ] );
    pass_ooEmooP              = bool ( iso                    < l_b_pfRelIso  [ id ] );
    pass_vtxDistXY            = bool ( fabs(VtxDistXY())      < l_b_d0        [ id ] );
    pass_vtxDistZ             = bool ( fabs(VtxDistZ ())      < l_b_dZ        [ id ] );
    pass_missingHits          = bool ( MissingHits()          < l_b_missHits  [ id ] );
    pass_convVeto             = ! HasMatchedConvPhot();
  } 

  //----------------------------------------------------------------------
  // Endcap electron test
  //----------------------------------------------------------------------

  else if ( fabs(SCEta()) > 1.479 && fabs(SCEta()) < 2.5 ){ 
    pass_full5x5SigmaIetaIeta = bool ( Full5x5SigmaIEtaIEta() < l_e_f5x5sieie [ id ] );
    pass_deltaEta             = bool ( fabs(DeltaEta())       < l_e_dEtaIn    [ id ] );
    pass_deltaPhi             = bool ( fabs(DeltaPhi())       < l_e_dPhiIn    [ id ] );
    pass_hoe                  = bool ( HoE()                  < l_e_hoe       [ id ] );
    pass_pfIsoWBetaOverPt     = bool ( ooEmooP                < l_e_ooemoop   [ id ] );
    pass_ooEmooP              = bool ( iso                    < l_e_pfRelIso  [ id ] );
    pass_vtxDistXY            = bool ( fabs(VtxDistXY())      < l_e_d0        [ id ] );
    pass_vtxDistZ             = bool ( fabs(VtxDistZ ())      < l_e_dZ        [ id ] );
    pass_missingHits          = bool ( MissingHits()          < l_e_missHits  [ id ] );
    pass_convVeto             = ! HasMatchedConvPhot();
  }

  bool decision = ( 
    pass_full5x5SigmaIetaIeta && 
    pass_deltaEta             && 
    pass_deltaPhi             && 
    pass_hoe                  && 
    pass_pfIsoWBetaOverPt     && 
    pass_ooEmooP              && 
    pass_vtxDistXY            && 
    pass_vtxDistZ             && 
    pass_missingHits          && 
    pass_convVeto             );
  
  return decision;
  
}

bool Electron::PassUserID_MVA (bool verbose){
  return false;
}

bool Electron::PassUserID_FakeRateLooseID(bool verbose){
  bool pass_ecalDriven    = bool ( EcalSeed()    == 1    );
  bool pass_missingHits   = bool ( MissingHits() <= 1    );
  bool pass_dxy           = false;
  bool pass_sigmaIEtaIEta = false;
  bool pass_hoe           = false;
  bool is_barrel = false;
  bool is_endcap = false;

  if ( fabs(Eta()) < 1.4442 ){
    is_barrel = true;
    pass_dxy              = bool ( fabs(LeadVtxDistXY()) < 0.02  );
    pass_sigmaIEtaIEta    = bool ( SigmaIEtaIEta()       < 0.013 );
    pass_hoe              = bool ( HoE()                 < 0.15  );
  }
  
  else if ( fabs(Eta()) > 1.566 && fabs(Eta()) < 2.5 ){ 
    is_endcap = true;
    pass_dxy              = bool ( fabs(LeadVtxDistXY()) < 0.05  );
    pass_sigmaIEtaIEta    = bool ( SigmaIEtaIEta()       < 0.034 );
    pass_hoe              = bool ( HoE()                 < 0.10  );
  }
  
  bool decision = ( pass_ecalDriven    && 
		    pass_missingHits   && 
		    pass_dxy           && 
		    pass_sigmaIEtaIEta && 
		    pass_hoe           );
  
  
  if ( verbose ) { 
    std::cout << std::endl;
    if ( !decision ){
      if      ( is_barrel ) std::cout << "\t\t\tElectron #" << m_raw_index << " (barrel) FAIL FakeRateLooseID" << std::endl; 
      else if ( is_endcap ) std::cout << "\t\t\tElectron #" << m_raw_index << " (endcap) FAIL FakeRateLooseID" << std::endl; 
      else                  std::cout << "\t\t\tElectron #" << m_raw_index << " (nonfid) FAIL FakeRateLooseID" << std::endl; 
      if ( is_barrel || is_endcap ) { 
	if ( !pass_ecalDriven    ) std::cout << "\t\t\tfail ecalDriven    :\t " << EcalSeed()      << std::endl;
	if ( !pass_missingHits   ) std::cout << "\t\t\tfail missingHits   :\t " << MissingHits()   << std::endl;
	if ( !pass_dxy           ) std::cout << "\t\t\tfail dxy           :\t " << LeadVtxDistXY() << std::endl;
	if ( !pass_sigmaIEtaIEta ) std::cout << "\t\t\tfail sigmaIEtaIEta :\t " << SigmaIEtaIEta() << std::endl;
	if ( !pass_hoe           ) std::cout << "\t\t\tfail hoe           :\t " << HoE()           << std::endl;
      }
      else std::cout << "\t\t\tfail eta(fiducial) :\t " << Eta()      << std::endl;
    }
    else { 
      if      ( is_barrel ) std::cout << "\t\t\tElectron #" << m_raw_index << " (barrel) PASS FakeRateLooseID" << std::endl; 
      else if ( is_endcap ) std::cout << "\t\t\tElectron #" << m_raw_index << " (endcap) PASS FakeRateLooseID" << std::endl; 
      else                  std::cout << "\t\t\tElectron #" << m_raw_index << " (nonfid) PASS FakeRateLooseID" << std::endl;  
    }
  }
  
  return decision;

}
