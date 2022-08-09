#!/usr/bin/env python

# ---Import
import sys
import os
import string
import math
import re
import glob
import copy
from collections import OrderedDict
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
    # "hack" for data-driven QCD samples: name is created by the createInputList script
    # do this first, since it's at the very end of the filename
    # special hacks for datasets
    # if dataset_fromInputList.contains('_reduced_skim'):
    #  #dataset_fromInputList = dataset_fromInputList[0:dataset_fromInputList.find('_reduced_skim')]
    #  dataset_fromInputList.replace('_reduced_skim','')
    # print '0) SanitizeDatasetNameFromInputList() result is:'+dataset_fromInputList
    dataset_fromInputList = dataset_fromInputList.replace("_reduced_skim", "")
    # in rare cases, replace __ by _
    dataset_fromInputList = dataset_fromInputList.replace("__", "_")
    # if dataset_fromInputList.endswith("_pythia8"):
    #     dataset_fromInputList = dataset_fromInputList[
    #         0: dataset_fromInputList.find("_pythia8")
    #     ]
    # # if '__' in dataset_fromInputList:
    # #  dataset_fromInputList = dataset_fromInputList[0:dataset_fromInputList.find('__')]
    if dataset_fromInputList.endswith("_tree"):
        dataset_fromInputList = dataset_fromInputList[
            0: dataset_fromInputList.find("_tree")
        ]
    # if 'ZToEE' in dataset_fromInputList:
    #     print 'found ZToEE in dataset='+dataset_fromInputList
    #     dataset_fromInputList = dataset_fromInputList.replace('TuneCP5_', '').replace('13TeV-', '')
    # dataset_fromInputList = dataset_fromInputList.replace("ext2_", "").replace("ext1_", "").replace("ext_", "").replace("ext1", "").replace("ext", "")
    #dataset_fromInputList = re.sub("ext[0-9_]*", "", dataset_fromInputList)
    #dataset_fromInputList = re.sub("EXT[0-9_]*", "", dataset_fromInputList)
    #dataset_fromInputList = dataset_fromInputList.replace("backup_", "")
    #dataset_fromInputList = dataset_fromInputList.replace("_backup", "")
    #dataset_fromInputList = re.sub("newPMX[_]*", "", dataset_fromInputList)
    ## dataset_fromInputList = re.sub("NNPDF[0-9_]*", "", dataset_fromInputList)
    # print '1) SanitizeDatasetNameFromInputList() result is:'+dataset_fromInputList
    dataset_fromInputList = dataset_fromInputList.strip("_APV")
    dataset_fromInputList = dataset_fromInputList.rstrip("_")
    return dataset_fromInputList


