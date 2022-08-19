#include "HLTriggerObject.h"
#include "Object.h"
#include "IDTypes.h"

HLTriggerObject::HLTriggerObject ():
  Object()
{}

HLTriggerObject::HLTriggerObject (Collection& c, unsigned int i, unsigned int j):
  Object        ( c,i,j, "HLTriggerObject" )
{
  //std::cout << "HLTriggerObject::HLTriggerObject -- make new object with raw_index=" << i << " and trigObj_index=" << j << std::endl;
}

//void HLTriggerObject::WritePtEtaPhi() {
//  m_collection->ReadArrayBranch<Float_t>("") HLTriggerObjPt  -> at ( m_raw_index ) = float ( m_float_pt  );
//  m_collection->ReadArrayBranch<Float_t>("") HLTriggerObjEta -> at ( m_raw_index ) = float ( m_float_eta );
//  m_collection->ReadArrayBranch<Float_t>("") HLTriggerObjPhi -> at ( m_raw_index ) = float ( m_float_phi );
//}

int HLTriggerObject::ObjectID () { return m_collection->ReadArrayBranch<Int_t>("TrigObj_id",m_raw_index); }

// HLT
std::vector<std::string> HLTriggerObject::GetFilterNames() { return std::vector<std::string>(); }
std::vector<std::string> HLTriggerObject::GetPathNames() { return std::vector<std::string>(); }
std::string HLTriggerObject::GetCollectionName() { return "undefined"; }


long int HLTriggerObject::GetPathIndex(std::string pathName)
{
  std::vector<std::string> pathNames = GetPathNames();
  std::vector<std::string>::iterator pathItr = std::find(pathNames.begin(),pathNames.end(),pathName);
  if(pathItr==pathNames.end())
    return -1; // could not find path in list of associated paths
  else
    return std::distance(pathNames.begin(),pathItr);
}

bool HLTriggerObject::PassedPathL3Filter(std::string pathName)
{
  return true;
}

bool HLTriggerObject::PassedPathLastFilter(std::string pathName)
{
  //FIXME
  return false;
}

bool HLTriggerObject::PassUserID(ID id, bool verbose)
{
  return id==ObjectID();
} 


std::ostream& operator<<(std::ostream& stream, HLTriggerObject& object) {
  stream << object.Name() << " " << ": "
    << "ID = {" << object.ObjectID() << "}, "
    << "Pt = "  << object.Pt ()       << ", "
    << "Eta = " << object.Eta()       << ", "
    << "Phi = " << object.Phi();
  return stream;
}
