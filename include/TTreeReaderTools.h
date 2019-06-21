#include <map>
#include <vector>
#include <memory>
#include <typeindex>
#include <typeinfo>
#include "TTreeReaderValue.h"
#include "TTreeReaderArray.h"
#include "TTreeReader.h"

class TTreeReaderTools {
  public:
    TTreeReaderTools() = delete;
    TTreeReaderTools(TTree* tree);
    template <typename T> T ReadValueBranch(const std::string& branchName);
    template <typename T> TTreeReaderArray<T>& ReadArrayBranch(const std::string& branchName);
    void LoadEntry(Long64_t entry);

  private:
    void checkReaderIsClean();
    void remakeAllReaders();
    std::string getTypeName(const std::string& branchName) const;
    void gotoEntry(Long64_t entry, bool forceCall = false);
    template <typename T> void remakeReader(T& readerMap);
    template <typename T> T ReadValueBranch(const std::string& branchName, std::map<std::string, TTreeReaderValue<T> >& valueReaderMap);
    template <typename T> TTreeReaderArray<T>& ReadArrayBranch(const std::string& branchName, std::map<std::string, TTreeReaderArray<T> >& arrayReaderMap);

    std::map<std::string, TTreeReaderValue<UInt_t>    > m_ttreeValueUIntReaders;
    std::map<std::string, TTreeReaderValue<ULong64_t> > m_ttreeValueULong64Readers;
    std::map<std::string, TTreeReaderValue<Float_t>   > m_ttreeValueFloatReaders;
    std::map<std::string, TTreeReaderValue<Int_t>     > m_ttreeValueIntReaders;
    std::map<std::string, TTreeReaderValue<UChar_t>   > m_ttreeValueUCharReaders;
    std::map<std::string, TTreeReaderValue<Bool_t>    > m_ttreeValueBoolReaders;

    std::map<std::string, TTreeReaderArray<Float_t> > m_ttreeArrayFloatReaders;
    std::map<std::string, TTreeReaderArray<Int_t>   > m_ttreeArrayIntReaders;
    std::map<std::string, TTreeReaderArray<UChar_t> > m_ttreeArrayUCharReaders;
    std::map<std::string, TTreeReaderArray<Bool_t>  > m_ttreeArrayBoolReaders;
    //std::map<std::type_index, std::map<std::string, TTreeReaderArray<std::type_index> > > m_arrayReadersMap;

    bool m_readerIsClean;
    std::unique_ptr<TTreeReader> m_reader;
    TTree* m_tree;
    Long64_t m_entry;
    Long64_t m_entries;
};

