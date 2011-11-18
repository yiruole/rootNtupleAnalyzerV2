COMP=c++
FLAGS =
#FLAGS += -DUSE_EXAMPLE
FLAGS += -DSAVE_ALL_HISTOGRAMS
#FLAGS += -DCREATE_OPT_CUT_FILE
ROOTLIBS = `root-config --glibs --cflags` -lMinuit
INC= -I.. -I. -I./include  -I${CLHEP}/include
### For JEC with FWLite
#INC= -I.. -I. -I./include  -I${CLHEP}/include -I${CMSSW_RELEASE_BASE}/src -I/afs/cern.ch/cms/${SCRAM_ARCH}/external/boost/1.44.0-cms3/include
ROOTINC= -I${ROOTSYS}/include
LIBS= -L.  ${ROOTLIBS} -L${CLHEP}/lib -L${CLHEP}/lib
### For JEC with FWLite
#LIBS= -L.  ${ROOTLIBS} -L${CLHEP}/lib -L${CLHEP}/lib -L${CMSSW_RELEASE_BASE}/lib/${SCRAM_ARCH} -L${CMSSW_RELEASE_BASE}/external/${SCRAM_ARCH}/lib -L/afs/cern.ch/cms/${SCRAM_ARCH}/external/boost/1.44.0-cms3/lib
SRC= ./src
SELECTIONLIB = $(SRC)/rootNtupleClass.o $(SRC)/baseClass.o $(SRC)/analysisClass.o $(SRC)/jsonParser.o $(SRC)/pileupReweighter.o
### For JEC with FWLite
#SELECTIONLIB = $(SRC)/rootNtupleClass.o $(SRC)/baseClass.o $(SRC)/analysisClass.o $(SRC)/jsonParser.o $(SRC)/pileupReweighter.o ${CMSSW_RELEASE_BASE}/lib/${SCRAM_ARCH}/libFWCoreFWLite.so ${CMSSW_RELEASE_BASE}/lib/${SCRAM_ARCH}/libCondFormatsJetMETObjects.so
EXE = main

# ********** TEMPLATE *************
# mainProg: mainProg.o $(SELECTIONLIB)
#	$(COMP) $(INC) $(ROOTINC) $(LIBS) $(ROOTLIBS) -o $@  $(SELECTIONLIB) $@.o
# *********************************

all: ${EXE}

main: $(SRC)/main.o $(SELECTIONLIB)
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


