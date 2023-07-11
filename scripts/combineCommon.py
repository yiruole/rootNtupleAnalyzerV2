#!/usr/bin/env python3

# ---Import
import sys
import os
import string
import math
import re
import glob
import copy
from collections import OrderedDict
from ruamel.yaml import YAML
import numpy as np
import ROOT as r
import faulthandler
faulthandler.enable()

# FORMAT = "%(levelname)s %(module)s %(funcName)s line:%(lineno)d - %(message)s"
# logging.basicConfig(format=FORMAT, level=logging.INFO)

intLumi = -1
xsectionDict = {}
finalSelectionName = ""


def FindInputFiles(inputList, analysisCode, inputDir, skipSimilarDatasets=True):
    # ---Loop over datasets in the inputlist to check if dat/root files are there
    foundAllFiles = True
    dictDatasetsFileNames = dict()
    print()
    print("Checking for root/dat files from samples in inputList...", end=' ')
    sys.stdout.flush()
    datasetsHandled = []
    for lin in open(inputList):
        lin = lin.strip("\n")
        # print 'lin=',lin
        if lin.startswith("#"):
            continue
        dataset_fromInputList = lin.split("/")[-1].split(".")[0]
        if skipSimilarDatasets and SanitizeDatasetNameFromInputList(dataset_fromInputList) in datasetsHandled:
            continue  # in the case where we already combined similar datasets, skip similiar dataset entries in the inputlist
        # strip off the slashes and the .txt at the end
        # so this will look like 'TTJets_DiLept_reduced_skim'
        # print combineCommon.SanitizeDatasetNameFromInputList(dataset_fromInputList) + " ... ",
        # print combineCommon.SanitizeDatasetNameFromInputList(dataset_fromInputList),dataset_fromInputList,
        # sys.stdout.flush()
        rootFileName1 = (
            analysisCode
            + "___"
            + dataset_fromInputList
            + ".root"
        )
        # rootFileName2 = rootFileName1.replace(".root", "_0.root")
        fullPath1 = inputDir
        # fullPath2: condor style with one job per dataset
        fullPath2 = (
            inputDir
            + "/"
            + analysisCode
            + "___"
            + dataset_fromInputList
            + "/"
            + "output"
        )
        completeNamesTried = []
        fileList = glob.glob(fullPath1+"/"+rootFileName1)
        completeNamesTried.append(fullPath1+"/"+rootFileName1)
        if len(fileList) < 1:
            newPathToTry = fullPath2+"/"+rootFileName1.replace(".root", "*.root")
            fileList = glob.glob(newPathToTry)
            completeNamesTried.append(newPathToTry)
        if len(fileList) < 1:
            newPathToTry = fullPath1+"/"+analysisCode+"___"+SanitizeDatasetNameFromInputList(dataset_fromInputList)+".root"
            fileList = glob.glob(newPathToTry)
            completeNamesTried.append(newPathToTry)
        # if len(fileList) < 1:
        #     newPathToTry = fullPath1+"/"+rootFileName1.replace("backup", "ext*").replace(".root", "*.root")
        #     fileList = glob.glob(newPathToTry)
        #     completeNamesTried.append(newPathToTry)
        # if len(fileList) < 1:
        #     rootFileNameWithoutExt = rootFileName1[:rootFileName1.find("ext")] + rootFileName1[rootFileName1.rfind("_")+1:]
        #     newPathToTry = fullPath1+"/"+rootFileNameWithoutExt.replace(".root", "*.root")
        #     fileList = glob.glob(newPathToTry)
        #     completeNamesTried.append(newPathToTry)
        # if len(fileList) < 1:
        #     rootFileNameWithoutBackup = rootFileName1[:rootFileName1.find("backup")] + rootFileName1[rootFileName1.rfind("_")+1:]
        #     newPathToTry = fullPath1+"/"+rootFileNameWithoutBackup.replace(".root", "*.root")
        #     fileList = glob.glob(newPathToTry)
        #     completeNamesTried.append(newPathToTry)
        if len(fileList) < 1:
            print()
            print("ERROR: could not find root file for dataset:", dataset_fromInputList)
            print("ERROR: tried these full paths:", completeNamesTried)
            foundAllFiles = False
        elif len(fileList) > 1:
            print("ERROR: found {} root files for dataset: {}".format(len(fileList), dataset_fromInputList))
            print("ERROR: considered these full paths: {}".format(completeNamesTried))
            foundAllFiles = False
        else:
            sampleName = SanitizeDatasetNameFromInputList(dataset_fromInputList.replace("_tree", ""))
            dictDatasetsFileNames[dataset_fromInputList] = fileList[0]
            # print "for dataset {}, found files: {}".format(dataset_fromInputList, fileList[0])
            datasetsHandled.append(sampleName)
    return foundAllFiles, dictDatasetsFileNames


def SanitizeDatasetNameFromInputList(dataset_fromInputList):
    # print '0) SanitizeDatasetNameFromInputList() result is:'+dataset_fromInputList
    dataset_fromInputList = dataset_fromInputList.replace("_reduced_skim", "")
    # in rare cases, replace __ by _
    dataset_fromInputList = dataset_fromInputList.replace("__", "_")
    if dataset_fromInputList.endswith("_tree"):
        dataset_fromInputList = dataset_fromInputList[
            0: dataset_fromInputList.find("_tree")
        ]
    # print '1) SanitizeDatasetNameFromInputList() result is:'+dataset_fromInputList
    dataset_fromInputList = dataset_fromInputList.replace("_APV", "")
    # it was causing problems for me that the v9-v* was being left on here but removed in SanitizeDatasetNameFromFullDataset - Emma
    if dataset_fromInputList.find("_NanoAODv")>0:
        dataset_fromInputList = dataset_fromInputList[:dataset_fromInputList.find("_NanoAODv")+8]
    dataset_fromInputList = dataset_fromInputList.rstrip("_")
    return dataset_fromInputList


def SanitizeDatasetNameFromFullDataset(dataset):
    # print 'SanitizeDatasetNameFromFullDataset: dataset looks like:'+dataset
    # this logic is somewhat copied from the submission script for the ntuples:
    #    https://github.com/CMSLQ/submitJobsWithCrabV2/blob/master/createAndSubmitJobsWithCrab3.py
    if "Run20" not in dataset:
        outputFile = dataset.split("/")[1]
    else:
        outputFile = "_".join(dataset.split("/")[1:3])
        # ignore any v specifications; i.e., NanoAODv9* -> NanoAOD
        if outputFile.find("_NanoAODv") > 0:
            outputFile = outputFile[:outputFile.find("_NanoAODv")+8]
    return outputFile


def GetSamplesToCombineDict(sampleListForMerging):
    dictSamples = OrderedDict()
    with open(sampleListForMerging, "r") as yaml_file:
        data = YAML().load(yaml_file)
    data = dict(data)
    for sample in data.keys():
        values = dict(data[sample])
        pieces = values["pieces"]
        if len(pieces) < 1:
            raise RuntimeError("GetSamplesToCombineDict(): cannot deal with sample which does not contain at least one piece: '"+sample+"'")
        if sample in list(dictSamples.keys()):
            print("ERROR: GetSamplesToCombineDict(): name '{}' has already been defined earlier in the sampleListForMerging file!".format(sample))
            print("\toffending part looks like '{}'".format(sample))
            raise RuntimeError("duplicate key found")
        dictSamples[sample] = {}
        dictSamples[sample]["pieces"] = pieces
        dictSamples[sample]["correlateLHESystematics"] = values["correlateLHESystematics"] if "correlateLHESystematics" in values.keys() else True
        dictSamples[sample]["save"] = values["save"] if "save" in values.keys() else False
        dictSamples[sample]["isMC"] = values["isMC"] if "isMC" in values.keys() else True
    return dictSamples


def CreateGraphDict(sampleDict):
    graphDict = {}
    for sample, keys in reversed(sampleDict.items()):
        #print("sample={}, pieces={}".format(sample, keys["pieces"]))
        pieces = keys["pieces"]
        graphDict[sample] = [piece for piece in pieces if "/" not in piece]
    return graphDict


def ExpandPiece(piece, dictSamples):
    if "/" in piece:
        piece = SanitizeDatasetNameFromFullDataset(piece)
        return [piece]
    else:
        pieces = dictSamples[piece]["pieces"]
        return ExpandPieces(pieces, dictSamples)


def ExpandPieces(pieceList, dictSamples):
    piecesToAdd = []
    for piece in pieceList:
        piecesToAdd.extend(ExpandPiece(piece, dictSamples))
    return piecesToAdd


def ExpandSampleDict(dictSamples):
    outputDict = dict()
    for sampleName, sampleList in list(dictSamples.items()):
        outputDict[sampleName] = ExpandPieces(sampleList, dictSamples)
    return outputDict


def PartialExpand(pieceList):
    piecesToAdd = []
    for piece in pieceList:
        if "/" in piece:
            piecesToAdd.extend([SanitizeDatasetNameFromFullDataset(piece)])
        else:
            piecesToAdd.extend([piece])
    return piecesToAdd


def NeedsExpansion(pieceList):
    for piece in pieceList:
        if "/" not in piece:
            return True
    return False


def ParseXSectionFile(xsectionFile):
    for line in open(os.path.expandvars(xsectionFile)):

        # ignore comments
        if line.startswith("#"):
            continue
        line = line.strip("\n")
        line = line.split("#")[0]  # strip off anything after any '#' if present
        # ignore empty lines
        if len(line) <= 0:
            continue

        try:
            dataset, xsection_val = line.split()
        except ValueError:
            raise RuntimeError('ERROR: could not split line "', line, '"')
        if "Run20" in dataset:
            # for data, add secondary dataset info
            dataset="_".join(dataset.split("/")[1:3])
            xsectionDict[dataset] = xsection_val
        else:
            xsectionDict[dataset.split("/")[1]] = xsection_val

        # print 'ParseXSectionFile: line looked like:"'+line+'"; call SanitizeDatasetNameFromFullDataset on dataset=',dataset
        # outputFile = SanitizeDatasetNameFromFullDataset(dataset)
        # xsectionDict[outputFile] = xsection_val
        # print outputFile + " " + xsection_val


def lookupXSection(datasetNameFromInputList):
    verbose = False
    datasetNameFromInputList = SanitizeDatasetNameFromInputList(datasetNameFromInputList)
    if len(xsectionDict) <= 0:
        raise RuntimeError("xsectionDict is empty. Cannot lookupXSection for "+datasetNameFromInputList)
    # for key in sorted(xsectionDict.keys()):
    #     print('sample=',key,'xsection=',xsectionDict[key])
    if datasetNameFromInputList in xsectionDict.keys():
        return xsectionDict[datasetNameFromInputList]
    else:
        # for key in sorted(xsectionDict.keys()):
        #     print('sample=',key,'xsection=',xsectionDict[key], flush=True)
        if "Run20" in datasetNameFromInputList:
            for key in sorted(xsectionDict.keys()):
                if datasetNameFromInputList in key:
                    return xsectionDict[key]
        raise RuntimeError("xsectionDict has no entry for key: {}".format(datasetNameFromInputList))


def ParseDatFile(datFilename):
    # ---Read .dat table for current dataset
    data = {}
    column = []
    lineCounter = int(0)

    # print("Opening:" , datFilename, flush=True)
    with open(datFilename) as datFile:
        # start with line that begins with '#id'
        foundFirstLine = False
        startIdx = 0
        for j, line in enumerate(datFile):
            # ignore comments
            if re.search("^###", line):
                continue
            line = line.strip("\n")
            if line.strip().startswith("#id"):
                foundFirstLine = True
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
                        else:
                            data[row][column[i]] = piece
                            # print data[row][ column[i] ]

                lineCounter = lineCounter + 1
    return data


