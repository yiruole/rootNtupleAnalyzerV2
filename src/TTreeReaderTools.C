#include <iostream>
#include <string>
#include "include/TTreeReaderTools.h"

TTreeReaderTools::TTreeReaderTools(TTree* tree) :
  m_tree(tree), m_readerIsClean(true), m_entry(-1) {
    m_reader = std::unique_ptr<TTreeReader>(new TTreeReader(tree));
    m_entries = m_reader->GetEntries(false);
}

void TTreeReaderTools::LoadEntry(Long64_t entry) {
  gotoEntry(entry);
}

void TTreeReaderTools::gotoEntry(Long64_t entry, bool forceCall) {
  m_readerIsClean = false;
  if(m_entry != entry || forceCall) {
    if(m_entry == entry-1 && entry!=0)
      m_reader->Next();
    else {
      m_reader->SetEntry(entry);
    }
    m_entry = entry;
  }
}

template <typename T> T TTreeReaderTools::ReadValueBranch(const std::string& branchName) {
  checkReaderIsClean();
  std::string type = getTypeName(branchName);
  if(type=="UInt_t") {
    auto itr = m_ttreeValueUIntReaders.find(branchName);
    if(itr != m_ttreeValueUIntReaders.end())
      return *(itr->second.Get());
    else {
      if(!m_readerIsClean)
        remakeAllReaders();
      TTreeReaderValue<UInt_t> ttrv = TTreeReaderValue<UInt_t>(*m_reader, branchName.c_str());
      m_ttreeValueUIntReaders.insert(std::pair<std::string,TTreeReaderValue<UInt_t> >(branchName,ttrv));
      gotoEntry(m_entry,true);
      return *(ttrv.Get());
    }
  }
  else if(type=="ULong64_t") {
    auto itr = m_ttreeValueULong64Readers.find(branchName);
    if(itr != m_ttreeValueULong64Readers.end())
      return *(itr->second.Get());
    else {
      if(!m_readerIsClean)
        remakeAllReaders();
      TTreeReaderValue<ULong64_t> ttrv = TTreeReaderValue<ULong64_t>(*m_reader, branchName.c_str());
      m_ttreeValueULong64Readers.insert(std::pair<std::string,TTreeReaderValue<ULong64_t> >(branchName,ttrv));
      gotoEntry(m_entry,true);
      return *(ttrv.Get());
    }
  }
  else if(type=="Float_t") {
    auto itr = m_ttreeValueFloatReaders.find(branchName);
    if(itr != m_ttreeValueFloatReaders.end())
      return *(itr->second.Get());
    else {
      if(!m_readerIsClean)
        remakeAllReaders();
      TTreeReaderValue<Float_t> ttrv = TTreeReaderValue<Float_t>(*m_reader, branchName.c_str());
      m_ttreeValueFloatReaders.insert(std::pair<std::string,TTreeReaderValue<Float_t> >(branchName,ttrv));
      gotoEntry(m_entry,true);
      return *(ttrv.Get());
    }
  }
  else if(type=="Int_t") {
    auto itr = m_ttreeValueIntReaders.find(branchName);
    if(itr != m_ttreeValueIntReaders.end())
      return *(itr->second.Get());
    else {
      if(!m_readerIsClean)
        remakeAllReaders();
      TTreeReaderValue<Int_t> ttrv = TTreeReaderValue<Int_t>(*m_reader, branchName.c_str());
      m_ttreeValueIntReaders.insert(std::pair<std::string,TTreeReaderValue<Int_t> >(branchName,ttrv));
      gotoEntry(m_entry,true);
      return *(ttrv.Get());
    }
  }
  else if(type=="UChar_t") {
    auto itr = m_ttreeValueUCharReaders.find(branchName);
    if(itr != m_ttreeValueUCharReaders.end())
      return *(itr->second.Get());
    else {
      if(!m_readerIsClean)
        remakeAllReaders();
      TTreeReaderValue<UChar_t> ttrv = TTreeReaderValue<UChar_t>(*m_reader, branchName.c_str());
      m_ttreeValueUCharReaders.insert(std::pair<std::string,TTreeReaderValue<UChar_t> >(branchName,ttrv));
      gotoEntry(m_entry,true);
      return *(ttrv.Get());
    }
  }
  else if(type=="Bool_t") {
    auto itr = m_ttreeValueBoolReaders.find(branchName);
    if(itr != m_ttreeValueBoolReaders.end())
      return *(itr->second.Get());
    else {
      if(!m_readerIsClean)
        remakeAllReaders();
      TTreeReaderValue<Bool_t> ttrv = TTreeReaderValue<Bool_t>(*m_reader, branchName.c_str());
      m_ttreeValueBoolReaders.insert(std::pair<std::string,TTreeReaderValue<Bool_t> >(branchName,ttrv));
      gotoEntry(m_entry,true);
      return *(ttrv.Get());
    }
  }
  else {
    std::cout << "ERROR: ReadValueBranch for type: " << type << " is not implemented." << std::endl;
    exit(1);
  }

}

