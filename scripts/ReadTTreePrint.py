#!/usr/bin/env python2

import operator
from prettytable import PrettyTable
import sys
import os
import ROOT as r

#treeFilename = "root://eoscms.cern.ch//store/group/phys_exotica/leptonsPlusJets/LQ/scooper/nanoPostProc/2016/nanoAODv7/DYJetsToLL_Pt-650ToInf_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/LQ-v1/200803_164045/0000/DYJetsToLL_Pt-650ToInf_ext2_1.root"
#treeFilename = "root://eoscms//store/group/phys_exotica/leptonsPlusJets/LQ/scooper/NanoV7/skims/2016/rskSingleEleL_egLoose_3feb2022/SingleElectron_Run2016G-02Apr2020-v1/SingleElectron_Run2016G-02Apr2020-v1_1_rsk.root"
treeFilename = "root://eosuser//eos/user/s/scooper/LQ/NanoV7/skims/2016/rskQCD_26nov2021/SingleElectron_Run2016G-02Apr2020-v1/SingleElectron_Run2016G-02Apr2020-v1_1_rsk.root"
filename = "/tmp/scooper/treeLogTest.txt"
numberOfLargestBranchesToShow = 50

save = os.dup(sys.stdout.fileno())
newout = file(filename, "w")
os.dup2(newout.fileno(), sys.stdout.fileno())
tfile = r.TFile.Open(treeFilename)
# tree = tfile.Get("Events")
tree = tfile.Get("rootTupleTree/tree")
tree.Print()
tfile.Close()
os.dup2(save, sys.stdout.fileno())
newout.close()

branchNameToSizeDict = {}
with open(filename, "r") as theFile:
    currentBranchName = ""
    for line in theFile:
        if "Br " in line:
            currentBranchName = line.split(":")[1].strip()
        if "File Size  = " in line:
            size = int(line.split()[-2])  # bytes
            branchNameToSizeDict[currentBranchName] = size/1024.0/1024.0  # MB

# sort
sortedList = sorted(branchNameToSizeDict.items(), key=operator.itemgetter(1), reverse=True)
totalSize = sum([thisSize for name, thisSize in sortedList])
sortedList = sortedList[:numberOfLargestBranchesToShow]  # limit number of items to 100

# print
print "total file size:", totalSize, "(MB)"
print "space used by {} largest branches:".format(numberOfLargestBranchesToShow)
t = PrettyTable(["Branch name", "size (MB)", "% of total"])
t.float_format = "4.3"
t.align["Branch name"] = "l"
t.align["Size"] = "r"
for brNameSize in sortedList:
    t.add_row([brNameSize[0], brNameSize[1], 100*brNameSize[1]/(1.0*totalSize)])
print t
