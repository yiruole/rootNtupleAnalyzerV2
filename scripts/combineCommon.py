#!/usr/bin/env python

# ---Import
import sys
import os
import string
import math
import re
from collections import OrderedDict
import ROOT as r

# FORMAT = "%(levelname)s %(module)s %(funcName)s line:%(lineno)d - %(message)s"
# logging.basicConfig(format=FORMAT, level=logging.INFO)

intLumi = -1
xsectionDict = {}


def SanitizeDatasetNameFromInputList(dataset_fromInputList):
    # "hack" for data-driven QCD samples: name is created by the createInputList script
    # do this first, since it's at the very end of the filename
    # XXX FIXME special hacks for datasets
    # if dataset_fromInputList.contains('_reduced_skim'):
    #  #dataset_fromInputList = dataset_fromInputList[0:dataset_fromInputList.find('_reduced_skim')]
    #  dataset_fromInputList.replace('_reduced_skim','')
    # print '0) SanitizeDatasetNameFromInputList() result is:'+dataset_fromInputList
    dataset_fromInputList = dataset_fromInputList.replace("_reduced_skim", "")
    # in rare cases, replace __ by _
    dataset_fromInputList = dataset_fromInputList.replace("__", "_")
    # XXX FIXME
    # # special hack for handling repated madgraphMLM samples
    # if dataset_fromInputList.endswith('_madgraphMLM'):
    #  dataset_fromInputList = dataset_fromInputList[0:dataset_fromInputList.find('_madgraphMLM')]
    # XXX FIXME
    # # special hack for handling repated amcatnloFXFX samples
    # elif dataset_fromInputList.endswith('_amcatnloFXFX'):
    #  dataset_fromInputList = dataset_fromInputList[0:dataset_fromInputList.find('_amcatnloFXFX')]
    if dataset_fromInputList.endswith("_pythia8"):
        dataset_fromInputList = dataset_fromInputList[
            0: dataset_fromInputList.find("_pythia8")
        ]
    # if '__' in dataset_fromInputList:
    #  dataset_fromInputList = dataset_fromInputList[0:dataset_fromInputList.find('__')]
    if dataset_fromInputList.endswith("_tree"):
        dataset_fromInputList = dataset_fromInputList[
            0: dataset_fromInputList.find("_tree")
        ]
    # if 'ZToEE' in dataset_fromInputList:
    #     print 'found ZToEE in dataset='+dataset_fromInputList
    #     dataset_fromInputList = dataset_fromInputList.replace('TuneCP5_', '').replace('13TeV-', '')
    # dataset_fromInputList = dataset_fromInputList.replace("ext2_", "").replace("ext1_", "").replace("ext_", "").replace("ext1", "").replace("ext", "")
    dataset_fromInputList = re.sub("ext[0-9_]*", "", dataset_fromInputList)
    dataset_fromInputList = dataset_fromInputList.replace("backup_", "")
    dataset_fromInputList = re.sub("newPMX[_]*", "", dataset_fromInputList)
    # dataset_fromInputList = re.sub("NNPDF[0-9_]*", "", dataset_fromInputList)
    dataset_fromInputList = dataset_fromInputList.rstrip("_")
    # print '1) SanitizeDatasetNameFromInputList() result is:'+dataset_fromInputList
    return dataset_fromInputList


