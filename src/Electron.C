#include "Electron.h"
#include "Object.h"
#include "IDTypes.h"
#include "TVector3.h"

Electron::Electron ():
  Object()
  // m_rawSuperClusterPt(0.)
{}

Electron::Electron (Collection & c, unsigned short i, short j, Long64_t current_entry ):
  Object(c,i,"Electron") {
  //if ( m_collection -> GetData() -> ElectronCaloEnergy -> at ( m_raw_index ) == 0. ) m_rawSuperClusterPt = 0.;
  //else { 
  //  m_rawSuperClusterPt = ( ( m_collection -> GetData() -> ElectronPtHeep       -> at ( m_raw_index ) ) * 
  //			    ( m_collection -> GetData() -> ElectronSCRawEnergy  -> at ( m_raw_index ) ) / 
  //			    ( m_collection -> GetData() -> ElectronCaloEnergy   -> at ( m_raw_index ) ) );
  //}
    ptLeaf = m_collection->GetData()->fReader.GetTree()->GetLeaf("GenPart_pt");
    etaLeaf = m_collection->GetData()->fReader.GetTree()->GetLeaf("GenPart_eta");
    phiLeaf = m_collection->GetData()->fReader.GetTree()->GetLeaf("GenPart_phi");
    nGenPartLeaf = m_collection->GetData()->fReader.GetTree()->GetLeaf("nGenPart");
    genPartIdxLeaf = m_collection->GetData()->fReader.GetTree()->GetLeaf("Electron_genPartIdx");
    // load current entry
    if(current_entry >= 0) {
      ptLeaf->GetBranch()->GetEntry(current_entry);
      etaLeaf->GetBranch()->GetEntry(current_entry);
      phiLeaf->GetBranch()->GetEntry(current_entry);
      nGenPartLeaf->GetBranch()->GetEntry(current_entry);
      genPartIdxLeaf->GetBranch()->GetEntry(current_entry);
    }
}

// Kinematic variables

float & Electron::Pt                 (){ return m_collection -> GetData() -> Electron_pt      [m_raw_index]; } 
float & Electron::Eta                (){ return m_collection -> GetData() -> Electron_eta     [m_raw_index]; } 
float & Electron::Phi                (){ return m_collection -> GetData() -> Electron_phi     [m_raw_index]; } 
float   Electron::PtHeep             (){ return CaloEnergy()/cosh(SCEta()); }
float   Electron::SCEta              (){ return m_collection -> GetData() -> Electron_scEta     [m_raw_index]; } 
float   Electron::SCSeedEta          (){ return -1.0; } 
float   Electron::SCPhi              (){ return m_collection -> GetData() -> Electron_scPhi     [m_raw_index]; } 
float   Electron::SCPt               (){ return SCEnergy()/cosh(SCEta()); } 
float   Electron::IsEB               (){ return fabs(Eta()) < 1.5; } 
float   Electron::IsEE               (){ return fabs(Eta()) < 2.5; } 

float   Electron::Charge             (){ return m_collection -> GetData() -> Electron_charge    [m_raw_index]; } 
float   Electron::R9                 (){ return m_collection -> GetData() -> Electron_r9        [m_raw_index]; } 
float   Electron::RawEnergy          (){ return -1.0; } 
float   Electron::SCEnergy           (){ return m_collection -> GetData() -> Electron_scEnergy  [m_raw_index];} 
float   Electron::ECorr              (){ return m_collection -> GetData() -> Electron_eCorr     [m_raw_index];} 
								      
// EGamma bits													      
int    Electron::PassEGammaIDLoose    (){ return m_collection -> GetData() -> Electron_cutBased     [m_raw_index]; } 
int    Electron::PassEGammaIDMedium   (){ return m_collection -> GetData() -> Electron_cutBased     [m_raw_index]; } 
int    Electron::PassEGammaIDTight    (){ return m_collection -> GetData() -> Electron_cutBased     [m_raw_index]; } 
int    Electron::PassEGammaIDVeto     (){ return m_collection -> GetData() -> Electron_cutBased     [m_raw_index]; } 
int    Electron::PassHEEPID           (){ return m_collection -> GetData() -> Electron_cutBased_HEEP[m_raw_index]; } 
														      
// ID variables			      	   		      		  	  				      
bool Electron::PassIDCut(HEEPIDCut cut) {
  return 0x1 & (m_collection -> GetData() -> Electron_vidNestedWPBitmapHEEP[m_raw_index] >> static_cast<int>(cut));
}
//bool   Electron::EcalSeed             (){ return m_collection -> GetData() -> ElectronHasEcalDrivenSeed        -> at ( m_raw_index ); }
//bool   Electron::EcalDriven           (){ return m_collection -> GetData() -> ElectronIsEcalDriven             -> at ( m_raw_index ); }
bool   Electron::EcalSeed             (){ return false; }
bool   Electron::EcalDriven           (){ return PassIDCut(HEEPIDCut::GsfEleEcalDrivenCut); }
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
// -999 --> indicates that it's not available in NanoAOD
float Electron::DeltaPhi             (){ return -999; }
float Electron::HoE                  (){ return m_collection -> GetData() -> Electron_hoe                [m_raw_index]; }
//FIXME remove
float Electron::SigmaEtaEta          (){ return -999; } 

