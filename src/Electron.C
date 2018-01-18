#include "Electron.h"
#include "Object.h"
#include "IDTypes.h"
#include "TVector3.h"

Electron::Electron ():
  Object()
  // m_rawSuperClusterPt(0.)
{}

Electron::Electron (Collection & c, unsigned short i, short j ):
  Object(c,i,"Electron") {
  //if ( m_collection -> GetData() -> ElectronCaloEnergy -> at ( m_raw_index ) == 0. ) m_rawSuperClusterPt = 0.;
  //else { 
  //  m_rawSuperClusterPt = ( ( m_collection -> GetData() -> ElectronPtHeep       -> at ( m_raw_index ) ) * 
  //			    ( m_collection -> GetData() -> ElectronSCRawEnergy  -> at ( m_raw_index ) ) / 
  //			    ( m_collection -> GetData() -> ElectronCaloEnergy   -> at ( m_raw_index ) ) );
  //}
}

// Kinematic variables

float & Electron::PtHeep             (){ return m_collection -> GetData() -> ElectronPtHeep                   -> at ( m_raw_index ); }
float & Electron::Pt                 (){ return m_collection -> GetData() -> ElectronPt                       -> at ( m_raw_index ); } 
float & Electron::Eta                (){ return m_collection -> GetData() -> ElectronEta                      -> at ( m_raw_index ); } 
float & Electron::Phi                (){ return m_collection -> GetData() -> ElectronPhi                      -> at ( m_raw_index ); } 
float   Electron::SCEta              (){ return m_collection -> GetData() -> ElectronSCEta                    -> at ( m_raw_index ); } 
float   Electron::SCSeedEta          (){ return m_collection -> GetData() -> ElectronSCSeedEta                -> at ( m_raw_index ); } 
float   Electron::SCPhi              (){ return m_collection -> GetData() -> ElectronSCPhi                    -> at ( m_raw_index ); } 
float   Electron::SCPt               (){ return m_collection -> GetData() -> ElectronSCPt                     -> at ( m_raw_index ); } 
float   Electron::IsEB               (){ return m_collection -> GetData() -> ElectronIsEB                     -> at ( m_raw_index ); } 
float   Electron::IsEE               (){ return m_collection -> GetData() -> ElectronIsEE                     -> at ( m_raw_index ); } 
float   Electron::Charge             (){ return m_collection -> GetData() -> ElectronCharge                   -> at ( m_raw_index ); } 
float   Electron::RawEnergy          (){ return m_collection -> GetData() -> ElectronSCRawEnergy              -> at ( m_raw_index ); } 
float   Electron::SCEnergy           (){ return m_collection -> GetData() -> ElectronSCEnergy                 -> at ( m_raw_index ); } 
								      
// EGamma bits													      
														      
int    Electron::PassEGammaIDLoose    (){ return m_collection -> GetData() -> ElectronPassEGammaIDLoose        -> at ( m_raw_index ); } 
int    Electron::PassEGammaIDMedium   (){ return m_collection -> GetData() -> ElectronPassEGammaIDMedium       -> at ( m_raw_index ); } 
int    Electron::PassEGammaIDTight    (){ return m_collection -> GetData() -> ElectronPassEGammaIDTight        -> at ( m_raw_index ); } 
int    Electron::PassEGammaIDVeto     (){ return m_collection -> GetData() -> ElectronPassEGammaIDVeto         -> at ( m_raw_index ); } 
int    Electron::PassHEEPID           (){ return m_collection -> GetData() -> ElectronPassHEEPID               -> at ( m_raw_index ); } 
														      
// ID variables			      	   		      		  	  				      
					                                      					      