def SanitizeDatasetNameFromFullDataset(dataset):
    # print 'SanitizeDatasetNameFromFullDataset: dataset looks like:'+dataset
    # this logic is somewhat copied from the submission script for the ntuples:
    #    https://github.com/CMSLQ/submitJobsWithCrabV2/blob/master/createAndSubmitJobsWithCrab3.py
    if "Run20" not in dataset:
        outputFileNames = []
        outputFileNames.append(dataset[1: dataset.find("_Tune")])
        outputFileNames.append(dataset[1: dataset.find("_13TeV")])
        try:
            outputFileNames.append(dataset.split("/")[1])
        except IndexError:
            print "ERROR: SanitizeDatasetNameFromFullDataset(): IndexError trying to split('/') dataset:", dataset, "; this can happen if this is a piece (not a full dataset) containing multiple samples that has not been defined earlier in the sampleListToCombineFile"
            raise

        # use the one with the shortest filename
        outputFile = sorted(outputFileNames, key=len)[0]
        # ignore all ext files, or rather, treat them the same as non-ext
        #if "ext" in dataset:
        #    extN = dataset[dataset.find("_ext") + 4]
        #    outputFile = outputFile + "_ext" + extN
        if "madgraphMLM" in dataset:
            outputFile += "_madgraphMLM"
        elif "amcatnloFXFX" in dataset or "amcnloFXFX" in dataset:
            outputFile += "_amcatnloFXFX"
        if 'ZToEE' in dataset:
            # print 'found ZToEE in dataset='+dataset
            outputFile = dataset.split("/")[1].replace('TuneCP5_', '').replace('13TeV-', '')
        # print 'SanitizeDatasetNameFromFullDataset:', dataset, 'shortened to:', outputFile
        # print 'choices were:',outputFileNames
    else:
        # outputFile = dataset[1:].replace('/','__')
        # outputFile = outputFile.split('__')[0]+'__'+outputFile.split('__')[1]
        outputFile = dataset[1:].replace("/", "_")
        # if(len(outputFile.split('_')) == 3):
        #  outputFile = outputFile.split('_')[0]+'_'+outputFile.split('_')[1]
        # elif(len(outputFile.split('_')) == 4):
        #  outputFile = outputFile.split('_')[0]+'_'+outputFile.split('_')[1]+'_'+outputFile.split('_')[2]
        outputFileSplit = outputFile.split("_")
        outputFile = ""
        for i in xrange(0, len(outputFileSplit) - 1):
            outputFile += outputFileSplit[i] + "_"
        outputFile = outputFile[:-1]
        # print '2 outputFile=',outputFile
        # print 'outputFile.split("_")=',outputFile.split('_')
    return outputFile


def GetSamplesToCombineDict(sampleListForMerging):
    dictSamples = OrderedDict()
    duplicateKeyError = False
    for l, line in enumerate(open(sampleListForMerging)):
        # ignore comments
        if line.startswith("#"):
            continue
        line = string.strip(line, "\n")
        # ignore empty lines
        if len(line) <= 0:
            continue

        # print 'line from samplesToCombineFile looks like:"'+line+'"'
        # line looks like: "ZJet_Madgraph_Inc    DYJetsToLL_M-5to50 DYJetsToLL_M-50"
        # or "LQ_M200   /LQToUE_M-200_BetaOne_TuneCUETP8M1_13TeV-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2/MINIAODSIM"

        # the rule is that the name of each 'piece' here must match the inputList name and filename
        if len(line.split()) < 2:
            print "ERROR: GetSamplesToCombineDict(): cannot deal with line which does not contain at least one piece: '"+line+"'"
            exit(-1)
        for i, piece in enumerate(line.split()):
            # print "GetSamplesToCombineDict(): i=", i, "  piece= ", piece
            if i == 0:
                key = piece
                if key in dictSamples.keys():
                    print "ERROR: GetSamplesToCombineDict(): key '{}' in line #{} has already been defined earlier in the sampleListForMerging file!".format(key, l+1)
                    print "\toffending line #{} looks like '{}'".format(l+1, line)
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
        exit(-1)
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
    for sampleName, sampleList in dictSamples.items():
        outputDict[sampleName] = ExpandPieces(sampleList, dictSamples)
    return outputDict


def ParseXSectionFile(xsectionFile):
    for line in open(os.path.expandvars(xsectionFile)):

        # ignore comments
        if line.startswith("#"):
            continue
        line = string.strip(line, "\n")
        line = line.split("#")[0]  # strip off anything after any '#' if present
        # ignore empty lines
        if len(line) <= 0:
            continue

        try:
            dataset, xsection_val = string.split(line)
        except ValueError:
            print 'ERROR: could not split line "', line, '"'
            exit(-1)

        # print 'ParseXSectionFile: line looked like:"'+line+'"; call SanitizeDatasetNameFromFullDataset on dataset=',dataset
        outputFile = SanitizeDatasetNameFromFullDataset(dataset)
        xsectionDict[outputFile] = xsection_val
        # print outputFile + " " + xsection_val