def FillTableEfficiencies(table, rootFileName, weight, sampleName=""):
    verbose = True
    tfile = r.TFile.Open(rootFileName)
    if not tfile:
        raise RuntimeError("Could not open file '{}'.".format(rootFileName))
    if sampleName:
        histName = "profile1D__{}__EventsPassingCuts".format(sampleName)
    else:
        histName = "EventsPassingCuts"
    eventsPassingHist = tfile.Get(histName)
    if not eventsPassingHist:
        raise RuntimeError("ERROR: could not find hist '{}' in file '{}'.".format(histName, rootFileName))
    cutHists = []
    for i in range(0, eventsPassingHist.GetNbinsX()):
        iBin = i+1
        # cutHist = r.TH1D("passCutBin"+str(iBin), "passCutBin"+str(iBin), 1, 0, 1)
        if eventsPassingHist.ClassName() == "TProfile":
            binContent = eventsPassingHist.GetBinContent(iBin)*eventsPassingHist.GetBinEntries(iBin)
            binError = math.sqrt(eventsPassingHist.GetSumw2().At(iBin))
        else:
            binContent = eventsPassingHist.GetBinContent(iBin)
            binError = eventsPassingHist.GetBinError(iBin)
        histName = "passCutBin"+str(iBin)+"_"+eventsPassingHist.GetXaxis().GetBinLabel(iBin)
        cutHist = r.TH1D(histName, histName, 1, 0, 1)
        cutHist.SetBinContent(1, binContent)
        cutHist.SetBinError(1, binError)
        cutHists.append(cutHist)
    # create TEfficiencies
    noCutHist = cutHists[0]
    # Turn off warning messages
    # FIXME restore later
    prevIgnoreLevel = r.gErrorIgnoreLevel
    #r.gErrorIgnoreLevel = r.kError+1
    for i, hist in enumerate(cutHists):
        if i == 0:
            table[i]["errNpassSqr"] = pow(hist.GetBinError(1), 2)
            table[i]["errNSqr"] = table[i]["errNpassSqr"]
        else:
            if verbose:
                print("--> FillTableEfficiencies(): i={}; FillTableEfficiencies() -- hist {}".format(i, hist.GetName()))
                print("FillTableEfficiencies(): hist: GetBinContent(1) = {} +/- {}".format(hist.GetBinContent(1), hist.GetBinError(1)))
                print("FillTableEfficiencies(): cutHists[i-1]: GetBinContent(1) = {} +/- {}".format(cutHists[i-1].GetBinContent(1), cutHists[i-1].GetBinError(1)))
                print("FillTableEfficiencies(): noCutHist: GetBinContent(1) = {} +/- {}".format(noCutHist.GetBinContent(1), noCutHist.GetBinError(1)))
                print("- Creating TEfficiencyRel")
                sys.stdout.flush()
            r.gErrorIgnoreLevel = 0
            if(hist.GetBinContent(1) > cutHists[i-1].GetBinContent(1)):
                # here, passed > total, so root will complain; this can happen if we remove a negative weight event with this cut
                print("\tINFO: passed > pass(N-1); attempting to silence error messages!")
                sys.stdout.flush()
                r.gErrorIgnoreLevel = r.kError+1
                # r.gErrorIgnoreLevel = 3001
                #r.gROOT.ProcessLine("gErrorIgnoreLevel = 3001;")
            table[i]["TEfficiencyRel"] = r.TEfficiency(hist, cutHists[i-1])
            table[i]["TEfficiencyRel"].SetWeight(weight)
            print("- Creating TEfficiencyAbs")
            sys.stdout.flush()
            # r.gErrorIgnoreLevel = r.kInfo+1
            table[i]["TEfficiencyAbs"] = r.TEfficiency(hist, noCutHist)
            table[i]["TEfficiencyAbs"].SetWeight(weight)
            table[i]["errNpassSqr"] = pow(hist.GetBinError(1), 2)
            table[i]["errNSqr"] = pow(cutHists[i-1].GetBinError(1), 2)
        r.gErrorIgnoreLevel = prevIgnoreLevel
    # FIXME restore later
    #r.gErrorIgnoreLevel = prevIgnoreLevel
    tfile.Close()
    return table


def FillTableErrors(table, rootFileName, sampleName=""):
    tfile = r.TFile.Open(rootFileName)
    if not tfile:
        raise RuntimeError("ERROR: could not open file '{}'.".format(rootFileName))
    if sampleName:
        histName = "histo1D__{}__EventsPassingCutsAllHist".format(sampleName)
    else:
        histName = "EventsPassingCutsAllHist"
    eventsPassingHist = tfile.Get(histName)
    if not eventsPassingHist:
        raise RuntimeError("ERROR: could not find hist '{}' in file '{}'.".format(histName, rootFileName))

    for j, line in enumerate(table):
        iBin = j+1
        # print "Table line {}: {}".format(j, table[j])
        # print "GetSumw2() in hist={} for iBin={}".format(eventsPassingHist.GetName(), iBin)
        # sys.stdout.flush()
        # errNpassSqr = eventsPassingHist.GetSumw2().At(iBin)
        errNpassSqr = eventsPassingHist.GetBinError(iBin)**2
        if j > 0:
            # print "GetSumw2() in hist={} for iBin={}".format(eventsPassingHist.GetName(), iBin-1)
            # sys.stdout.flush()
            # errNSqr = eventsPassingHist.GetSumw2().At(iBin-1)
            errNSqr = eventsPassingHist.GetBinError(iBin-1)**2
        else:
            errNSqr = errNpassSqr
        table[j]["errNpassSqr"] = errNpassSqr
        table[j]["errNSqr"] = errNSqr
    tfile.Close()
    return table


def CreateWeightedTable(data, weight=1.0, xsection_X_intLumi=1.0):
    # ---Create new table using weight
    newtable = {}

    #Ntot = float(data[0]["N"])
    for j, line in enumerate(data):
        if j == 0:
            newtable[int(j)] = {
                    "variableName": data[j]["variableName"],
                    "min1": "-",
                    "max1": "-",
                    "min2": "-",
                    "max2": "-",
                    #"N": (Ntot * weight),
                    #"errNSqr": int(0),
                    "Npass": (float(data[j]["Npass"]) * weight),
                    "errNpassSqr": int(0),
                    }

        else:
            # print "data[{}]={}".format(j, data[j])
            #N = float(data[j]["N"]) * weight
            ## errN = float(data[j - 1]["errEffAbs"]) * xsection_X_intLumi
            #errNSqr = pow(float(data[j]["errN"]) * weight, 2)
            # print data[j]['variableName']
            # print "errN: " , errN
            #if str(errNSqr) == "nan":
            #    errNSqr = 0

                #            if( float(N) > 0 and float(errN) > 0 ):
                #                errRelN = errN / N
                #            else:
                #                errRelN = float(0)

            Npass = float(data[j]["Npass"]) * weight
            # errNpass = float(data[j]["errEffAbs"]) * xsection_X_intLumi
            if "errNpass" in data[j]:
                errNpassSqr = pow(float(data[j]["errNpass"]) * weight, 2)
            else:
                errNpassSqr = float(data[j]["errNpassSqr"]) * pow(weight, 2)
            # print "errNPass " , errNpass
            # print ""
            #if str(errNpassSqr) == "nan":
            #    errNpassSqr = 0

                #            if( float(Npass) > 0 and float(errNpass) > 0 ):
                #                errRelNpass = errNpass / Npass
                #            else:
                #                errRelNpass = float(0)

            newtable[int(j)] = {
                    "variableName": data[j]["variableName"],
                    "min1": data[j]["min1"],
                    "max1": data[j]["max1"],
                    "min2": data[j]["min2"],
                    "max2": data[j]["max2"],
                    #"N": N,
                    #"errNSqr": errNSqr,
                    "Npass": Npass,
                    "errNpassSqr": errNpassSqr,
                    # "TEfficiencyAbs": data[j]["TEfficiencyAbs"].SetWeight(weight),
                    # "TEfficiencyRel": data[j]["TEfficiencyRel"].SetWeight(weight)
                    }

            # print newtable
    return newtable


def UpdateTable(inputTable, outputTable):
    if not outputTable:
        outputTable = inputTable
    else:
        for j, line in enumerate(inputTable):
            # print 'outputTable[int(',j,')][N]=',outputTable[int(j)]['N'],'inputTable[',j,']','[N]=',inputTable[j]['N']
            # teffAbsIn = inputTable[j]["TEfficiencyAbs"]
            # teffAbsOut = outputTable[j]["TEfficiencyAbs"]
            # teffRelIn = inputTable[j]["TEfficiencyRel"]
            # teffRelOut = outputTable[j]["TEfficiencyRel"]
            outputTable[int(j)] = {
                "variableName": inputTable[j]["variableName"],
                "min1": inputTable[j]["min1"],
                "max1": inputTable[j]["max1"],
                "min2": inputTable[j]["min2"],
                "max2": inputTable[j]["max2"],
                #"N": float(outputTable[int(j)]["N"]) + float(inputTable[j]["N"]),
                #"errNSqr": float(outputTable[int(j)]["errNSqr"]) + float(inputTable[j]["errNSqr"]),
                "Npass": float(outputTable[int(j)]["Npass"]) + float(inputTable[j]["Npass"]),
                "errNpassSqr": float(outputTable[int(j)]["errNpassSqr"]) + float(inputTable[j]["errNpassSqr"]),
                "EffRel": float(0),
                "errEffRel": float(0),
                "EffAbs": float(0),
                "errEffAbs": float(0),
                # "errN": float(0),
                # "errNpass": float(0),
                # "TEfficiencyAbs": teffAbsOut + teffAbsIn,
                # "TEfficiencyRel": teffRelOut + teffRelIn
            }
    return outputTable


def SubtractTables(inputTable, outputTable, zeroNegatives=False):
    # subtract the inputTable from the outputTable
    if not outputTable:
        raise RuntimeError("No outputTable found! cannot subtract input from nothing")
    else:
        for j, line in enumerate(inputTable):
            # print 'outputTable[int(',j,')][N]=',outputTable[int(j)]['N'],'inputTable[',j,']','[N]=',inputTable[j]['N']
            newN = float(outputTable[int(j)]["N"]) - float(inputTable[j]["N"])
            newNpass = float(outputTable[int(j)]["Npass"]) - float(
                inputTable[j]["Npass"]
            )
            if newN < 0.0 and zeroNegatives:
                newN = 0.0
            if newNpass < 0.0 and zeroNegatives:
                newNpass = 0.0
            outputTable[int(j)] = {
                "variableName": inputTable[j]["variableName"],
                "min1": inputTable[j]["min1"],
                "max1": inputTable[j]["max1"],
                "min2": inputTable[j]["min2"],
                "max2": inputTable[j]["max2"],
                "N": newN,
                "errN": math.sqrt(
                    pow(float(outputTable[int(j)]["errN"]), 2)
                    + pow(float(inputTable[j]["errN"]), 2)
                ),
                "Npass": newNpass,
                "errNpass": math.sqrt(
                    pow(float(outputTable[int(j)]["errNpass"]), 2)
                    + pow(float(inputTable[j]["errNpass"]), 2)
                ),
                "EffRel": float(0),
                "errEffRel": float(0),
                "EffAbs": float(0),
                "errEffAbs": float(0),
            }
    return


def ScaleTable(inputTable, scaleFactor, errScaleFactor):
    if not inputTable:
        raise RuntimeError("No inputTable found! cannot scale nothing")
    else:
        for j, line in enumerate(inputTable):
            nOrig = float(inputTable[int(j)]["N"])
            errNorig = float(inputTable[int(j)]["errN"])
            nNew = nOrig * scaleFactor
            if nOrig > 0.0:
                errNnew = nNew * math.sqrt(
                    pow(errNorig / nOrig, 2) + pow(errScaleFactor / scaleFactor, 2)
                )
            else:
                errNnew = nNew * errScaleFactor / scaleFactor
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
                "N": nNew,
                "errN": errNnew,
                "Npass": nPassNew,
                "errNpass": errNpassNew,
                "EffRel": float(0),
                "errEffRel": float(0),
                "EffAbs": float(0),
                "errEffAbs": float(0),
            }
    return


def SquareTableErrorsForEfficiencyCalc(table):
    if not table:
        raise RuntimeError("No inputTable found! cannot convert nothing")
    else:
        for j, line in enumerate(table):
            table[int(j)] = {
                "variableName": table[j]["variableName"],
                "min1": table[j]["min1"],
                "max1": table[j]["max1"],
                "min2": table[j]["min2"],
                "max2": table[j]["max2"],
                "N": float(table[j]["N"]),
                "errN": pow(float(table[j]["errN"]), 2),
                "Npass": float(table[j]["Npass"]),
                "errNpass": pow(float(table[j]["errNpass"]), 2),
                "EffRel": float(0),
                "errEffRel": float(0),
                "EffAbs": float(0),
                "errEffAbs": float(0),
            }
    return


