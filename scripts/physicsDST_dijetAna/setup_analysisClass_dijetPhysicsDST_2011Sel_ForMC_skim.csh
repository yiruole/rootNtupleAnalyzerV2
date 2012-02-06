ln -sf $DIJETMACRO/src2011/analysisClass_dijetPhysicsDST_2011Sel_ForMC_skim.C $DIJETANA/src/analysisClass.C
./scripts/make_rootNtupleClass.sh -f /data/santanas/Ntuples/2011/BigNtuplesForTests/RootNtuple-V00-02-07-MCFall11-Qstar-Zprime-RSGraviton-ToJJ-17122011/QstarToJJ_M-500_TuneD6T_7TeV_pythia6__Fall11-PU_S6_START42_V14B-v1__GEN-RAW_1_1_bbb.root -t rootTupleTree/tree
make clean
make