def lookupXSection(datasetNameFromInputList):
    verbose = False
    if len(xsectionDict) <= 0:
        print
        print "ERROR: xsectionDict is empty. Cannot lookupXSection for", datasetNameFromInputList
        exit(-1)
    for dataset in xsectionDict.keys():
        if verbose and "LQ" in dataset:
            print 'INFO: dataset in xsec file:', dataset, ' starts with the one we are asking for:', datasetNameFromInputList, '?'
        if dataset.startswith(datasetNameFromInputList):
            if verbose:
                print 'INFO: dataset in xsec file:', dataset, 'starts with the one we are asking for:', datasetNameFromInputList
            # check to make sure dataset in xsec file up to first underscore matches the datasetNameFromInputList
            # this should catch a case where we have TT as the datasetNameFromInputList [e.g., powheg] and it would otherwise match TTJets in the xsec file
            if datasetNameFromInputList.startswith(dataset.split("_")[0]):
                # print 'INFO: found dataset in xsec file:', dataset, 'that starts with the one we are asking for:', datasetNameFromInputList
                return xsectionDict[dataset]
    print
    print "ERROR"
    # for key in sorted(xsectionDict.iterkeys()):
    #  print 'sample=',key,'xsection=',xsectionDict[key]
    print "ERROR: lookupXSection(): xsectionDict does not have an entry for", datasetNameFromInputList, "; i.e., no dataset in xsectionDict starts with this."
    exit(-1)


def ParseDatFile(datFilename):
    # ---Read .dat table for current dataset
    data = {}
    column = []
    lineCounter = int(0)

    # print '(opening:',inputDataFile,
    sys.stdout.flush()
    with open(datFilename) as datFile:
        for j, line in enumerate(datFile):
            # ignore comments
            if re.search("^###", line):
                continue
            line = string.strip(line, "\n")
            # print "---> lineCounter: " , lineCounter
            # print line

            if lineCounter == 0:
                for i, piece in enumerate(line.split()):
                    column.append(piece)
            else:
                for i, piece in enumerate(line.split()):
                    if i == 0:
                        data[int(piece)] = {}
                        row = int(piece)
                    else:
                        data[row][column[i]] = piece
                        # print data[row][ column[i] ]

            lineCounter = lineCounter + 1
    return data


def FillTableEfficiencies(table, rootFileName, weight, sampleName=""):
    verbose = True
    tfile = r.TFile.Open(rootFileName)
    if not tfile:
        print "ERROR: could not open file '{}'. Exiting here.".format(rootFileName)
        exit(-1)
    if sampleName:
        histName = "profile1D__{}__EventsPassingCuts".format(sampleName)
    else:
        histName = "EventsPassingCuts"
    eventsPassingHist = tfile.Get(histName)
    if not eventsPassingHist:
        raise RuntimeError("ERROR: could not find hist '{}' in file '{}'. Exiting here.".format(histName, rootFileName))
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
                print "--> FillTableEfficiencies(): i={}; FillTableEfficiencies() -- hist {}".format(i, hist.GetName())
                print "FillTableEfficiencies(): hist: GetBinContent(1) = {} +/- {}".format(hist.GetBinContent(1), hist.GetBinError(1))
                print "FillTableEfficiencies(): cutHists[i-1]: GetBinContent(1) = {} +/- {}".format(cutHists[i-1].GetBinContent(1), cutHists[i-1].GetBinError(1))
                print "FillTableEfficiencies(): noCutHist: GetBinContent(1) = {} +/- {}".format(noCutHist.GetBinContent(1), noCutHist.GetBinError(1))
                print "- Creating TEfficiencyRel"
                sys.stdout.flush()
            r.gErrorIgnoreLevel = 0
            if(hist.GetBinContent(1) > cutHists[i-1].GetBinContent(1)):
                # here, passed > total, so root will complain; this can happen if we remove a negative weight event with this cut
                print "\tINFO: passed > pass(N-1); attempting to silence error messages!"
                sys.stdout.flush()
                r.gErrorIgnoreLevel = r.kError+1
                # r.gErrorIgnoreLevel = 3001
                #r.gROOT.ProcessLine("gErrorIgnoreLevel = 3001;")
            table[i]["TEfficiencyRel"] = r.TEfficiency(hist, cutHists[i-1])
            table[i]["TEfficiencyRel"].SetWeight(weight)
            print "- Creating TEfficiencyAbs"
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
        raise RuntimeError("ERROR: could not open file '{}'. Exiting here.".format(rootFileName))
    if sampleName:
        histName = "profile1D__{}__EventsPassingCuts".format(sampleName)
    else:
        histName = "EventsPassingCuts"
    eventsPassingHist = tfile.Get(histName)
    if not eventsPassingHist:
        raise RuntimeError("ERROR: could not find hist '{}' in file '{}'. Exiting here.".format(histName, rootFileName))

    for j, line in enumerate(table):
        iBin = j+1
        errNpassSqr = eventsPassingHist.GetSumw2().At(iBin)
        if j > 0:
            errNSqr = eventsPassingHist.GetSumw2().At(iBin-1)
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
            # print 'data[j]=',data[j]
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
            errNpassSqr = pow(float(data[j]["errNpass"]) * weight, 2)
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
        print "ERROR: no outputTable found! cannot subtract input from nothing; FATAL"
        exit(-1)
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
        print "ERROR: no inputTable found! cannot scale nothing; FATAL"
        exit(-1)
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
        print "ERROR: no inputTable found! cannot convert nothing; FATAL"
        exit(-1)
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


