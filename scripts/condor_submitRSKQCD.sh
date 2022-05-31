#!/bin/bash

YEAR=$1

if [ "$YEAR" = "2016" ]; then
  echo "Doing 2016!"
  #SKIMNAME=rskQCD_looseEGM_23mar2022
  SKIMNAME=rskQCD_heep_4apr2022
  INPUTLIST=config/nanoV7_2016_postProc/inputListAllCurrent.txt
  #CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/ReducedSkims/cutTable_lq1_skim_QCD.txt
  CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/ReducedSkims/cutTable_lq1_skim_QCD_HEEP.txt
elif [ "$YEAR" = "2017" ]; then
  SKIMNAME=rskQCD_22apr2021
  INPUTLIST=config/nanoV7_2017_postProc/inputListAllCurrent.txt
  CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2017/ReducedSkims/cutTable_lq1_skim_QCD.txt
elif [ "$YEAR" = "2018" ]; then
  SKIMNAME=rskQCD_22apr2021
  INPUTLIST=config/nanoV7_2018_postProc/inputListAllCurrent.txt
  CUTFILE=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2018/ReducedSkims/cutTable_lq1_skim_QCD.txt
else
  echo "ERROR: did not understand given year of '$YEAR' which is not one of 2016, 2017, 2018"
  echo "Usage: $0 [2016 | 2017 | 2018]"
  exit -1
fi

#EOSDIR=/eos/user/s/scooper/LQ/NanoV7/skims/${YEAR}/$SKIMNAME
EOSDIR=/eos/cms/store/group/phys_exotica/leptonsPlusJets/LQ/scooper/NanoV7/skims/${YEAR}/$SKIMNAME
#EOSDIR=/eos/cms/store/user/scooper/LQ/NanoV7/skims/${YEAR}/$SKIMNAME
OUTPUTDIR=/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nanoV7/skims/${YEAR}/$SKIMNAME

python scripts/launchAnalysis_batch_ForSkimToEOS.py -j 40 -q tomorrow -i $INPUTLIST -o $OUTPUTDIR -n Events -c $CUTFILE -d $EOSDIR -r
