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
files=`ls $LQMACRO/config2012/MakeFlatNtupleSkims/cutTable_lq_eejjPreselection_skim.txt`
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
#------------
SUBDIR="lq_skim_2013/RootNtuple-V00-03-13-EEJJReducedSkim_DYJets_MGSysts/"
#SUBDIR="lq_skim_2012/RootNtuple-V00-03-11-EEJJReducedSkim_New/"
# SUBDIR="lq_skim_2012/RootNtuple-V00-03-07-Summer12MC_DY0JetsToLL_MG"
         # output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
         # it is suggested to specify the luminosity in the name of the directory
#------------
FULLEOSDIR="/eos/cms/store/user/scooper/LQ/Skims_2013/RootNtuple-V00-03-13-EEJJReducedSkim_DYJets_MGSysts"
# FULLEOSDIR="/eos/cms/store/user/eberry/LQ/Skims_2012/RootNtuple-V00-03-11-EEJJReducedSkim/"
#FULLEOSDIR="/eos/cms/store/user/eberry/LQ/Skims_2012/RootNtuple-V00-03-11-EEJJReducedSkim-New/"
# FULLEOSDIR="/eos/cms/store/group/phys_exotica/leptonsPlusJets/RootNtuple_skim/eberry/RootNtuple-V00-03-09-Summer12MC_DY0JetsToLL_MG"
#------------
CODENAME=analysisClass_eejj_preselection_skim
#------------
# INPUTLIST=inputListAll.txt
#INPUTLIST=config/FlatNtuple_OneOrMoreTightEle_Pt35/inputListAllCurrent.txt
INPUTLIST=config/CombinedDYJetsMGSystsMiniSkimDatasets/inputListAllCurrent.txt
#------------
NJOBS=50 #number of jobs for each dataset - for PhysicsDST
WAIT=0 #seconds of delay between submission of different datasets
#------------
QUEUE=1nh #bsub queue  
#------------
#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_MakeEEJJReducedSkim_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
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
