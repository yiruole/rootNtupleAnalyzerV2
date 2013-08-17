#include "Electron.h"
#include "Object.h"
#include "IDTypes.h"

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

double & Electron::Pt                 (){ return m_collection -> GetData() -> ElectronPtHeep                   -> at ( m_raw_index ); }
//double & Electron::Pt                 (){ return m_rawSuperClusterPt; } 
double & Electron::Eta                (){ return m_collection -> GetData() -> ElectronEta                      -> at ( m_raw_index ); } 
double & Electron::Phi                (){ return m_collection -> GetData() -> ElectronPhi                      -> at ( m_raw_index ); } 
double   Electron::SCEta              (){ return m_collection -> GetData() -> ElectronSCEta                    -> at ( m_raw_index ); } 
double   Electron::SCPhi              (){ return m_collection -> GetData() -> ElectronSCPhi                    -> at ( m_raw_index ); } 
double   Electron::IsEB               (){ return m_collection -> GetData() -> ElectronIsEB                     -> at ( m_raw_index ); } 
double   Electron::IsEE               (){ return m_collection -> GetData() -> ElectronIsEE                     -> at ( m_raw_index ); } 
double   Electron::Charge             (){ return m_collection -> GetData() -> ElectronCharge                   -> at ( m_raw_index ); } 
double   Electron::RawEnergy          (){ return m_collection -> GetData() -> ElectronSCRawEnergy              -> at ( m_raw_index ); } 
								      
// EGamma bits													      
														      
int    Electron::PassEGammaIDEoP      (){ return m_collection -> GetData() -> ElectronPassEGammaIDEoP          -> at ( m_raw_index ); } 
int    Electron::PassEGammaIDLoose    (){ return m_collection -> GetData() -> ElectronPassEGammaIDLoose        -> at ( m_raw_index ); } 
int    Electron::PassEGammaIDMedium   (){ return m_collection -> GetData() -> ElectronPassEGammaIDMedium       -> at ( m_raw_index ); } 
int    Electron::PassEGammaIDTight    (){ return m_collection -> GetData() -> ElectronPassEGammaIDTight        -> at ( m_raw_index ); } 
int    Electron::PassEGammaIDTrigTight(){ return m_collection -> GetData() -> ElectronPassEGammaIDTrigTight    -> at ( m_raw_index ); }  
int    Electron::PassEGammaIDTrigWP70 (){ return m_collection -> GetData() -> ElectronPassEGammaIDTrigWP70     -> at ( m_raw_index ); }  
int    Electron::PassEGammaIDVeto     (){ return m_collection -> GetData() -> ElectronPassEGammaIDVeto         -> at ( m_raw_index ); } 
														      
// ID variables			      	   		      		  	  				      
					                                      					      
bool   Electron::EcalSeed             (){ return m_collection -> GetData() -> ElectronHasEcalDrivenSeed        -> at ( m_raw_index ); }
double Electron::DeltaEta             (){ return m_collection -> GetData() -> ElectronDeltaEtaTrkSC            -> at ( m_raw_index ); }
double Electron::DeltaPhi             (){ return m_collection -> GetData() -> ElectronDeltaPhiTrkSC            -> at ( m_raw_index ); }
double Electron::HoE                  (){ return m_collection -> GetData() -> ElectronHoE                      -> at ( m_raw_index ); }
double Electron::SigmaIEtaIEta        (){ return m_collection -> GetData() -> ElectronSigmaIEtaIEta            -> at ( m_raw_index ); }
double Electron::SigmaEtaEta          (){ return m_collection -> GetData() -> ElectronSigmaEtaEta              -> at ( m_raw_index ); } 
double Electron::E1x5OverE5x5         (){ return m_collection -> GetData() -> ElectronE1x5OverE5x5             -> at ( m_raw_index ); }
double Electron::E2x5OverE5x5         (){ return m_collection -> GetData() -> ElectronE2x5OverE5x5             -> at ( m_raw_index ); }
double Electron::LeadVtxDistXY        (){ return m_collection -> GetData() -> ElectronLeadVtxDistXY            -> at ( m_raw_index ); }
double Electron::LeadVtxDistZ         (){ return m_collection -> GetData() -> ElectronLeadVtxDistZ             -> at ( m_raw_index ); }
double Electron::VtxDistXY            (){ return m_collection -> GetData() -> ElectronVtxDistXY                -> at ( m_raw_index ); }
double Electron::VtxDistZ             (){ return m_collection -> GetData() -> ElectronVtxDistZ                 -> at ( m_raw_index ); }
double Electron::Dist                 (){ return m_collection -> GetData() -> ElectronDist                     -> at ( m_raw_index ); }
double Electron::DCotTheta            (){ return m_collection -> GetData() -> ElectronDCotTheta                -> at ( m_raw_index ); }
double Electron::ValidFrac            (){ return m_collection -> GetData() -> ElectronTrackValidFractionOfHits -> at ( m_raw_index ); }
double Electron::CaloEnergy           (){ return m_collection -> GetData() -> ElectronCaloEnergy               -> at ( m_raw_index ); }
double Electron::ESuperClusterOverP   (){ return m_collection -> GetData() -> ElectronESuperClusterOverP       -> at ( m_raw_index ); }
double Electron::NBrems               (){ return m_collection -> GetData() -> ElectronNumberOfBrems            -> at ( m_raw_index ); }
double Electron::HasMatchedConvPhot   (){ return m_collection -> GetData() -> ElectronHasMatchedConvPhot       -> at ( m_raw_index ); }
double Electron::FBrem                (){ return m_collection -> GetData() -> ElectronFbrem                    -> at ( m_raw_index ); }
double Electron::BeamSpotDXY          (){ return m_collection -> GetData() -> ElectronBeamSpotDXY              -> at ( m_raw_index ); }
double Electron::BeamSpotDXYErr       (){ return m_collection -> GetData() -> ElectronBeamSpotDXYError         -> at ( m_raw_index ); }
double Electron::GsfCtfScPixCharge    (){ return m_collection -> GetData() -> ElectronGsfCtfScPixCharge        -> at ( m_raw_index ); }
double Electron::GsfScPixCharge       (){ return m_collection -> GetData() -> ElectronGsfScPixCharge           -> at ( m_raw_index ); }
double Electron::GsfCtfCharge         (){ return m_collection -> GetData() -> ElectronGsfCtfCharge             -> at ( m_raw_index ); }
double Electron::Classif              (){ return m_collection -> GetData() -> ElectronClassif                  -> at ( m_raw_index ); }
					                                      					      
