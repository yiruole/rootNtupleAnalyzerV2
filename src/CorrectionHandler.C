#include "CorrectionHandler.h"
#include <iostream>


correction::Correction::Ref CorrectionHandler::GetCorrectionFromFile(const std::string& fileName, const std::string& corrName) {
  std::unique_ptr<correction::CorrectionSet> correctionSetPtr;
  try {
    correctionSetPtr = correction::CorrectionSet::from_file(fileName);
  } catch (std::exception& e) {
    std::cout << "ERROR: Caught exception while loading CorrectionSet from file '" << fileName << "': " << e.what() << ". Exiting." << std::endl;
    exit(-9);
  }
  // now load correction
  correction::Correction::Ref corr;
  try {
    corr = correctionSetPtr->at(corrName);
  } catch(std::out_of_range const & e) {
    std::cout << "ERROR: Caught out_of_range while obtaining Correction '" << corrName << "', from JSON file '" << fileName << "': " << e.what() << ". Exiting." << std::endl;
    exit(-9);
  } catch (std::exception& e) {
    std::cout << "ERROR: Caught exception while obtaining Correction '" << corrName << "', from JSON file '" << fileName << "': " << e.what() << ". Exiting." << std::endl;
    exit(-9);
  }
  return corr;
}

correction::Correction::Ref CorrectionHandler::GetCorrection(const std::string& corrName) {
  correction::Correction::Ref corr;
  try {
    corr = m_correctionSetPtr->at(corrName);
  } catch(std::out_of_range const & e) {
    std::cout << "ERROR: Caught out_of_range while obtaining Correction '" << corrName << "', from JSON file '" << m_correctionSetFileName << "': " << e.what() << ". Exiting." << std::endl;
    exit(-9);
  } catch (std::exception& e) {
    std::cout << "ERROR: Caught exception while obtaining Correction '" << corrName << "', from JSON file '" << m_correctionSetFileName << "': " << e.what() << ". Exiting." << std::endl;
    exit(-9);
  }
  return corr;
}

void CorrectionHandler::LoadCorrectionSetFromFile(const std::string& fileName) {
  try {
    m_correctionSetPtr = correction::CorrectionSet::from_file(fileName);
  } catch (std::exception& e) {
    std::cout << "ERROR: Caught exception while loading CorrectionSet from file '" << fileName << "': " << e.what() << ". Exiting." << std::endl;
    exit(-9);
  }
  m_correctionSetFileName = fileName;
}
