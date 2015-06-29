#include "TTree.h"
#include "TBranchElement.h"
#include <vector>
#include <iostream>


using namespace std;
void SetAddress(TBranch* branch1, TBranch* branch2)
{
  branch1->SetAddress(branch2->GetAddress());
}

void AddTreeBranch(TTree* tree, TBranch* oldBranch)
//void AddTreeBranch(TTree* tree, TBranchElement* oldBranch)
{
  tree->Branch(oldBranch->GetName(),oldBranch->GetClassName(),oldBranch->GetAddress());
  //tree->Branch(oldBranch->GetName(),oldBranch->GetClassName(),oldBranch->GetObject());
}
