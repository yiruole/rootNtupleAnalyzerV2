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
files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_noJets.txt"

#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_loosenEleRequirements_2lowPtJets.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_eles50GeV_jets50GeV_st300GeV.txt"
# opt
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Optimization/cutTable_lq_eejj_opt.txt"
# studies
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_loosenEleRequirements_1Jet.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_loosenEleRequirements_noJetRequirement.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_1jetOrLess.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_preselectionOnly.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_2012preselectionOnly.txt
#/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_preselectionOnly_tightenEleCuts.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Studies/SignalEffiTriggerStudy/cutTable_lq1_eejj_trigger5_id1_effiStudy.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/745/LQRootTupleMiniAOD745/src/Leptoquarks/macros/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_preselectionOnly.txt"
#files=`ls $LQMACRO/config2012/Analysis/cutTable_lq_eejj.txt`
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=2016analysis/dec1_onPSK_addStSFplots_ICHEPDataExcludeEarlyRuns_ele27wplooseEta2p1Data2016CurveMC_eejj2015FinalSels
#SUBDIR=2016analysis/nov28_onRSK_addStSFplots_ICHEPDataExcludeEarlyRuns_ele27wplooseEta2p1Data2016CurveMC_eejj2015FinalSels
#SUBDIR=2016analysis/nov28_onRSK_addStSFplots_ICHEPDataAndMC_ele27wptightOrPhoton175Data2015CurveMC_eejj2015FinalSels
#SUBDIR=2016analysis/nov26_addStSFplots_ICHEPDataAndMC_ele27wptightOrPhoton175Data2015CurveMC_eejj2015FinalSels
#SUBDIR=2016analysis/nov28_noJets_ele27wptightOrPhoton175Data2015CurveMC_eejj2015FinalSels
#SUBDIR=2016analysis/nov20_addStSFplots_allDataAndMC_ele27wptightOrPhoton175Data2015CurveMC_eejj2015FinalSels
# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
#ILUM=27217 # ntupleV211 2016B-G runs # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
ILUM=12900 # ICHEP2016
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
EXE=mainEEJJana
CODENAME=analysisClass_lq_eejj
#CODENAME=analysisClass_lq_eejj_noJets
#CODENAME=analysisClass_lq_eejj_1Jet
#CODENAME=analysisClass_lq_eejj_opt
#CODENAME=analysisClass_lq_eejj_preselectionOnly #the actual name of the code used to process the ntuples (without the suffix ".C") 
#CODENAME=analysisClass_lq1_effiStudy
#------------
#INPUTLIST=config/RSK_SingleEleLoose_oct25/inputListAllCurrent.txt
INPUTLIST=config/PSK_SingleEleLoose_eejj_nov11/inputListAllCurrent.txt
#INPUTLIST=config/PSK_SingleEleLoose_eejjNoJetsNoST_nov24/inputListAllCurrent.txt
#INPUTLIST=config/PSK_SingleEleLoose_sep24/inputList_SingleElectron.txt
#INPUTLIST=config/PSK_SingleEleLoose_eejj_oct26/inputListAllCurrent.txt
#INPUTLIST=config/FullNTupleDatasets_ReRunHLTSignals/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDatasets_AK4CHS_test/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDatasets/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDatasets/inputList_eejjMinimal.txt
#------------
XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_eejj.txt
#SAMPLELISTFORMERGING=config/sampleListForMerging_8TeV_eejj.txt
#SAMPLELISTFORMERGING=config/sampleListForMerging_8TeV_eejj_LQVector.txt ### CHANGE TO USE VECTOR LQ
#SAMPLELISTFORMERGING=config/sampleListForMerging_8TeV_eejj_rpvStop.txt ### CHANGE TO USE RPV STOP
#------------
#NCORES=8 #Number of processor cores to be used to run the job
NCORES=16 #Number of processor cores to be used to run the job
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_local_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_noJets_local_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_optimization_local_`hostname -s`.txt
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
