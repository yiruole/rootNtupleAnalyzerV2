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
        return 0;
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
        return 0;
    }

    static float LookupHIPSF(float eta)
    {
      // from Dave, Mar. 8 2018
      //trackerHIP = '
      //  *(0.991237*(Eta_muon1>-2.4)*(Eta_muon1<-2.1)
      //    +0.994853*(Eta_muon1>-2.1)*(Eta_muon1<-1.6)
      //    +0.996413*(Eta_muon1>-1.6)*(Eta_muon1<-1.2)
      //    +0.997157*(Eta_muon1>-1.2)*(Eta_muon1<-0.9)
      //    +0.997512*(Eta_muon1>-0.9)*(Eta_muon1<-0.6)
      //    +0.99756*(Eta_muon1>-0.6)*(Eta_muon1<-0.3)
      //    +0.996745*(Eta_muon1>-0.3)*(Eta_muon1<-0.2)
      //    +0.996996*(Eta_muon1>-0.2)*(Eta_muon1<0.2)
      //    +0.99772*(Eta_muon1>0.2)*(Eta_muon1<0.3)
      //    +0.998604*(Eta_muon1>0.3)*(Eta_muon1<0.6)
      //    +0.998321*(Eta_muon1>0.6)*(Eta_muon1<0.9)
      //    +0.997682*(Eta_muon1>0.9)*(Eta_muon1<1.2)
      //    +0.995252*(Eta_muon1>1.2)*(Eta_muon1<1.6)
      //    +0.994919*(Eta_muon1>1.6)*(Eta_muon1<2.1)
      //    +0.987334*(Eta_muon1>2.1)*(Eta_muon1<2.4) )'

      if(-2.4 <= eta  && eta < -2.1)
        return 0.991237;
      else if(eta < -1.6)
        return 0.994853;
      else if(eta < -1.2)
        return 0.996413;
      else if(eta < -0.9)
        return 0.997157;
      else if(eta < -0.6)
        return 0.997512;
      else if(eta < -0.3)
        return 0.99756;
      else if(eta < -0.2)
        return 0.996745;
      else if(eta < 0.2)
        return 0.996996;
      else if(eta < 0.3)
        return 0.99772;
      else if(eta < 0.6)
        return 0.998604;
      else if(eta < 0.9)
        return 0.998321;
      else if(eta < 1.2)
        return 0.997682;
      else if(eta < 1.6)
        return 0.995252;
      else if(eta < 2.1)
        return 0.994919;
      else if(eta < 2.4)
        return 0.987334;
      else
        return 0;
    }

    static float LookupTrackingSF(float eta)
    {
      // https://twiki.cern.ch/twiki/bin/view/CMS/MuonWorkInProgressAndPagResults

      // etabins: [0        ,0.2       ,0.4      ,0.6      ,0.8      ,1.0      ,1.2      ,1.4      ,1.6      ,1.8      ,.2.0     ,2.2,2.4]
      // SF:      [0.9969965,0.9977118,0.9980776,0.9978039,0.9979708,0.9971477,0.9962274,0.9954786,0.9957808,0.9938919,0.9929427,0.9873133]

      if(fabs(eta) < 0.2)
        return 0.9969965;
      else if(fabs(eta) < 0.4)
        return 0.9977118;
      else if(fabs(eta) < 0.6)
        return 0.9980776;
      else if(fabs(eta) < 0.8)
        return 0.9978039;
      else if(fabs(eta) < 1.0)
        return 0.9979708;
      else if(fabs(eta) < 1.2)
        return 0.9971477;
      else if(fabs(eta) < 1.4)
        return 0.9962274;
      else if(fabs(eta) < 1.6)
        return 0.9954786;
      else if(fabs(eta) < 1.8)
        return 0.9957808;
      else if(fabs(eta) < 2.0)
        return 0.9938919;
      else if(fabs(eta) < 2.2)
        return 0.9929427;
      else if(fabs(eta) < 2.4)
        return 0.9873133;
      else
        return 0;
    }

    static float GetTotalScaleFactor(float eta)
    {
      return LookupIDSF(eta)*LookupIsoSF(eta)*LookupHIPSF(eta)*LookupTrackingSF(eta);
    }
};

