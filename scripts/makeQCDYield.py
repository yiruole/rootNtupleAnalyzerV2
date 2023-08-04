#!/usr/bin/env python3

import os
import sys
import glob
import math
import copy
from pathlib import Path
from optparse import OptionParser
import re

from combineCommon import SubtractTables, WriteTable

from ROOT import TFile, gROOT, SetOwnership


def FindFile(dirname, filename):
    fileList = glob.glob(os.path.abspath(dirname)+"/"+filename)
    if len(fileList) != 1:
        raise RuntimeError("Could not find unique file with name {} in dir {}; found {} files instead.".format(filename, dirname, len(fileList)))
    return fileList[0]


def GetSampleHistosFromTFile(tfileName, sample):
    histNameToHistDict = {}
    if tfileName.startswith("/eos/cms"):
        tfileName = "root://eoscms/" + tfileName
    elif tfileName.startswith("/eos/user"):
        tfileName = "root://eosuser/" + tfileName
    tfile = TFile.Open(tfileName)
    print("INFO: using file {} for sample {}".format(tfileName, sample))
    for key in tfile.GetListOfKeys():
        histoName = key.GetName()
        sampleNameFromHist = histoName.split("__")[1]
        if sample != sampleNameFromHist:
            continue
        htemp = key.ReadObj()
        if not htemp or htemp is None:
            raise RuntimeError("failed to get histo named:", histoName, "from file:", tfile.GetName())
        SetOwnership(htemp, True)
        if htemp.InheritsFrom("TH1"):
            htemp.SetDirectory(0)
        histNameToHistDict[histoName] = htemp
    sortedDict = dict(sorted(histNameToHistDict.items()))
    sampleHistos = list(sortedDict.values())
    tfile.Close()
    if len(sampleHistos) < 1:
        raise RuntimeError(
                "GetSampleHistosFromTFile({}, {}) -- failed to read any histos for the sampleName from this file!".format(
                    tfile.GetName(), sample))
    else:
        print("\tINFO: found {} hists for sample {}".format(len(sampleHistos), sample))
    return sampleHistos


def DoHistoSubtraction(singleFRQCDHistos, doubleFRQCDHistos, dyjSingleFRHistos):
    subHistos = []
    for idx, singleFRHisto in enumerate(singleFRQCDHistos):
        doubleFRHisto = doubleFRQCDHistos[idx]
        dyjSingleFRHisto = dyjSingleFRHistos[idx]
        singleFRHistoNameSuffix = singleFRHisto.GetName().split("__")[-1]
        if "LHEPdfSum" in singleFRHistoNameSuffix:
            continue  # don't consider LHEPdf hists
        verbose = False
        doubleFRHistoNameSuffix = doubleFRHisto.GetName().split("__")[-1]
        dyjSingleFRHistoNameSuffix = dyjSingleFRHisto.GetName().split("__")[-1]
        if singleFRHistoNameSuffix != doubleFRHistoNameSuffix:
            raise RuntimeError("Histo names don't match between singleFR and doubleFR: {} vs. {}, respectively.".format(singleFRHisto.GetName(), doubleFRHisto.GetName()))
        if singleFRHistoNameSuffix != dyjSingleFRHistoNameSuffix:
            raise RuntimeError("Histo names don't match between singleFR and dyjSingleFR: {} vs. {}, respectively.".format(singleFRHisto.GetName(), dyjSingleFRHisto.GetName()))
        if singleFRHisto.GetSumw2N() < 1:
            singleFRHisto.Sumw2()
        if doubleFRHisto.GetSumw2N() < 1:
            doubleFRHisto.Sumw2()
        if dyjSingleFRHisto.GetSumw2N() < 1:
            dyjSingleFRHisto.Sumw2()
        assert(singleFRHisto.GetNbinsX() == doubleFRHisto.GetNbinsX())
        assert(singleFRHisto.GetNbinsY() == doubleFRHisto.GetNbinsY())
        assert(singleFRHisto.GetNbinsZ() == doubleFRHisto.GetNbinsZ())
        # first, subtract the DYJ from the singleFR
        result = singleFRHisto.Add(dyjSingleFRHisto, -1)
        if not result:
            raise RuntimeError("Something wrong happened while subtracting {} from {}.".format(dyjSingleFRHisto.GetName(), singleFRHisto.GetName()))
        subHisto = SubtractHistosWithLimit(singleFRHisto, doubleFRHisto, verbose)
        subHistos.append(subHisto)
    return subHistos


