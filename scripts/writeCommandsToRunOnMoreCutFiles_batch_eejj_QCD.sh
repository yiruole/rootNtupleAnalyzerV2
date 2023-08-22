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
ANANAME=HEM1516study_Jet2_PhiInHEM1516_UL_QCD
#------------
inputlist2018=config/rskQCD_heep_20jun2023/inputListAllCurrent.txt
#------------
CODENAME=analysisClass_lq_eejj_QCD
#------------
OUTDIRPATH=/afs/cern.ch/user/r/ryi/HEM1516/Leptoquarks/analyzer/rootNtupleAnalyzerV2/HEM1516study_Jet2_PhiInHEM1516_UL_QCD
# cut files
cutFileAna="/afs/cern.ch/user/r/ryi/HEM1516/Leptoquarks/analyzer/rootNtupleAnalyzerV2/HEM1516file/cutTable_lq_eejj_jet2_phi_in_QCD.txt"
cutFileOpt="/afs/cern.ch/user/r/ryi/HEM1516/Leptoquarks/analyzer/rootNtupleAnalyzerV2/HEM1516file/cutTable_lq_eejj_jet2_phi_in_QCD.txt"# ilumi
ilumi2016pre=19501.601622
ilumi2016post=16812.151722
ilumi2017=41540 #FIXME: this number is just from the Egamma twiki
#ilumi2018=59399
#ilumi2018=20760 #AB
ilumi2018=38630 #CD
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
#EOSDIR=/eos/cms/store/group/phys_exotica/leptonsPlusJets/LQ/scooper/ultralegacy/${DIRSTR}/${YEAR}/$ANANAME
EOSDIR=/eos/user/r/ryi/LQ/NanoV7/${YEAR}/$DIRSTR/$ANANAME
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
