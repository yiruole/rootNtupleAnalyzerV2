#include "rootNtupleClass.h"
#include "analysisClass.h"
#include <iostream>
#include <fstream>
#include <string>
#include <stdio.h> 
#include <iomanip>

#include <TTree.h>
#include <TChain.h>
#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TH2.h>
#include <TH1F.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TLorentzVector.h>
#include <TVector2.h>
#include <TVector3.h>

using namespace std;

int main(int argc, char* argv[])
{
  const int Nparam=5;   // NUMBER OF PARAMETERS

  if(argc!=Nparam+1)
    {
      cout << "main() : arcg = " << argc << " is different from " << Nparam+1 <<". Exiting." <<endl;
      cout << "Usage  : ./main inputList cutFile treeName outputRootFileWithoutExtension outputEfficiencyFileWithoutExtension" << endl;
      cout << "Example: ./main config/inputListExample.txt config/cutFileExample.txt RootTupleMaker data/output/rootFile data/output/cutEfficiencyFile" << endl;
      cout << "Example: ./main config/inputListExample.txt config/cutFileExample.txt treeCreator/RootTupleMakerPAT data/output/rootFile data/output/cutEfficiencyFile" << endl;
      cout << "Example: ./main config/inputListExample.txt config/cutFileExample.txt rootTupleTree/tree  data/output/rootFile data/output/cutEfficiencyFile" << endl;
      exit (1);
    };

  string * inputList      = new  string(argv[1]);
  string * cutFile        = new  string(argv[2]);
  string * treeName       = new  string(argv[3]);
  string * outputFileName = new  string(argv[4]);
  string * cutEfficFile   = new  string(argv[5]);

  analysisClass analysisClass_(inputList, cutFile, treeName, outputFileName, cutEfficFile);
  analysisClass_.Loop();

}

