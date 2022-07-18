cmake_minimum_required(VERSION 3.14.0)

set(MY_PROJECT_VERSION 0.9.0 CACHE STRING "project version number")

project(lqAnalysis VERSION ${MY_PROJECT_VERSION})

if(PROJECT_SOURCE_DIR STREQUAL PROJECT_BINARY_DIR)
  message(
    FATAL_ERROR
      "In-source builds not allowed. Please make a new directory (called a build directory) and run CMake from there."
  )
endif()

### compile_commands.json DB
set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE INTERNAL "")

#add_compile_options(-fno-omit-frame-pointer -fsanitize=address,undefined,leak)
#add_link_options(-fsanitize=address,undefined,leak)
add_compile_options(-DSAVE_ALL_HISTOGRAMS)
add_compile_options(-DUSE_FULL_NTUPLE)
add_compile_options(-O2)
add_compile_options(-std=c++17)
#add_compile_options(-DUSE_EXAMPLE)
#add_compile_options(-g)
#add_compile_options(-pg)
#add_compile_options(${USER_CXXFLAGS})

find_package(Boost REQUIRED iostreams regex)
find_package(ROOT REQUIRED Hist Tree TreePlayer Physics TMVA)
find_package(correctionlib REQUIRED)
find_package(Threads)
find_package(ZLIB)

#add_library(mylib
#  src/mylib.cpp
#  )
#
#set_target_properties(mylib PROPERTIES CXX_STANDARD 17)

# target_compile_options(lsplib
#   PUBLIC "$<$<COMPILE_LANG_AND_ID:CXX,MSVC>:/permissive->")

# Link dependencies
#target_link_libraries(lsplib)

#target_include_directories(mylib
#  PUBLIC
#    $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>
#    $<INSTALL_INTERFACE:include/${PROJECT_NAME}-${PROJECT_VERSION}>
#)
include_directories(${CMAKE_SOURCE_DIR}/include)

add_executable(main
  src/TTreeReaderTools.C
  src/main.C
  src/analysisClass.C
  src/baseClass.C
  src/Collection.C
  src/Electron.C
  src/ElectronIDs.C
  src/GenJet.C
  src/GenJetIDs.C
  src/GenParticle.C
  src/GenParticleIDs.C
  src/HLTriggerObject.C
  src/HLTriggerObjectCollectionHelper.C
  src/LooseElectron.C
  src/HistoReader.C
  src/Muon.C
  src/MuonIDs.C
  src/Object.C
  src/PFJet.C
  src/PFJetIDs.C
  src/QCDFakeRate.C
  src/eventListHelper.C
  src/jsonParser.C
)

target_link_libraries(main
  PUBLIC
  Boost::iostreams
  Boost::regex
  ROOT::Hist
  ROOT::Tree
  ROOT::TreePlayer
  ROOT::Physics
  ROOT::TMVA
  correctionlib
)
