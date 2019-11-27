#include <string>
#include "TH2F.h"
#include "TFile.h"

class HistoReader {
  
 public:
  HistoReader();
  HistoReader(std::string& filename, std::string& barrelHistName, std::string& endcapHistName, bool absEta, bool etIsXAxis);
  ~HistoReader();
  
  void addHistoBarrel  ( TH2F* histo ) { histoBarrel = std::unique_ptr<TH2F>(histo); };
  void addHistoEndcap  ( TH2F* histo ) { histoEndcap = std::unique_ptr<TH2F>(histo); };
  float LookupValue(const float& eta, const float& et, bool verbose=false);
  float LookupValueError(const float& eta, const float& et, bool verbose=false);

 private:
  int GetLookupBin(TH2F& histRef, bool isXaxis, float& rawValue, bool verbose=false);

  //FIXME
  //TFile* qcdTFile;
  std::unique_ptr<TH2F> histoBarrel;
  std::unique_ptr<TH2F> histoEndcap;
  bool isAbsEta;
  bool isEtXAxis;
};


