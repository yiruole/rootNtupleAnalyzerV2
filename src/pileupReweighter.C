#include <iostream>
#include <string>
#include <sstream>
#include <fstream>
#include <algorithm>
#include <iterator>
#include <memory>

#include "pileupReweighter.h"
#include "TFile.h"

PileupReweighter::PileupReweighter():
  m_max_n_pileup ( 0 ) ,
  m_weights_calculated ( false ) 
{}

PileupReweighter::~PileupReweighter(){}

double PileupReweighter::getPileupWeight ( int n_pileup ) { 
  
  if ( n_pileup > m_max_n_pileup ) {
    std::cout << "ERROR: System is asking for n(pileup) = " << n_pileup << " but we only have information for pileup up to " << m_max_n_pileup << std::endl;
    return -1; 
  }
  
  if ( n_pileup == -1 ) {
    std::cout << "ERROR: System is asking for n(pileup) = " << n_pileup << ", which is not a valid index number" << std::endl;
    return -1; 
  }

  return m_pileup_weights[n_pileup];
  
}

void PileupReweighter::readPileupDataFile ( std::string * file_name ) { 
  
  m_data_file_name = * file_name ;
  
  TFile * file = new TFile ( file_name -> c_str() ) ;
  
  if ( !file ) { 
    std::cout << "ERROR: I cannot open the pileup file: " << file_name << std::endl;
    return;
  }

  TH1F* pileup_hist = (TH1F*) file -> Get("pileup");

  if ( !pileup_hist ) { 
    std::cout << "ERROR: I can open the pileup file: " << file_name << std::endl;
    std::cout << "       But I cannot open the hist: pileup" << std::endl;
    return;
  }
  
  int nbins = pileup_hist -> GetNbinsX();
  int last_bin_center = (int) pileup_hist -> GetBinCenter ( nbins ) ;
  
  pileup_hist -> Sumw2();
  pileup_hist -> Scale ( 1.0 / pileup_hist -> Integral ( 0, nbins + 1 ) );
  
  m_data_pileup_pdf.resize ( last_bin_center + 1 ) ;

  for (int pileup = 0; pileup <= last_bin_center; ++pileup ){
    int bin = pileup_hist -> FindBin ( pileup ) ;
    if ( bin == 0 || bin == nbins + 1 ) 
      m_data_pileup_pdf[pileup] = 0.0;
    else 
      m_data_pileup_pdf[pileup] = pileup_hist -> GetBinContent ( bin ) ;
  }

  file -> Close();
  if ( file ) delete file;

}

std::vector<std::string> PileupReweighter::split(const std::string& s, const std::string& delim, const bool keep_empty = false) {
  std::vector<std::string> result;
    if (delim.empty()) {
        result.push_back(s);
        return result;
    }
    std::string::const_iterator substart = s.begin(), subend;
    while (true) {      
      subend = std::search(substart, s.end(), delim.begin(), delim.end());
      std::string temp(substart, subend);
      if (keep_empty || !temp.empty()) 	result.push_back(temp);
      if (subend == s.end())            break;
      substart = subend + delim.size();
    }
    return result;
}


void PileupReweighter::readPileupMCFile ( std::string * file_name ) { 

  m_mc_file_name = * file_name ;
  
  std::ifstream f (file_name -> c_str());
  std::stringstream buffer;
  buffer << f.rdbuf();

  std::string raw_pdf_string ( buffer.str());
  
  std::vector<std::string> split_pdf_strings = split ( raw_pdf_string , std::string(","));

  m_mc_pileup_pdf.resize( split_pdf_strings.size() );

  for (int i = 0; i < (int) split_pdf_strings.size() ; ++i) {
    double pdf = atof ( split_pdf_strings[i].c_str() );
    m_mc_pileup_pdf[i] = pdf;
  }

}

void PileupReweighter::printPileupWeights() { 
  std::cout << "Calculated Pileup Weights for Monte Carlo:" << std::endl;
  for (int i = 0; i <  m_max_n_pileup; ++i){
    std::cout << "\t Pileup = " << i << "\t Data PDF ( " << std::scientific << m_data_pileup_pdf[i] << " ) / MC PDF ( " << m_mc_pileup_pdf [i] << " ) = Weight ( " << m_pileup_weights [i] << " ) " << std::endl;
  }
}

void PileupReweighter::normalizeVector ( std::vector<double> & v, int max_n_pileup ) {
  
  double integral = 0.0;
  double new_integral = 0.0;
  
  for ( int n_pileup = 0 ; n_pileup < max_n_pileup; ++n_pileup) integral += v [ n_pileup ];
  for ( int n_pileup = 0 ; n_pileup < max_n_pileup; ++n_pileup) v[ n_pileup ] /=  integral;

}

void PileupReweighter::calculatePileupWeights() {
  
  if ( m_mc_pileup_pdf.size() < m_data_pileup_pdf.size() ) 
    m_max_n_pileup = m_mc_pileup_pdf.size();
  else 
    m_max_n_pileup = m_data_pileup_pdf.size();

  normalizeVector ( m_mc_pileup_pdf  , m_max_n_pileup );
  normalizeVector ( m_data_pileup_pdf, m_max_n_pileup ) ;

  m_pileup_weights.resize ( m_max_n_pileup ) ;

  for (int i = 0; i < m_max_n_pileup; i++){
    m_pileup_weights[i] = 0.0;
    if ( m_mc_pileup_pdf[i] != 0.0 ) 
      m_pileup_weights[i] = m_data_pileup_pdf [i] / m_mc_pileup_pdf [i];
  }

  m_weights_calculated = true;

}
