#ifndef QCD_FAKE_RATE
#define QCD_FAKE_RATE

#include <string>
#include "TGraphErrors.h"
#include "TFile.h"

class QCDFakeRate {
  
 public:
  QCDFakeRate();
  QCDFakeRate(std::string qcdFilename);
  ~QCDFakeRate();
  
  void addGraphBarrel  ( TGraphErrors* graph ) { qcdGraphBarrel = graph; };
  void addGraphEndcap1  ( TGraphErrors* graph ) { qcdGraphEndcap1 = graph; };
  void addGraphEndcap2  ( TGraphErrors* graph ) { qcdGraphEndcap2 = graph; };
  //TODO add the error here and redo with 2-D histo
  float GetFakeRate(const float& eta, const float& et);

 private:
  //TFile* qcdTFile;
  TGraphErrors* qcdGraphBarrel;
  TGraphErrors* qcdGraphEndcap1;
  TGraphErrors* qcdGraphEndcap2;

};


#endif 
