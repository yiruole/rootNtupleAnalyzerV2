#ifndef QCD_FAKE_RATE
#define QCD_FAKE_RATE

#include <string>
#include "TH2F.h"
#include "TFile.h"

class QCDFakeRate {
  
 public:
  QCDFakeRate();
  QCDFakeRate(std::string qcdFilename);
  ~QCDFakeRate();
  
  void addHistoBarrel  ( TH2F* histo ) { histoBarrel = histo; };
  void addHistoEndcap  ( TH2F* histo ) { histoEndcap = histo; };
  float GetFakeRate(const float& eta, const float& et, bool verbose=false);
  float GetFakeRateError(const float& eta, const float& et, bool verbose=false);

 private:
  //TFile* qcdTFile;
  TH2F* histoBarrel;
  TH2F* histoEndcap;

};


#endif 
