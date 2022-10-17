#ifndef HLTRIGGER_OBJECT_H
#define HLTRIGGER_OBJECT_H

#include "Object.h"
#include "IDTypes.h"
#include "Collection.h"

class HLTriggerObject : public Object { 
  
 public: 
  
  HLTriggerObject  ();
  HLTriggerObject (Collection& collection, unsigned int index, int unsigned hlt_filter_index = 0);
  
  // Work-around for now
  //FIXME SIC: is this really needed?
  //void WritePtEtaPhi();

  // Kinematic variables

  // HLT info
  std::vector<std::string> GetFilterNames();
  std::vector<std::string> GetPathNames();
  std::string GetCollectionName();
  long int GetPathIndex(std::string pathName);
  bool PassedFilterBit(unsigned int bitNumber);

  // IDs 

  bool   PassUserID ( ID id, bool verbose = false );
  int ObjectID ();
  int FilterBits();

};

std::ostream& operator<< (std::ostream& stream, HLTriggerObject& object);

#endif
