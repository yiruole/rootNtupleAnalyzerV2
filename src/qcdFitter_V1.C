#include "qcdFitter.h"
#include <cmath>



double fitFunctionV1 ( double * x, double * par ){
  double fitval;
  double xx = x[0];
  if (xx < par[0]) fitval = par[1] + par[2] * xx;
  else             fitval = ( par[3] * ( xx - par[0] )) + par[1] + ( par[2] * par[0] );
  return fitval;
}

void qcdFitter::initializeV1(){
  
  int    n_par         = 4;
  double x_min         = 35.;
  double x_max         = 1000.;
  double y_min_barrel  = -0.005;
  double y_max_barrel  =  0.03;
  double y_min_endcap1 = -0.05;
  double y_max_endcap1 =  0.15;
  double y_min_endcap2 = -0.02;
  double y_max_endcap2 =  0.20;
  
  m_qcd_barrel_fitf   = new TF1 ("barrel_function" , fitFunctionV1, x_min, x_max, n_par );
  m_qcd_endcap1_fitf  = new TF1 ("endcap1_function", fitFunctionV1, x_min, x_max, n_par );
  m_qcd_endcap2_fitf  = new TF1 ("endcap2_function", fitFunctionV1, x_min, x_max, n_par );
  
  m_qcd_barrel_fitf  -> SetParLimits (0, 150., 250.);
  m_qcd_endcap1_fitf -> SetParLimits (0, 75. , 150.);
  m_qcd_endcap2_fitf -> SetParLimits (0, 75. , 150.);
  
  m_qcd_barrel_fitf  -> SetParLimits (1, y_min_barrel , y_max_barrel  );
  m_qcd_endcap1_fitf -> SetParLimits (1, y_min_endcap1, y_max_endcap1 );
  m_qcd_endcap2_fitf -> SetParLimits (1, y_min_endcap2, y_max_endcap2 );
  
  m_qcd_barrel_fitf  -> SetParLimits (2, -100., 0. );
  m_qcd_endcap1_fitf -> SetParLimits (2, -100., 0. );
  m_qcd_endcap2_fitf -> SetParLimits (2, -100., 0. );
  
  m_qcd_barrel_fitf  -> SetParameter( 0, (250. - x_min) / 2.0 );
  m_qcd_endcap1_fitf -> SetParameter( 0, (250. - x_min) / 2.0 );
  m_qcd_endcap2_fitf -> SetParameter( 0, (250. - x_min) / 2.0 );
  
  m_qcd_barrel_fitf  -> SetParameter( 1, (y_max_barrel  - y_min_barrel ) / 2.0 );
  m_qcd_endcap1_fitf -> SetParameter( 1, (y_max_endcap1 - y_min_endcap1) / 2.0 );
  m_qcd_endcap2_fitf -> SetParameter( 1, (y_max_endcap2 - y_min_endcap2) / 2.0 );
  
  m_qcd_barrel_fitf  -> SetParameter( 2, -0.001 );
  m_qcd_endcap1_fitf -> SetParameter( 2, -0.001 );
  m_qcd_endcap2_fitf -> SetParameter( 2, -0.001 );
  
  m_qcd_barrel_fit  = m_qcd_barrel_hist  -> Fit ( m_qcd_barrel_fitf  , "MRSQ" );
  m_qcd_endcap1_fit = m_qcd_endcap1_hist -> Fit ( m_qcd_endcap1_fitf , "MRSQ" );
  m_qcd_endcap2_fit = m_qcd_endcap2_hist -> Fit ( m_qcd_endcap2_fitf , "MRSQ" );
  
}

double getHighSlopeV1 ( TF1* func ) { 
  
  double slope = ( ( func -> GetParameter(1) ) + 
		   ( func -> GetParameter(2) * 
		     func -> GetParameter(0) ) -
		   ( func -> GetParameter(3) * 
		     func -> GetParameter(0) ) );

  return slope;
}
          
void qcdFitter::printV1(){
  
  std::cout << "barrel function:" << std::endl;
  std::cout << "\t" << "if pT < " << m_qcd_barrel_fitf -> GetParameter(0) << ": " << m_qcd_barrel_fitf -> GetParameter(1);
  if ( m_qcd_barrel_fitf -> GetParameter(2) < 0.0 )   std::cout << " - " << fabs ( m_qcd_barrel_fitf -> GetParameter(2) ) << " * pT" << std::endl;
  else                                                std::cout << " + " << fabs ( m_qcd_barrel_fitf -> GetParameter(2) ) << " * pT" << std::endl;
  std::cout << "\t" << "if pT > " << m_qcd_barrel_fitf -> GetParameter(0) << ": " << getHighSlopeV1 ( m_qcd_barrel_fitf );
  if ( m_qcd_barrel_fitf -> GetParameter(3) < 0.0 )   std::cout << " - " << fabs ( m_qcd_barrel_fitf -> GetParameter(3) ) << " * pT" << std::endl;
  else                                                std::cout << " + " << fabs ( m_qcd_barrel_fitf -> GetParameter(3) ) << " * pT" << std::endl;
  
  std::cout << "endcap1 function:" << std::endl;
  std::cout << "\t" << "if pT < " << m_qcd_endcap1_fitf -> GetParameter(0) << ": " << m_qcd_endcap1_fitf -> GetParameter(1);
  if ( m_qcd_endcap1_fitf -> GetParameter(2) < 0.0 )  std::cout << " - " << fabs ( m_qcd_endcap1_fitf -> GetParameter(2) ) << " * pT" << std::endl;
  else                                                std::cout << " + " << fabs ( m_qcd_endcap1_fitf -> GetParameter(2) ) << " * pT" << std::endl;
  std::cout << "\t" << "if pT > " << m_qcd_endcap1_fitf -> GetParameter(0) << ": " << getHighSlopeV1 ( m_qcd_endcap1_fitf );
  if ( m_qcd_endcap1_fitf -> GetParameter(3) < 0.0 )  std::cout << " - " << fabs ( m_qcd_endcap1_fitf -> GetParameter(3) ) << " * pT" << std::endl;
  else                                                std::cout << " + " << fabs ( m_qcd_endcap1_fitf -> GetParameter(3) ) << " * pT" << std::endl;
  
  std::cout << "endcap2 function:" << std::endl;
  std::cout << "\t" << "if pT < " << m_qcd_endcap2_fitf -> GetParameter(0) << ": " << m_qcd_endcap2_fitf -> GetParameter(1);
  if ( m_qcd_endcap2_fitf -> GetParameter(2) < 0.0 )  std::cout << " - " << fabs ( m_qcd_endcap2_fitf -> GetParameter(2) ) << " * pT" << std::endl;
  else                                                std::cout << " + " << fabs ( m_qcd_endcap2_fitf -> GetParameter(2) ) << " * pT" << std::endl;
  std::cout << "\t" << "if pT > " << m_qcd_endcap2_fitf -> GetParameter(0) << ": " << getHighSlopeV1 ( m_qcd_endcap2_fitf );
  if ( m_qcd_endcap2_fitf -> GetParameter(3) < 0.0 )  std::cout << " - " << fabs ( m_qcd_endcap2_fitf -> GetParameter(3) ) << " * pT" << std::endl;
  else                                                std::cout << " + " << fabs ( m_qcd_endcap2_fitf -> GetParameter(3) ) << " * pT" << std::endl;
}
