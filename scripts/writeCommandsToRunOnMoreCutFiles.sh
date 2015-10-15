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
#files=`ls $LQMACRO/config/cutTable_enujjSample.txt` # list of cut files that will be used
files="/afs/cern.ch/work/s/scooper/private/cmssw/745/LQRootTupleMiniAOD745/src/Leptoquarks/macros/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger1_id1_effiStudy.txt
/afs/cern.ch/work/s/scooper/private/cmssw/745/LQRootTupleMiniAOD745/src/Leptoquarks/macros/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger1_id2_effiStudy.txt
/afs/cern.ch/work/s/scooper/private/cmssw/745/LQRootTupleMiniAOD745/src/Leptoquarks/macros/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger1_id3_effiStudy.txt
/afs/cern.ch/work/s/scooper/private/cmssw/745/LQRootTupleMiniAOD745/src/Leptoquarks/macros/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger1_id4_effiStudy.txt
/afs/cern.ch/work/s/scooper/private/cmssw/745/LQRootTupleMiniAOD745/src/Leptoquarks/macros/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger1_id5_effiStudy.txt
/afs/cern.ch/work/s/scooper/private/cmssw/745/LQRootTupleMiniAOD745/src/Leptoquarks/macros/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger2_id1_effiStudy.txt
/afs/cern.ch/work/s/scooper/private/cmssw/745/LQRootTupleMiniAOD745/src/Leptoquarks/macros/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger3_id1_effiStudy.txt
/afs/cern.ch/work/s/scooper/private/cmssw/745/LQRootTupleMiniAOD745/src/Leptoquarks/macros/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger3_id2_effiStudy.txt
/afs/cern.ch/work/s/scooper/private/cmssw/745/LQRootTupleMiniAOD745/src/Leptoquarks/macros/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger3_id3_effiStudy.txt
/afs/cern.ch/work/s/scooper/private/cmssw/745/LQRootTupleMiniAOD745/src/Leptoquarks/macros/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger3_id4_effiStudy.txt
/afs/cern.ch/work/s/scooper/private/cmssw/745/LQRootTupleMiniAOD745/src/Leptoquarks/macros/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger3_id5_effiStudy.txt"

#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=trigIDSpring15EffStudyEejjSignals
         # output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
         # it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=330 # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
CODENAME=analysisClass_lq1_effiStudy #the actual name of the code used to process the ntuples (without the suffix ".C") 
#------------
INPUTLIST=config/LQToUE_BetaOne_RunIIMC_MINIAODSIM/inputListAllCurrent.txt #specify input list
#------------
XSECTION=config/xsection_7TeV_2011.txt #specify cross section file
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_7TeV_enujj_2011.txt #specify list for sample merging
#------------
##DATA
NJOBS=5 #number of jobs for each dataset
WAIT=1 #seconds of delay between submission of different datasets
##MC
#NJOBS=30 #number of jobs for each dataset
#WAIT=5 #seconds of delay between submission of different datasets
#------------
QUEUE=1nh #bsub queue  

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_trigEffStudyEejjSignals_trigsNewIDs_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
echo "" > $COMMANDFILE

for file in $files
do
suffix=`basename $file`
suffix=${suffix%\.*}
cat >> $COMMANDFILE <<EOF

####################################################
#### launch, check and combine cmds for $suffix ####

  ./scripts/launchAnalysis_batch.pl \
    -i $INPUTLIST \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -j $NJOBS \
    -q $QUEUE \
    -w $WAIT \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/launch_${suffix}.log

   rm ToBeResubmitted.list  && ./scripts/check_combine_output_batch.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -q $QUEUE \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/checkcombine_${suffix}.log

  ./scripts/combineTablesTemplate.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l  `echo "$ILUM*$FACTOR" | bc` \
    -x $XSECTION  \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s $SAMPLELISTFORMERGING \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTables_${suffix}.log

  ./scripts/combinePlotsTemplate.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l ${ILUM} \
    -x $XSECTION  \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s $SAMPLELISTFORMERGING \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combinePlots_${suffix}.log

EOF
done


echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to $COMMANDFILE"
