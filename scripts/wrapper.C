#include "TTree.h"
#include "TTreeIndex.h"
#include <vector>
#include <iostream>


using namespace std;
std::vector<Long64_t> GetTreeEntryList(TTree* tree)
{
  tree->BuildIndex("event");
  TTreeIndex *index = (TTreeIndex*)tree->GetTreeIndex();
  std::vector<Long64_t> eventList;
  //for( int i = index->GetN() - 1; i >=0 ; --i )
  for( int i = 0; i < index->GetN() ; ++i )
  {
    ////Long64_t local = tree->GetEntryNumberWithIndex( index->GetIndex()[i] );
    //Long64_t local = tree->LoadTree( index->GetIndex()[i] );
    //cout << "GetEntryNumberWithIndex(" << index->GetIndex()[i] << ") results in event: " << local << endl;
    //eventList.push_back(local);
    //cout << "index->GetIndex()[" << i << "] = " << index->GetIndex()[i] << endl;
    eventList.push_back(index->GetIndex()[i]);
  }

  return eventList;
}
