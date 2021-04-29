#!/bin/bash

# Please run this script from the rootNtupleAnalyzerV2 directory by:  
# ./scripts/writeCommandsToRunOnMoreCutFiles.sh

# This scripts creates the whole sets of commands needed to run the analysis on multiple cut files.
# The commands will be written in a text file commandsToRunOnMoreCutFiles.txt in the current directory, 
# to be used by doing cut&paste to a terminal.

# Cut Files should first be created by a script ../rootNtupleMacrosV2/config/eejj/make_eejj_cutFiles.py
# This script will then use those cut files to create the commands needed to run on them.

die () {
    echo >&2 "$@"
    exit 1
}

[ "$#" -eq 1 ] || die "must specify year as argument; usage: writeCommandsToRunOnMoreCutFiles_batch_eejj.sh year [doOptimization]"
YEAR=$1

if [ "$#" -gt 2 ]; then
  OPT=1
else
  OPT=0
fi

#### INPUTS HERE ####
#------------
#ANANAME=eejj_9nov2020
#ANANAME=eejj_exclude319077_17nov2020_oldOptFinalSels
#ANANAME=prefire_eejj_16nov2020_oldOptFinalSels
#ANANAME=prefire_eejj_3feb2021_oldOptFinalSels
#ANANAME=validation_eejj_16feb2021_oldOptFinalSels
#ANANAME=validation_looserPSK_eejj_26feb2021_oldOptFinalSels
ANANAME=precomputePrefire_looserPSK_eejj_12apr2021_oldOptFinalSels
#------------
# inputlist2016=config/nanoV7_2016_pskEEJJ_9nov2020_comb/inputListAllCurrent.txt
# inputlist2016=config/nanoV7_2016_pskEEJJ_4jan2021_comb/inputListAllCurrent.txt
# inputlist2016=config/nanoV7_2016_validation_pskEEJJ_15feb2021/inputListAllCurrent.txt
#inputlist2016=config/nanoV7_2016_pskEEJJ_25feb2021_comb/inputListAllCurrent.txt
#inputlist2016=config/nanoV7_2016_pskEEJJ_16mar2021_comb/inputListAllCurrent.txt
#inputlist2017=config/nanoV7_2017_pskEEJJ_15nov2020_comb/inputListAllCurrent.txt
#inputlist2018=config/nanoV7_2018_pskEEJJ_15nov2020_comb/inputList_dataOnly.txt
inputlist2016=config/nanoV7_2016_pskEEJJ_12apr2021/inputListAllCurrent.txt
inputlist2017=config/nanoV7_2017_pskEEJJ_12apr2021/inputListAllCurrent.txt
#inputlist2017=config/nanoV7_2017_pskEEJJ_12apr2021_separate/inputList_LQToBEleOnly.txt
inputlist2018=config/nanoV7_2018_pskEEJJ_12apr2021/inputListAllCurrent.txt
#------------
CODENAME=analysisClass_lq_eejj
#CODENAME=analysisClass_lq_eejj_noJets
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
# cut files
cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR}/Analysis/cutTable_lq_eejj.txt"
cutFileOpt="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR}/Optimization/cutTable_lq_eejj_opt.txt"
# ilumi
ilumi2016=35867 #TODO
ilumi2017=41540 #FIXME: this number is just from the Egamma twiki
ilumi2018=59399
excludeCombining=""
#------------
if [ "$YEAR" = "2016" ]; then
  echo "Doing 2016!"
  ILUM=$ilumi2016
  INPUTLIST=$inputlist2016
elif [ "$YEAR" = "2017" ]; then
  ILUM=$ilumi2017
  INPUTLIST=$inputlist2017
  excludeCombining="-e LQToBEle*"
elif [ "$YEAR" = "2018" ]; then
  ILUM=$ilumi2018
  INPUTLIST=$inputlist2018
fi
#------------
if [ "$OPT" = "1" ]; then
  DIRSTR="opt"
  files=$cutFileOpt
else
  DIRSTR="analysis"
  files=$cutFileAna
fi
SUBDIR=nanoV7/${YEAR}/$DIRSTR/$ANANAME
EOSDIR=/eos/user/s/scooper/LQ/NanoV7/${YEAR}/$DIRSTR/$ANANAME
COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_${YEAR}_${DIRSTR}_batch_`hostname -s`.txt
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_eejj_${YEAR}.txt
#------------
QUEUE=tomorrow # for systs
#QUEUE=longlunch
#QUEUE=microcentury # sufficient for no systs
#------------
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
EXE=main
#------------
XSECTION=config/xsection_13TeV_2015.txt
#------------
#### END OF INPUTS ####

echo "" > $COMMANDFILE

for file in $files
do
suffix=`basename $file`
suffix=${suffix%\.*}
cat >> $COMMANDFILE <<EOF

####################################################
#### launch, check and combine cmds for $suffix ####
# 1 job per file
python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $OUTDIRPATH/$SUBDIR/condor -c $file -q $QUEUE -d $EOSDIR -j -1 -n rootTupleTree/tree

./scripts/checkJobs.sh $OUTDIRPATH/$SUBDIR/condor $OUTDIRPATH/$SUBDIR/condor

mkdir -p $OUTDIRPATH/$SUBDIR/output_$suffix \
&& time  ./scripts/combineOutputJobs.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/condor \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    $excludeCombining \
    -s

time  ./scripts/combinePlots.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l  `echo "$ILUM*$FACTOR" | bc` \
    -x $XSECTION  \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s $SAMPLELISTFORMERGING \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}.log \
&& mv -v $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}.log $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}_unscaled.log \
&& mv -v $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_plots.root $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_plots_unscaled.root \
&& mv -v $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_tables.dat $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_tables_unscaled.dat
EOF
done


echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to $COMMANDFILE"
