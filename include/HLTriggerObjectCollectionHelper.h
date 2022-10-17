#ifndef HLTRIGGER_OBJECT_COLLECTION_HELPER
#define HLTRIGGER_OBJECT_COLLECTION_HELPER

#include "Collection.h"

class HLTriggerObjectCollectionHelper{

 public:
  HLTriggerObjectCollectionHelper( analysisClass & d , std::string prefix = "");
  // takes the bit number: use 1 for the first bit
  CollectionPtr GetTriggerObjectsByFilterBit ( unsigned int bitNumber, bool verbose=false );
  CollectionPtr GetTriggerObjectsByType ( int typeId, bool verbose=false );
  CollectionPtr GetTriggerObjectsByType ( std::vector<int>& typeIds, bool verbose=false );
  CollectionPtr GetTriggerObjectsByFilterBitAndType ( std::vector<unsigned int>& filterBits, std::vector<int>& typeIds, bool verbose=false );
  
 private:
  void PrintObjectInfo(unsigned short i);
  std::vector<std::vector<int> >* GetHLTriggerObjTypeIds();

  analysisClass * m_data;
  std::string m_prefix;

};

#endif 
