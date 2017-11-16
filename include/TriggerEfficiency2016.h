#ifndef TRIGGEREFFICIENCY2015_H
#define TRIGGEREFFICIENCY2015_H

#include <string>
#include "TH2F.h"
#include "TFile.h"
#include "TRandom3.h"

class TriggerEfficiency {
  
 public:
  TriggerEfficiency();
  TriggerEfficiency(std::string rootFilename, std::string graphName);
  ~TriggerEfficiency();
  
  void AddHisto  ( TH2F* histo ) { histo_ = histo; };
  float GetEfficiency(const float& eta, const float& et, bool verbose=false);
  float GetEfficiencyError(const float& eta, const float& et, bool verbose=false);
  bool PassTrigger(const float& eta, const float& et, bool verbose=false);

 private:
  //TFile* tFile;
  TH2F* histo_;
  TH2F* histoErr_;

  TRandom3 randNrGen;

};


#endif 
