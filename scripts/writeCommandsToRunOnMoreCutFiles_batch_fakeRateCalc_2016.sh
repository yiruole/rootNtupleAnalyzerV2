#!/bin/bash

# Please run this script from the rootNtupleAnalyzerV2 directory by:  
# ./scripts/writeCommandsToRunOnMoreCutFiles.sh

# This scripts creates the whole sets of commands needed to run the analysis on multiple cut files.
# The commands will be written in a text file commandsToRunOnMoreCutFiles.txt in the current directory, 
# to be used by doing cut&paste to a terminal.

# Cut Files should first be created by a script ../rootNtupleMacrosV2/config/eejj/make_eejj_cutFiles.py
# This script will then use those cut files to create the commands needed to run on them.

#### INPUTS HERE ####
#------------
# analysis - FinalSels
files="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/QCDFakeRate/cutTable_lq_QCD_FakeRateCalculation.txt"
#------------
QUEUE=workday
#------------
ANANAME=24nov2021
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=nanoV7/2016/qcdFakeRateCalc/$ANANAME
EOSDIR=/eos/user/s/scooper/LQ/NanoV7/2016/qcdFakeRateCalc/$ANANAME
#EOSDIR=/eos/cms/store/user/scooper/LQ/nanoV7/2016/qcdFakeRateCalc/$ANANAME
excludeCombining=""

# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=35867 #TODO
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
EXE=main
CODENAME=analysisClass_lq_QCD_FakeRateCalculation
#CODENAME=analysisClass_lq_eejj_noJets
#------------
#INPUTLIST=config/nanoV6_2016_rskQCD_18may2020_comb/inputListAllCurrent.txt
#INPUTLIST=config/nanoV6_2016_rskQCD_14jul2020_comb/inputListAllCurrent.txt
#INPUTLIST=config/nanoV6_2016_rskQCD_15jul2020_comb/inputListAllCurrent.txt
#INPUTLIST=config/nanoV6_2016_rskQCD_17jul2020_comb/inputListAllCurrent.txt
INPUTLIST=config/nanoV7_2016_rskQCD_23nov2021_comb/inputListAllCurrent.txt
#------------
XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_QCD_calc_2016.txt
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_fakeRateCalc_2016_batch_`hostname -s`.txt

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
    $excludeCombining

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
