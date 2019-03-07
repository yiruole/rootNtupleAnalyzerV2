#include "GenParticle.h"
#include "Object.h"
#include "IDTypes.h"

// Constructors
GenParticle::GenParticle():
  Object() {}

GenParticle::GenParticle(Collection& c, unsigned short i, short j, Long64_t current_entry ):
  Object(c,i,"GenParticle") {
    ptLeaf = m_collection->GetData()->fChain->GetLeaf("GenPart_pt");
    etaLeaf = m_collection->GetData()->fChain->GetLeaf("GenPart_eta");
    phiLeaf = m_collection->GetData()->fChain->GetLeaf("GenPart_phi");
    massLeaf = m_collection->GetData()->fChain->GetLeaf("GenPart_mass");
    pdgIdLeaf = m_collection->GetData()->fChain->GetLeaf("GenPart_pdgId");
    motherIdxLeaf = m_collection->GetData()->fChain->GetLeaf("GenPart_genPartIdxMother");
    statusLeaf = m_collection->GetData()->fChain->GetLeaf("GenPart_status");
    // load current entry
    ptLeaf->GetBranch()->GetEntry(current_entry);
    etaLeaf->GetBranch()->GetEntry(current_entry);
    phiLeaf->GetBranch()->GetEntry(current_entry);
    massLeaf->GetBranch()->GetEntry(current_entry);
    pdgIdLeaf->GetBranch()->GetEntry(current_entry);
    motherIdxLeaf->GetBranch()->GetEntry(current_entry);
    statusLeaf->GetBranch()->GetEntry(current_entry);
  }

// Kinematic variables

float & GenParticle::Pt       (){ return static_cast<float*>(ptLeaf->GetValuePointer())[m_raw_index]; }
float & GenParticle::Eta      (){ return static_cast<float*>(etaLeaf->GetValuePointer())[m_raw_index]; } 
float & GenParticle::Phi      (){ return static_cast<float*>(phiLeaf->GetValuePointer())[m_raw_index]; } 
float & GenParticle::Mass     (){ return static_cast<float*>(massLeaf->GetValuePointer())[m_raw_index]; } 

// ID variables		                                                       

int    GenParticle::PdgId       (){ return pdgIdLeaf->GetValue(m_raw_index); }
int    GenParticle::MotherIndex (){ return motherIdxLeaf->GetValue(m_raw_index); }
int    GenParticle::Status      (){ return statusLeaf->GetValue(m_raw_index); }
//int    GenParticle::NumDaughters(){ return m_collection -> GetData() -> GenPartNumDaught  -> at ( m_raw_index ); }
int    GenParticle::NumDaughters(){ return -1.0; }

//FIXME: parse from status flags
//bool GenParticle::IsHardProcess(){ return m_collection -> GetData() -> GenParticleIsHardProcess -> at ( m_raw_index ); }
//bool GenParticle::IsFromHardProcessFinalState(){ return m_collection -> GetData() -> GenParticleFromHardProcessFinalState -> at ( m_raw_index ); }
bool GenParticle::IsHardProcess(){ return true; }
bool GenParticle::IsFromHardProcessFinalState(){ return true; }

std::ostream& operator<<(std::ostream& stream, GenParticle& object) {
  stream << object.Name() << " " << ": "
	 << "PDG = "    << object.PdgId () << ", "
	 << "MotherIndex = "    << object.MotherIndex () << ", "
	 << "Num. daughters = " << object.NumDaughters () << ", "
	 << "Status = " << object.Status () << ", "
   << "IsHardProcess = " << object.IsHardProcess() << ", "
   << "IsFromHardProcessFinalState = " << object.IsFromHardProcessFinalState() << ", "
	 << "Pt = "     << object.Pt ()    << ", "
	 << "Eta = "    << object.Eta()    << ", "
	 << "Phi = "    << object.Phi()    << ", "
   << "Mass = "   << object.Mass();
  return stream;
}

