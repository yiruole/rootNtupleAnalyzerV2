#include "QCDFakeRate.h"
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

bool QCDFakeRate::isHEMElectron(float eta, float phi) {
  if(eta <= -1.3 && eta >= -3.0)
    if(phi <= -0.87 && phi >= -1.57)
      return true;
  return false;
}

std::string QCDFakeRate::GetFakeRateRegion(bool isBarrel, bool isEndcap1, bool isEndcap2, float eta, float phi, int run) {
  std::string region = "";
  if(isBarrel)
    region = "Bar_";
  else if(isEndcap1)
    region = "End1_";
  else if(isEndcap2)
    region = "End2_";
  
  if(run < 0)
    return region+"2Jet";
  else { // 2018
    if(run < 319077)
      return region+"pre319077_2Jet";
    else if(isHEMElectron(eta, phi))
      return region+"HEMonly_post319077_2Jet";
    else
      return region+"noHEM_post319077_2Jet";
  }
}
