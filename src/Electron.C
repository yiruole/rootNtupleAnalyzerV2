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

//FIXME ptheep
float & Electron::PtHeep             (){ return m_collection -> GetData() -> Electron_pt      [m_raw_index]; }
float & Electron::Pt                 (){ return m_collection -> GetData() -> Electron_pt      [m_raw_index]; } 
float & Electron::Eta                (){ return m_collection -> GetData() -> Electron_eta     [m_raw_index]; } 
float & Electron::Phi                (){ return m_collection -> GetData() -> Electron_phi     [m_raw_index]; } 
//FIXME
float   Electron::SCEta              (){ return m_collection -> GetData() -> Electron_eta     [m_raw_index]; } 
float   Electron::SCSeedEta          (){ return -1.0; } 
float   Electron::SCPhi              (){ return 1.0; } 
float   Electron::SCPt               (){ return 1.0; } 
float   Electron::IsEB               (){ return fabs(Eta()) < 1.5; } 
float   Electron::IsEE               (){ return fabs(Eta()) < 2.5; } 

float   Electron::Charge             (){ return m_collection -> GetData() -> Electron_charge  [m_raw_index]; } 
float   Electron::RawEnergy          (){ return -1.0; } 
float   Electron::SCEnergy           (){
  const float px = Pt()*cos(Phi());
  const float py = Pt()*sin(Phi());
  const float pz = Pt()*sinh(Eta());
  const float e = sqrt(px*px + py*py + pz*pz);
  return e;
} 
								      
// EGamma bits													      
//FIXME
int    Electron::PassEGammaIDLoose    (){ return m_collection -> GetData() -> Electron_cutBased     [m_raw_index]; } 
int    Electron::PassEGammaIDMedium   (){ return m_collection -> GetData() -> Electron_cutBased     [m_raw_index]; } 
int    Electron::PassEGammaIDTight    (){ return m_collection -> GetData() -> Electron_cutBased     [m_raw_index]; } 
int    Electron::PassEGammaIDVeto     (){ return m_collection -> GetData() -> Electron_cutBased     [m_raw_index]; } 
int    Electron::PassHEEPID           (){ return m_collection -> GetData() -> Electron_cutBased_HEEP[m_raw_index]; } 
														      
// ID variables			      	   		      		  	  				      
//FIXME from bitmap
int Electron::GetNbitFromBitMap(int n, int base) { return (m_collection->GetData()->Electron_vidNestedWPBitmap[m_raw_index]>>(base*n))%int(pow(2,base)); }

//bool   Electron::EcalSeed             (){ return m_collection -> GetData() -> ElectronHasEcalDrivenSeed        -> at ( m_raw_index ); }
//bool   Electron::EcalDriven           (){ return m_collection -> GetData() -> ElectronIsEcalDriven             -> at ( m_raw_index ); }
bool   Electron::EcalSeed             (){ return false; }
bool   Electron::EcalDriven           (){ return false; }
//float Electron::DeltaEtaSeed         (){ return m_collection -> GetData() -> ElectronDeltaEtaTrkSeedSC        -> at ( m_raw_index ); }
float Electron::DeltaEtaSeed          (){
  //std::cout << "Electron::DeltaEtaTrkSeedSC=" << m_collection -> GetData() -> ElectronDeltaEtaTrkSeedSC            -> at ( m_raw_index )
  //  //<< "\tElectron::dEtaSCTrkAtVtx-SCEta+SCSeedEta=" << 
  //  //m_collection -> GetData() -> ElectronDeltaEtaTrkSC            -> at ( m_raw_index ) -
  //  //m_collection -> GetData() -> ElectronSCEta -> at( m_raw_index) +
  //  //m_collection -> GetData() -> ElectronSCSeedEta -> at(m_raw_index)
  //  << std::endl;
  return -1.0;
}
float Electron::DeltaPhi             (){ return -1.0; }
float Electron::HoE                  (){ return m_collection -> GetData() -> Electron_hoe                [m_raw_index]; }
float Electron::SigmaEtaEta          (){ return m_collection -> GetData() -> Electron_sieie              [m_raw_index]; } 
//FIXME from bitmap?
float Electron::Full5x5SigmaIEtaIEta (){ return -1.0; }
float Electron::Full5x5E1x5OverE5x5  (){ return -1.0; }
float Electron::Full5x5E2x5OverE5x5  (){ return -1.0; }
float Electron::LeadVtxDistXY        (){ return m_collection -> GetData() -> Electron_dxy            [m_raw_index]; }
float Electron::LeadVtxDistZ         (){ return m_collection -> GetData() -> Electron_dz             [m_raw_index]; }
//FIXME VtxDist?
float Electron::VtxDistXY            (){ return m_collection -> GetData() -> Electron_dxy            [m_raw_index]; }
float Electron::VtxDistZ             (){ return m_collection -> GetData() -> Electron_dz             [m_raw_index]; }
//
float Electron::Dist                 (){ return -1.0; }
float Electron::DCotTheta            (){ return -1.0; }
float Electron::ValidFrac            (){ return -1.0; }
float Electron::CaloEnergy           (){ return -1.0; }
float Electron::EcalEnergy           (){ return -1.0; }
float Electron::ESuperClusterOverP   (){ return -1.0; }
float Electron::NBrems               (){ return -1.0; }
float Electron::HasMatchedConvPhot   (){ return -1.0; }
float Electron::FBrem                (){ return -1.0; }
float Electron::BeamSpotDXY          (){ return -1.0; }
float Electron::BeamSpotDXYErr       (){ return -1.0; }
float Electron::GsfCtfScPixCharge    (){ return -1.0; }
float Electron::GsfScPixCharge       (){ return -1.0; }
float Electron::GsfCtfCharge         (){ return -1.0; }
float Electron::Classif              (){ return -1.0; }
float Electron::RhoForHEEP           (){ return m_collection -> GetData() -> fixedGridRhoFastjetAll; }
float Electron::DeltaEta             (){ return m_collection -> GetData() -> Electron_deltaEtaSC[m_raw_index]; }
					                                      					      
