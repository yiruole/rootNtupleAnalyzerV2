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
# analysis with final sels
files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_enujj_MT.txt"
# analysis with preselection only
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_enujj_MT_preselOnly.txt"
# MET 100, presel only
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_enujj_MT_preselOnly_MET100.txt"
# opt
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Optimization/cutTable_lq_enujj_MT_opt.txt"
#
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=2016analysis/enujj_psk_apr3_lq650from2012
#SUBDIR=2016analysis/enujj_psk_mar26_addMTPlots
#SUBDIR=2016analysis/enujj_psk_mar26_muonVetoUncert
#SUBDIR=2016analysis/enujj_psk_mar23_highMetMTDataInfo
#SUBDIR=2016analysis/enujj_psk_mar22_muonVetoUncert
#SUBDIR=2016analysis/enujj_psk_mar20_addPlots
#SUBDIR=2016analysis/enujj_psk_mar16_fixMuons
#SUBDIR=2016analysis/enujj_RSK_mar5_forCutFlow
#SUBDIR=2016analysis/enujj_psk_mar5_removeTopPtReweight
#SUBDIR=2016analysis/enujj_psk_feb27_dPhiEleMet0p8_fixMETPlot
#SUBDIR=2016analysis/enujj_psk_feb23_dPhiEleMet0p8_fixMTPlots
#SUBDIR=2016analysis/enujj_psk_feb20_dPhiEleMet0p8_newSingTop
#SUBDIR=2016analysis/enujj_psk_feb19_dPhiEleMet0p8_btagSysts
#SUBDIR=2016analysis/enujj_psk_feb14_dPhiEleMet0p8
#SUBDIR=2016analysis/enujj_psk_feb12_v237_fixPlot
#SUBDIR=2016analysis/enujj_psk_feb10_v237_bugfix
#SUBDIR=2016analysis/enujj_psk_feb7_v237_MET100_PtEMET70_addHists
#SUBDIR=2016analysis/enujj_psk_feb4_v237_MET100_PtEMET70_prevCutHists
#SUBDIR=2016analysis/enujj_psk_feb4_v237_MET100_PtEMET70
#SUBDIR=2016analysis/enujj_psk_feb2_v237_MET100_addMTPlots
#SUBDIR=2016analysis/enujj_psk_jan26_v237_finalSels
#SUBDIR=2016analysis/enujj_psk_jan24_v237_preselOnly
#SUBDIR=2016analysis/enujj_psk_jan20_usePtHeep_finalSels
#SUBDIR=2016analysis/enujj_psk_dec13_fixTrigEff_usePtHeep_preselOnly
#SUBDIR=2016analysis/enujj_psk_dec5_fixTrigEff_usePtHeep_eventListData_preselOnly
#SUBDIR=2016analysis/enujj_psk_nov22_fixTrigEff_usePtHeep_preselOnly
#SUBDIR=2016analysis/enujj_psk_nov17_highMejPlots_preselOnly
#SUBDIR=2016analysis/enujj_psk_nov17_newTrigEff_preselOnly
#SUBDIR=2016analysis/enujj_psk_nov16_addDiElectronPlot_preselOnly
#SUBDIR=2016analysis/enujj_psk_nov14_attemptMjjControlRegions_preselOnly
#SUBDIR=2016analysis/enujj_psk_nov12_addGenEleNuPlot
#SUBDIR=2016analysis/enujj_psk_nov10_reprodNominal
#SUBDIR=2016analysis/enujj_rsk_nov7_noMuonReq
#SUBDIR=2016analysis/enujj_psk_oct31_addSCEtPlots_updatedFinalSels
#SUBDIR=2016analysis/enujj_rsk_oct28_noMuonReq
#SUBDIR=2016analysis/enujj_psk_oct18_mejEtaPlots_updatedFinalSels
#SUBDIR=2016analysis/enujj_psk_oct15_extendMTRange_updatedFinalSels
#SUBDIR=2016analysis/enujj_psk_oct8_finerBinnedTrigEff_updatedFinalSels
#SUBDIR=2016analysis/enujj_psk_oct6_finerBinnedTrigEff_updateFinalSels
#SUBDIR=2016analysis/enujj_psk_oct6_finerBinnedTrigEff_enujjPowhegOptFinalSels
#SUBDIR=2016analysis/enujj_psk_oct3_bTagFix_enujjPowhegOptFinalSels
#SUBDIR=2016analysis/enujj_psk_sep26_bTagFix_enujjPowhegOptFinalSels
#SUBDIR=2016analysis/enujj_psk_sep13_ele27wptightOREle115ORPhoton175_enujjPowhegOptFinalSels
#SUBDIR=2016analysis/enujj_psk_jul4_ele27wptightOREle115ORPhoton175_enujjOptFinalSels
#SUBDIR=2016analysis/enujj_psk_jul1_ele27wptightOREle115ORPhoton175_enujjOptFinalSels
#SUBDIR=2016analysis/enujj_psk_jun1_ele27wptightOREle115ORPhoton175_enujj2012FinSels
#SUBDIR=2016analysis/enujj_psk_may23_ele27wptightOREle115_enujj2012FinSels
#SUBDIR=2016analysis/enujj_psk_may14_ele27wptight_enujj2012FinSels
#SUBDIR=2016analysis/enujj_psk_may11_ele27wptight_enujj2012FinSels
#SUBDIR=2016analysis/enujj_psk_may10_ele27wptightEta2p1_enujj2012FinSels
#SUBDIR=2016analysis/enujj_psk_may8_ele27wptightOREle115_enujj2012FinSels

