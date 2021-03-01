#!/usr/bin/env python

# ---Import
import sys
import string
from optparse import OptionParser
import os.path
from ROOT import TFile, gROOT
import re
import glob

import combineCommon


def CalculateWeight(Ntot, xsection_val, intLumi, sumWeights, lhePdfWeightSumw=0.0, pdfReweight=False):
    if xsection_val == "-1":
        weight = 1.0
        plotWeight = 1.0
        xsection_X_intLumi = Ntot
        sumWeights = -1
        print "\t[data]",
        sys.stdout.flush()
    else:
        xsection_X_intLumi = float(xsection_val) * float(intLumi)
        print "\t[MC]",
        sys.stdout.flush()

        # removed 2018 March 2
        # XXX: This is incorrect anyway.
        # if re.search('TT_',dataset_fromInputList):
        #  avgTopPtWeight = sumTopPtWeights / Ntot
        #  print '\tapplying extra TopPt weight of',avgTopPtWeight,'to',dataset_fromInputList
        #  xsection_X_intLumi/=avgTopPtWeight

        if pdfReweight:
            print "\tapplying LHEPdfWeight={} to dataset={}".format(lhePdfWeightSumw, dataset_fromInputList)+"[instead of original sumWeights={}]".format(sumWeights)
            sumWeights = lhePdfWeightSumw

        # now calculate the actual weight
        # weight = 1.0
        # if Ntot == 0:
        #     weight = float(0)
        # else:
        #     print "\tapplying sumWeights=", sumWeights, "to", dataset_fromInputList
        #     weight = xsection_X_intLumi / sumWeights
        print "\tapplying sumWeights=", sumWeights, "to", dataset_fromInputList
        weight = xsection_X_intLumi / sumWeights
        plotWeight = weight / 1000.0
    return weight, plotWeight, xsection_X_intLumi


doProfiling = False
# for profiling
if doProfiling:
    from cProfile import Profile
    from pstats import Stats

    prof = Profile()
    prof.disable()  # i.e. don't time imports
    # import time

    prof.enable()  # profiling back on
# for profiling


# ---Run
# Turn off warning messages
gROOT.ProcessLine("gErrorIgnoreLevel=2001;")

# ---Option Parser
# --- TODO: WHY PARSER DOES NOT WORK IN CMSSW ENVIRONMENT? ---#
usage = "usage: %prog [options] \nExample: \n./combinePlots.py -i /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config/inputListAllCurrent.txt -c analysisClass_genStudies -d /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/data/output -l 100 -x /home/santanas/Data/Leptoquarks/RootNtuples/V00-00-06_2008121_163513/xsection_pb_default.txt -o /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/data/output -s /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config/sampleListForMerging.txt"

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
    "-l",
    "--intLumi",
    dest="intLumi",
    help="results are rescaled to the integrated luminosity INTLUMI (in pb-1)",
    metavar="INTLUMI",
)

parser.add_option(
    "-x",
    "--xsection",
    dest="xsection",
    help="the file XSEC contains the cross sections (in pb) for all the datasets (full path required). Use -1 as cross section value for no-rescaling",
    metavar="XSEC",
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
    "--sampleListForMerging",
    dest="sampleListForMerging",
    help="put in the file SAMPLELIST the name of the sample with the associated strings which should  match with the dataset name (full path required)",
    metavar="SAMPLELIST",
)

parser.add_option(
    "-t",
    "--tablesOnly",
    action="store_true",
    dest="tablesOnly",
    default=False,
    help="only combine tables, do not do plots",
    metavar="TABLESONLY",
)

parser.add_option(
    "-b",
    "--ttbarBkg",
    action="store_true",
    dest="ttbarBkg",
    default=False,
    help="do the ttbar background prediction from data; don't write out any other plots",
    metavar="TTBARBKG",
)

parser.add_option(
    "-q",
    "--qcdClosure",
    action="store_true",
    dest="qcdClosure",
    default=False,
    help="do the QCD observed 1 pass HEEP 1 fail HEEP yield (cej), subtracting non-QCD processes from data using MC; don't write out any other plots",
    metavar="QCDCLOSURE",
)
parser.add_option(
    "-f",
    "--logFile",
    dest="logFile",
    default="",
    help="log file from the analysis (used to look for errors)",
    metavar="LOGFILE",
)


(options, args) = parser.parse_args()

