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
#files=`ls $LQMACRO/config2012/MakeFlatNtupleSkims/cutTable_lq_eejjPreselection_skim.txt`
files=`ls $LQMACRO/config2012/MakeFlatNtupleSkims/cutTable_lq_enujjPreselection_skim.txt`
#files=`ls $LQMACRO/config2012/ReducedSkims/cutTable_lq1_skim_SingleEle_loose_JESup.txt`
#files=`ls $LQMACRO/config2012/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt`
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
#------------
SUBDIR="lq_skim_2014/RootNtuple-V00-03-18-EGammaMediumID_LegacyNTupleVersion_enujjPreselSkim"
#SUBDIR="lq_skim_2014/RootNtuple-V00-03-18-Summer12MC_StopToEBBQ_LegacyNTupleVersion_eejjPreselSkim_JESup"
#SUBDIR="lq_skim_2014/RootNtuple-V00-03-18-Summer12MC_LQ_Vector_LegacyNTupleVersion_eejjPreselSkim_JESup"
#SUBDIR="lq_skim_2014/RootNtuple-V00-03-18-Summer12MC_LQ_Vector_LegacyNTupleVersion_JESup"
#SUBDIR="lq_skim_2013/RootNtuple-V00-03-11-Summer12MC_DY4JetsToLL_ScaleMatchingSysts_MG"
#SUBDIR="lq_skim_2013/RootNtuple-V00-03-11-Summer12MC_W4JetsToLNu_ScaleMatchingSysts_MG"
#SUBDIR="lq_skim_2013/RootNtuple-V00-03-11-Summer12MC_TTBar_Systs_MG"
# SUBDIR="lq_skim_2012/RootNtuple-V00-03-07-Summer12MC_DY0JetsToLL_MG"
         # output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
         # it is suggested to specify the luminosity in the name of the directory
#------------
FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2013/RootNtuple-V00-03-18-EGammaMediumID_LegacyNTupleVersion_enujjPreselSkim"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2013/RootNtuple-V00-03-18-Summer12MC_LQ_Vector_LegacyNTupleVersion_JESup"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2013/RootNtuple-V00-03-11-Summer12MC_DY4JetsToLL_ScaleMatchingSysts_MG/"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2013/RootNtuple-V00-03-11-Summer12MC_W4JetsToLNu_ScaleMatchingSysts_MG/"
#FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2013/RootNtuple-V00-03-11-Summer12MC_TTBar_Systs_MG/"
#------------
CODENAME=analysisClass_eejj_preselection_skim
#------------
INPUTLIST=config/FlatNtupleDatasets_RootNtuple-V00-03-18-EGammaMediumID_LegacyNTupleVersion/inputListAllCurrent.txt
#INPUTLIST=config/FlatNtupleDatasets_RootNtuple-V00-03-18-Summer12MC_StopToEBBQ_LegacyNTupleVersion_JESup/inputListAllCurrent.txt
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

COMMANDFILE=commandsToRunOnMoreCutFiles_EGammaMediumID_MakeENuJJPreselectionSkim_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
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
