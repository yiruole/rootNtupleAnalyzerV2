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

[ $# -gt 0 ] || die "must specify year as argument; usage: writeCommandsToRunOnMoreCutFiles_batch_fakeRateCalc.sh year"
YEAR=$1

#### INPUTS HERE ####
#------------
ANANAME=calcFR_2016pre_June2023
#------------
files="/afs/cern.ch/user/e/eipearso/leptoquark_analysis/rootNtupleMacrosV2/config2016/QCDFakeRate/cutTable_lq_QCD_FakeRateCalculation.txt"
#------------
QUEUE=workday
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
#EOSDIR=/eos/cms/store/user/eipearso/LQ/nanoV7/2016/qcdFakeRateCalc/$ANANAME
excludeCombining=""

# output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
# it is suggested to specify the luminosity in the name of the directory
#------------
ilumi2016=19501601.622000 #TODO
ilumi2017=41540 #FIXME: this number is just from the Egamma twiki
ilumi2018=59399
CODENAME=analysisClass_lq_QCD_FakeRateCalculation
#CODENAME=analysisClass_lq_eejj_noJets
#------------
#INPUTLIST=config/nanoV6_2016_rskQCD_18may2020_comb/inputListAllCurrent.txt
#INPUTLIST=config/nanoV6_2016_rskQCD_14jul2020_comb/inputListAllCurrent.txt
#INPUTLIST=config/nanoV6_2016_rskQCD_15jul2020_comb/inputListAllCurrent.txt
#INPUTLIST=config/nanoV6_2016_rskQCD_17jul2020_comb/inputListAllCurrent.txt
#inputlist2016=config/nanoV7_2016_rskQCD_23nov2021_comb/inputListAllCurrent.txt
#inputlist2016=config/nanoV7_2016_rskQCD_26nov2021_comb/inputListAllCurrent.txt
#inputlist2016=config/nanoV7_2016_rskQCD_looseEGM_18mar2022_comb/inputListAllCurrent.txt
#inputlist2016=config/myDatasets/inputListAllCurrent.txt
inputlist2016=config/myDatasets/2016HEEPpreVFP/inputListAllCurrent.txt
#------------
if [ "$YEAR" = "2016" ]; then
  echo "Doing 2016!"
  ILUM=$ilumi2016
  INPUTLIST=$inputlist2016
elif [ "$YEAR" = "2017" ]; then
  ILUM=$ilumi2017
  INPUTLIST=$inputlist2017
  excludeCombining="-e LQToBEle*"
elif [ "$YEAR" = "2018" ]; then
  ILUM=$ilumi2018
  INPUTLIST=$inputlist2018
fi
SUBDIR=${YEAR}/qcdFakeRateCalc/$ANANAME
EOSDIR=/eos/user/e/eipearso/LQ/${YEAR}/qcdFakeRateCalc/$ANANAME
COMMANDFILE=commandsToRunOnMoreCutFiles_fakeRateCalc_${YEAR}PostVFP_batch_`hostname -s`.txt
SAMPLELISTFORMERGING=config/sampleListForMerging_13TeV_QCD_calc_${YEAR}PostVFP.yaml
#------------
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
EXE=main
#------------
XSECTION=config/xsection_13TeV_2022.txt #specify cross section file
#------------
#### END OF INPUTS ####

echo "" > $COMMANDFILE

for file in $files
do
suffix=`basename $file`
suffix=${suffix%\.*}
cat >> $COMMANDFILE <<EOF

####################################################
#### launch, check and combine cmds for $suffix ####
# 1 job per file
python scripts/launchAnalysis_batch_ForSkimToEOS.py -i $INPUTLIST -o $OUTDIRPATH/$SUBDIR/condor -c $file -q $QUEUE -d $EOSDIR -j 1 -n rootTupleTree/tree

./scripts/checkJobs.sh $OUTDIRPATH/$SUBDIR/condor $OUTDIRPATH/$SUBDIR/condor

# mkdir -p $OUTDIRPATH/$SUBDIR/output_$suffix \
# && time  ./scripts/combineOutputJobs.py \
#     -i $INPUTLIST \
#     -c $CODENAME \
#     -d $OUTDIRPATH/$SUBDIR/condor \
#     -o $OUTDIRPATH/$SUBDIR/output_$suffix \
#     $excludeCombining

time  ./scripts/combinePlots.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l  `echo "$ILUM*$FACTOR" | bc` \
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
