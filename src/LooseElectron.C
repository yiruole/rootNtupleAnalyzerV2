#include "LooseElectron.h"

LooseElectron::LooseElectron ():
  Electron()
{}

LooseElectron::LooseElectron (Collection & c, unsigned short i, short j):
  Electron(c,i,j) {
}

float & LooseElectron::Pt(){
  //scEt =  SCEnergy()/cosh(SCEta());
  //return scEt;
  //FIXME: go back to scEta when NanoAODv7 is out
  float pt = m_collection->ReadArrayBranch<Float_t>("Electron_pt",m_raw_index);
  ptCorr = pt/ECorr();
  return ptCorr;
} 

