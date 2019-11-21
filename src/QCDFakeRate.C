#include "include/QCDFakeRate.h"

#include <iostream>
#include <cassert>

using namespace std;

QCDFakeRate::QCDFakeRate(string qcdFilename)
{
  TFile* qcdTFile = TFile::Open(qcdFilename.c_str());
  // x-axis-->SCEt, y-axis-->|SCEta|
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
  if(et==0 && eta==0) { // uninitialized/unstored electron2 (events with only 1 loose ele)
    fr = 0.99;
    if(verbose) {
      std::cout << "INFO: Found electron with zero et=" << etLookup << " and zero eta=" << eta << "; FR will be set to 0.99. FR=" << fr << std::endl;
    }
  }
  else {
    // make sure that we don't ask for an Et that is beyond the max x range of the histogram
    // NB: fix this by filling the overflow with the same bin content as the last bin
    if(et > histoBarrel->GetXaxis()->GetXmax() || et > histoEndcap->GetXaxis()->GetXmax()) {
      etLookup = min(histoBarrel->GetXaxis()->GetXmax(),histoEndcap->GetXaxis()->GetXmax())-1;
    } else if(et < 35) {
      etLookup = 35;
    }
    if(verbose && etLookup != et) {
      std::cout << "INFO: electron Et was: " << et << " which was beyond the bounds of the histogram: [barrel: " << histoBarrel->GetXaxis()->GetXmax()
        << " - " << histoBarrel->GetXaxis()->GetXmin() << ", endcap: " << histoEndcap->GetXaxis()->GetXmax() << " - " << histoEndcap->GetXaxis()->GetXmin()
        << "]; changed it to " << etLookup << " for fake rate lookup." << std::endl;
    }
    if(fabs(eta) < 1.5) { // add extra margin b/c nanoAOD and composite variable rounding; assumes eta cuts are applied upstream
      fr = histoBarrel->GetBinContent(histoBarrel->GetBin(histoBarrel->GetXaxis()->FindBin(etLookup),1)); // 1 y bin (eta)
      if(verbose) {
        std::cout << "INFO: Found barrel electron with et=" << etLookup << " and eta=" << eta << "; FR=" << fr << std::endl;
      }
    }
    else {
      float etaLookup = fabs(eta);
      // protect against eta < 1.566  or eta < 2.5 b/c nanoAOD and composite variable rounding; assumes eta cuts are applied upstream
      if(fabs(etaLookup) >= histoEndcap->GetYaxis()->GetXmax())
        etaLookup = histoEndcap->GetYaxis()->GetXmax()-0.01;
      else if(fabs(etaLookup) < histoEndcap->GetYaxis()->GetXmin())
        etaLookup = histoEndcap->GetYaxis()->GetXmin()+0.01;
      fr = histoEndcap->GetBinContent(histoEndcap->GetBin(histoEndcap->GetXaxis()->FindBin(etLookup),histoEndcap->GetYaxis()->FindBin(etaLookup)));
      if(verbose) {
        std::cout << "INFO: Found endcap electron with et=" << etLookup << " and eta=" << eta << "; FR=" << fr << std::endl;
      }
    }
  }
  if(fr<=0) {
    std::cerr << "ERROR: Found an electron with unknown fake rate: eta=" << eta << "; eT=" << et << "; return " << fr << " for qcd fake rate" << std::endl;
    std::cerr << "ERROR: Found barrel eta bin: " << histoBarrel->GetYaxis()->FindBin(fabs(eta)) << "; found barrel et bin: " << histoBarrel->GetXaxis()->FindBin(etLookup) << std::endl;
    std::cerr << "ERROR: Found endcap eta bin: " << histoEndcap->GetYaxis()->FindBin(fabs(eta)) << "; found endcap et bin: " << histoEndcap->GetXaxis()->FindBin(etLookup) << std::endl;
  }
  assert(fr>0);
  return fr;
}

