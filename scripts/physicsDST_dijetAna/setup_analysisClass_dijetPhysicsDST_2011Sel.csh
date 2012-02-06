ln -sf $DIJETMACRO/src2011/analysisClass_dijetPhysicsDST_2011Sel.C $DIJETANA/src/analysisClass.C
./scripts/make_rootNtupleClass.sh -f /data/santanas/Ntuples/2011/RootNtuple-V00-02-07-MCFall11-Qstar-Zprime-RSGraviton-ToJJ_JECL123_2011Sel_30012012/reducedNtuples/QstarToJJ_M-500_reduced_skim_1.root -t rootTupleTree/tree
make clean
make
# ./main config/RootNtuple-V00-02-07-MCFall11-Qstar-Zprime-RSGraviton-ToJJ_JECL123_2011Sel_30012012/QstarToJJ_M-500_reduced_skim.txt $DIJETMACRO/config2011/cutTable_dijetPhysicsDST_2011Sel.txt rootTupleTree/tree analysisClass_dijetPhysicsDST_2011Sel analysisClass_dijetPhysicsDST_2011Sel