def SubtractHistosWithLimit(singleFRHisto, doubleFRHisto, verbose = False):
    limit = 0.5
    singleFRHistoNew = copy.deepcopy(singleFRHisto.Clone())
    singleFRHistoNew.Reset()
    for globalBin in range(0, singleFRHisto.GetNcells()+1):
        singleBinContent = singleFRHisto.GetBinContent(globalBin)
        singleBinErrorSqr = pow(singleFRHisto.GetBinError(globalBin), 2)
        doubleBinContent = doubleFRHisto.GetBinContent(globalBin)
        doubleBinErrorSqr = pow(doubleFRHisto.GetBinError(globalBin), 2)
        if abs(doubleBinContent) > limit*abs(singleBinContent):
            # print("INFO: limited bin {} in histo {} to 50% of singleFR bin content = {:.2f}; singleFR orig content={:.2f}; doubleFR orig content={:.2f}".format(
            #     globalBin, singleFRHisto.GetName(), singleBinContent - limit*abs(singleBinContent), singleBinContent, doubleBinContent))
            #FIXME ERROR? Probably still OK to take the double FR weights into the errors sums as usual.
            doubleBinContent = limit*abs(singleBinContent)
        binError = math.sqrt(singleBinErrorSqr + doubleBinErrorSqr)
        singleFRHistoNew.SetBinContent(globalBin, singleBinContent - doubleBinContent)
        singleFRHistoNew.SetBinError(globalBin, binError)
    return singleFRHistoNew


def ParseDatFile(datFilename, sampleName):
    data = {}
    column = []
    lineCounter = int(0)
    with open(datFilename) as datFile:
        # find line that begins with '#id' and check that it belongs to the given sample
        foundFirstLine = False
        startIdx = 0
        prevLine = None
        for j, line in enumerate(datFile):
            # ignore comments
            if re.search("^###", line):
                prevLine = line
                continue
            line = line.strip("\n")
            if line.strip().startswith("#id"):
                if not foundFirstLine and sampleName in prevLine.strip():
                    foundFirstLine = True
                    print("INFO: found table for sample {} in file {}".format(sampleName, datFilename))
                elif foundFirstLine:
                    break
            # print "---> lineCounter: " , lineCounter
            # print line
            if foundFirstLine:
                if lineCounter == 0:
                    for i, piece in enumerate(line.split()):
                        column.append(piece)
                else:
                    for i, piece in enumerate(line.split()):
                        if i == 0:
                            if len(data) == 0:
                                startIdx = int(piece)
                            row = int(piece)-startIdx
                            data[row] = {}
                        elif i < 6:
                            data[row][column[i]] = piece
                        else:
                            data[row][column[i]] = float(piece)
                            # print data[row][ column[i] ]

                lineCounter = lineCounter + 1
            line = prevLine
    return data


