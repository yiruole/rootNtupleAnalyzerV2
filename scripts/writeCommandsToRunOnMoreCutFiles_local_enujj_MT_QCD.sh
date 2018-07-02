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
# QCD FR
files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_enujj_MT_QCD.txt"
# QCD FR -- presel only
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_enujj_MT_QCD_preselOnly.txt"
# QCD FR -- MET100, presel only
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_enujj_MT_QCD_preselOnly_MET100.txt"
# opt
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Optimization/cutTable_lq_enujj_MT_QCD_opt.txt"
#
# QCD closure test, 1 jet, observed; need to manually set FR to 1.0 in analysis class!
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/QCDFakeRate/cutTable_lq_enujj_MT_QCD_presel_1j_closure.txt"
# QCD closure test, 1 jet, predicted
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/QCDFakeRate/cutTable_lq_enujj_MT_QCD_presel_1j_predicted.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_enujj_MT_QCD_preselOnly_fakeRateETHLTNoSt.txt
#       /afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_enujj_MT_QCD_preselOnly_fakeRateETHLTWithStMET.txt"
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=2016qcd/enujj_apr3_lq650from2012/
#SUBDIR=2016qcd/enujj_mar26_addMTPlots
#SUBDIR=2016qcd/enujj_mar20_addPlots
#SUBDIR=2016qcd/enujj_mar16_fixMuons
#SUBDIR=2016qcd/enujj_feb27_addMoreFinalSelPlots_2
#SUBDIR=2016qcd/enujj_feb27_addMoreFinalSelPlots
#SUBDIR=2016qcd/enujj_feb14_dPhiEleMET0p8
#SUBDIR=2016qcd/enujj_feb10_addPlot
#SUBDIR=2016qcd/enujj_feb10_bugfix
#SUBDIR=2016qcd/enujj_newRsk237_feb7_gsfEtaCheck_MET100_PtEMET70_addHists
#SUBDIR=2016qcd/enujj_newRsk237_feb5_gsfEtaCheck_MET100_PtEMET70_prevCutHists
#SUBDIR=2016qcd/enujj_newRsk237_feb4_gsfEtaCheck_MET100_PtEMET70
#SUBDIR=2016qcd/enujj_newRsk237_feb2_gsfEtaCheck_MET100_addPlots
#SUBDIR=2016qcd/enujj_newRsk237_jan26_gsfEtaCheck_finalSels
#SUBDIR=2016qcd/enujj_newRsk237_jan24_gsfEtaCheck_preselOnly
#SUBDIR=2016qcd/enujj_newRsk237_jan20_finalSels
#SUBDIR=2016qcd/enujj_newRsk237_jan17_preselOnly
#SUBDIR=2016qcd/enujj_jan12_1jetClosureTest_observed
#SUBDIR=2016qcd/enujj_jan12_1jetClosureTest_predicted
#SUBDIR=2016qcd/enujj_jan8_preselOnly
#SUBDIR=2016qcd/enujj_newRsk_dec20_noFR_275376_preselOnly
#SUBDIR=2016qcd/enujj_newRsk_dec18_noFR_preselOnly
#SUBDIR=2016qcd/enujj_newRsk_dec13_preselOnly
#SUBDIR=2016qcd/enujj_newRsk_dec10_withAndWithoutSt_preselOnly
#SUBDIR=2016qcd/enujj_newRsk_dec5_skim_preselOnly
#SUBDIR=2016qcd/enujj_newRsk_nov17_highMejPlots_preselOnly
#SUBDIR=2016qcd/enujj_newRsk_nov17_noDeltaPhiNoMT_preselOnly
#SUBDIR=2016qcd/enujj_newRsk_nov16_addDiElectronPlot_preselOnly
#SUBDIR=2016qcd/enujj_newRsk_nov15_attemptMjjControlRegions_preselOnly
#SUBDIR=2016qcd/enujj_rsk_nov14_attemptMjjControlRegions_preselOnly
#SUBDIR=2016qcd/enujj_rsk_nov10_failHEEP_updateFRSCEt_preselOnly
#SUBDIR=2016qcd/enujj_rsk_nov8_failHEEP_updateFRSCEtAndOct21QCDRSK
#SUBDIR=2016qcd/enujj_rsk_nov7_ignoreHEEPnoFR_updateFRSCEtAndOct21QCDRSK
#SUBDIR=2016qcd/enujj_rsk_nov7_failHEEPnoFR_updateFRSCEtAndOct21QCDRSK
#SUBDIR=2016qcd/enujj_rsk_nov6_failHEEPupdateFRrSCEtAndOct21QCDRSK
#SUBDIR=2016qcd/enujj_rsk_oct31_updateFRSCEtAndOct21QCDRSK
#SUBDIR=2016qcd/enujj_rsk_oct28_updateFRAndOct21QCDRSK_noMuonReq
#SUBDIR=2016qcd/enujj_psk_oct24_updateFRAndOct21QCDRSK_updatedFinalSels
#SUBDIR=2016qcd/enujj_psk_oct23_updateFR_updatedFinalSels
#SUBDIR=2016qcd/enujj_psk_oct19_reminiAODFR_updatedFinalSels
#SUBDIR=2016qcd/enujj_psk_oct18_mejEtaPlots_updatedFinalSels
#SUBDIR=2016qcd/enujj_psk_oct16_newFR_updatedFinalSels
#SUBDIR=2016qcd/enujj_psk_oct15_extendMTRange_updatedFinalSels
#SUBDIR=2016qcd/enujj_psk_oct8_updatedFinalSels
#SUBDIR=2016qcd/enujj_psk_oct6_updateFinalSels
#SUBDIR=2016qcd/enujj_psk_oct2_btags__enujjOptFinalSels
#SUBDIR=2016qcd/enujj_psk_jul1_ele27wptightOREle115ORPhoton175_enujjOptFinalSels
#SUBDIR=2016qcd/enujj_psk_jun1_ele27wptightOREle115ORPhoton175
#SUBDIR=2016qcd/enujj_psk_may23_ele27wptightOREle115
#SUBDIR=2016qcd/enujj_psk_feb28_recoHeepSF_rereco_stitchDYW_ele27wptightEta2p1CurveMC

