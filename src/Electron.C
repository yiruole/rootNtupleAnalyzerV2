#include "Electron.h"
#include "Object.h"
#include "IDTypes.h"
#include "TVector3.h"

Electron::Electron ():
  Object()
  // m_rawSuperClusterPt(0.)
{}

Electron::Electron (Collection & c, unsigned short i, short j):
  Object(c,i,"Electron") {
  //if ( m_collection->ReadArrayBranch<Float_t>("Electron_") ElectronCaloEnergy -> at ( m_raw_index ) == 0. ) m_rawSuperClusterPt = 0.;
  //else { 
  //  m_rawSuperClusterPt = ( ( m_collection->ReadArrayBranch<Float_t>("Electron_") ElectronPtHeep       -> at ( m_raw_index ) ) * 
  //			    ( m_collection->ReadArrayBranch<Float_t>("Electron_") ElectronSCRawEnergy  -> at ( m_raw_index ) ) / 
  //			    ( m_collection->ReadArrayBranch<Float_t>("Electron_") ElectronCaloEnergy   -> at ( m_raw_index ) ) );
  //}
}

// Kinematic variables

float   Electron::PtHeep             (){ return CaloEnergy()/cosh(SCEta()); }
float   Electron::SCEta              (){ return m_collection->ReadArrayBranch<Float_t>("Electron_deltaEtaSC",m_raw_index)+m_collection->ReadArrayBranch<Float_t>("Electron_eta",m_raw_index); } 
float   Electron::SCSeedEta          (){ return -1.0; } 
float   Electron::SCPhi              (){ return m_collection->ReadArrayBranch<Float_t>("Electron_scPhi",m_raw_index); } 
float   Electron::SCPt               (){ return SCEnergy()/cosh(SCEta()); } 
float   Electron::IsEB               (){ return fabs(Eta()) < 1.5; } 
float   Electron::IsEE               (){ return fabs(Eta()) < 2.5; } 

float   Electron::Charge             (){ return m_collection->ReadArrayBranch<Int_t>("Electron_charge",m_raw_index); } 
float   Electron::R9                 (){ return m_collection->ReadArrayBranch<Float_t>("Electron_r9",m_raw_index); } 
float   Electron::RawEnergy          (){ return -1.0; } 
float   Electron::SCEnergy           (){ return m_collection->ReadArrayBranch<Float_t>("Electron_scEnergy",m_raw_index);} 
// ratio of the calibrated energy/miniaod energy
float   Electron::ECorr              (){ return m_collection->ReadArrayBranch<Float_t>("Electron_eCorr",m_raw_index);} 
								      
// EGamma bits													      
int    Electron::PassEGammaIDLoose    (){ return m_collection->ReadArrayBranch<Bool_t>("Electron_cutBased",m_raw_index); } 
int    Electron::PassEGammaIDMedium   (){ return m_collection->ReadArrayBranch<Bool_t>("Electron_cutBased",m_raw_index); } 
int    Electron::PassEGammaIDTight    (){ return m_collection->ReadArrayBranch<Bool_t>("Electron_cutBased",m_raw_index); } 
int    Electron::PassEGammaIDVeto     (){ return m_collection->ReadArrayBranch<Bool_t>("Electron_cutBased",m_raw_index); } 
int    Electron::PassHEEPID           (){ return m_collection->ReadArrayBranch<Bool_t>("Electron_cutBased_HEEP",m_raw_index); } 
														      
