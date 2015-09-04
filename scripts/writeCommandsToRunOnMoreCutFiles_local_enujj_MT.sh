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
files=`ls $LQMACRO/config2012/Analysis/cutTable_lq_enujj_MT.txt`
#files=`ls $LQMACRO/config2012/Systematics/cutTable_lq_enujj_MT_Systematics_PUdown.txt`
#files=`ls $LQMACRO/config2012/Analysis/cutTable_lq_enujj_MT.txt`
#files=`ls $LQMACRO/config2012/MakeFlatNtupleSkims/cutTable_lq_enujjPreselection_skim.txt`
#
#files=`ls $LQMACRO/config2012/Analysis/cutTable_lq_enujj_MT.txt`
#files=`ls $LQMACRO/config2012/Analysis/cutTable_lq_enujj_MT_noMTcut.txt`
#
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=enujj_analysis_lqvector_newCwrElectronScaleRes_EESdown/
#SUBDIR=enujj_analysis_lqvector_newCwrElectronScaleRes_EESup/
#SUBDIR=enujj_analysis_lqvector_newCwrElectronScaleRes_EER/
#SUBDIR=enujj_analysis_lqvector_newCwrElectronScaleRes/
#SUBDIR=enujj_analysis_newCwrElectronScaleRes/
#SUBDIR=enujj_analysis_newCwrElectronScaleRes_EESdown/
#SUBDIR=enujj_analysis_newCwrElectronScaleRes_EESup/
#SUBDIR=enujj_analysis_newCwrElectronScaleRes_EER/
#SUBDIR=METUncert_enujj_analysis/LQSignals
#SUBDIR=METUncert_enujj_analysis/WJets_UnclEneDown
#SUBDIR=EGammaMediumID_enujj_analysis/
#SUBDIR=enujj_analysis/LQ_Vector_LegacyNTupleVersion_JESdown
#SUBDIR=enujj_analysis/NoMTCut_CombinedWJetsMGSysts/
#SUBDIR=enujj_analysis/CombinedWJetsMGSysts/
#
#SUBDIR=enujj_analysis/enujj/
#SUBDIR=lq_microSkims/W3JetsToLNu_ScaleMatchingSysts/
#SUBDIR=enujj_analysis/W2JetsToLNu_ScaleMatchingSysts/
#SUBDIR=enujj_analysis/W3JetsToLNu_ScaleMatchingSysts/
#SUBDIR=enujj_analysis/TTBar_Systs/
#SUBDIR=enujj_analysis/W4JetsToLNu_ScaleMatchingSysts/
         # output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
         # it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=19800 # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
CODENAME=analysisClass_lq_enujj_MT #the actual name of the code used to process the ntuples (without the suffix ".C") 
#------------
INPUTLIST=config/ReducedSkimDataSets_RootNtuple-V00-03-18-Summer12MC_LQVector_EESdown/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDataSets_RootNtuple-V00-03-18-Summer12MC_LQVector_EESup/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDataSets_RootNtuple-V00-03-18-Summer12MC_LQVector_EER/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDataSets_RootNtuple-V00-03-18-Summer12MC_LQVector/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDataSets_RootNtuple-V00-03-18-Summer12MC_SignalsAndBackgrounds/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDataSets_RootNtuple-V00-03-18-Summer12MC_SignalsAndBackgrounds_EESdown/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDataSets_RootNtuple-V00-03-18-Summer12MC_SignalsAndBackgrounds_EESup/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDataSets_RootNtuple-V00-03-18-Summer12MC_SignalsAndBackgrounds_EER/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDataSets_RootNtuple-V00-03-18-Summer12MC_WNJets_AddMETs/inputListAllCurrent.txt
#INPUTLIST=config/ReducedSkimDataSets_RootNtuple-V00-03-18-Summer12MC_ENuJJ_AddMETs/inputListAllCurrent.txt
#INPUTLIST=config/PreselectionSkimDataSets_RootNtuple-V00-03-18-EGammaMediumIDLegacyNTupleVersion_enujj/inputListAllCurrent.txt
#INPUTLIST=config/PreselectionSkimDataSets_RootNtuple-V00-03-18-Summer12MC_LQ_Vector_LegacyNTupleVersion_enujj_JESdown/inputListAllCurrent.txt
#INPUTLIST=config/MicroSkimDatasets_Summer12MC_WJetsToLNu_ScaleMatchingSysts_MG/inputListAllCurrent.txt
#INPUTLIST=config/CombinedWJetsMGSystsMiniSkimDatasets/inputListAllCurrent.txt
# INPUTLIST=config/FlatNtuple_ENuJJ_Preselection/inputListAllCurrent_forAnalysis.txt
#INPUTLIST=config/FlatNtuple_ENuJJ_Preselection/inputListAllCurrent.txt
#INPUTLIST=config/MiniSkimDatasets_Summer12MC_W4JetsToLNu_ScaleMatchingSysts_MG/inputListAllCurrent.txt
#INPUTLIST=config/MiniSkimDatasets_Summer12MC_W2JetsToLNu_ScaleMatchingSysts_MG/inputListAllCurrent.txt
#INPUTLIST=config/MiniSkimDatasets_Summer12MC_W3JetsToLNu_ScaleMatchingSysts_MG/inputListAllCurrent.txt
#INPUTLIST=config/MiniSkimDatasets_Summer12MC_TTBar_Systs_MG/inputListAllCurrent.txt
#------------
XSECTION=config/xsection_8TeV_2012.txt #specify cross section file
#------------
#SAMPLELISTFORMERGING=config/sampleListForMerging_8TeV_enujj.txt.orig
SAMPLELISTFORMERGING=config/sampleListForMerging_8TeV_enujj.txt
#------------
NCORES=8 #Number of processor cores to be used to run the job
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_lqvector_newCwrElectronScaleResEESdown_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_lqvector_newCwrElectronScaleResEESup_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_lqvector_newCwrElectronScaleResEER_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_lqvector_newCwrElectronScaleRes_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_Signals_AndBackgrounds_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_Signals_AndBackgrounds_EESdown_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_Signals_AndBackgrounds_EESup_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_Signals_AndBackgrounds_EER_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_LQSignals_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_LQSignals_UnclEneUp_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_WNJets_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
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
    >& launch_${suffix}.log 

mv launch_${suffix}.log $OUTDIRPATH/$SUBDIR/output_$suffix/

time  ./scripts/combineTablesTemplate.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l  `echo "$ILUM*$FACTOR" | bc` \
    -x $XSECTION  \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s $SAMPLELISTFORMERGING \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTables_${suffix}.log

time  ./scripts/combinePlotsTemplate.py \
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