def CalculateEfficiency(table):
    newTable = {}
    # cutHists = []
    for j, line in enumerate(table):
        #errN = math.sqrt(table[j]["errNSqr"])
        errNpass = math.sqrt(table[j]["errNpassSqr"])
        newTable[int(j)] = {
            "variableName": table[int(j)]["variableName"],
            "min1": table[int(j)]["min1"],
            "max1": table[int(j)]["max1"],
            "min2": table[int(j)]["min2"],
            "max2": table[int(j)]["max2"],
            #"N": float(table[j]["N"]),
            #"errN": errN,
            "Npass": float(table[j]["Npass"]),
            "errNpass": errNpass,
            "EffRel": int(1),
            "errEffRel": int(0),
            "EffAbs": int(1),
            "errEffAbs": int(0),
        }
        # iBin = j+1
        # cutHist = r.TH1D("passCutBin"+str(iBin), "passCutBin"+str(iBin), 1, 0, 1)
        # cutHist.SetDirectory(0) # possible fix for memory leak due to duplicate hists in root registry
        # cutHist.SetBinContent(1, newTable[j]["Npass"])
        # cutHist.SetBinError(1, errNpass)
        # cutHists.append(cutHist)
        # if j > 0:
        #     prevHist = cutHists[j-1]
        #     print "creating TEfficiencyRel"
        #     sys.stdout.flush()
        #     r.gErrorIgnoreLevel = r.kPrint
        #     teffRel = r.TEfficiency(cutHist, prevHist)
        #     newTable[j]["EffRel"] = teffRel.GetEfficiency(1)
        #     newTable[j]["errEffRel"] = (teffRel.GetEfficiencyErrorUp(1)+teffRel.GetEfficiencyErrorLow(1))/2.
        #     print "creating TEfficiencyAbs"
        #     sys.stdout.flush()
        #     teffAbs = r.TEfficiency(cutHist, cutHists[0])
        #     newTable[j]["EffAbs"] = teffAbs.GetEfficiency(1)
        #     newTable[j]["errEffAbs"] = (teffAbs.GetEfficiencyErrorUp(1)+teffAbs.GetEfficiencyErrorLow(1))/2.

        # manual
        confLevel = 0.683
        prob = 0.5 * (1 - confLevel)
        if j > 0:
            # if newTable[j-1]["Npass"] <= 0:
            #     print "INFO: newTable[j]['Npass']={}, newTable[j-1]['Npass']={}".format(float(newTable[j]["Npass"]), float(newTable[j-1]["Npass"]))
            #     if newTable[j-1]["Npass"] < 0:
            #         print "\teff={}".format(float(newTable[j]["Npass"])/newTable[j-1]["Npass"])
            pw2 = float(table[j]["errNpassSqr"])
            tw2 = float(table[j-1]["errNpassSqr"])
            tw = float(table[j-1]["Npass"])
            prevNpass = newTable[j-1]["Npass"]
            eff = 0 if prevNpass == 0 else float(newTable[j]["Npass"])/prevNpass
            newTable[j]["EffRel"] = eff
            # copied from TEfficiency code; normal approximation with weights (only frequentist method available)
            # print "({} * (1. - 2 * {}) + {} * {} * {}) / ({} * {})".format(pw2, eff, tw2, eff, eff, tw, tw)
            variance = (pw2 * (1. - 2 * eff) + tw2 * eff * eff) / (tw * tw) if tw != 0 else 0
            if variance >= 0:
                sigma = math.sqrt(variance)
                delta = r.Math.normal_quantile_c(prob, sigma)
                newTable[j]["errEffRel"] = eff if eff-delta < 0 else delta
            else:
                newTable[j]["errEffRel"] = -1
            eff = float(newTable[j]["Npass"])/newTable[0]["Npass"]
            tw2 = float(table[0]["errNpassSqr"])
            tw = float(table[0]["Npass"])
            newTable[j]["EffAbs"] = newTable[j]["Npass"]/newTable[0]["Npass"]
            variance = (pw2 * (1. - 2 * eff) + tw2 * eff * eff) / (tw * tw)
            if variance >= 0:
                sigma = math.sqrt(variance)
                delta = r.Math.normal_quantile_c(prob, sigma)
                newTable[j]["errEffAbs"] = eff if eff-delta < 0 else delta
            else:
                newTable[j]["errEffAbs"] = -1

        # else:
        #     N = float(table[j]["N"])
        #     errN = math.sqrt(float(table[j]["errN"]))
        #     if float(N) > 0:
        #         errRelN = errN / N
        #     else:
        #         errRelN = float(0)

        #     Npass = float(table[j]["Npass"])
        #     errNpass = math.sqrt(float(table[j]["errNpass"]))
        #     if float(Npass) > 0:
        #         errRelNpass = errNpass / Npass
        #     else:
        #         errRelNpass = float(0)

        #     if Npass > 0 and N > 0:
        #         EffRel = Npass / N
        #         errRelEffRel = math.sqrt(errRelNpass * errRelNpass + errRelN * errRelN)
        #         errEffRel = errRelEffRel * EffRel

        #         EffAbs = Npass / float(table[0]["N"])
        #         errEffAbs = errNpass / float(table[0]["N"])
        #     else:
        #         EffRel = 0
        #         errEffRel = 0
        #         EffAbs = 0
        #         errEffAbs = 0

        #     table[int(j)] = {
        #         "variableName": table[int(j)]["variableName"],
        #         "min1": table[int(j)]["min1"],
        #         "max1": table[int(j)]["max1"],
        #         "min2": table[int(j)]["min2"],
        #         "max2": table[int(j)]["max2"],
        #         "N": N,
        #         "errN": errN,
        #         "Npass": Npass,
        #         "errNpass": errNpass,
        #         "EffRel": EffRel,
        #         "errEffRel": errEffRel,
        #         "EffAbs": EffAbs,
        #         "errEffAbs": errEffAbs,
        #     }
        #     # print table[j]
    return newTable


def CombineEfficiencies(tableList):
    newTable = {}
    nLines = len(tableList[0])
    weightList = [t[1]["TEfficiencyAbs"].GetWeight() for t in tableList]
    firstTable = tableList[0]
    for j in range(0, nLines):
        nPass = 0
        errNpassSqr = 0
        for i, t in enumerate(tableList):
            nPass += float(t[j]["Npass"])*weightList[i]
            errNpassSqr += float(t[j]["errNpassSqr"])*pow(weightList[i], 2)
        if j > 0:
            # ideally, we'd be more accurate with this
            # - different processes should be combined, not added
            # TODO FIXME
            # if len(tableList) > 1:
            #     coll = r.TList()
            #     for o in [t[j]["TEfficiencyRel"] for t in tableList]:
            #         coll.AddLast(o)
            #     grRel = r.TEfficiency.Combine(coll)
            #     effRel = grRel.GetY()[0]
            #     effRelErr = max(grRel.GetErrorYhigh(0), grRel.GetErrorYlow(0))
            #     # print "CombineEfficiencies() -- varName={} Npass={} effRel={}".format(firstTable[int(j)]["variableName"], nPass, effRel)
            #     coll = r.TList()
            #     for o in [t[j]["TEfficiencyAbs"] for t in tableList]:
            #         coll.AddLast(o)
            #     grAbs = r.TEfficiency.Combine(coll)
            #     effAbs = grAbs.GetY()[0]
            #     effAbsErr = max(grAbs.GetErrorYhigh(0), grAbs.GetErrorYlow(0))
            # else:
            #     effRel = firstTable[j]["TEfficiencyRel"].GetEfficiency(1)
            #     effRelErr = max(firstTable[j]["TEfficiencyRel"].GetEfficiencyErrorLow(1), firstTable[j]["TEfficiencyRel"].GetEfficiencyErrorUp(1))
            #     effAbs = firstTable[j]["TEfficiencyAbs"].GetEfficiency(1)
            #     effAbsErr = max(firstTable[j]["TEfficiencyAbs"].GetEfficiencyErrorLow(1), firstTable[j]["TEfficiencyAbs"].GetEfficiencyErrorUp(1))
            firstRelEff = firstTable[j]["TEfficiencyRel"]
            for o in [t[j]["TEfficiencyRel"] for t in tableList[1:]]:
                firstRelEff.Add(o)
            firstRelEff.SetStatisticOption(r.TEfficiency.kFNormal)
            effRel = firstRelEff.GetEfficiency(1)
            # print "INFO: CombineEfficiencies() -- varName={} Npass={} (N-1)pass effRel={}".format(firstTable[int(j)]["variableName"], nPass, firstRelEff.GetPassedHistogram().GetBinContent(1), effRel)
            effRelErr = max(firstRelEff.GetEfficiencyErrorLow(1), firstRelEff.GetEfficiencyErrorUp(1))
            firstAbsEff = firstTable[j]["TEfficiencyAbs"]
            for o in [t[j]["TEfficiencyAbs"] for t in tableList[1:]]:
                firstAbsEff.Add(o)
            firstAbsEff.SetStatisticOption(r.TEfficiency.kFNormal)
            effAbs = firstAbsEff.GetEfficiency(1)
            effAbsErr = max(firstAbsEff.GetEfficiencyErrorLow(1), firstAbsEff.GetEfficiencyErrorUp(1))
        else:
            effRel = effAbs = 1
            effRelErr = effAbsErr = 0

        newTable[int(j)] = {
            "variableName": firstTable[int(j)]["variableName"],
            "min1": firstTable[int(j)]["min1"],
            "max1": firstTable[int(j)]["max1"],
            "min2": firstTable[int(j)]["min2"],
            "max2": firstTable[int(j)]["max2"],
            # "N": nTot,
            # "errNSqr": errNSqr,
            "Npass": nPass,
            "errNpass": math.sqrt(errNpassSqr),
            "EffRel": effRel,
            "errEffRel": effRelErr,
            "EffAbs": effAbs,
            "errEffAbs": effAbsErr,
        }
    return newTable

# --- TODO: FIX TABLE FORMAT (NUMBER OF DECIMAL PLATES AFTER THE 0)


def WriteTable(table, name, file, printToScreen=False):
    print("### "+name, file=file)
    print("#id".rjust(4, " "), end=' ', file=file)
    print("variableName".rjust(35), end=' ', file=file)
    print("min1".rjust(15), end=' ', file=file)
    print("max1".rjust(15), end=' ', file=file)
    print("min2".rjust(15), end=' ', file=file)
    print("max2".rjust(15), end=' ', file=file)
    print("Npass".rjust(17), end=' ', file=file)
    print("errNpass".rjust(17), end=' ', file=file)
    print("EffRel".rjust(15), end=' ', file=file)
    print("errEffRel".rjust(15), end=' ', file=file)
    print("EffAbs".rjust(15), end=' ', file=file)
    print("errEffAbs".rjust(15), file=file)

    for j, line in enumerate(table):
        print(str(j).rjust(4, " "), end=' ', file=file)
        print(table[j]["variableName"].rjust(35), end=' ', file=file)
        print(table[j]["min1"].rjust(15), end=' ', file=file)
        print(table[j]["max1"].rjust(15), end=' ', file=file)
        print(table[j]["min2"].rjust(15), end=' ', file=file)
        print(table[j]["max2"].rjust(15), end=' ', file=file)
        ###
        if table[j]["Npass"] >= 0.1:
            print(("%.04f" % table[j]["Npass"]).rjust(17), end=' ', file=file)
        else:
            print(("%.04e" % table[j]["Npass"]).rjust(17), end=' ', file=file)
        ###
        if table[j]["errNpass"] >= 0.1:
            print(("%.04f" % table[j]["errNpass"]).rjust(17), end=' ', file=file)
        else:
            print(("%.04e" % table[j]["errNpass"]).rjust(17), end=' ', file=file)
        ###
        if table[j]["EffRel"] >= 0.1:
            print(("%.04f" % table[j]["EffRel"]).rjust(15), end=' ', file=file)
        else:
            print(("%.04e" % table[j]["EffRel"]).rjust(15), end=' ', file=file)
        ###
        if table[j]["errEffRel"] >= 0.1:
            print(("%.04f" % table[j]["errEffRel"]).rjust(15), end=' ', file=file)
        else:
            print(("%.04e" % table[j]["errEffRel"]).rjust(15), end=' ', file=file)
        ###
        if table[j]["EffAbs"] >= 0.1:
            print(("%.04f" % table[j]["EffAbs"]).rjust(15), end=' ', file=file)
        else:
            print(("%.04e" % table[j]["EffAbs"]).rjust(15), end=' ', file=file)
        ###
        if table[j]["errEffAbs"] >= 0.1:
            print(("%.04f" % table[j]["errEffAbs"]).rjust(15), file=file)
        else:
            print(("%.04e" % table[j]["errEffAbs"]).rjust(15), file=file)
        ###

    print("\n", file=file)

    # --- print to screen
    if printToScreen:
        print("\n")
        print("### "+name)
        print("#id".rjust(4, " "), end=' ')
        print("variableName".rjust(35), end=' ')
        print("min1".rjust(15), end=' ')
        print("max1".rjust(15), end=' ')
        print("min2".rjust(15), end=' ')
        print("max2".rjust(15), end=' ')
        print("Npass".rjust(17), end=' ')
        print("errNpass".rjust(17), end=' ')
        print("EffRel".rjust(15), end=' ')
        print("errEffRel".rjust(15), end=' ')
        print("EffAbs".rjust(15), end=' ')
        print("errEffAbs".rjust(15))

        for j, line in enumerate(table):
            print(str(j).rjust(4, " "), end=' ')
            print(table[j]["variableName"].rjust(35), end=' ')
            print(table[j]["min1"].rjust(15), end=' ')
            print(table[j]["max1"].rjust(15), end=' ')
            print(table[j]["min2"].rjust(15), end=' ')
            print(table[j]["max2"].rjust(15), end=' ')
            ###
            if table[j]["Npass"] >= 0.1:
                print(("%.04f" % table[j]["Npass"]).rjust(17), end=' ')
            else:
                print(("%.04e" % table[j]["Npass"]).rjust(17), end=' ')
            ###
            if table[j]["errNpass"] >= 0.1:
                print(("%.04f" % table[j]["errNpass"]).rjust(17), end=' ')
            else:
                print(("%.04e" % table[j]["errNpass"]).rjust(17), end=' ')
            ###
            if table[j]["EffRel"] >= 0.1:
                print(("%.04f" % table[j]["EffRel"]).rjust(15), end=' ')
            else:
                print(("%.04e" % table[j]["EffRel"]).rjust(15), end=' ')
            ###
            if table[j]["errEffRel"] >= 0.1:
                print(("%.04f" % table[j]["errEffRel"]).rjust(15), end=' ')
            else:
                print(("%.04e" % table[j]["errEffRel"]).rjust(15), end=' ')
            ###
            if table[j]["EffAbs"] >= 0.1:
                print(("%.04f" % table[j]["EffAbs"]).rjust(15), end=' ')
            else:
                print(("%.04e" % table[j]["EffAbs"]).rjust(15), end=' ')
            ###
            if table[j]["errEffAbs"] >= 0.1:
                print(("%.04f" % table[j]["errEffAbs"]).rjust(15))
            else:
                print(("%.04e" % table[j]["errEffAbs"]).rjust(15))
            ###


