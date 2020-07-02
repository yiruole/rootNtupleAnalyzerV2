#include "include/QCDFakeRate.h"
#include "TFile.h"

QCDFakeRate::QCDFakeRate(std::string filename, std::vector<std::string>& regionVec, int year) {
  TFile* myFile = TFile::Open(filename.c_str());
  std::string histNamePrefix = "y"+std::to_string(year);
  histNamePrefix+="_";
  int index = 0;
  for(auto regionName : regionVec) {
    std::string histName = histNamePrefix+regionName;
    histName+="_combinedFit";
    funcVec.push_back(std::unique_ptr<TF1>(static_cast<TF1*>(myFile->Get(histName.c_str()))));
    regionToFuncIndexMap[regionName] = index;
    index++;
  }
}

float QCDFakeRate::GetFakeRate(double et, std::string regionName) {
  return funcVec[regionToFuncIndexMap[regionName]]->Eval(et);
}
