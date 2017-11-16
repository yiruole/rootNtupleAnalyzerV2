#include "LooseElectron.h"

LooseElectron::LooseElectron ():
  Electron()
{}

LooseElectron::LooseElectron (Collection & c, unsigned short i, short j ):
  Electron(c,i,j) {
}

float & LooseElectron::Pt(){
  scEt = m_collection->GetData()->ElectronSCEnergy->at( m_raw_index)/cosh( m_collection->GetData()->ElectronSCEta->at( m_raw_index));
  return scEt;
} 

