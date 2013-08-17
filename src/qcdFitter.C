#include "qcdFitter.h"
#include <cmath>
#include <stdlib.h> 

//---------------------------------------------------------------------------
// Helper functions
//---------------------------------------------------------------------------

bool isBarrel ( double eta ) {
  bool isBarrel  = ( fabs(eta) > 0.000 && fabs(eta) < 1.442 );
  return isBarrel;
}

bool isEndcap1 ( double eta ) {
  bool isEndcap1  = ( fabs(eta) > 1.560 && fabs(eta) < 2.000 );
  return isEndcap1;
}

bool isEndcap2 ( double eta ) {
  bool isEndcap2  = ( fabs(eta) > 2.000 && fabs(eta) < 2.500 );
  return isEndcap2;
}

//---------------------------------------------------------------------------
// Constructor
//---------------------------------------------------------------------------

qcdFitter::qcdFitter( int version, 
		      std::string & file_name, 
		      std::string & barrel_plot_name ,
		      std::string & endcap1_plot_name,
		      std::string & endcap2_plot_name ):
  m_version           ( version ),
  m_file_name         ( file_name ),
  m_barrel_plot_name  ( barrel_plot_name ),
  m_endcap1_plot_name ( endcap1_plot_name ),
  m_endcap2_plot_name ( endcap2_plot_name ),
  m_confidence_level  ( 0.683 ),
  m_file              ( new TFile ( file_name.c_str() ) ),
  m_qcd_barrel_hist   ( (TH1F*) m_file -> Get( barrel_plot_name .c_str() )),
  m_qcd_endcap1_hist  ( (TH1F*) m_file -> Get( endcap1_plot_name.c_str() )),
  m_qcd_endcap2_hist  ( (TH1F*) m_file -> Get( endcap2_plot_name.c_str() ))
{
  if ( m_version == 1 ) initializeV1();
  else std::cout << "ERROR! I don't know anything about version " << m_version << " of QCD fit functions" << std::endl;
}

//---------------------------------------------------------------------------
// Destructor
//---------------------------------------------------------------------------

qcdFitter::~qcdFitter(){ 
  if ( m_qcd_barrel_fitf  ) delete m_qcd_barrel_fitf  ;
  if ( m_qcd_endcap1_fitf ) delete m_qcd_endcap1_fitf ;
  if ( m_qcd_endcap2_fitf ) delete m_qcd_endcap2_fitf ;
  if ( m_qcd_barrel_hist  ) delete m_qcd_barrel_hist  ;
  if ( m_qcd_endcap1_hist ) delete m_qcd_endcap1_hist ;
  if ( m_qcd_endcap2_hist ) delete m_qcd_endcap2_hist ;
  if ( m_file ) {
    m_file -> Close();
    delete m_file;
  }
}

//---------------------------------------------------------------------------
// Print information to stdout
//---------------------------------------------------------------------------

void qcdFitter::print(){
  if ( m_version == 1 ) printV1();
  else std::cout << "ERROR! I don't know anything about version " << m_version << " of QCD fit functions" << std::endl;
}

//---------------------------------------------------------------------------
// Evalulate the fake rate for a given pt, eta
//---------------------------------------------------------------------------

double qcdFitter::getFakeRate( double pt, double eta ) {

  bool is_barrel  = isBarrel ( eta );
  bool is_endcap1 = isEndcap1( eta );
  bool is_endcap2 = isEndcap2( eta );

  double fakeRate = 0.0;

  if      ( is_barrel  ) fakeRate = m_qcd_barrel_fitf  -> Eval ( pt );
  else if ( is_endcap1 ) fakeRate = m_qcd_endcap1_fitf -> Eval ( pt );
  else if ( is_endcap2 ) fakeRate = m_qcd_endcap2_fitf -> Eval ( pt );
  else { 
    std::cout << "ERROR!  I don't know how to handle eta = " << eta << std::endl;
    exit(0);
  }
  
  return fakeRate;
}

//---------------------------------------------------------------------------
// Evaluate the fit uncertainty on the fake rate for a given pt, eta
// All uncertainties are symmetric
//---------------------------------------------------------------------------

double qcdFitter::getFakeRateErr( double pt, double eta ) {
  
  bool is_barrel  = isBarrel ( eta );
  bool is_endcap1 = isEndcap1( eta );
  bool is_endcap2 = isEndcap2( eta );
  
  double fakeRateErr = 0.0;

  double x [1] = { pt };
  double confidence_interval[1];

  if ( is_barrel ) { 
    m_qcd_barrel_fit  -> GetConfidenceIntervals (1, 1, 1, x, confidence_interval, m_confidence_level, false);
    fakeRateErr = confidence_interval[0];
  }

  else if ( is_endcap1 ) { 
    m_qcd_endcap1_fit -> GetConfidenceIntervals (1, 1, 1, x, confidence_interval, m_confidence_level, false);
    fakeRateErr = confidence_interval[0];
  }

  else if ( is_endcap2 ) { 
    m_qcd_endcap2_fit -> GetConfidenceIntervals (1, 1, 1, x, confidence_interval, m_confidence_level, false);
    fakeRateErr = confidence_interval[0];
  }

  else { 
    std::cout << "ERROR!  I don't know how to handle eta = " << eta << std::endl;
    exit(0);
  }
  
  return fakeRateErr ;

}
