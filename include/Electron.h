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
  double & PtHeep             ();
  double & Eta                (); 
  double & Phi                (); 
  double SCEta                (); 
  double SCPhi                (); 
  double SCEnergy             (); 
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
  double DeltaEtaSeed         ();
  double DeltaPhi             ();
  double HoE                  ();
  double SigmaIEtaIEta        ();
  double Full5x5SigmaIEtaIEta ();
  double SigmaEtaEta          ();
  double E1x5OverE5x5         ();
  double E2x5OverE5x5         ();
  double Full5x5E1x5OverE5x5     ();
  double Full5x5E2x5OverE5x5     ();
  double LeadVtxDistXY        ();
  double LeadVtxDistZ         ();
  double VtxDistXY            ();
  double VtxDistZ             ();
  double Dist                 ();
  double DCotTheta            ();
  double ValidFrac            ();
  double CaloEnergy           ();
  double EcalEnergy           ();
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
  
  double EcalIsoDR03          ();
  double HcalIsoD1DR03        ();
  double TrkIsoDR03           ();
  
  double PFChargedHadronIso03 ();
  double PFPhotonIso03        ();
  double PFNeutralHadronIso03 ();
  double PFPUIso03            ();

  double PFChargedHadronIso04 ();
  double PFPhotonIso04        ();
  double PFNeutralHadronIso04 ();
  
  
  // GEN matching

  double MatchedGenParticlePt (); 
  double MatchedGenParticleEta(); 
  double MatchedGenParticlePhi();

  
  // HLT matching
  bool IsHLTEleJetJetMatched();
  bool IsHLTDoubleEleMatched();
  bool IsHLTSingleEleMatched();
  bool IsHLTSingleEleWP85Matched();
  double HLTEleJetJetMatchPt();
  double HLTEleJetJetMatchEta();
  double HLTEleJetJetMatchPhi();
  double HLTDoubleEleMatchPt();
  double HLTDoubleEleMatchEta();
  double HLTDoubleEleMatchPhi();
  double HLTSingleEleMatchPt();
  double HLTSingleEleMatchEta();
  double HLTSingleEleMatchPhi();
  double HLTSingleEleWP85MatchPt();
  double HLTSingleEleWP85MatchEta();
  double HLTSingleEleWP85MatchPhi();

  // Isolation variables

  double HEEPCaloIsolation    ();
  double HEEPCorrIsolation    ();
  double TrackPt              ();
  double RawEnergy            ();

 private:

  double m_rawSuperClusterPt;

  bool   PassUserID_BuiltIn_HEEPv6p0   ();
  bool   PassUserID_HEEP               (bool verbose);
  bool   PassUserID_BuiltIn_EGamma     ( ID id);
  bool   PassUserID_EGamma             ( ID id,  bool verbose);
  bool   PassUserID_MVA                (bool verbose);
  bool   PassUserID_ECALFiducial       (bool verbose);
  bool   PassUserID_FakeRateLooseID    (bool verbose);

};

std::ostream& operator<< (std::ostream& stream, Electron& object);

#endif 