def SanitizeDatasetNameFromFullDataset(dataset):
    # print 'SanitizeDatasetNameFromFullDataset: dataset looks like:'+dataset
    # this logic is somewhat copied from the submission script for the ntuples:
    #    https://github.com/CMSLQ/submitJobsWithCrabV2/blob/master/createAndSubmitJobsWithCrab3.py
    if "Run20" not in dataset:
        # outputFileNames = []
        # outputFileNames.append(dataset[1: dataset.find("_Tune")])
        # outputFileNames.append(dataset[1: dataset.find("_13TeV")])
        # try:
        #     outputFileNames.append(dataset.split("/")[1])
        # except IndexError:
        #     print("ERROR: SanitizeDatasetNameFromFullDataset(): IndexError trying to split('/') dataset:", dataset, "; this can happen if this is a piece (not a full dataset) containing multiple samples that has not been defined earlier in the sampleListToCombineFile")
        #     raise
        # # use the one with the shortest filename
        # outputFile = sorted(outputFileNames, key=len)[0]
        # ignore all ext files, or rather, treat them the same as non-ext
        #if "ext" in dataset:
        #    extN = dataset[dataset.find("_ext") + 4]
        #    outputFile = outputFile + "_ext" + extN
        # if "madgraphMLM" in dataset:
        #     outputFile += "_madgraphMLM"
        # elif "amcatnloFXFX" in dataset or "amcnloFXFX" in dataset:
        #     outputFile += "_amcatnloFXFX"
        # if 'ZToEE' in dataset:
        #     # print 'found ZToEE in dataset='+dataset
        #     outputFile = dataset.split("/")[1].replace('TuneCP5_', '').replace('13TeV-', '')
        # print 'SanitizeDatasetNameFromFullDataset:', dataset, 'shortened to:', outputFile
        # print 'choices were:',outputFileNames
        outputFile = dataset.split("/")[1]
    else:
        # # outputFile = dataset[1:].replace('/','__')
        # # outputFile = outputFile.split('__')[0]+'__'+outputFile.split('__')[1]
        # outputFile = dataset[1:].replace("/", "_")
        # # if(len(outputFile.split('_')) == 3):
        # #  outputFile = outputFile.split('_')[0]+'_'+outputFile.split('_')[1]
        # # elif(len(outputFile.split('_')) == 4):
        # #  outputFile = outputFile.split('_')[0]+'_'+outputFile.split('_')[1]+'_'+outputFile.split('_')[2]
        # outputFileSplit = outputFile.split("_")
        # outputFile = ""
        # for i in range(0, len(outputFileSplit) - 1):
        #     outputFile += outputFileSplit[i] + "_"
        # outputFile = outputFile[:-1]
        # print '2 outputFile=',outputFile
        # print 'outputFile.split("_")=',outputFile.split('_')
        outputFile = "_".join(dataset.split("/")[1:3])
    return outputFile


def GetSamplesToCombineDict(sampleListForMerging):
    dictSamples = OrderedDict()
    duplicateKeyError = False
    for l, line in enumerate(open(sampleListForMerging)):
        # ignore comments
        if line.startswith("#"):
            continue
        line = line.strip("\n")
        # ignore empty lines
        if len(line) <= 0:
            continue

        # print 'line from samplesToCombineFile looks like:"'+line+'"'
        # line looks like: "ZJet_Madgraph_Inc    DYJetsToLL_M-5to50 DYJetsToLL_M-50"
        # or "LQ_M200   /LQToUE_M-200_BetaOne_TuneCUETP8M1_13TeV-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2/MINIAODSIM"

        # the rule is that the name of each 'piece' here must match the inputList name and filename
        if len(line.split()) < 2:
            raise RuntimeError("GetSamplesToCombineDict(): cannot deal with line which does not contain at least one piece: '"+line+"'")
        for i, piece in enumerate(line.split()):
            # print "GetSamplesToCombineDict(): i=", i, "  piece= ", piece
            if i == 0:
                key = piece
                if key in list(dictSamples.keys()):
                    print("ERROR: GetSamplesToCombineDict(): key '{}' in line #{} has already been defined earlier in the sampleListForMerging file!".format(key, l+1))
                    print("\toffending line #{} looks like '{}'".format(l+1, line))
                    duplicateKeyError = True
                    break
                dictSamples[key] = []
            # elif piece in dictSamples:
            #     dictSamples[key].extend(dictSamples[piece])
            else:
                # # print "GetSamplesToCombineDict(): SanitizeDatasetNameFromFullDataset({})=".format(piece),
                # try:
                #     piece = SanitizeDatasetNameFromFullDataset(piece)
                # except IndexError:
                #     print "ERROR: GetSamplesToCombineDict(): caught exception when trying to deal with pieces in line '"+line+'"'
                #     exit(-1)
                # # print piece
                # dictSamples[key].append(piece)
                dictSamples[key].append(piece)
        # print "dictSamples["+key+"]=", dictSamples[key]
    if duplicateKeyError:
        raise RuntimeError("duplicate key found")
    return dictSamples


def ExpandPiece(piece, dictSamples):
    if "/" in piece:
        piece = SanitizeDatasetNameFromFullDataset(piece)
        return [piece]
    else:
        pieces = dictSamples[piece]
        return ExpandPieces(pieces, dictSamples)


