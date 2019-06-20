ROOTSYS=/cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt
ROOTCONFIG=$(ROOTSYS)/bin/root-config
ROOTCINT=$(ROOTSYS)/bin/rootcint
COMP=g++
FLAGS =
#FLAGS += -DUSE_EXAMPLE
FLAGS += -DSAVE_ALL_HISTOGRAMS 
FLAGS += -std=c++1y
FLAGS += -O2
FLAGS += -g
#ROOTLIBS = `$(ROOTCONFIG) --glibs --cflags` -lMinuit -lTreePlayer
ROOTLIBS := $(shell $(ROOTCONFIG) --glibs --cflags)
ROOTINC= -I$(shell $(ROOTCONFIG) --incdir)
INC= -I.. -I. -I./include
#ROOTINC = -I$(ROOTSYS)/include
#CMSSWLIBS = ${CMSSW_RELEASE_BASE}/external/${SCRAM_ARCH}/lib/
#LIBS= -L.  ${ROOTLIBS} -L${CMSSWLIBS} -lboost_iostreams
LIBS= -L.  $(ROOTLIBS) -lboost_iostreams
SRC= ./src
HEADERS=$(wildcard include/*.h)
TMPHEADERS := $(HEADERS)
HEADERS = $(filter-out include/LinkDef.h, $(TMPHEADERS))
SELECTIONLIB=$(SRC)/rootNtupleClass.o $(SRC)/baseClass.o $(SRC)/analysisClass.o $(SRC)/jsonParser.o $(SRC)/eventListHelper.o $(SRC)/QCDFakeRate.o $(SRC)/TriggerEfficiency2016.o
EXE = main

# ********** TEMPLATE *************
# mainProg: mainProg.o $(SELECTIONLIB)
#	$(COMP) $(INC) $(ROOTINC) $(LIBS) $(ROOTLIBS) -o $@  $(SELECTIONLIB) $@.o
# *********************************

all: ${EXE} makeOptCutFile

main: $(SRC)/main.o $(SELECTIONLIB) $(SRC)/MyDict.cxx
	$(COMP) $(INC) $(ROOTINC) -o $@ $(SELECTIONLIB) $(SRC)/$@.o $(SRC)/MyDict.cxx $(LIBS) $(FLAGS) -Wl,-rpath,$(shell $(ROOTCONFIG) --libdir)

makeOptCutFile: $(SRC)/makeOptCutFile.o $(SELECTIONLIB) $(SRC)/MyDict.cxx
	$(COMP) $(INC) $(ROOTINC) -o $@ $(SELECTIONLIB) $(SRC)/$@.o $(SRC)/MyDict.cxx $(LIBS) $(FLAGS) -Wl,-rpath,$(shell $(ROOTCONFIG) --libdir)

$(SRC)/MyDict.cxx: include/rootNtupleClass.h include/LinkDef.h
	$(ROOTCINT) -f $@ -s MyDict $^

clean:
	rm -f src/*.o *.lo core core.*
	rm -f *~
	rm -f *.exe
	rm -f $(EXE)

.cpp.o:
	$(COMP) -c $(INC) $(ROOTINC) $(FLAGS) -o $@ $<

.cc.o:
	$(COMP) -m32 -c $(INC) $(ROOTINC) $(FLAGS) -o $@ $<

.cxx.o:
	$(COMP) -c $(INC) $(ROOTINC) $(FLAGS) -o $@ $<

.C.o:
	$(COMP) -c $(INC) $(ROOTINC) $(FLAGS) -o $@ $<


