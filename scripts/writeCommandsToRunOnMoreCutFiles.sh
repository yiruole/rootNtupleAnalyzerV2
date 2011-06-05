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
#files=`ls $LQMACRO/config/cutTable_enujjSample.txt` # list of cut files that will be used
#files=`ls $LQMACRO/config/cutTable_enujjSample_QCD.txt` # list of cut files that will be used
#files=`ls $LQMACRO/config/eejj/cutTable_eejjSample_*.txt $LQMACRO/config/cutTable_eejjSample.txt` # list of cut files that will be used
#files=`ls $LQANA/Test_eejj_QCD/cutTable_eejjSample_QCD.txt` # list of cut files that will be used
#files=`ls $LQANA/Test_enujj_QCD/cutTable_enujjSample_QCD.txt` # list of cut files that will be used
files=`ls $LQMACRO2011/config/cutTable_enujjSample_2011.txt` # list of cut files that will be used
#------------
OUTDIRPATH=$LQDATA  # a subdir will be created for each cut file 
#SUBDIR=enujj_analysis/6.7pb-1_v2_Brussels_QCD_HLT20_noEle
#SUBDIR=enujj_analysis/6.7pb-1_v2_Brussels_noDeltaPhi
#SUBDIR=enujj_analysis/7.4pb-1_v1_QCD_HLT30
#SUBDIR=enujj_analysis/15.1pb-1_v4
#SUBDIR=enujj_analysis/21.9pb-1_v2
SUBDIR=enujj_analysis/330pb-1_enujjskim
#SUBDIR=enujj_analysis/10.9pb-1_v3_EcalDeadCellsStudy
         # output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
         # it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=330 # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
CODENAME=analysisClass_enujjSample_2011 #the actual name of the code used to process the ntuples (without the suffix ".C") 
#CODENAME=analysisClass_enujjSample_QCD #the actual name of the code used to process the ntuples (without the suffix ".C") 
#CODENAME=analysisClass_eejjSample_QCD #the actual name of the code used to process the ntuples (without the suffix ".C") 
#------------
#INPUTLIST=config/PhotonSkim/inputListAllCurrent.txt #specify input list
INPUTLIST=config/ElectronSkimENUJJ/inputListAllCurrent.txt #specify input list
#INPUTLIST=config/ElectronSkim/input_skim.txt
#INPUTLIST=config/ElectronSkim/inputListAllCurrent_MC.txt #specify input list
#------------
XSECTION=config/xsection_7TeV_2011.txt #specify cross section file
#XSECTION=config/xsection_7TeV_Zrescale_Wrescale.txt #specify cross section file
#XSECTION=config/xsection_7TeV_Zrescale.txt #specify cross section file
#------------
#SAMPLELISTFORMERGING=config/sampleListForMerging_7TeV.txt #specify list for sample merging
#SAMPLELISTFORMERGING=config/sampleListForMerging_7TeV_enujj_QCD.txt #specify list for sample merging
SAMPLELISTFORMERGING=config/sampleListForMerging_7TeV_enujj_2011.txt #specify list for sample merging
#------------
##DATA
NJOBS=5 #number of jobs for each dataset
WAIT=5 #seconds of delay between submission of different datasets
##MC
#NJOBS=30 #number of jobs for each dataset
#WAIT=5 #seconds of delay between submission of different datasets
#------------
QUEUE=1nh #bsub queue  

#### END OF INPUTS ####

COMMANDFILE=commandsToRunOnMoreCutFiles_`hostname -s |perl -pi -e 's|lxplus[0-9]*|lxplus|'`.txt
echo "" > $COMMANDFILE

for file in $files
do
suffix=`basename $file`
suffix=${suffix%\.*}
cat >> $COMMANDFILE <<EOF

####################################################
#### launch, check and combine cmds for $suffix ####

  ./scripts/launchAnalysis_batch.pl \
    -i $INPUTLIST \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -j $NJOBS \
    -q $QUEUE \
    -w $WAIT \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/launch_${suffix}.log

  ./scripts/check_combine_output_batch.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -q $QUEUE \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/checkcombine_${suffix}.log

  ./scripts/combineTablesTemplate.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -l  `echo "$ILUM*$FACTOR" | bc` \
    -x $XSECTION  \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -s $SAMPLELISTFORMERGING \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/combineTables_${suffix}.log

  ./scripts/combinePlotsTemplate.py \
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
