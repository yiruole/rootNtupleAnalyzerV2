// from https://twiki.cern.ch/twiki/bin/view/CMS/EgammaIDRecipesRun2#Efficiencies_and_scale_factors
// and https://indico.cern.ch/event/604912/contributions/2490008/attachments/1418885/2173433/HEEP7_Moriond_GSFix_final_RW_v3.pdf [slide 17]

class ElectronScaleFactors2016 {

  public:
    static float LookupRecoSF(float scEta)
    {
      if(scEta<-2.45)
          return 1.318;
      if(scEta<-2.4)
          return 1.114;
      if(scEta<-2.3)
          return 1.025;
      if(scEta<-2.2)
          return 1.014;
      if(scEta<-2.0)
          return 1.007;
      if(scEta<-1.8)
          return 0.995;
      if(scEta<-1.63)
          return 0.995;
      if(scEta<-1.566)
          return 0.992;
      if(scEta<-1.444)
          return 0.963;
      if(scEta<-1.2)
          return 0.99;
      if(scEta<-1.0)
          return 0.986;
      if(scEta<-0.6)
          return 0.982;
      if(scEta<-0.4)
          return 0.985;
      if(scEta<-0.2)
          return 0.982;
      if(scEta<0.0)
          return 0.98;
      if(scEta<0.2)
          return 0.985;
      if(scEta<0.4)
          return 0.989;
      if(scEta<0.6)
          return 0.988;
      if(scEta<1.0)
          return 0.988;
      if(scEta<1.2)
          return 0.988;
      if(scEta<1.444)
          return 0.988;
      if(scEta<1.566)
          return 0.968;
      if(scEta<1.63)
          return 0.99;
      if(scEta<1.8)
          return 0.993;
      if(scEta<2.0)
          return 0.992;
      if(scEta<2.2)
          return 0.998;
      if(scEta<2.3)
          return 1.001;
      if(scEta<2.4)
          return 0.99;
      if(scEta<2.45)
          return 0.971;
      if(scEta<2.5)
          return 0.907;
      else
        return 0.907;
    }
    static float LookupHeepSF(float scEta)
    {
      if(fabs(scEta)<0.5)
        return 0.967;
      else if(fabs(scEta)<1.566)
        return 0.975;
      else if(fabs(scEta)<2.5)
        return 0.983;
    }

};
