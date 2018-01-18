#include "include/QCDFakeRate.h"

#include <iostream>
#include <cassert>

using namespace std;

QCDFakeRate::QCDFakeRate(string qcdFilename)
{
  TFile* qcdTFile = TFile::Open(qcdFilename.c_str());
  //FIXME right now the graph name, etc. are hardcoded, fix
  TH2F* histoB = 0;
  qcdTFile->GetObject("Barrel_Fake_Rate",histoB);
  assert(histoB>0);
  histoBarrel = histoB;

  TH2F* histoE = 0;
  qcdTFile->GetObject("Endcap_Fake_Rate",histoE);
  assert(histoE>0);
  histoEndcap = histoE;
}

QCDFakeRate::~QCDFakeRate()
{
  //qcdTFile->Close();
}

float QCDFakeRate::GetFakeRate(const float& eta, const float& et, bool verbose)
{
  float fr = -1.0;
  float etLookup = et;
  if(et>=35)
  {
    // make sure that we don't ask for an Et that is beyond the max x range of the histogram
    // NB: fix this by filling the overflow with the same bin content as the last bin
    if(et > histoBarrel->GetXaxis()->GetXmax() || et > histoEndcap->GetXaxis()->GetXmax()) {
      etLookup = min(histoBarrel->GetXaxis()->GetXmax(),histoEndcap->GetXaxis()->GetXmax())-1;
      if(verbose) {
        std::cout << "INFO: electron Et was: " << et << " which was beyond the bounds of the histogram: [barrel: " << histoBarrel->GetXaxis()->GetXmax()
          << ", endcap: " << histoEndcap->GetXaxis()->GetXmax() << "]; changed it to " << etLookup << " for fake rate lookup." << std::endl;
      }
    }
    if(fabs(eta) < 1.4442) {
      fr = histoBarrel->GetBinContent(histoBarrel->GetBin(histoBarrel->GetXaxis()->FindBin(etLookup),1)); // 1 y bin
      if(verbose) {
        std::cout << "INFO: Found barrel electron with et=" << etLookup << " and eta=" << eta << "; FR=" << fr << std::endl;
      }
    }
    else {
      fr = histoEndcap->GetBinContent(histoEndcap->GetBin(histoEndcap->GetXaxis()->FindBin(etLookup),histoEndcap->GetYaxis()->FindBin(fabs(eta))));
      if(verbose) {
        std::cout << "INFO: Found endcap electron with et=" << etLookup << " and eta=" << eta << "; FR=" << fr << std::endl;
      }
    }
  }
  else if(et<35 && eta != 0) {
    fr = 1.0;
    if(verbose) {
      std::cout << "INFO: Found electron with LOW et=" << etLookup << " and eta=" << eta << "; FR will be set to 1. FR=" << fr << std::endl;
    }
  }
  else if(et==0 && eta==0) { // uninitialized/unstored electron2 (events with only 1 loose ele)
    fr = 1.0;
    if(verbose) {
      std::cout << "INFO: Found electron with zero et=" << etLookup << " and zero eta=" << eta << "; FR will be set to 1. FR=" << fr << std::endl;
    }
  }

  if(fr<=0) {
    std::cerr << "ERROR: Found an electron with unknown fake rate: eta=" << eta << "; eT=" << et << "; return " << fr << " for qcd fake rate" << std::endl;
    std::cerr << "ERROR: Found endcap eta bin: " << histoEndcap->GetYaxis()->FindBin(fabs(eta)) << "; found endcap et bin: " << histoEndcap->GetXaxis()->FindBin(etLookup) << std::endl;
  }
  assert(fr>0);
  return fr;
}