#SUBDIR=2016opt/enujj_QCD_jan19
#SUBDIR=2016opt/enujj_QCD_psk_oct16_newFR
#SUBDIR=2016opt/qcd_enujj_psk_jun1_ele27wptightOREle115ORPhoton175
#SUBDIR=2016opt/enujj_psk_may23_ele27wptightOREle115
#SUBDIR=2016opt/qcd_enujj_apr11

#SUBDIR=2016analysis/enujj_2016FR_QCD_mar3_rereco_enujj2012FinSels
#SUBDIR=2016analysis/enujj_psk_QCD_feb27_rereco_enujj2012FinSels
# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=35867 # [was 36455] ntupleV235 2016B-H rereco runs # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
#ILUM=12900 # ICHEP2016
#ILUM=6910 # ICHEP2016 remove early runs
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
#EXE=main
#EXE=mainENUJJqcd
EXE=mainENUJJqcd_650only
CODENAME=analysisClass_lq_enujj_QCD
#------------
INPUTLIST=config/RSK_QCD_mar16_v237_local/inputList_data.txt
#INPUTLIST=config/RSK_QCD_jan21_v237_eoscms/inputListAllCurrent.txt
#INPUTLIST=config/RSK_QCD_jan12_v237_eoscms_comb/inputListAllCurrent.txt
#INPUTLIST=config/RSK_QCD_jan6_v236_eoscms_comb/inputListAllCurrent.txt
#INPUTLIST=config/RSK_QCD_nov14_tuplev236_eoscms_comb/inputList_MC.txt
#INPUTLIST=config/RSK_QCD_nov14_tuplev236_eoscms_comb/inputList_singlePhoton.txt
#INPUTLIST=config/RSK_QCD_nov14_tuplev236_eoscms_comb/inputListAllCurrent.txt
#INPUTLIST=config/RSK_QCD_nov5_v236_eoscms_comb/inputList_singlePhoton.txt
#INPUTLIST=config/RSK_QCD_oct21_v236_eoscms/inputList_singlePhoton.txt#INPUTLIST=config/RSK_QCD_sep13_v236_eoscms/inputList_singlePhoton.txt
#INPUTLIST=config/RSK_QCD_sep13_v236_eoscms/inputList_singlePhoton.txt
#INPUTLIST=config/RSK_QCD_reminiAOD_v236/inputList_singlePhoton.txt

#INPUTLIST=config/RSK_QCD_rereco_v235/inputListAllCurrent.txt
#INPUTLIST=config/PSK_QCD_rereco_v233_heep7_enujj/inputListAllCurrent.txt
#------------
XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
#XSECTION=config/xsection_13TeV_2015_Zrescale.txt #first try at Z rescale
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_QCD_dataDriven.txt
#------------
#NCORES=8 #Number of processor cores to be used to run the job
NCORES=20 #Number of processor cores to be used to run the job
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_QCD_local_`hostname -s`.txt
#COMMANDFILE=commandsToRunOnMoreCutFiles_enujj_QCD_opt_local_`hostname -s`.txt
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
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combinePlots_${suffix}.log

EOF
done


echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to $COMMANDFILE"
