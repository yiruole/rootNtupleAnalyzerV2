// from the Z' group
// modified from
// https://gitlab.cern.ch/cms-zprime-dileptons/DiEleScaleFactors/blob/master/Ele27WPLooseTrigTurnOn.C
// SIC, Mar 24, 2016

#ifndef DIELESCALEFACTORS_ELE27WPLOOSETRIGTURN_C
#define DIELESCALEFACTORS_ELE27WPLOOSETRIGTURN_C

#include "TMath.h"
#include "TRandom3.h"

namespace trigEle27{
  class TurnOn {
  public:
    class TurnOnFunc {
      float maxEff_,midPoint_,turnOn_;      
    public:
      TurnOnFunc():maxEff_(0),midPoint_(0),turnOn_(0){}
      TurnOnFunc(float maxEff,float midPoint,float turnOn):maxEff_(maxEff),midPoint_(midPoint),turnOn_(turnOn){}
      float operator()(float et)const{
  return 0.5*maxEff_*(1+TMath::Erf((et-midPoint_)/(sqrt(2)*turnOn_)));
      }
    };
    
    class DiTurnOnFunc {
    private:
      TurnOnFunc turnOn1_,turnOn2_;
    public:
      DiTurnOnFunc(){}
      DiTurnOnFunc(const TurnOnFunc& turnOn1,const TurnOnFunc& turnOn2):
  turnOn1_(turnOn1),turnOn2_(turnOn2){}
      float operator()(float et)const{return turnOn1_(et)+turnOn2_(et);}
    };
    
    template<typename T> 
    struct Nop{
      T operator()(const T& val)const{return val;}
    };
    template<typename T> 
    struct Abs{
      T operator()(const T& val)const{return std::abs(val);}
    };

    template<typename T,typename Func=Nop<T>>
    class ValRange {
    private:
      Func manipFunc_;
      T minVal_;
      T maxVal_;
    public:
      ValRange(){}
      ValRange(const T& minVal,const T& maxVal):minVal_(minVal),maxVal_(maxVal){}
      bool operator()(const T& inputVal)const{return manipFunc_(inputVal)>=minVal_ && manipFunc_(inputVal)<maxVal_;}
    };
   
    using ValRangeAbsF = ValRange<float,Abs<float>>;
    
  private:
    std::vector<std::pair<ValRangeAbsF,DiTurnOnFunc>> turnOnData_;
  public:
    TurnOn(){
      // this is 2015 WPLoose (no eta restriction)
//      turnOnData_.push_back(std::make_pair<ValRangeAbsF,DiTurnOnFunc>({0.0,1.5},
//  {{0.241,30.0,1.68},{0.687,18.5,16.1}}));
//      turnOnData_.push_back(std::make_pair<ValRangeAbsF,DiTurnOnFunc>({1.5,2.5},
//  {{0.784,24.3,5.29},{0.095,25.2,25}}));
      // this is for 2016 (ichep) WPLoose eta2.1
      //turnOnData_.push_back(std::make_pair<ValRangeAbsF,DiTurnOnFunc>({0.0,1.5},  {{0.76,23.5,11.5},{0.189,5.24e-7,53.8}}));
      //turnOnData_.push_back(std::make_pair<ValRangeAbsF,DiTurnOnFunc>({1.5,2.1},   {{0.673,27.4,2.45},{0.174,35.8,7.95}}));
      //turnOnData_.push_back(std::make_pair<ValRangeAbsF,DiTurnOnFunc>({2.1,2.5},   {{0.,35.4,1.03},{0.,37.6,2.09}}));
      // this is WPTight_eta2p1 on re-reco, from (slide 4, far right): https://indico.cern.ch/event/591192/contributions/2385819/attachments/1379390/2096232/2016-11-29Xuyang_rereco.pdf
      turnOnData_.push_back(std::make_pair<ValRangeAbsF,DiTurnOnFunc>({0.0,1.5},  {{0.702,22.65,11.149},{0.223,37.622,37.619}}));
      turnOnData_.push_back(std::make_pair<ValRangeAbsF,DiTurnOnFunc>({1.5,2.1},   {{-6.245,-373.183,-1453.482},{3.155,7.617,15.789}}));
      turnOnData_.push_back(std::make_pair<ValRangeAbsF,DiTurnOnFunc>({2.1,2.5},   {{0,0,0},{0,0,0}}));
    }
    float operator()(float et,float eta)const{
      for(const auto& data : turnOnData_){
  if(data.first(eta)) return data.second(et);
      }
      return 0;
    }
    

  };
  
  TurnOn turnOnData;
  TRandom3 randNrGen;
  
  float turnOn(float scEt,float scEta){return turnOnData(scEt,scEta);}
  
  bool passTrig(float scEt,float scEta){return turnOn(scEt,scEta)>randNrGen.Uniform(0,1);}

}
  


#endif


