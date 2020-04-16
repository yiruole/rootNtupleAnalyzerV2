#ifndef ELECTRON_H
#define ELECTRON_H

#include "Object.h"
#include "IDTypes.h"
#include "Collection.h"

class Electron : public Object {
  
 public: 
  Electron ();
  Electron (Collection& c, unsigned short i, short j = 0);

  // Kinematic variables
  
  float PtHeep               ();
  float SCEta                (); 
  float SCSeedEta            (); 
  float SCPhi                (); 
  float SCPt                 (); 
  float SCEnergy             (); 
  float ECorr                ();
  float Charge               (); 
  float R9                   ();

  // Energy resolution scale factors

  float EnergyResScaleFactor ();
  float EnergyResScaleError  ();
  float EnergyScaleFactor    ();
  
  // IDs 

  bool   PassUserID ( ID id, bool verbose = false );
  bool   IsEBFiducial();
  bool   IsEEFiducial();
  
  // ID variables		
  // EventsTree.GetBranch('Electron_vidNestedWPBitmapHEEP').Print()
  enum class HEEPIDCut {
    MinPtCut                             = 0,
    GsfEleSCEtaMultiRangeCut             = 1,
    GsfEleDEtaInSeedCut                  = 2,
    GsfEleDPhiInCut                      = 3,
    GsfEleFull5x5SigmaIEtaIEtaWithSatCut = 4,
    GsfEleFull5x5E2x5OverE5x5WithSatCut  = 5,
    GsfEleHadronicOverEMLinearCut        = 6,
    GsfEleTrkPtIsoCut                    = 7,
    GsfEleEmHadD1IsoRhoCut               = 8,
    GsfEleDxyCut                         = 9,
    GsfEleMissingHitsCut                 = 10,
    GsfEleEcalDrivenCut                  = 11,
  };

  bool PassHEEPIDCut(HEEPIDCut cut);
  bool PassHEEPMinPtCut                            ();
  bool PassHEEPGsfEleSCEtaMultiRangeCut            (); 
  bool PassHEEPGsfEleDEtaInSeedCut                 (); 
  bool PassHEEPGsfEleDPhiInCut                     (); 
  bool PassHEEPGsfEleFull5x5SigmaIEtaIEtaWithSatCut(); 
  bool PassHEEPGsfEleFull5x5E2x5OverE5x5WithSatCut (); 
  bool PassHEEPGsfEleHadronicOverEMLinearCut       (); 
  bool PassHEEPGsfEleTrkPtIsoCut                   (); 
  bool PassHEEPGsfEleEmHadD1IsoRhoCut              (); 
  bool PassHEEPGsfEleDxyCut                        (); 
  bool PassHEEPGsfEleMissingHitsCut                (); 
  bool PassHEEPEcalDrivenCut                       ();

  float IsEB                 ();
  float IsEE                 ();
  bool   EcalSeed            ();
  float DeltaEta             ();
  float DeltaEtaSeed         ();
  float DeltaPhi             ();
  float HoE                  ();
  //float SigmaIEtaIEta        ();
  float Full5x5SigmaIEtaIEta ();
  float SigmaEtaEta          ();
  //float E1x5OverE5x5         ();
  //float E2x5OverE5x5         ();
  float Full5x5E1x5OverE5x5     ();
  float Full5x5E2x5OverE5x5     ();
  float LeadVtxDistXY        ();
  float LeadVtxDistZ         ();
  float VtxDistXY            ();
  float VtxDistZ             ();
  float Dist                 ();
  float DCotTheta            ();
  float ValidFrac            ();
  float CaloEnergy           ();
  float EcalEnergy           ();
  float ESuperClusterOverP   ();
  float FBrem                ();
  float NBrems               ();
  bool  HasMatchedConvPhot   ();
  float BeamSpotDXY          ();
  float BeamSpotDXYErr       ();
  float GsfCtfScPixCharge    ();
  float GsfScPixCharge       ();
  float GsfCtfCharge         ();
  float Classif              ();
  float  RhoForHEEP           ();


  // EGamma bits

  int    PassEGammaIDEoP      ();
  int    PassEGammaIDLoose    ();
  int    PassEGammaIDMedium   ();
  int    PassEGammaIDTight    ();
  int    PassEGammaIDTrigTight();
  int    PassEGammaIDTrigWP70 ();
  int    PassEGammaIDVeto     ();
  int    PassHEEPID           ();
  
  // Conversion variables		      	
  
  int    MissingHitsEG        ();
  int    MissingHits          ();
  
  // Isolation variables		       	
  
  float EcalIsoDR03          ();
  float HcalIsoD1DR03        ();
  float TrkIsoDR03           ();
  
  float PFChargedHadronIso03 ();
  float PFPhotonIso03        ();
  float PFNeutralHadronIso03 ();
  float PFPUIso03            ();

  //float PFChargedHadronIso04 ();
  //float PFPhotonIso04        ();
  //float PFNeutralHadronIso04 ();
  
  
  // GEN matching
  UInt_t NumGenParticles();
  int    MatchedGenParticleIdx();
  bool   IsValidGenParticleIdx(int index);
  float  MatchedGenParticlePt (); 
  float  MatchedGenParticleEta(); 
  float  MatchedGenParticlePhi();

  
  // HLT matching

  // Isolation variables

  float HEEPCaloIsolation    ();
  float HEEPCorrIsolation    ();
  float HEEP70TrackIsolation ();
  float TrackPt              ();
  float TrackEta             ();
  float RawEnergy            ();

 private:

  float m_rawSuperClusterPt;

  bool   PassUserID_BuiltIn_HEEPv7p0   (bool verbose);
  bool   PassUserID_HEEPv6p1           (bool verbose);
  bool   PassUserID_HEEP               (bool verbose);
  bool   PassUserID_HEEP_2018          (bool verbose);
  bool   PassUserID_BuiltIn_EGamma     ( ID id);
  bool   PassUserID_EGamma             ( ID id,  bool verbose);
  bool   PassUserID_MVA                (bool verbose);
  bool   PassUserID_ECALFiducial       (bool verbose);
  bool   PassUserID_FakeRateLooseID    (bool verbose);
};

std::ostream& operator<< (std::ostream& stream, Electron& object);

#endif 
