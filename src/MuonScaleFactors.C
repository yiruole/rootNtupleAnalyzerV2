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

    static float GetScaleFactorForUncertainty(float eta, float p)
    {
      // https://twiki.cern.ch/twiki/bin/viewauth/CMS/TWikiEXO-MUODocumentationRun2

      //The final p-dependent SFs used to estimate the systematic uncertainty in the Barrel is taken as the linear function describing the MC efficiency,
      //while in the Endcaps the scale factor is calculated as the ratio of the functions describing the Data and MC efficiencies:
      //
      //    eff(P) = a + b * P where
      //    MC Eff: a=0.9936, b =-3.71e-06 when |eta|< 1.6 and P>100 GeV
      //    MC Eff: a =0.9908, b=-1.26e-5 when 1.6 < |eta| < 2.4 and P>200 GeV
      //    Data Eff: a =0.9784, b=-4.73e-5 when 1.6 < |eta| < 2.4 and P>200 GeV 
      if(fabs(eta) <= 1.6 && p > 100)
      {
        float a = 0.9936;
        float b = -3.71e-6;
        return a + b*p;
      }
      else if(fabs(eta) > 1.6 && fabs(eta) <= 2.4 && p > 200)
      {
        float a = 0.9908;
        float b = -1.26e-5;
        float mcEff = a+b*p;
        a = 0.9784;
        b = -4.73e-5;
        float dataEff = a+b*p;
        return dataEff/mcEff;
      }
      else
        return 1.0;

    }

    static float GetVetoMCDataEffRatio(float eta)
    {
      return (1-GetDataEfficiency(eta))/(1-GetMCEfficiency(eta));
    }

    static float GetDataEfficiency(float eta)
    {
      // from https://gaperrin.web.cern.ch/gaperrin/tnp/TnP2016/2016Data_Moriond2017_6_12_16/JSON/RunBCDEF/EfficienciesAndSF_BCDEF.root
      // MC_NUM_HighPtID_DEN_genTracks_PAR_eta/efficienciesDATA/eta_DATA
      if(-2.4 <= eta  && eta < -2.1)
        return 9.46785032749176025e-01;
      else if(eta < -1.6)
        return 9.72316265106201172e-01;
      else if(eta < -1.2)
        return 9.78777945041656494e-01;
      else if(eta < -0.9)
        return 9.49105560779571533e-01;
      else if(eta < -0.3)
        return 9.68738019466400146e-01;
      else if(eta < -0.2)
        return 8.62136840820312500e-01;
      else if(eta < 0.2)
        return 9.65130269527435303e-01;
      else if(eta < 0.3)
        return 8.46984624862670898e-01;
      else if(eta < 0.9)
        return 9.66875076293945312e-01;
      else if(eta < 1.2)
        return 9.46293532848358154e-01;
      else if(eta < 1.6)
        return 9.77776467800140381e-01;
      else if(eta < 2.1)
        return 9.75666642189025879e-01;
      else if(eta <= 2.4)
        return 9.53107833862304688e-01;
      else
        return 0;
    }

    static float GetMCEfficiency(float eta)
    {
      // from https://gaperrin.web.cern.ch/gaperrin/tnp/TnP2016/2016Data_Moriond2017_6_12_16/JSON/RunBCDEF/EfficienciesAndSF_BCDEF.root
      // MC_NUM_HighPtID_DEN_genTracks_PAR_eta/efficienciesMC/eta_MC
      if(-2.4 <= eta  && eta < -2.1)
        return 9.79680061340332031e-01;
      else if(eta < -1.6)
        return 9.91421937942504883e-01;
      else if(eta < -1.2)
        return 9.93640184402465820e-01;
      else if(eta < -0.9)
        return 9.81082260608673096e-01;
      else if(eta < -0.3)
        return 9.84158456325531006e-01;
      else if(eta < -0.2)
        return 8.96989524364471436e-01;
      else if(eta < 0.2)
        return 9.78685915470123291e-01;
      else if(eta < 0.3)
        return 8.90416383743286133e-01;
      else if(eta < 0.9)
        return 9.83016192913055420e-01;
      else if(eta < 1.2)
        return 9.81224596500396729e-01;
      else if(eta < 1.6)
        return 9.93545174598693848e-01;
      else if(eta < 2.1)
        return 9.92338299751281738e-01;
      else if(eta <= 2.4)
        return 9.83877837657928467e-01;
      else
        return 0;
    }
};

