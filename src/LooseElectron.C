#include "LooseElectron.h"

LooseElectron::LooseElectron ():
  Electron()
{}

LooseElectron::LooseElectron (Collection & c, unsigned short i, short j ):
  Electron(c,i,j) {
}

float & LooseElectron::Pt(){
  uncorrEt = m_collection->GetData()->Electron_pt[m_raw_index]/m_collection->GetData()->Electron_eCorr[m_raw_index];
  return uncorrEt;
} 