// Conversion variables		      	   		      		  	  				      
					                                      					      
int    Electron::MissingHitsEG        (){ return m_collection -> GetData() -> ElectronMissingHitsEG            -> at ( m_raw_index ); }
int    Electron::MissingHits          (){ return m_collection -> GetData() -> ElectronMissingHits              -> at ( m_raw_index ); }
double Electron::ConvFitProb          (){ return m_collection -> GetData() -> ElectronConvFitProb              -> at ( m_raw_index ); }
					                                      					      
// Isolation variables		       	   		       			  				      
					                                      					      
double Electron::EcalIsoDR03          (){ return m_collection -> GetData() -> ElectronEcalIsoDR03              -> at ( m_raw_index ); }
double Electron::HcalIsoD1DR03        (){ return m_collection -> GetData() -> ElectronHcalIsoD1DR03            -> at ( m_raw_index ); }
double Electron::TrkIsoDR03           (){ return m_collection -> GetData() -> ElectronTrkIsoDR03               -> at ( m_raw_index ); }
double Electron::PFChargedHadronIso03 (){ return m_collection -> GetData() -> ElectronPFChargedHadronIso03     -> at ( m_raw_index ); }
double Electron::PFPhotonIso03        (){ return m_collection -> GetData() -> ElectronPFPhotonIso03            -> at ( m_raw_index ); }
double Electron::PFNeutralHadronIso03 (){ return m_collection -> GetData() -> ElectronPFNeutralHadronIso03     -> at ( m_raw_index ); }
double Electron::PFChargedHadronIso04 (){ return m_collection -> GetData() -> ElectronPFChargedHadronIso04     -> at ( m_raw_index ); }
double Electron::PFPhotonIso04        (){ return m_collection -> GetData() -> ElectronPFPhotonIso04            -> at ( m_raw_index ); }
double Electron::PFNeutralHadronIso04 (){ return m_collection -> GetData() -> ElectronPFNeutralHadronIso04     -> at ( m_raw_index ); }

// Rho variables

double Electron::RhoForHEEPv4p0        (){ return m_collection -> GetData() -> rhoForHEEP; }
double Electron::RhoForEGamma2012      (){ return m_collection -> GetData() -> rhoJets   ; }

// GEN matching

double Electron::MatchedGenParticlePt (){ return m_collection -> GetData() -> ElectronMatchedGenParticlePt  -> at ( m_raw_index ); } 
double Electron::MatchedGenParticleEta(){ return m_collection -> GetData() -> ElectronMatchedGenParticleEta -> at ( m_raw_index ); } 
double Electron::MatchedGenParticlePhi(){ return m_collection -> GetData() -> ElectronMatchedGenParticlePhi -> at ( m_raw_index ); }

// Isolation variables

double Electron::HEEPCaloIsolation(){ return (EcalIsoDR03() + HcalIsoD1DR03()); }
double Electron::HEEPCorrIsolation(){ return ( HEEPCaloIsolation() - (2.0 + ( 0.03 * Pt() ) + (0.28 * RhoForHEEPv4p0()))); }
double Electron::TrackPt          (){ return m_collection -> GetData() -> ElectronTrackPt -> at ( m_raw_index ); }

// Fiduciality

bool   Electron::IsEBFiducial     (){ return bool  ( fabs(SCEta()) < 1.442 );}
bool   Electron::IsEEFiducial     (){ return bool (( fabs(SCEta()) > 1.560 ) && 
						   ( fabs(SCEta()) < 2.500 ));}

// Energy resolution scale factors

double Electron::EnergyResScaleFactor (){ 
  if      ( IsEBFiducial() ) return 1.004;
  else if ( IsEEFiducial() ) return 1.041;
  else                       return 1.000;
}

double Electron::EnergyResScaleError  (){ 
  return 0.000;
}

double Electron::EnergyScaleFactor (){ 
  if      ( IsEBFiducial() ) return 0.006;
  else if ( IsEEFiducial() ) return 0.015;
  else                       return 0.000;
}

std::ostream& operator<<(std::ostream& stream, Electron& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "    << object.Pt ()           << ", "
	 << "Eta = "   << object.Eta()           << ", "
	 << "Phi = "   << object.Phi()           ;
  return stream;
}
