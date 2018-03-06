//From Dave, Feb. 13, 2018
// run-weighted averages over all 2016 data
// for HighPT Mu ID + TrkRelIso03

class MuonScaleFactors {
  public:
    static float LookupIDSF(float eta)
    {
      if(-2.4 <= eta  && eta < -2.1)
        return 0.97;
      else if(eta < -1.6)
        return 0.98;
      else if(eta < -1.2)
        return 0.99;
      else if(eta < -0.9)
        return 0.98;
      else if(eta < -0.3)
        return 0.99;
      else if(eta < -0.2)
        return 0.97;
      else if(eta < 0.2)
        return 0.99;
      else if(eta < 0.3)
        return 0.96;
      else if(eta < 0.9)
        return 0.99;
      else if(eta < 1.2)
        return 0.97;
      else if(eta < 1.6)
        return 0.99;
      else if(eta < 2.1)
        return 0.98;
      else if(eta < 2.4)
        return 0.97;
      else
        return -1;
    }
    static float LookupIsoSF(float eta)
    {
      if(-2.4 <= eta  && eta < -2.1)
        return 0.999;
      else if(eta < -1.6)
        return 1.0;
      else if(eta < -1.2)
        return 0.999;
      else if(eta < -0.9)
        return 0.999;
      else if(eta < -0.3)
        return 0.998;
      else if(eta < -0.2)
        return 0.998;
      else if(eta < 0.2)
        return 0.998;
      else if(eta < 0.3)
        return 0.997;
      else if(eta < 0.9)
        return 0.998;
      else if(eta < 1.2)
        return 1.0;
      else if(eta < 1.6)
        return 0.999;
      else if(eta < 2.1)
        return 1.0;
      else if(eta < 2.4)
        return 1.0;
      else
        return -1;
    }
};

