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

[ $# -gt 0 ] || die "must specify year as argument; usage: writeCommandsToRunOnMoreCutFiles_batch_eejj_QCD.sh year [doOptimization]"
YEAR=$1

if [[ "$#" -gt 1 ]]; then
  OPT=1
else
  OPT=0
fi

#### INPUTS HERE ####
#------------
#ANANAME=qcdYield_eejj_9aug2021_oldOptFinalSels
#ANANAME=qcd_eejj_btagMed_8jul2021
#ANANAME=qcd_eejj_btagLoose_gtetwoBTags_13jul2021
#ANANAME=qcd_eejj_loosenMee_addMasym_addMET_10aug2021
#ANANAME=qcd_eejj_finalSelTestPunziAddMsym_3sep2021
#ANANAME=qcd_eejj_optEGLooseFR_17jan2022
#ANANAME=qcd_eejj_finalSels_EGLooseFR_19jan2022
#ANANAME=qcd_eejj_BDTLQ1700parametrized_EGLooseFR_13may2022
#ANANAME=qcd_eejj_preselOnly_EGLooseFR_6dec2022
ANANAME=qcd_eejj_EGLooseFR_bdtParamFinalSels_7dec2022
#------------
#inputlist2016=config/oldInputLists/nanoV7/2016/nanoV7_2016_rskQCD_16oct2020_comb/inputList_dataOnly.txt
#inputlist2016=config/nanoV7_2016_rskQCD_22mar2021_comb/inputList_dataOnly.txt
#inputlist2016=config/nanoV7_2016_rskQCD_26nov2021_comb/inputList_dataOnly.txt
#inputlist2016=config/nanoV7_2016_pskQCDEEJJ_egLoose_24mar2022_comb/inputList_dataOnly.txt
#inputlist2017=config/nanoV7_2017_rskQCD_22apr2021/inputList_dataOnly.txt
#inputlist2018=config/nanoV7_2018_rskQCD_22apr2021/inputList_dataOnly.txt
inputlist2016pre=config/inputListsPSKQCD_egmloose_UL16preVFP_5dec2022/inputListAllCurrent.txt
inputlist2016post=config/inputListsPSKQCD_egmloose_UL16postVFP_5dec2022/inputListAllCurrent.txt
#------------
CODENAME=analysisClass_lq_eejj_QCD
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
# cut files
#cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR}/Analysis/cutTable_lq_eejj_QCD.txt"
#cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/cutTable_lq_eejj_BDT1400_QCD.txt"
#cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/cutTable_lq_eejj_BDT_parametrized_QCD.txt"
#cutFileAna="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/Analysis/cutTable_lq_eejj_QCD_MasymTest.txt"
cutFileOpt="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config${YEAR}/Optimization/cutTable_lq_eejj_QCD_opt.txt"
#cutFileOpt="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/Optimization/cutTable_lq_eejj_QCD_oneBTag_opt.txt"
#cutFileOpt="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/Optimization/cutTable_lq_eejj_QCD_twoBTags_opt.txt"
#
#cutFileAna2016="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2016/Analysis/cutTable_lq_eejj_QCD_preselOnly.txt"
#
cutFileAna2016="/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/cutTable_lq_eejj_BDT1300_QCD.txt
/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/cutTable_lq_eejj_BDT1200_QCD.txt
/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/cutTable_lq_eejj_BDT1100_QCD.txt
"
# ilumi
ilumi2016pre=19501.601622
ilumi2016post=16812.151722
ilumi2017=41540 #FIXME: this number is just from the Egamma twiki
ilumi2018=59399
QUEUEOPT=testmatch
QUEUEANA=workday
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
elif [ "$YEAR" = "2018" ]; then
  echo "Doing 2018!"
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
EOSDIR=/eos/cms/store/group/phys_exotica/leptonsPlusJets/LQ/scooper/ultralegacy/${DIRSTR}/${YEAR}/$ANANAME
COMMANDFILE=commandsToRunOnMoreCutFiles_eejj_QCD_${YEAR}_${DIRSTR}_batch_$(hostname -s).txt
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_QCD_dataDriven_${YEAR}.yaml
#------------
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
EXE=build/main
#------------
XSECTION=config/xsection_13TeV_2022.txt
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
python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $OUTDIRPATH/$SUBDIR/condor_$suffix -c $file -q $queue -d $EOSDIR/$suffix -j 1 -n rootTupleTree/tree

./scripts/checkJobs.sh $OUTDIRPATH/$SUBDIR/condor_$suffix $OUTDIRPATH/$SUBDIR/condor_$suffix

mkdir -p $OUTDIRPATH/$SUBDIR/output_$suffix \
&& time  ./scripts/combinePlots.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/condor_$suffix \
    -l  $(echo "$ILUM*$FACTOR" | bc) \
    -x $XSECTION  \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s $SAMPLELISTFORMERGING \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTablesAndPlots_${suffix}.log

EOF
done


echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to $COMMANDFILE"
