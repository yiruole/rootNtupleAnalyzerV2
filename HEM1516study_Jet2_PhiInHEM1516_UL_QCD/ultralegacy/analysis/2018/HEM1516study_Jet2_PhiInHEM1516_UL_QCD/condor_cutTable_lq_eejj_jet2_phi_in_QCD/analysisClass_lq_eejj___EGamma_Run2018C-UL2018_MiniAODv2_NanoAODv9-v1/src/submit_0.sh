#!/bin/bash
source /cvmfs/sft.cern.ch/lcg/views/LCG_102/x86_64-centos7-gcc11-opt/setup.sh
[ -z "$HOME" ] && export HOME=/afs/cern.ch/user/r/ryi
export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH
./main input_0.list cutTable_lq_eejj_jet2_phi_in_QCD.txt rootTupleTree/tree analysisClass_lq_eejj___EGamma_Run2018C-UL2018_MiniAODv2_NanoAODv9-v1_0 analysisClass_lq_eejj___EGamma_Run2018C-UL2018_MiniAODv2_NanoAODv9-v1_0
retVal=$?
if [ $retVal -ne 0 ]; then
  echo "./main return error code=$retVal; quitting here."
  exit $retVal
fi
mv -v analysisClass_lq_eejj___EGamma_Run2018C-UL2018_MiniAODv2_NanoAODv9-v1_0.root /afs/cern.ch/user/r/ryi/HEM1516/Leptoquarks/analyzer/rootNtupleAnalyzerV2/HEM1516study_Jet2_PhiInHEM1516_UL_QCD/ultralegacy/analysis/2018/HEM1516study_Jet2_PhiInHEM1516_UL_QCD/condor_cutTable_lq_eejj_jet2_phi_in_QCD/analysisClass_lq_eejj___EGamma_Run2018C-UL2018_MiniAODv2_NanoAODv9-v1/output/
mv -v analysisClass_lq_eejj___EGamma_Run2018C-UL2018_MiniAODv2_NanoAODv9-v1_0.dat /afs/cern.ch/user/r/ryi/HEM1516/Leptoquarks/analyzer/rootNtupleAnalyzerV2/HEM1516study_Jet2_PhiInHEM1516_UL_QCD/ultralegacy/analysis/2018/HEM1516study_Jet2_PhiInHEM1516_UL_QCD/condor_cutTable_lq_eejj_jet2_phi_in_QCD/analysisClass_lq_eejj___EGamma_Run2018C-UL2018_MiniAODv2_NanoAODv9-v1/output/
if [ -f analysisClass_lq_eejj___EGamma_Run2018C-UL2018_MiniAODv2_NanoAODv9-v1_0_skim.root ]; then
    xrdfs root://eoscms.cern.ch/ mkdir "/store/user/ryi/HEM1516study_Jet2_PhiInHEM1516_UL_QCD/cutTable_lq_eejj_jet2_phi_in_QCD/EGamma_Run2018C-UL2018_MiniAODv2_NanoAODv9-v1"
    xrdcp -fs "analysisClass_lq_eejj___EGamma_Run2018C-UL2018_MiniAODv2_NanoAODv9-v1_0_skim.root" "root://eoscms.cern.ch//store/user/ryi/HEM1516study_Jet2_PhiInHEM1516_UL_QCD/cutTable_lq_eejj_jet2_phi_in_QCD/EGamma_Run2018C-UL2018_MiniAODv2_NanoAODv9-v1/EGamma_Run2018C-UL2018_MiniAODv2_NanoAODv9-v1_0_sk.root"
fi
