#!/bin/bash

# Please run this script from the rootNtupleAnalyzerV2 directory by:  
# ./scripts/writeCommandsToRunOnMoreCutFiles.sh

# This scripts creates the whole sets of commands needed to run the analysis on multiple cut files.
# The commands will be written in a text file commandsToRunOnMoreCutFiles.txt in the current directory, 
# to be used by doing cut&paste to a terminal.

# Cut Files should first be created by a script ../rootNtupleMacrosV2/config/eejj/make_eejj_cutFiles.py
# This script will then use those cut files to create the commands needed to run on them.

#### INPUTS HERE ####
files=`ls ../rootNtupleMacrosV2/config/eejj/cutTable_eejjSample_*.txt` # list of cut files that will be used
OUTDIRPATH=/afs/cern.ch/user/p/prumerio/scratch0/lq/collisions/data  # a subdir will be created for each cut file 
ILUM=100 # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
#### END OF INPUTS ####

echo "" > commandsToRunOnMoreCutFiles.txt

for file in $files
do
suffix=`basename $file`
suffix=${suffix%\.*}
OUTDIR=$OUTDIRPATH/output_$suffix
cat >> commandsToRunOnMoreCutFiles.txt <<EOF

####################################################
#### launch, check and combine cmds for $suffix ####

  ./scripts/launchAnalysis_batch.pl \
    -i config/inputListReallyAll.txt \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIR  \
    -j 30 \
    -q 1nh \
    | tee launch_${suffix}.log

  ./scripts/check_combine_output_batch.py \
    -i config/inputListReallyAll.txt \
    -c analysisClass_eejjSample \
    -d $OUTDIR \
    -o $OUTDIR \
    -q 1nh \
    | tee checkcombine_${suffix}.log


  ./scripts/combineTablesTemplate.py \
    -i config/inputListReallyAll.txt \
    -c analysisClass_eejjSample \
    -d $OUTDIR \
    -l ${ILUM} \
    -x config/xsection_7TeV.txt \
    -o $OUTDIR \
    -s config/sampleListForMerging_7TeV.txt \
    | tee combineTables_${suffix}.log

  ./scripts/combinePlotsTemplate.py \
    -i config/inputListReallyAll.txt \
    -c analysisClass_eejjSample \
    -d $OUTDIR \
    -l ${ILUM} \
    -x config/xsection_7TeV.txt \
    -o $OUTDIR \
    -s config/sampleListForMerging_7TeV.txt \
    | tee combinePlots_${suffix}.log

EOF
done

echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to commandsToRunOnMoreCutFiles.txt"