if len(sys.argv) < 14:
    print usage
    sys.exit()

# print options.analysisCode

# ---Check if sampleListForMerging file exists
if os.path.isfile(options.sampleListForMerging) is False:
    print "ERROR: file " + options.sampleListForMerging + " not found"
    print "exiting..."
    sys.exit()

# ---Check if xsection file exists
if os.path.isfile(options.xsection) is False:
    print "ERROR: file " + options.xsection + " not found"
    print "exiting..."
    sys.exit()

print "Launched like:"
print "python ",
for arg in sys.argv:
    print " " + arg,
print

doPDFReweight2016LQSignals = False
if doPDFReweight2016LQSignals:
    print "Doing PDF reweighting for 2016 LQ B/D signal samples"

# check logfile for errors if given
# FIXME: this seems obsolete
if os.path.isfile(options.logFile):
    foundError = False
    with open(options.logFile, "r") as logFile:
        for line in logFile:
            if (
                "error" in line
                or "ERROR" in line
                and "ERROR in cling::CIFactory::createCI(): cannot extract standard library include paths!"
                not in line
            ):
                print "Found error line in logfile:", line
                foundError = True
    if foundError:
        print "WARNING: FOUND ERRORS IN THE LOGFILE! bailing out..."
        sys.exit(-2)
    else:
        print "Great! Logfile was checked and was completely clean!"
else:
    print "WARNING: cannot open log file named '" + options.logFile + "'; not checking it"

if not options.tablesOnly:
    outputTfile = TFile(
        options.outputDir + "/" + options.analysisCode + "_plots.root", "RECREATE", "", 207
    )

xsectionDict = combineCommon.ParseXSectionFile(options.xsection)
# print 'Dataset      XSec'
# for key,value in xsectionDict.iteritems():
#  print key,'  ',value

dictSamples = combineCommon.GetSamplesToCombineDict(options.sampleListForMerging)
dictSamplesPiecesAdded = {}
for key in dictSamples.iterkeys():
    dictSamplesPiecesAdded[key] = []

# --- Declare efficiency tables
dictFinalTables = {}
# --- Declare histograms
dictFinalHisto = {}

# check to make sure we have xsections for all samples
for lin in open(options.inputList):
    lin = string.strip(lin, "\n")
    if lin.startswith("#"):
        continue
    dataset_fromInputList = string.split(string.split(lin, "/")[-1], ".")[0]
    dataset_fromInputList = dataset_fromInputList.replace("_tree", "")
    xsection_val = combineCommon.lookupXSection(
        combineCommon.SanitizeDatasetNameFromInputList(
            dataset_fromInputList.replace("_tree", "")
        )
    )

# ---Loop over datasets in the inputlist to check if dat/root files are there
foundAllFiles = True
dictDatasetsFileNames = dict()
print
print "Checking for root/dat files from samples in inputList...",
sys.stdout.flush()
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
    # rootFileName2 = rootFileName1.replace(".root", "_0.root")
    fullPath1 = options.inputDir
    # fullPath2: condor style with one job per dataset
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
    fileList = glob.glob(fullPath1+"/"+rootFileName1)
    completeNamesTried.append(fullPath1+"/"+rootFileName1)
    if len(fileList) < 1:
        fileList = glob.glob(fullPath2+"/"+rootFileName1.replace(".root", "*.root"))
        completeNamesTried.append(fullPath2+"/"+rootFileName1.replace(".root", "*.root"))
    if len(fileList) < 1:
        print
        print "ERROR: could not find root file for dataset:", dataset_fromInputList
        print "ERROR: tried these full paths:", completeNamesTried
        foundAllFiles = False
    elif len(fileList) > 1:
        print "ERROR: found {} root files for dataset: {}".format(len(fileList), dataset_fromInputList)
        print "ERROR: considered these full paths: {}".format(completeNamesTried)
        foundAllFiles = False
    sampleName = combineCommon.SanitizeDatasetNameFromInputList(dataset_fromInputList.replace("_tree", ""))
    dictDatasetsFileNames[dataset_fromInputList] = fileList[0]

if not foundAllFiles:
    print "Some files not found. Exiting..."
    sys.exit()
else:
    print "\bDone.  All root/dat files are present."
    print

if not os.path.isdir(options.outputDir):
    os.makedirs(options.outputDir)

