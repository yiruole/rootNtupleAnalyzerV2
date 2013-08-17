#include <algorithm>
#include <cmath>

#include "Electron.h"
#include "IDTypes.h"

bool Electron::PassUserID (ID id, bool verbose){ 
  if      ( id == HEEP          ) return PassUserID_HEEPv4p1       (verbose);
  else if ( id == HEEP_LOOSE    ) return PassUserID_FakeRateLooseID(verbose);
  else if ( id == EGAMMA_TIGHT  ) return PassUserID_EGamma2012     (EGAMMA_TIGHT , verbose);
  else if ( id == EGAMMA_MEDIUM ) return PassUserID_EGamma2012     (EGAMMA_MEDIUM, verbose);
  else if ( id == EGAMMA_LOOSE  ) return PassUserID_EGamma2012     (EGAMMA_LOOSE , verbose);
  else if ( id == EGAMMA_VETO   ) return PassUserID_EGamma2012     (EGAMMA_VETO  , verbose);
  else if ( id == MVA           ) return PassUserID_MVA            (verbose);
  else if ( id == ECAL_FIDUCIAL ) return PassUserID_ECALFiducial   (verbose);
  else return false;
}

bool Electron::PassUserID_ECALFiducial (bool verbose){
  if ( IsEBFiducial() || IsEEFiducial() ) return true;
  else return false;
}

bool Electron::PassUserID_HEEPv4p0 (bool verbose){
  
  //----------------------------------------------------------------------
  //  Bools that are the same whether barrel or endcap
  //----------------------------------------------------------------------
  
  bool pass_et            = bool ( Pt()              >  35.0 );
  bool pass_ecalDriven    = bool ( EcalSeed()        == 1    );
  bool pass_deltaPhi      = bool ( fabs (DeltaPhi()) <  0.06 );
  bool pass_hoe           = bool ( HoE()             <  0.05 );
  bool pass_trkIsolation  = bool ( TrkIsoDR03()      <  5.0  );
  bool pass_missingHits   = bool ( MissingHits()     == 0    );

  //----------------------------------------------------------------------
  // Bools that depend on barrel vs. endcap
  //----------------------------------------------------------------------
  
  bool pass_deltaEta      = false;
  bool pass_sigmaIEtaIEta = false;
  bool pass_shape         = false;
  bool pass_shape1        = false;
  bool pass_shape2        = false;
  bool pass_caloIsolation = false;
  
  double caloIsolation = EcalIsoDR03() + HcalIsoD1DR03();
  
  //----------------------------------------------------------------------
  // Barrel electrons
  //----------------------------------------------------------------------
  
  if ( fabs(Eta()) < 1.442 ){
    pass_sigmaIEtaIEta     = true;
    pass_deltaEta          = bool ( fabs (DeltaEta() ) < 0.005 );
    pass_shape1            = bool ( E1x5OverE5x5()     > 0.83  );
    pass_shape2            = bool ( E2x5OverE5x5()     > 0.94  );
    pass_shape             = bool ( pass_shape1 || pass_shape2 );
    pass_caloIsolation     = bool ( caloIsolation < ( 2.0 + ( 0.03 * Pt() ) + (0.28 * RhoForHEEPv4p0() ) ) );
  }
  
  //----------------------------------------------------------------------
  // Endcap electrons
  //----------------------------------------------------------------------
  
  else if ( fabs(Eta()) > 1.56 && fabs(Eta()) < 2.5 ){ 
    
    pass_deltaEta          = bool ( fabs (DeltaEta()) < 0.007 );
    pass_sigmaIEtaIEta     = bool ( SigmaIEtaIEta()   < 0.03  );
    pass_shape             = true;
    
    if   ( Pt()  < 50 ) {
      pass_caloIsolation = bool ( caloIsolation < ( 2.5 + 
						    ( 0.28 * RhoForHEEPv4p0() ) ) );
    }
    else                { 
      pass_caloIsolation = bool ( caloIsolation < ( 2.5 + 
						    ( 0.28 * RhoForHEEPv4p0() ) + 
						    ( 0.03 * (Pt() - 50.0 ) ) ) );
    }
  }

  bool decision = (pass_et            && 
		   pass_ecalDriven    && 
		   pass_deltaEta      && 
		   pass_deltaPhi      && 
		   pass_hoe           && 
		   pass_sigmaIEtaIEta && 
		   pass_shape         && 
		   pass_missingHits   && 
		   pass_trkIsolation  && 
		   pass_caloIsolation ); 

  
  
  return decision;
}