def WriteTable(table, name, file, printToScreen=True):
    print >> file, "### "+name
    print >> file, "#id".rjust(4, " "),
    print >> file, "variableName".rjust(35),
    print >> file, "min1".rjust(15),
    print >> file, "max1".rjust(15),
    print >> file, "min2".rjust(15),
    print >> file, "max2".rjust(15),
    print >> file, "Npass".rjust(17),
    print >> file, "errNpass".rjust(17),
    print >> file, "EffRel".rjust(15),
    print >> file, "errEffRel".rjust(15),
    print >> file, "EffAbs".rjust(15),
    print >> file, "errEffAbs".rjust(15)

    for j, line in enumerate(table):
        print >> file, str(j).rjust(4, " "),
        print >> file, table[j]["variableName"].rjust(35),
        print >> file, table[j]["min1"].rjust(15),
        print >> file, table[j]["max1"].rjust(15),
        print >> file, table[j]["min2"].rjust(15),
        print >> file, table[j]["max2"].rjust(15),
        ###
        if table[j]["Npass"] >= 0.1:
            print >> file, ("%.04f" % table[j]["Npass"]).rjust(17),
        else:
            print >> file, ("%.04e" % table[j]["Npass"]).rjust(17),
        ###
        if table[j]["errNpass"] >= 0.1:
            print >> file, ("%.04f" % table[j]["errNpass"]).rjust(17),
        else:
            print >> file, ("%.04e" % table[j]["errNpass"]).rjust(17),
        ###
        if table[j]["EffRel"] >= 0.1:
            print >> file, ("%.04f" % table[j]["EffRel"]).rjust(15),
        else:
            print >> file, ("%.04e" % table[j]["EffRel"]).rjust(15),
        ###
        if table[j]["errEffRel"] >= 0.1:
            print >> file, ("%.04f" % table[j]["errEffRel"]).rjust(15),
        else:
            print >> file, ("%.04e" % table[j]["errEffRel"]).rjust(15),
        ###
        if table[j]["EffAbs"] >= 0.1:
            print >> file, ("%.04f" % table[j]["EffAbs"]).rjust(15),
        else:
            print >> file, ("%.04e" % table[j]["EffAbs"]).rjust(15),
        ###
        if table[j]["errEffAbs"] >= 0.1:
            print >> file, ("%.04f" % table[j]["errEffAbs"]).rjust(15)
        else:
            print >> file, ("%.04e" % table[j]["errEffAbs"]).rjust(15)
        ###

    print >> file, "\n"

    # --- print to screen
    if printToScreen:
        print "\n"
        print "### "+name
        print "#id".rjust(4, " "),
        print "variableName".rjust(35),
        print "min1".rjust(15),
        print "max1".rjust(15),
        print "min2".rjust(15),
        print "max2".rjust(15),
        print "Npass".rjust(17),
        print "errNpass".rjust(17),
        print "EffRel".rjust(15),
        print "errEffRel".rjust(15),
        print "EffAbs".rjust(15),
        print "errEffAbs".rjust(15)

        for j, line in enumerate(table):
            print str(j).rjust(4, " "),
            print table[j]["variableName"].rjust(35),
            print table[j]["min1"].rjust(15),
            print table[j]["max1"].rjust(15),
            print table[j]["min2"].rjust(15),
            print table[j]["max2"].rjust(15),
            ###
            if table[j]["Npass"] >= 0.1:
                print ("%.04f" % table[j]["Npass"]).rjust(17),
            else:
                print ("%.04e" % table[j]["Npass"]).rjust(17),
            ###
            if table[j]["errNpass"] >= 0.1:
                print ("%.04f" % table[j]["errNpass"]).rjust(17),
            else:
                print ("%.04e" % table[j]["errNpass"]).rjust(17),
            ###
            if table[j]["EffRel"] >= 0.1:
                print ("%.04f" % table[j]["EffRel"]).rjust(15),
            else:
                print ("%.04e" % table[j]["EffRel"]).rjust(15),
            ###
            if table[j]["errEffRel"] >= 0.1:
                print ("%.04f" % table[j]["errEffRel"]).rjust(15),
            else:
                print ("%.04e" % table[j]["errEffRel"]).rjust(15),
            ###
            if table[j]["EffAbs"] >= 0.1:
                print ("%.04f" % table[j]["EffAbs"]).rjust(15),
            else:
                print ("%.04e" % table[j]["EffAbs"]).rjust(15),
            ###
            if table[j]["errEffAbs"] >= 0.1:
                print ("%.04f" % table[j]["errEffAbs"]).rjust(15)
            else:
                print ("%.04e" % table[j]["errEffAbs"]).rjust(15)
            ###


