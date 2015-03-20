#include "Collection.h"

//------------------------------------------------------------------------------------------
// Constructors and destructors
//------------------------------------------------------------------------------------------

Collection::Collection ( rootNtupleClass & d, size_t size ):
  m_data ( & d ),
  m_trigObj_index ( -1 )
{
  SetLeadNConstituents ( size ) ;
} 

Collection::Collection ( Collection & c ): 
  m_data ( c.m_data ),
  m_raw_indices ( c.m_raw_indices ),
  m_trigObj_index ( -1 )
{}