def ExpandPieces(pieceList, dictSamples):
    piecesToAdd = []
    # for piece in pieceList:
    #     if "/" in piece:
    #         piece = SanitizeDatasetNameFromFullDataset(piece)
    #         piecesToAdd.append(piece)
    #     else:
    #         pieces = dictSamples[piece]
    #         expandedPieces = ExpandPieces(pieces, dictSamples)
    #         piecesToAdd.extend(expandedPieces)
    for piece in pieceList:
        piecesToAdd.extend(ExpandPiece(piece, dictSamples))
    return piecesToAdd


def ExpandSampleDict(dictSamples):
    outputDict = dict()
    for sampleName, sampleList in list(dictSamples.items()):
        outputDict[sampleName] = ExpandPieces(sampleList, dictSamples)
    return outputDict


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
    return xsectionDict[datasetNameFromInputList]
    #for dataset in list(xsectionDict.keys()):
    #    if verbose and "LQ" in dataset:
    #        print('INFO: dataset in xsec file:', dataset, ' starts with the one we are asking for:', datasetNameFromInputList, '?')
    #    if dataset.startswith(datasetNameFromInputList):
    #        if verbose:
    #            print('INFO: dataset in xsec file:', dataset, 'starts with the one we are asking for:', datasetNameFromInputList)
    #        # check to make sure dataset in xsec file up to first underscore matches the datasetNameFromInputList
    #        # this should catch a case where we have TT as the datasetNameFromInputList [e.g., powheg] and it would otherwise match TTJets in the xsec file
    #        if datasetNameFromInputList.startswith(dataset.split("_")[0]):
    #            # print 'INFO: found dataset in xsec file:', dataset, 'that starts with the one we are asking for:', datasetNameFromInputList
    #            return xsectionDict[dataset]
    ## for key in sorted(xsectionDict.iterkeys()):
    ##  print 'sample=',key,'xsection=',xsectionDict[key]
    #raise RuntimeError("xsectionDict does not have an entry for " + datasetNameFromInputList + ", i.e., no dataset in xsectionDict starts with this.")


def ParseDatFile(datFilename):
    # ---Read .dat table for current dataset
    data = {}
    column = []
    lineCounter = int(0)

    # print '(opening:',inputDataFile,
    # sys.stdout.flush()
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
        histName = "profile1D__{}__EventsPassingCutsAllHist".format(sampleName)
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
        # for j, line in enumerate(inputTable):
        #     outputTable[int(j)] = {
        #         "variableName": inputTable[j]["variableName"],
        #         "min1": inputTable[j]["min1"],
        #         "max1": inputTable[j]["max1"],
        #         "min2": inputTable[j]["min2"],
        #         "max2": inputTable[j]["max2"],
        #         "N": float(inputTable[j]["N"]),
        #         "errN": pow(float(inputTable[j]["errN"]), 2),
        #         "Npass": float(inputTable[j]["Npass"]),
        #         "errNpass": pow(float(inputTable[j]["errNpass"]), 2),
        #         "EffRel": float(0),
        #         "errEffRel": float(0),
        #         "EffAbs": float(0),
        #         "errEffAbs": float(0),
        #     }
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


