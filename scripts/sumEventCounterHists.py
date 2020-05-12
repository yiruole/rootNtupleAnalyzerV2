#!/usr/bin/env python2

from ROOT import TFile

fileList = "/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nanoV6/2018/rskSingleEleL_27apr2020/analysisClass_lq1_skim___EGamma_Run2018A-Nano25Oct2019-v1/input/input_0.list"

with open(fileList, "r") as listFile:
    files = listFile.read().splitlines()

fileHandles = []
for i, f in enumerate(files):
    thisFile = TFile.Open(f)
    if i == 0:
        myHist = thisFile.Get("EventCounter")
    else:
        myHist.Add(thisFile.Get("EventCounter"))
    fileHandles.append(thisFile)

myHist.Draw()

# for f in fileHandles:
#     f.Close()
