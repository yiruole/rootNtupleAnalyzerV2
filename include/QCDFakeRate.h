#include <vector>
#include <string>
#include <memory>
#include "TF1.h"
#include "HistoReader.h"


class QCDFakeRate {

  public:
    QCDFakeRate();
    QCDFakeRate(std::string filename, std::string histPrefix, std::vector<std::string>& regionVec, bool lookupFromHist=true, bool absEta=true, bool etIsXAxis=false);
    float GetFakeRate(double et, std::string regionName);
    float GetFakeRate(double et, std::string regionName, double scEta);
    float GetFakeRate(double et, double scEta, double phi, unsigned int run);
    static std::string GetFakeRateRegion(float eta=-999, float phi=-999, unsigned int run=0);
    static bool isHEMElectron(float eta, float phi);

  private:
    std::vector<std::unique_ptr<TF1> > m_funcVec;
    std::vector<std::unique_ptr<HistoReader> > m_histoReaderVec;
    std::map<std::string, int> m_regionToIndexMap;
    bool m_lookupFromHist;
};