bool Electron::PassUserID_HEEPv4p1 (bool verbose){
  
  //----------------------------------------------------------------------
  //  Bools that are the same whether barrel or endcap
  //----------------------------------------------------------------------
  
  bool pass_et            = bool ( Pt()              >  35.0 );
  bool pass_ecalDriven    = bool ( EcalSeed()        == 1    );
  bool pass_deltaPhi      = bool ( fabs (DeltaPhi()) <  0.06 );
  bool pass_hoe           = bool ( HoE()             <  0.05 );
  bool pass_trkIsolation  = bool ( TrkIsoDR03()      <  5.0  );
  bool pass_missingHits   = bool ( MissingHits()     <= 1    );

  //----------------------------------------------------------------------
  // Bools that depend on barrel vs. endcap
  //----------------------------------------------------------------------
  
  bool pass_deltaEta      = false;
  bool pass_sigmaIEtaIEta = false;
  bool pass_shape         = false;
  bool pass_shape1        = false;
  bool pass_shape2        = false;
  bool pass_caloIsolation = false;
  bool pass_dxy           = false;
  
  double caloIsolation = EcalIsoDR03() + HcalIsoD1DR03();
  
  //----------------------------------------------------------------------
  // Barrel electrons
  //----------------------------------------------------------------------
  
  if ( fabs(Eta()) < 1.442 ){
    pass_sigmaIEtaIEta     = true;
    pass_dxy               = bool ( fabs(LeadVtxDistXY()) < 0.02  );
    pass_deltaEta          = bool ( fabs(DeltaEta() )     < 0.005 );
    pass_shape1            = bool ( E1x5OverE5x5()        > 0.83  );
    pass_shape2            = bool ( E2x5OverE5x5()        > 0.94  );
    pass_shape             = bool ( pass_shape1 || pass_shape2    );
    pass_caloIsolation     = bool ( caloIsolation < ( 2.0 + ( 0.03 * Pt() ) + (0.28 * RhoForHEEPv4p0() ) ) );
  }
  
  //----------------------------------------------------------------------
  // Endcap electrons
  //----------------------------------------------------------------------
  
  else if ( fabs(Eta()) > 1.56 && fabs(Eta()) < 2.5 ){ 
    
    pass_dxy               = bool ( fabs(LeadVtxDistXY()) < 0.05  );
    pass_deltaEta          = bool ( fabs (DeltaEta())     < 0.007 );
    pass_sigmaIEtaIEta     = bool ( SigmaIEtaIEta()       < 0.03  );
    pass_shape             = true;
    
    if   ( Pt()  < 50 ) {
      pass_caloIsolation = bool ( caloIsolation < ( 2.5 + 
						    ( 0.28 * RhoForHEEPv4p0() ) ) );
    }
    else                { 
      pass_caloIsolation = bool ( caloIsolation < ( 2.5 + 
						    ( 0.28 * RhoForHEEPv4p0() ) + 
						    ( 0.03 * (Pt() - 50.0 ) ) ) );
    }
  }

  bool decision = (pass_et            && 
		   pass_ecalDriven    && 
		   pass_deltaEta      && 
		   pass_deltaPhi      && 
		   pass_hoe           && 
		   pass_sigmaIEtaIEta && 
		   pass_shape         && 
		   pass_dxy           && 
		   pass_missingHits   && 
		   pass_trkIsolation  && 
		   pass_caloIsolation ); 

  if ( verbose ) {
    if ( decision ) std::cout << "Electron #" << m_raw_index << " PASS FakeRateLooseID" << std::endl;
    else { 
      std::cout << "Electron #" << m_raw_index << " FAIL FakeRateLooseID" << std::endl;
      if ( !pass_et            ) std::cout << "\tfail et            " << std::endl;
      if ( !pass_ecalDriven    ) std::cout << "\tfail ecalDriven    " << std::endl;
      if ( !pass_deltaEta      ) std::cout << "\tfail deltaEta      " << std::endl;
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


bool Electron::PassUserID_EGamma2012 ( ID id, bool verbose ){

  //----------------------------------------------------------------------
  // Barrel electron cut values
  //----------------------------------------------------------------------

  double l_b_dEtaIn  [4] = { 0.007 , 0.007, 0.004, 0.004 };
  double l_b_dPhiIn  [4] = { 0.8   , 0.15 , 0.06 , 0.03  };
  double l_b_sieie   [4] = { 0.01  , 0.01 , 0.01 , 0.01  };
  double l_b_hoe     [4] = { 0.15  , 0.12 , 0.12 , 0.12  };
  double l_b_d0      [4] = { 0.04  , 0.02 , 0.02 , 0.02  };
  double l_b_dZ      [4] = { 0.2   , 0.2  , 0.1  ,  0.1  };
  double l_b_ep      [4] = { 999.  , 0.05 , 0.05 , 0.05  };
  double l_b_pfRelIso[4] = { 0.15  , 0.15 , 0.15 , 0.10  };
  double l_b_vtxProb [4] = { 999.  , 1e-6 , 1e-6 , 1e-6  };
  int    l_b_missHits[4] = { 999   , 1    , 1    , 0     }; 

  //----------------------------------------------------------------------
  // Endcap electron cut values
  //----------------------------------------------------------------------
  
  double l_e_dEtaIn  [4] = { 0.01  , 0.009, 0.007, 0.005 };
  double l_e_dPhiIn  [4] = { 0.7   , 0.10 , 0.03 , 0.02  };
  double l_e_sieie   [4] = { 0.03  , 0.03 , 0.03 , 0.03  };
  double l_e_hoe     [4] = { 999.  , 0.10 , 0.10 , 0.10  };
  double l_e_d0      [4] = { 0.04  , 0.02 , 0.02 , 0.02  };
  double l_e_dZ      [4] = { 0.2   , 0.2  , 0.1  , 0.1   };
  double l_e_ep      [4] = { 999.  , 0.05 , 0.05 , 0.05  };
  double l_e_pfRelIso[4] = { 0.15  , 0.15 , 0.15 , 0.10  };
  double l_e_vtxProb [4] = { 999.  , 1e-6 , 1e-6 , 1e-6  };
  int    l_e_missHits[4] = { 999   , 1    , 1    , 0     };
  
  //----------------------------------------------------------------------
  // Bools that depend on barrel vs. endcap
  //----------------------------------------------------------------------

  bool   pass_deltaEta      = false;
  bool   pass_deltaPhi      = false;
  bool   pass_sigmaIEtaIEta = false;
  bool   pass_hoe           = false;
  bool   pass_vtxDistXY     = false;
  bool   pass_vtxDistZ      = false;
  bool   pass_ep            = false;
  bool   pass_pfIsolation   = false;
  bool   pass_convFitProb   = false;
  bool   pass_missingHits   = false;

  //----------------------------------------------------------------------
  // Define EGamma ep parameter
  //----------------------------------------------------------------------

  double egamma_e  = CaloEnergy();
  double egamma_p  = CaloEnergy() / ESuperClusterOverP();
  double egamma_ep = fabs ( ( 1.0 / egamma_e ) - ( 1.0 / egamma_p ) );

  //----------------------------------------------------------------------
  // Define PF Isolation
  //----------------------------------------------------------------------

  double effective_area_eta_minimums    [7] = { 0.000, 1.000, 1.479, 2.000, 2.200, 2.300, 2.400 };
  double effective_area_eta_maximums    [7] = { 1.000, 1.479, 2.000, 2.200, 2.300, 2.400, 999.0 };
  double effective_areas_04             [7] = { 0.190, 0.250, 0.120, 0.210, 0.270, 0.440, 0.520 };
  double effective_areas_03             [7] = { 0.100, 0.120, 0.085, 0.110, 0.120, 0.120, 0.130 };
  double effective_area_03  = 0.0;
  double effective_area_04  = 0.0;
  
  for (int i = 0; i < 7; ++i ){ 
    double bin_minimum = effective_area_eta_minimums[i];
    double bin_maximum = effective_area_eta_maximums[i];
    if ( fabs(Eta()) >= bin_minimum && fabs(Eta()) < bin_maximum ) {
      effective_area_03 = effective_areas_03 [i];
      effective_area_04 = effective_areas_04 [i];
    }
  }
  
  double egamma_pfiso_03 = PFChargedHadronIso03() + std::max ( PFPhotonIso03() + PFNeutralHadronIso03() - ( RhoForEGamma2012() * effective_area_03 ), 0.0 );
  double egamma_pfiso_04 = PFChargedHadronIso04() + std::max ( PFPhotonIso04() + PFNeutralHadronIso04() - ( RhoForEGamma2012() * effective_area_04 ), 0.0 );

  egamma_pfiso_03 /= Pt();
  egamma_pfiso_04 /= Pt();
  
  //----------------------------------------------------------------------
  // Barrel electron test
  //----------------------------------------------------------------------

  if ( fabs(Eta()) < 1.442 ){

    pass_deltaEta      = bool ( fabs(DeltaEta())   <= l_b_dEtaIn  [ id ] ) ;
    pass_deltaPhi      = bool ( fabs(DeltaPhi())   <= l_b_dPhiIn  [ id ] ) ;
    pass_sigmaIEtaIEta = bool ( SigmaIEtaIEta()    <= l_b_sieie   [ id ] ) ;
    pass_hoe           = bool ( HoE            ()  <= l_b_hoe     [ id ] ) ;
    pass_vtxDistXY     = bool ( fabs(VtxDistXY())  <= l_b_d0      [ id ] ) ;
    pass_vtxDistZ      = bool ( fabs(VtxDistZ ())  <= l_b_dZ      [ id ] ) ;
    pass_ep            = bool ( egamma_ep          <= l_b_ep      [ id ] ) ;
    pass_pfIsolation   = bool ( egamma_pfiso_03    <= l_b_pfRelIso[ id ] ) ;
    pass_convFitProb   = bool ( ConvFitProb  ()    <= l_b_vtxProb [ id ] ) ;
    pass_missingHits   = bool ( MissingHitsEG()    <= l_b_missHits[ id ] ) ;
    
  } 

  //----------------------------------------------------------------------
  // Endcap electron test
  //----------------------------------------------------------------------

  else if ( fabs(Eta()) > 1.56 && fabs(Eta()) < 2.5 ){ 

    pass_deltaEta      = bool ( fabs(DeltaEta())   <= l_e_dEtaIn  [ id ] ) ;
    pass_deltaPhi      = bool ( fabs(DeltaPhi())   <= l_e_dPhiIn  [ id ] ) ;
    pass_sigmaIEtaIEta = bool ( SigmaIEtaIEta()    <= l_e_sieie   [ id ] ) ;
    pass_hoe           = bool ( HoE          ()    <= l_e_hoe     [ id ] ) ;
    pass_vtxDistXY     = bool ( fabs(VtxDistXY())  <= l_e_d0      [ id ] ) ;
    pass_vtxDistZ      = bool ( fabs(VtxDistZ ())  <= l_e_dZ      [ id ] ) ;
    pass_ep            = bool ( egamma_ep          <= l_e_ep      [ id ] ) ;
    pass_pfIsolation   = bool ( egamma_pfiso_03    <= l_e_pfRelIso[ id ] ) ;
    pass_convFitProb   = bool ( ConvFitProb  ()    <= l_e_vtxProb [ id ] ) ;
    pass_missingHits   = bool ( MissingHitsEG()    <= l_e_missHits[ id ] ) ;
  }

  bool decision = ( 
		   pass_deltaEta      && 
		   pass_deltaPhi      && 
		   pass_sigmaIEtaIEta && 
		   pass_hoe           && 
		   pass_vtxDistXY     && 
		   pass_vtxDistZ      && 
		   pass_ep            && 
		   pass_pfIsolation   && 
		   pass_convFitProb   && 
		   pass_missingHits   ) ;
  
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

  if ( fabs(Eta()) < 1.442 ){
    is_barrel = true;
    pass_dxy              = bool ( fabs(LeadVtxDistXY()) < 0.02  );
    pass_sigmaIEtaIEta    = bool ( SigmaIEtaIEta()       < 0.013 );
    pass_hoe              = bool ( HoE()                 < 0.15  );
  }
  
  else if ( fabs(Eta()) > 1.56 && fabs(Eta()) < 2.5 ){ 
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