def SubtractTables(inputTable, tableToSubtractOrig, zeroNegatives=False, limitSub=False):
    limit = 0.5
    # subtract the tableToSubtract from the inputTable
    if not inputTable:
        raise RuntimeError("No inputTable found! cannot subtract from nothing")
    else:
        outputTable = copy.deepcopy(inputTable)
        tableToSubtract = copy.deepcopy(tableToSubtractOrig)
        for j, line in enumerate(tableToSubtract):
            # print 'outputTable[int(',j,')][N]=',outputTable[int(j)]['N'],'tableToSubtract[',j,']','[N]=',tableToSubtract[j]['N']
            if limitSub:
                # if abs(float(tableToSubtract[j]["N"])) > limit*abs(float(outputTable[int(j)]["N"])):
                #     tableToSubtract[j]["N"]= limit*float(outputTable[int(j)]["N"])
                #     print("INFO: limited N to {}%".format(100%limit))
                if abs(float(tableToSubtract[j]["Npass"])) > limit*abs(float(outputTable[int(j)]["Npass"])):
                    print("INFO: limiting Npass to {:.2f}; originally {:.2f}, toSub {:.2f}".format(
                        limit*abs(float(outputTable[int(j)]["Npass"])), float(outputTable[int(j)]["Npass"]), float(tableToSubtract[j]["Npass"])))
                    tableToSubtract[j]["Npass"] = limit*abs(float(outputTable[int(j)]["Npass"]))
            # newN = float(outputTable[int(j)]["N"]) - float(tableToSubtract[j]["N"])
            newNpass = float(outputTable[int(j)]["Npass"]) - float(
                tableToSubtract[j]["Npass"]
            )
            # if newN < 0.0 and zeroNegatives:
            #     newN = 0.0
            if newNpass < 0.0 and zeroNegatives:
                newNpass = 0.0
            outputTable[int(j)] = {
                "variableName": tableToSubtract[j]["variableName"],
                "min1": tableToSubtract[j]["min1"],
                "max1": tableToSubtract[j]["max1"],
                "min2": tableToSubtract[j]["min2"],
                "max2": tableToSubtract[j]["max2"],
                # "N": newN,
                # #     #FIXME ERROR? Probably still OK to take the double FR weights into the errors sums as usual.
                # "errN": math.sqrt(
                #     pow(float(outputTable[int(j)]["errN"]), 2)
                #     + pow(float(tableToSubtract[j]["errN"]), 2)
                # ),
                "Npass": newNpass,
                #     #FIXME ERROR? Probably still OK to take the double FR weights into the errors sums as usual.
                "errNpass": math.sqrt(
                    pow(float(outputTable[int(j)]["errNpass"]), 2)
                    + pow(float(tableToSubtract[j]["errNpass"]), 2)
                ),
                "EffRel": float(0),
                "errEffRel": float(0),
                "EffAbs": float(0),
                "errEffAbs": float(0),
            }
    return outputTable


def ScaleTable(inputTableOrig, scaleFactor, errScaleFactor):
    if not inputTableOrig:
        raise RuntimeError("No inputTable found! cannot scale nothing")
    else:
        inputTable = copy.deepcopy(inputTableOrig)
        for j, line in enumerate(inputTable):
            nPassOrig = float(inputTable[int(j)]["Npass"])
            errNPassOrig = float(inputTable[j]["errNpass"])
            nPassNew = nPassOrig * scaleFactor
            if nPassOrig > 0.0:
                errNpassNew = nPassNew * math.sqrt(
                    pow(errNPassOrig / nPassOrig, 2)
                    + pow(errScaleFactor / scaleFactor, 2)
                )
            else:
                errNpassNew = nPassNew * errScaleFactor / scaleFactor

            inputTable[int(j)] = {
                "variableName": inputTable[j]["variableName"],
                "min1": inputTable[j]["min1"],
                "max1": inputTable[j]["max1"],
                "min2": inputTable[j]["min2"],
                "max2": inputTable[j]["max2"],
                "Npass": nPassNew,
                "errNpass": errNpassNew,
                "EffRel": float(0),
                "errEffRel": float(0),
                "EffAbs": float(0),
                "errEffAbs": float(0),
            }
    return inputTable


####################################################################################################
# RUN
####################################################################################################
zjetMCSampleName = "ZJet_amcatnlo_ptBinned_IncStitch"
qcdSampleName = "QCDFakes_DATA"
# ---Option Parser
usage = "usage: %prog [options] \nExample: \n./makeQCDYield.py -s /my/dir/with/plotsAndTablesFor1FREstimate -d /my/dir/with/plotsAndTablesFor2FREstimate -o /my/test//data/output"

parser = OptionParser(usage=usage)

parser.add_option(
    "-s",
    "--singleFakeRateEstimate",
    dest="singleFakeRateEstimateDir",
    help="directory containing single fake rate estimate results (full path required)",
    metavar="SINGLEFAKERATEESTIMATEDIR",
)
parser.add_option(
    "-d",
    "--doubleFakeRateEstimate",
    dest="doubleFakeRateEstimateDir",
    help="direcectory containing double fake rate estimate results (full path required)",
    metavar="DOUBLEFAKERATEESTIMATEDIR",
)
parser.add_option(
    "-o",
    "--outputDir",
    dest="outputDir",
    help="the directory OUTDIR contains the output of the program (full path required)",
    metavar="OUTDIR",
)
parser.add_option(
    "-f",
    "--fileName",
    dest="fileName",
    help="the FILENAME to write out the subtracted hists",
    default = "qcdSubtracted_plots.root",
    metavar="OUTDIR",
)

