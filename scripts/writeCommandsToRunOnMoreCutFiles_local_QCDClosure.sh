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
# analysis
files="afs/cern.ch/user/e/eipearso/public/leptoquark_analysis/rootNtupleMacrosV2/config2016/QCDFakeRate/cutTable_lq_QCD_FakeRateClosureTest_ccj_DataOnly.txt"
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=qcdFRCT
# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=35867 # [was 36455] ntupleV235 2016B-H rereco runs # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
#ILUM=12900 # ICHEP2016
#ILUM=6910 # ICHEP2016 minus early runs
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
EXE=main
CODENAME=analysisClass_lq_QCD_FakeRateClosureTest
#------------
INPUTLIST=config/myDatasets/2016HEEPpreDataOnly/inputListAllCurrent.txt
#------------
XSECTION=config/xsection_13TeV_2022.txt #specify cross section file
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_QCD_calc_2016preVFPDataOnly.yaml
#------------
#NCORES=8 #Number of processor cores to be used to run the job
NCORES=10 #Number of processor cores to be used to run the job
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_analysis_QCDClosureTest_local_`hostname -s`.txt
echo "" > $COMMANDFILE

for file in $files
do
suffix=`basename $file`
suffix=${suffix%\.*}
cat >> $COMMANDFILE <<EOF

####################################################
#### launch, check and combine cmds for $suffix ####

time python scripts/launchAnalysis.py \
    -k $CODENAME \
    -e $EXE \
    -i $INPUTLIST \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -p $NCORES \
    -k $CODENAME \
    >& launch_${suffix}_`hostname -s`.log

mv launch_${suffix}_`hostname -s`.log $OUTDIRPATH/$SUBDIR/output_$suffix/

time  ./scripts/combinePlots.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l  `echo "$ILUM*$FACTOR" | bc` \
    -x $XSECTION  \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s $SAMPLELISTFORMERGING \
    -f $OUTDIRPATH/$SUBDIR/output_$suffix/launch_${suffix}_`hostname -s`.log \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}.log

EOF
done


echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to $COMMANDFILE"
