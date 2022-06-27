#/usr/bin/env python3

import subprocess
import shlex
import sys
import collections
from optparse import OptionParser


def GetFileList(dataset):
    query="\"file dataset={} | grep file.name, file.size\"".format(dataset)
    fullCommand = "dasgoclient --query="+query
    fullCommand += " --limit=0"
    rawOut = subprocess.run(shlex.split(fullCommand), check=True, stdout=subprocess.PIPE).stdout
    
    out = rawOut.decode(sys.stdout.encoding).split("\n")
    fileNameToSizeDict = dict()
    for line in out:
        if len(line) <= 0:
            continue
        lineSplit = line.split()
        fileNameToSizeDict[lineSplit[0]] = lineSplit[1]
    sortedFileNameToSizes = sorted(fileNameToSizeDict.items(), key=lambda kv: int(kv[1]))
    sortedFileNameToSizesDict = collections.OrderedDict(sortedFileNameToSizes)
    
    # look at the sorted dict
    # i = 0
    # for key in sortedFileNameToSizesDict.keys():
    #     print(key, sortedFileNameToSizesDict[key])
    #     i += 1
    #     if i > 5:
    #         break
    
    de = collections.deque(sortedFileNameToSizesDict.keys())
    
    fileList = list()
    while de:
        fileList.append(de.pop())  # largest
        if de:
          fileList.append(de.popleft())
    
    return fileList


def ReadDatasetList(datasetFile):
    datasetList = list()
    with open(datasetFile, "r") as theFile:
        for line in theFile:
            if not len(line.strip()) > 0:
                continue
            if line.strip().startswith("#"):
                continue
            datasetList.append(line.strip())
    return datasetList


# --------------------------------------------------------------------------------
# Parse options
# --------------------------------------------------------------------------------
usage = "usage: %prog [options] \nExample: python3 ./scripts/makeNanoSkimLists.py <options>"

parser = OptionParser(usage=usage)

parser.add_option(
    "-i",
    "--inputlist",
    dest="inputlist",
    help="list of all datasets to be used",
    metavar="LIST",
)
(options, args) = parser.parse_args()

if (
    not options.inputlist
):
    print("Inputlist not specified")
    parser.print_help()
    sys.exit()

prefix="root://cmsxrootd.fnal.gov/"
datasetList = ReadDatasetList(options.inputlist)
# dataset="/DYJetsToLL_LHEFilterPtZ-0To50_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL16NanoAODv9-106X_mcRun2_asymptotic_v17-v1/NANOAODSIM"
for dataset in datasetList:
    fileList = GetFileList(dataset)
    fileName = dataset.split("/")[1]
    fileName += ".txt"
    
    with open(fileName, "w") as outFile:
        for fName in fileList:
            outFile.write(prefix+fName+"\n")
