#!/usr/bin/env python

# ---Import
import sys
import os
import string
import math
import re
import fnmatch


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
    dictSamples = {}
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
            # print "i=", i , "  piece= " , piece
            if i == 0:
                key = piece
                dictSamples[key] = []
            elif piece in dictSamples:
                dictSamples[key].extend(dictSamples[piece])
            else:
                # print 'GetSamplesToCombineDict: SanitizeDatasetNameFromFullDataset(',piece,')=',
                try:
                    piece = SanitizeDatasetNameFromFullDataset(piece)
                except IndexError:
                    print "ERROR: GetSamplesToCombineDict(): caught exception when trying to deal with pieces in line '"+line+'"'
                    exit(-1)
                # print piece
                dictSamples[key].append(piece)
    return dictSamples


def ParseXSectionFile(xsectionFile):
    xsectionDict = {}

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

    return xsectionDict


def lookupXSection(datasetNameFromInputList, xsectionDict):
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


def UpdateTable(inputTable, outputTable):
    if not outputTable:
        for j, line in enumerate(inputTable):
            outputTable[int(j)] = {
                "variableName": inputTable[j]["variableName"],
                "min1": inputTable[j]["min1"],
                "max1": inputTable[j]["max1"],
                "min2": inputTable[j]["min2"],
                "max2": inputTable[j]["max2"],
                "N": float(inputTable[j]["N"]),
                "errN": pow(float(inputTable[j]["errN"]), 2),
                "Npass": float(inputTable[j]["Npass"]),
                "errNpass": pow(float(inputTable[j]["errNpass"]), 2),
                "EffRel": float(0),
                "errEffRel": float(0),
                "EffAbs": float(0),
                "errEffAbs": float(0),
            }
    else:
        for j, line in enumerate(inputTable):
            # print 'outputTable[int(',j,')][N]=',outputTable[int(j)]['N'],'inputTable[',j,']','[N]=',inputTable[j]['N']
            outputTable[int(j)] = {
                "variableName": inputTable[j]["variableName"],
                "min1": inputTable[j]["min1"],
                "max1": inputTable[j]["max1"],
                "min2": inputTable[j]["min2"],
                "max2": inputTable[j]["max2"],
                "N": float(outputTable[int(j)]["N"]) + float(inputTable[j]["N"]),
                "errN": float(outputTable[int(j)]["errN"])
                + pow(float(inputTable[j]["errN"]), 2),
                "Npass": float(outputTable[int(j)]["Npass"])
                + float(inputTable[j]["Npass"]),
                "errNpass": float(outputTable[int(j)]["errNpass"])
                + pow(float(inputTable[j]["errNpass"]), 2),
                "EffRel": float(0),
                "errEffRel": float(0),
                "EffAbs": float(0),
                "errEffAbs": float(0),
            }
    return


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
    # this also (sneakily) converts 'errors' in the tables (which are really errSqr) to sqrt(errors)
    for j, line in enumerate(table):
        if j == 0:
            table[int(j)] = {
                "variableName": table[int(j)]["variableName"],
                "min1": table[int(j)]["min1"],
                "max1": table[int(j)]["max1"],
                "min2": table[int(j)]["min2"],
                "max2": table[int(j)]["max2"],
                "N": float(table[j]["N"]),
                "errN": int(0),
                "Npass": float(table[j]["Npass"]),
                "errNpass": int(0),
                "EffRel": int(1),
                "errEffRel": int(0),
                "EffAbs": int(1),
                "errEffAbs": int(0),
            }
        else:
            N = float(table[j]["N"])
            errN = math.sqrt(float(table[j]["errN"]))
            if float(N) > 0:
                errRelN = errN / N
            else:
                errRelN = float(0)

            Npass = float(table[j]["Npass"])
            errNpass = math.sqrt(float(table[j]["errNpass"]))
            if float(Npass) > 0:
                errRelNpass = errNpass / Npass
            else:
                errRelNpass = float(0)

            if Npass > 0 and N > 0:
                EffRel = Npass / N
                errRelEffRel = math.sqrt(errRelNpass * errRelNpass + errRelN * errRelN)
                errEffRel = errRelEffRel * EffRel

                EffAbs = Npass / float(table[0]["N"])
                errEffAbs = errNpass / float(table[0]["N"])
            else:
                EffRel = 0
                errEffRel = 0
                EffAbs = 0
                errEffAbs = 0

            table[int(j)] = {
                "variableName": table[int(j)]["variableName"],
                "min1": table[int(j)]["min1"],
                "max1": table[int(j)]["max1"],
                "min2": table[int(j)]["min2"],
                "max2": table[int(j)]["max2"],
                "N": N,
                "errN": errN,
                "Npass": Npass,
                "errNpass": errNpass,
                "EffRel": EffRel,
                "errEffRel": errEffRel,
                "EffAbs": EffAbs,
                "errEffAbs": errEffAbs,
            }
            # print table[j]
    return


# --- TODO: FIX TABLE FORMAT (NUMBER OF DECIMAL PLATES AFTER THE 0)


def WriteTable(table, name, file):
    print >> file, name
    print >> file, "variableName".rjust(25),
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
        print >> file, table[j]["variableName"].rjust(25),
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

    print "\n"
    print name
    print "variableName".rjust(25),
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
        print table[j]["variableName"].rjust(25),
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

    return


def GetUnscaledTotalEvents(unscaledRootFile, ttBarUnscaledRawSampleName=""):
    if len(ttBarUnscaledRawSampleName) <= 0:
        unscaledEvtsHist = unscaledRootFile.Get("EventsPassingCuts")
        unscaledTotalEvts = unscaledEvtsHist.GetBinContent(1)
    else:
        # scaledEvtsHist = unscaledRootFile.Get('histo1D__'+ttbarSampleName+'__EventsPassingCuts')
        unscaledEvtsHist = unscaledRootFile.Get(
            "histo1D__" + ttBarUnscaledRawSampleName + "__EventsPassingCuts"
        )
        # nonTTBarHist = combinedRootFile.Get('histo1D__'+nonTTBarSampleName+'__EventsPassingCuts')
        # unscaledTotalEvts = unscaledEvtsHist.GetBinContent(1)-nonTTBarHist.GetBinContent(1)
        # print 'GetUnscaledTotalEvents(): Got unscaled events=',unscaledTotalEvts,'from hist:',unscaledEvtsHist.GetName(),'in file:',unscaledRootFile.GetName()
        unscaledTotalEvts = unscaledEvtsHist.GetBinContent(1)
    return unscaledTotalEvts


def FindUnscaledRootFile(filepath, sampleName):
    filepath = os.path.expandvars(filepath.rstrip("/"))
    filepath = filepath[:filepath.rfind("/")]
    for root, dirs, files in os.walk(filepath):
        for name in files:
            # print "check against file:", name
            noExtName = re.sub("ext[0-9_]*", "", name)  # remove any "ext/extN" from file name
            noExtBackupName = noExtName.replace("backup_", "").replace("newPMX_", "")
            # print "compare", noExtBackupName, " to *"+sampleName+"*.root"
            if fnmatch.fnmatch(noExtBackupName, "*"+sampleName+"*.root"):
                return os.path.join(root, name)
    print "ERROR:  could not find unscaled root file for sample", sampleName
    print "Looked in:", filepath
    print "Exiting..."
    exit(-1)
