#include "Collection.h"

//------------------------------------------------------------------------------------------
// Constructors and destructors
//------------------------------------------------------------------------------------------

Collection::Collection (std::shared_ptr<TTreeReaderTools> tools):
  m_readerTools (tools),
  m_trigObj_index ( -1 )
{} 

Collection::Collection (std::shared_ptr<TTreeReaderTools> tools, unsigned short int size ):
  m_readerTools (tools),
  m_trigObj_index ( -1 )
{
  SetLeadNConstituents ( size ) ;
} 

Collection::Collection ( Collection & c ): 
  m_readerTools ( c.m_readerTools ),
  m_raw_indices ( c.m_raw_indices ),
  m_trigObj_index ( -1 ),
  m_systematicVariationNames(c.m_systematicVariationNames),
  m_systematicVariations(c.m_systematicVariations)
{}

