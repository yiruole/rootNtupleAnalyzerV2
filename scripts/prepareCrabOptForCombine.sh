#!/bin/bash

if [ "$#" -ne 1 ]; then
  echo "specify codename (e.g., analysisClass_lq_eejj)"
  exit -1
fi

echo "using codename=$1"
codename=$1

# find root/dat files in crab folder and move to main dir
find crab -iname "*.root" -exec mv {} . \;
find crab -iname "*.dat" -exec mv {} . \;

## add analysisClass beginning
##for i in *.root; do mv $i analysisClass_lq_eejj___$i; done;
##for i in *.dat; do mv $i analysisClass_lq_eejj___$i; done;
##for i in *.root; do mv $i analysisClass_lq_enujj_MT___$i; done;
##for i in *.dat; do mv $i analysisClass_lq_enujj_MT___$i; done;
#for i in *.root; do mv $i analysisClass_lq_ttbarEst___$i; done;
#for i in *.dat; do mv $i analysisClass_lq_ttbarEst___$i; done;
for i in *.root; do mv $i ${codename}___$i; done;
for i in *.dat; do mv $i ${codename}___$i; done;

# remove _1 suffix from _1.root
for i in *.root; do mv $i ${i%_*}.root; done;
for i in *.dat; do mv $i ${i%_*}.dat; done;
