#!/bin/sh

usage ()
{
        echo ""
        echo "Usage:   $0 -f FILENAME -t TTREENAME "
        echo "where:   FILENAME is the *.root file to be analyzed and TTREENAME the name of the TTree"
        echo "Example: $0 -f /afs/cern.ch/user/p/prumerio/scratch0/lq/mc/data/RootTupleMakerV2_output_MC.root -t rootTupleTree/tree"
        echo "Example for CASTOR: $0  -f rfio:/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-00-03-DATA-GR_R_35X_V7A_SD_EG-v2-132440-133511_20100505_233733/MinimumBias__Commissioning10-GR_R_35X_V7A_SD_EG-v2__RECO_1_1.root -t rootTupleTree/tree"
#### Note: the option "-d DIRECTORY" to run this script on the full chain of root files is left in the code but no longer needed (since arrays have been replaced by vectors) 
#         echo "Usage:   $0 -d directory -t TTreeName "
#         echo "where:   directory is the location of the *.root files to be analyzed"
#         echo "Example: $0 -d /home/data/RootTuples/Leptoquarks/V00-00-09_2009310_142420/output -t RootTupleMaker"
#         echo "Example: $0 -d /home/data/RootTuples/Leptoquarks/LQenujj-10TeV-CMSSW2-PAT-V00-00-07_091016_212933/output -t treeCreator/RootTupleMakerPAT"
        echo ""
        exit 1;
}

if [ $# -le 3 ]; then usage; fi;
while [ $# -gt 0 ]; # till there are parameters
do
  case "$1" in
    -f) FILENAME="$2"; shift ;;
    -d) DIRNAME="$2"; shift ;;
    -t) TTREENAME="$2"; shift ;;
    *) usage ;;
  esac
  shift  # get following parameters
done

if [ ! -z "${FILENAME}" ] && [ ! -z "${DIRNAME}" ] ; then
  usage;
  exit;
fi

cd `dirname $0`/../ ; # go to the directory rootNtupleAnalyzer/

if [ ! -z "${FILENAME}" ] ; then
  FILES=${FILENAME}
elif [ ! -z "${DIRNAME}" ] ; then
  FILES=`ls ${DIRNAME}/*.root`
fi

cat > temporaryMacro.C <<EOF
{
  TChain c("$TTREENAME");
EOF

for FILE in $FILES
do
  echo "  c.Add(\"${FILE}\"); " >> temporaryMacro.C
done

cat >> temporaryMacro.C <<EOF
  c.MakeClass("rootNtupleClass");
}
EOF

root -l -q temporaryMacro.C

rm temporaryMacro.C

# insert additional lines needed by rootNtupleClass.h
sed '
/\<TROOT\.h\>/ i\
\/\/\/\/ Lines added by make_rootNtupleClass.sh - BEGIN \n\#include \<vector\> \nusing namespace std\; \n\/\/\/\/ Lines added by make_rootNtupleClass.sh - END \n
' < rootNtupleClass.h > tmp.h
mv tmp.h rootNtupleClass.h

if [ -f "rootNtupleClass.h" ] && [ -f "rootNtupleClass.C" ]; then
    echo "Moving rootNtupleClass.h/C to ./include/ and ./src/ directories ..."
    mv -i rootNtupleClass.h include/
    mv -i rootNtupleClass.C src/
    #if [ -f "include/rootNtupleClass.h" ] && [ -f "src/rootNtupleClass.C" ]; then echo "... done."; fi;

    #echo "Creating src/analysisClass.C ..."
    #cp -i src/analysisClass_template.C src/analysisClass.C

    echo "done";    
else
    echo "Error: files rootNtupleClass.h/C have not been created."
fi







