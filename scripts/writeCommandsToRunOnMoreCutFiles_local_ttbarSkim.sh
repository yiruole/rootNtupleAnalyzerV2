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
# skim
files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/FlatNTupleSkims/cutTable_lq_TTBar_skim.txt"

#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=RunII/lq_skim_2015/RootNtuple-mix-silverData_TTbarSkim
#SUBDIR=RunII/eejj_analysis_preselectionOnly_noExactTwoElectronsRequirement_30jun2016
# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
# integrated luminosity in pb-1 to be used for rescaling/merging MC samples
ILUM=2570 # was 2153; this is from May3 2016: no Run2015C, no bad beamspot runs, moriond2016 normtag, silverJSON
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
CODENAME=analysisClass_TTbar_skim
#CODENAME=analysisClass_lq_eejj_noJets
#CODENAME=analysisClass_lq_eejj_1Jet
#CODENAME=analysisClass_lq_eejj_opt
#CODENAME=analysisClass_lq_eejj_QCD
#CODENAME=analysisClass_lq_eejj
#CODENAME=analysisClass_lq_eejj_preselectionOnly #the actual name of the code used to process the ntuples (without the suffix ".C") 
#CODENAME=analysisClass_lq1_effiStudy
#------------
INPUTLIST=config/TestCombinationMay4/inputListAllCurrent.txt
#INPUTLIST=config/TestCombinationMay4/inputList_DYJets.txt
#INPUTLIST=config/FullNTupleDatasets_ReRunHLTSignals/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDatasets_AK4CHS_test/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDatasets/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDatasets/inputListAllCurrentEEJJ.txt
#INPUTLIST=config/ReducedSkimDatasets_silver_SinglePhoton_v1-5-5/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDatasets_silver_SingleElectron_V1-5-5/inputListAllCurrent.txt
#INPUTLIST=config/TestCombinationMay4/inputListAMCatNLO.txt
#INPUTLIST=config/TestCombinationMay4/inputList_QCD.txt
#INPUTLIST=config/TestCombinationMay4/inputListFailedCrabs.txt
#------------
#XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
XSECTION=versionsOfAnalysis_eejj/1jun_ttbarRescale/xsection_13TeV_2015_TTbarRescale.txt # with ttbar rescaling
#XSECTION=config/xsection_13TeV_2015_Zrescale.txt #first try at Z rescale
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_eejj.txt
#SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_eejj_QCD.txt
#------------
NCORES=8 #Number of processor cores to be used to run the job
#NCORES=16 #Number of processor cores to be used to run the job
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_ttbarSkim_local_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_optimization_local_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_optimization_QCD_local_`hostname -s`.txt
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
