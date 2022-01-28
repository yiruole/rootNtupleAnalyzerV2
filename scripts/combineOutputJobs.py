#!/usr/bin/env python

# ---Import
import sys
import os
import string
from optparse import OptionParser
import glob
import multiprocessing
import traceback
import re
import ROOT as r
import combineCommon
import faulthandler
faulthandler.enable()

result_list = []
logString = "INFO: running {} parallel jobs for {} separate datasets found in inputList..."


def CombineLikeDatasets(dictDatasetsFileNames):
    combinedDictDatasetsFileNames = dict()
    sanitizedDatasetsHandled = []
    for dataset, fileList in dictDatasetsFileNames.iteritems():
        sanitizedName = combineCommon.SanitizeDatasetNameFromInputList(dataset)
        if sanitizedName in sanitizedDatasetsHandled:
            continue  # already handled this dataset
        matchingDatasets = []
        matchingFiles = []
        for matchingDataset, matchingFileList in dictDatasetsFileNames.iteritems():
            sanitizedMatchingName = combineCommon.SanitizeDatasetNameFromInputList(matchingDataset)
            if sanitizedMatchingName == sanitizedName:
                matchingFiles.extend(matchingFileList)
                matchingDatasets.append(matchingDataset)
        #shortestDataset = sorted(matchingDatasets, key=lambda x: len(x))[0]
        #combinedDictDatasetsFileNames[shortestDataset] = matchingFiles
        combinedDictDatasetsFileNames[sanitizedName] = matchingFiles
        sanitizedDatasetsHandled.append(sanitizedName)
    # print "combinedDictDatasetsFileNames DY keys: {}".format([key for key in combinedDictDatasetsFileNames.keys() if "DY" in key])
    return combinedDictDatasetsFileNames


def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)
    sys.stdout.write("\r"+logString.format(jobCount, datasetCount))
    sys.stdout.write("\t"+str(len(result_list))+" jobs done")
    sys.stdout.flush()


def CombinePlotsAndTables(args):
    fileList, datasetName = args
    # print "INFO: CombinePlotsAndTables() called for datasetName {} -- {} input files: {}".format(datasetName, len(fileList), fileList)
    try:
        sampleHistos = {}
        sampleTable = {}
        for currentRootFile in fileList:
            combineCommon.AddHistosFromFile(currentRootFile, sampleHistos, currentRootFile)  # use root filename as piece name--only used for logging
            # print "INFO: done with AddHistosFromFile for datasetName {} file {}".format(datasetName, currentRootFile)
            # sys.stdout.flush()
            currentDatFile = currentRootFile.replace(".root", ".dat")
            # print "INFO: ParseDatFile for datasetName {} file {}".format(datasetName, currentRootFile)
            # sys.stdout.flush()
            data = combineCommon.ParseDatFile(currentDatFile)
            # print "INFO: FillTableErrors for datasetName {} file {}".format(datasetName, currentRootFile)
            # sys.stdout.flush()
            data = combineCommon.FillTableErrors(data, currentRootFile)
            # print "INFO: UpdateTable for datasetName {} file {}".format(datasetName, currentRootFile)
            # sys.stdout.flush()
            sampleTable = combineCommon.UpdateTable(data, sampleTable)
        # print "INFO: CalculateEfficiency for datasetName {}".format(datasetName)
        # sys.stdout.flush()
        sampleTable = combineCommon.CalculateEfficiency(sampleTable)
        outputTableFilename = options.outputDir + "/" + options.analysisCode + "___" + datasetName + ".dat"
        # print "INFO: WriteTable for datasetName {}".format(datasetName)
        # sys.stdout.flush()
        with open(outputTableFilename, "w") as outputTableFile:
            # print "Write table to file:", outputTableFilename
            combineCommon.WriteTable(sampleTable, datasetName, outputTableFile)
        outputTfile = r.TFile(
            outputTableFilename.replace(".dat", ".root"), "RECREATE", "", 207
        )
        # print "INFO: opened TFile; writing histos for datasetName {} to file {}".format(datasetName, outputTfile.GetName())
        # sys.stdout.flush()
        combineCommon.WriteHistos(outputTfile, sampleHistos)
        outputTfile.Close()
    except Exception as e:
        print "ERROR: exception in CombinePlotsAndTables for datasetName={}".format(datasetName)
        traceback.print_exc()
        raise e

    return True


usage = "usage: %prog [options] \nExample: \n./combineOutputJobs.py "

parser = OptionParser(usage=usage)

parser.add_option(
    "-i",
    "--inputList",
    dest="inputList",
    help="list of all datasets to be used (full path required)",
    metavar="LIST",
)

parser.add_option(
    "-c",
    "--code",
    dest="analysisCode",
    help="name of the CODE.C code used to generate the rootfiles (which is the beginning of the root file names before ___)",
    metavar="CODE",
)

parser.add_option(
    "-d",
    "--inputDir",
    dest="inputDir",
    help="the directory INDIR contains the rootfiles with the histograms to be combined (full path required)",
    metavar="INDIR",
)

parser.add_option(
    "-o",
    "--outputDir",
    dest="outputDir",
    help="the directory OUTDIR contains the output of the program (full path required)",
    metavar="OUTDIR",
)

parser.add_option(
    "-s",
    "--saveInputFiles",
    action="store_true",
    dest="saveInputFiles",
    default=False,
    help="Save input files (don't delete them); defaults to False",
    metavar="SAVEINPUTFILES",
)

