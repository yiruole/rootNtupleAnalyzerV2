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
ANANAME=qcdYield_eejj_2mar2021_oldOptFinalSels
#ANANAME=qcdYield_eejj_20oct2020_optFinalSels
#ANANAME=qcdOpt_14sep2020
#ANANAME=qcdYield_eejj_23oct2020_optFinalSels
#ANANAME=qcdYield_eejj_16sep2020_optFinalSels
#------------
inputlist2016=config/oldInputLists/nanoV7/2016/nanoV7_2016_rskQCD_16oct2020_comb/inputList_dataOnly.txt
inputlist2017=config/nanoV7_2017_rskQCD_19oct2020_comb/inputList_dataOnly.txt
inputlist2018=config/nanoV7_2018_rskQCD_21aug2020_comb/inputList_eGammaOnly.txt
#------------
CODENAME=analysisClass_lq_eejj_QCD
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
# cut files
cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR}/Analysis/cutTable_lq_eejj_QCD.txt"
cutFileOpt="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR}/Optimization/cutTable_lq_eejj_QCD_opt.txt"
# ilumi
ilumi2016=35867 #TODO
ilumi2017=41540 #FIXME: this number is just from the Egamma twiki
ilumi2018=59399
#------------
if [ "$YEAR" = "2016" ]; then
  echo "Doing 2016!"
  ILUM=$ilumi2016
  INPUTLIST=$inputlist2016
elif [ "$YEAR" = "2017" ]; then
  ILUM=$ilumi2017
  INPUTLIST=$inputlist2017
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
COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_QCD_${YEAR}_${DIRSTR}_batch_`hostname -s`.txt
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_QCD_dataDriven_${YEAR}.txt
#------------
#QUEUE=tomorrow
QUEUE=workday
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

python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $OUTDIRPATH/$SUBDIR/condor -c $file -q $QUEUE -d $EOSDIR -j 20 -n rootTupleTree/tree

./scripts/checkJobs.sh $OUTDIRPATH/$SUBDIR/condor $OUTDIRPATH/$SUBDIR/condor

mkdir -p $OUTDIRPATH/$SUBDIR/output_$suffix \
&& time  ./scripts/combineOutputJobs.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/condor \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s

time  ./scripts/combinePlots.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l  `echo "$ILUM*$FACTOR" | bc` \
    -x $XSECTION  \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s $SAMPLELISTFORMERGING \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}.log

EOF
done


echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to $COMMANDFILE"
