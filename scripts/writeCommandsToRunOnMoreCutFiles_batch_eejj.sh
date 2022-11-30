#!/bin/bash

# Please run this script from the rootNtupleAnalyzerV2 directory by:  
# ./scripts/writeCommandsToRunOnMoreCutFiles.sh

# This scripts creates the whole sets of commands needed to run the analysis on multiple cut files.
# The commands will be written in a text file commandsToRunOnMoreCutFiles.txt in the current directory, 
# to be used by doing cut&paste to a terminal.

# Cut Files should first be created by a script ../rootNtupleMacrosV2/config/eejj/make_eejj_cutFiles.py
# This script will then use those cut files to create the commands needed to run on them.

die () {
    echo >&2 "$@"
    exit 1
}

[ $# -gt 0 ] || die "must specify year as argument; usage: writeCommandsToRunOnMoreCutFiles_batch_eejj.sh year [doOptimization]"
YEAR=$1

if [[ "$#" -gt 1 ]]; then
  OPT=1
else
  OPT=0
fi

#### INPUTS HERE ####
#------------
#ANANAME=eejj_test_29nov2021_1jobPerDataset
#ANANAME=eejj_finalSelsPunziAddFlatMasym_3sep2021
#ANANAME=eejj_loosenMee_addMasym_addMET_10aug2021
#ANANAME=eejj_masym_9aug2021
#ANANAME=eejj_btagMed_8jul2021
#ANANAME=eejj_gteOneBtag_btagMed_9jul2021
#ANANAME=eejj_gteTwoBtags_btagLoose_9jul2021
#ANANAME=eejj_gteTwoBtags_btagMed_13jul2021
#ANANAME=eejj_opt_egLoose_18jan2022
#ANANAME=eejj_finalSels_egLoose_19jan2022
#ANANAME=eejj_finalSels_egLoose_4feb2022
#ANANAME=eejj_optBDTLQ1700_egLoose_19feb2022_10kCutPoints_moreInputs
#ANANAME=eejj_optBDTLQ1400_heepID_25feb2022
#ANANAME=eejj_BDTLQ1700parametrized1-2_egLoose_13may2022
#ANANAME=eejj_optBDTLQ1500_egLoose_21feb2022
#ANANAME=eejj_optBDTLQ1700Mee200sT400_egLoose_23feb2022
# ANANAME=eejj_optBDT_LQ1700_Mee200sT400_egLoose_6apr2022
#ANANAME=eejj_nextTry_3aug2022
#ANANAME=eejj_looseWithHeepEta_9aug2022
ANANAME=eejj_2nov2022_preselOnly_eleSFsTrigSFsLead_ele27AndPhoton175_fromPSK_meeBkgSystHist
#------------
# inputlist2016=config/nanoV7_2016_pskEEJJ_9nov2020_comb/inputListAllCurrent.txt
# inputlist2016=config/nanoV7_2016_pskEEJJ_4jan2021_comb/inputListAllCurrent.txt
# inputlist2016=config/nanoV7_2016_validation_pskEEJJ_15feb2021/inputListAllCurrent.txt
#inputlist2016=config/nanoV7_2016_pskEEJJ_25feb2021_comb/inputListAllCurrent.txt
#inputlist2016=config/nanoV7_2016_pskEEJJ_16mar2021_comb/inputListAllCurrent.txt
#inputlist2017=config/nanoV7_2017_pskEEJJ_15nov2020_comb/inputListAllCurrent.txt
#inputlist2018=config/nanoV7_2018_pskEEJJ_15nov2020_comb/inputList_dataOnly.txt
#
#inputlist2016=config/nanoV7_2016_pskEEJJ_12apr2021_comb/inputListAllCurrent.txt
#inputlist2016=config/nanoV7_2016_pskEEJJ_egLoose_22sep2021/inputListAllCurrent.txt
#inputlist2016=config/nanoV7_2016_pskEEJJ_egLoose_4feb2022/inputListAllCurrent.txt
#
inputlist2016pre=config/inputListsPSKEEJJ_UL16preVFP_19oct2022/inputListAllCurrent.txt
inputlist2016post=config/inputListsPSKEEJJ_UL16postVFP_19oct2022/inputListAllCurrent.txt
#inputlist2016pre=config/inputListsRSK_UL16preVFP_SEleL_6oct2022/inputListAllCurrent.txt
#inputlist2016post=config/inputListsRSK_UL16postVFP_SEleL_6oct2022/inputListAllCurrent.txt
#inputlist2016pre=config/inputListsTest_RSK_UL16preVFP_SEleL_30sep2022/inputListAllCurrent.txt
#inputlist2016post=config/inputListsTest_RSK_UL16postVFP_SEleL_30sep2022/inputListAllCurrent.txt
#inputlist2016pre=config/inputListsRSK_UL16preVFP_SEleL_22sep2022/inputListAllCurrent.txt
#inputlist2016post=config/inputListsRSK_UL16postVFP_SEleL_22sep2022/inputListAllCurrent.txt
#inputlist2016pre=config/inputListsRSK_UL16preVFP_SEleL_9sep2022/inputListAllCurrent.txt
#inputlist2016post=config/inputListsRSK_UL16postVFP_SEleL_9sep2022/inputListAllCurrent.txt
#inputlist2016pre=config/inputListsRSK_UL16preVFP_SEleL_29aug2022/inputListAllCurrent.txt
#inputlist2016post=config/inputListsRSK_UL16postVFP_SEleL_29aug2022/inputListAllCurrent.txt
#inputlist2016pre=config/inputListsRSK_UL16preVFP_SEleL_12aug2022/inputListAllCurrent.txt
#inputlist2016post=config/inputListsRSK_UL16postVFP_SEleL_12aug2022/inputListAllCurrent.txt
#inputlist2016pre=config/inputListsRSK_UL16preVFP_SEleL_11aug2022/inputListAllCurrent.txt  # MET smearing
#inputlist2016post=config/inputListsRSK_UL16postVFP_SEleL_11aug2022/inputListAllCurrent.txt  # MET smearing
#inputlist2016pre=config/inputListsPSK_UL16preVFP_eejj_8aug2022/inputListAllCurrent.txt
#inputlist2016post=config/inputListsPSK_UL16postVFP_eejj_8aug2022/inputListAllCurrent.txt
#inputlist2016pre=config/inputListsPSK_UL16preVFP_eejj_8aug2022_heep/inputListAllCurrent.txt
#inputlist2016post=config/inputListsPSK_UL16postVFP_eejj_8aug2022_heep/inputListAllCurrent.txt
#inputlist2016=config/nanoV7_2016_analysisPreselSkims_egLoose_4feb2022/inputListAllCurrent.txt
#inputlist2016=config/nanoV7_2016_analysisPreselSkims_heep_2sep2021/inputListAllCurrent.txt
inputlist2017=config/nanoV7_2017_pskEEJJ_12apr2021/inputListAllCurrent.txt
#inputlist2017=config/nanoV7_2017_pskEEJJ_12apr2021_separate/inputList_LQToBEleOnly.txt
inputlist2018=config/nanoV7_2018_pskEEJJ_12apr2021/inputListAllCurrent.txt
#------------
CODENAME=analysisClass_lq_eejj
#CODENAME=analysisClass_lq_eejj_oneBTag
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
# cut files
cutFileAna2016="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR%%p*}/Analysis/${YEAR#2016}/cutTable_lq_eejj_preselOnly.txt"
#cutFileAna2016="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR%%p*}/Analysis/${YEAR#2016}/cutTable_lq_eejj_looserPresel.txt"
#cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR%%p*}/Analysis/cutTable_lq_eejj_loosePresel.txt"
#cutFileAna2016="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR%%p*}/Analysis/${YEAR#2016}/cutTable_lq_eejj_loosePresel.txt"
#cutFileAna2016="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR%%p*}/Analysis/${YEAR#2016}/cutTable_lq_eejj_loosePresel_noJetRequirements.txt"
#cutFileAna2016="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR%%p*}/Analysis/${YEAR#2016}/cutTable_lq_eejj_loosePresel_noJetRequirements_noPtEE.txt"
#cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR%%p*}/Analysis/cutTable_lq_eejj.txt"
#cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR}/Analysis/cutTable_lq_eejj.txt"
#cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/cutTable_lq_eejj_BDT1400.txt"
#cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/cutTable_lq_eejj_BDT1500.txt"
#cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/cutTable_lq_eejj_BDT1600.txt"
#cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/cutTable_lq_eejj_BDT1700.txt"
#cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/cutTable_lq_eejj_BDT_parametrized.txt"
#
#cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/Analysis/cutTable_lq_eejj_MasymTest.txt"
cutFileOpt="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR}/Optimization/cutTable_lq_eejj_BDT_opt.txt"
#cutFileOpt="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR}/Optimization/cutTable_lq_eejj_opt.txt"
#cutFileOpt="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR}/Optimization/cutTable_lq_eejj_oneBTag_opt.txt"
#cutFileOpt="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/Optimization/cutTable_lq_eejj_twoBTags_opt.txt"
# ilumi
ilumi2016pre=19501.601622
ilumi2016post=16812.151722
ilumi2017=41540 #FIXME: this number is just from the Egamma twiki
ilumi2018=59399
excludeCombining=""
#------------
#QUEUEANA=tomorrow # for systs
QUEUEOPT=testmatch
#QUEUEANA=longlunch  # one job failed using longlunch
QUEUEANA=workday
#QUEUEANA=microcentury # sufficient for no systs
#------------
if [ "$YEAR" = "2016preVFP" ]; then
  echo "Doing 2016preVFP!"
  ILUM=$ilumi2016pre
  INPUTLIST=$inputlist2016pre
elif [ "$YEAR" = "2016postVFP" ]; then
  echo "Doing 2016postVFP!"
  ILUM=$ilumi2016post
  INPUTLIST=$inputlist2016post
elif [ "$YEAR" = "2017" ]; then
  echo "Doing 2017!"
  ILUM=$ilumi2017
  INPUTLIST=$inputlist2017
  excludeCombining="-e LQToBEle*"
elif [ "$YEAR" = "2018" ]; then
  echo "Doing 2087!"
  ILUM=$ilumi2018
  INPUTLIST=$inputlist2018
else
  die "year argument ${YEAR} not one of 2016preVFP, 2016postVFP, 2017, 2018"
fi
#------------
if [ "$OPT" = "1" ]; then
  DIRSTR="opt"
  files=$cutFileOpt
  queue=$QUEUEOPT
elif [[ "$YEAR" == *2016* ]]; then
  DIRSTR="analysis"
  files=$cutFileAna2016
  queue=$QUEUEANA
else
  DIRSTR="analysis"
  files=$cutFileAna
  queue=$QUEUEANA
fi
SUBDIR=ultralegacy/${DIRSTR}/${YEAR}/$ANANAME
#EOSDIR=/eos/user/s/scooper/LQ/NanoV7/${YEAR}/$DIRSTR/$ANANAME
EOSDIR=/eos/cms/store/group/phys_exotica/leptonsPlusJets/LQ/scooper/ultralegacy/${DIRSTR}/${YEAR}/$ANANAME
COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_${YEAR}_${DIRSTR}_batch_$(hostname -s).txt
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_eejj_${YEAR}.txt
#------------
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
EXE=build/main
#------------
XSECTION=config/xsection_13TeV_2022.txt
#XSECTION=/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/versionsOfOptimization/nanoV7/2016/eejj_17jan_egmLooseID/xsection_13TeV_2015_Mee_PAS_gteTwoBtaggedJets_TTbar_Mee_PAS_DYJets.txt
#------------
#### END OF INPUTS ####

echo "" > $COMMANDFILE

for file in $files
do
  suffix=$(basename $file)
suffix=${suffix%\.*}
cat >> $COMMANDFILE <<EOF
####################################################
#### launch, check and combine cmds for $suffix ####
# 1 job per dataset
python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $OUTDIRPATH/$SUBDIR/condor -c $file -q $queue -d $EOSDIR -j 1 -n rootTupleTree/tree

./scripts/checkJobs.sh $OUTDIRPATH/$SUBDIR/condor $OUTDIRPATH/$SUBDIR/condor

mkdir -p $OUTDIRPATH/$SUBDIR/output_$suffix \
&& time  ./scripts/combinePlots.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/condor \
    -l  $(echo "$ILUM*$FACTOR" | bc) \
    -x $XSECTION  \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s $SAMPLELISTFORMERGING \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}.log \