def GetSampleHistosFromTFile(tfileName, sampleHistos, sampleName=""):
    # used in combinePlots.py
    tfile = r.TFile(tfileName)
    for key in tfile.GetListOfKeys():
        # histoName = file.GetListOfKeys()[h].GetName()
        # htemp = file.Get(histoName)
        histoName = key.GetName()
        htemp = key.ReadObj()
        if not htemp or htemp is None:
            raise RuntimeError("failed to get histo named:", histoName, "from file:", tfile.GetName())
        r.SetOwnership(htemp, True)
        if sampleName in histoName:
            if "amcatnlo" in tfileName.lower() and "systematics" in histoName.lower() and "diffs" not in histoName.lower():
                # in this case, we check if there are 102 LHEPdfWeights in the y bins, and if so, we remove index 100 and 101 (alpha_S weights)
                yBinLabels = htemp.GetYaxis().GetLabels()
                lhePdfWeightLabels = [label for label in yBinLabels if "lhepdfweight" in label.GetString().Data()]
                if len(lhePdfWeightLabels) == 102:
                    print("INFO: removing {} bins from the LHEPdfWeights (indices 100 and 101) histo {} with ybins {} in file {}".format(
                            len(lhePdfWeightLabels)-100, htemp.GetName(), htemp.GetNbinsY(), tfileName))
                    htemp = RemoveHistoBins(htemp, "y", lhePdfWeightLabels[-2:])
            if htemp.InheritsFrom("TH1"):
                htemp.SetDirectory(0)
            sampleHistos.append(htemp)
    tfile.Close()
    if len(sampleHistos) < 1:
        raise RuntimeError(
                "GetSampleHistosFromTFile({}, {}) -- failed to read any histos for the sampleName from this file!".format(
                    tfile.GetName(), sampleName))


def AddHistosFromFile(rootFileName, sampleHistoDict, piece, sample="", plotWeight=1.0):
    # ---Combine histograms using PYROOT
    tfile = r.TFile.Open(rootFileName)
    nHistos = len(tfile.GetListOfKeys())
    # print 'list of keys in this rootfile:',file.GetListOfKeys()
    # print
    #print "INFO: AddHistosFromFile for file: {}: nKeys={}".format(rootFileName, nHistos)
    #sys.stdout.flush()
    # loop over histograms in rootfile
    # for h in range(0, nHistos):
    h = 0
    for key in tfile.GetListOfKeys():
        # histoName = file.GetListOfKeys()[h].GetName()
        # htemp = file.Get(histoName)
        histoName = key.GetName()
        htemp = key.ReadObj()
        if not htemp:
            raise RuntimeError("ERROR: failed to get histo named: {} from file: {}".format(histoName, tfile.GetName()))
        # log XXX DEBUG
        #else:
        #    print "INFO: AddHistosFromFile for file: {}: handling histoName={}".format(rootFileName, histoName)
        # log XXX DEBUG
        r.SetOwnership(htemp, True)
        #
        # temporary
        #
        # if "TDir" in htemp.__repr__():
        # #print "Getting optimizer hist!"
        # htemp = file.Get(histoName + "/optimizer")
        # #print "entries:",htemp.GetEntries()
        # only go 1 subdir deep
        if "TDir" in htemp.ClassName():
            dirKeys = htemp.GetListOfKeys()
            for dirKey in dirKeys:
                hname = dirKey.GetName()
                htmp = dirKey.ReadObj()
                if not htmp:
                    raise RuntimeError("ERROR: failed to get histo named: {} from file: {}".format(hname, tfile.GetName()))
                # else:
                #  print "INFO: found key in subdir named:",hname,"hist name:",htmp.GetName()
                # log XXX DEBUG
                #else:
                #    print "INFO: AddHistosFromFile for file: {}: in a TDir, about to updateSample for histoName={}".format(rootFileName, hname)
                #    sys.stdout.flush()
                # log XXX DEBUG
                r.SetOwnership(htmp, True)
                updateSample(
                    sampleHistoDict, htmp, h, piece, sample, plotWeight
                )
                h += 1
        else:
            # log XXX DEBUG
            #print "INFO: AddHistosFromFile for file: {}: about to updateSample for histoName={}".format(rootFileName, histoName)
            #sys.stdout.flush()
            # log XXX DEBUG
            updateSample(
                sampleHistoDict, htemp, h, piece, sample, plotWeight
            )
            h += 1
    # print "INFO: AddHistosFromFile for file: {} -- finished updateSample calls".format(rootFileName)
    # log XXX DEBUG
    #print "INFO: AddHistosFromFile for file: {} -- finished updateSample calls".format(rootFileName)
    #sys.stdout.flush()
    # log XXX DEBUG
    # check TMap consistency
    sampleTMap = next((x.ReadObj() for x in tfile.GetListOfKeys() if x.ReadObj().ClassName() == "TMap" and "systematicNameToBranchesMap" in x.GetName()), None)
    comboTMap = next((x for x in list(sampleHistoDict.values()) if x.ClassName() == "TMap" and "systematicNameToBranchesMap" in x.GetName()), None)
    comboSystHist = next((x for x in list(sampleHistoDict.values()) if x.GetName() == "systematics"), None)
    if comboSystHist is not None:
        CheckSystematicsTMapConsistency(comboTMap, sampleTMap, list(comboSystHist.GetYaxis().GetLabels()))
    tfile.Close()


