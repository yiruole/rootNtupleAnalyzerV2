#include "correction.h"

class CorrectionHandler {
  public:
    static correction::Correction::Ref GetCorrectionFromFile(const std::string& fileName, const std::string& corrName);
    CorrectionHandler(const std::string& fileName) { LoadCorrectionSetFromFile(fileName); }
    correction::Correction::Ref GetCorrection(const std::string& corrName);
    void LoadCorrectionSetFromFile(const std::string& fileName);

  private:
    std::unique_ptr<correction::CorrectionSet> m_correctionSetPtr;
    std::string m_correctionSetFileName;
};
