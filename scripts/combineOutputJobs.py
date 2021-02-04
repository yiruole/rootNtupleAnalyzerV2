#!/usr/bin/env python

# ---Import
import sys
import os
import string
from optparse import OptionParser
import glob
import multiprocessing
import ROOT as r
import combineCommon

result_list = []


def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)


def CombinePlotsAndTables(args):
    fileList, sampleName, dataset_fromInputList = args
    sampleHistos = {}
    sampleTable = {}
    for currentRootFile in fileList:
        combineCommon.AddHistosFromFile(currentRootFile, sampleHistos, sampleName)
        currentDatFile = currentRootFile.replace(".root", ".dat")
        data = combineCommon.ParseDatFile(currentDatFile)
        data = combineCommon.FillTableErrors(data, currentRootFile)
        sampleTable = combineCommon.UpdateTable(data, sampleTable)
    sampleTable = combineCommon.CalculateEfficiency(sampleTable)
    outputTableFilename = options.outputDir + "/" + options.analysisCode + "___" + dataset_fromInputList + "_tables.dat"
    with open(outputTableFilename, "w") as outputTableFile:
        print "Write table to file:", outputTableFilename
        combineCommon.WriteTable(sampleTable, sampleName, outputTableFile, False)
    outputTfile = r.TFile(
        outputTableFilename.replace("_tables.dat", ".root"), "RECREATE", "", 207
    )
    combineCommon.WriteHistos(outputTfile, sampleHistos)
    outputTfile.Close()
    if not options.saveInputFiles:
        print "removing input root files"
        for rootFile in fileList:
            os.remove(rootFile)
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


(options, args) = parser.parse_args()

if options.inputList is None or options.analysisCode is None or options.inputDir is None or options.outputDir is None:
    print "ERROR: missing a required option: i, c, d, o"
    parser.print_help()
    exit(-1)

# ncores = multiprocessing.cpu_count()
ncores = 4  # only use 4 parallel jobs to be nice
pool = multiprocessing.Pool(ncores)

# ---Loop over datasets in the inputlist to check if dat/root files are there
foundAllFiles = True
for lin in open(options.inputList):

    lin = string.strip(lin, "\n")
    # print 'lin=',lin
    if lin.startswith("#"):
        continue

    dataset_fromInputList = string.split(string.split(lin, "/")[-1], ".")[0]
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
    fileList = glob.glob(fullPath1+"/"+rootFileName1.replace(".root", "_*.root"))
    completeNamesTried.append(fullPath1+"/"+rootFileName1.replace(".root", "_*.root"))
    if len(fileList) < 1:
        fileList = glob.glob(fullPath2+"/"+rootFileName1.replace(".root", "_*.root"))
        completeNamesTried.append(fullPath2+"/"+rootFileName1.replace(".root", "_*.root"))
    if len(fileList) < 1:
        print
        print "ERROR: could not find root file for dataset:", dataset_fromInputList
        print "ERROR: tried these full paths:", completeNamesTried
        foundAllFiles = False
    sampleName = combineCommon.SanitizeDatasetNameFromInputList(dataset_fromInputList.replace("_tree", ""))
    # print "Found dataset {}: matching files:".format(dataset_fromInputList), fileList
    try:
        pool.apply_async(CombinePlotsAndTables, [[fileList, sampleName, dataset_fromInputList]], callback=log_result)
    except KeyboardInterrupt:
        print "\n\nCtrl-C detected: Bailing."
        pool.terminate()
        sys.exit(1)

# now close the pool and wait for jobs to finish
pool.close()
pool.join()
# check results?
# print(result_list)

if not foundAllFiles:
    print "Some files not found. Exiting..."
    sys.exit()
