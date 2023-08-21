#!/usr/bin/env python3

import sys
import glob
from pathlib import Path
import subprocess
import shlex
import re
from tabulate import tabulate
import ROOT as r


def appendSlash(dirName):
    if not dirName.endswith("/"):
        dirName+="/"
    return dirName


def GetNEventsFromRootFile(rootFileURL, treeName = "Events"):
    r.gErrorIgnoreLevel = r.kWarning
    tfile = r.TFile.Open(rootFileURL)
    nevents = tfile.Get(treeName).GetEntries()
    tfile.Close()
    r.gErrorIgnoreLevel = r.kPrint
    return nevents


def GetNEventsFromFiles(fileList, treeName = "Events"):
    r.gErrorIgnoreLevel = r.kWarning+1
    tchain = r.TChain(treeName)
    for rootFileURL in fileList:
        tchain.Add(rootFileURL)
    nevents = tchain.GetEntries()
    r.gErrorIgnoreLevel = r.kPrint
    return nevents


def GetDatasets(datasetListFile):
    datasets = []
    with open(datasetListFile, "r") as datasetList:
        for line in datasetList:
            line = re.sub("#.*", "", line).strip()
            if len(line) < 4:
                continue
            datasets.append(line)
    return datasets


def GetFileEventsMapFromDAS(datasetList):
    fileNameToNEventsDict = {}
    datasets = GetDatasets(datasetsFile)
    cmdsToRun = []
    for dataset in datasets:
        dataset = dataset.strip("\n")
        query = "file dataset={} | grep file.name, file.nevents".format(dataset)
        cmd = 'dasgoclient --query="{}" --limit=-1'.format(query)
        cmdsToRun.append(cmd)
    # use 6 processes in parallel
    procsToUse = 6
    for i in range(0, len(cmdsToRun), procsToUse):
         cmds = cmdsToRun[i:i+procsToUse]
         procs = [subprocess.Popen(shlex.split(i), stdout=subprocess.PIPE, stderr=subprocess.PIPE) for i in cmds]
         for idx, p in enumerate(procs):
             res = p.communicate()
             if p.returncode != 0:
                  raise RuntimeError("DAS command failed with stderr =", res[1])
             output = res[0].decode()
             split = output.split()
             it = iter(split)
             for element in it:
                 fileName = element
                 nEvents = next(it)
                 fileNameToNEventsDict[fileName] = int(nEvents)
    return fileNameToNEventsDict


def CheckEventsProcessedPerJob(fileNameEventsDict):
    fileList = glob.glob(localDir+"**/submit_*.sh", recursive=True)
    if len(fileList) < 0:
        raise RuntimeError("Could not find any submit files in localDir {}".format(localDir))
    for srcFile in fileList:
        index = srcFile.split("_")[-1].split(".")[0]
        filesProcessed = []
        with open(srcFile, 'r') as thisFile:
            for line in thisFile:
                if "haddnano.py" in line:
                    filesProcessed =  line.split()[2:]
                    break
        if len(filesProcessed) < 1:
            raise RuntimeError("Did not find any input files processed when parsing file {}. Cannot check for correct number of events processed.".format(srcFile))
        eventsExpected = 0
        filesToReadFrom = []
        for rootFile in filesProcessed:
            fileName = "/"+rootFile.split("//")[-1]
            try:
                eventsExpected += fileNameEventsDict[fileName]
            except KeyError:
                filesToReadFrom.append(rootFile)
        if len(filesToReadFrom) > 0:
            eventsExpected += GetNEventsFromFiles(filesToReadFrom)
        path = Path(srcFile)
        datasetDir = str(path.parent.absolute().parent)+"/"
        datFiles = glob.glob(datasetDir+"output/*_{}.dat".format(index), recursive=True)
        if len(datFiles) > 1:
            raise RuntimeError("Didn't get exactly 1 dat file matching pattern '{}': {}. There should only be one.".format(datasetDir+"output/*_{}.dat".format(index), datFiles))
        elif len(datFiles) == 0:
            print("ERROR: Something happened with the job for src file {}: was not able to find dat file matching pattern '{}'.".format(srcFile, datasetDir+"output/*_{}.dat".format(index)))
            continue
        datFilename = datFiles[0]
        eventsProcessed = 0
        with open(datFilename, 'r') as datFile:
            for line in datFile:
                splitLine = line.split()
                if splitLine[1] == "nocut":
                    eventsProcessed = int(splitLine[7])
                    eventsProcessedPass = int(splitLine[8])
                    assert(eventsProcessed == eventsProcessedPass)
                    assert(eventsProcessed > 0)
                    break
        if eventsExpected != eventsProcessed:
            print("ERROR: Something happened with the job for src file {}: expected {} events but processed {}".format(srcFile, eventsExpected, eventsProcessed))


####################################################################################################
# Run
####################################################################################################
#FIXME change to optparser
if len(sys.argv) < 3:
    raise RuntimeError("Incorrect number of arguments\n. Usage: {} datasetsFile localDir [outputFileDir].")

datasetsFile = sys.argv[1]
localDir = sys.argv[2]
if len(sys.argv) > 3:
    outputDir = sys.argv[3]
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
harmlessErrorMessages.append("Error in <TNetXNGFile::ReadBuffers>: [ERROR] Server responded with an error: [3008] Single readv transfer is too large")
harmlessErrorMessages.append("INFO:    /etc/singularity/ exists;")
harmlessErrorMessages.append("security protocol 'ztn' disallowed for non-TLS connections.")
harmlessErrorMessages.append("tac: write error: Broken pipe")  # no idea what this is about, but apparently harmless
harmlessErrorMessages.append("Info in <TCanvas::MakeDefCanvas>:  created default TCanvas with name c1")

print("Checking processing of events...")
print("\t1) Gathering information on expected events per file from DAS...", end = '', flush = True)
fileToEventsDict = GetFileEventsMapFromDAS(datasetsFile)
print ("Done.", flush = True)
print("\t2) Checking that all events expected were processed...", end = '', flush = True)
CheckEventsProcessedPerJob(fileToEventsDict)
print ("Done.", flush = True)

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
            elif len(line.strip("\n")) > 0:
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
                datasetInfoDict[datasets[idx]]["OK"] = False
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
