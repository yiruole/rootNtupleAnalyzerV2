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

float   Electron::PtUncorr           (){ return ECorr() != 0 ? Pt()/ECorr() : Pt(); }
float   Electron::Energy             (){ return Pt() * cosh(Eta()); }
float   Electron::SCEta              (){ return m_collection->ReadArrayBranch<Float_t>("Electron_deltaEtaSC",m_raw_index)+m_collection->ReadArrayBranch<Float_t>("Electron_eta",m_raw_index); } 
float   Electron::SCPhi              (){ return m_collection->ReadArrayBranch<Float_t>("Electron_scPhi",m_raw_index); } 
float   Electron::SCEt               (){ return (m_collection->ReadArrayBranch<Float_t>("Electron_scEtOverPt",m_raw_index)+1)*Pt(); } 
float   Electron::IsEB               (){ return fabs(Eta()) < 1.5; } 
float   Electron::IsEE               (){ return fabs(Eta()) < 2.5; } 

int     Electron::Charge             (){ return m_collection->ReadArrayBranch<Int_t>("Electron_charge",m_raw_index); } 
float   Electron::R9                 (){ return m_collection->ReadArrayBranch<Float_t>("Electron_r9",m_raw_index); } 
float   Electron::SCEnergy           (){ return SCEt()*cosh(SCEta()); } 
// ratio of the calibrated energy/miniaod energy
float   Electron::ECorr              (){ return m_collection->ReadArrayBranch<Float_t>("Electron_eCorr",m_raw_index);} 
								      
// EGamma IDs
bool Electron::PassEGammaIDVeto     (){ return m_collection->ReadArrayBranch<Int_t>("Electron_cutBased",m_raw_index) > 0; } 
bool Electron::PassEGammaIDLoose    (){ return m_collection->ReadArrayBranch<Int_t>("Electron_cutBased",m_raw_index) > 1; } 
bool Electron::PassEGammaIDMedium   (){ return m_collection->ReadArrayBranch<Int_t>("Electron_cutBased",m_raw_index) > 2; } 
bool Electron::PassEGammaIDTight    (){ return m_collection->ReadArrayBranch<Int_t>("Electron_cutBased",m_raw_index) > 3; } 
bool Electron::PassHEEPID           (){ return m_collection->ReadArrayBranch<Bool_t>("Electron_cutBased_HEEP",m_raw_index); } 
														      
// ID variables			      	   		      		  	  				      
int Electron::GetHEEPBitmap() {
  return m_collection->ReadArrayBranch<Int_t>("Electron_vidNestedWPBitmapHEEP",m_raw_index);
}

bool Electron::PassHEEPIDCut(HEEPIDCut cut) {
  return 0x1 & (GetHEEPBitmap() >> static_cast<int>(cut));
}
bool Electron::PassHEEPGsfEleHadronicOverEMLinearCut2018   () {
  // using corrected quantities here, probably OK
  return bool ( HoE()            < (-0.4+0.4*fabs(SCEta()))*RhoForHEEP()/SCEnergy() + 0.05 );
}
bool Electron::PassHEEPGsfEleEmHadD1IsoRhoCut2018          () {
  float caloIsolation = EcalIsoDR03() + HcalIsoD1DR03();
  bool pass_caloIsolation = false;

  if   ( Pt()  < 50 ) {
    pass_caloIsolation = bool ( caloIsolation < ( 2.5 + 
          ( (0.15+0.07*fabs(SCEta())) * RhoForHEEP() ) ) );
  }
  else                { 
    pass_caloIsolation = bool ( caloIsolation < ( 2.5 + 
          ( (0.15+0.07*fabs(SCEta())) * RhoForHEEP() ) +
          ( 0.03 * (Pt() - 50.0 ) ) ) );
  }
  return pass_caloIsolation;
}

// EGamma
int Electron::GetEGammaIDBitmap() {
  return m_collection->ReadArrayBranch<Int_t>("Electron_vidNestedWPBitmap",m_raw_index);
}
bool Electron::PassEGammaIDLooseCut(EGammaIDCut cut) {
  unsigned int result = 0x7 & (GetEGammaIDBitmap() >> (static_cast<int>(cut)*3) );
  if(result > 1)
    return true;
  return false;
}