def GetSampleHistosFromTFile(tfileName, sample, keepHistName=True):
    histNameToHistDict = {}
    if tfileName.startswith("/eos/cms"):
        tfileName = "root://eoscms/" + tfileName
    elif tfileName.startswith("/eos/user"):
        tfileName = "root://eosuser/" + tfileName
    tfile = r.TFile.Open(tfileName)
    for key in tfile.GetListOfKeys():
        histoName = key.GetName()
        htemp = key.ReadObj()
        if not htemp or htemp is None:
            raise RuntimeError("failed to get histo named:", histoName, "from file:", tfile.GetName())
        r.SetOwnership(htemp, True)
        if htemp.InheritsFrom("TH1"):
            htemp.SetDirectory(0)
        histNameToHistDict[histoName] = htemp
    sortedDict = dict(sorted(histNameToHistDict.items()))
    for htemp in sortedDict.values():
        if not keepHistName:
            hname = htemp.GetName()
            if "cutHisto" in hname:
                prefixEndPos = hname.rfind("cutHisto")
            elif len(re.findall("__", hname)) > 2:
                raise RuntimeError("Found hist {} in file {} and unclear how to shorten its name".format(hname, tfile.GetName()))
            else:
                prefixEndPos = hname.rfind("__")+2
            htemp.SetName(hname[prefixEndPos:])
    sampleHistos = list(sortedDict.values())
    tfile.Close()
    if len(sampleHistos) < 1:
        raise RuntimeError(
                "GetSampleHistosFromTFile({}, {}) -- failed to read any histos for the sampleName from this file!".format(
                    tfile.GetName(), sampleName))
    return sampleHistos


def ExtractBranchTitles(systHist, tmap):
    systDict = {}
    specialSysts = ["LHEPdfWeightMC_UpComb", "LHEPdfWeightMC_DownComb", "LHEPdfWeightHessian_NominalComb", "LHEPdf_UpComb", "LHEPdf_DownComb", "LHEScale_UpComb", "LHEScale_DownComb"]
    for yBin in range(1, systHist.GetNbinsY()+1):
        systName = systHist.GetYaxis().GetBinLabel(yBin)
        if any(substring in systName for substring in specialSysts):
            continue  # skip the special bins we may add ourselves
        branchTitleList = []
        mapObject = tmap.FindObject(systName)
        if not mapObject:
            # assume it's an array syst, so try to match stripping off the _N part
            mapObject = tmap.FindObject(systName[:systName.rfind("_")])
        if not mapObject:
            raise RuntimeError("For syst {}, using systHist {} and map {}, could not find matching map object for syst name nor for array type systName={}.".format(
                systName, systHist.GetName(), tmap.GetName(), systName[:systName.rfind("_")]))
        #print("INFO: for syst {}, found matching mapObject key: {}, value: {}".format(systName, mapObject.Key(), mapObject.Value()))
        branchTitleListItr = r.TIter(mapObject.Value())
        branchTitle = branchTitleListItr.Next()
        while branchTitle:
            branchTitleList.append(branchTitle.GetName())
            branchTitle = branchTitleListItr.Next()
        systDict[systName] = branchTitleList
    return systDict


def GetBranchTitle(systName, sampleName, systDict):
    keys = [syst for syst in systDict.keys() if syst == systName]
    if len(keys) == 1:
        return "", keys
    if len(keys) < 1:
        # try for an array branch
        keys = [syst for syst in systDict.keys() if syst[:syst.rfind("_")] == systName]
    # here we have to handle the PDF syst somehow
    if len(keys) > 0:
        #print("INFO (1) systName={}, keys={}, systDict.keys()={}".format(systName, keys, systDict.keys()))
        if type(systDict[keys[0]]) is dict:
            branchTitleLists = [systDict[key]["branchTitles"] for key in keys]
        else:
            branchTitleLists = [systDict[key] for key in keys]
    else:
        #print("INFO (2) systName={}, keys={}, systDict.keys()={}".format(systName, keys, systDict.keys()))
        branchTitleLists = []
    branchTitleLists = [list(item) for item in set(tuple(titleList) for titleList in branchTitleLists)]
    # branchTitleLists = set(tuple(titleList) for titleList in branchTitleLists)
    if len(branchTitleLists) > 1:
        raise RuntimeError("For sample {} and systName {}, found multiple branch title lists: {}".format(sampleName, systName, branchTitleLists))
    if len(branchTitleLists) < 1:
        # this can happen when there are no events passing selections in the sample, so it's not clearly a problem
        raise RuntimeError("For sample {} and systName {}, found zero branch title lists; you probably need to manually specify a flat systematic. systDict.keys()={}".format(sampleName, systName, systDict.keys()))
        #return "", []
    branchTitleList = branchTitleLists[0]
    if len(branchTitleList) > 1:
        raise RuntimeError("For sample {} and systName {}, found multiple branch titles: {}".format(sampleName, systName, branchTitleList))
    branchTitle = branchTitleList[0]
    return branchTitle, keys


def ParseShapeBranchTitle(branchTitle):
    validIndices = []
    validTitles = []
    # one format of title: 'LHE scale variation weights (w_var / w_nominal); [0] is muR=0.50000E+00 muF=0.50000E+00 ; [1] is muR=0.50000E+00 muF=0.10000E+01 ; " ... "[7] is muR=0.20000E+01 muF=0.10000E+01 ; [8] is muR=0.20000E+01 muF=0.20000E+01"'
    # a second format: 'LHE scale variation weights (w_var / w_nominal); [0] is renscfact=0.5d0 facscfact=0.5d0 ; [1] is renscfact=0.5d0 facscfact=1d0 ; " ... "[7] is renscfact=2d0 facscfact=1d0 ; [8] is renscfact=2d0 facscfact=2d0"'
    # found in UL: 'LHE scale variation weights (w_var / w_nominal); [0] is MUF="0.5" MUR="0.5"; [1] is MUF="1.0" MUR="0.5"; ' ... '[7] is MUF="1.0" MUR="2.0"; [8] is MUF="2.0" MUR="2.0"'
    regEx = re.compile(r'\[(\d+)\][\D\s]+="?([0-9.+Ed]+)"?[\D\s]+="?([0-9.+Ed]+)"?')
    match = re.search(regEx, branchTitle)
    searchStart = 0
    while match:
        groups = match.groups()
        end = match.end()
        index = int(groups[0])
        muR = float(groups[1].replace("d", "E+"))
        muF = float(groups[2].replace("d", "E+"))
        ratio = muR/muF
        if ratio < 3.9 and ratio > 0.3:  # leave some room for float rounding
            # print "INFO: keep this variation with title={}; index={}, ratio={}".format(branchTitle[searchStart:searchStart+end], index, ratio)
            validIndices.append(str(index))
            validTitles.append(branchTitle[searchStart:searchStart+end])
        # else:
        #     print "INFO: REJECT this variation with title={}; index={}, ratio={}".format(branchTitle[searchStart:searchStart+end], index, ratio)
        searchStart += end
        match = re.search(regEx, branchTitle[searchStart:])
    if len(validIndices) < 1:
        raise RuntimeError("Failed to parse branch title which looks like '{}'".format(branchTitle))
    return validIndices, validTitles


def CalculateShapeSystematic(hist, sampleName, systDict):
    verbose = False
    result = {}
    systName = "LHEScaleWeight"
    branchTitle, shapeKeys = GetBranchTitle(systName, sampleName, systDict)
    if verbose:
        print("INFO: For sampleName={}, systName={}, found branch title={} and shapeKeys={}".format(sampleName, systName, branchTitle, shapeKeys))
        # print "INFO: For sampleName={}, systName={}, found branch title={}".format(sampleName, systName, branchTitle)
    validIndices, shapeTitles = ParseShapeBranchTitle(branchTitle)
    validShapeKeys = [shapeKey for shapeKey in shapeKeys if shapeKey[shapeKey.rfind("_")+1:] in validIndices]
    validYbins = [yBin for yBin in range(0, hist.GetNbinsY()+2) if hist.GetYaxis().GetBinLabel(yBin) in validShapeKeys]
    for xBin in range(0, hist.GetNbinsX()+2):
        nominal = hist.GetBinContent(xBin, 1)
        shapeYields = [hist.GetBinContent(xBin, yBin) for yBin in validYbins]
        if verbose:
            print("\tINFO: For sampleName={}, systName={}, found validShapeKeys={}, valid shapeTitles={} and shapeYields={}".format(
                    sampleName, systName, validShapeKeys, shapeTitles, shapeYields))
        deltas = [shapeYield-nominal for shapeYield in shapeYields]
        deltasAbs = [math.fabs(delta) for delta in deltas]
        maxDeltaIdx = deltasAbs.index(max(deltasAbs))
        maxDelta = deltas[maxDeltaIdx]
        if verbose:
            print("\tINFO: For sampleName={}, systName={}, found deltas={} with maxDelta={} and nominal={}".format(
                    sampleName, systName, deltas, maxDelta, nominal))
        result[xBin] = maxDelta
    return result, validYbins


def GetPDFVariationType(branchTitle):
    # example title: "LHE pdf variation weights (w_var / w_nominal) for LHA IDs 292200 - 292302"
    # see: https://lhapdf.hepforge.org/pdfsets.html
    # NNPDF3.0 is always MC; NNPDF3.1 can be either, but usually Hessian in CMS samples
    if "292200" in branchTitle:
        pdfType = "mc"
        pdfName = "NNPDF30_nlo_nf_5_pdfas"
    elif "292201" in branchTitle:
        pdfType = "mcNoCentral"
        pdfName = "NNPDF30_nlo_nf_5_pdfas"
    elif "262000" in branchTitle:
        pdfType = "mc"
        pdfName = "NNPDF30_lo_as_0118"
    elif "260001" in branchTitle:
        pdfType = "mcNoCentral"
        pdfName = "NNPDF30_lo_as_0118"
    elif "91400" in branchTitle:
        pdfType = "hessian"
        pdfName = "PDF4LHC15_nnlo_30_pdfas"
    elif "306000" in branchTitle:
        pdfType = "hessian"
        pdfName = "NNPDF31_nnlo_hessian_pdfas"
    elif "325300" in branchTitle:
        pdfType = "hessian"
        pdfName = "NNPDF31_nnlo_as_0118_mc_hessian_pdfas"
    elif "320900" in branchTitle:
        pdfType = "mc"
        pdfName = "NNPDF31_nnlo_as_0118_nf_4"
    elif "325500" in branchTitle:
        pdfType = "hessian"
        pdfName = "NNPDF31_nnlo_as_0118_nf_4_mc_hessian"
    else:
        raise RuntimeError("Can't determine whether branch title '{}' is a Hessian or MC set".format(branchTitle))
    return pdfType, pdfName


def CalculatePDFSystematic(hist, sampleName, systDict):
    systName = "LHEPdfWeight"
    branchTitle, pdfKeys = GetBranchTitle(systName, sampleName, systDict)
    if len(pdfKeys) < 1:
        # this should mean that we don't have any PDF systs in the hist
        return np.zeros(hist.GetNbinsX()+2), np.zeros(hist.GetNbinsX()+2), []
    #if len(pdfKeys) == 1:
    #    # we have an exactly matching PDF syst key; hwe manually specified a flat syst
    #    # assumes that the number here is < 1
    #    return str(1 + systDict[systName][selection]), systDict[systName][selection], systDict[systName][selection], True
    # print "INFO: For sampleName={}, systName={}, found branch title={}".format(sampleName, systName, branchTitle)
    # print len(pdfKeys), "sorted(pdfKeys)=", sorted(pdfKeys, key=lambda x: int(x[x.rfind("_")+1:]))
    pdfVariationType, pdfName = GetPDFVariationType(branchTitle)
    #print("INFO: CalculatePDFSystematic(): For sampleName={}, systName={}, found branch title={} and PDFType={}".format(sampleName, systName, branchTitle, pdfVariationType))
    if pdfVariationType != "mcNoCentral":
        pdfKeys.remove("LHEPdfWeight_0")  # don't consider index 0, central value
    if "mc" in pdfVariationType:
        pdfSystDeltasUp, pdfSystDeltasDown, yBins = CalculatePDFVariationMC(hist, sampleName, pdfKeys)
    elif pdfVariationType == "hessian":
        pdfSystDeltasUp, pdfSystDeltasDown, yBins = CalculatePDFVariationHessian(hist, sampleName, pdfKeys)
    else:
        raise RuntimeError("Unknown PDF type '{}'. Can't calculate the PDF variations for this type (unimplemented).".format(pdfVariationType))
    return pdfSystDeltasUp, pdfSystDeltasDown, yBins


