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
#files=`ls $LQMACRO/config2012/ReducedSkims/cutTable_lq1_skim_SingleEle_loose_addMETs.txt`
#files=`ls $LQMACRO/config2012/ReducedSkims/cutTable_lq1_skim_SingleEle_loose_JESdown_addMETs.txt`
#files=`ls $LQMACRO/config2012/ReducedSkims/cutTable_lq1_skim_SingleEle_loose_addMETs.txt`
#files=`ls $LQMACRO/config2012/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt`
# 2015 skims
#files=`ls $LQMACRO/config2012/ReducedSkims/cutTable_lq1_skim_SingleEle_loose_EER.txt`
#files=`ls $LQMACRO/config2012/ReducedSkims/cutTable_lq1_skim_SingleEle_loose_EESup.txt`
#files=`ls $LQMACRO/config2012/ReducedSkims/cutTable_lq1_skim_SingleEle_loose_EESdown.txt`
files=`ls $LQMACRO/config2012/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt`
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
#------------
SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_LQ_Vector"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_LQ_Vector_EESdown"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_LQ_Vector_EESup"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_LQ_Vector_EER"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_StopToEBBQ_EER"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_StopToEBBQ_EESup"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_StopToEBBQ_EESdown"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_StopToEBBQ"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_LQ_Vector"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_Signals"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_Signals_EESdown"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_Signals_EESup"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_Signals_EER"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_BackgroundMC"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_BackgroundMC_EESdown"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_BackgroundMC_EESup"
#SUBDIR="lq_skim_2015/RootNtuple-V00-03-18-SingleEleLoose_BackgroundMC_EER"

#SUBDIR="lq_skim_2014/RootNtuple-V00-03-18-SingleEleLoose_AddMETs_ENuJJ_JESdown"
#SUBDIR="lq_skim_2014/RootNtuple-V00-03-11-LegacyNTupleVersion_EGammaMediumID"
#SUBDIR="lq_skim_2014/RootNtuple-V00-03-18-Summer12MC_StopToEBBQ_LegacyNTupleVersion_JESdown"
#SUBDIR="lq_skim_2014/RootNtuple-V00-03-18-Summer12MC_LQ_Vector_LegacyNTupleVersion_JESdown"
#SUBDIR="lq_skim_2013/RootNtuple-V00-03-11-Summer12MC_DY4JetsToLL_ScaleMatchingSysts_MG"
#SUBDIR="lq_skim_2013/RootNtuple-V00-03-11-Summer12MC_W4JetsToLNu_ScaleMatchingSysts_MG"
#SUBDIR="lq_skim_2013/RootNtuple-V00-03-11-Summer12MC_TTBar_Systs_MG"
# SUBDIR="lq_skim_2012/RootNtuple-V00-03-07-Summer12MC_DY0JetsToLL_MG"
         # output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
         # it is suggested to specify the luminosity in the name of the directory
#------------
#FULLEOSDIR="/eos/cms/store/group/phys_exotica/leptonsPlusJets/leptoquarks/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_LQ_Vector_EER"
#FULLEOSDIR="/eos/cms/store/group/phys_exotica/leptonsPlusJets/leptoquarks/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_LQ_Vector_EESup"
#FULLEOSDIR="/eos/cms/store/group/phys_exotica/leptonsPlusJets/leptoquarks/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_LQ_Vector_EESdown"
FULLEOSDIR="/eos/cms/store/group/phys_exotica/leptonsPlusJets/leptoquarks/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_LQ_Vector"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_LQ_Vector_EESdown"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_LQ_Vector_EESup"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_LQ_Vector_EER"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_StopToEBBQ_EER"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_StopToEBBQ_EESup"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_StopToEBBQ_EESdown"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_StopToEBBQ"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_LQ_Vector"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_Signals_EESdown"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_Signals_EESup"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_Signals_EER"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_BackgroundMC"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_BackgroundMC_EESdown"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_BackgroundMC_EESup"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2015/RootNtuple-V00-03-18-SingleEleLoose_BackgroundMC_EER"