parser.add_option(
    "-e",
    "--excludeDatasetsFromLikeCombining",
    dest="regexToExcludeFromCombining",
    default="",
    help="Regex matching datasets that should not be combined when similar",
    metavar="EXCLUDEDATASETS",
)

(options, args) = parser.parse_args()

if options.inputList is None or options.analysisCode is None or options.inputDir is None or options.outputDir is None:
    print "ERROR: missing a required option: i, c, d, o"
    parser.print_help()
    exit(-1)

if not os.path.exists(options.outputDir):
    os.makedirs(options.outputDir)

# ncores = multiprocessing.cpu_count()
ncores = 4  # only use 4 parallel jobs to be nice
pool = multiprocessing.Pool(ncores)

# ---Loop over datasets in the inputlist to check if dat/root files are there
#FIXME use combineCommon.FindInputFiles instead (needs some adaptation)
dictDatasetsFileNames = {}
missingDatasets = []
jobCount = 0
datasetCount = 0
for lin in open(options.inputList):

    lin = string.strip(lin, "\n")
    # print 'lin=',lin
    if lin.startswith("#"):
        continue

    dataset_fromInputList = string.split(string.split(lin, "/")[-1], ".")[0]
    datasetCount += 1
    # strip off the slashes and the .txt at the end
    # so this will look like 'TTJets_DiLept_reduced_skim'
    # print combineCommon.SanitizeDatasetNameFromInputList(dataset_fromInputList) + " ... ",
    # print combineCommon.SanitizeDatasetNameFromInputList(dataset_fromInputList),dataset_fromInputList,
    # sys.stdout.flush()

    rootFileName1 = (
        options.analysisCode
        + "___"
        + dataset_fromInputList
        + ".root"
    )
    rootFileName2 = rootFileName1.replace(".root", "_0.root")
    fullPath1 = options.inputDir
    fullPath2 = (
        options.inputDir
        + "/"
        + options.analysisCode
        + "___"
        + dataset_fromInputList
        + "/"
        + "output"
    )
    completeNamesTried = []
    # TODO: replace with either newer python glob with recursive globbing, or something like os.walk()
    fileList = glob.glob(fullPath1+"/"+rootFileName1.replace(".root", "_*.root"))
    completeNamesTried.append(fullPath1+"/"+rootFileName1.replace(".root", "_*.root"))
    if len(fileList) < 1:
        fileList = glob.glob(fullPath2+"/"+rootFileName1.replace(".root", "_*.root"))
        completeNamesTried.append(fullPath2+"/"+rootFileName1.replace(".root", "_*.root"))
    if len(fileList) < 1:
        print "ERROR: could not find root file for dataset:", dataset_fromInputList
        print "ERROR: tried these full paths:", completeNamesTried
        print
        missingDatasets.append(dataset_fromInputList)
        continue
    # sampleName = combineCommon.SanitizeDatasetNameFromInputList(dataset_fromInputList.replace("_tree", ""))
    # print "Found dataset {}: matching files:".format(dataset_fromInputList), fileList
    dictDatasetsFileNames[dataset_fromInputList] = fileList

datasetsToKeepSeparate = []
if len(options.regexToExcludeFromCombining) > 0:
    regex = re.compile(options.regexToExcludeFromCombining)
    for dataset, fileList in dictDatasetsFileNames.iteritems():
        regexMatch = re.match(regex, dataset)
        if regexMatch:
            datasetsToKeepSeparate.append(dataset)
    print "Not combining like datasets for: {}".format(datasetsToKeepSeparate)
dictDatasetsToKeepSeparate = {dataset: fileList for dataset, fileList in dictDatasetsFileNames.items() if dataset in datasetsToKeepSeparate}
dictDatasetsToCombine = {dataset: fileList for dataset, fileList in dictDatasetsFileNames.items() if dataset not in datasetsToKeepSeparate}
dictDatasetsFileNames = CombineLikeDatasets(dictDatasetsToCombine)
dictDatasetsFileNames.update(dictDatasetsToKeepSeparate)

for datasetName, fileList in dictDatasetsFileNames.iteritems():
    try:
        pool.apply_async(CombinePlotsAndTables, [[fileList, datasetName]], callback=log_result)
        jobCount += 1
    except KeyboardInterrupt:
        print "\n\nCtrl-C detected: Bailing."
        pool.terminate()
        sys.exit(1)
    except Exception as e:
        print "ERROR: caught exception in job for datasetName: {}; exiting".format(datasetName)
        exit(-2)

# now close the pool and wait for jobs to finish
pool.close()
sys.stdout.write(logString.format(jobCount, datasetCount))
sys.stdout.write("\t"+str(len(result_list))+" jobs done")
sys.stdout.flush()
pool.join()
# check results?
if len(result_list) < jobCount:
    print "ERROR: {} jobs had errors. Exiting.".format(jobCount-len(result_list))
    exit(-2)

# don't remove anything until everything looks OK
if not options.saveInputFiles:
    for datasetName, fileList in dictDatasetsFileNames.iteritems():
        # print "removing input root files"
        for rootFile in fileList:
            os.remove(rootFile)
print
print "Done"
sys.stdout.flush()

if len(missingDatasets):
    print "ERROR: Some files not found. Missing datasets:", missingDatasets, ". Exiting..."
    exit(-2)
