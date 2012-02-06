## CHANGE THE OUTPUT DIR
#set THISOUTPUTDIR=$DIJETDATA/dijets_PhysicsDST/117pb-1_JECL123Res__Fall11MC_JECL123__31_01_2012
set THISOUTPUTDIR=/data/santanas/Results/dijets_PhysicsDST/117pb-1_JECL123Res__Fall11MC_JECL123__06_02_2012
mkdir -p $THISOUTPUTDIR
################################
# cp $DIJETMACRO/config2011/cutTable_dijetPhysicsDST_2011Sel.txt .
# cp cutTable_dijetPhysicsDST_2011Sel.txt cutTable_dijetPhysicsDST_2011Sel_DATA.txt
# cp cutTable_dijetPhysicsDST_2011Sel.txt cutTable_dijetPhysicsDST_2011Sel_gg.txt 
# edit  cutTable_dijetPhysicsDST_2011Sel_gg.txt 
#        ggFinalState			0	     1			-		-		0       2 -0.5 1.5
# cp cutTable_dijetPhysicsDST_2011Sel.txt cutTable_dijetPhysicsDST_2011Sel_qg.txt 
# edit  cutTable_dijetPhysicsDST_2011Sel_qg.txt
#        qgFinalState			0	     1			-		-		0       2 -0.5 1.5
# cp cutTable_dijetPhysicsDST_2011Sel.txt cutTable_dijetPhysicsDST_2011Sel_qq.txt 
# edit  cutTable_dijetPhysicsDST_2011Sel_qq.txt
#        qqFinalState			0	     1			-		-		0       2 -0.5 1.5
################################
# DATA
foreach i ( 1 2 3 4 5 6 7 8 9 10 )
./main config/RootNtuple-HEAD_Nov19-2011BData-PhysicsDST-179959-180282_dijets_allEvents_JECL123Res_2011Sel_30012012/PhysicsDST__Run2011B-v1__RAW_${i}.txt scripts/physicsDST_dijetAna/cutTable_dijetPhysicsDST_2011Sel_DATA.txt rootTupleTree/tree $THISOUTPUTDIR/finalResults_DATA_${i} $THISOUTPUTDIR/finalResults_DATA_${i} >&! $THISOUTPUTDIR/finalResults_DATA_${i}.log &
end
# gg
foreach i ( 700 1200 2000 )
./main config/RootNtuple-V00-02-07-MCFall11-Qstar-Zprime-RSGraviton-ToJJ_JECL123_2011Sel_30012012/RSGravitonToJJ_M-${i}_reduced_skim.txt scripts/physicsDST_dijetAna/cutTable_dijetPhysicsDST_2011Sel_gg.txt rootTupleTree/tree $THISOUTPUTDIR/finalResults_RSGravitonToJJ_M-${i}_gg $THISOUTPUTDIR/finalResults_RSGravitonToJJ_M-${i}_gg >&! $THISOUTPUTDIR/finalResults_RSGravitonToJJ_M-${i}_gg.log &
end
# qg
foreach i ( 500 700 1200 2000 )
./main config/RootNtuple-V00-02-07-MCFall11-Qstar-Zprime-RSGraviton-ToJJ_JECL123_2011Sel_30012012/QstarToJJ_M-${i}_reduced_skim.txt scripts/physicsDST_dijetAna/cutTable_dijetPhysicsDST_2011Sel_qg.txt rootTupleTree/tree $THISOUTPUTDIR/finalResults_QstarToJJ_M-${i}_qg $THISOUTPUTDIR/finalResults_QstarToJJ_M-${i}_qg >&! $THISOUTPUTDIR/finalResults_QstarToJJ_M-${i}_qg.log &
end
# qq
foreach i ( 700 1200 2000 )
./main config/RootNtuple-V00-02-07-MCFall11-Qstar-Zprime-RSGraviton-ToJJ_JECL123_2011Sel_30012012/RSGravitonToJJ_M-${i}_reduced_skim.txt scripts/physicsDST_dijetAna/cutTable_dijetPhysicsDST_2011Sel_qq.txt rootTupleTree/tree $THISOUTPUTDIR/finalResults_RSGravitonToJJ_M-${i}_qq $THISOUTPUTDIR/finalResults_RSGravitonToJJ_M-${i}_qq >&! $THISOUTPUTDIR/finalResults_RSGravitonToJJ_M-${i}_qq.log & 
end
#################################
#
# python scripts/physicsDST_dijetAna/combine_dat_files.py 
#
#################################
#
# python scripts/physicsDST_dijetAna/getMassList.py -i "/data/santanas/Results/dijets_PhysicsDST/117pb-1_JECL123Res__Fall11MC_JECL123__06_02_2012/finalResults_DATA_*.log" -m PrintPFDiJetMass -o PFDiJetMassList_DATA.txt
# python scripts/physicsDST_dijetAna/getMassList.py -i "/data/santanas/Results/dijets_PhysicsDST/117pb-1_JECL123Res__Fall11MC_JECL123__06_02_2012/finalResults_DATA_*.log" -m PrintPFDiFatJetMass -o PFDiFatJetMassList_DATA.txt
#
#################################
#
# ./getHistoBinContent.csh
#
#################################