def CalculatePDFVariationMC(hist, sampleName, pdfKeys, verbose=False):
    pdfKeys = sorted(pdfKeys, key=lambda x: int(x[x.rfind("_")+1:]))
    # now, if we still have over 100, remove the last two
    if len(pdfKeys) > 100:
        pdfKeys = pdfKeys[:-2]
    elif len(pdfKeys) == 32:
        pdfKeys = pdfKeys[:-2]
    if verbose:
        print("INFO: CalculatePDFVariationMC() -- sampleName={}, we now have {} pdf variations to consider".format(sampleName, len(pdfKeys)), flush=True)
    validYbins = [yBin for yBin in range(0, hist.GetNbinsY()+2) if hist.GetYaxis().GetBinLabel(yBin) in pdfKeys]
    deltaUp = {}
    deltaDown = {}
    for xBin in range(0, hist.GetNbinsX()+2):
        nominal = hist.GetBinContent(xBin, 1)
        pdfYieldsUnsorted = [hist.GetBinContent(xBin, yBin) for yBin in validYbins]
        # Order the 100 yields and take the 84th and 16th.
        # See eq. 25 here: https://arxiv.org/pdf/1510.03865.pdf
        pdfYields = sorted(pdfYieldsUnsorted)
        if len(pdfKeys) == 100:
            pdfUp = pdfYields[83]
            pdfDown = pdfYields[15]
        elif len(pdfKeys) == 30:
            pdfUp = pdfYields[27]
            pdfDown = pdfYields[5]
        else:
            raise RuntimeError("Could not determine MC PDF variations as we have {} PDF keys".format(len(pdfKeys)), flush=True)
        deltaUp[xBin] = pdfUp-nominal
        deltaDown[xBin] = pdfDown-nominal
        if verbose:
            print("INFO: CalculatePDFVariationMC() -- for sampleName={}, xBin={}, nominal={}; pdfUp={}, pdfDown={}; pdfUp-nominal={}, pdfDown-nominal={}".format(
                    sampleName, xBin, nominal, pdfUp, pdfDown, pdfUp-nominal, pdfDown-nominal), flush=True)
            if len(pdfKeys) == 100:
                print("INFO: CalculatePDFVariationMC() -- yield 15 = {}; yield 83 = {}".format(pdfYields[15], pdfYields[83]), flush=True)
            elif len(pdfKeys) == 30:
                print("INFO: CalculatePDFVariationMC() -- yield 27 = {}; yield 5 = {}".format(pdfYields[27], pdfYields[5]), flush=True)
            # print("\tINFO: CalculatePDFVariationMC() -- pdfYields={}".format(pdfYields), flush=True)
    return deltaUp, deltaDown, validYbins


def CalculatePDFVariationHessian(hist, sampleName, pdfKeys=[], nominalBin=1, systDict={}, verbose=False):
    # if len(pdfKeys) < 1:
    #     systName = "LHEPdfWeight"
    #     pdfKeys = [syst for syst in systDict.keys() if syst[:syst.rfind("_")] == systName]
    #     pdfKeys.remove("LHEPdfWeight_0")  # don't consider index 0, central value
    # Sum in quadrature central - var, and use this as a symmetric uncertainty (both the up and down)
    pdfKeys = sorted(pdfKeys, key=lambda x: int(x[x.rfind("_")+1:]))
    # now, if we still have over 100, remove the last two
    if len(pdfKeys) > 100:
        pdfKeys = pdfKeys[:-2]
    elif len(pdfKeys) == 32:
        pdfKeys = pdfKeys[:-2]
    if verbose:
        print("INFO: sampleName={}, we now have {} pdf variations to consider".format(sampleName, len(pdfKeys)))
    validYbins = [yBin for yBin in range(0, hist.GetNbinsY()+2) if hist.GetYaxis().GetBinLabel(yBin) in pdfKeys]
    deltaUp = {}
    for xBin in range(0, hist.GetNbinsX()+2):
        nominal = hist.GetBinContent(xBin, nominalBin)
        pdfYields = [hist.GetBinContent(xBin, yBin) for yBin in validYbins]
        pdfVars = [pow(nominal-pdfYield, 2) for pdfYield in pdfYields]
        pdfDeltaX = math.sqrt(sum(pdfVars))
        deltaUp[xBin] = pdfDeltaX
    return deltaUp, deltaUp, validYbins


def GetShortHistoName(histName):
    if "histo1D" in histName or "histo2D" in histName or "histo3D" in histName or "profile1D" in histName:
        return histName.split(histName.split("__")[1])[1].strip("_")
    else:
        return histName


def UpdateHistoDict(sampleHistoDict, pieceHistoList, piece, sample="", plotWeight=1.0, correlateLHESystematics=False, isData=False):
    # print "INFO: UpdateHistoDict for sample {}".format(sample)
    # sys.stdout.flush()
    systNameToBranchTitleDict = {}
    if not isData:
        sampleTMap = next((x for x in pieceHistoList if x.ClassName() == "TMap" and "systematicNameToBranchesMap" in x.GetName()), None)
        sampleSystHist = next((x for x in pieceHistoList if x.GetName() == "systematics"), None)
        if sampleSystHist is not None:
            systNameToBranchTitleDict = ExtractBranchTitles(sampleSystHist, sampleTMap)
        else:
            print("WARN: Did not find systematics hist for the sample {}, though it's not data.".format(sample))
    idx = 0
    for pieceHisto in pieceHistoList:
        pieceHistoName = pieceHisto.GetName()
        pieceHisto.SetName(GetShortHistoName(pieceHistoName))
        if idx in sampleHistoDict:
            sampleHisto = sampleHistoDict[idx]
            if pieceHisto.GetName() not in sampleHisto.GetName():
                raise RuntimeError(
                        "ERROR: non-matching histos between sample {} hist with name '{}' and piece {} hist with name '{}'. Quitting here".format(
                            sample, sampleHisto.GetName(), piece, pieceHisto.GetName()))
        # print("INFO: UpdateHistoDict(): sample={}, piece={}, pieceHisto={}, idx={}".format(sample, piece, pieceHisto.GetName(), idx), flush=True)
        if "eventspassingcuts" in pieceHisto.GetName().lower() and "unscaled" not in pieceHisto.GetName().lower():
            if pieceHisto.GetName()+"_unscaled" not in [histo.GetName() for histo in pieceHistoList]:
                # create new EventsPassingCuts hist that doesn't have scaling/reweighting by int. lumi.
                unscaledEvtsPassingCuts = copy.deepcopy(pieceHisto)
                unscaledEvtsPassingCuts.SetNameTitle(pieceHisto.GetName()+"_unscaled", pieceHisto.GetTitle()+"_unscaled")
                #print("INFO: UpdateHistoDict(): sample={}, piece={}, create new EventsPassingCuts hist from {} that doesn't have scaling/reweighting by int. lumi. idx is now {}".format(sample, piece, pieceHisto.GetName(), idx), flush=True)
                sampleHistoDict = updateSample(sampleHistoDict, unscaledEvtsPassingCuts, idx, piece, sample, 1.0, correlateLHESystematics, isData, systNameToBranchTitleDict)
                idx += 1
        #print("INFO: updateSample for sample={}, correlateLHESystematics={}".format(sample, correlateLHESystematics), flush=True)
        #print("INFO: [1] UpdateHistoDict(): sample={}, piece={}, pieceHisto={}, idx={}".format(sample, piece, pieceHisto.GetName(), idx), flush=True)
        sampleHistoDict = updateSample(sampleHistoDict, pieceHisto, idx, piece, sample, plotWeight, correlateLHESystematics, isData, systNameToBranchTitleDict)
        # if idx < 2:
        #     print "\tINFO: UpdateHistoDict for sample {}: added pieceHisto {} with entries {} to sampleHistoDict[idx], which has name {} and entries {}".format(
        #             sample, pieceHisto.GetName(), pieceHisto.GetEntries(), sampleHistoDict[idx].GetName(), sampleHistoDict[idx].GetEntries())
        idx += 1
    # check TMap consistency
    #sampleTMap = next((x for x in pieceHistoList if x.ClassName() == "TMap" and "systematicNameToBranchesMap" in x.GetName()), None)
    comboTMap = next((x for x in list(sampleHistoDict.values()) if x.ClassName() == "TMap" and "systematicNameToBranchesMap" in x.GetName()), None)
    comboSystHist = next((x for x in list(sampleHistoDict.values()) if x.GetName().endswith("systematics")), None)
    # if comboSystHist is None:
        # print "Could not find comboSystHist in sampleHistoDict"
        # print [x.GetName() for x in sampleHistoDict.values() if "systematics" in x.GetName()]
    if not isData and comboSystHist is not None:
        # ignore pdf/scale weight bins, since we handle them specially
        binLabels = list(comboSystHist.GetYaxis().GetLabels())
        binLabels = [label for label in binLabels if "pdf" not in label.GetString().Data().lower() and "scale" not in label.GetString().Data().lower()]
        CheckSystematicsTMapConsistency(comboTMap, sampleTMap, binLabels)
    return sampleHistoDict


