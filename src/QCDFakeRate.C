#include "QCDFakeRate.h"
#include "TFile.h"

QCDFakeRate::QCDFakeRate(std::string filename, std::string histPrefix, std::vector<std::string>& regionVec, bool lookupFromHist, bool absEta, bool etIsXAxis) {
  TFile* myFile = TFile::Open(filename.c_str());
  int index = 0;
  for(auto regionName : regionVec) {
    std::string histName = histPrefix+regionName;
    if(lookupFromHist)
      m_histoReaderVec.push_back(std::make_unique<HistoReader>(filename, histName, histName, absEta, etIsXAxis));
    else
      m_funcVec.push_back(std::unique_ptr<TF1>(static_cast<TF1*>(myFile->Get(histName.c_str()))));
    m_regionToIndexMap[regionName] = index;
    index++;
  }
}

float QCDFakeRate::GetFakeRate(double et, double scEta, double phi, unsigned int run) {
  return GetFakeRate(et, GetFakeRateRegion(scEta, phi, run), scEta);
}

float QCDFakeRate::GetFakeRate(double et, std::string regionName, double scEta) {
  return m_histoReaderVec[m_regionToIndexMap[regionName]]->LookupValue(scEta, et);
}

float QCDFakeRate::GetFakeRate(double et, std::string regionName) {
  return m_funcVec[m_regionToIndexMap[regionName]]->Eval(et);
}

bool QCDFakeRate::isHEMElectron(float eta, float phi) {
  if(eta <= -1.3 && eta >= -3.0)
    if(phi <= -0.87 && phi >= -1.57)
      return true;
  return false;
}

std::string QCDFakeRate::GetFakeRateRegion(float eta, float phi, unsigned int run) {
  std::string region = "";

  if(run < 319077)
    return region+"pre319077_2Jet";
  else if(isHEMElectron(eta, phi))
    return region+"HEMonly_post319077_2Jet";
  else
    return region+"noHEM_post319077_2Jet";
}
