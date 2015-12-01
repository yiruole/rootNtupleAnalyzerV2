COMP=g++
FLAGS =
#FLAGS += -DUSE_EXAMPLE
FLAGS += -DSAVE_ALL_HISTOGRAMS 
FLAGS += -std=c++11
# FLAGS += -DCREATE_OPT_CUT_FILE
ROOTLIBS = `root-config --glibs --cflags` -lMinuit 
INC= -I.. -I. -I./include  -I${CLHEP}/include
ROOTINC= -I${ROOTSYS}/include
LIBS= -L.  ${ROOTLIBS} -L${CLHEP}/lib -L${CLHEP}/lib
SRC= ./src
FULLNTUPLELIB=$(SRC)/rootNtupleClass.o
SKIMMEDNTUPLELIB=$(SRC)/rootSkimmedNtupleClass.o
ANALYSISCLASSES=$(shell find $(LQSRC) -name '*.C')
ANALYSISOBJS=$(patsubst %.C,%.o,$(ANALYSISCLASSES))
#ANALYSISOBJS := $(ANALYSISCLASSES:$(LQSRC)/%.C=$(LQSRC)/%.o)
ANALYSISPROGS=$(patsubst %.C,%,$(ANALYSISCLASSES))
ANALYSISCLASS=$(SRC)/analysisClass.o 
SKIMCLASS=$(SRC)/analysisClass_skim.o 
SELECTIONLIB=$(SRC)/baseClass.o $(SRC)/jsonParser.o $(SRC)/pileupReweighter.o $(SRC)/qcdFitter.o $(SRC)/qcdFitter_V1.o  $(SRC)/likelihoodGetter.o $(SRC)/eventListHelper.o
COLLECTIONLIB=$(SRC)/Collection.o
PHYOBJECTSLIB=$(SRC)/Object.o $(SRC)/GenParticle.o $(SRC)/GenJet.o $(SRC)/Electron.o $(SRC)/Muon.o $(SRC)/HighPtMuon.o $(SRC)/PFJet.o $(SRC)/HLTriggerObject.o
IDOBJECTSLIB=$(SRC)/GenParticleIDs.o $(SRC)/GenJetIDs.o $(SRC)/ElectronIDs.o $(SRC)/MuonIDs.o $(SRC)/HighPtMuonIDs.o $(SRC)/PFJetIDs.o
TOOLSLIB=$(SRC)/HLTriggerObjectCollectionHelper.o 
EXE = main main_skim

# ********** TEMPLATE *************
# mainProg: mainProg.o $(SELECTIONLIB)
#	$(COMP) $(INC) $(ROOTINC) $(LIBS) $(ROOTLIBS) -o $@  $(SELECTIONLIB) $@.o
# *********************************

#all: ${EXE}
all: $(ANALYSISPROGS)

#main: $(SRC)/main.o $(SELECTIONLIB) $(SKIMMEDNTUPLELIB) $(ANALYSISCLASS)
#	$(COMP) $(INC) $(ROOTINC) $(LIBS) $(FLAGS) -o $@  $(SELECTIONLIB) $(SKIMMEDNTUPLELIB) $(SRC)/$@.o

main_skim: $(SRC)/main.o $(SELECTIONLIB) $(FULLNTUPLELIB) $(SKIMCLASS) $(COLLECTIONLIB) $(PHYOBJECTSLIB) $(IDOBJECTSLIB) $(TOOLSLIB)
	$(COMP) $(INC) $(ROOTINC) $(LIBS) $(FLAGS) -o $@  $(SELECTIONLIB) $(FULLNTUPLELIB) $(SKIMCLASS) $(COLLECTIONLIB) $(PHYOBJECTSLIB) $(IDOBJECTSLIB) $(TOOLSLIB) $(SRC)/main.o

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

%.o: %.C
	$(COMP) -c $(INC) $(ROOTINC) $(FLAGS) -o $@ $<

$(ANALYSISPROGS): $(SRC)/main.o $(SELECTIONLIB) $(FULLNTUPLELIB) $(SKIMCLASS) $(COLLECTIONLIB) $(PHYOBJECTSLIB) $(IDOBJECTSLIB) $(TOOLSLIB) $(ANALYSISOBJS)
	$(COMP) $(INC) $(ROOTINC) $(LIBS) $(FLAGS) -o $@  $(SELECTIONLIB) $(FULLNTUPLELIB) $(SKIMCLASS) $(COLLECTIONLIB) $(PHYOBJECTSLIB) $(IDOBJECTSLIB) $(TOOLSLIB) $(SRC)/main.o

$(ANALYSISOBJS): $(LQSRC)/%.o : $(LQSRC)/%.C
	$(COMP) -c $(INC) $(ROOTINC) $(FLAGS) -o $@ $<
	@echo "Compiled "$<""

#$(LQSRC)/%.o: $(LQSRC)/%.C
#	$(COMP) -c $(INC) $(ROOTINC) $(FLAGS) -o $@ $<
#	@echo "Compiled "$<" using rule1"

