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
  
  double & Pt                 ();
  double & Eta                (); 
  double & Phi                (); 
  double SCEta                (); 
  double SCPhi                (); 
  double Charge               (); 

  // Energy resolution scale factors

  double EnergyResScaleFactor ();
  double EnergyResScaleError  ();
  double EnergyScaleFactor    ();
  
  // IDs 

  bool   PassUserID ( ID id, bool verbose = false );
  bool   IsEBFiducial();
  bool   IsEEFiducial();
  
  // ID variables		
  
  double IsEB                 ();
  double IsEE                 ();
  bool   EcalSeed             ();
  double DeltaEta             ();
  double DeltaPhi             ();
  double HoE                  ();
  double SigmaIEtaIEta        ();
  double SigmaEtaEta          ();
  double E1x5OverE5x5         ();
  double E2x5OverE5x5         ();
  double LeadVtxDistXY        ();
  double LeadVtxDistZ         ();
  double VtxDistXY            ();
  double VtxDistZ             ();
  double Dist                 ();
  double DCotTheta            ();
  double ValidFrac            ();
  double CaloEnergy           ();
  double ESuperClusterOverP   ();
  double FBrem                ();
  double NBrems               ();
  double HasMatchedConvPhot   ();
  double BeamSpotDXY          ();
  double BeamSpotDXYErr       ();
  double GsfCtfScPixCharge    ();
  double GsfScPixCharge       ();
  double GsfCtfCharge         ();
  double Classif              ();


  // EGamma bits

  int    PassEGammaIDEoP      ();
  int    PassEGammaIDLoose    ();
  int    PassEGammaIDMedium   ();
  int    PassEGammaIDTight    ();
  int    PassEGammaIDTrigTight();
  int    PassEGammaIDTrigWP70 ();
  int    PassEGammaIDVeto     ();
  
  // Conversion variables		      	
  
  int    MissingHitsEG        ();
  int    MissingHits          ();
  double ConvFitProb          ();
  
  // Isolation variables		       	
  
  double EcalIsoDR03          ();
  double HcalIsoD1DR03        ();
  double TrkIsoDR03           ();
  
  double PFChargedHadronIso03 ();
  double PFPhotonIso03        ();
  double PFNeutralHadronIso03 ();

  double PFChargedHadronIso04 ();
  double PFPhotonIso04        ();
  double PFNeutralHadronIso04 ();
  
  // Isolation rho correction factors

  double RhoForHEEPv4p0       ();
  double RhoForEGamma2012     ();
  
  // GEN matching

  double MatchedGenParticlePt (); 
  double MatchedGenParticleEta(); 
  double MatchedGenParticlePhi();

  // Isolation variables

  double HEEPCaloIsolation    ();
  double HEEPCorrIsolation    ();
  double TrackPt              ();
  double RawEnergy            ();

 private:

  double m_rawSuperClusterPt;

  bool   PassUserID_HEEPv4p1           (bool verbose);
  bool   PassUserID_HEEPv4p0           (bool verbose);
  bool   PassUserID_EGamma2012( ID id,  bool verbose);
  bool   PassUserID_MVA                (bool verbose);
  bool   PassUserID_ECALFiducial       (bool verbose);
  bool   PassUserID_FakeRateLooseID    (bool verbose);

};

std::ostream& operator<< (std::ostream& stream, Electron& object);

#endif 
