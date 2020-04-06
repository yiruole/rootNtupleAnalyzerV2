#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "Incorrect number of parameters"
    echo "Usage: $0 localDir eosDir"
    exit -1
fi

localdir=$1
eosdir=$2

echo -n "Grepping error files..."
find $localdir -iname "*.err" -exec grep -ivH "no dict" {} \;
echo "Done."
#echo "submit files: `find $localdir -iname "submit*sh" | wc -l`"
#echo "files on eos: `EOS_MGM_URL=root://eosuser.cern.ch eos find -f $eosdir | grep -v '.sys.v#.' | wc -l`"
dirlist=`find $localdir -maxdepth 1 -type d | tail -n +2`
#echo $dirlist
declare -i numOKDatasets=0
declare -i numBadDatasets=0
declare -i numDatasets=0
echo
echo -n "Checking files on eos..."
txtOut="dataset    submitFiles    filesOnEOS    status    \n"
for dir in $dirlist
do
  #echo $dir
  #echo "dataset=${dir##*/}  submit files: `find $localdir -iname \"submit*sh\" | wc -l` files on eos: `EOS_MGM_URL=root://eosuser.cern.ch eos find -f $eosdir | grep -v '.sys.v#.' | wc -l`"
  # works
  #txtOut=$txtOut"${dir##*___} `find $dir -iname \"submit*sh\" | wc -l` `EOS_MGM_URL=root://eosuser.cern.ch eos find -f $eosdir/${dir##*___} | grep -v '.sys.' | wc -l`\n"
  numDatasets+=1
  numSubmitFiles=`find $dir -iname "submit*sh" | wc | awk '{print $1}'`
  numEosFiles=`EOS_MGM_URL=root://eosuser.cern.ch eos find -f $eosdir/${dir##*___} | grep -v '.sys.' | wc -l`
  dataset=${dir##*___}
  if [ "$numSubmitFiles" != "$numEosFiles" ]; then
    txtOut=$txtOut"$dataset $numSubmitFiles $numEosFiles BAD\n"
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