def GetShortHistoName(histName):
    if "histo1D" in histName or "histo2D" in histName or "histo3D" in histName or "profile1D" in histName:
        return histName.split(histName.split("__")[1])[1].strip("_")
    else:
        return histName


def UpdateHistoDict(sampleHistoDict, pieceHistoList, piece, sample="", plotWeight=1.0):
    # print "INFO: UpdateHistoDict for sample {}".format(sample)
    sys.stdout.flush()
    idx = 0
    for pieceHisto in pieceHistoList:
        pieceHistoName = pieceHisto.GetName()
        pieceHisto.SetName(GetShortHistoName(pieceHistoName))
        if idx in sampleHistoDict:
            sampleHisto = sampleHistoDict[idx]
            # sampleHistoName = sampleHisto.GetName()
            # sampleHisto.SetName(GetShortHistoName(sampleHistoName))
            if pieceHisto.GetName() not in sampleHisto.GetName():
                raise RuntimeError(
                        "ERROR: non-matching histos between sample hist with name '{}' and piece hist with name '{}'. Quitting here".format(
                            sampleHisto.GetName(), pieceHisto.GetName()))
        if "eventspassingcuts" in pieceHisto.GetName().lower() and "unscaled" not in pieceHisto.GetName().lower():
            # create new EventsPassingCuts hist that doesn't have scaling/reweighting by int. lumi.
            # print "INFO: create new EventsPassingCuts hist from {} that doesn't have scaling/reweighting by int. lumi.".format(pieceHisto.GetName())
            unscaledEvtsPassingCuts = copy.deepcopy(pieceHisto)
            unscaledEvtsPassingCuts.SetNameTitle(pieceHisto.GetName()+"_unscaled", pieceHisto.GetTitle()+"_unscaled")
            sampleHistoDict = updateSample(sampleHistoDict, unscaledEvtsPassingCuts, idx, piece, sample, 1.0)
            idx += 1
        sampleHistoDict = updateSample(sampleHistoDict, pieceHisto, idx, piece, sample, plotWeight)
        # if idx < 2:
        #     print "\tINFO: UpdateHistoDict for sample {}: added pieceHisto {} with entries {} to sampleHistoDict[idx], which has name {} and entries {}".format(
        #             sample, pieceHisto.GetName(), pieceHisto.GetEntries(), sampleHistoDict[idx].GetName(), sampleHistoDict[idx].GetEntries())
        idx += 1
    # check TMap consistency
    sampleTMap = next((x for x in pieceHistoList if x.ClassName() == "TMap" and "systematicNameToBranchesMap" in x.GetName()), None)
    comboTMap = next((x for x in list(sampleHistoDict.values()) if x.ClassName() == "TMap" and "systematicNameToBranchesMap" in x.GetName()), None)
    comboSystHist = next((x for x in list(sampleHistoDict.values()) if x.GetName().endswith("systematics")), None)
    # if comboSystHist is None:
        # print "Could not find comboSystHist in sampleHistoDict"
        # print [x.GetName() for x in sampleHistoDict.values() if "systematics" in x.GetName()]
    if comboSystHist is not None:
        CheckSystematicsTMapConsistency(comboTMap, sampleTMap, list(comboSystHist.GetYaxis().GetLabels()))
    return sampleHistoDict


