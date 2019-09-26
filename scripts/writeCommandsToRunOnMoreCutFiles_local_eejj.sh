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
# analysis - FinalSels
files="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj.txt"
# analysis - Preselection only
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_preselOnly.txt"
# opt
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Optimization/cutTable_lq_eejj_opt.txt"

#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_noJets.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_loosenEleRequirements_2lowPtJets.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/LQRootTuples7414/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_eles50GeV_jets50GeV_st300GeV.txt"
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
SUBDIR=nano/2016/analysis/eejj_psk_sep20
#SUBDIR=2016analysis/eejj_psk_apr3_lq650from2012
#SUBDIR=2016analysis/eejj_psk_mar26_muonVetoSyst
#SUBDIR=2016analysis/eejj_psk_mar22_muonVetoSyst
#SUBDIR=2016analysis/eejj_psk_mar20_fixPlots
#SUBDIR=2016analysis/eejj_psk_mar16_fixMuons
#SUBDIR=2016analysis/eejj_RSK_mar5_forCutFlow
#SUBDIR=2016analysis/eejj_psk_feb20_newSingTop
#SUBDIR=2016analysis/eejj_psk_feb10_bugfix
#SUBDIR=2016analysis/eejj_psk_feb7_addHists_finalSels
#SUBDIR=2016analysis/eejj_psk_feb5_addPrevCutPlots_finalSels
#SUBDIR=2016analysis/eejj_psk_jan26_gsfEtaCheck_finalSels
#SUBDIR=2016analysis/eejj_psk_jan24_gsfEtaCheck_preselOnly
#SUBDIR=2016analysis/eejj_psk_jan20_updateFinalSels
#SUBDIR=2016analysis/eejj_psk_jan19_updateFinalSels
#SUBDIR=2016analysis/eejj_psk_sep17_ptEECut_updateFinalSels
#SUBDIR=2016analysis/eejj_psk_sep17_ptEECut_properEle27wptightOREle115ORPhoton175_eejjOptFinalSels
#SUBDIR=2016analysis/eejj_psk_oct6_ptEECut_updateFinalSels
#SUBDIR=2016analysis/eejj_psk_oct20_ptEECut_addDisplSUSY
#SUBDIR=2016analysis/eejj_psk_oct26_ptEECut_noMuonReq
#SUBDIR=2016analysis/eejj_psk_oct28_ptEECut_noMuonReq
#SUBDIR=2016analysis/eejj_rsk_nov7_ptEECut_noMuonReq
#SUBDIR=2016analysis/eejj_psk_nov10_ptEECut_redoNominalPreselOnly
#SUBDIR=2016analysis/eejj_psk_nov16_preselOnly
#SUBDIR=2016analysis/eejj_psk_nov17_finalSels
#SUBDIR=2016analysis/eejj_psk_nov17_updateTrigEff_preselOnly
#SUBDIR=2016analysis/eejj_psk_nov19_updateTrigEff_finalSels_noMuonVeto_nEleGte2
#SUBDIR=2016analysis/eejj_psk_nov22_fixTrigEff_finalSels_noMuonVeto_nEleGte2
#SUBDIR=2016analysis/eejj_psk_nov24_fixTrigEff_finalSels_muonVetoDef20GeV_nEleGte2
#SUBDIR=2016opt/eejj_psk_nov27_fixTrigEff_finalSels_muonVetoDef20GeV_nEleGte2

#SUBDIR=2016analysis/eejj_psk_sep14_dyjStitch_properEle27wptightOREle115ORPhoton175_eejjOptFinalSels
#SUBDIR=2016analysis/eejj_psk_jul4_properEle27wptightOREle115ORPhoton175_eejjOptFinalSels

#SUBDIR=2016analysis/eejj_psk_jul2_properEle27wptightOREle115ORPhoton175_eejjOptFinalSels
#SUBDIR=2016analysis/eejj_psk_jul1_properEle27wptightOREle115ORPhoton175_eejjOptFinalSels
#SUBDIR=2016analysis/eejj_psk_may30_properEle27wptightOREle115ORPhoton175_eejjBadOptFinalSels
#SUBDIR=2016analysis/eejj_psk_may29_lowWZPt_ele27wptightOREle115ORPhoton175_eejjBadOptFinalSels
#SUBDIR=2016analysis/eejj_psk_may22_lowWZPt_ele27wptightOREle115_eejjBadOptFinalSels
#SUBDIR=2016analysis/eejj_psk_may8_lowWZPt_ele27wptightOREle115_eejjBadOptFinalSels
#SUBDIR=2016analysis/eejj_psk_apr27_fixedDYW_ele27wptightOREle115_eejjOptFinalSels

