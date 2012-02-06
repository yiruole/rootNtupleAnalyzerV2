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
#files=`ls $LQMACRO/config/eejj/cutTable_eejjSample_*.txt $LQMACRO/config/cutTable_eejjSample.txt` # list of cut files that will be used
#files=`ls $LQMACRO2011/config/cutTable_enujjSample_2011_skim.txt` # list of cut files that will be used
#files=`ls $AXIGLUONMACRO/config2011/cutTable_axigluons_lnujj_skim.txt` # list of cut files that will be used
#files=`ls $AXIGLUONMACRO/config2011/cutTable_axigluons_skim.txt` # list of cut files that will be used
files=`ls $DIJETMACRO/config2011/cutTable_dijetPhysicsDST_2011Sel_skim.txt` # list of cut files that will be used          
#------------
#OUTDIRPATH=$AXIGLUONDATA  # a subdir will be created for each cut file 
OUTDIRPATH=$DIJETDATA  # a subdir will be created for each cut file 
#------------
#SUBDIR=enujj_analysis/21.9pb-1_v2
#SUBDIR=axigluons_lnujj/RootNtuple-V00-02-0X__DATA2011_160329_165969_330pb-1__MCSpring11__axigluons_enujj_skimEle30MET30_16072011
#SUBDIR=axigluons_lnujj/RootNtuple-V00-02-06__MCSummer11__axigluons_lnujj_skimEleORMu20MET20Jet1st20Jet2nd20_09092011
#SUBDIR=axigluons_lljj/RootNtuple-V00-02-06__MCSummer11__axigluons_lljj_skimDiEleORDiMu20Jet1st30Jet2nd30_25102011
#SUBDIR=dijets_PhysicsDST/RootNtuple-HEAD_Nov19-2011BData-PhysicsDST-179959-180282_dijets_allEvents_JECL123Res_23112011
SUBDIR=dijets_PhysicsDST/RootNtuple-HEAD_Nov19-2011BData-PhysicsDST-179959-180282_dijets_allEvents_JECL123Res_2011Sel_30012012
         # output sub-directory (i.e. output will be in OUTDIRPATH/SUBDIR)
         # it is suggested to specify the luminosity in the name of the directory
#------------
#CASTORDIR=LQ/RootNtuple/RootNtuple-V00-02-0X-DATA-MC-2011-enujj_preselection_skim_05062011
#CASTORDIR=Vjj/RootNtuple/RootNtuple-V00-02-0X__DATA2011_160329_165969_330pb-1__MCSpring11__axigluons_enujj_skimEle30MET30_16072011
#CASTORDIR=Vjj/RootNtuple/RootNtuple-V00-02-06__MCSummer11__axigluons_lnujj_skimEleORMu20MET20Jet1st20Jet2nd20_09092011
#CASTORDIR=Vjj/RootNtuple/RootNtuple-V00-02-06__MCSummer11__axigluons_lljj_skimDiEleORDiMu20Jet1st30Jet2nd30_25102011
CASTORDIR=DiJets/ReducedRootNtuple2011/RootNtuple-HEAD_Nov19-2011BData-PhysicsDST-179959-180282_dijets_allEvents_JECL123Res_2011Sel_30012012
FULLCASTORDIR=$CASTOR_HOME/$CASTORDIR #--> do not modify this line
#------------
#CODENAME=analysisClass_axigluons_lnujj_skim #the actual name of the code used to process the ntuples (without the suffix ".C") 
#CODENAME=analysisClass_axigluons_skim #the actual name of the code used to process the ntuples (without the suffix ".C") 
#CODENAME=analysisClass_dijetPhysicsDST_skim #the actual name of the code used to process the ntuples (without the suffix ".C") 
CODENAME=analysisClass_dijetPhysicsDST_2011Sel_skim #the actual name of the code used to process the ntuples (without the suffix ".C") 
#------------
#INPUTLIST=config/Summer11MC/inputListAllCurrent.txt #specify input list
#INPUTLIST=config/Summer11MC/inputListAllCurrent_Axigluons.txt #signal only
#INPUTLIST=config/Summer11MC/inputListAllCurrent_smallBkg.txt #small samples 
#INPUTLIST=config/Summer11MC/inputListAllCurrent_largeBkg.txt #large samples
#INPUTLIST=config/Summer11MC/inputListAllCurrent_edmundFiles.txt #large samples
#INPUTLIST=config/RootNtuple-HEAD_Nov3-2011BData-PhysicsDST-179959-180282_20111104_140216/inputListAllCurrent.txt #large samples
INPUTLIST=config/RootNtuple-HEAD_Nov19-2011BData-PhysicsDST-179959-180282_20111119_120219/inputListAllCurrent.txt
#------------
#NJOBS=1 #number of jobs for each dataset - #signal only
#NJOBS=5 #number of jobs for each dataset - #small samples  was 10
#NJOBS=40 #number of jobs for each dataset - #large samples  was 100
NJOBS=60 #number of jobs for each dataset - for PhysicsDST
WAIT=5 #seconds of delay between submission of different datasets
#------------
QUEUE=1nd #bsub queue  
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

  ./scripts/launchAnalysis_batch_ForSkimToCastor.pl \
    -i $INPUTLIST \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -j $NJOBS \
    -q $QUEUE \
    -w $WAIT \
    -d $CASTORDIR \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/launch_${suffix}.log

#### OR 

  ./scripts/launchAnalysis_batch_ForSkimToCastor.py \
    -i $INPUTLIST \
    -n rootTupleTree/tree \
    -c $file \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix  \
    -j $NJOBS \
    -q $QUEUE \
    -w $WAIT \
    -d $CASTORDIR \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/launch_${suffix}.log


#### THEN

  ./scripts/check_combine_output_batch_ForSkimToCastor.py \
    -i $INPUTLIST \
    -c $CODENAME \
    -d $OUTDIRPATH/$SUBDIR/output_$suffix \
    -o $OUTDIRPATH/$SUBDIR/output_$suffix \
    -q $QUEUE \
    -s $FULLCASTORDIR \
    | tee $OUTDIRPATH/$SUBDIR/output_$suffix/checkcombine_${suffix}.log

EOF
done


echo "The set of commands to run on the cut files:" 
for file in $files
do
echo "  " $file
done 
echo "has been written to $COMMANDFILE"
