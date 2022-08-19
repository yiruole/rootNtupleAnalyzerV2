#include <string>
#include "TH2F.h"
#include "TFile.h"

class HistoReader {
  
 public:
  HistoReader();
  HistoReader(std::string filename, std::string barrelHistName, std::string endcapHistName, bool absEta, bool etIsXAxis);
  ~HistoReader();
  
  void addHistoBarrel  ( TH2F* histo ) { histoBarrel = std::unique_ptr<TH2F>(histo); };
  void addHistoEndcap  ( TH2F* histo ) { histoEndcap = std::unique_ptr<TH2F>(histo); };
  double LookupValueError(const double eta, const double et, bool verbose=false) { return DoLookup(eta, et, true, verbose); }
  double LookupValue(const double eta, const double et, bool verbose=false) { return DoLookup(eta, et, false, verbose); }

 private:
  double DoLookup(const double eta, const double et, bool returnError, bool verbose);
  int GetLookupBin(const TH2F& histRef, bool isXaxis, double& rawValue, bool verbose);

  std::unique_ptr<TH2F> histoBarrel;
  std::unique_ptr<TH2F> histoEndcap;
  bool isAbsEta;
  bool isEtXAxis;
};


