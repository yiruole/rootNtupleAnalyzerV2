COMP=g++
FLAGS =
#FLAGS += -DUSE_EXAMPLE
FLAGS += -DSAVE_ALL_HISTOGRAMS 
FLAGS += -std=c++1y
FLAGS += -O2
#FLAGS += -g
ROOTLIBS = `root-config --glibs --cflags` -lMinuit -lTreePlayer
INC= -I.. -I. -I./include
ROOTINC= -I${ROOTSYS}/include
CMSSWLIBS = ${CMSSW_RELEASE_BASE}/external/${SCRAM_ARCH}/lib/
LIBS= -L.  ${ROOTLIBS} -L${CMSSWLIBS} -lboost_iostreams
SRC= ./src
SELECTIONLIB=$(SRC)/rootNtupleClass.o $(SRC)/baseClass.o $(SRC)/analysisClass.o $(SRC)/jsonParser.o $(SRC)/pileupReweighter.o $(SRC)/likelihoodGetter.o $(SRC)/eventListHelper.o $(SRC)/QCDFakeRate.o $(SRC)/TriggerEfficiency2016.o
EXE = main

# ********** TEMPLATE *************
# mainProg: mainProg.o $(SELECTIONLIB)
#	$(COMP) $(INC) $(ROOTINC) $(LIBS) $(ROOTLIBS) -o $@  $(SELECTIONLIB) $@.o
# *********************************

all: ${EXE} makeOptCutFile

main: $(SRC)/main.o $(SELECTIONLIB) 
	$(COMP) $(INC) $(ROOTINC) $(LIBS) $(FLAGS) -o $@  $(SELECTIONLIB) $(SRC)/$@.o

makeOptCutFile: $(SRC)/makeOptCutFile.o $(SELECTIONLIB) 
	$(COMP) $(INC) $(ROOTINC) $(LIBS) $(FLAGS) -o $@  $(SELECTIONLIB) $(SRC)/$@.o

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


