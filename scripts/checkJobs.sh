#!/bin/bash

#if [[ $# -ne 2 ]]; then
if [[ $# -gt 2 ]]; then
    echo "Incorrect number of parameters"
    echo "Usage: $0 localDir [outputFileDir]"
    exit -1
fi

localdir=$1
eosdir=$2

echo "Grepping error files..."
find $localdir -iname "*.err" -exec sh -c "grep -ivH \"no dict\" {} | grep -iv \"No branch name is matching wildcard\" | grep -iv \"glidein_config\" | grep -iv \"WARNING: While\" | grep -v \"singularity\" " \;
echo "Done."

echo "Checking .out files..."
find $localdir -iname "*.out" -exec grep -iH "error" {} \;
echo "Done."

if [[ -z "$eosdir" ]]; then
  exit 0
fi

#echo "submit files: `find $localdir -iname "submit*sh" | wc -l`"
#echo "files on eos: `EOS_MGM_URL=root://eosuser.cern.ch eos find -f $eosdir | grep -v '.sys.v#.' | wc -l`"
dirlist=`find $localdir -maxdepth 1 -type d | tail -n +2`
#echo $dirlist
declare -i numOKDatasets=0
declare -i numBadDatasets=0
declare -i numDatasets=0
echo
echo -n "Checking for output files..."
txtOut="dataset    submitFiles    filesOnEOS    status    \n"
for dir in $dirlist
do
  #echo $dir
  #echo "eos find -f $eosdir/${dir##*___}"
  #echo "dataset=${dir##*/}  submit files: `find $localdir -iname \"submit*sh\" | wc -l` files on eos: `EOS_MGM_URL=root://eosuser.cern.ch eos find -f $eosdir | grep -v '.sys.v#.' | wc -l`"
  # works
  #txtOut=$txtOut"${dir##*___} `find $dir -iname \"submit*sh\" | wc -l` `EOS_MGM_URL=root://eosuser.cern.ch eos find -f $eosdir/${dir##*___} | grep -v '.sys.' | wc -l`\n"
  numDatasets+=1
  numSubmitFiles=`find $dir -iname "submit*sh" | wc | awk '{print $1}'`
  if [[ $eosdir == *"eos/cms"* ]]; then
    numOutputFiles=`xrdfs root://eoscms.cern.ch ls $eosdir/${dir##*___}| wc -l`
  elif [[ $eosdir == *"eos/user"* ]]; then
    #numOutputFiles=`EOS_MGM_URL=root://eosuser.cern.ch eos find -f $eosdir/${dir##*___} | grep -v '.sys.' | wc -l`
    numOutputFiles=`xrdfs root://eosuser.cern.ch ls $eosdir/${dir##*___}| wc -l`
  else
    #echo "find $eosdir/${dir##*/}/output -type f -iname '*.root' | grep -v '.sys.' | wc -l"
    numOutputFiles=`find $eosdir/${dir##*/}/output -type f -iname "*.root" | grep -v '.sys.' | wc -l`
  fi
  dataset=${dir##*___}
  if [ "$numSubmitFiles" != "$numOutputFiles" ]; then
    txtOut=$txtOut"$dataset $numSubmitFiles $numOutputFiles BAD\n"
    #echo "numSubmitFiles=$numSubmitFiles"
    #echo "numEosFiles=$numEosFiles"
    numBadDatasets+=1
  else
    #txtOut=$txtOut"$dataset $numSubmitFiles $numEosFiles OK\n"
    numOKDatasets+=1
  fi
done
echo "Done"
echo
echo "####################################################################################################"
echo "$numOKDatasets/$numDatasets datasets were checked and are OK."
if [ $numBadDatasets -gt 0 ]; then
  echo "$numBadDatasets/$numDatasets datasets have problems:"
  echo -e $txtOut | column -t
fi
