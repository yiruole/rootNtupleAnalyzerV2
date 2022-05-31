#include <vector>
#include <string>
#include <memory>
#include "TF1.h"


class QCDFakeRate {

  public:
    QCDFakeRate();
    QCDFakeRate(std::string filename, std::vector<std::string>& regionVec, int year);
    float GetFakeRate(double et, std::string regionName);
    static std::string GetFakeRateRegion(bool isBarrel, bool isEndcap1, bool isEndcap2, float eta=-999, float phi=-999, int run=-1);
    static bool isHEMElectron(float eta, float phi);

  private:
    std::vector<std::unique_ptr<TF1> > funcVec;
    std::map<std::string, int> regionToFuncIndexMap;
};
