#!/bin/bash

# Please run this script from the rootNtupleAnalyzerV2 directory by:  
# ./scripts/writeCommandsToRunOnMoreCutFiles.sh

# This scripts creates the whole sets of commands needed to run the analysis on multiple cut files.
# The commands will be written in a text file commandsToRunOnMoreCutFiles.txt in the current directory, 
# to be used by doing cut&paste to a terminal.

# Cut Files should first be created by a script ../rootNtupleMacrosV2/config/eejj/make_eejj_cutFiles.py
# This script will then use those cut files to create the commands needed to run on them.

#### INPUTS HERE ####
#files=`ls ../rootNtupleMacrosV2/config/eejj/cutTable_eejjSample_*.txt` # list of cut files that will be used
files=`ls ../rootNtupleMacrosV2/config/cutTable_eejjSample.txt` # list of cut files that will be used
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=HEEPeffic/254nb-1/IDIso_ID #output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
ILUM=0.25385 # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
CODENAME=analysisClass_eejjSample #the actual name of the code used to process the ntuples (without the suffix ".C") 

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
echo "" > $COMMANDFILE

for file in $files
do
suffix=`basename $file`
suffix=${suffix%\.*}
cat >> $COMMANDFILE <<EOF

####################################################
#### launch, check and combine cmds for $suffix ####

  ./scripts/launchAnalysis_batch.pl \
    -i config/inputListAllCurrent.txt \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -j 30 \
    -q 1nh \
    -w 5 \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/launch_${suffix}.log

  ./scripts/check_combine_output_batch.py \
    -i config/inputListAllCurrent.txt \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -q 1nh \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/checkcombine_${suffix}.log

  ./scripts/combineTablesTemplate.py \
    -i config/inputListAllCurrent.txt \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l  `echo "$ILUM*$FACTOR" | bc` \
    -x config/xsection_7TeV.txt \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s config/sampleListForMerging_7TeV.txt \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTables_${suffix}.log

  ./scripts/combinePlotsTemplate.py \
    -i config/inputListAllCurrent.txt \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l ${ILUM} \
    -x config/xsection_7TeV.txt \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s config/sampleListForMerging_7TeV.txt \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combinePlots_${suffix}.log

EOF
done


echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to $COMMANDFILE"