def updateSample(dictFinalHistoAtSample, htemp, h, piece, sample, plotWeight, correlateLHESystematics, isData, systNameToBranchTitleDict):
    histoName = htemp.GetName()
    histoTitle = htemp.GetTitle()
    if "systematics" in histoName.lower():
        if h in dictFinalHistoAtSample:
            if list(dictFinalHistoAtSample[h].GetYaxis().GetLabels()) != list(htemp.GetYaxis().GetLabels()):
                if IsHistEmpty(dictFinalHistoAtSample[h]):
                    del dictFinalHistoAtSample[h]  # replace the empty hist with a filled one
                elif IsHistEmpty(htemp):
                    # For systematics hists, these can have the wrong number of bins in the case where the tree read by the analysis has zero entries
                    #    because any array systematics will have size zero, instead of the actual size.
                    # In the case where the input tree has zero entries, the systematics hist will be empty anyway, so we can safely skip it.
                    return dictFinalHistoAtSample
    if "systematicsdiffs" in histoName.lower():
        # ignore systematicsDiffs hist here; we remake this at the end so that it's correct
        return dictFinalHistoAtSample
    # thanks Riccardo
    # init histo if needed
    firstHistForSample = False
    if h not in dictFinalHistoAtSample:
        firstHistForSample = True
        if "TH2" in htemp.__repr__():
            dictFinalHistoAtSample[h] = r.TH2F()
            if sample != "":
                dictFinalHistoAtSample[h].SetNameTitle("histo2D__" + sample + "__" + histoName, histoTitle)
            else:
                dictFinalHistoAtSample[h].SetNameTitle(histoName, histoTitle)
            dictFinalHistoAtSample[h].SetBins(
                htemp.GetNbinsX(),
                htemp.GetXaxis().GetXmin(),
                htemp.GetXaxis().GetXmax(),
                htemp.GetNbinsY(),
                htemp.GetYaxis().GetBinLowEdge(1),
                htemp.GetYaxis().GetBinUpEdge(htemp.GetNbinsY()),
            )
            htemp.GetXaxis().Copy(dictFinalHistoAtSample[h].GetXaxis())
            htemp.GetYaxis().Copy(dictFinalHistoAtSample[h].GetYaxis())
            # continue
        elif "TH1" in htemp.ClassName():
            dictFinalHistoAtSample[h] = r.TH1D()
            if sample != "":
                dictFinalHistoAtSample[h].SetNameTitle("histo1D__" + sample + "__" + histoName, histoTitle)
            else:
                dictFinalHistoAtSample[h].SetNameTitle(histoName, histoTitle)
            dictFinalHistoAtSample[h].SetBins(
                htemp.GetNbinsX(),
                htemp.GetXaxis().GetXmin(),
                htemp.GetXaxis().GetXmax(),
            )
            htemp.GetXaxis().Copy(dictFinalHistoAtSample[h].GetXaxis())
        elif "TProfile" in htemp.ClassName():
            dictFinalHistoAtSample[h] = r.TProfile()
            if sample != "":
                dictFinalHistoAtSample[h].SetNameTitle("profile1D__" + sample + "__" + histoName, histoTitle)
            else:
                dictFinalHistoAtSample[h].SetNameTitle(histoName, histoTitle)
            dictFinalHistoAtSample[h].SetBins(
                htemp.GetNbinsX(),
                htemp.GetXaxis().GetXmin(),
                htemp.GetXaxis().GetXmax(),
            )
            htemp.GetXaxis().Copy(dictFinalHistoAtSample[h].GetXaxis())
        elif "TH3" in htemp.ClassName():
            dictFinalHistoAtSample[h] = r.TH3D()
            if sample != "":
                dictFinalHistoAtSample[h].SetNameTitle("histo3D__" + sample + "__" + histoName, histoTitle)
            else:
                dictFinalHistoAtSample[h].SetNameTitle(histoName, histoTitle)
            dictFinalHistoAtSample[h].SetBins(
                htemp.GetNbinsX(),
                htemp.GetXaxis().GetXmin(),
                htemp.GetXaxis().GetXmax(),
                htemp.GetNbinsY(),
                htemp.GetYaxis().GetBinLowEdge(1),
                htemp.GetYaxis().GetBinUpEdge(htemp.GetNbinsY()),
                htemp.GetNbinsZ(),
                htemp.GetZaxis().GetBinLowEdge(1),
                htemp.GetZaxis().GetBinUpEdge(htemp.GetNbinsZ()),
            )
            htemp.GetXaxis().Copy(dictFinalHistoAtSample[h].GetXaxis())
            htemp.GetYaxis().Copy(dictFinalHistoAtSample[h].GetYaxis())
            htemp.GetZaxis().Copy(dictFinalHistoAtSample[h].GetZaxis())
        elif "TMap" in htemp.ClassName() and "systematicNameToBranchesMap" in htemp.GetName():
            dictFinalHistoAtSample[h] = htemp.Clone()
            if sample != "":
                dictFinalHistoAtSample[h].SetName("tmap__" + sample + "__" + histoName)
            else:
                dictFinalHistoAtSample[h].SetName(histoName)
        elif "TObjString" in htemp.ClassName() and "Cut" in htemp.GetName():
            # skip
            return dictFinalHistoAtSample
        else:
            raise RuntimeError("not combining hist named '{}' with classtype of {}".format(htemp.GetName(), htemp.ClassName()))
        if "TMap" not in htemp.ClassName():
            dictFinalHistoAtSample[h].Sumw2()
    if "optimizerentries" in histoName.lower() or "noweight" in histoName.lower() or "unscaled" in histoName.lower():
        returnVal = dictFinalHistoAtSample[h].Add(htemp)
    else:
        if "TMap" in htemp.ClassName() and "systematicNameToBranchesMap" in histoName:
            # for this special TMap, check that the keys and values are consistent
            # recall: TObjString --> TList
            # print "INFO: checking systematicNameToBranchesMap consistency for piece {} in combined sample {}".format(piece, sample)
            # CheckSystematicsTMapConsistency(dictFinalHistoAtSample[h], htemp)
            # no-op
            return dictFinalHistoAtSample
        if "systematics" in histoName.lower() and not isData:
            pdfSysts = False
            labelsToAdd = ["LHEPdfWeightMC_UpComb", "LHEPdfWeightMC_DownComb", "LHEPdfWeightHessian_NominalComb", "LHEScaleWeight_maxComb"]
            if not any(substring in list(htemp.GetYaxis().GetLabels()) for substring in labelsToAdd):
                htemp = AddHistoBins(htemp, "y", labelsToAdd)
                if firstHistForSample:
                    dictFinalHistoAtSample[h] = AddHistoBins(dictFinalHistoAtSample[h], "y", labelsToAdd)
            else:
                pdfWeightMCDownCombBin = htemp.GetYaxis().FindFixBin("LHEPdfWeightMC_DownComb")
                pdfWeightMCUpCombBin = htemp.GetYaxis().FindFixBin("LHEPdfWeightMC_UpComb")
                pdfWeightHessianCombBin = htemp.GetYaxis().FindFixBin("LHEPdfWeightHessian_NominalComb")
                for xBin in range(0, htemp.GetNbinsX()+2):
                    mcUpContent = htemp.GetBinContent(xBin, pdfWeightMCUpCombBin)
                    mcDownContent = htemp.GetBinContent(xBin, pdfWeightMCDownCombBin)
                    hessianContent = htemp.GetBinContent(xBin, pdfWeightHessianCombBin)
                    if mcUpContent != 0 or mcDownContent != 0 or hessianContent != 0:
                        pdfSysts = True
                        break
            if not IsHistEmpty(htemp) and not pdfSysts:
                hessianNominalYields = np.zeros(htemp.GetNbinsX()+2)
                pdfSystDeltasUp = np.zeros(htemp.GetNbinsX()+2)
                pdfSystDeltasDown = np.zeros(htemp.GetNbinsX()+2)
                pdfVariationType = ""
                # case for combining between samples
                # 1. we have to calculate the PDF syst if it's an MC PDF
                #  - make two special bins to hold this
                #  - zero all the MC PDF weight bins
                #  - at the end, call from WriteHistos(), we combine any hessian vars with the MC vars into one bin (and any hessian into one bin)
                pdfVariationType, pdfName = GetPDFVariationType(GetBranchTitle("LHEPdfWeight", sample, systNameToBranchTitleDict)[0])
                if "mc" in pdfVariationType:
                    pdfSystDeltasUp, pdfSystDeltasDown, yBins = CalculatePDFSystematic(htemp, sample, systNameToBranchTitleDict)
                elif "hessian" in pdfVariationType:
                    hessianNominalYields = [htemp.GetBinContent(xBin, 1) for xBin in range(0, htemp.GetNbinsX()+2)]
                pdfWeightMCDownCombBin = htemp.GetYaxis().FindFixBin("LHEPdfWeightMC_DownComb")
                pdfWeightMCUpCombBin = htemp.GetYaxis().FindFixBin("LHEPdfWeightMC_UpComb")
                pdfWeightHessianCombBin = htemp.GetYaxis().FindFixBin("LHEPdfWeightHessian_NominalComb")
                for xBin in range(0, htemp.GetNbinsX()+2):
                    htemp.SetBinContent(xBin, pdfWeightMCUpCombBin, pdfSystDeltasUp[xBin])
                    htemp.SetBinContent(xBin, pdfWeightMCDownCombBin, pdfSystDeltasDown[xBin])
                    htemp.SetBinContent(xBin, pdfWeightHessianCombBin, hessianNominalYields[xBin])
                    htemp.SetBinError(xBin, pdfWeightMCUpCombBin, pdfSystDeltasUp[xBin])
                    htemp.SetBinError(xBin, pdfWeightMCDownCombBin, pdfSystDeltasDown[xBin])
                    htemp.SetBinError(xBin, pdfWeightHessianCombBin, hessianNominalYields[xBin])
                # zero all individual weight bins for MC PDF systs
                if "mc" in pdfVariationType:
                    pdfWeightLabels = [label.GetString().Data() for label in htemp.GetYaxis().GetLabels() if "LHEPdfWeight" in label.GetString().Data()]
                    pdfWeightLabels.remove("LHEPdfWeightMC_UpComb")
                    pdfWeightLabels.remove("LHEPdfWeightMC_DownComb")
                    pdfWeightLabels.remove("LHEPdfWeightHessian_NominalComb")
                    for xBin in range(0, htemp.GetNbinsX()+2):
                        for label in pdfWeightLabels:
                            yBin = htemp.GetYaxis().FindFixBin(label)
                            htemp.SetBinContent(xBin, yBin, 0)
                            htemp.SetBinError(xBin, yBin, 0)
                # 2. we have to calculate the scale syst
                ##   - replace the scale weights with one bin holding the max deviation
                scaleSystDeltas, yBins = CalculateShapeSystematic(htemp, sample, systNameToBranchTitleDict)
                lheScaleMaxCombBin = htemp.GetYaxis().FindFixBin("LHEScaleWeight_maxComb")
                for xBin in range(0, htemp.GetNbinsX()+2):
                    nominal = htemp.GetBinContent(xBin, 1)  # y-bin 1 always being nominal
                    htemp.SetBinContent(xBin, lheScaleMaxCombBin, scaleSystDeltas[xBin]+nominal)
                    htemp.SetBinError(xBin, lheScaleMaxCombBin, scaleSystDeltas[xBin])
            # check systematics hist bins
            systematicsListFromDictHist = list(dictFinalHistoAtSample[h].GetYaxis().GetLabels())
            systematicsListFromTempHist = list(htemp.GetYaxis().GetLabels())
            systsNotInTempHist = [label for label in systematicsListFromDictHist if label not in systematicsListFromTempHist]
            if len(systsNotInTempHist) > 0:
                print("\tINFO: some systematics absent from piece {}; removing them from {} for combined sample {}. Missing systematics: {}".format(
                        piece, htemp.GetName(), sample, systsNotInTempHist), flush=True)
                # print "SethLog: systematicsListFromTempHist={} and piece={}".format(systematicsListFromTempHist, piece)
                # print "SethLog: systematicsListFromDictHist={} and sample={}".format(systematicsListFromDictHist, sample)
                # remove systs that are missing from htemp
                dictFinalHistoAtSample[h] = RemoveHistoBins(dictFinalHistoAtSample[h], "y", systsNotInTempHist)
                # now update the systematics list, since we removed some
                systematicsListFromDictHist = list(dictFinalHistoAtSample[h].GetYaxis().GetLabels())
            # it can also happen that new systematics appear in htemp that aren't in the dict hist
            systsNotInDictHist = [label for label in systematicsListFromTempHist if label not in systematicsListFromDictHist]
            if len(systsNotInDictHist) > 0:
                print("\tINFO: some systematics absent from combined sample {}; removing them from {} for piece {}. Missing systematics: {}".format(
                        sample, htemp.GetName(), piece, systsNotInDictHist))
                # print "SethLog: systematicsListFromTempHist={} and piece={}".format(systematicsListFromTempHist, piece)
                # print "SethLog: systematicsListFromDictHist={} and sample={}".format(systematicsListFromDictHist, sample)
                # sys.stdout.flush()
                # remove systs that are missing from htemp
                htemp = RemoveHistoBins(htemp, "y", systsNotInDictHist)
            if htemp.GetNbinsX() != dictFinalHistoAtSample[h].GetNbinsX() or htemp.GetNbinsY() != dictFinalHistoAtSample[h].GetNbinsY():
                print("ERROR: piece {} has bin labels: {}".format(piece, list(htemp.GetYaxis().GetLabels())), flush=True)
                print("ERROR: sample {} has bin labels: {}".format(sample, list(dictFinalHistoAtSample[h].GetYaxis().GetLabels())), flush=True)
                raise RuntimeError("htemp {} from piece {} to be added has {} x bins and {} y bins, which is inconsistent with the existing hist from sample {}, which has {} x bins and {} y bins; different y bins={}".format(
                    htemp.GetName(), piece, htemp.GetNbinsX(), htemp.GetNbinsY(),
                    sample, dictFinalHistoAtSample[h].GetNbinsX(), dictFinalHistoAtSample[h].GetNbinsY(), str(list(set(htemp.GetYaxis().GetLabels()).symmetric_difference(set(dictFinalHistoAtSample[h].GetYaxis().GetLabels()))))))
            if list(htemp.GetYaxis().GetLabels()) != list(dictFinalHistoAtSample[h].GetYaxis().GetLabels()):
                print("ERROR: piece {} has bin labels: {}".format(piece, list(htemp.GetYaxis().GetLabels())), flush=True)
                print("ERROR: sample {} has bin labels: {}".format(sample, list(dictFinalHistoAtSample[h].GetYaxis().GetLabels())), flush=True)
                raise RuntimeError("htemp {} from piece {} to be added has y-axis bin labels {} which are inconsistent with existing hist from sample {}: {}".format(
                    htemp.GetName(), piece,list(htemp.GetYaxis().GetLabels()), sample, list(dictFinalHistoAtSample[h].GetYaxis().GetLabels())))
            if dictFinalHistoAtSample[h].GetXaxis().GetLabels():
                if list(htemp.GetXaxis().GetLabels()) != list(dictFinalHistoAtSample[h].GetXaxis().GetLabels()):
                    raise RuntimeError("htemp {} from piece {} to be added has x-axis bin labels {} which are inconsistent with existing hist from sample {}: {}".format(
                        htemp.GetName(), piece, list(htemp.GetXaxis().GetLabels()), sample, list(dictFinalHistoAtSample[h].GetXaxis().GetLabels())))
                
        # Sep. 17 2017: scale first, then add with weight=1 to have "entries" correct
        htemp.Scale(plotWeight)
        #r.gDebug = 3
        #r.gErrorIgnoreLevel = r.kPrint
        #if "Mee_BkgControlRegion"==histoName:
        #    print("SICINFO: adding hist named '{}' to {} of class {}; htemp class={}".format(histoName, dictFinalHistoAtSample[h].GetName(), dictFinalHistoAtSample[h].ClassName(), htemp.ClassName()))
        #    print("SICINFO: adding hist named '{}' with {} xbins to hist with {} xbins; htemp has {} ybins and hist has {} ybins".format(histoName, htemp.GetNbinsX(), dictFinalHistoAtSample[h].GetNbinsX(), htemp.GetNbinsY(), dictFinalHistoAtSample[h].GetNbinsY()))
        #    sys.stdout.flush()
        returnVal = dictFinalHistoAtSample[h].Add(htemp)
        #r.gDebug = 0
        #r.gErrorIgnoreLevel = r.kError
    # if 'OptBinLQ60' in histoName:
    #  if dictFinalHistoAtSample[h].GetBinContent(binToExamine) != 0:
    #    print 'AFTER Add',histoName,'hist: sample=',sample,'bin',binToExamine,'content=',dictFinalHistoAtSample[h].GetBinContent(binToExamine),' error=',dictFinalHistoAtSample[h].GetBinError(binToExamine),'relError=',dictFinalHistoAtSample[h].GetBinError(binToExamine)/dictFinalHistoAtSample[h].GetBinContent(binToExamine)
    #    print
    if not returnVal:
        raise RuntimeError("ERROR: Failed adding hist named '{}' to {}".format(histoName, dictFinalHistoAtSample[h].GetName()))
    return dictFinalHistoAtSample