#SUBDIR=2016opt/enujj_psk_jan19
#SUBDIR=2016opt/enujj_psk_oct6
#SUBDIR=2016opt/enujj_psk_jun1_reminiAOD_ele27wptightOREle115ORPhoton175
#SUBDIR=2016opt/enujj_psk_mar30_topPtWeight_recoHeepSF_reminiAOD_sele27wptightEta2p1CurveMC
#SUBDIR=2016analysis/enujj_psk_mar30_topPtWeight_recoHeepSF_rereco_ele27wptightEta2p1CurveMC_enujj2012FinSels
#SUBDIR=2016analysis/enujj_psk_apr11_ele27wptightOREle115_enujj2012FinSels

#SUBDIR=2016opt/enujj_psk_feb28_recoHeepSF_rereco_stitchDYW_ele27wptightEta2p1CurveMC
#SUBDIR=2016analysis/enujj_psk_feb28_recoHeepSF_rereco_stitchDYW_ele27wptightEta2p1CurveMC_enujj2012FinSels

         # output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
         # it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=35867 # [was 36455] ntupleV235 2016B-H rereco runs # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
#ILUM=12900 # ICHEP2016
#ILUM=6910 # ICHEP2016 remove early runs
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
#EXE=mainENuJJ
#EXE=mainENuJJmuonVeto
#EXE=mainENuJJevtInfo
EXE=mainENuJJ_650only
CODENAME=analysisClass_lq_enujj_MT #the actual name of the code used to process the ntuples (without the suffix ".C") 
#------------
INPUTLIST=config/PSKenujj_mar26_v237_local_comb/inputListAllCurrent.txt
#INPUTLIST=config/PSKenujj_mar16_v237_local_comb/inputListAllCurrent.txt
#INPUTLIST=config/PSKenujj_mar16_v237_local_comb/inputList_newSingleTop.txt
#INPUTLIST=config/RSK_SEleL_jan21_v237_eoscms/inputList_enujj.txt
#INPUTLIST=config/PSKenujj_jan23_SEleL_v237_eoscms_comb/inputListAllCurrent.txt
#
#INPUTLIST=config/PSKenujj_jan23_SEleL_v237_eoscms_comb/inputList_newSingleTop.txt
#INPUTLIST=config/PSKenujj_nov15_SEleL_reminiaod_v236_eoscms_comb/inputList_reduced.txt
#INPUTLIST=config/PSKenujj_nov15_SEleL_reminiaod_v236_eoscms_comb/inputList_data.txt
#INPUTLIST=config/PSKenujj_nov15_SEleL_reminiaod_v236_eoscms_comb/inputListAllCurrent.txt
#INPUTLIST=config/PSKenujj_nov8_SEleL_reminiaod_v236/inputListAllCurrent.txt
#INPUTLIST=config/RSK_nov3_tuplev236_SEleL_eoscms_comb/inputListAllCurrent.txt
#INPUTLIST=config/RSK_oct2_tuplev236_SEleL_eoscms_combined/inputListAllCurrent.txt
#INPUTLIST=config/PSKenujj_oct2_SEleL_reminiaod_v236_eoscms/inputListAllCurrent.txt
#INPUTLIST=config/PSKenujj_may21_SEleL_reminiAOD_v236_eoscms/inputListAllCurrent.txt
#------------
XSECTION=$LQANA/versionsOfAnalysis_enujj/mar17/unscaled/newSingleTop/xsection_13TeV_2015_MTenu_50_110_gteOneBtaggedJet_TTbar_MTenu_50_110_noBtaggedJets_WJets.txt
#XSECTION=$LQANA/config/xsection_13TeV_2015.txt #specify cross section file
#XSECTION=$LQANA/versionsOfAnalysis_enujj/feb20/unscaled/xsection_13TeV_2015_MTenu_50_110_gteOneBtaggedJet_TTbar_MTenu_50_110_noBtaggedJets_WJets.txt
#XSECTION=$LQANA/versionsOfAnalysis_enujj/feb11/unscaled/xsection_13TeV_2015_MTenu_50_110_gteOneBtaggedJet_TTbar_MTenu_50_110_noBtaggedJets_WJets.txt
#XSECTION=$LQANA/versionsOfAnalysis_enujj/feb1_met100/unscaled/xsection_13TeV_2015_TTbarRescale_WJetsRescale.txt
#XSECTION=$LQANA/versionsOfAnalysis_enujj/jan26/unscaled/xsection_13TeV_2015_TTbarRescale_WJetsRescale.txt
#XSECTION=$LQANA/versionsOfAnalysis_enujj/jan17/unscaled/xsection_13TeV_2015_TTbarRescale_WJetsRescale.txt
#XSECTION=$LQANA/versionsOfAnalysis_enujj/nov22/unscaled/xsection_13TeV_2015_TTbarRescale_WJetsRescale.txt
#XSECTION=$LQANA/versionsOfAnalysis_enujj/nov10/unscaled/dibosonAMCAtNLO/xsection_13TeV_2015_TTbarRescale_WJetsRescale.txt
#XSECTION=$LQANA/versionsOfAnalysis_enujj/oct6_finerTrigEff/unscaled/btagCR/xsection_13TeV_2015_TTbarRescale_WJetsRescale.txt
#XSECTION=$LQANA/config/xsection_13TeV_2015enujj_WandTTbarRescaled.txt
#------------
SAMPLELISTFORMERGING=$LQANA/config/sampleListForMerging_13TeV_enujj.txt
#------------
#NCORES=8 #Number of processor cores to be used to run the job
NCORES=24
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_PSK_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_opt_local_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_MT_local_RSK_`hostname -s`.txt
echo "" > $COMMANDFILE

for file in $files
do
suffix=`basename $file`
suffix=${suffix%\.*}
cat >> $COMMANDFILE <<EOF

####################################################
#### launch, check and combine cmds for $suffix ####

time python $LQANA/scripts/launchAnalysis.py \
    -e $EXE \
    -k $CODENAME \
    -i $INPUTLIST \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -p $NCORES \
    >& launch_${suffix}_`hostname -s`.log

mv launch_${suffix}_`hostname -s`.log $OUTDIRPATH/$SUBDIR/output_$suffix/

time  $LQANA/scripts/combinePlots.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l  `echo "$ILUM*$FACTOR" | bc` \
    -x $XSECTION  \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s $SAMPLELISTFORMERGING \
    -f $OUTDIRPATH/$SUBDIR/output_$suffix/launch_${suffix}_`hostname -s`.log \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combinePlots_${suffix}.log

EOF
done


echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to $COMMANDFILE"