outputTableFile = open(
    options.outputDir + "/" + options.analysisCode + "_tables.dat", "w"
)

# loop over samples defined in sampleListForMerging
for sample, pieceList in dictSamples.iteritems():
    # if 'ALLBKG_MG_HT' in sample:
    #    print "look at sample named:",sample
    print "-->Look at sample named:", sample, "with piecelist=", pieceList

    # # init if needed
    # if sample not in dictFinalTables:
    #     dictFinalTables[sample] = {}
    # if sample not in dictFinalHisto:
    #     dictFinalHisto[sample] = {}
    histoDictThisSample = {}
    tablesThisSample = []

    # piecesToAdd = []
    # print "dictDatasetsFileNames=", dictDatasetsFileNames
    # for piece in pieceList:
    #     if "/" in piece:
    #         piece = combineCommon.SanitizeDatasetNameFromFullDataset(piece)
    #     if piece in dictDatasetsFileNames.iterkeys():
    #         sampleHistos = combineCommon.GetSampleHistosFromTFile(outputTfile, piece)
    #         print "INFO: replace non-dataset piece '{}' in sample '{}' by combining dicts.".format(piece, sample)
    #         combineCommon.UpdateHistoDict(dictFinalHisto[sample], sampleHistos, sample)
    #         dictSamplesPiecesAdded[sample].append(piece)
    #         # FIXME TODO add tables
    #     else:
    #         print "ERROR: can't handle piece '{}' in sample '{}'; perhaps it was not defined already in the sampleList. Exiting.".format(
    #                 piece, sample)
    #         print "dictDatasetsFileNames:", dictDatasetsFileNames
    #         exit(-2)
    piecesToAdd = combineCommon.ExpandPieces(pieceList, dictSamples)
    # piecesToAdd = []
    # for piece in pieceList:
    #     if "/" in piece:
    #         piece = combineCommon.SanitizeDatasetNameFromFullDataset(piece)
    #         piecesToAdd.append(piece)
    #     else:
    #         pieces = [combineCommon.SanitizeDatasetNameFromFullDataset(x) for x in dictSamples[piece]]
    #         piecesToAdd.extend(pieces)
    # print "INFO: piecesToAdd:", piecesToAdd

    # ---Loop over datasets in the inputlist
    # TODO: rewrite to be more efficient (loop over piecesToAdd instead)
    for dataset_fromInputList, rootFile in dictDatasetsFileNames.iteritems():
        if len(dictSamplesPiecesAdded[sample]) == len(piecesToAdd):
            break  # we're done!
        toBeUpdated = False
        matchingPiece = combineCommon.SanitizeDatasetNameFromInputList(
            dataset_fromInputList.replace("_tree", "")
        )
        # print "INFO: possible matchingPiece from inputList=", matchingPiece
        # print "INFO: piecesToAdd=", piecesToAdd
        if matchingPiece in piecesToAdd:
            toBeUpdated = True
            # print 'INFO: matchingPiece in piecesToAdd: toBeUpdated=True'
        # if no match, maybe the dataset in the input list ends with "_reduced_skim", so try to match without that
        elif matchingPiece.endswith("_reduced_skim"):
            matchingPieceNoRSK = matchingPiece[0: matchingPiece.find("_reduced_skim")]
            if matchingPieceNoRSK in piecesToAdd:
                toBeUpdated = True
                matchingPiece = matchingPieceNoRSK
                # print 'INFO: matchingPieceNoRSK in pieceList: toBeUpdated=True, matchingPiece=', matchingPieceNoRSK
        # elif matchingPiece.endswith("_ext1"):
        #     matchingPieceNoExt1 = matchingPiece[0: matchingPiece.find("_ext1")]
        #     if matchingPieceNoExt1 in pieceList:
        #         toBeUpdated = True
        #         matchingPiece = matchingPieceNoExt1
        #         # print 'INFO: matchingPieceNoExt1 in pieceList: toBeUpdated=True, matchingPiece=', matchingPieceNoExt1
        if not toBeUpdated:
            continue

        # prepare to combine
        print "\tfound matching dataset:", matchingPiece + " ... ",
        # print combineCommon.SanitizeDatasetNameFromInputList(dataset_fromInputList),dataset_fromInputList,
        sys.stdout.flush()

        inputDatFile = rootFile.replace(".root", ".dat")
        # sampleHistos = combineCommon.GetSampleHistosFromTFile(rootFile, matchingPiece)
        sampleHistos = []
        combineCommon.GetSampleHistosFromTFile(rootFile, sampleHistos)

        print "looking up xsection...",
        sys.stdout.flush()
        xsection_val = combineCommon.lookupXSection(
            # combineCommon.SanitizeDatasetNameFromInputList(
            #     dataset_fromInputList.replace("_tree", "")
            # )
            matchingPiece
        )
        print "found", xsection_val, "pb"
        sys.stdout.flush()

        # example
        # print 'inputDataFile='+inputDataFile
        # print '\tdata[0]=',data[0]
        # print 'Ntot=',Ntot

        # ---Read .dat table for current dataset
        data = combineCommon.ParseDatFile(inputDatFile)

        # ---Calculate weight
        sumWeights = 0
        lhePdfWeightSumw = 0
        for hist in sampleHistos:
            if "SumOfWeights" in hist.GetName():
                sumWeights = hist.GetBinContent(1)
            elif "LHEPdfSumw" in hist.GetName():
                lhePdfWeightSumw = hist.GetBinContent(1)  # sum[genWeight*pdfWeight_0]
        Ntot = float(data[0]["Npass"])
        doPDFReweight = False
        # FIXME
        # if "2016" in inputRootFile:
        #     if "LQToBEle" in inputRootFile or "LQToDEle" in inputRootFile:
        #         doPDFReweight = doPDFReweight2016LQSignals
        weight, plotWeight, xsection_X_intLumi = CalculateWeight(
            Ntot, xsection_val, options.intLumi, sumWeights, lhePdfWeightSumw, doPDFReweight
        )
        # print "xsection: " + xsection_val,
        print "\tweight(x1000): " + str(weight) + " = " + str(xsection_X_intLumi), "/",
        sys.stdout.flush()
        print str(sumWeights)
        sys.stdout.flush()

        # ---Update table
        # data = combineCommon.FillTableErrors(data, rootFile)
        data = combineCommon.FillTableEfficiencies(data, rootFile, weight)
        # newTable = combineCommon.CreateWeightedTable(data, weight, xsection_X_intLumi)
        # tableDictThisSample = combineCommon.UpdateTable(data, tableDictThisSample)
        tablesThisSample.append(data)
        # FIXME TODO tables
        # newTable = combineCommon.CreateWeightedTable(data, weight, xsection_X_intLumi)
        # # add this dataset's tables to the sample's table
        # combineCommon.UpdateTable(newTable, dictFinalTables[sample])

        # XXX TEST
        # print "sampleHistos[0]=", sampleHistos[0]
        # first2pairs = {k: dictFinalHisto[sample][k] for k in dictFinalHisto[sample].keys()[:2]}
        # print "before: dictFinalHisto[sample][:2]=", first2pairs
        if not options.tablesOnly:
            # dictFinalHisto[sample] = combineCommon.UpdateHistoDict(dictFinalHisto[sample], sampleHistos, sample, plotWeight)
            histoDictThisSample = combineCommon.UpdateHistoDict(histoDictThisSample, sampleHistos, sample, plotWeight)
        # XXX TEST
        # first2pairs = {k: dictFinalHisto[sample][k] for k in dictFinalHisto[sample].keys()[:2]}
        # print "after dictFinalHisto[sample][:2]=", first2pairs
        dictSamplesPiecesAdded[sample].append(matchingPiece)

    # done with this sample
    # validation of combining pieces
    piecesAdded = dictSamplesPiecesAdded[sample]
    # if set(piecesAdded) != set(pieceList):
    if set(piecesAdded) != set(piecesToAdd):
        # print
        # print 'set(piecesAdded)=',set(piecesAdded),'set(pieceList)=',set(pieceList)
        # print 'are they equal?',
        print
        # print 'ERROR: for sample',sample,'the pieces added were:'
        # print sorted(piecesAdded)
        print "ERROR: for sample", sample + ", the following pieces requested in sampleListForMerging were not added:"
        # print list(set(piecesAdded).symmetric_difference(set(pieceList)))
        print list(set(piecesAdded).symmetric_difference(set(piecesToAdd)))
        print "\twhile the pieces indicated as part of the sample were:"
        # print sorted(pieceList)
        print sorted(piecesToAdd)
        print "\tand the pieces added were:"
        print sorted(piecesAdded)
        print "\tRefusing to proceed."
        exit(-1)

    # ---Create final tables
    combinedTableThisSample = combineCommon.CombineEfficiencies(tablesThisSample)
    # --- Write tables
    combineCommon.WriteTable(combinedTableThisSample, sample, outputTableFile)

    # write histos
    if not options.tablesOnly:
        # combineCommon.WriteHistos(outputTfile, dictFinalHisto[sample])
        combineCommon.WriteHistos(outputTfile, histoDictThisSample, True)
        # if this is a ttbar/singlephoton/allbkg sample, we do need the hists later
        if (
            "tt" in sample.lower()
            or "singlephoton" in sample.lower()
            or "allbkg" in sample.lower()
        ):
            dictFinalHisto[sample] = histoDictThisSample
            dictFinalTables[sample] = combinedTableThisSample
        # print "Done"


