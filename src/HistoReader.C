#include "HistoReader.h"

#include <iostream>

using namespace std;

HistoReader::HistoReader()
{
  isAbsEta=true;
  histoBarrel = 0;
  histoEndcap = 0;
}

HistoReader::HistoReader(std::string filename, std::string barrelHistName, std::string endcapHistName,
    bool absEta, bool etIsXAxis) : isAbsEta(absEta), isEtXAxis(etIsXAxis)
{
  unique_ptr<TFile> myTFile(TFile::Open(filename.c_str()));
  histoBarrel = unique_ptr<TH2F>(myTFile->Get<TH2F>(barrelHistName.c_str()));
  histoBarrel->SetDirectory(0);

  histoEndcap = unique_ptr<TH2F>(myTFile->Get<TH2F>(endcapHistName.c_str()));
  histoEndcap->SetDirectory(0);
}

HistoReader::~HistoReader()
{
}

// make sure that we don't ask for an Et that is beyond the max x range of the histogram
int HistoReader::GetLookupBin(const TH2F& histRef, bool isXaxis, float& rawValue, bool verbose)
{
  int lookupBin = -1;
  bool changedBin = false;
  if(isXaxis) {
    if(rawValue >= histRef.GetXaxis()->GetXmax()) {
      lookupBin = histRef.GetNbinsX(); // last real, non-overflow bin
      changedBin = true;
    }
    else if(rawValue < histRef.GetXaxis()->GetXmin()) {
      lookupBin = 1; // first real bin
      changedBin = true;
    }
    else
      lookupBin = histRef.GetXaxis()->FindBin(rawValue);
  }
  else {
    if(rawValue >= histRef.GetYaxis()->GetXmax()) {
      lookupBin = histRef.GetNbinsY(); // last real, non-overflow bin
      changedBin = true;
    }
    else if(rawValue < histRef.GetYaxis()->GetXmin()) {
      lookupBin = 1; // first real bin
      changedBin = true;
    }
    else
      lookupBin = histRef.GetYaxis()->FindBin(rawValue);
  }

  if(verbose && changedBin) {
    std::cout << "INFO: raw value was: " << rawValue << " which is outside the bounds of the histogram "
      << histRef.GetName() << " [";
    if(isXaxis)
      std::cout << histRef.GetXaxis()->GetXmax() << " - " << histRef.GetXaxis()->GetXmin() << "]; using bin-center value: " << histRef.GetXaxis()->GetBinCenter(lookupBin) << " for lookup." << std::endl;
    else
      std::cout << histRef.GetYaxis()->GetXmax() << " - " << histRef.GetYaxis()->GetXmin() << "]; using bin-center value: " << histRef.GetYaxis()->GetBinCenter(lookupBin) << " for lookup." << std::endl;
  }

  return lookupBin;
}

float HistoReader::DoLookup(const float eta, const float et, bool returnError, bool verbose) {
  float value = -1.0;
  float etLookup = et;
  float etaLookup = isAbsEta ? fabs(eta) : eta;
  bool isBarrel = true;
  int etLookupBin = -1;
  int etaLookupBin = -1;

  if(et<=0 && eta==0) { // uninitialized/unstored electron2 (events with only 1 loose ele)
    value = 0.99;
    if(verbose) {
      std::cout << "INFO: Found electron with et=" << etLookup << " and zero eta=" << eta << "; set value=" << value << std::endl;
    }
  }
  else {
    if(fabs(eta) >= 1.5) { // add extra margin b/c nanoAOD and composite variable rounding; assumes eta cuts are applied upstream
      // protect against eta < 1.566  or eta < 2.5 b/c nanoAOD and composite variable rounding; assumes eta cuts are applied upstream
      isBarrel = false;
      if(etaLookup > 0 && etaLookup < 1.566)
        etaLookup = 1.567;
      else if(etaLookup < 0 && etaLookup > -1.566)
        etaLookup = -1.567;
    }
    // handle cases where the barrel electron eta is outside the bounds of where the triggerSF hist is filled
    // the QCD FR barrel hist currently goes from 0 to 1.4442, and only one eta bin anyway...so OK for now
    else if(fabs(eta) < 1.5) {
      if(etaLookup > 1.444)
        etaLookup = 1.443;
      else if(etaLookup < -1.444)
        etaLookup = -1.443;
    }
    const TH2F& histRef = isBarrel ? *histoBarrel : *histoEndcap;
    //std::cout << "Using histRef with name: " << histRef.GetName() << " as the histRef for GetLookupBin()"
    //  << " for electron with eta=" << eta << "; isBarrel=" << isBarrel << std::endl;
    etLookupBin = GetLookupBin(histRef,isEtXAxis,etLookup,verbose);
    etaLookupBin = GetLookupBin(histRef,!isEtXAxis,etaLookup,verbose);
    if(returnError)
      value = isEtXAxis ? histRef.GetBinError(etLookupBin,etaLookupBin) : histRef.GetBinError(etaLookupBin,etLookupBin);
    else
      value = isEtXAxis ? histRef.GetBinContent(etLookupBin,etaLookupBin) : histRef.GetBinContent(etaLookupBin,etLookupBin);
    if(verbose) {
      std::cout << "INFO: Found " << (isBarrel ? "barrel" : "endcap") << " electron with et=" << et << " and eta=" << eta <<
        (returnError ? "; value=" : "; error=") << value << std::endl;
    }
  }

  if(value<=0) {
    std::cerr << "ERROR: Found an electron with unknown value: eta=" << eta << "; eT=" << et << "; return " << (returnError ? "; value=" : "; error=") <<
      value << std::endl;
    std::cerr << "ERROR: Used etaLookup=" << etaLookup << "; eT=" << etLookup << std::endl;
    std::cerr << "ERROR: Found " << (isBarrel ? "barrel" : "endcap") << " eta bin: " << etaLookupBin << "; found et bin: " << etLookupBin << std::endl;
  }
  assert(value>0);
  return value;
}

