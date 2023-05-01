#!/usr/bin/env python3

import sys
import glob
from pathlib import Path
import subprocess
import shlex
from tabulate import tabulate


def appendSlash(dirName):
    if not dirName.endswith("/"):
        dirName+="/"
    return dirName


if len(sys.argv) < 2:
    raise RuntimeError("Incorrect number of arguments\n. Usage: {} localDir [outputFileDir].")

localDir = sys.argv[1]
if len(sys.argv) > 2:
    outputDir = sys.argv[2]
else:
    outputDir = localDir

localDir = appendSlash(localDir)
outputDir = appendSlash(outputDir)

harmlessErrorMessages = ["WARNING: While bind mounting", "INFO:    Environment variable", "TClass::Init:0: RuntimeWarning: no dictionary for class"]
harmlessErrorMessages.append("Environment variable SINGULARITY")
harmlessErrorMessages.append("Unable to set SINGULARITY")
harmlessErrorMessages.append("WARNING: Environment variable")
harmlessErrorMessages.append("Warning in <TClass::Init>: no dictionary for class")
harmlessErrorMessages.append("No branch name is matching wildcard")

print("Grepping error files...")
fileList = glob.glob(localDir+"**/*.err", recursive=True)
filesAndErrorOutput = {}
for errFile in fileList:
    errorOutputThisFile = []
    with open(errFile, 'r') as thisFile:
        lines = thisFile.readlines()
        for line in lines:
            if "messages after this line are from the actual job" in line:
                errorOutputThisFile.clear()
            elif any(substring in line for substring in harmlessErrorMessages):
                continue
            elif "mkdir" in line and "File exists" in line:
                continue
            else:
                errorOutputThisFile.append(line.strip("\n"))
    if len(errorOutputThisFile) > 0:
        filesAndErrorOutput[errFile] = errorOutputThisFile

for errorFile, errorOutput in filesAndErrorOutput.items():
    print("Found unexpected content in {}".format(errorFile))
    for line in errorOutput:
        print("\t" + line)
print ("Done.", flush=True)

print("Grepping .out files...")
fileList = glob.glob(localDir+"**/*.out", recursive=True)
filesAndOutput = {}
for outFile in fileList:
    outputThisFile = []
    with open(outFile, 'r') as thisFile:
        lines = thisFile.readlines()
        for line in lines:
            if "error" in line.lower():
                outputThisFile.append(line.strip("\n"))
    if len(outputThisFile) > 0:
        filesAndOutput[outFile] = outputThisFile

for outFile, output in filesAndOutput.items():
    print("Found unexpected content in {}".format(outFile))
    for line in output:
        print("\t" + line)
print ("Done.", flush=True)

datasetInfoDict = {}
print("Checking for output files...")
fileList = glob.glob(localDir+"**/*.sub", recursive=True)
numSubmitFiles = len(fileList)
p = Path(localDir)
subdirs = [x.name for x in p.iterdir() if x.is_dir()]
cmdsToRun = []
for dirName in subdirs:
    if "analysisClass" in dirName:
        dataset = dirName.split("___")[1].strip("/")
        datasetInfoDict[dataset] = {}
        numExpectedOutputFiles = len(glob.glob(localDir+dirName+"/src/submit*.sh"))
        datasetInfoDict[dataset]["numExpectedOutputFiles"] = numExpectedOutputFiles
        datasetInfoDict[dataset]["OK"] = True
        if "/eos/cms" in outputDir:
            cmd = "xrdfs root://eoscms.cern.ch ls {}".format(outputDir+dataset)
        elif "/eos/user" in outputDir:
            cmd = "xrdfs root://eosuser.cern.ch ls {}".format(outputDir+dataset)
        else:
            # cmd = 'find {}/output -type f -iname "*.root" | grep -v ".sys." | wc -l'.format(outputDir+dirName)
            numOutputFiles = glob.glob(outputDir+dirName+"/output/*.root", recursive=True)
        if "xrdfs" in cmd:
            # cmdOutput = subprocess.check_output(shlex.split(cmd))
            # numOutputFiles = len(cmdOutput.split())
            cmdsToRun.append(cmd)
            continue
        datasetInfoDict[dataset]["numOutputFiles"] = numOutputFiles
        if numOutputFiles != numExpectedOutputFiles:
            datasetInfoDict[dataset]["OK"] = False
if len(cmdsToRun) > 0:
    # use 4 processes
    for i in range(0, len(cmdsToRun), 4):
        cmds = cmdsToRun[i:i+4]
        datasets = list(datasetInfoDict.keys())[i:i+4]
        procs = [subprocess.Popen(shlex.split(i), stdout=subprocess.PIPE) for i in cmds]
        for idx, p in enumerate(procs):
            output = p.communicate()[0]
            numOutputFiles = len(output.split())
            datasetInfoDict[datasets[idx]]["numOutputFiles"] = numOutputFiles
            if numOutputFiles != datasetInfoDict[datasets[idx]]["numExpectedOutputFiles"]:
                datasetInfoDict[datasets[idx]]["numOutputFiles"] = False
        # print("Ran commands {} for datasets {} and got info {}".format(cmds, datasets, [datasetInfoDict[datasets[datasetIdx]] for datasetIdx in range(0, 4)]))
print("Done")
print()
table = []
columnNames = ["dataset", "expectedOutputFiles", "actualOutputFiles"]
numOKdatasets = 0
numBadDatasets = 0
for dataset in datasetInfoDict.keys():
    if datasetInfoDict[dataset]["OK"]:
        numOKdatasets += 1
    else:
        numBadDatasets += 1
        table.append([dataset, datasetInfoDict[dataset]["numExpectedOutputFiles"], datasetInfoDict[dataset]["numOutputFiles"]])
numDatasets = len(datasetInfoDict.keys())
print("####################################################################################################")
print("{}/{} datasets were checked and are OK.".format(numOKdatasets, numDatasets))
if numBadDatasets > 0:
    print("{}/{} datasets have problems:".format(numBadDatasets, numDatasets))
    print(tabulate(table, headers=columnNames, tablefmt="github"))
