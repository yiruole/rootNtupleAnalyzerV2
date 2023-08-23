#!/bin/bash
source /cvmfs/sft.cern.ch/lcg/views/LCG_102/x86_64-centos7-gcc11-opt/setup.sh
[ -z "$HOME" ] && export HOME=/afs/cern.ch/user/r/ryi
export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH
./main input_0.list cutTable_lq_eejj_ele1_both_in.txt rootTupleTree/tree analysisClass_lq_eejj___WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8_0 analysisClass_lq_eejj___WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8_0
retVal=$?
if [ $retVal -ne 0 ]; then
  echo "./main return error code=$retVal; quitting here."
  exit $retVal
fi
mv -v analysisClass_lq_eejj___WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8_0.root /afs/cern.ch/user/r/ryi/HEM1516/Leptoquarks/analyzer/rootNtupleAnalyzerV2/HEM1516study_Ele1_BothInHEM1516_UL/ultralegacy/analysis/2018/HEM1516study_Ele1_BothInHEM1516_UL/condor_cutTable_lq_eejj_ele1_both_in/analysisClass_lq_eejj___WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8/output/
mv -v analysisClass_lq_eejj___WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8_0.dat /afs/cern.ch/user/r/ryi/HEM1516/Leptoquarks/analyzer/rootNtupleAnalyzerV2/HEM1516study_Ele1_BothInHEM1516_UL/ultralegacy/analysis/2018/HEM1516study_Ele1_BothInHEM1516_UL/condor_cutTable_lq_eejj_ele1_both_in/analysisClass_lq_eejj___WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8/output/
if [ -f analysisClass_lq_eejj___WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8_0_skim.root ]; then
    xrdfs root://eosuser.cern.ch/ mkdir "/eos/user/r/ryi/LQ/NanoV7/2018/analysis/HEM1516study_Ele1_BothInHEM1516_UL/cutTable_lq_eejj_ele1_both_in/WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8"
    xrdcp -fs "analysisClass_lq_eejj___WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8_0_skim.root" "root://eosuser.cern.ch//eos/user/r/ryi/LQ/NanoV7/2018/analysis/HEM1516study_Ele1_BothInHEM1516_UL/cutTable_lq_eejj_ele1_both_in/WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8/WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8_0_sk.root"
fi