def GetSampleHistosFromTFile(tfileName, sampleHistos, sampleName=""):
    tfile = r.TFile(tfileName)
    # sampleHistos = []
    for key in tfile.GetListOfKeys():
        # histoName = file.GetListOfKeys()[h].GetName()
        # htemp = file.Get(histoName)
        histoName = key.GetName()
        htemp = key.ReadObj()
        if not htemp or htemp is None:
            raise RuntimeError("ERROR: failed to get histo named:", histoName, "from file:", tfile.GetName())
        r.SetOwnership(htemp, True)
        if sampleName in histoName:
            htemp.SetDirectory(0)
            sampleHistos.append(htemp)
    tfile.Close()
    if len(sampleHistos) < 1:
        raise RuntimeError(
                "ERROR: GetSampleHistosFromTFile({}, {}) -- failed to read any histos for the sampleName from this file! Exiting."
                .format(tfile.GetName(), sampleName))
    # return sampleHistos


def AddHistosFromFile(rootFileName, sampleHistoDict, sample="", plotWeight=1.0):
    # ---Combine histograms using PYROOT
    tfile = r.TFile(rootFileName)
    # nHistos = len(file.GetListOfKeys())
    # print "\tnKeys: " , nHistos
    # print 'list of keys in this rootfile:',file.GetListOfKeys()
    # loop over histograms in rootfile
    # for h in range(0, nHistos):
    h = 0
    for key in tfile.GetListOfKeys():
        # histoName = file.GetListOfKeys()[h].GetName()
        # htemp = file.Get(histoName)
        histoName = key.GetName()
        htemp = key.ReadObj()
        if not htemp:
            print "ERROR: failed to get histo named:", histoName, "from file:", tfile.GetName()
            exit(-1)
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
                    print "ERROR: failed to get histo named:", hname, "from file:", tfile.GetName()
                    exit(-1)
                # else:
                #  print "INFO: found key in subdir named:",hname,"hist name:",htmp.GetName()
                r.SetOwnership(htmp, True)
                updateSample(
                    sampleHistoDict, htmp, h, sample, plotWeight
                )
                h += 1
        else:
            updateSample(
                sampleHistoDict, htemp, h, sample, plotWeight
            )
            h += 1
    tfile.Close()


def GetShortHistoName(histName):
    if "histo1D" in histName or "histo2D" in histName or "histo3D" in histName or "profile1D" in histName:
        return histName.split(histName.split("__")[1])[1].strip("_")
    else:
        return histName


