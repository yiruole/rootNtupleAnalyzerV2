#include <math.h>
#include <algorithm>
#include <string>
#include <stdexcept>
// UL
// https://indico.cern.ch/event/1259725/contributions/5294821/attachments/2603712/4496433/HEEP%20ID%202016UL%20Update%20for%20EGamma.pdf
class ElectronScaleFactors2016preVFP {

  public:
    static double LookupHeepSF(const double scEta) {
      if(fabs(scEta)<1.566)
        return 0.989;
      else if(fabs(scEta)<2.5)
        return 0.992;
      return -1.;
    }

    static double LookupHeepSFSyst(const double scEta, const double et) {
      if(fabs(scEta)<1.566)
        return 0.0051;
      else if(fabs(scEta)<2.5)
        return 0.0076;
      return -1.;
    }

};

class ElectronScaleFactors2016postVFP {

  public:
    static double LookupHeepSF(const double scEta) {
      if(fabs(scEta)<1.566)
        return 0.98;
      else if(fabs(scEta)<2.5)
        return 0.989;
      return -1.;
    }

    static double LookupHeepSFSyst(const double scEta, const double et) {
      if(fabs(scEta)<1.566)
        return 0.0051;
      else if(fabs(scEta)<2.5)
        return 0.0081;
      return -1.;
    }

};

class ElectronScaleFactors2017 {

  public:
    static constexpr double zVtxSF = 0.991;

    static double LookupHeepSF(const double scEta)
    {
      if(fabs(scEta)<1.566)
        return 0.979;
      else if(fabs(scEta)<2.5)
        return 0.987;
      return -1.;
    }

    static double LookupHeepSFSyst(const double scEta, const double et) {
      if(fabs(scEta)<1.566)
        return 0.0051;
      else if(fabs(scEta)<2.5)
        return 0.01;
      return -1.;
    }
};


class ElectronScaleFactors2018 {
  public:
    static double LookupHeepSF(const double scEta)
    {
      if(fabs(scEta)<1.566)
        return 0.973;
      else if(fabs(scEta)<2.5)
        return 0.98;
      return -1.;
    }

    static double LookupHeepSFSyst(const double scEta, const double et) {
      if(fabs(scEta)<1.566)
        return 0.0041;
      else if(fabs(scEta)<2.5)
        return 0.0112;
      return -1.;
    }
};

class ElectronScaleFactorsRunII {
  public:
    static double LookupHeepSF(const double scEta, const std::string analysisYear) {
      if(analysisYear=="2016preVFP")
        return ElectronScaleFactors2016preVFP::LookupHeepSF(scEta);
      else if(analysisYear=="2016postVFP")
        return ElectronScaleFactors2016postVFP::LookupHeepSF(scEta);
      else if(analysisYear=="2017")
        return ElectronScaleFactors2017::LookupHeepSF(scEta);
      else if(analysisYear=="2018")
        return ElectronScaleFactors2018::LookupHeepSF(scEta);
      throw std::runtime_error("Did not understand year given: "+analysisYear);
    }

    static double LookupHeepSFSyst(const double scEta, const double et, const std::string analysisYear) {
      if(analysisYear=="2016preVFP")
        return ElectronScaleFactors2016preVFP::LookupHeepSFSyst(scEta, et);
      else if(analysisYear=="2016postVFP")
        return ElectronScaleFactors2016postVFP::LookupHeepSFSyst(scEta, et);
      else if(analysisYear=="2017")
        return ElectronScaleFactors2017::LookupHeepSFSyst(scEta, et);
      else if(analysisYear=="2018")
        return ElectronScaleFactors2018::LookupHeepSFSyst(scEta, et);
      throw std::runtime_error("Did not understand year given: "+analysisYear);
    }
};
