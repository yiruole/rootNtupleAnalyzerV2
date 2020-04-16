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
files="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2017/Analysis/cutTable_lq_eejj_QCD.txt"
# analysis -- preselection only
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_QCD_preselOnly.txt"
# opt
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Optimization/cutTable_lq_eejj_QCD_opt.txt"
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=nanoV6/2017/analysis/eejj_qcd_rsk_apr15
# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=41540 #FIXME: this number is just from the Egamma twiki
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
EXE=main
CODENAME=analysisClass_lq_eejj_QCD
#------------
INPUTLIST=config/nanoV6_2017_rskQCD_29mar2020_comb/inputList_data.txt
#------------
XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_QCD_dataDriven_2017.txt
#------------
#NCORES=8 #Number of processor cores to be used to run the job
NCORES=10 #Number of processor cores to be used to run the job
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_QCD_2017_local_`hostname -s`.txt
# opt
#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_optimization_QCD_local_`hostname -s`.txt

#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_optimization_local_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_QCD_local_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_trigEff_reHLT_AK5_local_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_AK5_local_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_AK4CHS_local_`hostname -s`.txt
echo "" > $COMMANDFILE

for file in $files
do
suffix=`basename $file`
suffix=${suffix%\.*}
cat >> $COMMANDFILE <<EOF

####################################################
#### launch, check and combine cmds for $suffix ####

time python scripts/launchAnalysis.py \
    -e $EXE \
    -k $CODENAME \
    -i $INPUTLIST \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -p $NCORES \
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
