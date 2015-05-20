#ifndef HLTRIGGER_OBJECT_COLLECTION_HELPER
#define HLTRIGGER_OBJECT_COLLECTION_HELPER

#include "rootNtupleClass.h"
#include "Collection.h"

class HLTriggerObjectCollectionHelper{

 public:
  HLTriggerObjectCollectionHelper( rootNtupleClass & d , std::string prefix = "");
  CollectionPtr GetL3FilterObjectsByPath ( const char * path_name, bool verbose=false );
  CollectionPtr GetLastFilterObjectsByPath ( const char * path_name, bool verbose=false );
  
 private:
  short IndexOfAssociatedPath(const char* path_name, unsigned short trigObjIndex);
  void PrintObjectInfo(unsigned short i);
  std::vector<std::vector<int> >* GetHLTriggerObjTypeIds();

  rootNtupleClass * m_data;
  std::string m_prefix;

};

#endif 
