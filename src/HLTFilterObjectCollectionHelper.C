#include <algorithm>
#include "HLTFilterObjectCollectionHelper.h"

HLTFilterObjectCollectionHelper::HLTFilterObjectCollectionHelper( rootNtupleClass & d ):
  m_data ( & d )
{}

short HLTFilterObjectCollectionHelper::FindHLTFilterIndex( const char* filter_name ) { 
  
  std::vector<std::string>::iterator it = std::find ( m_data -> HLTFilterName -> begin(),
						      m_data -> HLTFilterName -> end(),
						      std::basic_string<char> ( filter_name ));
  
  bool found = ( it != m_data -> HLTFilterName -> end() );

  short index = -1;
  if ( found ) index = std::distance ( m_data -> HLTFilterName -> begin(), it ) ;
  
  return index;
  
}


CollectionPtr HLTFilterObjectCollectionHelper::GetHLTFilterObjects ( const char * filter_name ){
  CollectionPtr collection ( new Collection ( *m_data, 0));

  short filter_object_index = FindHLTFilterIndex ( filter_name ) ;

  if ( filter_object_index < 0 ) return collection;
  
  collection -> SetHLTFilterObjectIndex ( filter_object_index ) ;
  collection -> SetLeadNConstituents( collection -> GetData() -> HLTFilterObjPt -> at ( filter_object_index ).size() );

  return collection;
}
