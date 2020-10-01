#
# 2016
#
INPUTLIST=config/nanoV7_2016_pskEEJJ_24aug2020_comb/inputListAllCurrent.txt
ANANAME=24aug2020
CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/Analysis/cutTable_lq_eejj.txt
python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $LQDATA/nanoV6/2016/analysis/$ANANAME/condor -c $CUTFILE -q longlunch -d /eos/user/s/scooper/LQ/NanoV6/2016/analysis/$ANANAME -j 1 -n rootTupleTree/tree
#
# 2017
#
##INPUTLIST=config/nanoV6_2017_rskSingleEleL_7may2020_comb/inputListAllCurrent.txt
##INPUTLIST=config/nanoV6_2017_pskEEJJ_8may2020/inputListAllCurrent.txt
#INPUTLIST=config/nanoV6_2017_pskEEJJ_25and8may2020_comb/inputList_DYJetsToLL_Pt-50To100.txt
#ANANAME=noPrefire_22may2020
##CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2017/Analysis/cutTable_lq_eejj_noJets_pt35.txt
#CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2017/Analysis/cutTable_lq_eejj.txt
##python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $LQDATA/nanoV6/2017/analysis/$ANANAME/condor -c $CUTFILE -q tomorrow -d /eos/user/s/scooper/LQ/NanoV6/2017/analysis/$ANANAME -j 1 -n rootTupleTree/tree
##CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2017/Analysis/cutTable_lq_eejj_noJets.txt
##python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $LQDATA/nanoV6/2017/analysis/$ANANAME/condor -c $CUTFILE -q microcentury -d /eos/user/s/scooper/LQ/NanoV6/2017/analysis/$ANANAME -j 1 -n rootTupleTree/tree
##python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $LQDATA/nanoV6/2017/analysis/$ANANAME/condor -c $CUTFILE -q tomorrow -d /eos/user/s/scooper/LQ/NanoV6/2017/analysis/$ANANAME -j 1 -n rootTupleTree/tree
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $LQDATA/nanoV6/2017/analysis/$ANANAME/condor -c $CUTFILE -q longlunch -d /eos/user/s/scooper/LQ/NanoV6/2017/analysis/$ANANAME -j 1 -n rootTupleTree/tree
#
# 2018
#
##INPUTLIST=config/nanoV6_2018_pskEEJJ_5may2020_comb/inputListAllCurrent.txt
#CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2018/Analysis/cutTable_lq_eejj.txt
##python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $LQDATA/nanoV6/2018/analysis/$ANANAME/condor -c $CUTFILE -q longlunch -d /eos/user/s/scooper/LQ/NanoV6/2018/analysis/$ANANAME -j 1 -n rootTupleTree/tree
##python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $LQDATA/nanoV6/2018/analysis/$ANANAME/condor -c $CUTFILE -q tomorrow -d /eos/user/s/scooper/LQ/NanoV6/2018/analysis/$ANANAME -j 1 -n rootTupleTree/tree
##INPUTLIST=config/nanoV6_2018_rskSingleEleL_4may2020_comb/inputListAllCurrent.txt
#INPUTLIST=config/nanoV6_2018_pskEEJJ_25and5may2020_comb/inputList_jetPtBinnedDY.txt
#ANANAME=eejj_5may2020
##CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2018/Analysis/cutTable_lq_eejj_noJets.txt
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $LQDATA/nanoV6/2018/analysis/$ANANAME/condor -c $CUTFILE -q longlunch -d /eos/user/s/scooper/LQ/NanoV6/2018/analysis/$ANANAME -j 1 -n rootTupleTree/tree
#
# QCD FR
#
#ANANAME=may13_heepFix
#INPUTLIST=config/nanoV6_2018_rskQCD_8may_2020/inputListAllCurrent.txt
#CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2018/QCDFakeRate/cutTable_lq_QCD_FakeRateCalculation.txt
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $LQDATA/nanoV6/2018/qcdFakeRateCalc/$ANANAME/condor -c $CUTFILE -q longlunch -d /eos/user/s/scooper/LQ/NanoV6/2018/qcdFakeRateCalc/$ANANAME -j 1 -n rootTupleTree/tree