// Conversion variables		      	   		      		  	  				      
//FIXME: difference between these is...?
int    Electron::MissingHitsEG        (){ return m_collection -> GetData() -> Electron_lostHits[m_raw_index]; }
int    Electron::MissingHits          (){ return m_collection -> GetData() -> Electron_lostHits[m_raw_index]; }
					                                      					      
// Isolation variables		       	   		       			  				      
					                                      					      
float Electron::EcalIsoDR03          (){ return m_collection -> GetData() -> Electron_dr03EcalRecHitSumEt     [m_raw_index]; }
float Electron::HcalIsoD1DR03        (){ return m_collection -> GetData() -> Electron_dr03HcalDepth1TowerSumEt[m_raw_index]; }
float Electron::TrkIsoDR03           (){ return m_collection -> GetData() -> Electron_dr03TkSumPt             [m_raw_index]; }
//FIXME with Electron_pfRelIso03_chg/all or bitmap?
float Electron::PFChargedHadronIso03 (){ return -1.0; }
float Electron::PFPhotonIso03        (){ return -1.0; }
float Electron::PFNeutralHadronIso03 (){ return -1.0; }
float Electron::PFPUIso03            (){ return -1.0; }
//float Electron::PFChargedHadronIso04 (){ return m_collection -> GetData() -> ElectronPFChargedHadronIso04     -> at ( m_raw_index ); }
//float Electron::PFPhotonIso04        (){ return m_collection -> GetData() -> ElectronPFPhotonIso04            -> at ( m_raw_index ); }
//float Electron::PFNeutralHadronIso04 (){ return m_collection -> GetData() -> ElectronPFNeutralHadronIso04     -> at ( m_raw_index ); }

// GEN matching
//FIXME need to add checking on index
float Electron::MatchedGenParticlePt (){ return m_collection->GetData()->GenPart_pt[m_collection -> GetData() -> Electron_genPartIdx[m_raw_index]]; } 
float Electron::MatchedGenParticleEta(){ return m_collection->GetData()->GenPart_eta[m_collection -> GetData() -> Electron_genPartIdx[m_raw_index]]; } 
float Electron::MatchedGenParticlePhi(){ return m_collection->GetData()->GenPart_phi[m_collection -> GetData() -> Electron_genPartIdx[m_raw_index]]; }

//FIXME bitmap
float Electron::HEEPCaloIsolation(){ return -1.0; }
float Electron::HEEPCorrIsolation(){ return -1.0; }
float Electron::HEEP70TrackIsolation(){ return 1.0; }
float Electron::TrackPt          (){ return -1.0; }
float Electron::TrackEta         (){ return -1.0; }

// Fiduciality
// FIXME was using SCEta; from bitmap?
bool   Electron::IsEBFiducial     (){ return bool  ( fabs(Eta()) < 1.442 );}
bool   Electron::IsEEFiducial     (){ return bool (( fabs(Eta()) > 1.560 ) && 
						   ( fabs(Eta()) < 2.500 ));}

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
	 //<< "Uncorrected Pt = "    << object.SCPt()           << ", "
	 //<< "SCEnergy = "          << object.SCEnergy() << ", "
	 //<< "SCRawEnergy = "          << object.RawEnergy() << ", "
	 //<< "EcalEnergy = "          << object.EcalEnergy() << ", "
	 << "H/E = "          << object.HoE() << ", "
	 << "Eta = "   << object.Eta()           << ", "
	 //<< "SCEta = "   << object.SCEta()           << ", "
	 //<< "SCSeedEta = "   << object.SCSeedEta()           << ", "
	 << "Phi = "   << object.Phi()           << ", "
   << "PassLooseID = " << object.PassUserID(FAKE_RATE_HEEP_LOOSE,true) << ", "
   << "PassHEEP (builtin) = " << object.PassHEEPID() << ", "
   //<< "PassHEEP (manual) = " << object.PassUserID(HEEP70_MANUAL,true);
   ;
  return stream;
}
