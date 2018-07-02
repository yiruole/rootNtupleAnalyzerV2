#include <math.h>

extern "C" {
double etaToTheta(double eta)
{
  //  if(eta<0) return -2*atan(exp(eta));
  //  else return 2*atan(exp(-1*eta));
  return 2*atan(exp(-1*eta));
  //else return 2*atan(exp(-1*eta));

}

double thetaToEta(double theta)
{
  const float kPi = 3.1415926;
  //first bounds check theta to get into -pi/2 - pi/2 range
  while( fabs(theta) > kPi/2.){
    if(theta>0) theta-=kPi;
    else theta+=kPi;
  }
  //now check sign
  if(theta<0) return log(tan(fabs(theta/2.)));
  else return -1.*log(tan(theta/2.));
}

double detEtaFromEvnt(double evntEta,double z0)
{
 
  double thetaEvt = etaToTheta(evntEta);
  double z = 129.4 / tan(thetaEvt); //129.4 is the average barrel radius
  double zTot = z+z0;

  if(fabs(zTot)<269){ //269 is an emperically derived number which means that < its likely in th barrel
    return zTot !=0 ? thetaToEta(atan(129.4/zTot)) : 0.; //otherwise endcap time
  }
  double endcapZ = 319.2; //average z position of endcap
  if(evntEta<0) endcapZ*=-1;
  double rxy = tan(thetaEvt) * (endcapZ-z0);
  return thetaToEta(atan(rxy/endcapZ));

}

}