#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2014/RootNtuple-V00-03-18-SingleEleLoose_AddMETs_ENuJJ_JESdown"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2013/RootNtuple-V00-03-18-EGammaMediumID_LegacyNTupleVersion"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2013/RootNtuple-V00-03-18-Summer12MC_StopToEBBQ_LegacyNTupleVersion_JESdown"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2013/RootNtuple-V00-03-11-Summer12MC_DY4JetsToLL_ScaleMatchingSysts_MG/"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2013/RootNtuple-V00-03-11-Summer12MC_W4JetsToLNu_ScaleMatchingSysts_MG/"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2013/RootNtuple-V00-03-11-Summer12MC_TTBar_Systs_MG/"
#------------
CODENAME=analysisClass_lq1_skim_orig
#------------
#------------
INPUTLIST=config/FullNtupleDatasets_Summer12MC_LQ_Vector_LegacyNTupleVersion/inputListOnlyBetaOneYM500.txt
#INPUTLIST=config/FullNtupleDatasets_Summer12MC_StopToEBBQ/inputListAllCurrent.txt
#INPUTLIST=config/FullNtupleDatasets_Summer12MC_LQ_Vector_LegacyNTupleVersion/inputListAllCurrent.txt
#INPUTLIST=config/FullNtupleDatasets/inputListAllCurrent_BackgroundMC.txt
#INPUTLIST=config/FullNtupleDatasets/inputListAllCurrent_allSignals.txt
#INPUTLIST=config/FullNtupleDatasets_Summer12MC_V00-03-18_ENuJJSignal/inputListAllCurrent.txt
#INPUTLIST=config/FullNtupleDatasets/inputListAllCurrent_ElectronID.txt
#INPUTLIST=config/FullNtupleDatasets_Summer12MC_StopToEBBQ/inputListAllCurrent.txt
#INPUTLIST=config/FullNtupleDatasets_Summer12MC_LQ_Vector_LegacyNTupleVersion/inputListOnlyBetaOneYM600.txt
#INPUTLIST=config/FullNtupleDatasets_Summer12MC_LQ_Vector_LegacyNTupleVersion/inputListAllCurrent.txt
#INPUTLIST=config/FullNtupleDatasets_Summer12MC_TTBar_Systematics_MG/inputListAllCurrent.txt
#INPUTLIST=config/FullNtupleDatasets_Summer12MC_W4JetsToLNu_ScaleMatchingSysts_MG/inputListAllCurrent.txt
#INPUTLIST=config/FullNtupleDatasets_Summer12MC_DY4JetsToLL_ScaleMatchingSysts_MG/inputListAllCurrent.txt
#------------
NJOBS=20 #number of jobs for each dataset - for PhysicsDST
WAIT=0 #seconds of delay between submission of different datasets
#------------
QUEUE=8nh #bsub queue  
#------------
#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_nominal_LQVector_BetaOneYM500_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_EESdown_LQVector_BetaOneYM500_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_EESup_LQVector_BetaOneYM500_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_EER_LQVector_BetaOneYM500_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_EESdown_LQVector_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_EESup_LQVector_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_EER_LQVector_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_EER_StopToEBBQ_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_EESup_StopToEBBQ_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_EESdown_StopToEBBQ_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_nominal_StopToEBBQ_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_nominal_LQVector_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_nominal_signals_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_nominal_backgroundMC_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_EESdown_signals_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
echo "" > $COMMANDFILE

for file in $files
do
suffix=`basename $file`
suffix=${suffix%\.*}
cat >> $COMMANDFILE <<EOF

####################################################
#### launch, check and combine cmds for $suffix ####

  ./scripts/launchAnalysis_batch_ForSkimToEOS.py \
    -i $INPUTLIST \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -j $NJOBS \
    -q $QUEUE \
    -w $WAIT \
    -d $FULLEOSDIR \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/launch_${suffix}.log


#### THEN

  ./scripts/check_combine_output_batch_ForSkimToEOS.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -q $QUEUE \
    -s $FULLEOSDIR \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/checkcombine_${suffix}.log

EOF
done


echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to $COMMANDFILE"
