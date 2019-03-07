#include "GenJet.h"
#include "Object.h"
#include "IDTypes.h"

// Constructors

GenJet::GenJet():
  Object(){}

GenJet::GenJet(Collection& c, unsigned short i, short j, Long64_t current_entry ):
  Object(c,i,"GenJet") {
    ptLeaf  = m_collection->GetData()->fChain->GetLeaf("GenJet_pt");
    etaLeaf = m_collection->GetData()->fChain->GetLeaf("GenJet_eta");
    phiLeaf = m_collection->GetData()->fChain->GetLeaf("GenJet_phi");
    // load current entry
    ptLeaf->GetBranch()->GetEntry(current_entry);
    etaLeaf->GetBranch()->GetEntry(current_entry);
    phiLeaf->GetBranch()->GetEntry(current_entry);
  }

// Kinematic variables

float & GenJet::Pt  () { return static_cast<float*>(ptLeaf->GetValuePointer())[m_raw_index]; }
float & GenJet::Eta () { return static_cast<float*>(etaLeaf->GetValuePointer())[m_raw_index]; } 
float & GenJet::Phi () { return static_cast<float*>(phiLeaf->GetValuePointer())[m_raw_index]; } 

std::ostream& operator<<(std::ostream& stream, GenJet& object) {
  stream << object.Name() << " " << ": "
	 << "Pt = "  << object.Pt ()    << ", "
	 << "Eta = " << object.Eta()    << ", "
	 << "Phi = " << object.Phi();
  return stream;
}