float Electron::Full5x5SigmaIEtaIEta (){ return m_collection -> GetData() -> Electron_sieie              [m_raw_index]; }
float Electron::Full5x5E1x5OverE5x5  (){ return -999; }
float Electron::Full5x5E2x5OverE5x5  (){ return -999; }
float Electron::LeadVtxDistXY        (){ return m_collection -> GetData() -> Electron_dxy            [m_raw_index]; }
float Electron::LeadVtxDistZ         (){ return m_collection -> GetData() -> Electron_dz             [m_raw_index]; }
//
float Electron::VtxDistXY            (){ return -999; }
float Electron::VtxDistZ             (){ return -999; }
//
float Electron::Dist                 (){ return -999; }
float Electron::DCotTheta            (){ return -999; }
float Electron::ValidFrac            (){ return -999; }
float Electron::CaloEnergy           (){ return m_collection -> GetData() -> Electron_caloEnergy [m_raw_index]; }
float Electron::EcalEnergy           (){ return -999; }
float Electron::ESuperClusterOverP   (){ return -999; }
float Electron::NBrems               (){ return -999; }
float Electron::HasMatchedConvPhot   (){ return !(m_collection -> GetData() -> Electron_convVeto[m_raw_index]); }
float Electron::FBrem                (){ return -999; }
float Electron::BeamSpotDXY          (){ return -999; }
float Electron::BeamSpotDXYErr       (){ return -999; }
float Electron::GsfCtfScPixCharge    (){ return -999; }
float Electron::GsfScPixCharge       (){ return -999; }
float Electron::GsfCtfCharge         (){ return -999; }
float Electron::Classif              (){ return -999; }
float Electron::RhoForHEEP           (){ return *(m_collection -> GetData() -> fixedGridRhoFastjetAll); }
float Electron::DeltaEta             (){ return m_collection -> GetData() -> Electron_deltaEtaSC[m_raw_index]; }
					                                      					      
// Conversion variables		      	   		      		  	  				      
//FIXME: difference between these is...?
int    Electron::MissingHitsEG        (){ return m_collection -> GetData() -> Electron_lostHits[m_raw_index]; }
int    Electron::MissingHits          (){ return m_collection -> GetData() -> Electron_lostHits[m_raw_index]; }
					                                      					      
// Isolation variables		       	   		       			  				      
					                                      					      
float Electron::EcalIsoDR03          (){ return m_collection -> GetData() -> Electron_dr03EcalRecHitSumEt     [m_raw_index]; }
float Electron::HcalIsoD1DR03        (){ return m_collection -> GetData() -> Electron_dr03HcalDepth1TowerSumEt[m_raw_index]; }
float Electron::TrkIsoDR03           (){ return m_collection -> GetData() -> Electron_dr03TkSumPt             [m_raw_index]; }
float Electron::PFChargedHadronIso03 (){ return m_collection -> GetData() -> Electron_pfRelIso03_chg [m_raw_index]; }
float Electron::PFPhotonIso03        (){ return -999; }
float Electron::PFNeutralHadronIso03 (){ return -999; }
float Electron::PFPUIso03            (){ return -999; }

// GEN matching
UInt_t Electron::NumGenParticles() {  }
int    Electron::MatchedGenParticleIdx(){ return static_cast<int*>(genPartIdxLeaf->GetValuePointer())[m_raw_index]; }
bool   Electron::IsValidGenParticleIdx(int index) {
  if(MatchedGenParticleIdx() < NumGenParticles() && MatchedGenParticleIdx() >= 0)
    return true;
  return false;
}
float  Electron::MatchedGenParticlePt (){ if(IsValidGenParticleIdx(MatchedGenParticleIdx())) return static_cast<float*>(ptLeaf->GetValuePointer())[m_raw_index]; else return -1;} 
float  Electron::MatchedGenParticleEta(){ if(IsValidGenParticleIdx(MatchedGenParticleIdx())) return static_cast<float*>(etaLeaf->GetValuePointer())[m_raw_index]; else return -1;} 
float  Electron::MatchedGenParticlePhi(){ if(IsValidGenParticleIdx(MatchedGenParticleIdx())) return static_cast<float*>(phiLeaf->GetValuePointer())[m_raw_index]; else return -1;}

float Electron::HEEPCaloIsolation(){ return EcalIsoDR03() + HcalIsoD1DR03(); }
float Electron::HEEPCorrIsolation(){ return (HEEPCaloIsolation() - (2.0 + ( 0.03 * Pt() ) + (0.28 * RhoForHEEP()))); }
float Electron::HEEP70TrackIsolation(){ return m_collection->GetData()->Electron_dr03TkSumPtHEEP[m_raw_index]; }
float Electron::TrackPt          (){
  float px = m_collection -> GetData() -> Electron_trkPx [m_raw_index];
  float py = m_collection -> GetData() -> Electron_trkPy [m_raw_index];
  float pz = m_collection -> GetData() -> Electron_trkPz [m_raw_index];
  TVector3 v1;
  v1.SetXYZ(px,py,pz);
  return v1.Pt();
}
float Electron::TrackEta         (){
  float px = m_collection -> GetData() -> Electron_trkPx [m_raw_index];
  float py = m_collection -> GetData() -> Electron_trkPy [m_raw_index];
  float pz = m_collection -> GetData() -> Electron_trkPz [m_raw_index];
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
