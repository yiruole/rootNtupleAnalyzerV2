#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_rskSEleL_eoscms_comb/inputListAllCurrent.txt -o pskEEJJPresel_18jun2019/ -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/FlatNTupleSkims/cutTable_lq_eejjPreselection_skim.txt -q microcentury -d /eos/user/s/scooper/LQ/Nano/pskEEJJPresel_18jun2019 -j 10 -n rootTupleTree/tree
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_rskSingleEleL_eoscms_comb/inputListAllCurrent.txt -o /afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nano/2016/pskEEJJPresel_12jul2019/ -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/FlatNTupleSkims/cutTable_lq_eejjPreselection_skim.txt -q microcentury -d /eos/user/s/scooper/LQ/Nano/pskEEJJPresel_12jul2019 -j 5 -n rootTupleTree/tree
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_rskSingleEleL_30jul2019/inputListAllCurrent.txt -o /afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nano/2016/pskEEJJPresel_31jul2019/ -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/FlatNTupleSkims/cutTable_lq_eejjPreselection_skim.txt -q microcentury -d /eos/user/s/scooper/LQ/Nano/pskEEJJPresel_31jul2019 -j 5 -n rootTupleTree/tree
#
# 2017
#INPUTLIST=config/nanoV6_2017_rskSingleEleL_21apr2020/inputListAllCurrent.txt
INPUTLIST=config/nanoV6_2017_rskSingleEleL_7may2020/inputListAllCurrent.txt
SKIMNAME=pskEEJJ_8may2020
CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/FlatNTupleSkims/cutTable_lq_eejjPreselection_skim.txt
python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $LQDATA/nanoV6/2017/skims/$SKIMNAME -c $CUTFILE -q microcentury -d /eos/user/s/scooper/LQ/NanoV6/2017/skims/$SKIMNAME -j 5 -n rootTupleTree/tree
# 2018
#INPUTLIST=config/nanoV6_2018_rskSingleEleL_4may2020/inputListAllCurrent.txt
#SKIMNAME=pskEEJJ_5may2020
#CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/FlatNTupleSkims/cutTable_lq_eejjPreselection_skim.txt
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $LQDATA/nanoV6/2018/skims/$SKIMNAME -c $CUTFILE -q microcentury -d /eos/user/s/scooper/LQ/NanoV6/2018/skims/$SKIMNAME -j 5 -n rootTupleTree/tree
