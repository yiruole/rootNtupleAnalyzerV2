#include <algorithm>
#include <bitset>
#include "HLTriggerObjectCollectionHelper.h"
#include "HLTriggerObject.h"
#include "TBranchElement.h"


HLTriggerObjectCollectionHelper::HLTriggerObjectCollectionHelper( analysisClass & d, std::string prefix ):
  m_data ( & d ),
  m_prefix ( prefix )
{}

//std::vector<std::vector<int> >* HLTriggerObjectCollectionHelper::GetHLTriggerObjTypeIds()
//{
//  //return reinterpret_cast<std::vector<std::vector<int > >* >(((TBranchElement*)m_data->fChain->GetBranch((m_prefix+"HLTriggerObjTypeIds").c_str()))->GetObject());
//  //FIXME
//}

void HLTriggerObjectCollectionHelper::PrintObjectInfo(unsigned short i)
{

  CollectionPtr collection ( new Collection ( m_data->readerTools_));
  std::cout << "Pt = "  << m_data->readerTools_->ReadArrayBranch<Float_t>("TrigObj_pt",i) << ", "
    << "Eta = " << m_data->readerTools_->ReadArrayBranch<Float_t>("TrigObj_eta",i)        << ", "
    << "Phi = " << m_data->readerTools_->ReadArrayBranch<Float_t>("TrigObj_phi",i)        << ", "
    << "ID = " << m_data->readerTools_->ReadArrayBranch<Int_t>("TrigObj_id",i)            << ", "
    << " filterBits = " << std::bitset<32>(m_data->readerTools_->ReadArrayBranch<Int_t>("TrigObj_filterBits",i))
    << std::endl;
}


// is this trigger object associated to the given HLT path?
short HLTriggerObjectCollectionHelper::IndexOfAssociatedPath(const char* path_name, unsigned short trigObjIndex)
{
  ////std::cout << "HLTriggerObjectCollectionHelper::IndexOfAssociatedPath("<<path_name<<","<<trigObjIndex<< ")"<<std::endl;
  //std::vector<std::string> pathNames = m_data->HLTriggerObjPathNames->at(trigObjIndex);
  //
  ////for(std::vector<std::string>::const_iterator itr = pathNames.begin(); itr != pathNames.end(); ++itr)
  ////  std::cout << "\t found path: " << *itr << std::endl;
  //
  //std::vector<std::string>::iterator it = std::find ( pathNames.begin(),
  //    pathNames.end(),
  //    std::string( path_name ));
  //// returns -1 if no association found
  //if(it != pathNames.end())
  //{
  //  unsigned short idx = std::distance(pathNames.begin(),it);
  //  return idx;
  //}
  //else
  //{
  //  // try to look by prefix of given path name: if path_name is find in a pathNames entry
  //  auto found = find_if(pathNames.begin(), pathNames.end(), [path_name] (const std::string& s) { 
  //      return s.find(path_name) != std::string::npos;
  //      });
  //  if(found!=pathNames.end())
  //  {
  //    unsigned short idx = std::distance(pathNames.begin(),found);
  //    //std::cout << "Found matching trigger path for search '" << path_name << "' = " << *found << " with index = " << idx << std::endl;
  //    return idx;
  //  }
  //  //std::cout << "ERROR: could not find associated index for given path name: " << path_name << std::endl;
  //  return -1;
  //}
  return -1;
}


CollectionPtr HLTriggerObjectCollectionHelper::GetLastFilterObjectsByPath ( unsigned int bitNumber, bool verbose ){
  CollectionPtr collection ( new Collection ( m_data->readerTools_));
  std::vector<short unsigned int> matchingObjIdxs;
  for(unsigned int idx = 0; idx < collection->ReadValueBranch<UInt_t>("nTrigObj"); ++idx) {
    if(verbose)
      PrintObjectInfo(idx);
    bool passedLastFilter = (collection->ReadArrayBranch<Int_t>("TrigObj_filterBits",idx) >> (bitNumber-1)) & 0x1;
    if(passedLastFilter)
      matchingObjIdxs.push_back(idx);
  }
  collection->SetRawIndices(matchingObjIdxs);
  
  return collection;
}

// See (for example): https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py#L52
CollectionPtr HLTriggerObjectCollectionHelper::GetFilterObjectsByType(int typeId, bool verbose) {
  if(verbose)
    std::cout << "INFO HLTriggerObjectCollectionHelper::GetFilterObjectsByType(" << typeId << ") BEGINS" << std::endl;
  CollectionPtr collection ( new Collection ( m_data->readerTools_));
  unsigned int nTrigObj = m_data->readerTools_->ReadValueBranch<UInt_t>("nTrigObj");
  std::vector<short unsigned int> matchingObjIdxs;
  for(unsigned int idx = 0; idx < nTrigObj; ++idx) {
    if(verbose) {
      PrintObjectInfo(idx);
      std::cout << "idx=" << idx << ": nTrigObj=" << nTrigObj << "; try to check typeId=" << typeId << std::endl;
      //std::cout << "size=" << size << "; try to check typeId=" << typeId << std::endl;
    }
    int id = m_data->readerTools_->ReadArrayBranch<Int_t>("TrigObj_id",idx);
    if(id==typeId)
      matchingObjIdxs.push_back(id);
  }
  collection->SetRawIndices(matchingObjIdxs);

  if(verbose)
    std::cout << "INFO HLTriggerObjectCollectionHelper::GetFilterObjectsByType(" << typeId << ") ENDS" << std::endl;
  return collection;
}

