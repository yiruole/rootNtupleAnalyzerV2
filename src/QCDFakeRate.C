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
  //// try this with the SCEta
  //if(fabs(eta) <= 1.4442)
  ////if(fabs(eta) < 1.5)
  //  return qcdGraphBarrel->Eval(et);
  //else if(fabs(eta) >= 1.566 && fabs(eta) <= 2.0)
  ////else if(fabs(eta) >= 1.5 && fabs(eta) <= 2.0)
  //  return qcdGraphEndcap1->Eval(et);
  //else if(fabs(eta) > 2.0)
  //  return qcdGraphEndcap2->Eval(et);
  //else
  //{
  //  std::cerr << "Found an electron with eta outside expected range: " << eta << "; return -1 for qcd fake rate" << std::endl;
  //  return -1;
  //}

  float fr1 = 1;
  // Try Muzamil's hardcoding
  if(fabs(eta) < 1.4442 ){ //loop02

    //if(et >= 35 && et < 40) {
    if(et < 40) {
      fr1=0.00471123;
    }
    if(et >= 40 && et < 45) {
      fr1=0.0120292;
    }
    if(et >= 45 && et < 50) {
      fr1=0.00207535;
    }
    if(et >= 50 && et < 60) {
      fr1=0.00458322;
    }
    if(et >= 60 && et < 70) {
      fr1=0.00523049;
    }
    if(et >= 70 && et < 80) {
      fr1=0.00325132;
    }
    if(et >= 80 && et < 90) {
      fr1=0.00753344;
    }
    if(et >= 90 && et < 100) {
      fr1=0.0033647;
    }
    if(et >= 100 && et < 110) {
      fr1=0.00294766;
    }
    if(et >= 110 && et < 130) {
      fr1=0.00412781;
    }
    if(et >= 130 && et < 150) {
      fr1=0.00420222;
    }
    if(et >= 150 && et < 170) {
      fr1=0.003488;
    }
    if(et >= 170 && et < 200) {
      fr1=0.00416076;
    }
    if(et >= 200 && et < 250) {
      fr1=0.00498197;
    }
    if(et >= 250 && et < 300) {
      fr1=0.00594786;
    }
    if(et >= 300 && et < 400) {
      fr1=0.00588025;
    }
    if(et >= 400 && et < 500) {
      fr1=0.00735338;
    }
    if(et >= 500 && et < 600) {
      fr1=0.00597363;
    }
    if(et >= 600 && et < 800) {
      fr1=0.00390865;
    }
    if(et >= 800 && et < 1000) {
      fr1=0.0337838;
    }

  }//loop02

  else if(fabs(eta) >1.566 && fabs(eta) <2.0 ){ //loop03

    //if(et > 30 && et < 50  ) {
    if(et < 50  ) {
      fr1=0.0367958;
    }
    if(et >= 50 && et < 75  ) {
      fr1=0.0332162;
    }
    if(et >= 75 && et < 100  ) {
      fr1=0.0140037;
    }
    if(et >= 100 && et < 125  ) {
      fr1=0.0241511;
    }
    if(et >= 125 && et < 150  ) {
      fr1=0.0257674;
    }
    if(et >= 150 && et < 200  ) {
      fr1=0.0311389;
    }
    if(et >= 200 && et < 250  ) {
      fr1=0.0344264;
    }
    if(et >= 250 && et < 300  ) {
      fr1=0.0410732;
    }
    if(et >= 300 && et < 350  ) {
      fr1=0.0567231;
    }
    if(et >= 350 && et < 500  ) {
      fr1=0.0408509;
    }
    if(et >= 500 && et < 1000  ) {
      fr1=0.0980684;
    }
  }//loop03
  else if(fabs(eta) >  2.0){//loop04
    //if(et > 30 && et < 50  ) {
    if(et < 50  ) {
      fr1=0.0400492;
    }
    if(et >= 50 && et < 75  ) {
      fr1=0.0302726;
    }
    if(et >= 75 && et < 100  ) {
      fr1=0.0140113;
    }
    if(et >= 100 && et < 125  ) {
      fr1=0.0298407;
    }
    if(et >= 125 && et < 150  ) {
      fr1=0.0266637;
    }
    if(et >= 150 && et < 200  ) {
      fr1=0.0308586;
    }
    if(et >= 200 && et < 250  ) {
      fr1=0.0421336;
    }
    if(et >= 250 && et < 300  ) {
      fr1=0.052223;
    }
    if(et >= 300 && et < 350  ) {
      fr1=0.0526189;
    }
    if(et >= 350 && et < 500  ) {
      fr1=0.0645787;
    }
    if(et >= 500 && et < 1000  ) {
      fr1=0.0333333;
    }
  }//loop04

  //if(fr1<0)
  //  std::cerr << "Found an electron with eta or eT outside expected range: eta=" << eta << "; eT=" << et << "; return " << fr1 << " for qcd fake rate" << std::endl;
  return fr1;
}