// ID variables			      	   		      		  	  				      
bool Electron::PassHEEPIDCut(HEEPIDCut cut) {
  return 0x1 & (m_collection->ReadArrayBranch<Int_t>("Electron_vidNestedWPBitmapHEEP",m_raw_index) >> static_cast<int>(cut));
}
bool Electron::PassHEEPMinPtCut                            (){ return PassHEEPIDCut(HEEPIDCut::MinPtCut); }
bool Electron::PassHEEPGsfEleSCEtaMultiRangeCut            (){ return PassHEEPIDCut(HEEPIDCut::GsfEleSCEtaMultiRangeCut); }
bool Electron::PassHEEPGsfEleDEtaInSeedCut                 (){ return PassHEEPIDCut(HEEPIDCut::GsfEleDEtaInSeedCut); }
bool Electron::PassHEEPGsfEleDPhiInCut                     (){ return PassHEEPIDCut(HEEPIDCut::GsfEleDPhiInCut); }
bool Electron::PassHEEPGsfEleFull5x5SigmaIEtaIEtaWithSatCut(){ return PassHEEPIDCut(HEEPIDCut::GsfEleFull5x5SigmaIEtaIEtaWithSatCut); }
bool Electron::PassHEEPGsfEleFull5x5E2x5OverE5x5WithSatCut (){ return PassHEEPIDCut(HEEPIDCut::GsfEleFull5x5E2x5OverE5x5WithSatCut); }
bool Electron::PassHEEPGsfEleHadronicOverEMLinearCut       (){ return PassHEEPIDCut(HEEPIDCut::GsfEleHadronicOverEMLinearCut); }
bool Electron::PassHEEPGsfEleTrkPtIsoCut                   (){ return PassHEEPIDCut(HEEPIDCut::GsfEleTrkPtIsoCut); }
bool Electron::PassHEEPGsfEleEmHadD1IsoRhoCut              (){ return PassHEEPIDCut(HEEPIDCut::GsfEleEmHadD1IsoRhoCut); }
bool Electron::PassHEEPGsfEleDxyCut                        (){ return PassHEEPIDCut(HEEPIDCut::GsfEleDxyCut); }
bool Electron::PassHEEPGsfEleMissingHitsCut                (){ return PassHEEPIDCut(HEEPIDCut::GsfEleMissingHitsCut); }
bool Electron::PassHEEPEcalDrivenCut                       (){ return PassHEEPIDCut(HEEPIDCut::GsfEleEcalDrivenCut); }

//bool   Electron::EcalSeed             (){ return m_collection->ReadArrayBranch<Float_t>("Electron_") ElectronHasEcalDrivenSeed        -> at ( m_raw_index ); }
//bool   Electron::EcalDriven           (){ return m_collection->ReadArrayBranch<Float_t>("Electron_") ElectronIsEcalDriven             -> at ( m_raw_index ); }
bool   Electron::EcalSeed             (){ return false; }
//float Electron::DeltaEtaSeed         (){ return m_collection->ReadArrayBranch<Float_t>("Electron_") ElectronDeltaEtaTrkSeedSC        -> at ( m_raw_index ); }
float Electron::DeltaEtaSeed          (){
  //std::cout << "Electron::DeltaEtaTrkSeedSC=" << m_collection->ReadArrayBranch<Float_t>("Electron_") ElectronDeltaEtaTrkSeedSC            -> at ( m_raw_index )
  //  //<< "\tElectron::dEtaSCTrkAtVtx-SCEta+SCSeedEta=" << 
  //  //m_collection->ReadArrayBranch<Float_t>("Electron_") ElectronDeltaEtaTrkSC            -> at ( m_raw_index ) -
  //  //m_collection->ReadArrayBranch<Float_t>("Electron_") ElectronSCEta -> at( m_raw_index) +
  //  //m_collection->ReadArrayBranch<Float_t>("Electron_") ElectronSCSeedEta -> at(m_raw_index)
  //  << std::endl;
  return -1.0;
}
// -999 --> indicates that it's not available in NanoAOD
float Electron::DeltaPhi             (){ return -999; }
float Electron::HoE                  (){ return m_collection->ReadArrayBranch<Float_t>("Electron_hoe",m_raw_index); }
//FIXME remove
float Electron::SigmaEtaEta          (){ return -999; } 

