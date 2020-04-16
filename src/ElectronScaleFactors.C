#include <math.h>
#include <algorithm>
// from https://twiki.cern.ch/twiki/bin/view/CMS/EgammaIDRecipesRun2#Efficiencies_and_scale_factors
// and https://indico.cern.ch/event/604912/contributions/2490008/attachments/1418885/2173433/HEEP7_Moriond_GSFix_final_RW_v3.pdf [slide 17]
// and https://indico.cern.ch/event/831669/contributions/3485543/attachments/1871797/3084930/ApprovalSlides_EE_v3.pdf [slide 10]
class ElectronScaleFactors2016 {

  public:

    static float LookupHeepSF(float scEta) {
      if(fabs(scEta)<1.566)
        return 0.983;
      else if(fabs(scEta)<2.5)
        return 0.991;
      return -1.;
    }

    // this is the prompt uncertainty
    static float LookupHeepSFSyst(float scEta, float et) {
      if(fabs(scEta)<1.566) {
        if(et < 90)
          return 0.01;
        else
          return 0.01*std::min(1+(et-90)*0.0022,3.0);
      }
      else if(fabs(scEta)<2.5) {
        if(et < 90)
          return 0.01;
        else
          return 0.01*std::min(1+(et-90)*0.0143,4.0);
      }
      return -1.;
    }

};

// see: https://twiki.cern.ch/twiki/bin/view/CMS/Egamma2017DataRecommendations#2017_Efficiency_Scale_Factors
class ElectronScaleFactors2017 {

  public:

    static constexpr float zVtxSF = 0.991;

    static float LookupHeepSF(float scEta)
    {
      if(fabs(scEta)<1.566)
        return 0.968;  // from the slides: https://indico.cern.ch/event/831669/contributions/3485543/attachments/1871797/3084930/ApprovalSlides_EE_v3.pdf
      else if(fabs(scEta)<2.5)
        return 0.973;
      return -1.;
    }

    static float LookupHeepSFSyst(float scEta, float et) {
      if(fabs(scEta)<1.566) {
        if(et < 90)
          return 0.01;
        else
          return 0.01*std::min(1+(et-90)*0.0022,3.0);
      }
      else if(fabs(scEta)<2.5) {
        if(et < 90)
          return 0.02;
        else
          return 0.01*std::min(1+(et-90)*0.0143,5.0);
      }
      return -1.;
    }
};


class ElectronScaleFactors2018 {

  public:

    // for HEEPv7.0-2018Prompt 
    static float LookupHeepSF(float scEta)
    {
      if(fabs(scEta)<1.566)
        return 0.969;
      else if(fabs(scEta)<2.5)
        return 0.984;
      return -1.;
    }

    static float LookupHeepSFSyst(float scEta, float et) {
      return ElectronScaleFactors2017::LookupHeepSFSyst(scEta, et);
    }
};