bool   Electron::EcalSeed             (){ return m_collection -> GetData() -> ElectronHasEcalDrivenSeed        -> at ( m_raw_index ); }
bool   Electron::EcalDriven           (){ return m_collection -> GetData() -> ElectronIsEcalDriven             -> at ( m_raw_index ); }
float Electron::DeltaEta              (){ return m_collection -> GetData() -> ElectronDeltaEtaTrkSC            -> at ( m_raw_index ); }
//float Electron::DeltaEtaSeed         (){ return m_collection -> GetData() -> ElectronDeltaEtaTrkSeedSC        -> at ( m_raw_index ); }
float Electron::DeltaEtaSeed          (){
  //std::cout << "Electron::DeltaEtaTrkSeedSC=" << m_collection -> GetData() -> ElectronDeltaEtaTrkSeedSC            -> at ( m_raw_index )
  //  //<< "\tElectron::dEtaSCTrkAtVtx-SCEta+SCSeedEta=" << 
  //  //m_collection -> GetData() -> ElectronDeltaEtaTrkSC            -> at ( m_raw_index ) -
  //  //m_collection -> GetData() -> ElectronSCEta -> at( m_raw_index) +
  //  //m_collection -> GetData() -> ElectronSCSeedEta -> at(m_raw_index)
  //  << std::endl;
  return m_collection -> GetData() -> ElectronDeltaEtaTrkSeedSC        -> at ( m_raw_index );
}
float Electron::DeltaPhi             (){ return m_collection -> GetData() -> ElectronDeltaPhiTrkSC            -> at ( m_raw_index ); }
float Electron::HoE                  (){ return m_collection -> GetData() -> ElectronHoE                      -> at ( m_raw_index ); }
//float Electron::SigmaIEtaIEta        (){ return m_collection -> GetData() -> ElectronSigmaIEtaIEta            -> at ( m_raw_index ); }
float Electron::Full5x5SigmaIEtaIEta (){ return m_collection -> GetData() -> ElectronFull5x5SigmaIEtaIEta     -> at ( m_raw_index ); }
float Electron::SigmaEtaEta          (){ return m_collection -> GetData() -> ElectronSigmaEtaEta              -> at ( m_raw_index ); } 
//float Electron::E1x5OverE5x5         (){ return m_collection -> GetData() -> ElectronE1x5OverE5x5             -> at ( m_raw_index ); }
//float Electron::E2x5OverE5x5         (){ return m_collection -> GetData() -> ElectronE2x5OverE5x5             -> at ( m_raw_index ); }
float Electron::Full5x5E1x5OverE5x5  (){ return m_collection -> GetData() -> ElectronFull5x5E1x5OverE5x5      -> at ( m_raw_index ); }
float Electron::Full5x5E2x5OverE5x5  (){ return m_collection -> GetData() -> ElectronFull5x5E2x5OverE5x5      -> at ( m_raw_index ); }
float Electron::LeadVtxDistXY        (){ return m_collection -> GetData() -> ElectronLeadVtxDistXY            -> at ( m_raw_index ); }
float Electron::LeadVtxDistZ         (){ return m_collection -> GetData() -> ElectronLeadVtxDistZ             -> at ( m_raw_index ); }
float Electron::VtxDistXY            (){ return m_collection -> GetData() -> ElectronVtxDistXY                -> at ( m_raw_index ); }
float Electron::VtxDistZ             (){ return m_collection -> GetData() -> ElectronVtxDistZ                 -> at ( m_raw_index ); }
float Electron::Dist                 (){ return m_collection -> GetData() -> ElectronDist                     -> at ( m_raw_index ); }
float Electron::DCotTheta            (){ return m_collection -> GetData() -> ElectronDCotTheta                -> at ( m_raw_index ); }
float Electron::ValidFrac            (){ return m_collection -> GetData() -> ElectronTrackValidFractionOfHits -> at ( m_raw_index ); }
float Electron::CaloEnergy           (){ return m_collection -> GetData() -> ElectronCaloEnergy               -> at ( m_raw_index ); }
float Electron::EcalEnergy           (){ return m_collection -> GetData() -> ElectronEcalEnergy               -> at ( m_raw_index ); }
float Electron::ESuperClusterOverP   (){ return m_collection -> GetData() -> ElectronESuperClusterOverP       -> at ( m_raw_index ); }
float Electron::NBrems               (){ return m_collection -> GetData() -> ElectronNumberOfBrems            -> at ( m_raw_index ); }
float Electron::HasMatchedConvPhot   (){ return m_collection -> GetData() -> ElectronHasMatchedConvPhot       -> at ( m_raw_index ); }
float Electron::FBrem                (){ return m_collection -> GetData() -> ElectronFbrem                    -> at ( m_raw_index ); }
float Electron::BeamSpotDXY          (){ return m_collection -> GetData() -> ElectronBeamSpotDXY              -> at ( m_raw_index ); }
float Electron::BeamSpotDXYErr       (){ return m_collection -> GetData() -> ElectronBeamSpotDXYError         -> at ( m_raw_index ); }
float Electron::GsfCtfScPixCharge    (){ return m_collection -> GetData() -> ElectronGsfCtfScPixCharge        -> at ( m_raw_index ); }
float Electron::GsfScPixCharge       (){ return m_collection -> GetData() -> ElectronGsfScPixCharge           -> at ( m_raw_index ); }
float Electron::GsfCtfCharge         (){ return m_collection -> GetData() -> ElectronGsfCtfCharge             -> at ( m_raw_index ); }
float Electron::Classif              (){ return m_collection -> GetData() -> ElectronClassif                  -> at ( m_raw_index ); }
float Electron::RhoForHEEP           (){ return m_collection -> GetData() -> ElectronRhoIsoHEEP               -> at ( m_raw_index ); }
					                                      					      
// Conversion variables		      	   		      		  	  				      
					                                      					      
