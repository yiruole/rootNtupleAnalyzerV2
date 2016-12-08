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
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_enujj_trigger3_id2_effiStudy.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_enujj_trigger3_id3_effiStudy.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_enujj_trigger3_id4_effiStudy.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_enujj_trigger3_id5_effiStudy.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_enujj_trigger4_id2_effiStudy.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_enujj_trigger4_id3_effiStudy.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_enujj_trigger4_id4_effiStudy.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_enujj_trigger4_id5_effiStudy.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_enujj_trigger5_id2_effiStudy.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_enujj_trigger5_id3_effiStudy.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_enujj_trigger5_id4_effiStudy.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_enujj_trigger5_id5_effiStudy.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger4_id1_effiStudy.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger5_id1_effiStudy.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger4_id0_effiStudy.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger5_id0_effiStudy.txt"
files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger6_id0_effiStudy.txt
/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger7_id0_effiStudy.txt"


#------------
OUTDIRPATH=$LQDATA/2016analysis/  # a subdir will be created for each cut file 
SUBDIR=trigEffStudies_2016sep19
#SUBDIR=RunII/enujj_trigEff_10Dec2015_AK5_reHLT/
#SUBDIR=RunII/enujj_trigEff_9Dec2015_AK5/
# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=2094 # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
#the actual name of the code used to process the ntuples (without the suffix ".C") 
CODENAME=analysisClass_lq1_effiStudy
#------------
INPUTLIST=config/FullNTuple_PrivateSignalSamples/inputListAllCurrent.txt
#INPUTLIST=config/FullNTupleDatasets/inputListAllCurrent_enujjSignals.txt
#INPUTLIST=config/FullNTupleDatasets_ReRunHLTSignals/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDatasets_AK4CHS_test/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDatasets/inputListAllCurrent.txt
#------------
XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_eejj.txt
#SAMPLELISTFORMERGING=config/sampleListForMerging_8TeV_eejj.txt
#SAMPLELISTFORMERGING=config/sampleListForMerging_8TeV_eejj_LQVector.txt ### CHANGE TO USE VECTOR LQ
#SAMPLELISTFORMERGING=config/sampleListForMerging_8TeV_eejj_rpvStop.txt ### CHANGE TO USE RPV STOP
#------------
NCORES=8 #Number of processor cores to be used to run the job
#NCORES=16 #Number of processor cores to be used to run the job
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_trigEff_privSigSamples_local_`hostname -s`.txt
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
    >& launch_${suffix}_`hostname -s`.log &

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
