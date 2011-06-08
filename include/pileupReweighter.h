#ifndef PILEUPREWEIGHTER_H
#define PILEUPREWEIGHTER_H

#include <vector>
#include "TH1F.h"

class PileupReweighter { 
  
 public:
  PileupReweighter();
  ~PileupReweighter();

  void                readPileupDataFile  ( std::string * data_file_name );
  void                readPileupMCFile    ( std::string * mc_file_name   );

  void                calculatePileupWeights();
  void                printPileupWeights();
  std::vector<double> getPileupWeights() { return m_pileup_weights; }
  double              getPileupWeight ( int n_pileup ) ;
  bool                pileupWeightsCalculated () { return m_weights_calculated ; } 

 private:
  std::vector<std::string> split(const std::string& s, const std::string& delim, const bool keep_empty);

  std::vector<double> m_data_pileup_pdf;
  std::vector<double> m_mc_pileup_pdf;
  std::vector<double> m_pileup_weights;
  int m_max_n_pileup;
  bool m_weights_calculated ;
};

#endif
