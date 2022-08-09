#include <algorithm>
#include <cmath>

#include "Electron.h"
#include "IDTypes.h"

bool Electron::PassUserID (ID id, bool verbose){ 
  if      ( id == HEEP61                       ) return PassUserID_HEEPv6p1          (verbose);
  else if ( id == HEEP70                       ) return PassUserID_BuiltIn_HEEPv7p0  (verbose);
  else if ( id == HEEP70_MANUAL                ) return PassUserID_HEEP              (verbose);
  else if ( id == HEEP70_2018                  ) return PassUserID_HEEP_2018         (verbose);
  else if ( id == EGAMMA_BUILTIN_TIGHT         ) return PassUserID_BuiltIn_EGamma    (EGAMMA_TIGHT );
  else if ( id == EGAMMA_BUILTIN_MEDIUM        ) return PassUserID_BuiltIn_EGamma    (EGAMMA_MEDIUM);
  else if ( id == EGAMMA_BUILTIN_LOOSE         ) return PassUserID_BuiltIn_EGamma    (EGAMMA_LOOSE );
  else if ( id == EGAMMA_LOOSE_HEEPETACUT      ) return PassUserID_BuiltIn_EGamma    (EGAMMA_LOOSE) && PassHEEPIDCut(HEEPIDCut::GsfEleSCEtaMultiRangeCut);
  else if ( id == EGAMMA_BUILTIN_VETO          ) return PassUserID_BuiltIn_EGamma    (EGAMMA_VETO  );
  else if ( id == EGAMMA_TIGHT                 ) return PassUserID_EGamma            (EGAMMA_TIGHT , verbose);
  else if ( id == EGAMMA_MEDIUM                ) return PassUserID_EGamma            (EGAMMA_MEDIUM, verbose);
  else if ( id == EGAMMA_LOOSE                 ) return PassUserID_EGamma            (EGAMMA_LOOSE , verbose);
  else if ( id == EGAMMA_VETO                  ) return PassUserID_EGamma            (EGAMMA_VETO  , verbose);
  else if ( id == MVA                          ) return PassUserID_MVA               (verbose);
  else if ( id == ECAL_FIDUCIAL                ) return PassUserID_ECALFiducial      (verbose);
  else if ( id == FAKE_RATE_HEEP_LOOSE         ) return PassUserID_FakeRateLooseID(verbose);
  else if ( id == FAKE_RATE_VERY_LOOSE         ) return PassUserID_FakeRateVeryLooseID(verbose);
  else if ( id == FAKE_RATE_EGMLOOSE           ) return PassUserID_FakeRateEGMLooseID(verbose);
  else if ( id == FAKE_RATE_VERY_LOOSE_EGMLOOSE) return PassUserID_FakeRateVeryLooseEGMLooseID(verbose);
  else return false;
}

bool Electron::PassUserID_ECALFiducial (bool verbose){
  if ( IsEBFiducial() || IsEEFiducial() ) return true;
  else return false;
}

bool Electron::PassUserID_BuiltIn_HEEPv7p0(bool verbose) {
  return PassHEEPID();
}

