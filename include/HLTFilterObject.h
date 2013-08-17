#ifndef HLT_FILTER_OBJECT_H
#define HLT_FILTER_OBJECT_H

#include "Object.h"
#include "IDTypes.h"
#include "Collection.h"

class HLTFilterObject : public Object { 
  
 public: 
  
  HLTFilterObject  ();
  HLTFilterObject (Collection& collection, unsigned int index, int unsigned hlt_filter_index = 0);
  
  // Work-around for now
  void WritePtEtaPhi();

  // Kinematic variables
  
  double & Pt  () ;
  double & Eta () ; 
  double & Phi () ; 

  // IDs 

  bool   PassUserID ( ID id, bool verbose = false );
  int    ObjectID();
  
 private:
  double m_double_pt;
  double m_double_eta;
  double m_double_phi;

};

std::ostream& operator<< (std::ostream& stream, HLTFilterObject& object);

#endif