def updateSample(dictFinalHistoAtSample, htemp, h, piece, sample, plotWeight):
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
    if h not in dictFinalHistoAtSample:
        if "TH2" in htemp.__repr__():
            dictFinalHistoAtSample[h] = r.TH2D()
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
    #  XXX DEBUG
    # binToExamine = 33
    # if 'OptBinLQ60' in histoName:
    #  print
    #  if htemp.GetBinContent(binToExamine)!=0:
    #    print 'Add',histoName,'hist: sample=',sample,'bin',binToExamine,'content=',htemp.GetBinContent(binToExamine),' error=',htemp.GetBinError(binToExamine),'relErr=',htemp.GetBinError(binToExamine)/htemp.GetBinContent(binToExamine)
    #  if dictFinalHistoAtSample[h].GetBinContent(binToExamine) != 0:
    #    print 'BEFORE',histoName,'hist: sample=',sample,'bin',binToExamine,'content=',dictFinalHistoAtSample[h].GetBinContent(binToExamine),' error=',dictFinalHistoAtSample[h].GetBinError(binToExamine),'relErr=',dictFinalHistoAtSample[h].GetBinError(binToExamine)/dictFinalHistoAtSample[h].GetBinContent(binToExamine)
    # if 'SumOfWeights' in histoName:
    #  continue # do not sum up the individual SumOfWeights histos
    # if 'optimizerentries' in histoName.lower():
    # XXX DEBUG TEST
    if "optimizerentries" in histoName.lower() or "noweight" in histoName.lower() or "unscaled" in histoName.lower():
        returnVal = dictFinalHistoAtSample[h].Add(htemp)
    else:
        if "TMap" in htemp.ClassName() and "systematicNameToBranchesMap" in htemp.GetName():
            # for this special TMap, check that the keys and values are consistent
            # recall: TObjString --> TList
            # print "INFO: checking systematicNameToBranchesMap consistency for piece {} in combined sample {}".format(piece, sample)
            # CheckSystematicsTMapConsistency(dictFinalHistoAtSample[h], htemp)
            # no-op
            return dictFinalHistoAtSample
        if "systematics" in htemp.GetName().lower():
            # check systematics hist bins
            systematicsListFromDictHist = list(dictFinalHistoAtSample[h].GetYaxis().GetLabels())
            systematicsListFromTempHist = list(htemp.GetYaxis().GetLabels())
            systsNotInTempHist = [label for label in systematicsListFromDictHist if label not in systematicsListFromTempHist]
            if len(systsNotInTempHist) > 0:
                print("\tINFO: some systematics absent from piece {}; removing them from the systematics histo for combined sample {}. Missing systematics: {}".format(
                        piece, sample, systsNotInTempHist))
                # print "SethLog: systematicsListFromTempHist={} and piece={}".format(systematicsListFromTempHist, piece)
                # print "SethLog: systematicsListFromDictHist={} and sample={}".format(systematicsListFromDictHist, sample)
                sys.stdout.flush()
                # remove systs that are missing from htemp
                dictFinalHistoAtSample[h] = RemoveHistoBins(dictFinalHistoAtSample[h], "y", systsNotInTempHist)
                # now update the systematics list, since we removed some
                systematicsListFromDictHist = list(dictFinalHistoAtSample[h].GetYaxis().GetLabels())
            # it can also happen that new systematics appear in htemp that aren't in the dict hist
            systsNotInDictHist = [label for label in systematicsListFromTempHist if label not in systematicsListFromDictHist]
            if len(systsNotInDictHist) > 0:
                print("\tINFO: some systematics absent from combined sample {}; removing them from the systematics histo for piece {}. Missing systematics: {}".format(
                        sample, piece, systsNotInDictHist))
                # print "SethLog: systematicsListFromTempHist={} and piece={}".format(systematicsListFromTempHist, piece)
                # print "SethLog: systematicsListFromDictHist={} and sample={}".format(systematicsListFromDictHist, sample)
                # sys.stdout.flush()
                # remove systs that are missing from htemp
                htemp = RemoveHistoBins(htemp, "y", systsNotInDictHist)
            if htemp.GetNbinsX() != dictFinalHistoAtSample[h].GetNbinsX() or htemp.GetNbinsY() != dictFinalHistoAtSample[h].GetNbinsY():
                raise RuntimeError("htemp to be added has {} x bins and {} y bins, which is inconsistent with the existing hist, which has {} x bins and {} y bins".format(
                    htemp.GetNbinsX(), htemp.GetNbinsY(),
                    dictFinalHistoAtSample[h].GetNbinsX(), dictFinalHistoAtSample[h].GetNbinsY()))
            if list(htemp.GetYaxis().GetLabels()) != list(dictFinalHistoAtSample[h].GetYaxis().GetLabels()):
                raise RuntimeError("htemp to be added has y-axis bin labels {} which are inconsistent with existing hist: {}".format(
                    list(htemp.GetYaxis().GetLabels()), list(dictFinalHistoAtSample[h].GetYaxis().GetLabels())))
            if list(htemp.GetXaxis().GetLabels()) != list(dictFinalHistoAtSample[h].GetXaxis().GetLabels()):
                raise RuntimeError("htemp to be added has x-axis bin labels {} which are inconsistent with existing hist: {}".format(
                    list(htemp.GetXaxis().GetLabels()), list(dictFinalHistoAtSample[h].GetXaxis().GetLabels())))
        # Sep. 17 2017: scale first, then add with weight=1 to have "entries" correct
        htemp.Scale(plotWeight)
        returnVal = dictFinalHistoAtSample[h].Add(htemp)
    # if 'OptBinLQ60' in histoName:
    #  if dictFinalHistoAtSample[h].GetBinContent(binToExamine) != 0:
    #    print 'AFTER Add',histoName,'hist: sample=',sample,'bin',binToExamine,'content=',dictFinalHistoAtSample[h].GetBinContent(binToExamine),' error=',dictFinalHistoAtSample[h].GetBinError(binToExamine),'relError=',dictFinalHistoAtSample[h].GetBinError(binToExamine)/dictFinalHistoAtSample[h].GetBinContent(binToExamine)
    #    print
    if not returnVal:
        raise RuntimeError("ERROR: Failed adding hist named '{}' to {}".format(histoName, dictFinalHistoAtSample[h].GetName()))
    return dictFinalHistoAtSample


