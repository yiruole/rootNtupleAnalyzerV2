ln -sf $DIJETMACRO/src2011/analysisClass_dijetPhysicsDST_2011Sel_skim.C $DIJETANA/src/analysisClass.C
./scripts/make_rootNtupleClass.sh -f /data/santanas/Ntuples/2011/BigNtuplesForTests/PhysicsDST__Run2011B-v1__RAW_6_1_J37_NoPTCutPFJets.root -t rootTupleTree/tree
make clean
make
