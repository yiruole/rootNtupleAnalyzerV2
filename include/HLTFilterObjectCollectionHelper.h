#ifndef HLT_FILTER_OBJECT_COLLECTION_HELPER
#define HLT_FILTER_OBJECT_COLLECTION_HELPER

#include "rootNtupleClass.h"
#include "Collection.h"

class HLTFilterObjectCollectionHelper{

 public:
  HLTFilterObjectCollectionHelper( rootNtupleClass & d );
  short FindHLTFilterIndex ( const char * filter_name );
  CollectionPtr GetHLTFilterObjects ( const char * filter_name );
  
 private:
  rootNtupleClass * m_data;

};

#endif 
