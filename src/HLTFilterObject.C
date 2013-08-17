#include "HLTFilterObject.h"
#include "Object.h"
#include "IDTypes.h"

HLTFilterObject::HLTFilterObject ():
  Object()
{}

HLTFilterObject::HLTFilterObject (Collection& c, unsigned int i, unsigned int j):
  Object        ( c,i,j, "HLTFilterObject" ),
  m_double_pt   ( m_collection -> GetData() -> HLTFilterObjPt  -> at ( m_hlt_filter_index )[m_raw_index] ),
  m_double_eta  ( m_collection -> GetData() -> HLTFilterObjEta -> at ( m_hlt_filter_index )[m_raw_index] ),
  m_double_phi  ( m_collection -> GetData() -> HLTFilterObjPhi -> at ( m_hlt_filter_index )[m_raw_index] )
{}

void HLTFilterObject::WritePtEtaPhi() {
  m_collection -> GetData() -> HLTFilterObjPt  -> at ( m_hlt_filter_index )[m_raw_index] = float ( m_double_pt  );
  m_collection -> GetData() -> HLTFilterObjEta -> at ( m_hlt_filter_index )[m_raw_index] = float ( m_double_eta );
  m_collection -> GetData() -> HLTFilterObjPhi -> at ( m_hlt_filter_index )[m_raw_index] = float ( m_double_phi );
}

double & HLTFilterObject::Pt        ()                   { return m_double_pt ; }
double & HLTFilterObject::Eta       ()                   { return m_double_eta; }
double & HLTFilterObject::Phi       ()                   { return m_double_phi; }
int      HLTFilterObject::ObjectID  ()                   { return m_collection -> GetData() -> HLTFilterObjId  -> at ( m_hlt_filter_index )[m_raw_index] ; }
bool     HLTFilterObject::PassUserID(ID id, bool verbose){ return false; } 

std::ostream& operator<<(std::ostream& stream, HLTFilterObject& object) {
  stream << object.Name() << " " << ": "
	 << "ID = "  << object.ObjectID () << ", "
	 << "Pt = "  << object.Pt ()       << ", "
	 << "Eta = " << object.Eta()       << ", "
	 << "Phi = " << object.Phi();
  return stream;
}
