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
  std::cout << "Pt = "  << m_data->readerTools_->ReadArrayBranch<Float_t>("TrigObj_pt")[i]       << ", "
    << "Eta = " << m_data->readerTools_->ReadArrayBranch<Float_t>("TrigObj_eta")[i]       << ", "
    << "Phi = " << m_data->readerTools_->ReadArrayBranch<Float_t>("TrigObj_phi")[i] << ", "
    << "ID = " << m_data->readerTools_->ReadArrayBranch<Int_t>("TrigObj_id")[i] << ", "
    << " filterBits = " << std::bitset<32>(m_data->readerTools_->ReadArrayBranch<Int_t>("TrigObj_filterBits")[i])
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
  // 1. need to figure out which bit to use based on path name. but this is suboptimal. probably should just require the user to ask for a bit.
  // 2. loop over trigger objects and see which have that bit enabled
  TTreeReaderArray<Int_t>& trigObjFilterBits = collection->ReadArrayBranch<Int_t>("TrigObj_filterBits");
  std::vector<short unsigned int> matchingObjIdxs;
  for(unsigned int idx = 0; idx < collection->ReadValueBranch<UInt_t>("nTrigObj"); ++idx) {
    if(verbose)
      PrintObjectInfo(idx);
    bool passedLastFilter = (trigObjFilterBits[idx] >> (bitNumber-1)) & 0x1;
    if(passedLastFilter)
      matchingObjIdxs.push_back(idx);
  }
  collection->SetRawIndices(matchingObjIdxs);

  //std::vector<unsigned short> matchingHLTriggerRawIndices;
  //// first, look at each object in the HLTriggerObj collection
  //for (unsigned short i = 0; i < m_data->HLTriggerObjPt->size() ; ++i)
  //{
  //  if(verbose)
  //    PrintObjectInfo(i);

  //  short pathIndex = IndexOfAssociatedPath(path_name, i);
  //  if(pathIndex > -1)
  //  {
  //    // if it is associated to a path, check to see if it passed the last filter in the path
  //    if(m_data->HLTriggerObjPassedPathLastFilter->at(i).at(pathIndex))
  //      matchingHLTriggerRawIndices.push_back(i); // keep raw index of trigObj
  //  }

  //}
  //collection->SetRawIndices(matchingHLTriggerRawIndices);
  
  return collection;
}

// See (for example): https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py#L52
CollectionPtr HLTriggerObjectCollectionHelper::GetFilterObjectsByType(int typeId, bool verbose) {
  CollectionPtr collection ( new Collection ( m_data->readerTools_));
  TTreeReaderArray<Int_t>& trigObjIds = m_data->readerTools_->ReadArrayBranch<Int_t>("TrigObj_id");
  std::vector<short unsigned int> matchingObjIdxs;
  for(unsigned int idx = 0; idx < m_data->readerTools_->ReadValueBranch<UInt_t>("nTrigObj"); ++idx) {
    if(verbose)
      PrintObjectInfo(idx); //FIXME !!!!
    if(trigObjIds[idx]==typeId)
      matchingObjIdxs.push_back(idx);
  }
  collection->SetRawIndices(matchingObjIdxs);

  return collection;
}
