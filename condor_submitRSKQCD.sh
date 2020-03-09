#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_nanoPostProc_eoscms/inputList_singlePhoton.txt -o /afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nano/2016/rskQCD_9jul2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_QCD.txt -j 10 -q longlunch -d /eos/user/s/scooper/LQ/Nano/rskQCD_9jul2019 -r
# workday queue
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_nanoPostProc_eoscms/inputList_singlePhoton.txt -o /afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nano/2016/rskQCD_9jul2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_QCD.txt -j 10 -q workday -d /eos/user/s/scooper/LQ/Nano/rskQCD_9jul2019 -r
# aug28
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_custom2016NanoSkimNewNanoDataWithJson_eoscms/inputList_singlePhoton.txt -o /afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nano/2016/rskQCD_28aug2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_QCD.txt -j 10 -q workday -d /eos/user/s/scooper/LQ/Nano/rskQCD_28aug2019 -r
# oct8; new postProcSkim with Ele_pt > 35 GeV
python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_nanoPostProc_eoscms/inputList_singlePhoton.txt -o /afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nano/2016/rskQCD_8oct2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_QCD.txt -j 10 -q workday -d /eos/user/s/scooper/LQ/Nano/rskQCD_8oct2019 -r