if options.ttbarBkg:
    # special actions for TTBarFromData
    # subtract nonTTbarBkgMC from TTbarRaw
    # FIXME: we hardcode the sample names for now
    ttbarDataRawSampleName = "TTBarUnscaledRawFromDATA"
    ttbarDataPredictionTable = dictFinalTables[ttbarDataRawSampleName]
    # nonTTbarAMCBkgSampleName = 'NONTTBARBKG_amcatnloPt_emujj'
    # move to amcAtNLO diboson
    nonTTbarAMCBkgSampleName = "NONTTBARBKG_amcatnloPt_amcAtNLODiboson_emujj"
    nonTTbarAMCBkgTable = dictFinalTables[nonTTbarAMCBkgSampleName]
    ttBarPredName = "TTBarFromDATA"
    # Mar17 fixing muon pt and eta-->2.4
    Rfactor = 0.418559  # Ree,emu = Nee/Nemu[TTbarMC]
    errRfactor = 0.002474
    print "TTBar data-driven: Using Rfactor =", Rfactor, "+/-", errRfactor
    print "TTBar data-driven: Using non-ttbar background sample:", nonTTbarAMCBkgSampleName
    # print '0) WHAT DOES THE RAW DATA TABLE LOOK LIKE?'
    # WriteTable(ttbarDataPredictionTable, ttbarDataRawSampleName, outputTableFile)
    # remove the x1000 from the nonTTbarBkgMC
    combineCommon.ScaleTable(nonTTbarAMCBkgTable, 1.0 / 1000.0, 0.0)
    # print '1) WHAT DOES THE SCALED MC TABLE LOOK LIKE?'
    # WriteTable(nonTTbarMCBkgTable, nonTTbarMCBkgSampleName, outputTableFile)
    # subtract the nonTTBarBkgMC from the ttbarRawData, NOT zeroing entries where we run out of data
    combineCommon.SubtractTables(nonTTbarAMCBkgTable, ttbarDataPredictionTable)
    # print '2) WHAT DOES THE SUBTRACTEDTABLE LOOK LIKE?'
    # WriteTable(ttbarDataPredictionTable, ttBarPredName, outputTableFile)
    # scale by Ree,emu
    combineCommon.ScaleTable(ttbarDataPredictionTable, Rfactor, errRfactor)
    # print '3) WHAT DOES THE RfactroCorrectedTABLE LOOK LIKE?'
    # WriteTable(ttbarDataPredictionTable, ttBarPredName, outputTableFile)
    combineCommon.SquareTableErrorsForEfficiencyCalc(ttbarDataPredictionTable)
    combineCommon.CalculateEfficiency(ttbarDataPredictionTable)
    # print '4) WHAT DOES THE SCALEDTABLE AFTER EFF CALCULATION LOOK LIKE?'
    combineCommon.WriteTable(ttbarDataPredictionTable, ttBarPredName, outputTableFile)

