#ifndef QCD_FITTER_H
#define QCD_FITTER_H

#include <TFitResult.h>
#include <TH1F.h>
#include <TF1.h>
#include <TFile.h>

class qcdFitter { 
  
 public:
  
  qcdFitter( int version, std::string & file_name, 
	     std::string & barrel_plot_name ,
	     std::string & endcap1_plot_name,
	     std::string & endcap2_plot_name );
  
  ~qcdFitter();
  
  void print();
  
  double getFakeRate   ( double pt, double eta );
  double getFakeRateErr( double pt, double eta );
  
  TH1F * getBarrelHist () { return m_qcd_barrel_hist ; }
  TH1F * getEndcap1Hist() { return m_qcd_endcap1_hist; }
  TH1F * getEndcap2Hist() { return m_qcd_endcap2_hist; }

  TF1 * getBarrelFunction () { return m_qcd_barrel_fitf ; }
  TF1 * getEndcap1Function() { return m_qcd_endcap1_fitf; }
  TF1 * getEndcap2Function() { return m_qcd_endcap2_fitf; }

  TFitResultPtr getBarrelFitResult () { return m_qcd_barrel_fit ; }
  TFitResultPtr getEndcap1FitResult() { return m_qcd_endcap1_fit; }
  TFitResultPtr getEndcap2FitResult() { return m_qcd_endcap2_fit; }
  
 private:

  // Confidence level (should be 0.683 for 1 sigma) 
  double m_confidence_level;
  
  // File and hist names
  std::string m_file_name;
  std::string m_barrel_plot_name;
  std::string m_endcap1_plot_name;
  std::string m_endcap2_plot_name;

  // File
  TFile * m_file;
  
  // Fit functions
  TF1 * m_qcd_barrel_fitf ;
  TF1 * m_qcd_endcap1_fitf;
  TF1 * m_qcd_endcap2_fitf;
  
  // Fit histograms;
  TH1F * m_qcd_barrel_hist ;
  TH1F * m_qcd_endcap1_hist;
  TH1F * m_qcd_endcap2_hist;

  // Fit results;
  TFitResultPtr m_qcd_barrel_fit ;
  TFitResultPtr m_qcd_endcap1_fit;
  TFitResultPtr m_qcd_endcap2_fit;
  
  // Version number
  const int m_version;
  
  // Functions for version 1
  void   initializeV1();
  void   printV1();
  
};

#endif 