template <typename T> TTreeReaderArray<T>& TTreeReaderTools::ReadArrayBranch(const std::string& branchName, std::map<std::string, TTreeReaderArray<T> >& arrayReaderMap) {
  checkReaderIsClean();
  auto itr = arrayReaderMap.find(branchName);
  if(itr != arrayReaderMap.end())
    return itr->second;
  else {
    if(!m_readerIsClean)
      remakeAllReaders();
    auto insertItr = arrayReaderMap.insert(std::pair<std::string,TTreeReaderArray<T> >(branchName,TTreeReaderArray<T>(*m_reader, branchName.c_str())));
    gotoEntry(m_entry,true);
    return insertItr.first->second;
  }
}

template <> TTreeReaderArray<Float_t>& TTreeReaderTools::ReadArrayBranch(const std::string& branchName) {
  return ReadArrayBranch<Float_t>(branchName, m_ttreeArrayFloatReaders);
}
template <> TTreeReaderArray<Int_t>& TTreeReaderTools::ReadArrayBranch(const std::string& branchName) {
  return ReadArrayBranch<Int_t>(branchName, m_ttreeArrayIntReaders);
}
template <> TTreeReaderArray<UChar_t>& TTreeReaderTools::ReadArrayBranch(const std::string& branchName) {
  return ReadArrayBranch<UChar_t>(branchName, m_ttreeArrayUCharReaders);
}

void TTreeReaderTools::checkReaderIsClean() {
  if (m_readerIsClean) {
    std::cout << "ERROR: ReadValueBranch/ReadArrayBranch must not be called before calling GotoEntry" << std::endl;
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

template <typename T> void TTreeReaderTools::remakeReader(T& readerMap) {
  using DataType = typename T::mapped_type;
  std::vector<std::string> branchNames;
  for(auto itr = readerMap.begin(); itr != readerMap.end(); ++itr)
    branchNames.push_back(itr->first);
  readerMap.clear();
  for(auto itr = branchNames.begin(); itr != branchNames.end(); ++itr)
    readerMap.insert(
        std::pair<std::string,DataType>(*itr,DataType(*m_reader,itr->c_str())));
}

void TTreeReaderTools::remakeAllReaders() {
  m_reader.reset(new TTreeReader(m_tree));
  m_readerIsClean = true;
  remakeReader<std::map<std::string, TTreeReaderValue<UInt_t> > >(m_ttreeValueUIntReaders);
  remakeReader<std::map<std::string, TTreeReaderValue<ULong64_t> > >(m_ttreeValueULong64Readers);
  remakeReader<std::map<std::string, TTreeReaderValue<Float_t> > >(m_ttreeValueFloatReaders);
  remakeReader<std::map<std::string, TTreeReaderValue<Int_t> > >(m_ttreeValueIntReaders);
  remakeReader<std::map<std::string, TTreeReaderValue<UChar_t> > >(m_ttreeValueUCharReaders);
  remakeReader<std::map<std::string, TTreeReaderValue<Bool_t> > >(m_ttreeValueBoolReaders);
  // array readers
  remakeReader<std::map<std::string, TTreeReaderArray<Float_t> > >(m_ttreeArrayFloatReaders);
  remakeReader<std::map<std::string, TTreeReaderArray<Int_t> > >(m_ttreeArrayIntReaders);
  remakeReader<std::map<std::string, TTreeReaderArray<UChar_t> > >(m_ttreeArrayUCharReaders);
  remakeReader<std::map<std::string, TTreeReaderArray<Bool_t> > >(m_ttreeArrayBoolReaders);
}

template UInt_t TTreeReaderTools::ReadValueBranch<UInt_t>(const std::string& branchName);
template ULong64_t TTreeReaderTools::ReadValueBranch<ULong64_t>(const std::string& branchName);
template Float_t TTreeReaderTools::ReadValueBranch<Float_t>(const std::string& branchName);
template Int_t TTreeReaderTools::ReadValueBranch<Int_t>(const std::string& branchName);
template UChar_t TTreeReaderTools::ReadValueBranch<UChar_t>(const std::string& branchName);
template Bool_t TTreeReaderTools::ReadValueBranch<Bool_t>(const std::string& branchName);
//
template TTreeReaderArray<Float_t>& TTreeReaderTools::ReadArrayBranch<Float_t>(const std::string& branchName);
template TTreeReaderArray<Int_t>& TTreeReaderTools::ReadArrayBranch<Int_t>(const std::string& branchName);
template TTreeReaderArray<UChar_t>& TTreeReaderTools::ReadArrayBranch<UChar_t>(const std::string& branchName);
template TTreeReaderArray<Bool_t>& TTreeReaderTools::ReadArrayBranch<Bool_t>(const std::string& branchName);
