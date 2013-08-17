#ifndef EGAMMAAREACORRECTIONS_H
#define EGAMMAAREACORRECTIONS_H

class EGammaAreaCorrections { 

 public:
  EGammaAreaCorrections();
  ~EGammaAreaCorrections();

  double EffectiveArea03 ( double eta );
  double EffectiveArea04 ( double eta );

 private:

  int GetEtaBin( double eta );

  const int m_n_bins;

  double * m_eta_minimums ; 
  double * m_eta_maximums ; 
  double * m_mean_eff_area_03; 
  double * m_err_eff_area_03 ; 
  double * m_mean_eff_area_04; 
  double * m_err_eff_area_04 ; 

};


EGammaAreaCorrections::EGammaAreaCorrections():
  m_n_bins ( 7 )
{
  m_eta_minimums    [m_n_bins] = { 0.000, 1.000, 1.479, 2.000, 2.200, 2.300, 2.400 };
  m_eta_maximums    [m_n_bins] = { 1.000, 1.479, 2.000, 2.200, 2.300, 2.400, 999.0 };
  m_mean_eff_area_04[m_n_bins] = { 0.190, 0.250, 0.120, 0.210, 0.270, 0.440, 0.520 };
  m_err_eff_area_04 [m_n_bins] = { 0.006, 0.006, 0.004, 0.007, 0.020, 0.030, 0.050 };
  m_mean_eff_area_03[m_n_bins] = { 0.100, 0.120, 0.085, 0.110, 0.120, 0.120, 0.130 };
  m_err_eff_area_03 [m_n_bins] = { 0.002, 0.003, 0.002, 0.003, 0.004, 0.005, 0.006 };
}

EGammaAreaCorrections::~EGammaAreaCorrections(){}

int  EGammaAreaCorrections::GetEtaBin      ( double eta ) {
  
  for (int i = 0; i < m_n_bins; ++i ){ 
    double bin_minimum = m_eta_minimums[i];
    double bin_maximum = m_eta_maximums[i];
    if ( eta >= bin_minimum && eta < bin_maximum ) return i;
  }

}

double EGammaAreaCorrections::EffectiveArea03( double eta ) {
  int bin = GetEtaBin ( eta ) ;
  return m_mean_eff_area_03[bin];
}

double EGammaAreaCorrections::EffectiveArea04( double eta ) {
  int bin = GetEtaBin ( eta ) ;
  return m_mean_eff_area_04[bin];
}

#endif 
