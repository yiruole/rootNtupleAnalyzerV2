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
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_2012LQ650FinalSelection.txt"
files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_loosenEleRequirements_2lowPtJets.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_eles50GeV_jets50GeV_st300GeV.txt"
# opt
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Optimization/cutTable_lq_eejj_opt.txt"
# QCD FR
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_QCD.txt"
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
SUBDIR=RunII/eejj_analysis_finalSels_StWithPtHeep_29may2016
#SUBDIR=RunII/eejj_analysis_2012LQ650finalSel_27may2016
#SUBDIR=RunII/eejj_analysis_finalSelsUnbugged_24may2016
#SUBDIR=RunII/eejj_analysis_opt_16may2016/
#SUBDIR=RunII/eejj_analysis_opt_14may2016
#SUBDIR=RunII/eejj_analysis_LQ650_8may2016
#SUBDIR=RunII/eejj_analysis_opt_8may2016_QCD
#SUBDIR=RunII/eejj_analysis_opt_5may2016_silverSingleElectron_v1-5-5_and_MCv1-5-3
#SUBDIR=RunII/eejj_analysis_opt_4may2016_silver_SingleElectron_v1-5-5/
#SUBDIR=RunII/eejj_ele27wplooseData_eles45GeV_2jets_21feb2016_v1-5-2
#SUBDIR=RunII/eejj_ele27wplooseData_eles35GeV_noJets_noSt_28feb2016_v1-5-3
#SUBDIR=RunII/eejj_eles50GeV_jets50GeV_sT300GeV_ele27WPLooseWithZPrimeEta2p1TurnOn_17mar2016_v1-5-3
#SUBDIR=RunII/eejj_opt_eles50GeV_jets50GeV_sT300GeV_ele27WPLooseWithZPrimeEta2p1TurnOn_26mar2016_v1-5-3
#SUBDIR=RunII/eejj_QCDFakeRate_eles50GeV_jets50GeV_sT300GeV_9apr2016_v1-5-5
#SUBDIR=RunII/eejj_QCDFakeRate_silver2015D_eles50GeV_jets50GeV_sT300GeV_1may2016_v1-5-5
#SUBDIR=RunII/eejj_ele27wplooseData_eles35GeV_1Jet50GeV_7feb2016_v1-5-2
#SUBDIR=RunII/eejj_24jan2016_v1-4-3_optimization
#SUBDIR=RunII/eejj_20jan2016_v1-4-3_updateEcalCondsRun2015D
#SUBDIR=RunII/eejj_16Dec2015_AK4CHS_v1-4-3_Few2012LQFinalSels
#SUBDIR=RunII/eejj_trigEff_9Dec2015_AK5_reHLTSignalsFromRaw/
# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
# integrated luminosity in pb-1 to be used for rescaling/merging MC samples
ILUM=2570 # was 2153; this is from May3 2016: no Run2015C, no bad beamspot runs, moriond2016 normtag, silverJSON
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
#CODENAME=analysisClass_lq_eejj_noJets
#CODENAME=analysisClass_lq_eejj_1Jet
#CODENAME=analysisClass_lq_eejj_opt
CODENAME=analysisClass_lq_eejj_QCD
#CODENAME=analysisClass_lq_eejj
#CODENAME=analysisClass_lq_eejj_preselectionOnly #the actual name of the code used to process the ntuples (without the suffix ".C") 
#CODENAME=analysisClass_lq1_effiStudy
#------------
#INPUTLIST=config/FullNTupleDatasets_ReRunHLTSignals/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDatasets_AK4CHS_test/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDatasets/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDatasets/inputListAllCurrentEEJJ.txt
#INPUTLIST=config/ReducedSkimDatasets_silver_SinglePhoton_v1-5-5/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDatasets_silver_SingleElectron_V1-5-5/inputListAllCurrent.txt
#INPUTLIST=config/TestCombinationMay4/inputListAllCurrent.txt
INPUTLIST=config/TestCombinationMay4/inputList_QCD.txt
#INPUTLIST=config/TestCombinationMay4/inputListFailedCrabs.txt
#------------
#XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
#XSECTION=config/xsection_13TeV_2015_Zrescale.txt #first try at Z rescale
#------------
#SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_eejj.txt
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_eejj_QCD.txt
#------------
NCORES=8 #Number of processor cores to be used to run the job
#NCORES=16 #Number of processor cores to be used to run the job
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_analysis_QCD_local_`hostname -s`.txt
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
