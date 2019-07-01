ROOTSYS=/cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt
ROOTCONFIG=$(ROOTSYS)/bin/root-config
ROOTCINT=$(ROOTSYS)/bin/rootcint
COMP=g++
FLAGS =
#FLAGS += -DUSE_EXAMPLE
#FLAGS += -g
FLAGS += -DSAVE_ALL_HISTOGRAMS 
FLAGS += -std=c++1y
FLAGS += -O2
ROOTLIBS := $(shell $(ROOTCONFIG) --glibs --cflags)
ROOTINC= -I$(shell $(ROOTCONFIG) --incdir)
INC= -I.. -I. -I./include ${ROOTINC}
LIBS= -L.  $(ROOTLIBS) -lboost_iostreams
SRC= ./src
HEADERS=$(wildcard include/*.h)
TMPHEADERS := $(HEADERS)
HEADERS = $(filter-out include/LinkDef.h, $(TMPHEADERS))
SELECTIONLIB=$(SRC)/baseClass.o $(SRC)/analysisClass.o $(SRC)/jsonParser.o $(SRC)/eventListHelper.o $(SRC)/QCDFakeRate.o $(SRC)/TriggerEfficiency2016.o
TOOLSLIB=$(SRC)/TTreeReaderTools.o
EXE = main

# ********** TEMPLATE *************
# mainProg: mainProg.o $(SELECTIONLIB)
#	$(COMP) $(INC) $(LIBS) $(ROOTLIBS) -o $@  $(SELECTIONLIB) $@.o
# *********************************

all: ${EXE} makeOptCutFile

main: $(SRC)/main.o $(SELECTIONLIB) $(TOOLSLIB) 
	$(COMP) $(INC) -o $@ $(SELECTIONLIB) $(TOOLSLIB) $(SRC)/$@.o $(LIBS) $(FLAGS) -Wl,-rpath,$(shell $(ROOTCONFIG) --libdir)

makeOptCutFile: $(SRC)/makeOptCutFile.o $(SELECTIONLIB) $(TOOLSLIB) 
	$(COMP) $(INC) -o $@ $(SELECTIONLIB) $(TOOLSLIB) $(SRC)/$@.o $(LIBS) $(FLAGS) -Wl,-rpath,$(shell $(ROOTCONFIG) --libdir)

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