#SUBDIR=2016opt/eejj_psk_oct4_ptEECut
#SUBDIR=2016opt/eejj_psk_mar30_recoHeepSFs_reminiAOD_ele27wptightEta2p1Data2016CurveMC
#SUBDIR=2016analysis/eejj_psk_apr11_ele27wptightOREle115_eejjOptFinalSels
#SUBDIR=2016analysis/eejj_psk_apr4_ele27wptightEta2p1Data2016CurveMC_eejjOptFinalSels
#SUBDIR=2016opt/eejj_mar4_recoHeepSFs_onPSK_rereco_ele27wptightEta2p1Data2016CurveMC
#SUBDIR=2016analysis/eejj_feb28_recoHeepSFs_onPSK_rereco_ele27wptightEta2p1Data2016CurveMC_eejj2015FinalSels
# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=35867 # [was 36455] ntupleV235 2016B-H rereco runs # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
#ILUM=12900 # ICHEP2016
#ILUM=6910 # ICHEP2016 minus early runs
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
EXE=main
#EXE=mainEEJJ
#EXE=mainEEJJmuonVeto
#EXE=mainEEJJ_650only
CODENAME=analysisClass_lq_eejj
#CODENAME=analysisClass_lq_eejj_opt
#CODENAME=analysisClass_lq_eejj_noJets
#CODENAME=analysisClass_lq_eejj_1Jet
#CODENAME=analysisClass_lq_eejj_preselectionOnly #the actual name of the code used to process the ntuples (without the suffix ".C") 
#CODENAME=analysisClass_lq1_effiStudy
#------------
INPUTLIST=config/2016_pskEEJJPresel_custom2016skimAll_eoscms_comb/inputListAllCurrent.txt
#INPUTLIST=config/2016_pskEEJJ_eoscms_comb/inputListAllCurrent.txt
#INPUTLIST=config/PSKeejj_mar26_v237_local_comb/inputListAllCurrent.txt
#INPUTLIST=config/PSKeejj_mar16_v237_local_comb/inputListAllCurrent.txt
#INPUTLIST=config/PSKeejj_mar16_v237_local_comb/inputList_newSingleTop.txt
#INPUTLIST=config/RSK_SEleL_jan21_v237_eoscms/inputList_eejj.txt
#INPUTLIST=config/PSKeejj_jan22_SEleL_v237_eoscms_comb/inputListAllCurrent.txt
#
#INPUTLIST=config/PSKeejj_nov15_SEleL_reminiaod_v236_eoscms_comb/inputListAllCurrent.txt
#INPUTLIST=config/PSKeejj_nov8_SEleL_reminiaod_v236/inputListAllCurrent.txt
#INPUTLIST=config/RSK_nov3_tuplev236_SEleL_eoscms_comb/inputListAllCurrent.txt
#INPUTLIST=config/RSK_oct2_tuplev236_SEleL_eoscms_combined/inputListAllCurrent.txt
#INPUTLIST=config/PSKeejj_oct2_SEleL_reminiaod_v236_eoscms/inputListAllCurrent.txt
#INPUTLIST=config/PSKeejj_may21_SEleL_reminiAOD_v236_eoscms/inputListAllCurrent.txt

#------------
#XSECTION=versionsOfAnalysis_eejj/mar17/unscaled/newSingleTop/xsection_13TeV_2015_Mee_PAS.txt
#XSECTION=versionsOfAnalysis_eejj/jan26/unscaled/xsection_13TeV_2015_Mee_PAS.txt
#XSECTION=versionsOfAnalysis_eejj/nov24_muonVeto35GeV/unscaled/xsection_13TeV_2015_Mee_PAS.txt
#XSECTION=$LQANA/versionsOfAnalysis_eejj/sep29_ptEE/unscaled/xsection_13TeV_2015_Mee_PAS.txt
#XSECTION=config/xsection_13TeV_2015eejj_DYrescale.txt
#
XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_eejj.txt
#SAMPLELISTFORMERGING=config/sampleListForMerging_8TeV_eejj.txt
#SAMPLELISTFORMERGING=config/sampleListForMerging_8TeV_eejj_LQVector.txt ### CHANGE TO USE VECTOR LQ
#SAMPLELISTFORMERGING=config/sampleListForMerging_8TeV_eejj_rpvStop.txt ### CHANGE TO USE RPV STOP
#------------
#NCORES=8 #Number of processor cores to be used to run the job
NCORES=10 #Number of processor cores to be used to run the job
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_local_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_optimization_local_`hostname -s`.txt

#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_heep61_local_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_noJets_local_`hostname -s`.txt
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
    -k $CODENAME \
    -i $INPUTLIST \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -p $NCORES \
    >& launch_${suffix}_`hostname -s`.log

mv launch_${suffix}_`hostname -s`.log $OUTDIRPATH/$SUBDIR/output_$suffix/

time  ./scripts/combinePlots.py \
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
