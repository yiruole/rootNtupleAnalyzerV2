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
files="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_QCD.txt"
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_QCD.txt"
# analysis -- preselection only
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Analysis/cutTable_lq_eejj_QCD_preselOnly.txt"
# opt
#files="/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/Optimization/cutTable_lq_eejj_QCD_opt.txt"
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
SUBDIR=nano/2016/analysis/eejj_qcd_rsk_oct24
#SUBDIR=nano/2016/analysis/eejj_qcd_rsk_aug29
#SUBDIR=2016opt/eejj_QCD_psk_nov27_finalSels_muonVeto35GeV_nEleGte2
#SUBDIR=2016opt/eejj_QCD_psk_nov27_finalSels_muonVeto35GeV_nEleGte2
#SUBDIR=2016qcd/eejj_psk_nov27_finalSels_muonVeto35GeV_nEleGte2
#SUBDIR=2016qcd/eejj_psk_nov19_finalSels_noMuonVeto_nEleGte2
#SUBDIR=2016qcd/eejj_psk_nov16_newFRFailHEEP_eta2p5_preselOnly/
#SUBDIR=2016qcd/eejj_psk_nov10_newFRFailHEEP_eta2p5_preselOnly/
#SUBDIR=2016qcd/eejj_rsk_nov6_newFRFailHEEP_eta2p5_ptEECut/
#SUBDIR=2016qcd/eejj_psk_oct28_newFR_ptEECut_noMuonReq/
#SUBDIR=2016qcd/eejj_psk_oct26_newFR_ptEECut_noMuonReq/
#SUBDIR=2016qcd/eejj_psk_oct16_newFR_ptEECut_actualUpdateFinalSels/
#SUBDIR=2016qcd/eejj_psk_oct6_ptEECut_actualUpdateFinalSels/
#SUBDIR=2016qcd/eejj_QCD_psk_oct6_ptEECut_updateFinalSels/
#SUBDIR=2016analysis/eejj_QCD_psk_sep29_ptEECut/
#SUBDIR=2016analysis/eejj_QCD_psk_jul1_ele27wptightOREle115ORPhoton175_eejjOptFinalSels/
#SUBDIR=2016analysis/eejj_QCD_psk_may29_ele27wptightOREle115ORPhoton175_eejjOptFinalSels/
#SUBDIR=2016analysis/eejj_QCD_psk_may22_ele27wptightOREle115_eejjOptFinalSels/
#SUBDIR=2016analysis/eejj_QCD_psk_apr11_ele27wptightOREle115_eejjOptFinalSels/
#SUBDIR=2016analysis/eejj_QCD_psk_apr4_ele27wptightEta2p1Data2016CurveMC_eejjOptFinalSels/
#SUBDIR=2016analysis/eejj_QCD_jan19_finalSels/
#SUBDIR=2016analysis/eejj_QCD_jan20_finalSels/
#SUBDIR=2016qcd/eejj_QCD_jan24_gsfEtaCheck_preselOnly/
#SUBDIR=2016qcd/eejj_QCD_jan26_gsfEtaCheck_finalSels/
#SUBDIR=2016qcd/eejj_QCD_feb5_gsfEtaCheck_finalSels_preCutHists/
#SUBDIR=2016qcd/eejj_QCD_feb7_gsfEtaCheck_finalSels_addHists/
#SUBDIR=2016qcd/eejj_QCD_feb10_bugfix/
#SUBDIR=2016qcd/eejj_QCD_feb13_addPlot/
#SUBDIR=2016qcd/eejj_QCD_mar16_fixMuons/
#SUBDIR=2016qcd/eejj_QCD_mar20_fixPlots/
#SUBDIR=2016qcd/eejj_apr3_lq650from2012/

#SUBDIR=2016opt/eejj_QCD_psk_oct16_newFR_ptEECut/
#SUBDIR=2016opt/eejj_QCD_psk_oct4_ptEECut/
#SUBDIR=2016opt/qcd_eejj_may29_ele27wptightOrEle115OrPhoton175
#SUBDIR=2016opt/qcd_eejj_may22_ele27wptightOrEle115
#SUBDIR=2016opt/qcd_eejj_apr13_ele27wptightOrEle115
#SUBDIR=2016opt/qcd_eejj_psk_mar30_recoHeepSFs_reminiAOD_ele27wptightEta2p1Data2016CurveMC_eejj2015FinalSels
#SUBDIR=2016qcd/eejj_psk_mar26_recoHeepSFs_reMiniAOD_ele27wptightEta2p1Data2016CurveMC_eejj2015FinalSels
#SUBDIR=2016opt/eejj_mar5_2015FR_QCD_jan24_rereco_opt/
#SUBDIR=2016analysis/mar3_2016FR_QCD_jan24_rereco/
#SUBDIR=2016analysis/feb22_onPsk_QCD_jan24_rereco/
# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=35867 # [was 36455] ntupleV235 2016B-H rereco runs # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
#ILUM=12900 # ICHEP2016
#ILUM=6910 # ICHEP2016 minus early runs
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
EXE=main
#EXE=mainEEJJqcd
#EXE=mainEEJJqcd_650only
CODENAME=analysisClass_lq_eejj_QCD
#------------
INPUTLIST=config/2016_rskQCD_eosuser_comb/inputListAllCurrent.txt
#INPUTLIST=config/2016_rskQCD_custom2016skimSinglePhotonJSON_eosuser/inputListAllCurrent.txt
#INPUTLIST=config/RSK_QCD_mar16_v237_local/inputList_data.txt
#INPUTLIST=config/RSK_QCD_jan21_v237_eoscms/inputListAllCurrent.txt
#INPUTLIST=config/RSK_QCD_nov14_tuplev236_eoscms_comb/inputListAllCurrent.txt
#INPUTLIST=config/RSK_QCD_nov5_v236_eoscms_comb/inputList_singlePhoton.txt
#INPUTLIST=config/RSK_QCD_oct21_v236_eoscms/inputList_singlePhoton.txt
#INPUTLIST=config/RSK_QCD_sep13_v236_eoscms/inputList_singlePhoton.txt
#INPUTLIST=config/RSK_QCD_reminiAOD_v236/inputList_singlePhoton.txt
#INPUTLIST=config/RSK_QCD_rereco_v235/inputListAllCurrent.txt
#INPUTLIST=config/PSK_QCD_rereco_v233_heep7_eejj/inputListAllCurrent.txt
#------------
XSECTION=config/xsection_13TeV_2015.txt #specify cross section file
#XSECTION=config/xsection_13TeV_2015_Zrescale.txt #first try at Z rescale
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_QCD_dataDriven.txt
#------------
#NCORES=8 #Number of processor cores to be used to run the job
NCORES=10 #Number of processor cores to be used to run the job
#------------

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_analysis_QCD_local_`hostname -s`.txt
# opt
#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_optimization_QCD_local_`hostname -s`.txt

#COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_optimization_local_`hostname -s`.txt
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
    -k $CODENAME \
    -e $EXE \
    -i $INPUTLIST \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -p $NCORES \
    -k $CODENAME \
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
