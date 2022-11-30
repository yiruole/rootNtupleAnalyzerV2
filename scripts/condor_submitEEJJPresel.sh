
#!/bin/bash

YEAR=$1

if [ "$YEAR" = "2016preVFP" ]; then
  echo "Doing 2016preVFP!"
  SKIMNAME=pskEEJJ_19oct2022
  INPUTLIST=config/inputListsRSK_UL16preVFP_SEleL_12oct2022/inputListAllCurrent.txt
  CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/FlatNTupleSkims/cutTable_lq_eejj_preselection_skim.txt
elif [ "$YEAR" = "2016postVFP" ]; then
  echo "Doing 2016postVFP!"
  SKIMNAME=pskEEJJ_19oct2022
  INPUTLIST=config/inputListsRSK_UL16postVFP_SEleL_12oct2022/inputListAllCurrent.txt
  CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/FlatNTupleSkims/cutTable_lq_eejj_preselection_skim.txt
elif [ "$YEAR" = "2017" ]; then
  #INPUTLIST=config/nanoV7_2017_rskSingleEleL_9apr2021/inputListAllCurrent.txt
  INPUTLIST=config/nanoV7_2017_rskSingleEleL_9apr2021/inputList_jun10.txt
  SKIMNAME=pskEEJJ_12apr2021
  CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2017/FlatNTupleSkims/cutTable_lq_eejj_preselection_skim.txt
elif [ "$YEAR" = "2018" ]; then
  #INPUTLIST=config/nanoV7_2018_rskSingleEleL_9apr2021/inputListAllCurrent.txt
  INPUTLIST=config/nanoV7_2018_rskSingleEleL_9apr2021/inputList_jun10.txt
  SKIMNAME=pskEEJJ_12apr2021
  CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2017/FlatNTupleSkims/cutTable_lq_eejj_preselection_skim.txt
else
  echo "ERROR: did not understand given year of '$YEAR' which is not one of 2016preVFP, 2016postVFP, 2017, 2018"
  echo "Usage: $0 [2016preVFP | 2016postVFP | 2017 | 2018]"
  exit -1
fi

#EOSDIR=/eos/cms/store/user/scooper/LQ/NanoV7/skims/${YEAR}/$SKIMNAME
EOSDIR=/eos/cms/store/group/phys_exotica/leptonsPlusJets/LQ/scooper/ultralegacy/skims/${YEAR}/$SKIMNAME
#EOSDIR=/eos/user/s/scooper/LQ/NanoV7/skims/${YEAR}/$SKIMNAME
OUTPUTDIR=/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/ultralegacy/skims/${YEAR}/$SKIMNAME

#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $OUTPUTDIR -c $CUTFILE -q microcentury -d $EOSDIR -j 5 -n rootTupleTree/tree
python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $OUTPUTDIR -c $CUTFILE -q longlunch -d $EOSDIR -j 10 -n rootTupleTree/tree