def WriteHistos(outputTfile, sampleHistoDict, sample, corrLHESysts, hasMC=True, verbose=False):
    histoList = sampleHistoDict.values()
    sampleTMap = next((x for x in histoList if x.ClassName() == "TMap" and "systematicNameToBranchesMap" in x.GetName()), None)
    sampleSystHist = next((x for x in histoList if "systematics" == x.GetName().split("__")[-1] ), None)
    #systObjects = [obj.GetName() for obj in sampleHistoDict.values() if "syst" in obj.GetName().lower()]
    #print("for sample={}. found systObjects: {}".format(sample, systObjects))
    systNameToBranchTitleDict = {}
    if hasMC:
        if sampleSystHist is not None:
            systNameToBranchTitleDict = ExtractBranchTitles(sampleSystHist, sampleTMap)
    outputTfile.cd()
    nHistos = len(sampleHistoDict)
    if verbose:
        print("[{}] Writing {} histos...".format(sample, nHistos), end=' ', flush=True)
    for histo in sampleHistoDict.values():  # for each hist contained in the sample's dict
        histName = histo.GetName()
        nbytes = 0
        if histo.ClassName() == "TMap":
            nbytes = histo.Write(histo.GetName(), r.TObject.kSingleKey)
        elif "TH2" in histo.ClassName() and "systematics" in histo.GetName().lower():
            pdfWeightLabels = [label.GetString().Data() for label in histo.GetYaxis().GetLabels() if "LHEPdfWeight" in label.GetString().Data() and "comb" not in label.GetString().Data().lower()]
            pdfWeightBins = [histo.GetYaxis().FindFixBin(label) for label in pdfWeightLabels]
            pdfMCVarLabels = ["LHEPdfWeightMC_UpComb", "LHEPdfWeightMC_DownComb"]
            pdfMCVarBins = [histo.GetYaxis().FindFixBin(label) for label in pdfMCVarLabels]
            hessianPDFSystDeltasUp = np.zeros(histo.GetNbinsX()+2)
            scaleSystDeltas = np.zeros(histo.GetNbinsX()+2)
            mcPDFSystDeltasUp = [histo.GetBinError(xBin, histo.GetYaxis().FindFixBin(pdfMCVarLabels[0])) for xBin in range(0, histo.GetNbinsX()+2)]
            mcPDFSystDeltasDown = [histo.GetBinError(xBin, histo.GetYaxis().FindFixBin(pdfMCVarLabels[1])) for xBin in range(0, histo.GetNbinsX()+2)]
            if corrLHESysts:
                if hasMC:
                    if len([x for x in [label.GetString().Data() for label in histo.GetYaxis().GetLabels()] if re.match(r"LHEScaleWeight_\d+", x)]) > 0:
                        scaleSystDeltas, yBins = CalculateShapeSystematic(histo, sample, systNameToBranchTitleDict)
            else:
                scaleSystDeltas = [histo.GetBinError(xBin, histo.GetYaxis().FindFixBin("LHEScaleWeight_maxComb")) for xBin in range(0, histo.GetNbinsX()+2)]

            hasHessianPDFVar = False
            for xBin in range(0, histo.GetNbinsX()+2):
                if histo.GetBinContent(xBin, histo.GetYaxis().FindFixBin("LHEPdfWeightHessian_NominalComb")) != 0:
                    hasHessianPDFVar = True
                    break
            if hasHessianPDFVar:
                pdfKeyLabels = pdfWeightLabels.copy()
                pdfKeyLabels.remove("LHEPdfWeight_0")
                hessianPDFSystDeltasUp, pdfSystDeltasDown, yBins = CalculatePDFVariationHessian(histo, sample, pdfKeyLabels, histo.GetYaxis().FindFixBin("LHEPdfWeightHessian_NominalComb"))
            labelsToAdd = ["LHEPdf_UpComb", "LHEPdf_DownComb"]
            if not any(substring in list(histo.GetYaxis().GetLabels()) for substring in labelsToAdd):
                histo = AddHistoBins(histo, "y", labelsToAdd)
            if not IsHistEmpty(histo):
                pdfUpCombBin = histo.GetYaxis().FindFixBin("LHEPdf_UpComb")
                pdfDownCombBin = histo.GetYaxis().FindFixBin("LHEPdf_DownComb")
                for xBin in range(0, histo.GetNbinsX()+2):
                    nominal = histo.GetBinContent(xBin, 1)  # y-bin 1 always being nominal
                    pdfSystDeltaUp = math.sqrt(pow(hessianPDFSystDeltasUp[xBin], 2)+pow(mcPDFSystDeltasUp[xBin], 2))
                    pdfSystDeltaDown = math.sqrt(pow(hessianPDFSystDeltasUp[xBin], 2)+pow(mcPDFSystDeltasDown[xBin], 2))
                    pdfSystTotUp = pdfSystDeltaUp+nominal  # convention of filling with x' = deltaX + x
                    pdfSystTotDown = pdfSystDeltaDown+nominal
                    histo.SetBinContent(xBin, pdfUpCombBin, pdfSystTotUp)
                    histo.SetBinContent(xBin, pdfDownCombBin, pdfSystTotDown)
                    histo.SetBinError(xBin, pdfUpCombBin, pdfSystDeltaUp)
                    histo.SetBinError(xBin, pdfDownCombBin, pdfSystDeltaDown)  # for plotting, we rely on the sumQuad addition of bin errors
            # now we handle the scale weights in a similar way
            scaleWeightLabels = [label.GetString().Data() for label in histo.GetYaxis().GetLabels() if "LHEScaleWeight_" in label.GetString().Data() and not "comb" in label.GetString().Data().lower()]
            labelsToAdd = ["LHEScale_UpComb", "LHEScale_DownComb"]
            if not any(substring in list(histo.GetYaxis().GetLabels()) for substring in labelsToAdd):
                histo = AddHistoBins(histo, "y", labelsToAdd)
            if not IsHistEmpty(histo):
                scaleUpCombBin = histo.GetYaxis().FindFixBin("LHEScale_UpComb")
                scaleDownCombBin = histo.GetYaxis().FindFixBin("LHEScale_DownComb")
                for xBin in range(0, histo.GetNbinsX()+2):
                    nominal = histo.GetBinContent(xBin, 1)  # y-bin 1 always being nominal
                    histo.SetBinContent(xBin, scaleUpCombBin, scaleSystDeltas[xBin]+nominal)
                    histo.SetBinError(xBin, scaleUpCombBin, scaleSystDeltas[xBin])  # for plotting, we rely on the sumQuad addition of bin errors
                    histo.SetBinContent(xBin, scaleDownCombBin, scaleSystDeltas[xBin]+nominal)
                    histo.SetBinError(xBin, scaleDownCombBin, scaleSystDeltas[xBin])
            # redo the bin errors for the other systematics, so that we can use their bin errors in case of any uncorrelated systs
            if not IsHistEmpty(histo):
                otherSystBins = [histo.GetYaxis().FindFixBin(label.GetString().Data()) for label in histo.GetYaxis().GetLabels() if "LHEScale" not in label.GetString().Data() and "LHEPdf" not in label.GetString().Data() and "nominal" not in label.GetString().Data().lower()]
                for xBin in range(0, histo.GetNbinsX()+2):
                    nominal = histo.GetBinContent(xBin, 1)  # y-bin 1 always being nominal
                    for yBin in otherSystBins:
                        val = histo.GetBinContent(xBin, yBin)
                        histo.SetBinError(xBin, yBin, val-nominal)
            # write the hist
            nbytes = histo.Write()
            # make systDiffs hist if needed
            if nbytes > 0 and "systematics" == histo.GetName().split("__")[-1].lower():
                systDiffsHist = MakeSystDiffsPlot(histo)
                nbytes = systDiffsHist.Write()
                histName = systDiffsHist.GetName()
        else:
            nbytes = histo.Write()
        if nbytes <= 0:
            raise RuntimeError("Error writing into the output file '{}': wrote {} bytes to file when writing object '{}'.".format(
                outputTfile.GetName(), nbytes, histName))
    if verbose:
        print("[{}] Done writing.".format(sample), flush=True)
    sys.stdout.flush()


def GetTMapKeys(tmap):
    mapKeys = []
    mapIter = r.TIter(tmap)
    mapKey = mapIter.Next()
    while mapKey:
        mapKeys.append(mapKey)
        mapKey = mapIter.Next()
    return mapKeys


def ComparePDFBranches(combList, sampleList):
    if len(combList) != 1 or len(sampleList) != 1:
        raise RuntimeError("One of the PDF branch lists has length != 1; combList={}, sampleList={}".format(
            combList, sampleList))
    sampleListItem = sampleList[0]
    combListItem = combList[0]
    sampleBranchName = sampleListItem.GetName()
    combBranchName = combListItem.GetName()
    if sampleBranchName != combBranchName:
        # handle special case of compatible PDFs
        if "260001" in sampleBranchName and "292201" in combBranchName:
            return
        elif "260001" in combBranchName and "292201" in sampleBranchName:
            return
        else:
            raise RuntimeError("branch title for combined sample '{}' does not equal branch name for candidate sample '{}' for PDF branch".format(
                combListItem.GetName(), sampleListItem.GetName()))


def CheckSystematicsTMapConsistency(combinedSampleMap, mapToCheck, systematicsList):
    combIter = r.TIter(combinedSampleMap)
    combKey = combIter.Next()
    while combKey:
        if combKey.GetName() not in systematicsList:
            combKey = combIter.Next()  # only check those systs which are still in the combined sample
        sampleMapObject = mapToCheck.FindObject(combKey.GetName())
        if not sampleMapObject:
            sampleItr = r.TIter(mapToCheck)
            sampleKey = sampleItr.Next()
            while sampleKey:
                print("sampleKey: '{}'".format(sampleKey.GetName()))
                sampleKey = sampleItr.Next()
            raise RuntimeError("could not find syst '{}' in sampleMap. systematics TMap in combined sample is inconsistent in input root file".format(
                combKey.GetName()))
        sampleMapVal = sampleMapObject.Value()  # TList of associated branch titles
        combVal = combinedSampleMap.GetValue(combKey)
        # now check the TLists
        combListIter = r.TIter(combVal)
        combListItem = combListIter.Next()
        while combListItem:
            if "lha id" in combListItem.GetName().lower():
                return ComparePDFBranches([item for item in combVal], [item for item in sampleMapVal])
            sampleListItem = sampleMapVal.FindObject(combListItem.GetName())
            if not sampleListItem:
                raise RuntimeError("branch title used in combined sample '{}' for syst '{}' not found in sample list: {}".format(
                    combListItem.GetName(), combKey.GetName(), [item for item in sampleMapVal]))
            if sampleListItem.GetName() != combListItem.GetName():
                raise RuntimeError("branch title for combined sample '{}' does not equal branch name for candidate sample '{}' for syst '{}'".format(
                    combListItem.GetName(), sampleListItem.GetName(), combKey.GetName()))
            combListItem = combListIter.Next()
        combKey = combIter.Next()
    # now check that we have a TMap entry for each systematic in the 2D syst hist
    for syst in systematicsList:
        # if syst.GetName() == "nominal":
        #     continue  # nominal doesn't have any associated branches so it will never be in the TMap
        found = False
        combIter = r.TIter(combinedSampleMap)
        combKey = combIter.Next()
        while combKey:
            if combKey.GetName() == syst.GetName():
                found = True
            elif combKey.GetName() == syst.GetName()[:syst.GetName().rfind("_")]:
                found = True
            combKey = combIter.Next()
        if not found:
            raise RuntimeError("syst '{}' used in combined sample not found in TMap '{}'; keys: '{}'".format(
                syst, combinedSampleMap.GetName(), GetTMapKeys(combinedSampleMap)))


def GetUnscaledTotalEvents(combinedRootFile, sampleName):
    if "DATA" in sampleName:
        # no scaling done to data
        histName = "profile1D__" + sampleName + "__EventsPassingCuts"
    else:
        histName = "profile1D__" + sampleName + "__EventsPassingCuts_unscaled"
    # scaledEvtsHist = combinedRootFile.Get('histo1D__'+ttbarSampleName+'__EventsPassingCuts')
    unscaledEvtsHist = combinedRootFile.Get(histName)
    if not unscaledEvtsHist:
        raise RuntimeError("could not get hist {} from root file {}".format(histName, combinedRootFile.GetName()))
    # print "INFO: reading hist {} from root file {}".format(histName, combinedRootFile.GetName())
    # nonTTBarHist = combinedRootFile.Get('histo1D__'+nonTTBarSampleName+'__EventsPassingCuts')
    # unscaledTotalEvts = unscaledEvtsHist.GetBinContent(1)-nonTTBarHist.GetBinContent(1)
    # print 'GetUnscaledTotalEvents(): Got unscaled events=',unscaledTotalEvts,'from hist:',unscaledEvtsHist.GetName(),'in file:',unscaledRootFile.GetName()
    if unscaledEvtsHist.ClassName() == "TProfile":
        unscaledTotalEvts = unscaledEvtsHist.GetBinContent(1)*unscaledEvtsHist.GetBinEntries(1)
    else:
        unscaledTotalEvts = unscaledEvtsHist.GetBinContent(1)
    return unscaledTotalEvts


def GetXSecTimesIntLumi(sampleNameFromDataset):
    # print 'GetXSecTimesIntLumi(',sampleNameFromDataset+')'
    xsection = float(lookupXSection(sampleNameFromDataset))
    intLumiF = float(intLumi)
    return xsection * intLumiF


def GetFinalSelection(selectionPoint, doEEJJ):
    # min_M_ej_LQ300 for eejj
    selection = "preselection"
    if "preselection" not in selectionPoint:
        if doEEJJ:
            if selectionPoint.isdigit():
                selection = finalSelectionName+"_LQ"+selectionPoint
            else:
                selection = finalSelectionName+"_"+selectionPoint
        else:
            # enujj
            if selectionPoint.isdigit():
                selection = finalSelectionName+"_LQ"+selectionPoint
            else:
                selection = finalSelectionName+"_"+selectionPoint
    return selection


