#ifndef LOOSEELECTRON_H
#define LOOSEELECTRON_H

#include "Electron.h"

class LooseElectron : public Electron {

 public: 
  LooseElectron ();
  LooseElectron (Collection& c, unsigned short i, short j = 0);

  virtual float & Pt         ();

 private:
  float uncorrEt;
};

#endif 
