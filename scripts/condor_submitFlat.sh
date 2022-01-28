
#!/bin/bash

YEAR=$1

if [ "$YEAR" = "2016" ]; then
  echo "Doing 2016!"
  #INPUTLIST=config/nanoV7_2016_rskSingleEleL_9apr2021/inputListAllCurrent.txt
  # INPUTLIST=config/nanoV7_2016_rskSingleEleL_9apr2021/inputList_wjetPt50Only.txt
  INPUTLIST=config/nanoV7_2016_rskSingleEleL_egLoose_21sep2021/inputListAllCurrent.txt
  SKIMNAME=pskEEJJ_egLoose_22sep2021
  CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/FlatNTupleSkims/cutTable_lq_eejjPreselection_skim.txt
elif [ "$YEAR" = "2017" ]; then
  #INPUTLIST=config/nanoV7_2017_rskSingleEleL_9apr2021/inputListAllCurrent.txt
  INPUTLIST=config/nanoV7_2017_rskSingleEleL_9apr2021/inputList_jun10.txt
  SKIMNAME=pskEEJJ_12apr2021
  CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2017/FlatNTupleSkims/cutTable_lq_eejjPreselection_skim.txt
elif [ "$YEAR" = "2018" ]; then
  #INPUTLIST=config/nanoV7_2018_rskSingleEleL_9apr2021/inputListAllCurrent.txt
  INPUTLIST=config/nanoV7_2018_rskSingleEleL_9apr2021/inputList_jun10.txt
  SKIMNAME=pskEEJJ_12apr2021
  CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2017/FlatNTupleSkims/cutTable_lq_eejjPreselection_skim.txt
else
  echo "ERROR: did not understand given year of '$YEAR' which is not one of 2016, 2017, 2018"
  echo "Usage: $0 [2016 | 2017 | 2018]"
  exit -1
fi

#EOSDIR=/eos/cms/store/user/scooper/LQ/NanoV7/skims/${YEAR}/$SKIMNAME
EOSDIR=/eos/cms/store/group/phys_exotica/leptonsPlusJets/LQ/scooper/nanoV7/skims/${YEAR}/$SKIMNAME
#EOSDIR=/eos/user/s/scooper/LQ/NanoV7/skims/${YEAR}/$SKIMNAME
OUTPUTDIR=/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nanoV7/skims/${YEAR}/$SKIMNAME

#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $OUTPUTDIR -c $CUTFILE -q microcentury -d $EOSDIR -j 5 -n rootTupleTree/tree
python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $OUTPUTDIR -c $CUTFILE -q longlunch -d $EOSDIR -j 10 -n rootTupleTree/tree
