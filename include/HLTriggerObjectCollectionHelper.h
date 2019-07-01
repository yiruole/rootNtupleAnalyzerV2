#ifndef HLTRIGGER_OBJECT_COLLECTION_HELPER
#define HLTRIGGER_OBJECT_COLLECTION_HELPER

#include "Collection.h"

class HLTriggerObjectCollectionHelper{

 public:
  HLTriggerObjectCollectionHelper( analysisClass & d , std::string prefix = "");
  // takes the bit number: use 1 for the first bit
  CollectionPtr GetLastFilterObjectsByPath ( unsigned int bitNumber, bool verbose=false );
  CollectionPtr GetFilterObjectsByType ( int typeId, bool verbose=false );
  
 private:
  short IndexOfAssociatedPath(const char* path_name, unsigned short trigObjIndex);
  void PrintObjectInfo(unsigned short i);
  std::vector<std::vector<int> >* GetHLTriggerObjTypeIds();

  analysisClass * m_data;
  std::string m_prefix;

};

#endif 
