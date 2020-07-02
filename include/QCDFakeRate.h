#include <vector>
#include <string>
#include <memory>
#include "TF1.h"


class QCDFakeRate {

  public:
    QCDFakeRate();
    QCDFakeRate(std::string filename, std::vector<std::string>& regionVec, int year);
    float GetFakeRate(double et, std::string regionName);

  private:
    std::vector<std::unique_ptr<TF1> > funcVec;
    std::map<std::string, int> regionToFuncIndexMap;
};
