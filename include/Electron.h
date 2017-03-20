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
  
  float & Pt                 ();
  float & PtHeep             ();
  float & Eta                (); 
  float & Phi                (); 
  float SCEta                (); 
  float SCPhi                (); 
  float SCEnergy             (); 
  float Charge               (); 

  // Energy resolution scale factors

  float EnergyResScaleFactor ();
  float EnergyResScaleError  ();
  float EnergyScaleFactor    ();
  
  // IDs 

  bool   PassUserID ( ID id, bool verbose = false );
  bool   IsEBFiducial();
  bool   IsEEFiducial();
  
  // ID variables		
  
  float IsEB                 ();
  float IsEE                 ();
  bool   EcalSeed            ();
  bool   EcalDriven          ();
  float DeltaEta             ();
  float DeltaEtaSeed         ();
  float DeltaPhi             ();
  float HoE                  ();
  float SigmaIEtaIEta        ();
  float Full5x5SigmaIEtaIEta ();
  float SigmaEtaEta          ();
  float E1x5OverE5x5         ();
  float E2x5OverE5x5         ();
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
  float HasMatchedConvPhot   ();
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

  float PFChargedHadronIso04 ();
  float PFPhotonIso04        ();
  float PFNeutralHadronIso04 ();
  
  
  // GEN matching

  float MatchedGenParticlePt (); 
  float MatchedGenParticleEta(); 
  float MatchedGenParticlePhi();

  
  // HLT matching

  // Isolation variables

  float HEEPCaloIsolation    ();
  float HEEPCorrIsolation    ();
  float HEEP70TrackIsolation ();
  float TrackPt              ();
  float RawEnergy            ();

 private:

  float m_rawSuperClusterPt;

  bool   PassUserID_BuiltIn_HEEPv7p0   (bool verbose);
  bool   PassUserID_HEEPv6p1           (bool verbose);
  bool   PassUserID_HEEP               (bool verbose);
  bool   PassUserID_HEEPv5p1           (bool verbose);
  bool   PassUserID_BuiltIn_EGamma     ( ID id);
  bool   PassUserID_EGamma             ( ID id,  bool verbose);
  bool   PassUserID_MVA                (bool verbose);
  bool   PassUserID_ECALFiducial       (bool verbose);
  bool   PassUserID_FakeRateLooseID    (bool verbose);

};

std::ostream& operator<< (std::ostream& stream, Electron& object);

#endif 
