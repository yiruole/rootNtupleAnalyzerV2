#include "include/TriggerEfficiency2016.h"

#include <iostream>
#include <cassert>

using namespace std;

TriggerEfficiency::TriggerEfficiency(string rootFilename, string graphName)
{
  TFile* tFile = TFile::Open(rootFilename.c_str());
  TH2F* histo;
  tFile->GetObject(graphName.c_str(),histo);
  histo_ = histo;
}

TriggerEfficiency::~TriggerEfficiency()
{
  //tFile->Close();
}

float TriggerEfficiency::GetEfficiency(const float& eta, const float& et, bool verbose)
{
  float eff = -1.0;
  float etLookup = et;
  // make sure that we don't ask for an Et that is beyond the max y range of the histogram
  // NB: fix this by filling the overflow with the same bin content as the last bin
  if(et > histo_->GetYaxis()->GetXmax())
    etLookup = histo_->GetYaxis()->GetBinCenter((histo_->GetYaxis()->GetNbins()));
  // trigger effs are valid over 35 GeV PtHeep, however some electrons have PtHeep slightly below for TTBar, for example
  // this is due to cuts on Pt being applied using "pt" and not "ptheep"
  // these should in any case fail the PtHeep cut requirement eventually
  else if(et < 35)
    etLookup = 35.0;
  // same for eta
  float etaLookup = fabs(eta);
  if(fabs(etaLookup-1.566)<0.001) etaLookup = 1.567;
  if(fabs(etaLookup-2.5)<0.001) etaLookup = 2.49;
  if(etaLookup > histo_->GetXaxis()->GetXmax())
    etaLookup = histo_->GetBinCenter(histo_->GetXaxis()->GetNbins());

  eff = histo_->GetBinContent( histo_->GetBin( histo_->GetXaxis()->FindBin(etaLookup),histo_->GetYaxis()->FindBin(etLookup) ,1) ); // 1 z bin

  if(verbose || eff<=0)
  {
    std::cout << "Found an electron: eta=" << eta << "; eT=" << et << "; etaLookup=" << etaLookup << "; xbin=" << histo_->GetXaxis()->FindBin(etaLookup)
      << "; etLookup=" << etLookup << "; ybin=" << histo_->GetYaxis()->FindBin(etLookup) << "; found " 
      << eff << " for efficiency." << std::endl;
  }

  if(eff<=0)
    std::cerr << "ERROR: Found an electron and could not lookup trigger efficiency: eta=" << eta << "; eT=" << et << "; return " << eff << " for efficiency." << std::endl;
  assert(eff>0);
  return eff;
}

bool TriggerEfficiency::PassTrigger(const float& eta, const float& et, bool verbose)
{
  // first, obtain efficiency
  float trigEff = GetEfficiency(eta, et, verbose);

  // then toss a random bumber and compare
  // if the efficiency is greater than the random number, we pass the trigger
  return trigEff > randNrGen.Uniform(0,1);
}
