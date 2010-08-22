#!/bin/bash

# Please run this script from the rootNtupleAnalyzerV2 directory by:  
# ./scripts/writeCommandsToRunOnMoreCutFiles.sh

# This scripts creates the whole sets of commands needed to run the analysis on multiple cut files.
# The commands will be written in a text file commandsToRunOnMoreCutFiles.txt in the current directory, 
# to be used by doing cut&paste to a terminal.

# Cut Files should first be created by a script ../rootNtupleMacrosV2/config/eejj/make_eejj_cutFiles.py
# This script will then use those cut files to create the commands needed to run on them.

#### INPUTS HERE ####
files=`ls $LQMACRO/config/eejj/cutTable_eejjSample_*.txt $LQMACRO/config/cutTable_eejjSample.txt` # list of cut files that will be used
#files=`ls ../rootNtupleMacrosV2/config/cutTable_eejjSample.txt` # list of cut files that will be used
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=eejj_analysis/1.1pb-1 # output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
                             # it is suggested to specify the luminosity in the name of the directory
ILUM=1.1 # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
CODENAME=analysisClass_eejjSample #the actual name of the code used to process the ntuples (without the suffix ".C") 
XSECTION=config/xsection_7TeV.txt #specify cross section file
#XSECTION=config/xsection_7TeV_Zrescale.txt #specify cross section file
NJOBS=30 #number of jobs for each dataset
WAIT=5 #seconds of delay between submission of different datasets

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
    -j $NJOBS \
    -q 1nh \
    -w $WAIT \
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
    -x $XSECTION  \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s config/sampleListForMerging_7TeV.txt \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTables_${suffix}.log

  ./scripts/combinePlotsTemplate.py \
    -i config/inputListAllCurrent.txt \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l ${ILUM} \
    -x $XSECTION  \
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