int    Electron::MissingHitsEG        (){ return m_collection -> GetData() -> ElectronMissingHitsEG            -> at ( m_raw_index ); }
int    Electron::MissingHits          (){ return m_collection -> GetData() -> ElectronMissingHits              -> at ( m_raw_index ); }
					                                      					      
// Isolation variables		       	   		       			  				      
					                                      					      
float Electron::EcalIsoDR03          (){ return m_collection -> GetData() -> ElectronEcalIsoDR03              -> at ( m_raw_index ); }
float Electron::HcalIsoD1DR03        (){ return m_collection -> GetData() -> ElectronHcalIsoD1DR03            -> at ( m_raw_index ); }
float Electron::TrkIsoDR03           (){ return m_collection -> GetData() -> ElectronTrkIsoDR03               -> at ( m_raw_index ); }
float Electron::PFChargedHadronIso03 (){ return m_collection -> GetData() -> ElectronPFChargedHadronIso03     -> at ( m_raw_index ); }
float Electron::PFPhotonIso03        (){ return m_collection -> GetData() -> ElectronPFPhotonIso03            -> at ( m_raw_index ); }
float Electron::PFNeutralHadronIso03 (){ return m_collection -> GetData() -> ElectronPFNeutralHadronIso03     -> at ( m_raw_index ); }
float Electron::PFPUIso03            (){ return m_collection -> GetData() -> ElectronPFPUIso03                -> at ( m_raw_index ); }
//float Electron::PFChargedHadronIso04 (){ return m_collection -> GetData() -> ElectronPFChargedHadronIso04     -> at ( m_raw_index ); }
//float Electron::PFPhotonIso04        (){ return m_collection -> GetData() -> ElectronPFPhotonIso04            -> at ( m_raw_index ); }
//float Electron::PFNeutralHadronIso04 (){ return m_collection -> GetData() -> ElectronPFNeutralHadronIso04     -> at ( m_raw_index ); }

// GEN matching

float Electron::MatchedGenParticlePt (){ return m_collection -> GetData() -> ElectronMatchedGenParticlePt  -> at ( m_raw_index ); } 
float Electron::MatchedGenParticleEta(){ return m_collection -> GetData() -> ElectronMatchedGenParticleEta -> at ( m_raw_index ); } 
float Electron::MatchedGenParticlePhi(){ return m_collection -> GetData() -> ElectronMatchedGenParticlePhi -> at ( m_raw_index ); }

// HLT matching

// Isolation variables


float Electron::HEEPCaloIsolation(){ return (EcalIsoDR03() + HcalIsoD1DR03()); }
float Electron::HEEPCorrIsolation(){ return ( HEEPCaloIsolation() - (2.0 + ( 0.03 * Pt() ) + (0.28 * RhoForHEEP()))); }
float Electron::HEEP70TrackIsolation(){ return m_collection -> GetData() -> ElectronHeep70TrkIso -> at(m_raw_index); }
float Electron::TrackPt          (){ return m_collection -> GetData() -> ElectronTrackPt -> at ( m_raw_index ); }
float Electron::TrackEta         (){
  float px = m_collection -> GetData() -> ElectronTrackPx -> at ( m_raw_index );
  float py = m_collection -> GetData() -> ElectronTrackPy -> at ( m_raw_index );
  float pz = m_collection -> GetData() -> ElectronTrackPz -> at ( m_raw_index );
  TVector3 v1;
  v1.SetXYZ(px,py,pz);
  return v1.Eta();
}

// Fiduciality

bool   Electron::IsEBFiducial     (){ return bool  ( fabs(SCEta()) < 1.442 );}
bool   Electron::IsEEFiducial     (){ return bool (( fabs(SCEta()) > 1.560 ) && 
						   ( fabs(SCEta()) < 2.500 ));}

// Energy resolution scale factors

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
	 << "Uncorrected Pt = "    << object.SCPt()           << ", "
	 << "SCEnergy = "          << object.SCEnergy() << ", "
	 << "SCRawEnergy = "          << object.RawEnergy() << ", "
	 << "EcalEnergy = "          << object.EcalEnergy() << ", "
	 << "H/E = "          << object.HoE() << ", "
	 << "Eta = "   << object.Eta()           << ", "
	 << "SCEta = "   << object.SCEta()           << ", "
	 << "SCSeedEta = "   << object.SCSeedEta()           << ", "
	 << "Phi = "   << object.Phi()           << ", "
   << "PassLooseID = " << object.PassUserID(FAKE_RATE_HEEP_LOOSE,true) << ", "
   << "PassHEEP (builtin) = " << object.PassHEEPID() << ", "
   << "PassHEEP (manual) = " << object.PassUserID(HEEP70_MANUAL,true);
  return stream;
}