def GetRatesAndErrors(
        combinedRootFile,
        sampleName,
        selection,
        doEEJJ=True,
        isDataOrQCD=False,
        isTTBarFromData=False
        ):
    verbose = False
    if verbose or isTTBarFromData:
        print("GetRatesAndErrors(", combinedRootFile.GetName(), sampleName, selection, doEEJJ, isDataOrQCD, isTTBarFromData, ")")
    histName = "EventsPassingCuts"
    # special case of TTBar from data
    # if isTTBarFromData:
    #     # rate calcs should be same as data/QCD
    #     mejHist = combinedRootFile.Get(
    #         "histo1D__" + ttbarSampleName + "__" + histName + "_" + selection
    #     )
    #     mejUnscaledRawHist = combinedRootFile.Get(
    #         "histo1D__" + ttBarUnscaledRawSampleName + "__" + histName + "_" + selection
    #     )
    #     mejNonTTBarHist = combinedRootFile.Get(
    #         "histo1D__" + nonTTBarSampleName + "__" + histName + "_" + selection
    #     )
    #     if not mejNonTTBarHist:
    #         sys.stdout.flush()
    #         print "ERROR: could not find hist histo1D__" + nonTTBarSampleName + "__" + histName + "_" + selection, " in file:", combinedRootFile.GetName()
    #         print "EXIT"
    #         exit(-1)
    #     rateErr = Double(0)
    #     integ = mejNonTTBarHist.IntegralAndError(
    #         1, mejNonTTBarHist.GetNbinsX(), rateErr
    #     )
    #     print "mejNonTTBar:", integ, ",+/-", rateErr
    #     integ = mejUnscaledRawHist.IntegralAndError(
    #         1, mejUnscaledRawHist.GetNbinsX(), rateErr
    #     )
    #     print "mejUnscaledRaw:", integ, ",+/-", rateErr
    #     # mejNonTTBarHist.Scale(1/1000.)
    #     # rate = mejHist.Integral()
    #     rate = mejHist.IntegralAndError(1, mejHist.GetNbinsX() + 1, rateErr)
    #     unscaledHist = mejUnscaledRawHist.Clone()
    #     # unscaledHist.Add(mejNonTTBarHist,-1) #LQ2 only uses emujj data events
    #     # integ = mejUnscaledHist.IntegralAndError(1,mejUnscaledHist.GetNbinsX(),rateErr)
    #     # print 'mejUnscaled:',integ,',+/-',rateErr
    #     # scaledHist = unscaledHist.Clone()
    #     # scaledHist.Scale(0.436873)
    #     # integ = mejScaledHist.IntegralAndError(1,mejScaledHist.GetNbinsX(),rateErr)
    #     # print 'mejScaled:',integ,',+/-',rateErr
    #     # unscaledRate = unscaledHist.Integral()
    #     unscaledRateErr = Double(0)
    #     unscaledRate = unscaledHist.IntegralAndError(
    #         1, mejHist.GetNbinsX() + 1, unscaledRateErr
    #     )
    #     # unscaledRate+=mejNonTTBarHist.Integral(1,mejHist.GetNbinsX()+1)
    #     if verbose:
    #         print "using unscaled (minus nonttbarMC) hist:", unscaledHist.GetName(), "from file:", combinedRootFile.GetName()
    #         print "TTBARFROMDATA-->rate=", rate, "+/-", rateErr
    #         print "mejUnscaled:", unscaledRate, ",+/-", unscaledRateErr
    #         print "using hist:", mejHist.GetName(), "from file:", combinedRootFile.GetName()
    #     return rate, rateErr, unscaledRate
    # mejHist = combinedRootFile.Get('histo1D__'+sampleName+histName+'_'+selection)
    # if not mejHist:
    #  print 'ERROR: could not find hist','histo1D__'+sampleName+histName+'_'+selection,' in file:',combinedRootFile.GetName()
    #  print 'EXIT'
    #  exit(-1)
    # rate = mejHist.Integral()

    scaledHistName = "profile1D__"+sampleName+"__"+histName
    scaledHist = combinedRootFile.Get(scaledHistName)
    if not scaledHist or scaledHist.ClassName() != "TProfile":
        raise RuntimeError("Could not find TProfile named '{}' in file: {}".format(scaledHistName, combinedRootFile.GetName()))
    selection = GetFinalSelection(selection, doEEJJ)
    selectionBin = scaledHist.GetXaxis().FindFixBin(selection)
    if selectionBin < 1:
        raise RuntimeError("Could not find requested selection name '{}' in hist {} in file {}".format(
            selection, scaledHistName, combinedRootFile.GetName()))
    rate = scaledHist.GetBinContent(selectionBin)*scaledHist.GetBinEntries(selectionBin)
    rateErr = math.sqrt(scaledHist.GetSumw2().At(selectionBin))
    # raw events (without weights or any kind of scaling) will always be the BinEntries in a TProfile, even if scaling/weights are applied
    rawEventsAtSelection = scaledHist.GetBinEntries(selectionBin)
    return rate, rateErr, rawEventsAtSelection


def IsHistEmpty(hist):
    # copy/adapt from TH1::IsEmpty()
    if hist.GetEntries() != 0:
        return False
    # not in the TH1::IsEmpty(), but for us, zero entries means empty
    if not hist.GetEntries() == 0:
        return True
    statArr = np.zeros(11)  # for TH3F
    hist.GetStats(statArr)
    fTsumw = statArr[0]
    if fTsumw != 0:
        return False
    sumw = 0.0
    for i in range(0, hist.GetNcells()):
        sumw += hist.GetBinContent(i)
    return False if sumw != 0 else True


def AddHistoBins(hist, axis, labelsToAdd):
    # NB: overflows not handled
    if "TH2" in hist.__repr__():
        newHist = r.TH2F()
        newHist.SetNameTitle(hist.GetName(), hist.GetTitle())
        if axis == "y":
            numNewBins = hist.GetNbinsY()+len(labelsToAdd)
            yBinLabels = hist.GetYaxis().GetLabels()
            newBinLabels = [label.GetString().Data() for label in yBinLabels]
            newBinLabels.extend(labelsToAdd)
            newHist.SetBins(
                    hist.GetNbinsX(),
                    hist.GetXaxis().GetXmin(),
                    hist.GetXaxis().GetXmax(),
                    numNewBins,
                    hist.GetYaxis().GetBinLowEdge(1),
                    hist.GetYaxis().GetBinUpEdge(numNewBins)
                    )
            for ibin in range(1, numNewBins+1):
                newHist.GetYaxis().SetBinLabel(ibin, newBinLabels[ibin-1])
            hist.GetXaxis().Copy(newHist.GetXaxis())
            if IsHistEmpty(hist):
                return newHist
            # now handle bin content
            for xbin in range(0, newHist.GetNbinsX()+2):
                for ybin in range(0, hist.GetNbinsY()+1):
                    binContent = hist.GetBinContent(xbin, ybin)
                    binError = hist.GetBinError(xbin, ybin)
                    newHist.SetBinContent(xbin, ybin, binContent)
                    newHist.SetBinError(xbin, ybin, binError)
            return newHist
        else:
            raise RuntimeError("ERROR: AddHistoBins not implemented for axes other than y, and {} was requested.".format(axis))
    else:
        raise RuntimeError("ERROR: AddHistoBins not implemented for histos other than TH2 and this is a {}.".format(hist.__repr__()))


def RemoveHistoBins(hist, axis, labelsToRemove):
    # NB: overflows not handled
    if "TH2" in hist.__repr__():
        newHist = r.TH2F()
        newHist.SetNameTitle(hist.GetName(), hist.GetTitle())
        if axis == "y":
            numNewBins = hist.GetNbinsY()-len(labelsToRemove)
            yBinLabels = hist.GetYaxis().GetLabels()
            newBinLabels = [label.GetString().Data() for label in yBinLabels if label.GetString().Data() not in labelsToRemove]
            newHist.SetBins(
                    hist.GetNbinsX(),
                    hist.GetXaxis().GetXmin(),
                    hist.GetXaxis().GetXmax(),
                    numNewBins,
                    hist.GetYaxis().GetBinLowEdge(1),
                    hist.GetYaxis().GetBinUpEdge(numNewBins)
                    )
            for ibin in range(1, numNewBins+1):
                newHist.GetYaxis().SetBinLabel(ibin, newBinLabels[ibin-1])
            hist.GetXaxis().Copy(newHist.GetXaxis())
            # now handle bin content
            for xbin in range(0, newHist.GetNbinsX()+2):
                ybin = 0
                ybinOld = 0
                while ybin < newHist.GetNbinsY()+2:
                    while hist.GetYaxis().GetBinLabel(ybinOld) in labelsToRemove:
                        ybinOld += 1
                    binLabelOld = hist.GetYaxis().GetBinLabel(ybinOld)
                    binLabelNew = newHist.GetYaxis().GetBinLabel(ybin)
                    if binLabelNew != binLabelOld:
                        raise RuntimeError("RemoveHistoBins(): bin label of old histo {} doesn't match new histo label {}!".format(
                            binLabelOld, binLabelNew))
                    binContent = hist.GetBinContent(xbin, ybinOld)
                    binError = hist.GetBinError(xbin, ybinOld)
                    newHist.SetBinContent(xbin, ybin, binContent)
                    newHist.SetBinError(xbin, ybin, binError)
                    ybin += 1
                    ybinOld += 1
            return newHist
        else:
            raise RuntimeError("ERROR: RemoveHistoBins not implemented for axes other than y, and {} was requested.".format(axis))
    else:
        raise RuntimeError("ERROR: RemoveHistoBins not implemented for histos other than TH2 and this is a {}.".format(hist.__repr__()))


def MakeSystDiffsPlot(systHist):
    histName = systHist.GetName().replace("systematics", "systematicsDiffs")
    # print "INFO: Creating new systematicsDiffs hist with name {}".format(histName)
    systDiffs = r.TH2F(histName, histName, systHist.GetNbinsX(), 0, systHist.GetXaxis().GetXmax(), systHist.GetNbinsY(), 0, systHist.GetYaxis().GetXmax())
    systHist.GetXaxis().Copy(systDiffs.GetXaxis())
    systHist.GetYaxis().Copy(systDiffs.GetYaxis())
    systDiffs.Sumw2()
    systDiffs.SetDirectory(0)
    nominal = systHist.ProjectionX("nominal", 1, 1, "e")
    nominal.LabelsDeflate()
    nominal.SetDirectory(0)
    for yBin in range(1, systHist.GetNbinsY()+1):
        proj = systHist.ProjectionX("proj", yBin, yBin, "e")
        proj.LabelsDeflate()  # otherwise we get 2x number of bins
        proj.SetDirectory(0)
        quotient = r.TGraphAsymmErrors()
        # suppress warning messages for divide this can happen for zero content bins, for example
        prevLevel = r.gErrorIgnoreLevel
        r.gErrorIgnoreLevel = r.kError
        quotient.Divide(proj, nominal, "pois cp")
        r.gErrorIgnoreLevel = prevLevel
        for iPoint in range(0, quotient.GetN()):
            x = quotient.GetPointX(iPoint)
            y = quotient.GetPointY(iPoint)
            err = quotient.GetErrorY(iPoint)
            binNum = systDiffs.FindBin(x, yBin-0.5)
            systDiffs.SetBinContent(binNum, y)
            systDiffs.SetBinError(binNum, err)
    return systDiffs


def SetDistinctiveTColorPalette():
    # 12 distinctive colors
    myColors = ["#76be79",
                "#8049c5",
                "#86d54b",
                "#d056a2",
                "#cab244",
                "#443058",
                "#d15739",
                "#7dc2c1",
                "#893e44",
                "#9090c5",
                "#4d5635",
                "#cca58a"]
    SetTColorPalette(myColors)


def SetTColorPalette(colorList):
    tcolors = [r.TColor.GetColor(i) for i in colorList]
    print("tcolors=", tcolors)
    r.gStyle.SetPalette(len(tcolors), np.array(tcolors, dtype=np.int32))


def DeleteTmpFiles(allTmpFilesByMass):
    for mass, tmpFileList in allTmpFilesByMass.items():
        for tmpFile in tmpFileList:
            os.unlink(tmpFile)


#FIXME: would be much better to use some kind of mkstemp named
def WriteTmpCard(txtFilePath, mass, cardIndex, cardContent, dirPath="/tmp"):
    tmpCardFileNameBasePath = "{}/tmpDatacard_m{}_card{}_{}"
    tmpCardFileName = tmpCardFileNameBasePath.format(dirPath, mass, cardIndex, os.path.basename(txtFilePath))
    print("INFO: writing tmp datacard to {}".format(tmpCardFileName))
    with open(tmpCardFileName, "w") as tmpCardFile:
        for lineToWrite in cardContent:
            tmpCardFile.write(lineToWrite+"\n")
    return tmpCardFileName


def SeparateDatacards(txtFilePath, cardIndex, dirPath):
    massList = []
    tmpFileByMass = {}
    cardContent = []
    for line in open(os.path.expandvars(txtFilePath)):
        if ".txt" in line:
            if len(cardContent) > 0:
                tmpFile = WriteTmpCard(txtFilePath, mass, cardIndex, cardContent, dirPath)
                tmpFileByMass[mass] = tmpFile
            cardContent = []
            mass = line.split("M")[-1].split(".txt")[0]
            massList.append(mass)
        else:
            cardContent.append(line)
    if len(cardContent) > 0:
        tmpFile = WriteTmpCard(txtFilePath, mass, cardIndex, cardContent, dirPath)
        tmpFileByMass[mass] = tmpFile
    return massList, tmpFileByMass
