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
files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/TTbarBkg/cutTable_lq_ttbar_emujj_correctTrig.txt"
# opt
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Optimization/cutTable_lq_ttbar_emujj_correctTrig_opt.txt"

#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
#SUBDIR=2016opt/may30_ttbarBkg_emujj
#SUBDIR=2016opt/may22_ttbarBkg_emujj
#SUBDIR=2016opt/mar5_ttbarBkg_emujj
#SUBDIR=2016opt/oct2_emujj_ptEE_eejjOptFinalSels

#SUBDIR=2016opt/nov19_emujj_ttbar
#SUBDIR=2016ttbar/nov19_emujj
#SUBDIR=2016ttbar/feb2_newSkim_emujj_correctTrig_finalSelections

SUBDIR=2016ttbar/apr3_emujj_lq650from2012/
#SUBDIR=2016ttbar/mar20_emujj_extraSFForSyst
#SUBDIR=2016ttbar/mar20_emujj_fixPlots
#SUBDIR=2016ttbar/mar17_emujj_fixMuons
#SUBDIR=2016ttbar/mar2_emujj_FixReeEmu_applyRTrig_newSingleTop
#SUBDIR=2016ttbar/mar1_emujj_RedoRTrig
#SUBDIR=2016ttbar/mar1_emujj_noRTrig_twoObjectTrigEval
#SUBDIR=2016ttbar/feb28_emujj_noRTrigReproduceOld_correctTrig
#SUBDIR=2016ttbar/feb28_emujj_RTrigBugFix_correctTrig
#SUBDIR=2016ttbar/feb13_emujj_newScaleFactors_correctTrig
#SUBDIR=2016ttbar/feb11_emujj_correctTrig
#SUBDIR=2016ttbar/feb7_newSkim_emujj_correctTrig_addHists
#SUBDIR=2016ttbar/feb5_newSkim_emujj_correctTrig_prevCutHists
#SUBDIR=2016opt/feb5_newSkim_emujj_correctTrig_logHighEle1PtEvents
#SUBDIR=2016opt/feb2_newSkim_emujj_correctTrig
#SUBDIR=2016opt/feb1_emujj_ttbar_newSkim_logHighEle1PtEvents
#SUBDIR=2016ttbar/jan31_emujj_correctTrig_finalSelections
#SUBDIR=2016ttbar/jan20_emujj_correctTrig_finalSelections
#SUBDIR=2016ttbar/jan19_emujj_correctTrig_finalSelections
#SUBDIR=2016ttbar/jan24_emujj_correctTrig
#SUBDIR=RunII/ttbarBkg_emujj_stScaleFactorPlots_1aug2016
#SUBDIR=RunII/ttbarBkg_emujj_stScaleFactorPlots_14jul2016
#SUBDIR=RunII/ttbarBkg_emujj_3jul2016
# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=35867 # [was 36455] ntupleV235 2016B-H rereco runs # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
#ILUM=12900 # ICHEP2016
#ILUM=6910 # ICHEP2016 minus early runs
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
#EXE=mainEEJJttbarSyst
#EXE=mainEEJJttbar
EXE=mainEEJJttbar_650only
CODENAME=analysisClass_lq_ttbarEst
#------------
INPUTLIST=config/TTbarSk_mar16_v237_local_comb/inputListAllCurrent.txt
#INPUTLIST=config/TTbarSk_mar16_v237_local_comb/inputList_newSingleTop.txt
#INPUTLIST=config/TTBarSkim_feb1_SEleL_v237_eoscms_comb/inputListAllCurrent.txt
#INPUTLIST=config/TTBarSkim_feb1_SEleL_v237_eoscms_comb/inputList_data.txt
#INPUTLIST=config/TTBarSkim_jan25_SEleL_v237_eoscms_comb/inputList_data.txt
#INPUTLIST=config/TTBarSkim_jan25_SEleL_v237_eoscms_comb/inputListAllCurrent.txt

#INPUTLIST=config/TTBarSkim_nov16_tuplev236_comb_eoscms/inputListAllCurrent.txt
#------------
XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
#XSECTION=config/xsection_13TeV_2015eejj_DYrescale.txt
#XSECTION=versionsOfAnalysis_eejj/1jun_ttbarRescale/xsection_13TeV_2015_TTbarRescale.txt # with ttbar rescaling
#XSECTION=config/xsection_13TeV_2015_Zrescale.txt #first try at Z rescale
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_ttbarBkg_emujj.txt
#SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_ttbarMC.txt
#SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_eejj.txt
#SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_eejj_QCD.txt
#------------
#NCORES=8 #Number of processor cores to be used to run the job
NCORES=24 #Number of processor cores to be used to run the job
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_ttbarBkg_emujj_local_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_ttbarBkg_emujj_opt_local_`hostname -s`.txt
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
    -k $CODENAME \
    -i $INPUTLIST \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -p $NCORES \
    -k $CODENAME \
    >& launch_${suffix}_`hostname -s`.log

mv launch_${suffix}_`hostname -s`.log $OUTDIRPATH/$SUBDIR/output_$suffix/

time  ./scripts/combinePlots.py \
    -b \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l  `echo "$ILUM*$FACTOR" | bc` \
    -x $XSECTION  \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s $SAMPLELISTFORMERGING \
    -f $OUTDIRPATH/$SUBDIR/output_$suffix/launch_${suffix}_`hostname -s`.log \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}.log

EOF
done


echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to $COMMANDFILE"
