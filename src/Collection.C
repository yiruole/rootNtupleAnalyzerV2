#include "Collection.h"

//------------------------------------------------------------------------------------------
// Constructors and destructors
//------------------------------------------------------------------------------------------

Collection::Collection (std::shared_ptr<TTreeReaderTools> tools, Long64_t current_entry, size_t size ):
  m_readerTools (tools),
  m_trigObj_index ( -1 ),
  m_currentEvent ( current_entry )
{
  SetLeadNConstituents ( size ) ;
} 

Collection::Collection ( Collection & c ): 
  m_readerTools ( c.m_readerTools ),
  m_raw_indices ( c.m_raw_indices ),
  m_trigObj_index ( -1 )
{}

