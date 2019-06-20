#include <iostream>
#include <string>
#include "include/TTreeReaderTools.h"

TTreeReaderTools::TTreeReaderTools(TTree* tree) :
  m_tree(tree), m_readerIsClean(true), m_entry(-1) {
    m_reader = new TTreeReader(tree);
    m_entries = m_reader->GetEntries(false);
}

void TTreeReaderTools::LoadEntry(Long64_t entry) {
  m_entry = entry;
  gotoEntry(entry);
}

template <typename T> T TTreeReaderTools::ReadValueBranch(const std::string& branchName) {
  checkReaderIsClean();
  std::string type = getTypeName(branchName);
  if(type=="UInt_t") {
    std::map<std::string, TTreeReaderValue<UInt_t> >::iterator itr;
    itr = m_ttreeValueUIntReaders.find(branchName);
    if(itr != m_ttreeValueUIntReaders.end())
      return *(itr->second.Get());
    else {
      if(!m_readerIsClean)
        remakeAllReaders();
      TTreeReaderValue<UInt_t> ttrv = TTreeReaderValue<UInt_t>(*m_reader, branchName.c_str());
      //m_ttreeValueUIntReaders.insert(std::pair<std::string,TTreeReaderValue<UInt_t> >(branchName,ttrv));
      gotoEntry(m_entry,true);
      return *(ttrv.Get());
    }
  }
  else {
    std::cout << "ERROR: ReadValueBranch for type: " << type << " is not implemented." << std::endl;
    exit(1);
  }
  //else if(type=="ULong64_t") {
  //}
  //else if(type=="Float_t") {
  //}
  //else if(type=="Int_t") {
  //}
  //else if(type=="UChar_t") {
  //}
  //else if(type=="Bool_t") {
  //}

}

template <typename T> T TTreeReaderTools::ReadArrayBranch(const std::string& branchName) {
  checkReaderIsClean();
}


void TTreeReaderTools::checkReaderIsClean() {
  if (m_readerIsClean) {
    std::cout << "ERROR: ReadBranch must not be called before calling GotoEntry" << std::endl;
    exit(1);
  }
}

std::string TTreeReaderTools::getTypeName(const std::string& branchName) const {
  TBranch* branch = m_reader->GetTree()->GetBranch(branchName.c_str());
    if(!branch) {
      std::cout << "ERROR: Unknown branch " << branchName << std::endl;
      exit(2);
    } 
    TLeaf* leaf = branch->GetLeaf(branchName.c_str());
    return std::string(leaf->GetTypeName());
}

void TTreeReaderTools::gotoEntry(Long64_t entry, bool forceCall) {
  m_readerIsClean = false;
  if(m_entry != entry || forceCall) {
    if(m_entry == entry-1 && entry!=0)
      m_reader->Next();
    else {
      m_reader->SetEntry(entry);
      m_entry = entry;
    }
  }
}

void TTreeReaderTools::remakeAllReaders() {
  delete m_reader;
  m_reader = new TTreeReader(m_tree);
  m_readerIsClean = true;
  std::vector<std::string> branchNames;
  for(auto itr = m_ttreeValueUIntReaders.begin(); itr != m_ttreeValueUIntReaders.end(); ++itr)
    branchNames.push_back(itr->first);
  m_ttreeValueUIntReaders.clear();
  for(auto itr = branchNames.begin(); itr != branchNames.end(); ++itr)
    m_ttreeValueUIntReaders.insert(
        std::pair<std::string,TTreeReaderValue<UInt_t> >(*itr,TTreeReaderValue<UInt_t>(*m_reader,itr->c_str())));
}

//template Item* find_name<Item>(std::vector<Item*> v, std::string name);
template UInt_t TTreeReaderTools::ReadValueBranch<UInt_t>(const std::string& branchName);