&& mv -v $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}.log $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}_unscaled.log \
&& mv -v $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_plots.root $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_plots_unscaled.root \
&& mv -v $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_tables.dat $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_tables_unscaled.dat \
&& mkdir -p $LQANA/versionsOfAnalysis/2016/eejj/${ANANAME}_${YEAR} && cd $LQANA/versionsOfAnalysis/2016/eejj/${ANANAME}_${YEAR} && python $LQMACRO/plotting2016/makeStackHistoTemplateV2_eejj.py dummy.root $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_plots_unscaled.root ${YEAR} \
&& python $LQMACRO/plotting2016/calc_DYJetsAndTTBarRescale_And_xsecFile.py dummy.root $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_plots_unscaled.root ${YEAR} > rescale.log \
&& cd $LQANA \
&& time  ./scripts/combinePlots.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/condor \
    -l $(echo "$ILUM*$FACTOR" | bc) \
    -x $LQANA/versionsOfAnalysis/2016/eejj/${ANANAME}_${YEAR}/xsection_13TeV_2022_Mee_BkgControlRegion_gteTwoBtaggedJets_TTbar_Mee_BkgControlRegion_DYJets.txt \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s $SAMPLELISTFORMERGING \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}.log \
&& mkdir -p $LQANA/versionsOfAnalysis/2016/eejj/${ANANAME}_${YEAR}/scaled && cd $LQANA/versionsOfAnalysis/2016/eejj/${ANANAME}_${YEAR}/scaled && python $LQMACRO/plotting2016/makeStackHistoTemplateV2_eejj.py dummy.root $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_plots.root ${YEAR}
EOF
#cat >> $COMMANDFILE <<EOF
#
#####################################################
##### launch, check and combine cmds for $suffix ####
## 1 job per dataset
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $OUTDIRPATH/$SUBDIR/condor -c $file -q $queue -d $EOSDIR -j 1 -n rootTupleTree/tree
#
#./scripts/checkJobs.sh $OUTDIRPATH/$SUBDIR/condor $OUTDIRPATH/$SUBDIR/condor
#
#mkdir -p $OUTDIRPATH/$SUBDIR/output_$suffix \
#&& time  ./scripts/combineOutputJobs.py \
#    -i $INPUTLIST \
#    -c $CODENAME \
#    -d $OUTDIRPATH/$SUBDIR/condor \
#    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
#    $excludeCombining
#
#time  ./scripts/combinePlots.py \
#    -i $INPUTLIST \
#    -c $CODENAME \
#    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
#    -l  `echo "$ILUM*$FACTOR" | bc` \
#    -x $XSECTION  \
#    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
#    -s $SAMPLELISTFORMERGING \
#    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}.log \
#&& mv -v $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}.log $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}_unscaled.log \
#&& mv -v $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_plots.root $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_plots_unscaled.root \
#&& mv -v $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_tables.dat $OUTDIRPATH/$SUBDIR/output_$suffix/${CODENAME}_tables_unscaled.dat
#EOF
done


echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to $COMMANDFILE"