def WriteHistos(outputTfile, sampleHistoDict, verbose=False):
    outputTfile.cd()
    nHistos = len(sampleHistoDict)
    if verbose:
        print("Writing", nHistos, "histos...", end=' ')
    sys.stdout.flush()
    for histo in sampleHistoDict.values():  # for each hist contained in the sample's dict
        nbytes = 0
        if histo.ClassName() == "TMap":
            nbytes = histo.Write(histo.GetName(), r.TObject.kSingleKey)
        else:
            nbytes = histo.Write()
            # make systDiffs hist if needed
            if nbytes > 0 and "systematics" in histo.GetName().split("__")[-1].lower():
                systDiffsHist = MakeSystDiffsPlot(histo)
                nbytes = systDiffsHist.Write()
        if nbytes <= 0:
            raise RuntimeError("Error writing into the output file '{}': wrote {} bytes to file when writing object '{}'.".format(
                outputTfile.GetName(), nbytes, histo.GetName()))
    if verbose:
        print("Done.")
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
    statArr = np.zeros(11)  # for TH3F
    hist.GetStats(statArr)
    fTsumw = statArr[0]
    if fTsumw != 0:
        return False
    if hist.GetEntries() != 0:
        return False
    sumw = 0.0
    for i in range(0, hist.GetNcells()):
        sumw += hist.GetBinContent(i)
    return False if sumw != 0 else True


def RemoveHistoBins(hist, axis, labelsToRemove):
    if "TH2" in hist.__repr__():
        newHist = r.TH2D()
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
    systDiffs = r.TH2D(histName, histName, systHist.GetNbinsX(), 0, systHist.GetXaxis().GetXmax(), systHist.GetNbinsY(), 0, systHist.GetYaxis().GetXmax())
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
