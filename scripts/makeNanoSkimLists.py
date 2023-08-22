#/usr/bin/env python3

import subprocess
import shlex
import sys
import os
import collections
from optparse import OptionParser


def GetFileNamesAndNEvents(dataset):
    query="\"file dataset={} | grep file.name, file.nevents\"".format(dataset)
    fullCommand = "dasgoclient --query="+query
    fullCommand += " --limit=0"
    rawOut = subprocess.run(shlex.split(fullCommand), check=True, stdout=subprocess.PIPE).stdout
    out = rawOut.decode(sys.stdout.encoding).split("\n")
    fileNameToEventsDict = dict()
    for line in out:
        if len(line) <= 0:
            continue
        lineSplit = line.split()
        fileNameToEventsDict[lineSplit[0]] = lineSplit[1]
    if len(fileNameToEventsDict) <= 0:
        raise RuntimeError("Did not find any files for the dataset '{}' by running the command '{}'.  Please correct or remove this dataset from the inputlist file.".format(dataset, fullCommand))
    # sortedFileNameToSizes = sorted(fileNameToSizeDict.items(), key=lambda kv: int(kv[1]))
    # sortedFileNameToSizesDict = collections.OrderedDict(sortedFileNameToSizes)
    # # look at the sorted dict
    # # i = 0
    # # for key in sortedFileNameToSizesDict.keys():
    # #     print(key, sortedFileNameToSizesDict[key])
    # #     i += 1
    # #     if i > 5:
    # #         break
    # de = collections.deque(sortedFileNameToSizesDict.keys())
    # fileList = list()
    # while de:
    #     fileList.append(de.pop())  # largest
    #     if de:
    #       fileList.append(de.popleft())
    # return fileList
    return fileNameToEventsDict


def ReadDatasetList(datasetFile):
    datasetList = list()
    with open(datasetFile, "r") as theFile:
        for line in theFile:
            if "#" in line:
              line = line.split("#")[0]
            if len(line.strip()) <= 0:
                continue
            datasetList.append(line.strip())
    return datasetList


def GetTxtFileNameFromDataset(dataset):
    datasetParts = dataset.split("/")
    fileName = datasetParts[1]
    if "APV" in dataset:
      fileName += "_APV"
    elif "Run20" in dataset:
      fileName += "_"+datasetParts[2]
    fileName += ".txt"
    return fileName


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
parser.add_option(
    "-o",
    "--outputDir",
    metavar="OUTPUTDIR",
    action="store",
    help="Specifies the output directory where the .txt list files will be stored. Please use the full path",
)
(options, args) = parser.parse_args()

if (
   options.inputlist is None or
   options.outputDir is None
):
    print("\nOptions -i and -o are required\n")
    parser.print_help()
    sys.exit()
outputDir = options.outputDir.rstrip("/") + "/"
os.makedirs(outputDir, exist_ok=True)  # don't complain if dir exists already

# prefix="root://cmsxrootd.fnal.gov/"
prefix="root://cms-xrd-global.cern.ch/"
outputFileName = outputDir + "inputListAllCurrent.txt"
datasetList = ReadDatasetList(options.inputlist)

print("INFO: Found {} datasets in inputlist file".format(len(datasetList)))
print("INFO: Querying DAS to obtain file lists")
steps = len(datasetList)
progressString = "0% ["+" "*steps+"] 100%"
print(progressString, end=" ")
print("\b"*(len(progressString)-3), end=" ")
sys.stdout.flush()

with open(outputFileName, "w") as mainInputList:
    for dataset in datasetList:
        # dataset="/DYJetsToLL_LHEFilterPtZ-0To50_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL16NanoAODv9-106X_mcRun2_asymptotic_v17-v1/NANOAODSIM"
        fileNamesToNEventsDict = GetFileNamesAndNEvents(dataset)
        fileName = outputDir+GetTxtFileNameFromDataset(dataset)
        with open(fileName, "w") as outFile:
            nEventsFilename = fileName.replace(".txt", "_nevents.txt")
            with open(nEventsFilename, "w") as eventsFile:
                for fName, nEvents in fileNamesToNEventsDict.items():
                    outFile.write(prefix+fName+"\n")
                    eventsFile.write(nEvents+"\n")
        mainInputList.write(fileName + "\n")
        print("\b.", end=" ")
        sys.stdout.flush()
print("\b] 100%")
print("INFO: Wrote {} dataset file lists into {}".format(len(datasetList), outputFileName))