bool  Electron::EcalSeed             (){ return false; }
float Electron::DeltaEta             (){ return m_collection->ReadArrayBranch<Float_t>("Electron_deltaEtaSC",m_raw_index); }
float Electron::HoE                  (){ return m_collection->ReadArrayBranch<Float_t>("Electron_hoe",m_raw_index); }
float Electron::Full5x5SigmaIEtaIEta (){ return m_collection->ReadArrayBranch<Float_t>("Electron_sieie",m_raw_index); }
float Electron::LeadVtxDistXY        (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dxy",m_raw_index); }
float Electron::LeadVtxDistZ         (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dz",m_raw_index); }
bool Electron::HasMatchedConvPhot    (){ return !(m_collection->ReadArrayBranch<Bool_t>("Electron_convVeto",m_raw_index)); }
float Electron::RhoForHEEP           (){ return m_collection->ReadValueBranch<Float_t>("fixedGridRhoFastjetAll"); }
int Electron::SeedGain               (){ return m_collection->ReadArrayBranch<UChar_t>("Electron_seedGain",m_raw_index); }

float Electron::DEScaleUp            (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dEscaleUp",m_raw_index); }
float Electron::DEScaleDown          (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dEscaleDown",m_raw_index); }
float Electron::DESigmaUp            (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dEsigmaUp",m_raw_index); }
float Electron::DESigmaDown          (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dEsigmaDown",m_raw_index); }
float Electron::PtDESigmaUp          (){ return (Energy()-DESigmaUp())/cosh(Eta()); }
float Electron::PtDESigmaDown        (){ return (Energy()-DESigmaDown())/cosh(Eta()); }

// Conversion variables		      	   		      		  	  				      
int    Electron::MissingHits          (){ return m_collection->ReadArrayBranch<UChar_t>("Electron_lostHits",m_raw_index); }
					                                      					      
// Isolation variables		       	   		       			  				      
					                                      					      
float Electron::EcalIsoDR03          (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dr03EcalRecHitSumEt"     , m_raw_index); }
float Electron::HcalIsoD1DR03        (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dr03HcalDepth1TowerSumEt", m_raw_index); }
float Electron::TrkIsoDR03           (){ return m_collection->ReadArrayBranch<Float_t>("Electron_dr03TkSumPt"             , m_raw_index); }
float Electron::PFRelIso03Charged    (){ return m_collection->ReadArrayBranch<Float_t>("Electron_pfRelIso03_chg"          , m_raw_index); }
float Electron::PFRelIso03All        (){ return m_collection->ReadArrayBranch<Float_t>("Electron_pfRelIso03_all"          , m_raw_index); }

// GEN matching
int Electron::NumGenParticles() { return 1; } //FIXME: this is either 1 matched particle or nothing matched
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
bool   Electron::IsEBFiducial     (){ return fabs(SCEta()) < 1.442;}
bool   Electron::IsEEFiducial     (){ return ( fabs(SCEta()) > 1.560 ) && 
						   ( fabs(SCEta()) < 2.500 );}

double Electron::EnergyRes (){
  // SIC: from https://arxiv.org/pdf/1502.02701v1.pdf
  //      page 23. SIM worst case: sqrt(2)*2.93/90.75 GeV = 4.6%
  return 0.05;
}
// Energy resolution scale factors
double Electron::EnergyResScaleFactor (){ 
  // SIC: changed May 12, 2015 to 10% as per LQ1 2012 CWR comment; see EGM-13-001 and email thread
  if      ( IsEBFiducial() ) return 1.1;
  else if ( IsEEFiducial() ) return 1.1;
  else                       return 1.000;
}

double Electron::EnergyResScaleError  (){ 
  return 0.000;
}

double Electron::EnergyScaleFactor (){ 
  // SIC: changed May 12, 2015 to 2% as per LQ1 2012 CWR comment; see EGM-13-001 and email thread
  if      ( IsEBFiducial() ) return 0.02;
  else if ( IsEEFiducial() ) return 0.02;
  else                       return 0.000;
}

std::ostream& operator<<(std::ostream& stream, Electron& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "    << object.Pt ()           << ", "
	 //<< "PtHeep = "    << object.PtHeep ()           << ", "
	 << "SC Et = "    << object.SCEt()           << ", "
	 << "SCEta = "   << object.SCEta()           << ", "
	 << "Phi = "   << object.Phi()           << ", "
	 << "Eta = "   << object.Eta()           << ", "
	 << "SC Energy = "          << object.SCEnergy() << ", "
   << "ECorr (calibEnergy/MiniAODEnergy) = " << object.ECorr() << ", "
	 << "H/E = "          << object.HoE() << ", "
	 << "dxy = "          << object.LeadVtxDistXY() << ", "
   //<< "PassLooseID = " << object.PassUserID(FAKE_RATE_HEEP_LOOSE) << ", "
   << "PassEGLooseID = " << object.PassUserID(EGAMMA_BUILTIN_LOOSE) << ", "
   << "PassHEEP (builtin) = " << object.PassHEEPID() << "; ";
  // << "Failing HEEP cuts = ";
  //for(int cut=0; cut < 12; ++cut)
  //  if(!object.PassHEEPIDCut(static_cast<Electron::HEEPIDCut>(cut)))
  //    stream << object.GetHEEPCutName(static_cast<Electron::HEEPIDCut>(cut)) << ", ";
  // //<< "PassHEEP (manual) = " << object.PassUserID(HEEP70_MANUAL,true);
  //stream << "HEEPCaloIso = " << object.HEEPCaloIsolation() << " < " << 2+0.03*object.SCEt()+0.28*object.RhoForHEEP() << " (bar), ";
  stream << "EGPFIso = " << object.PFRelIso03All() << " < " << 0.112+0.506/object.Pt() << " (bar)";
  return stream;
}
