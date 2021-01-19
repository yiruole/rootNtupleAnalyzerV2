# NB: Also needs to be changed in submit scripts for condor
ROOTSYS=/cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.20.04/x86_64-centos7-gcc48-opt
ROOTCONFIG=$(ROOTSYS)/bin/root-config
COMP=g++
FLAGS =
FLAGS += -std=c++1y
#FLAGS += -DUSE_EXAMPLE
#FLAGS += -g
FLAGS += -DSAVE_ALL_HISTOGRAMS
FLAGS += -DUSE_FULL_NTUPLE
FLAGS += -O2
FLAGS += ${USER_CXXFLAGS}
ROOTLIBS := $(shell $(ROOTCONFIG) --glibs --cflags)
ROOTINC= -I$(shell $(ROOTCONFIG) --incdir)
INC= -I.. -I. -I./include  -I${CLHEP}/include ${ROOTINC}
LIBS= -L.  ${ROOTLIBS} -lboost_iostreams -lboost_regex
SRC= ./src
HEADERS=$(wildcard include/*.h)
TMPHEADERS := $(HEADERS)
HEADERS = $(filter-out include/LinkDef.h, $(TMPHEADERS))
SELECTIONLIB=$(SRC)/baseClass.o $(SRC)/analysisClass.o $(SRC)/jsonParser.o $(SRC)/eventListHelper.o $(SRC)/TriggerEfficiency2016.o $(SRC)/HistoReader.o
COLLECTIONLIB=$(SRC)/Collection.o
PHYOBJECTSLIB=$(SRC)/Object.o $(SRC)/GenParticle.o $(SRC)/GenJet.o $(SRC)/Electron.o $(SRC)/LooseElectron.o $(SRC)/Muon.o $(SRC)/PFJet.o $(SRC)/HLTriggerObject.o
IDOBJECTSLIB=$(SRC)/GenParticleIDs.o $(SRC)/GenJetIDs.o $(SRC)/ElectronIDs.o $(SRC)/MuonIDs.o $(SRC)/PFJetIDs.o
TOOLSLIB=$(SRC)/HLTriggerObjectCollectionHelper.o $(SRC)/TTreeReaderTools.o $(SRC)/QCDFakeRate.o
EXE = main

# ********** TEMPLATE *************
# mainProg: mainProg.o $(SELECTIONLIB)
#	$(COMP) $(INC) $(LIBS) $(ROOTLIBS) -o $@  $(SELECTIONLIB) $@.o
# *********************************

all: ${EXE}

main: $(SRC)/main.o $(TOOLSLIB) $(SELECTIONLIB) $(COLLECTIONLIB) $(PHYOBJECTSLIB) $(IDOBJECTSLIB)
	$(COMP) $(INC) -o $@  $(TOOLSLIB) $(SELECTIONLIB) $(COLLECTIONLIB) $(PHYOBJECTSLIB) $(IDOBJECTSLIB) $(SRC)/$@.o $(LIBS) $(FLAGS) -Wl,-rpath,$(shell $(ROOTCONFIG) --libdir)

clean:
	rm -f src/*.o *.lo
	rm -f $(EXE)

.cpp.o:
	$(COMP) -c $(INC) $(FLAGS) -o $@ $<

.cc.o:
	$(COMP) -m32 -c $(INC) $(FLAGS) -o $@ $<

.cxx.o:
	$(COMP) -c $(INC) $(FLAGS) -o $@ $<

.C.o:
	$(COMP) -c $(INC) $(FLAGS) -o $@ $<


