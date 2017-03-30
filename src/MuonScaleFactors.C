//From Dave, Feb. 7
// run-weighted averages over all 2016 data
// for HighPT Mu ID + TrkRelIso03

class MuonScaleFactors {
  public:
    static float LookupIDSF(float pt)
    {
      if(pt<55)
        return 0.9813326964101629;
      else if(pt<60)
        return 0.9811215588407185;
      else if(pt<120)
        return 0.9888030350742609;
      else
        return 1.0179598732419621;
    }
    static float LookupIsoSF(float pt)
    {
      if(pt<55)
        return 0.9985465327438463;
      else if(pt<60)
        return 0.9988891755735836;
      else if(pt<120)
        return 0.9989480835906359;
      else
        return 1.0006806854046033;
    }
};