(options, args) = parser.parse_args()

if len(sys.argv) < 4:
    raise RuntimeError(usage)

if os.path.isdir(options.singleFakeRateEstimateDir) is False:
    raise RuntimeError("Dir {} does not exist.".format(options.singleFakeRateEstimateDir))
if os.path.isdir(options.doubleFakeRateEstimateDir) is False:
    raise RuntimeError("Dir {} does not exist.".format(options.doubleFakeRateEstimateDir))
if os.path.isdir(options.outputDir) is False:
    print("INFO: Making directory", options.outputDir)
    Path(options.outputDir).mkdir(parents=True)

print("Launched like:")
print("python ", end=' ')
for arg in sys.argv:
    print(" " + arg, end=' ')
print()
print("INFO: Using sample {} to subtract DY background from 1FR region".format(zjetMCSampleName))
print("INFO: Using sample {} for QCD data-driven yields".format(qcdSampleName))

# options.outputDir + "/" + options.analysisCode + "_plots.root"
# Try to find the 1FR plots and tables
singleFRPlotsFile = FindFile(options.singleFakeRateEstimateDir, "*_plots.root")
singleFRTablesFile = FindFile(options.singleFakeRateEstimateDir, "*_tables.dat")
singleFRQCDHistos = GetSampleHistosFromTFile(singleFRPlotsFile, qcdSampleName)
singleFRQCDTable = ParseDatFile(singleFRTablesFile, qcdSampleName)
singleFRDYJHistos = GetSampleHistosFromTFile(singleFRPlotsFile, zjetMCSampleName)
singleFRDYJTable = ScaleTable(ParseDatFile(singleFRTablesFile, zjetMCSampleName), 1/1000., 0)
# Try to find the 2FR plots and tables
doubleFRPlotsFile = FindFile(options.doubleFakeRateEstimateDir, "*_plots.root")
doubleFRTablesFile = FindFile(options.doubleFakeRateEstimateDir, "*_tables.dat")
doubleFRQCDHistos = GetSampleHistosFromTFile(doubleFRPlotsFile, qcdSampleName)
doubleFRQCDTable = ParseDatFile(doubleFRTablesFile, qcdSampleName)

# now we need to do 1FR - 2FR, where the subtraction is limited to 1FR/2 in each bin
print("INFO: Subtracting histograms...", flush=True, end='')
subbedHistos = DoHistoSubtraction(singleFRQCDHistos, doubleFRQCDHistos, singleFRDYJHistos)
print("Done.")
print("INFO: Subtracting tables...", flush=True, end='')
singleFRQCDTableNoDYJ = SubtractTables(singleFRQCDTable, singleFRDYJTable)
finalQCDYieldTable = SubtractTables(singleFRQCDTableNoDYJ, doubleFRQCDTable, False, True)
# subbedTable = DoTableSubtraction(singleFRQCDTable, doubleFRQCDTable, singleFRDYJTable)
subbedTable = finalQCDYieldTable
print("Done.")

tfilePath = options.outputDir+"/"+options.fileName
print("INFO: Writing subtracted plots to {}...".format(tfilePath), flush=True)
tfile = TFile.Open(tfilePath, "recreate", "", 207)
tfile.cd()
for histo in subbedHistos:
    histo.Write()
tfile.Close()
print("Done.")

datFilePath = options.outputDir+"/"+options.fileName.replace(".root", ".dat")
print("INFO: Writing subtracted tables to {}...".format(datFilePath), flush=True)
WriteTable(singleFRQCDTable, "1FR", open(datFilePath, "w"))
WriteTable(singleFRDYJTable, "DYJ1FR", open(datFilePath, "a"))
WriteTable(singleFRQCDTableNoDYJ, "1FR-DYJ1FR", open(datFilePath, "a"))
WriteTable(doubleFRQCDTable, "2FR", open(datFilePath, "a"))
WriteTable(subbedTable, qcdSampleName, open(datFilePath, "a"))
print("Done.")