bool Electron::PassUserID_HEEP (bool verbose){

  // See: https://twiki.cern.ch/twiki/bin/viewauth/CMS/HEEPElectronIdentificationRun2
  // apply cuts manually based on variables here
  // this is version 7.0

  //----------------------------------------------------------------------
  //  Bools that are the same whether barrel or endcap
  //----------------------------------------------------------------------
  
  bool pass_et            = PassHEEPIDCut(HEEPIDCut::MinPtCut);
  bool pass_scEta         = PassHEEPIDCut(HEEPIDCut::GsfEleSCEtaMultiRangeCut);
  bool pass_ecalDriven    = PassHEEPIDCut(HEEPIDCut::GsfEleEcalDrivenCut);
  bool pass_deltaPhi      = PassHEEPIDCut(HEEPIDCut::GsfEleDPhiInCut);
  bool pass_missingHits   = PassHEEPIDCut(HEEPIDCut::GsfEleMissingHitsCut);
  bool pass_trkIsolation  = PassHEEPIDCut(HEEPIDCut::GsfEleTrkPtIsoCut);
  bool pass_deltaEtaSeed      = PassHEEPIDCut(HEEPIDCut::GsfEleDEtaInSeedCut);
  bool pass_hoe               = PassHEEPIDCut(HEEPIDCut::GsfEleHadronicOverEMLinearCut);
  bool pass_sigmaIEtaIEta     = PassHEEPIDCut(HEEPIDCut::GsfEleFull5x5SigmaIEtaIEtaWithSatCut);
  bool pass_caloIsolation     = PassHEEPIDCut(HEEPIDCut::GsfEleEmHadD1IsoRhoCut);
  bool pass_dxy               = PassHEEPIDCut(HEEPIDCut::GsfEleDxyCut);
  bool pass_shape             = PassHEEPIDCut(HEEPIDCut::GsfEleFull5x5E2x5OverE5x5WithSatCut);

  bool cutByCutDecision = (pass_et            && 
       pass_scEta         &&
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
  bool decision = PassUserID_BuiltIn_HEEPv7p0(verbose);
  assert(cutByCutDecision==decision);

  if ( verbose ) {
    if ( decision )
      std::cout << "Electron #" << m_raw_index << " PASS HEEPID" << std::endl;
    else
      std::cout << "Electron #" << m_raw_index << " FAIL HEEPID" << std::endl;
    if ( !pass_et            ) std::cout << "\tFAIL et            :";
    else                       std::cout << "\tpass et            :";
    std::cout<< Pt() << std::endl;
    if ( !pass_ecalDriven    ) std::cout << "\tFAIL ecalDriven    " << std::endl;
    else                       std::cout << "\tpass ecalDriven    " << std::endl;
    if ( !pass_deltaEtaSeed  ) std::cout << "\tFAIL deltaEtaSeed  " << std::endl;
    else                       std::cout << "\tpass deltaEtaSeed  " << std::endl;
    if ( !pass_deltaPhi      ) std::cout << "\tFAIL deltaPhi      " << std::endl;
    else                       std::cout << "\tpass deltaPhi      " << std::endl;
    if ( !pass_hoe           ) std::cout << "\tFAIL hoe           :";
    else                       std::cout << "\tpass hoe           :";
      std::cout << HoE() << std::endl;
    if ( !pass_sigmaIEtaIEta ) std::cout << "\tFAIL sigmaIEtaIEta :";
    else                       std::cout << "\tpass sigmaIEtaIEta :";
    std::cout << Full5x5SigmaIEtaIEta() << std::endl;
    if ( !pass_shape         ) std::cout << "\tFAIL shape         " << std::endl; 
    else                       std::cout << "\tpass shape         " << std::endl; 
    if ( !pass_dxy           ) std::cout << "\tFAIL dxy           :"; 
    else                       std::cout << "\tpass dxy           :"; 
    std::cout << LeadVtxDistXY() << std::endl;
    if ( !pass_missingHits   ) std::cout << "\tFAIL missingHits   :"; 
    else                       std::cout << "\tpass missingHits   :"; 
    std::cout << MissingHits() << std::endl;
    if ( !pass_trkIsolation  ) std::cout << "\tFAIL trkIsolation  :"; 
    else                       std::cout << "\tpass trkIsolation  :"; 
    std::cout << HEEP70TrackIsolation() << std::endl;
    if ( !pass_caloIsolation ) std::cout << "\tFAIL caloIsolation :"; 
    else                       std::cout << "\tpass caloIsolation :"; 
    std::cout << HEEPCaloIsolation() << std::endl;
  }
  
  return decision;
}

bool Electron::PassUserID_HEEP_2018 (bool verbose){

  // See: https://twiki.cern.ch/twiki/bin/view/CMS/EgammaRunIIRecommendations#HEEPv7_0_2018Prompt
  // apply cuts manually based on variables here
  // this is version 7.0-2018Prompt, as of 15 Apr 2020

  if ( fabs(SCEta()) < 1.5 )
    return PassUserID_BuiltIn_HEEPv7p0(verbose);

  //----------------------------------------------------------------------
  //  Cuts that are the same
  //----------------------------------------------------------------------
  
  bool pass_et            = PassHEEPIDCut(HEEPIDCut::MinPtCut);
  bool pass_scEta         = PassHEEPIDCut(HEEPIDCut::GsfEleSCEtaMultiRangeCut);
  bool pass_ecalDriven    = PassHEEPIDCut(HEEPIDCut::GsfEleEcalDrivenCut);
  bool pass_deltaPhi      = PassHEEPIDCut(HEEPIDCut::GsfEleDPhiInCut);
  bool pass_missingHits   = PassHEEPIDCut(HEEPIDCut::GsfEleMissingHitsCut);
  bool pass_trkIsolation  = PassHEEPIDCut(HEEPIDCut::GsfEleTrkPtIsoCut);
  bool pass_deltaEtaSeed      = PassHEEPIDCut(HEEPIDCut::GsfEleDEtaInSeedCut);
  //bool pass_hoe               = PassHEEPIDCut(HEEPIDCut::GsfEleHadronicOverEMLinearCut);
  bool pass_sigmaIEtaIEta     = PassHEEPIDCut(HEEPIDCut::GsfEleFull5x5SigmaIEtaIEtaWithSatCut);
  //bool pass_caloIsolation     = PassHEEPIDCut(HEEPIDCut::GsfEleEmHadD1IsoRhoCut);
  bool pass_dxy               = PassHEEPIDCut(HEEPIDCut::GsfEleDxyCut);
  bool pass_shape             = PassHEEPIDCut(HEEPIDCut::GsfEleFull5x5E2x5OverE5x5WithSatCut);

  //float energy = Pt() * cosh(SCEta());  // using corrected quantities here, probably OK
  //bool pass_hoe               = bool ( HoE()            < (-0.4+0.4*fabs(SCEta()))*RhoForHEEP()/energy + 0.05 );
  bool pass_hoe = PassHEEPGsfEleHadronicOverEMLinearCut2018();
  //float caloIsolation = EcalIsoDR03() + HcalIsoD1DR03();
  //bool pass_caloIsolation = false;

  //if   ( Pt()  < 50 ) {
  //  pass_caloIsolation = bool ( caloIsolation < ( 2.5 + 
	//				    ( (0.15+0.07*fabs(SCEta())) * RhoForHEEP() ) ) );
  //}
  //else                { 
  //  pass_caloIsolation = bool ( caloIsolation < ( 2.5 + 
	//				    ( (0.15+0.07*fabs(SCEta())) * RhoForHEEP() ) +
	//				    ( 0.03 * (Pt() - 50.0 ) ) ) );
  //}
  bool pass_caloIsolation = PassHEEPGsfEleEmHadD1IsoRhoCut2018();

  bool decision = (pass_et && 
       pass_scEta         &&
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
    if ( decision )
      std::cout << "Electron #" << m_raw_index << " PASS HEEPIDv7.0-2018Prompt" << std::endl;
    else
      std::cout << "Electron #" << m_raw_index << " FAIL HEEPIDv7.0-2018Prompt" << std::endl;
    if ( !pass_et            ) std::cout << "\tFAIL et            :";
    else                       std::cout << "\tpass et            :";
    std::cout<< Pt() << std::endl;
    if ( !pass_ecalDriven    ) std::cout << "\tFAIL ecalDriven    " << std::endl;
    else                       std::cout << "\tpass ecalDriven    " << std::endl;
    if ( !pass_deltaEtaSeed  ) std::cout << "\tFAIL deltaEtaSeed  " << std::endl;
    else                       std::cout << "\tpass deltaEtaSeed  " << std::endl;
    if ( !pass_deltaPhi      ) std::cout << "\tFAIL deltaPhi      " << std::endl;
    else                       std::cout << "\tpass deltaPhi      " << std::endl;
    if ( !pass_hoe           ) std::cout << "\tFAIL hoe           :";
    else                       std::cout << "\tpass hoe           :";
      std::cout << HoE() << std::endl;
    if ( !pass_sigmaIEtaIEta ) std::cout << "\tFAIL sigmaIEtaIEta :";
    else                       std::cout << "\tpass sigmaIEtaIEta :";
    std::cout << Full5x5SigmaIEtaIEta() << std::endl;
    if ( !pass_shape         ) std::cout << "\tFAIL shape         " << std::endl; 
    else                       std::cout << "\tpass shape         " << std::endl; 
    if ( !pass_dxy           ) std::cout << "\tFAIL dxy           :"; 
    else                       std::cout << "\tpass dxy           :"; 
    std::cout << LeadVtxDistXY() << std::endl;
    if ( !pass_missingHits   ) std::cout << "\tFAIL missingHits   :"; 
    else                       std::cout << "\tpass missingHits   :"; 
    std::cout << MissingHits() << std::endl;
    if ( !pass_trkIsolation  ) std::cout << "\tFAIL trkIsolation  :"; 
    else                       std::cout << "\tpass trkIsolation  :"; 
    std::cout << HEEP70TrackIsolation() << std::endl;
    if ( !pass_caloIsolation ) std::cout << "\tFAIL caloIsolation :"; 
    else                       std::cout << "\tpass caloIsolation :"; 
    std::cout << HEEPCaloIsolation() << std::endl;
  }
  
  return decision;
}

bool Electron::PassUserID_HEEPv6p1 (bool verbose){
  return false;
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
  return false;
}

bool Electron::PassUserID_MVA (bool verbose){
  return false;
}

bool Electron::PassUserID_FakeRateLooseID(bool verbose){
  bool pass_ecalDriven    = PassHEEPIDCut(HEEPIDCut::GsfEleEcalDrivenCut);
  bool pass_missingHits   = PassHEEPIDCut(HEEPIDCut::GsfEleMissingHitsCut);
  bool pass_dxy           = PassHEEPIDCut(HEEPIDCut::GsfEleDxyCut);
  bool pass_scEta         = PassHEEPIDCut(HEEPIDCut::GsfEleSCEtaMultiRangeCut);
  bool pass_sigmaIEtaIEta = false;
  bool pass_hoe           = false;
  bool is_barrel = false;
  bool is_endcap = false;


  float hoe = HoE();
  //XXX SIC remove energy corrections
  //hoe *= (Pt()/SCPt());
  hoe *= ECorr();

  if ( fabs(SCEta()) < 1.5 ){
    is_barrel = true;
    pass_sigmaIEtaIEta    = bool ( Full5x5SigmaIEtaIEta()       < 0.013 );
    pass_hoe              = bool ( hoe                 < 0.15  );
  }

  else if ( pass_scEta ){
    is_endcap = true;
    pass_sigmaIEtaIEta    = bool ( Full5x5SigmaIEtaIEta()       < 0.034 );
    pass_hoe              = bool ( hoe                 < 0.10  );
  }

  bool decision = ( pass_ecalDriven    && 
        pass_scEta         &&
		    pass_missingHits   && 
		    pass_dxy           && 
		    pass_sigmaIEtaIEta && 
		    pass_hoe           );
  
  
  if ( verbose ) { 
    std::cout << std::endl;
    if ( !decision ){
      std::cout << "\t\t\tElectron #" << m_raw_index << " Eta: " << Eta() << " Phi: " << Phi() << " Pt: " << Pt() << std::endl;
      std::cout << "\t\t\tElectron #" << m_raw_index << " FAIL FakeRateLooseID" << std::endl; 
      if ( !pass_ecalDriven    ) std::cout << "\t\t\tfail ecalDriven    " << std::endl;
      if ( !pass_missingHits   ) std::cout << "\t\t\tfail missingHits   :\t " << MissingHits()   << std::endl;
      if ( !pass_dxy           ) std::cout << "\t\t\tfail dxy           :\t " << LeadVtxDistXY() << std::endl;
      if ( !pass_sigmaIEtaIEta ) std::cout << "\t\t\tfail sigmaIEtaIEta :\t " << Full5x5SigmaIEtaIEta() << std::endl;
      if ( !pass_hoe           ) std::cout << "\t\t\tfail hoe           :\t " << HoE()           << std::endl;
    }
    else { 
      std::cout << "\t\t\tElectron #" << m_raw_index << " Eta: " << Eta() << " Phi: " << Phi() << " Pt: " << Pt() << std::endl;
      std::cout << "\t\t\tElectron #" << m_raw_index << " PASS FakeRateLooseID" << std::endl; 
    }
  }
  
  return decision;

}

bool Electron::PassUserID_FakeRateVeryLooseID(bool verbose){
  bool pass_ecalDriven    = PassHEEPIDCut(HEEPIDCut::GsfEleEcalDrivenCut);

  float hoe = HoE();
  //XXX SIC remove energy corrections
  //hoe *= (Pt()/SCPt());
  hoe *= ECorr();

  bool pass_hoe              = bool ( hoe                 < 0.15  );

  bool decision = ( pass_ecalDriven    && 
		    pass_hoe           );
  
  
  if ( verbose ) { 
    std::cout << std::endl;
    if ( !decision ){
      std::cout << "\t\t\tElectron #" << m_raw_index << " Eta: " << Eta() << " Phi: " << Phi() << " Pt: " << Pt() << std::endl;
      std::cout << "\t\t\tElectron #" << m_raw_index << " FAIL FakeRateVeryLooseID" << std::endl; 
      if ( !pass_ecalDriven    ) std::cout << "\t\t\tfail ecalDriven    " << std::endl;
      if ( !pass_hoe           ) std::cout << "\t\t\tfail hoe           :\t " << HoE()           << std::endl;
    }
    else { 
      std::cout << "\t\t\tElectron #" << m_raw_index << " Eta: " << Eta() << " Phi: " << Phi() << " Pt: " << Pt() << std::endl;
      std::cout << "\t\t\tElectron #" << m_raw_index << " PASS FakeRateVeryLooseID" << std::endl; 
    }
  }
  return decision;
}

bool Electron::PassUserID_FakeRateEGMLooseID(bool verbose){
  bool pass_missingHits   = PassEGammaIDLooseGsfEleMissingHitsCut();
  bool pass_sigmaIEtaIEta = false;
  bool pass_hoe           = false;
  bool is_barrel = false;
  bool is_endcap = false;


  float hoe = HoE();
  //XXX SIC remove energy corrections
  //hoe *= (Pt()/SCPt());
  hoe *= ECorr();

  if ( fabs(SCEta()) < 1.479 ){
    is_barrel = true;
    pass_sigmaIEtaIEta    = bool ( Full5x5SigmaIEtaIEta()       < 0.013 );
    pass_hoe              = bool ( hoe                 < 0.15  );
  }
  else {
    is_endcap = true;
    pass_sigmaIEtaIEta    = bool ( Full5x5SigmaIEtaIEta()       < 0.0425 );
    pass_hoe              = bool ( hoe                 < 0.10  );
  }

  bool decision = (
		    pass_missingHits   && 
		    pass_sigmaIEtaIEta && 
		    pass_hoe           );
  
  
  if ( verbose ) { 
    std::cout << std::endl;
    if ( !decision ){
      std::cout << "\t\t\tElectron #" << m_raw_index << " Eta: " << Eta() << " Phi: " << Phi() << " Pt: " << Pt() << std::endl;
      std::cout << "\t\t\tElectron #" << m_raw_index << " FAIL FakeRateEGMLooseID" << std::endl; 
      if ( !pass_missingHits   ) std::cout << "\t\t\tfail missingHits   :\t " << MissingHits()   << std::endl;
      if ( !pass_sigmaIEtaIEta ) std::cout << "\t\t\tfail sigmaIEtaIEta :\t " << Full5x5SigmaIEtaIEta() << std::endl;
      if ( !pass_hoe           ) std::cout << "\t\t\tfail hoe           :\t " << HoE()           << std::endl;
    }
    else { 
      std::cout << "\t\t\tElectron #" << m_raw_index << " Eta: " << Eta() << " Phi: " << Phi() << " Pt: " << Pt() << std::endl;
      std::cout << "\t\t\tElectron #" << m_raw_index << " PASS FakeRateLooseID" << std::endl; 
    }
  }
  
  return decision;

}

bool Electron::PassUserID_FakeRateVeryLooseEGMLooseID(bool verbose){
  float hoe = HoE();
  //XXX SIC remove energy corrections
  //hoe *= (Pt()/SCPt());
  hoe *= ECorr();

  bool pass_hoe              = bool ( hoe                 < 0.15  );

  bool decision = ( pass_hoe );
  
  
  if ( verbose ) { 
    std::cout << std::endl;
    if ( !decision ){
      std::cout << "\t\t\tElectron #" << m_raw_index << " Eta: " << Eta() << " Phi: " << Phi() << " Pt: " << Pt() << std::endl;
      std::cout << "\t\t\tElectron #" << m_raw_index << " FAIL FakeRateVeryLooseEGMLooseID" << std::endl; 
      if ( !pass_hoe           ) std::cout << "\t\t\tfail hoe           :\t " << HoE()           << std::endl;
    }
    else { 
      std::cout << "\t\t\tElectron #" << m_raw_index << " Eta: " << Eta() << " Phi: " << Phi() << " Pt: " << Pt() << std::endl;
      std::cout << "\t\t\tElectron #" << m_raw_index << " PASS FakeRateVeryLooseEGMLooseID" << std::endl; 
    }
  }
  return decision;
}
