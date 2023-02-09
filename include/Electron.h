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
  
  float PtUncorr             ();
  float Energy               ();
  float SCEta                (); 
  float SCPhi                (); 
  float SCEt                 (); 
  float SCEnergy             (); 
  float ECorr                ();
  int Charge                 (); 
  float R9                   ();

  // Energy resolution scale factors

  double EnergyRes () override;
  double EnergyResScaleFactor () override;
  double EnergyResScaleError  () override;
  double EnergyScaleFactor    () override;
  
  // IDs 

  bool   PassUserID ( ID id, bool verbose = false );
  bool   IsEBFiducial();
  bool   IsEEFiducial();
  
  // ID variables		
  int GetHEEPBitmap();
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
    GsfEleEcalDrivenCut                  = 11
  };
  std::string GetHEEPCutName(HEEPIDCut cut) {
    if(cut==HEEPIDCut::MinPtCut)
      return "MinPtCut";
    else if(cut==HEEPIDCut::GsfEleSCEtaMultiRangeCut)
      return "GsfEleSCEtaMultiRangeCut";
    else if(cut==HEEPIDCut::GsfEleDEtaInSeedCut)
      return "GsfEleDEtaInSeedCut";
    else if(cut==HEEPIDCut::GsfEleDPhiInCut)
      return "GsfEleDPhiInCut";
    else if(cut==HEEPIDCut::GsfEleFull5x5SigmaIEtaIEtaWithSatCut)
      return "GsfEleFull5x5SigmaIEtaIEtaWithSatCut";
    else if(cut==HEEPIDCut::GsfEleFull5x5E2x5OverE5x5WithSatCut)
      return "GsfEleFull5x5E2x5OverE5x5WithSatCut";
    else if(cut==HEEPIDCut::GsfEleHadronicOverEMLinearCut)
      return "GsfEleHadronicOverEMLinearCut";
    else if(cut==HEEPIDCut::GsfEleTrkPtIsoCut)
      return "GsfEleTrkPtIsoCut";
    else if(cut==HEEPIDCut::GsfEleEmHadD1IsoRhoCut)
      return "GsfEleEmHadD1IsoRhoCut";
    else if(cut==HEEPIDCut::GsfEleDxyCut)
      return "GsfEleDxyCut";
    else if(cut==HEEPIDCut::GsfEleMissingHitsCut)
      return "GsfEleMissingHitsCut";
    else if(cut==HEEPIDCut::GsfEleEcalDrivenCut)
      return "GsfEleEcalDrivenCut";
    else
      return "unknown";
  }
  bool PassHEEPIDCut(HEEPIDCut cut);
  bool PassHEEPMinPtCut                            (){ return PassHEEPIDCut(HEEPIDCut::MinPtCut); }
  bool PassHEEPGsfEleSCEtaMultiRangeCut            (){ return PassHEEPIDCut(HEEPIDCut::GsfEleSCEtaMultiRangeCut); }
  bool PassHEEPGsfEleDEtaInSeedCut                 (){ return PassHEEPIDCut(HEEPIDCut::GsfEleDEtaInSeedCut); }
  bool PassHEEPGsfEleDPhiInCut                     (){ return PassHEEPIDCut(HEEPIDCut::GsfEleDPhiInCut); }
  bool PassHEEPGsfEleFull5x5SigmaIEtaIEtaWithSatCut(){ return PassHEEPIDCut(HEEPIDCut::GsfEleFull5x5SigmaIEtaIEtaWithSatCut); }
  bool PassHEEPGsfEleFull5x5E2x5OverE5x5WithSatCut (){ return PassHEEPIDCut(HEEPIDCut::GsfEleFull5x5E2x5OverE5x5WithSatCut); }
  bool PassHEEPGsfEleHadronicOverEMLinearCut       (){ return PassHEEPIDCut(HEEPIDCut::GsfEleHadronicOverEMLinearCut); }
  bool PassHEEPGsfEleTrkPtIsoCut                   (){ return PassHEEPIDCut(HEEPIDCut::GsfEleTrkPtIsoCut); }
  bool PassHEEPGsfEleEmHadD1IsoRhoCut              (){ return PassHEEPIDCut(HEEPIDCut::GsfEleEmHadD1IsoRhoCut); }
  bool PassHEEPGsfEleDxyCut                        (){ return PassHEEPIDCut(HEEPIDCut::GsfEleDxyCut); }
  bool PassHEEPGsfEleMissingHitsCut                (){ return PassHEEPIDCut(HEEPIDCut::GsfEleMissingHitsCut); }
  bool PassHEEPEcalDrivenCut                       (){ return PassHEEPIDCut(HEEPIDCut::GsfEleEcalDrivenCut); }
  bool PassHEEPGsfEleHadronicOverEMLinearCut2018   ();
  bool PassHEEPGsfEleEmHadD1IsoRhoCut2018          ();

  // ID variables		
  int GetEGammaIDBitmap();
  // EventsTree.GetBranch('Electron_vidNestedWPBitmap').Print()
  enum class EGammaIDCut {
    MinPtCut                             = 0,
    GsfEleSCEtaMultiRangeCut             = 1,
    GsfEleDEtaInSeedCut                  = 2,
    GsfEleDPhiInCut                      = 3,
    GsfEleFull5x5SigmaIEtaIEtaCut        = 4,
    GsfEleHadronicOverEMEnergyScaledCut  = 5,
    GsfEleEInverseMinusPInverseCut       = 6,
    GsfEleRelPFIsoScaledCut              = 7,
    GsfEleConversionVetoCut              = 8,
    GsfEleMissingHitsCut                 = 9
  };
  std::string GetEGammaIDCutName(EGammaIDCut cut) {
    if(cut==EGammaIDCut::MinPtCut)
      return "MinPtCut";
    else if(cut==EGammaIDCut::GsfEleSCEtaMultiRangeCut)
      return "GsfEleSCEtaMultiRangeCut";
    else if(cut==EGammaIDCut::GsfEleDEtaInSeedCut)
      return "GsfEleDEtaInSeedCut";
    else if(cut==EGammaIDCut::GsfEleDPhiInCut)
      return "GsfEleDPhiInCut";
    else if(cut==EGammaIDCut::GsfEleFull5x5SigmaIEtaIEtaCut)
      return "GsfEleFull5x5SigmaIEtaIEtaCut";
    else if(cut==EGammaIDCut::GsfEleHadronicOverEMEnergyScaledCut)
      return "GsfEleHadronicOverEMEnergyScaledCut";
    else if(cut==EGammaIDCut::GsfEleEInverseMinusPInverseCut)
      return "GsfEleEInverseMinusPInverseCut";
    else if(cut==EGammaIDCut::GsfEleRelPFIsoScaledCut)
      return "GsfEleRelPFIsoScaledCut";
    else if(cut==EGammaIDCut::GsfEleConversionVetoCut)
      return "GsfEleConversionVetoCut";
    else if(cut==EGammaIDCut::GsfEleMissingHitsCut)
      return "GsfEleMissingHitsCut";
    else
      return "unknown";
  }
  bool PassEGammaIDLooseCut(EGammaIDCut cut);
  bool PassEGammaIDLooseMinPtCut                            (){ return PassEGammaIDLooseCut(EGammaIDCut::MinPtCut); }
  bool PassEGammaIDLooseGsfEleSCEtaMultiRangeCut            (){ return PassEGammaIDLooseCut(EGammaIDCut::GsfEleSCEtaMultiRangeCut); }
  bool PassEGammaIDLooseGsfEleDEtaInSeedCut                 (){ return PassEGammaIDLooseCut(EGammaIDCut::GsfEleDEtaInSeedCut); }
  bool PassEGammaIDLooseGsfEleDPhiInCut                     (){ return PassEGammaIDLooseCut(EGammaIDCut::GsfEleDPhiInCut); }
  bool PassEGammaIDLooseGsfEleFull5x5SigmaIEtaIEtaCut       (){ return PassEGammaIDLooseCut(EGammaIDCut::GsfEleFull5x5SigmaIEtaIEtaCut); }
  bool PassEGammaIDLooseGsfEleHadronicOverEMScaledCut       (){ return PassEGammaIDLooseCut(EGammaIDCut::GsfEleHadronicOverEMEnergyScaledCut); }
  bool PassEGammaIDLooseGsfEleEInverseMinusPInverseCut      (){ return PassEGammaIDLooseCut(EGammaIDCut::GsfEleEInverseMinusPInverseCut); }
  bool PassEGammaIDLooseGsfEleRelPFIsoScaledCut             (){ return PassEGammaIDLooseCut(EGammaIDCut::GsfEleRelPFIsoScaledCut); }
  bool PassEGammaIDLooseGsfEleConversionVetoCut             (){ return PassEGammaIDLooseCut(EGammaIDCut::GsfEleConversionVetoCut); }
  bool PassEGammaIDLooseGsfEleMissingHitsCut                (){ return PassEGammaIDLooseCut(EGammaIDCut::GsfEleMissingHitsCut); }

  float IsEB                 ();
  float IsEE                 ();
  bool   EcalSeed            ();
  float DeltaEta             ();
  float HoE                  ();
  float Full5x5SigmaIEtaIEta ();
  float LeadVtxDistXY        ();
  float LeadVtxDistZ         ();
  bool  HasMatchedConvPhot   ();
  float RhoForHEEP           ();
  int SeedGain             ();

  float DEScaleUp            ();
  float DEScaleDown          ();
  float DESigmaUp            ();
  float DESigmaDown          ();
  float PtDESigmaUp          ();
  float PtDESigmaDown        ();


  // EGamma bits

  int    PassEGammaIDEoP      ();
  bool   PassEGammaIDLoose    ();
  bool   PassEGammaIDMedium   ();
  bool   PassEGammaIDTight    ();
  int    PassEGammaIDTrigTight();
  int    PassEGammaIDTrigWP70 ();
  bool   PassEGammaIDVeto     ();
  bool   PassHEEPID           ();
  
  // Conversion variables		      	
  
  int    MissingHits          ();
  
  // Isolation variables		       	
  
  float EcalIsoDR03          ();
  float HcalIsoD1DR03        ();
  float TrkIsoDR03           ();
  
  float PFRelIso03Charged    ();
  float PFRelIso03All        ();

  //float PFChargedHadronIso04 ();
  //float PFPhotonIso04        ();
  //float PFNeutralHadronIso04 ();
  
  
  // GEN matching
  int    NumGenParticles();
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

 private:

  float m_rawSuperClusterPt;

  bool   PassUserID_BuiltIn_HEEPv7p0    (bool verbose);
  bool   PassUserID_HEEPv6p1            (bool verbose);
  bool   PassUserID_HEEP                (bool verbose);
  bool   PassUserID_HEEP_2018           (bool verbose);
  bool   PassUserID_BuiltIn_EGamma      ( ID id);
  bool   PassUserID_EGamma              ( ID id,  bool verbose);
  bool   PassUserID_MVA                 (bool verbose);
  bool   PassUserID_ECALFiducial        (bool verbose);
  bool   PassUserID_FakeRateLooseID     (bool verbose);
  bool   PassUserID_FakeRateVeryLooseID (bool verbose);
  bool   PassUserID_FakeRateEGMLooseID  (bool verbose);
  bool   PassUserID_FakeRateVeryLooseEGMLooseID(bool verbose);
};

std::ostream& operator<< (std::ostream& stream, Electron& object);

#endif 
