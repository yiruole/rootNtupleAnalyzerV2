#include "HLTriggerObject.h"
#include "Object.h"
#include "IDTypes.h"

HLTriggerObject::HLTriggerObject ():
  Object()
{}

HLTriggerObject::HLTriggerObject (Collection& c, unsigned int i, unsigned int j):
  Object        ( c,i,j, "HLTriggerObject" ),
  m_float_pt   ( m_collection -> GetData() -> HLTriggerObjPt  -> at ( m_raw_index ) ),
  m_float_eta  ( m_collection -> GetData() -> HLTriggerObjEta -> at ( m_raw_index ) ),
  m_float_phi  ( m_collection -> GetData() -> HLTriggerObjPhi -> at ( m_raw_index ) )
{}

//void HLTriggerObject::WritePtEtaPhi() {
//  m_collection -> GetData() -> HLTriggerObjPt  -> at ( m_raw_index ) = float ( m_float_pt  );
//  m_collection -> GetData() -> HLTriggerObjEta -> at ( m_raw_index ) = float ( m_float_eta );
//  m_collection -> GetData() -> HLTriggerObjPhi -> at ( m_raw_index ) = float ( m_float_phi );
//}

float & HLTriggerObject::Pt                 () { return m_float_pt ; }
float & HLTriggerObject::Eta                () { return m_float_eta; }
float & HLTriggerObject::Phi                () { return m_float_phi; }
std::vector<int>& HLTriggerObject::ObjectIDs () { return m_collection -> GetData() -> HLTriggerObjTypeIds  -> at ( m_raw_index ) ; }

// HLT
//std::vector<std::string>& HLTriggerObject::GetFilterNames() { return m_collection -> GetData() -> HLTriggerObjFilterNames  -> at ( m_raw_index ) ; }
std::vector<std::string>& HLTriggerObject::GetPathNames() { return m_collection -> GetData() -> HLTriggerObjPathNames  -> at ( m_raw_index ) ; }
std::string HLTriggerObject::GetCollectionName() { return m_collection -> GetData() -> HLTriggerObjCollectionName  -> at ( m_raw_index ) ; }


int HLTriggerObject::GetPathIndex(std::string pathName)
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
  int index = GetPathIndex(pathName);
  if(index >= 0)
    return m_collection -> GetData() -> HLTriggerObjPassedPathLastFilter  -> at ( m_raw_index )[index];
  else
    return false;
}

bool HLTriggerObject::PassUserID(ID id, bool verbose)
{
  std::vector<int> objIds = ObjectIDs();
  bool found = std::find( objIds.begin(), objIds.end(), id) != objIds.end();
  return found;
} 


std::ostream& operator<<(std::ostream& stream, HLTriggerObject& object) {
  stream << object.Name() << " " << ": "
	 << "IDs = {";
  std::vector<int> objIds = object.ObjectIDs();
  for(std::vector<int>::const_iterator idItr = objIds.begin(); idItr != objIds.end(); ++idItr)
    if(idItr+1 < objIds.end())
      stream  << *idItr << ", ";
    else
      stream  << *idItr << "}, ";
    
  stream << "Pt = "  << object.Pt ()       << ", "
	 << "Eta = " << object.Eta()       << ", "
	 << "Phi = " << object.Phi();
  return stream;
}
