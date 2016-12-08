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
files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_enujj_MT.txt"
#
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=2016analysis/enujj_psk_dec3_ICHEPDataExcludeEarlyRunsAndMC_ele27wptightEta2p1CurveMC_enujj2012FinSels
#SUBDIR=2016analysis/enujj_oct26_addStSFplots_allDataAndMC_ele27wptightOrPhoton175Data2015CurveMC_enujj2012FinSels
#SUBDIR=2016analysis/enujj_onRSK_local_nov1_addStSFplots_allDataAndMC_ele27wptightOrPhoton175Data2015CurveMC_enujj2012FinSels
#SUBDIR=2016analysis/enujj_psk_local_nov18_addStSFplots_allDataAndMC_ele27wptightOrPhoton175Data2015CurveMC_enujj2012FinSels
#SUBDIR=2016analysis/enujj_psk_local_nov18_addStSFplots_ICHEPDataAndMC_ele27wptightOrPhoton175Data2015CurveMC_enujj2012FinSels
         # output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
         # it is suggested to specify the luminosity in the name of the directory
#------------
#ILUM=27217 # ntupleV211 2016B-G runs # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
#ILUM=12900 # ICHEP2016
ILUM=6910 # ICHEP2016 remove early runs
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
CODENAME=analysisClass_lq_enujj_MT #the actual name of the code used to process the ntuples (without the suffix ".C") 
#------------
INPUTLIST=config/PSK_SingleEleLoose_enujj_nov11/inputListAllCurrent.txt
#INPUTLIST=config/PSK_SingleEleLoose_enujj_oct26/inputListAllCurrent.txt
#INPUTLIST=config/RSK_SingleEleLoose_oct25/inputListAllCurrent.txt
#------------
XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_enujj.txt
#------------
#NCORES=8 #Number of processor cores to be used to run the job
NCORES=16
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_PSK_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_RSK_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_AK4CHS_`hostname -s`.txt
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
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}.log

EOF
done


echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to $COMMANDFILE"
