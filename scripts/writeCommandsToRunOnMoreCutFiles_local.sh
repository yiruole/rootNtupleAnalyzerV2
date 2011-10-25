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
#files=`ls $AXIGLUONMACRO/config2011/cutTable_axigluons_enujj.txt` # list of cut files that will be used
files=`ls $AXIGLUONMACRO/config2011/cutTable_axigluons_munujj.txt` # list of cut files that will be used
#------------
OUTDIRPATH=$AXIGLUONDATA  # a subdir will be created for each cut file 
#SUBDIR=axigluons_enujj/5fb-1_Summer11MC_AxigluonW_enujj_noSHERPA_24102011
SUBDIR=axigluons_enujj/5fb-1_Summer11MC_AxigluonW_munujj_noSHERPA_24102011
         # output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
         # it is suggested to specify the luminosity in the name of the directory
#------------
ILUM=5000 # integrated luminosity in pb-1 to be used for rescaling/merging MC samples
FACTOR=1000 # numbers in final tables (but *not* in plots) will be multiplied by this scale factor (to see well the decimal digits)
#------------
#CODENAME=analysisClass_axigluons_enujj #the actual name of the code used to process the ntuples (without the suffix ".C") 
CODENAME=analysisClass_axigluons_munujj #the actual name of the code used to process the ntuples (without the suffix ".C") 
#------------
#INPUTLIST=config/RootNtuple-V00-02-06__MCSummer11__axigluons_lnujj_skimEleORMu20MET20Jet1st30Jet2nd30_09092011/inputListAllCurrent.txt #specify input list
INPUTLIST=config/RootNtuple-V00-02-06__MCSummer11__axigluons_lnujj_skimEleORMu20MET20Jet1st30Jet2nd30_09092011/inputListAllCurrent_noSHERPA.txt #specify input list

#------------
XSECTION=config/xsection_7TeV_Summer2011.txt #specify cross section file
#------------
SAMPLELISTFORMERGING=config/sampleListForMerging_7TeV_axigluons_lnujj_2011.txt #specify list for sample merging
#------------
NCORES=2 #Number of processor cores to be used to run the job
#------------

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

python scripts/launchAnalysis.py \
    -i $INPUTLIST \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -p $NCORES \
    | tee launch_${suffix}.log 

mv launch_${suffix}.log $OUTDIRPATH/$SUBDIR/output_$suffix/

## --- SKIP THIS PART FOR THE MOMENT --- 
  ./scripts/check_combine_output_batch.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -q $QUEUE \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/checkcombine_${suffix}.log
## -------------------------------------

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
