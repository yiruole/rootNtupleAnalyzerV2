#include "Collection.h"

//------------------------------------------------------------------------------------------
// Constructors and destructors
//------------------------------------------------------------------------------------------

Collection::Collection ( rootNtupleClass & d, Long64_t current_entry, size_t size ):
  m_data ( & d ),
  m_trigObj_index ( -1 ),
  m_currentEvent ( current_entry )
{
  SetLeadNConstituents ( size ) ;
} 

Collection::Collection ( Collection & c ): 
  m_data ( c.m_data ),
  m_raw_indices ( c.m_raw_indices ),
  m_trigObj_index ( -1 )
{}

