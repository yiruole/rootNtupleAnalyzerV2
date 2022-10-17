#include <algorithm>
#include <bitset>
#include "HLTriggerObjectCollectionHelper.h"
#include "HLTriggerObject.h"
#include "TBranchElement.h"


HLTriggerObjectCollectionHelper::HLTriggerObjectCollectionHelper( analysisClass & d, std::string prefix ):
  m_data ( & d ),
  m_prefix ( prefix )
{}

void HLTriggerObjectCollectionHelper::PrintObjectInfo(unsigned short i)
{

  //CollectionPtr collection ( new Collection ( m_data->readerTools_));
  std::cout << "Pt = "  << m_data->readerTools_->ReadArrayBranch<Float_t>("TrigObj_pt",i) << ", "
    << "Eta = " << m_data->readerTools_->ReadArrayBranch<Float_t>("TrigObj_eta",i)        << ", "
    << "Phi = " << m_data->readerTools_->ReadArrayBranch<Float_t>("TrigObj_phi",i)        << ", "
    << "ID = " << m_data->readerTools_->ReadArrayBranch<Int_t>("TrigObj_id",i)            << ", "
    << " filterBits = " << std::bitset<32>(m_data->readerTools_->ReadArrayBranch<Int_t>("TrigObj_filterBits",i))
    << std::endl;
}


CollectionPtr HLTriggerObjectCollectionHelper::GetTriggerObjectsByFilterBit ( unsigned int bitNumber, bool verbose ){
  CollectionPtr collection ( new Collection ( m_data->readerTools_));
  std::vector<short unsigned int> matchingObjIdxs;
  for(unsigned int idx = 0; idx < collection->ReadValueBranch<UInt_t>("nTrigObj"); ++idx) {
    if(verbose)
      PrintObjectInfo(idx);
    bool passedLastFilter = (collection->ReadArrayBranch<Int_t>("TrigObj_filterBits",idx) >> bitNumber) & 0x1;
    if(passedLastFilter)
      matchingObjIdxs.push_back(idx);
  }
  collection->SetRawIndices(matchingObjIdxs);
  
  return collection;
}

// See (for example): https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py#L52
CollectionPtr HLTriggerObjectCollectionHelper::GetTriggerObjectsByType(int typeId, bool verbose) {
  std::vector<int> typeIdVec {typeId};
  return GetTriggerObjectsByType(typeIdVec,verbose);
}


CollectionPtr HLTriggerObjectCollectionHelper::GetTriggerObjectsByType(std::vector<int>& typeIdVec, bool verbose) {
  CollectionPtr collection ( new Collection ( m_data->readerTools_));
  unsigned int nTrigObj = m_data->readerTools_->ReadValueBranch<UInt_t>("nTrigObj");
  std::vector<short unsigned int> matchingObjIdxs;
  for(unsigned int idx = 0; idx < nTrigObj; ++idx) {
    if(verbose) {
      std::cout << "GetTriggerObjectsByType(): idx=" << idx << ": nTrigObj=" << nTrigObj << "; try to check typeIds={";
      for(auto itr : typeIdVec)
        std::cout << itr << " ";
      std::cout << "} for object: ";// << std::endl;
      PrintObjectInfo(idx);
      //std::cout << "size=" << size << "; try to check typeId=" << typeId << std::endl;
    }
    int id = m_data->readerTools_->ReadArrayBranch<Int_t>("TrigObj_id",idx);
    if(find(typeIdVec.begin(),typeIdVec.end(),id) != typeIdVec.end())
      matchingObjIdxs.push_back(idx);
  }
  collection->SetRawIndices(matchingObjIdxs);

  return collection;
}



CollectionPtr HLTriggerObjectCollectionHelper::GetTriggerObjectsByFilterBitAndType(std::vector<unsigned int>& filterBits, std::vector<int>& typeIdVec, bool verbose) {
  CollectionPtr collection ( new Collection ( m_data->readerTools_));
  unsigned int nTrigObj = m_data->readerTools_->ReadValueBranch<UInt_t>("nTrigObj");
  std::vector<short unsigned int> matchingObjIdxs;
  for(unsigned int idx = 0; idx < nTrigObj; ++idx) {
    if(verbose) {
      std::cout << "GetFilterObjectsByFilterBitType(): idx=" << idx << ": nTrigObj=" << nTrigObj << "; try to check typeIds={";
      for(auto itr : typeIdVec)
        std::cout << itr << " ";
      std::cout << "} for object: ";// << std::endl;
      PrintObjectInfo(idx);
      //std::cout << "size=" << size << "; try to check typeId=" << typeId << std::endl;
    }
    std::bitset<32> filterBitset(m_data->readerTools_->ReadArrayBranch<Int_t>("TrigObj_filterBits",idx));
    for(auto bitToTest : filterBits) {
      if(filterBitset.test(bitToTest)) {
        int id = m_data->readerTools_->ReadArrayBranch<Int_t>("TrigObj_id",idx);
        if(find(typeIdVec.begin(),typeIdVec.end(),id) != typeIdVec.end()) {
          matchingObjIdxs.push_back(idx);
        }
        break;
      }
    }
  }
  collection->SetRawIndices(matchingObjIdxs);

  return collection;
}
