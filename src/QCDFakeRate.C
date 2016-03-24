#include "include/QCDFakeRate.h"

#include <iostream>

#include "TCanvas.h"

using namespace std;

QCDFakeRate::QCDFakeRate(string qcdFilename)
{
  TFile* qcdTFile = TFile::Open(qcdFilename.c_str());
  //FIXME right now the graph name, etc. are hardcoded, fix
  TCanvas* c;
  qcdTFile->GetObject("Barrel_TWO_JetFR",c);
  qcdGraphBarrel = ((TGraphErrors*)(c->FindObject("Graph")));

  TCanvas* c1;
  qcdTFile->GetObject("Endcap1_TWO_Jet_FR",c1);
  qcdGraphEndcap1 = ((TGraphErrors*)(c1->FindObject("Graph")));

  TCanvas* c2;
  qcdTFile->GetObject("Endcap2_TWO_Jet_FR",c2);
  qcdGraphEndcap2 = ((TGraphErrors*)(c2->FindObject("Graph")));
}

QCDFakeRate::~QCDFakeRate()
{
  //qcdTFile->Close();
}

float QCDFakeRate::GetFakeRate(const float& eta, const float& et)
{
  //FIXME expanded eta range?? because HEEP ID is based on SCEta?
  // try this with the SCEta
  if(fabs(eta) <= 1.4442)
  //if(fabs(eta) < 1.5)
    return qcdGraphBarrel->Eval(et);
  else if(fabs(eta) >= 1.566 && fabs(eta) <= 2.0)
  //else if(fabs(eta) >= 1.5 && fabs(eta) <= 2.0)
    return qcdGraphEndcap1->Eval(et);
  else if(fabs(eta) > 2.0)
    return qcdGraphEndcap2->Eval(et);
  else
  {
    std::cerr << "Found an electron with eta outside expected range: " << eta << "; return -1 for qcd fake rate" << std::endl;
    return -1;
  }
}

