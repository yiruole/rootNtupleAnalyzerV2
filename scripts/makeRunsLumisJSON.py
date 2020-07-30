#!/usr/bin/env python
import sys
from ROOT import TFile, TChain, TFileCollection

try:
    import CRABClient
    from WMCore.DataStructs.LumiList import LumiList
except ImportError:
    print
    print "ERROR: Could not load WMCore.DataStructs.LumiList.  Please source the crab3 setup:"
    # print "source /cvmfs/cms.cern.ch/crab3/crab.sh"
    print("source /cvmfs/cms.cern.ch/common/crab-setup.sh")
    exit(-1)


print "opening files...",
sys.stdout.flush()
myTree = TChain("Events")
tfc = TFileCollection ("dum","","/tmp/scooper/2018B.txt")
myTree.AddFileInfoList(tfc.GetList())
print "done"
sys.stdout.flush()
myTree.SetBranchStatus("*", 0)
myTree.SetBranchStatus("run", 1)
myTree.SetBranchStatus("luminosityBlock", 1)
print
print "looping over events...",
sys.stdout.flush()

entry = 0
runAndLumisDict = {}
for ev in myTree:
    # if entry % 50000 == 0:
    #     print "event: "+str(entry)
    if ev.run not in runAndLumisDict.keys():
        runAndLumisDict[ev.run] = []
    runAndLumisDict[ev.run].append(ev.luminosityBlock)
    entry += 1
print "done"
sys.stdout.flush()

llFileName = "test.json"
lumiList = LumiList(runsAndLumis=runAndLumisDict)
lumiList.writeJSON(llFileName)
print "wrote to", llFileName