if options.qcdClosure:
    # special actions for the QCD closure test
    # subtract nonQCD from QCDData yield
    qcdDataSampleName = "SinglePhoton_all"
    qcdDataTable = dictFinalTables[qcdDataSampleName]
    nonQCDBkgSampleName = "ALLBKG_powhegTTBar_ZJetWJetPt_amcAtNLODiboson"  # Z, W, TTBar, SingleTop, Diboson, gamma+jets
    nonQCDBkgTable = dictFinalTables[nonQCDBkgSampleName]
    qcdClosureSampleName = "QCDClosureObserved"
    # print "TTBar data-driven: Using non-ttbar background sample:", nonTTbarAMCBkgSampleName
    # print '0) WHAT DOES THE RAW DATA TABLE LOOK LIKE?'
    # WriteTable(ttbarDataPredictionTable, ttbarDataRawSampleName, outputTableFile)
    # remove the x1000 from the nonQCDBkgMC
    combineCommon.ScaleTable(nonQCDBkgTable, 1.0 / 1000.0, 0.0)
    # print '1) WHAT DOES THE SCALED MC TABLE LOOK LIKE?'
    # WriteTable(nonTTbarMCBkgTable, nonTTbarMCBkgSampleName, outputTableFile)
    # subtract the nonTTBarBkgMC from the ttbarRawData, NOT zeroing entries where we run out of data
    combineCommon.SubtractTables(nonQCDBkgTable, qcdDataTable)
    # print '2) WHAT DOES THE SUBTRACTEDTABLE LOOK LIKE?'
    # WriteTable(ttbarDataPredictionTable, ttBarPredName, outputTableFile)
    combineCommon.SquareTableErrorsForEfficiencyCalc(qcdDataTable)
    combineCommon.CalculateEfficiency(qcdDataTable)
    # print '4) WHAT DOES THE SCALEDTABLE AFTER EFF CALCULATION LOOK LIKE?'
    combineCommon.WriteTable(qcdDataTable, qcdClosureSampleName, outputTableFile)

