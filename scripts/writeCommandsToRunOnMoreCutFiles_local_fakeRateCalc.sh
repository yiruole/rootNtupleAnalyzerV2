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
files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/QCDFakeRate/cutTable_lq_QCD_FakeRateCalculation.txt"
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=2016fakeRate/jan30_rereco/
# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
# integrated luminosity in pb-1 to be used for rescaling/merging MC samples
ILUM=36455 # ntupleV233 2016B-H runs # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
#ILUM=12900 # ICHEP2016
#ILUM=6910 # ICHEP2016 minus early runs
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
CODENAME=analysisClass_lq_QCD_FakeRateCalculation
#------------
INPUTLIST=config/RSK_QCD_rereco_v233_fakeRate/inputListAllCurrent.txt
#------------
XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
#XSECTION=config/xsection_13TeV_2015_Zrescale.txt #first try at Z rescale
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_QCD_dataDriven.txt
#------------
#NCORES=8 #Number of processor cores to be used to run the job
NCORES=16 #Number of processor cores to be used to run the job
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_fakeRateCalc_local_`hostname -s`.txt
echo "" > $COMMANDFILE

for file in $files
do
suffix=`basename $file`
suffix=${suffix%\.*}
cat >> $COMMANDFILE <<EOF

####################################################
#### launch, check and combine cmds for $suffix ####

time python scripts/launchAnalysis.py \
    -i $INPUTLIST \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -p $NCORES \
    >& launch_${suffix}_`hostname -s`.log

mv launch_${suffix}_`hostname -s`.log $OUTDIRPATH/$SUBDIR/output_$suffix/

time  ./scripts/combineTablesAndPlotsTemplate.py \
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