float Electron::Full5x5SigmaIEtaIEta (){ return m_collection->ReadArrayBranch<Float_t>("Electron_sieie",m_raw_index); }
float Electron::Full5x5E1x5OverE5x5  (){ return -999; }
float Electron::Full5x5E2x5OverE5x5  (){ return -999; }
float Electron::LeadVtxDistXY        (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dxy",m_raw_index); }
float Electron::LeadVtxDistZ         (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dz",m_raw_index); }
//
float Electron::VtxDistXY            (){ return -999; }
float Electron::VtxDistZ             (){ return -999; }
//
float Electron::Dist                 (){ return -999; }
float Electron::DCotTheta            (){ return -999; }
float Electron::ValidFrac            (){ return -999; }
float Electron::CaloEnergy           (){ return -999; }
float Electron::EcalEnergy           (){ return -999; }
float Electron::ESuperClusterOverP   (){ return -999; }
float Electron::NBrems               (){ return -999; }
bool Electron::HasMatchedConvPhot    (){ return !(m_collection->ReadArrayBranch<Bool_t>("Electron_convVeto",m_raw_index)); }
float Electron::FBrem                (){ return -999; }
float Electron::BeamSpotDXY          (){ return -999; }
float Electron::BeamSpotDXYErr       (){ return -999; }
float Electron::GsfCtfScPixCharge    (){ return -999; }
float Electron::GsfScPixCharge       (){ return -999; }
float Electron::GsfCtfCharge         (){ return -999; }
float Electron::Classif              (){ return -999; }
float Electron::RhoForHEEP           (){ return m_collection->ReadValueBranch<Float_t>("fixedGridRhoFastjetAll"); }
float Electron::DeltaEta             (){ return m_collection->ReadArrayBranch<Float_t>("Electron_deltaEtaSC",m_raw_index); }
					                                      					      
// Conversion variables		      	   		      		  	  				      
//FIXME: difference between these is...?
int    Electron::MissingHitsEG        (){ return m_collection->ReadArrayBranch<UChar_t>("Electron_lostHits",m_raw_index); }
int    Electron::MissingHits          (){ return m_collection->ReadArrayBranch<UChar_t>("Electron_lostHits",m_raw_index); }
					                                      					      
// Isolation variables		       	   		       			  				      
					                                      					      
float Electron::EcalIsoDR03          (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dr03EcalRecHitSumEt"     , m_raw_index); }
float Electron::HcalIsoD1DR03        (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dr03HcalDepth1TowerSumEt", m_raw_index); }
float Electron::TrkIsoDR03           (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dr03TkSumPt"             , m_raw_index); }
float Electron::PFChargedHadronIso03 (){ return m_collection->ReadArrayBranch<Float_t>("Electron_pfRelIso03_chg"          , m_raw_index); }
float Electron::PFPhotonIso03        (){ return -999; }
float Electron::PFNeutralHadronIso03 (){ return -999; }
float Electron::PFPUIso03            (){ return -999; }

// GEN matching
UInt_t Electron::NumGenParticles() { return 1; } //FIXME: this is either 1 matched particle or nothing matched
int    Electron::MatchedGenParticleIdx(){ return m_collection->ReadArrayBranch<Int_t>("Electron_genPartIdx",m_raw_index); }
bool   Electron::IsValidGenParticleIdx(int index) {
  if(MatchedGenParticleIdx() < NumGenParticles() && MatchedGenParticleIdx() >= 0)
    return true;
  return false;
}
float  Electron::MatchedGenParticlePt (){ if(IsValidGenParticleIdx(MatchedGenParticleIdx())) return m_collection->ReadArrayBranch<Float_t>("GenPart_pt",m_raw_index); else return -1;} 
float  Electron::MatchedGenParticleEta(){ if(IsValidGenParticleIdx(MatchedGenParticleIdx())) return m_collection->ReadArrayBranch<Float_t>("GenPart_eta",m_raw_index); else return -1;} 
float  Electron::MatchedGenParticlePhi(){ if(IsValidGenParticleIdx(MatchedGenParticleIdx())) return m_collection->ReadArrayBranch<Float_t>("GenPart_phi",m_raw_index); else return -1;}

float Electron::HEEPCaloIsolation(){ return EcalIsoDR03() + HcalIsoD1DR03(); }
float Electron::HEEPCorrIsolation(){ return (HEEPCaloIsolation() - (2.0 + ( 0.03 * Pt() ) + (0.28 * RhoForHEEP()))); }
float Electron::HEEP70TrackIsolation(){ return m_collection->ReadArrayBranch<Float_t>("Electron_dr03TkSumPtHEEP",m_raw_index); }
float Electron::TrackPt          (){
  float px = m_collection->ReadArrayBranch<Float_t>("Electron_trkPx",m_raw_index);
  float py = m_collection->ReadArrayBranch<Float_t>("Electron_trkPy",m_raw_index);
  float pz = m_collection->ReadArrayBranch<Float_t>("Electron_trkPz",m_raw_index);
  TVector3 v1;
  v1.SetXYZ(px,py,pz);
  return v1.Pt();
}
float Electron::TrackEta         (){
  float px = m_collection->ReadArrayBranch<Float_t>("Electron_trkPx",m_raw_index);
  float py = m_collection->ReadArrayBranch<Float_t>("Electron_trkPy",m_raw_index);
  float pz = m_collection->ReadArrayBranch<Float_t>("Electron_trkPz",m_raw_index);
  TVector3 v1;
  v1.SetXYZ(px,py,pz);
  return v1.Eta();
}

// Fiduciality
bool   Electron::IsEBFiducial     (){ return bool  ( fabs(SCEta()) < 1.442 );}
bool   Electron::IsEEFiducial     (){ return bool (( fabs(SCEta()) > 1.560 ) && 
						   ( fabs(SCEta()) < 2.500 ));}

// Energy resolution scale factors
//FIXME
float Electron::EnergyResScaleFactor (){ 
  // SIC: changed May 12, 2015 to 10% as per LQ1 2012 CWR comment; see EGM-13-001 and email thread
  if      ( IsEBFiducial() ) return 1.1;
  else if ( IsEEFiducial() ) return 1.1;
  else                       return 1.000;
}

float Electron::EnergyResScaleError  (){ 
  return 0.000;
}

float Electron::EnergyScaleFactor (){ 
  // SIC: changed May 12, 2015 to 2% as per LQ1 2012 CWR comment; see EGM-13-001 and email thread
  if      ( IsEBFiducial() ) return 0.02;
  else if ( IsEEFiducial() ) return 0.02;
  else                       return 0.000;
}

std::ostream& operator<<(std::ostream& stream, Electron& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "    << object.Pt ()           << ", "
	 << "PtHeep = "    << object.PtHeep ()           << ", "
	 << "Uncorrected (SC) Pt = "    << object.SCPt()           << ", "
	 << "SCEnergy = "          << object.SCEnergy() << ", "
	 //<< "SCRawEnergy = "          << object.RawEnergy() << ", "
	 //<< "EcalEnergy = "          << object.EcalEnergy() << ", "
	 << "CaloEnergy = "          << object.CaloEnergy() << ", "
	 << "H/E = "          << object.HoE() << ", "
	 << "dxy = "          << object.LeadVtxDistXY() << ", "
   << "ECorr = " << object.ECorr() << ", "
	 << "Eta = "   << object.Eta()           << ", "
	 //<< "SCEta = "   << object.SCEta()           << ", "
	 //<< "SCSeedEta = "   << object.SCSeedEta()           << ", "
	 << "Phi = "   << object.Phi()           << ", "
   << "PassLooseID = " << object.PassUserID(FAKE_RATE_HEEP_LOOSE) << ", "
   << "PassHEEP (builtin) = " << object.PassHEEPID() << ", "
   //<< "PassHEEP (manual) = " << object.PassUserID(HEEP70_MANUAL,true);
   ;
  return stream;
}