outputTableFile.close()


if not options.tablesOnly:
    if options.ttbarBkg:
        # special actions for TTBarFromData
        # subtract nonTTbarBkgMC from TTbarRaw
        ttbarDataPredictionHistos = dictFinalHisto[ttbarDataRawSampleName]
        # print 'ttbarDataPredictionHistos:',ttbarDataPredictionHistos
        for n, histo in ttbarDataPredictionHistos.iteritems():
            # subtract the nonTTBarBkgMC from the ttbarRawData
            # find nonTTbarMCBkg histo; I assume they are in the same order here
            histoToSub = dictFinalHisto[nonTTbarAMCBkgSampleName][n]
            ## also write histos that are subtracted
            # histToSub.Write()
            # print 'n=',n,'histo=',histo
            outputTfile.cd()
            histoTTbarPred = histo.Clone()
            histoTTbarPred.Add(histoToSub, -1)
            # scale by Rfactor
            histoTTbarPred.Scale(Rfactor)
            histoTTbarPred.SetName(
                re.sub(
                    "__.*?__",
                    "__" + ttBarPredName + "__",
                    histoTTbarPred.GetName(),
                    flags=re.DOTALL,
                )
            )
            histoTTbarPred.Write()

    if options.qcdClosure:
        # special actions for QCDClosure observed
        # subtract nonQCDBkgMC from data
        qcdClosureHistos = dictFinalHisto[qcdDataSampleName]
        # print 'qcdClosureHistos:',qcdClosureHistos
        for n, histo in qcdClosureHistos.iteritems():
            # find nonTTbarMCBkg histo; assume they are in the same order here
            histoToSub = dictFinalHisto[nonQCDBkgSampleName][n]
            ## also write histos that are subtracted
            # histToSub.Write()
            # print 'n=',n,'histo=',histo
            histoQCDClosure = histo.Clone()
            histoQCDClosure.Add(histoToSub, -1)
            histoQCDClosure.SetName(
                re.sub(
                    "__.*?__",
                    "__" + qcdClosureSampleName + "__",
                    histoQCDClosure.GetName(),
                    flags=re.DOTALL,
                )
            )
            histoQCDClosure.Write()

    outputTfile.Close()
    print "output plots at: " + options.outputDir + "/" + options.analysisCode + "_plots.root"

print "output tables at: ", options.outputDir + "/" + options.analysisCode + "_tables.dat"

# ---TODO: CREATE LATEX TABLE (PYTEX?) ---#

# for profiling
if doProfiling:
    prof.disable()  # don't profile the generation of stats
    prof.dump_stats("mystats.stats")
    print "profiling: dump stats to mystats_output.txt"
    with open("mystats_output.txt", "wt") as output:
        stats = Stats("mystats.stats", stream=output)
        stats.sort_stats("cumulative", "time")
        stats.print_stats()