def UpdateHistoDict(sampleHistoDict, pieceHistoList, sample="", plotWeight=1.0):
    idx = 0
    for pieceHisto in pieceHistoList:
        pieceHistoName = pieceHisto.GetName()
        pieceHisto.SetName(GetShortHistoName(pieceHistoName))
        if idx in sampleHistoDict:
            sampleHisto = sampleHistoDict[idx]
            # sampleHistoName = sampleHisto.GetName()
            # sampleHisto.SetName(GetShortHistoName(sampleHistoName))
            if pieceHisto.GetName() not in sampleHisto.GetName():
                print "ERROR: apparently non-matching histos between sample hist with name '{}' and piece hist with name '{}'. Quitting here".format(
                        sampleHisto.GetName(), pieceHisto.GetName())
                exit(-2)
        sampleHistoDict = updateSample(sampleHistoDict, pieceHisto, idx, sample, plotWeight)
        # if idx == 0:
        #     print "INFO: UpdateHistoDict for sample {}: added pieceHisto {} with entries {} to sampleHistoDict[idx], which has name {} and entries {}".format(
        #             sample, pieceHisto.GetName(), pieceHisto.GetEntries(), sampleHistoDict[idx].GetName(), sampleHistoDict[idx].GetEntries())
        idx += 1
        if "eventspassingcuts" in pieceHisto.GetName().lower() and "unscaled" not in pieceHisto.GetName().lower():
            # create new EventsPassingCuts hist that doesn't have scaling/reweighting by int. lumi.
            # print "INFO: create new EventsPassingCuts hist from {} that doesn't have scaling/reweighting by int. lumi.".format(pieceHisto.GetName())
            unscaledEvtsPassingCuts = pieceHisto.Clone()
            unscaledEvtsPassingCuts.SetNameTitle(pieceHisto.GetName()+"_unscaled", pieceHisto.GetTitle()+"_unscaled")
            sampleHistoDict = updateSample(sampleHistoDict, unscaledEvtsPassingCuts, idx, sample, 1.0)
            idx += 1
    return sampleHistoDict


def updateSample(dictFinalHistoAtSample, htemp, h, sample, plotWeight):
    histoName = htemp.GetName()
    histoTitle = htemp.GetTitle()
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
        else:
            # print 'not combining classtype of',htemp.ClassName()
            return
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
        # Sep. 17 2017: scale first, then add with weight=1 to have "entries" correct
        htemp.Scale(plotWeight)
        returnVal = dictFinalHistoAtSample[h].Add(htemp)
    #  XXX DEBUG
    # if 'OptBinLQ60' in histoName:
    #  if dictFinalHistoAtSample[h].GetBinContent(binToExamine) != 0:
    #    print 'AFTER Add',histoName,'hist: sample=',sample,'bin',binToExamine,'content=',dictFinalHistoAtSample[h].GetBinContent(binToExamine),' error=',dictFinalHistoAtSample[h].GetBinError(binToExamine),'relError=',dictFinalHistoAtSample[h].GetBinError(binToExamine)/dictFinalHistoAtSample[h].GetBinContent(binToExamine)
    #    print
    if not returnVal:
        print 'ERROR: Failed adding hist named"' + histoName + '"to', dictFinalHistoAtSample[
            h
        ].GetName()
        exit(-1)
    return dictFinalHistoAtSample


def WriteHistos(outputTfile, sampleHistoDict, verbose=False):
    outputTfile.cd()
    nHistos = len(sampleHistoDict)
    if verbose:
        print "Writing", nHistos, "histos...",
    sys.stdout.flush()
    for histo in sampleHistoDict.itervalues():  # for each hist contained in the sample's dict
        histo.Write()
    if verbose:
        print "Done."
    sys.stdout.flush()


