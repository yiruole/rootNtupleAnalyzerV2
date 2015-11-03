#include <algorithm>
#include "HLTriggerObjectCollectionHelper.h"
#include "HLTriggerObject.h"
#include "rootNtupleClass.h"
#include "TBranchElement.h"


HLTriggerObjectCollectionHelper::HLTriggerObjectCollectionHelper( rootNtupleClass & d, std::string prefix ):
  m_data ( & d ),
  m_prefix ( prefix )
{}

std::vector<std::vector<int> >* HLTriggerObjectCollectionHelper::GetHLTriggerObjTypeIds()
{
  return reinterpret_cast<std::vector<std::vector<int > >* >(((TBranchElement*)m_data->fChain->GetBranch((m_prefix+"HLTriggerObjTypeIds").c_str()))->GetObject());
}

void HLTriggerObjectCollectionHelper::PrintObjectInfo(unsigned short i)
{
  //std::vector<int> objIds = m_data->HLTriggerObjTypeIds->at(i);
  std::vector<int> objIds = GetHLTriggerObjTypeIds()->at(i);
  //XXX SIC TEST
  //std::vector<std::vector<int> >* myVec = reinterpret_cast<std::vector<std::vector<int > >* >(((TBranchElement*)m_data->fChain->GetBranch("HLTriggerObjTypeIds"))->GetObject());
  //std::cout << "myVec->size()=" << myVec->size() << std::endl;
  //std::cout << "myVec->at(i).size()=" << myVec->at(i).size() << std::endl;
  //std::cout << "objIds size()=" << objIds.size() << std::endl;
  //std::vector<int> myVecObjIds = myVec->at(i);
  //std::cout << "MyVec TrigObj: IDs = {";
  //for(std::vector<int>::const_iterator idItr = objIds.begin(); idItr != objIds.end(); ++idItr)
  //  if(idItr+1 < objIds.end())
  //    std::cout  << *idItr << ", ";
  //  else
  //    std::cout  << *idItr << "}, ";
  //XXX SIC TEST
  std::cout << "TrigObj: IDs = {";
  for(std::vector<int>::const_iterator idItr = objIds.begin(); idItr != objIds.end(); ++idItr)
    if(idItr+1 < objIds.end())
      std::cout  << *idItr << ", ";
    else
      std::cout  << *idItr << "}, ";
  std::vector<std::string> pathNamesVec = m_data->HLTriggerObjPathNames->at(i);
  for(std::vector<std::string>::const_iterator pathItr = pathNamesVec.begin(); pathItr != pathNamesVec.end(); ++pathItr)
    if(pathItr+1 < pathNamesVec.end())
      std::cout  << *pathItr << ", ";
    else
      std::cout  << *pathItr << "}, ";

  std::cout << "Pt = "  << m_data->HLTriggerObjPt->at(i)       << ", "
    << "Eta = " << m_data->HLTriggerObjEta->at(i)       << ", "
    << "Phi = " << m_data->HLTriggerObjPhi->at(i) << std::endl;
}


// is this trigger object associated to the given HLT path?
short HLTriggerObjectCollectionHelper::IndexOfAssociatedPath(const char* path_name, unsigned short trigObjIndex)
{
  //std::cout << "HLTriggerObjectCollectionHelper::IndexOfAssociatedPath("<<path_name<<","<<trigObjIndex<< ")"<<std::endl;
  std::vector<std::string> pathNames = m_data->HLTriggerObjPathNames->at(trigObjIndex);
  
  //for(std::vector<std::string>::const_iterator itr = pathNames.begin(); itr != pathNames.end(); ++itr)
  //  std::cout << "\t found path: " << *itr << std::endl;
  
  std::vector<std::string>::iterator it = std::find ( pathNames.begin(),
      pathNames.end(),
      std::string( path_name ));
  // returns -1 if no association found
  if(it != pathNames.end())
  {
    unsigned short idx = std::distance(pathNames.begin(),it);
    return idx;
  }
  else
  {
    // try to look by prefix of given path name: if path_name is find in a pathNames entry
    auto found = find_if(pathNames.begin(), pathNames.end(), [path_name] (const std::string& s) { 
        return s.find(path_name) != std::string::npos;
        });
    if(found!=pathNames.end())
    {
      unsigned short idx = std::distance(pathNames.begin(),found);
      //std::cout << "Found matching trigger path for search '" << path_name << "' = " << *found << " with index = " << idx << std::endl;
      return idx;
    }
    //std::cout << "ERROR: could not find associated index for given path name: " << path_name << std::endl;
    return -1;
  }
}


CollectionPtr HLTriggerObjectCollectionHelper::GetL3FilterObjectsByPath ( const char * path_name, bool verbose ){
  CollectionPtr collection ( new Collection ( *m_data, 0));

  std::vector<unsigned short> matchingHLTriggerRawIndices;
  // first, look at each object in the HLTriggerObj collection
  for (unsigned short i = 0; i < m_data->HLTriggerObjPt->size() ; ++i)
  {
    if(verbose)
      PrintObjectInfo(i);

    short pathIndex = IndexOfAssociatedPath(path_name, i);
    if(pathIndex > -1)
    {
      // if it is associated to a path, check to see if it passed an L3 filter in the path
      if(m_data->HLTriggerObjPassedPathL3Filter->at(i).at(pathIndex))
        matchingHLTriggerRawIndices.push_back(i); // keep raw index of trigObj
    }

  }
  collection->SetRawIndices(matchingHLTriggerRawIndices);
  
  return collection;
}


CollectionPtr HLTriggerObjectCollectionHelper::GetLastFilterObjectsByPath ( const char * path_name, bool verbose ){
  CollectionPtr collection ( new Collection ( *m_data, 0));

  std::vector<unsigned short> matchingHLTriggerRawIndices;
  // first, look at each object in the HLTriggerObj collection
  for (unsigned short i = 0; i < m_data->HLTriggerObjPt->size() ; ++i)
  {
    if(verbose)
      PrintObjectInfo(i);

    short pathIndex = IndexOfAssociatedPath(path_name, i);
    if(pathIndex > -1)
    {
      // if it is associated to a path, check to see if it passed the last filter in the path
      if(m_data->HLTriggerObjPassedPathLastFilter->at(i).at(pathIndex))
        matchingHLTriggerRawIndices.push_back(i); // keep raw index of trigObj
    }

  }
  collection->SetRawIndices(matchingHLTriggerRawIndices);
  
  return collection;
}
