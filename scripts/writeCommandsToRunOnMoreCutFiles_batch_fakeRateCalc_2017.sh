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
files="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2017/QCDFakeRate/cutTable_lq_QCD_FakeRateCalculation.txt"
#------------
QUEUE=tomorrow
#------------
ANANAME=20jul2020
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=nanoV6/2017/qcdFakeRateCalc/$ANANAME
EOSDIR=/eos/user/s/scooper/LQ/NanoV6/2017/qcdFakeRateCalc/$ANANAME

# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=41540 #FIXME: this number is just from the Egamma twiki
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
EXE=main
CODENAME=analysisClass_lq_QCD_FakeRateCalculation
#CODENAME=analysisClass_lq_eejj_noJets
#------------
#INPUTLIST=config/nanoV6_2017_rskQCD_29mar2020_comb/inputListAllCurrent.txt
INPUTLIST=config/nanoV6_2017_rskQCD_17jul2020_comb/inputListAllCurrent.txt
#------------
XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_QCD_calc_2017.txt
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_fakeRateCalc_2017_batch_`hostname -s`.txt

echo "" > $COMMANDFILE

for file in $files
do
suffix=`basename $file`
suffix=${suffix%\.*}
cat >> $COMMANDFILE <<EOF

####################################################
#### launch, check and combine cmds for $suffix ####

python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $OUTDIRPATH/$SUBDIR/condor -c $file -q $QUEUE -d $EOSDIR -j 1 -n rootTupleTree/tree

./scripts/checkJobs.sh $OUTDIRPATH/$SUBDIR/condor $OUTDIRPATH/$SUBDIR/condor

mkdir $OUTDIRPATH/$SUBDIR/output_$suffix

time  ./scripts/combinePlots.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/condor \
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