def GetUnscaledTotalEvents(combinedRootFile, sampleName):
    # XXX FIXME TODO: now moved to just using TProfile;
    # 1) remove code for hist support
    # 2) remove exception for QCD/DATA
    if "DATA" in sampleName:
        # no scaling done to data
        histName = "profile1D__" + sampleName + "__EventsPassingCuts"
    else:
        histName = "profile1D__" + sampleName + "__EventsPassingCuts_unscaled"
    # scaledEvtsHist = combinedRootFile.Get('histo1D__'+ttbarSampleName+'__EventsPassingCuts')
    unscaledEvtsHist = combinedRootFile.Get(histName)
    if not unscaledEvtsHist:
        # print "WARN: failed reading hist {} from root file {}".format(histName, combinedRootFile.GetName())
        oldHistName = histName
        if "DATA" in sampleName:
            histName = "histo1D__" + sampleName + "__EventsPassingCuts"
        else:
            histName = "histo1D__" + sampleName + "__EventsPassingCuts_unscaled"
        unscaledEvtsHist = combinedRootFile.Get(histName)
    if not unscaledEvtsHist:
        raise RuntimeError("could not get hist {} nor hist {} from root file {}".format(oldHistName, histName, combinedRootFile.GetName()))
    # print "INFO: reading hist {} from root file {}".format(histName, combinedRootFile.GetName())
    # nonTTBarHist = combinedRootFile.Get('histo1D__'+nonTTBarSampleName+'__EventsPassingCuts')
    # unscaledTotalEvts = unscaledEvtsHist.GetBinContent(1)-nonTTBarHist.GetBinContent(1)
    # print 'GetUnscaledTotalEvents(): Got unscaled events=',unscaledTotalEvts,'from hist:',unscaledEvtsHist.GetName(),'in file:',unscaledRootFile.GetName()
    if unscaledEvtsHist.ClassName() == "TProfile":
        unscaledTotalEvts = unscaledEvtsHist.GetBinContent(1)*unscaledEvtsHist.GetBinEntries(1)
    else:
        unscaledTotalEvts = unscaledEvtsHist.GetBinContent(1)
    return unscaledTotalEvts


#def FindUnscaledRootFile(filepath, sampleName):
#    for root, dirs, files in os.walk(filepath):
#        for name in files:
#            # print "FindUnscaledRootFile({}, {}): check against file: {}".format(filepath, sampleName, name)
#            noExtName = re.sub("ext[0-9_]*", "", name)  # remove any "ext/extN" from file name
#            noExtBackupName = noExtName.replace("backup_", "").replace("newPMX_", "")
#            # print "compare", noExtBackupName, " to *"+sampleName+"*.root"
#            # don't match an amcatnloFXFX file with a sampleName that doesn't include it
#            if "amcatnloFXFX" in name and "amcatnloFXFX" not in sampleName:
#                continue
#            if fnmatch.fnmatch(noExtBackupName, "*"+sampleName+"*.root"):
#                return os.path.join(root, name)
#    return None


def GetXSecTimesIntLumi(sampleNameFromDataset):
    # print 'GetXSecTimesIntLumi(',sampleNameFromDataset+')'
    xsection = float(lookupXSection(sampleNameFromDataset))
    intLumiF = float(intLumi)
    return xsection * intLumiF


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
        print "GetRatesAndErrors(", combinedRootFile.GetName(), sampleName, selection, doEEJJ, isDataOrQCD, isTTBarFromData, ")"
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
    if not scaledHist:
        # oldHistName = scaledHistName
        # scaledHistName = "histo1D__"+sampleName+"__"+histName
        # scaledHist = combinedRootFile.Get(scaledHistName)
        # if not scaledHist:
        #     raise RuntimeError("ERROR: could not find hist {} not hist {} in file: {}".format(oldHistName, scaledHistName, combinedRootFile.GetName()))
        raise RuntimeError("ERROR: could not find hist {} in file: {}".format(scaledHistName, combinedRootFile.GetName()))
    # min_M_ej_LQ300 for eejj
    if "preselection" not in selection:
        if doEEJJ:
            selection = "min_M_ej_"+selection
        else:
            # enujj
            selection = "MT_"+selection
    selectionBin = scaledHist.GetXaxis().FindFixBin(selection)
    if scaledHist.ClassName() == "TProfile":
        scaledInt = scaledHist.GetBinContent(selectionBin)*scaledHist.GetBinEntries(selectionBin)
        scaledIntErr = math.sqrt(scaledHist.GetSumw2().At(selectionBin))
    else:
        scaledInt = scaledHist.GetBinContent(selectionBin)
        scaledIntErr = scaledHist.GetBinError(selectionBin)
    rate = scaledInt
    rateErr = scaledIntErr
    if not isDataOrQCD:
        unscaledHistName = "profile1D__"+sampleName+"__"+histName+"_unscaled"
        unscaledHist = combinedRootFile.Get(unscaledHistName)
        if not unscaledHist:
            raise RuntimeError("ERROR: could not find hist {} in file: {}".format(unscaledHistName, combinedRootFile.GetName()))
        unscaledRate = unscaledHist.GetBinEntries(selectionBin)
    else:
        unscaledRate = scaledHist.GetBinEntries(selectionBin)
    return rate, rateErr, unscaledRate
