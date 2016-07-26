COMP=g++
FLAGS =
#FLAGS += -DUSE_EXAMPLE
FLAGS += -DSAVE_ALL_HISTOGRAMS 
FLAGS += -std=c++11
FLAGS += -DCREATE_OPT_CUT_FILE
FLAGS += -g
ROOTLIBS = `root-config --glibs --cflags` -lMinuit -lTreePlayer
INC= -I.. -I. -I./include
ROOTINC= -I${ROOTSYS}/include
LIBS= -L.  ${ROOTLIBS} -L/usr/lib64 -lboost_iostreams
SRC= ./src
SELECTIONLIB=$(SRC)/rootNtupleClass.o $(SRC)/baseClass.o $(SRC)/analysisClass.o $(SRC)/jsonParser.o $(SRC)/pileupReweighter.o $(SRC)/likelihoodGetter.o $(SRC)/eventListHelper.o $(SRC)/QCDFakeRate.o
EXE = main

# ********** TEMPLATE *************
# mainProg: mainProg.o $(SELECTIONLIB)
#	$(COMP) $(INC) $(ROOTINC) $(LIBS) $(ROOTLIBS) -o $@  $(SELECTIONLIB) $@.o
# *********************************

all: ${EXE}

main: $(SRC)/main.o $(SELECTIONLIB) 
	$(COMP) $(INC) $(ROOTINC) $(LIBS) $(FLAGS) -o $@  $(SELECTIONLIB) $(SRC)/$@.o

main2: $(SRC)/main2.o $(SELECTIONLIB) 
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


