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
#files=`ls $LQMACRO/config2012/Analysis/cutTable_lq_eejj.txt`
#files=`ls $LQMACRO/config2012/Systematics/cutTable_lq_eejj_Systematics_PUdown.txt`
#files=`ls $LQMACRO/config2012/Analysis/cutTable_lq_eejj.txt`
#files=`ls $LQMACRO/config2012/Analysis/cutTable_lq_eejj_noEEMassCut.txt`
#files=`ls $LQMACRO/config2012/MakeFlatNtupleSkims/cutTable_lq_eejjPreselection_skim.txt`
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR="lq_skim_2014/RootNtuple-V00-03-18-Summer12MC_StopToEBBQ_LegacyNTupleVersion_eejjPreselSkim_JESup"
#SUBDIR=StopToEBBQ_analysis/LegacyNTupleVersion_PUdown
#SUBDIR=EGammaMediumID_eejj_analysis/
#SUBDIR=lq_microSkims/DY2JetsToLL_ScaleSysts/
#SUBDIR=lq_microSkims/DY3JetsToLL_ScaleSysts/
#SUBDIR=eejj_analysis/DY2JetsToLL_ScaleSysts/
#SUBDIR=eejj_analysis/DY3JetsToLL_ScaleSysts/
#SUBDIR=eejj_analysis/TTBar_Systs/
#SUBDIR=eejj_analysis/DY4JetsToLL_ScaleMatchingSysts/
#SUBDIR=eejj_analysis/CombinedDY4JetsToLL_MGSysts/
#SUBDIR=eejj_analysis/NoEEMassCut_CombinedDY4JetsToLL_MGSysts/
         # output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
         # it is suggested to specify the luminosity in the name of the directory
#------------
CODENAME=analysisClass_eejj_preselection_skim
#------------
INPUTLIST=config/FlatNtupleDatasets_RootNtuple-V00-03-18-Summer12MC_StopToEBBQ_LegacyNTupleVersion_JESup/inputListAllCurrent.txt
#INPUTLIST=config/PreselectionSkimDataSets_RootNtuple-V00-03-18-EGammaMediumIDLegacyNTupleVersion_eejj/inputListAllCurrent.txt
#INPUTLIST=config/PreselectionSkimDataSets_RootNtuple-V00-03-18-Summer12MC_StopToEBBQ_LegacyNTupleVersion_eejj/inputListAllCurrent.txt
#INPUTLIST=config/PreselectionSkimDataSets_RootNtuple-V00-03-18-Summer12MC_LQ_Vector_LegacyNTupleVersion_eejj/inputListAllCurrent.txt
#INPUTLIST=config/FlatNtuple_EEJJ_Preselection/inputListAllCurrent.txt
#INPUTLIST=config/MiniSkimDatasets_Summer12MC_DY2JetsToLL_ScaleSysts_MG/inputListAllCurrent.txt
#INPUTLIST=config/MiniSkimDatasets_Summer12MC_DY3JetsToLL_ScaleSysts_MG/inputListAllCurrent.txt
#INPUTLIST=config/MiniSkimDatasets_Summer12MC_TTBar_Systs_MG/inputListAllCurrent.txt
#INPUTLIST=config/MiniSkimDatasets_Summer12MC_DY4JetsToLL_ScaleMatchingSysts_MG/inputListAllCurrent.txt
#INPUTLIST=config/MicroSkimDatasets_Summer12MC_DYJetsToLL_ScaleMatchingSysts_MG/inputListAllCurrent.txt
#------------
XSECTION=config/xsection_8TeV_2012.txt #specify cross section file
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_8TeV_eejj.txt
#------------
NCORES=8 #Number of processor cores to be used to run the job
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_StopToEBBQ_MakeEEJJPreselectionSkim_JESup_local.txt
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
    | tee launch_${suffix}.log 

mv launch_${suffix}.log $OUTDIRPATH/$SUBDIR/output_$suffix/

#time  ./scripts/combineTablesTemplate.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l  `echo "$ILUM*$FACTOR" | bc` \
    -x $XSECTION  \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s $SAMPLELISTFORMERGING \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTables_${suffix}.log

#time  ./scripts/combinePlotsTemplate.py \
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
