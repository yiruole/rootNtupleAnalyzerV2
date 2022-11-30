#!/usr/bin/env python3

# ---Import
import sys
import string
from optparse import OptionParser
import os
from ROOT import TFile, gROOT
import re
import multiprocessing
import traceback
import subprocess
import time

import combineCommon


def CalculateWeight(Ntot, xsection_val, intLumi, sumWeights, dataset_fromInputList, lhePdfWeightSumw=0.0, pdfReweight=False):
    if xsection_val == "-1":
        weight = 1.0
        plotWeight = 1.0
        xsection_X_intLumi = Ntot
        sumWeights = -1
        print("\t[data]", end=' ')
        sys.stdout.flush()
    else:
        xsection_X_intLumi = float(xsection_val) * float(intLumi)
        print("\t[MC]", end=' ')
        sys.stdout.flush()

        # removed 2018 March 2
        # XXX: This is incorrect anyway.
        # if re.search('TT_',dataset_fromInputList):
        #  avgTopPtWeight = sumTopPtWeights / Ntot
        #  print '\tapplying extra TopPt weight of',avgTopPtWeight,'to',dataset_fromInputList
        #  xsection_X_intLumi/=avgTopPtWeight

        if pdfReweight:
            print("\tapplying LHEPdfWeight={} to dataset={}".format(lhePdfWeightSumw, dataset_fromInputList)+"[instead of original sumWeights={}]".format(sumWeights))
            sumWeights = lhePdfWeightSumw

        # now calculate the actual weight
        # weight = 1.0
        # if Ntot == 0:
        #     weight = float(0)
        # else:
        #     print "\tapplying sumWeights=", sumWeights, "to", dataset_fromInputList
        #     weight = xsection_X_intLumi / sumWeights
        print("\tapplying sumWeights=", sumWeights, "to", dataset_fromInputList)
        weight = xsection_X_intLumi / sumWeights
        plotWeight = weight / 1000.0
    return weight, plotWeight, xsection_X_intLumi


def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)
    sys.stdout.write("\r"+logString.format(jobCount, sampleCount))
    sys.stdout.write("\t"+str(len(result_list))+" jobs done")
    sys.stdout.flush()


def MakeCombinedSample(args):
    try:
        sample, pieceList, dictSamples, dictDatasetsFileNames, corrLHESysts, tfileNameTemplate, samplesToSave, dictFinalHisto, dictFinalTables = args
        outputTfile = TFile(tfileNameTemplate.format(sample), "RECREATE", "", 207)
        histoDictThisSample = {}
        tablesThisSample = []
        sampleTable = {}
        piecesAdded = []

        combineCommon.ParseXSectionFile(options.xsection)
        piecesToAdd = combineCommon.ExpandPieces(pieceList, dictSamples)

        # ---Loop over datasets in the inputlist
        # TODO: rewrite to be more efficient (loop over piecesToAdd instead)
        for dataset_fromInputList, rootFilename in dictDatasetsFileNames.items():
            if len(piecesAdded) == len(piecesToAdd):
                break  # we're done!
            toBeUpdated = False
            matchingPiece = combineCommon.SanitizeDatasetNameFromInputList(
                dataset_fromInputList.replace("_tree", "")
            )
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
            print("\tfound matching dataset:", matchingPiece + " ... ", end=' ')
            sys.stdout.flush()

            inputDatFile = rootFilename.replace(".root", ".dat")
            sampleHistos = []
            print("with file: {}".format(rootFilename))
            sys.stdout.flush()
            combineCommon.GetSampleHistosFromTFile(rootFilename, sampleHistos)

            print("\tlooking up xsection...", end=' ')
            sys.stdout.flush()
            xsection_val = combineCommon.lookupXSection(
                matchingPiece
            )
            print("found", xsection_val, "pb")
            sys.stdout.flush()
            isData = False
            if float(xsection_val) < 0:
                isData = True

            # print "inputDatFile="+inputDatFile

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
                Ntot, xsection_val, options.intLumi, sumWeights, dataset_fromInputList, lhePdfWeightSumw, doPDFReweight
            )
            # print "xsection: " + xsection_val,
            print("\tweight(x1000): " + str(weight) + " = " + str(xsection_X_intLumi), "/", end=' ')
            sys.stdout.flush()
            print(str(sumWeights))
            sys.stdout.flush()

            # ---Update table
            data = combineCommon.FillTableErrors(data, rootFilename)
            data = combineCommon.CreateWeightedTable(data, weight, xsection_X_intLumi)
            sampleTable = combineCommon.UpdateTable(data, sampleTable)
            tablesThisSample.append(data)

            if not options.tablesOnly:
                histoDictThisSample = combineCommon.UpdateHistoDict(histoDictThisSample, sampleHistos, matchingPiece, sample, plotWeight, corrLHESysts, isData)
            piecesAdded.append(matchingPiece)

        # validation of combining pieces
        # if set(piecesAdded) != set(pieceList):
        if set(piecesAdded) != set(piecesToAdd):
            # print
            # print 'set(piecesAdded)=',set(piecesAdded),'set(pieceList)=',set(pieceList)
            # print 'are they equal?',
            print()
            # print 'ERROR: for sample',sample,'the pieces added were:'
            # print sorted(piecesAdded)
            print("ERROR: for sample", sample + ", the following pieces requested in sampleListForMerging were not added:")
            # print list(set(piecesAdded).symmetric_difference(set(pieceList)))
            print(list(set(piecesAdded).symmetric_difference(set(piecesToAdd))))
            print("\twhile the pieces indicated as part of the sample were:")
            # print sorted(pieceList)
            print(sorted(piecesToAdd))
            print("\tand the pieces added were:")
            print(sorted(piecesAdded))
            print("\tRefusing to proceed.")
            raise RuntimeError("sample validation failed")

        # ---Create final tables
        combinedTableThisSample = combineCommon.CalculateEfficiency(sampleTable)
        # for writing tables later
        dictFinalTables[sample] = combinedTableThisSample

        # write histos
        if not options.tablesOnly:
            combineCommon.WriteHistos(outputTfile, histoDictThisSample, sample, corrLHESysts, True)
            if sample in samplesToSave:
                dictFinalHisto[sample] = histoDictThisSample
        outputTfile.Close()
    except Exception as e:
        print("ERROR: exception in MakeCombinedSample for sample={}".format(sample))
        traceback.print_exc()
        raise e
    return True


####################################################################################################
# RUN
####################################################################################################
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


(options, args) = parser.parse_args()

if len(sys.argv) < 14:
    raise RuntimeError(usage)

# print options.analysisCode

# ---Check if sampleListForMerging file exists
if os.path.isfile(options.sampleListForMerging) is False:
    raise RuntimeError("File " + options.sampleListForMerging + " not found")

# ---Check if xsection file exists
if os.path.isfile(options.xsection) is False:
    raise RuntimeError("File " + options.xsection + " not found")

print("Launched like:")
print("python ", end=' ')
for arg in sys.argv:
    print(" " + arg, end=' ')
print()

doPDFReweight2016LQSignals = False
if doPDFReweight2016LQSignals:
    print("Doing PDF reweighting for 2016 LQ B/D signal samples")

ncores = 8
pool = multiprocessing.Pool(ncores)
result_list = []
logString = "INFO: running {} parallel jobs for {} separate samples found in samplesToCombineFile..."
jobCount = 0
sampleCount = 0

if not os.path.exists(options.outputDir):
    os.makedirs(options.outputDir)

xsectionDict = combineCommon.ParseXSectionFile(options.xsection)
# print 'Dataset      XSec'
# for key,value in xsectionDict.iteritems():
#  print key,'  ',value

dictSamples = combineCommon.GetSamplesToCombineDict(options.sampleListForMerging)
dictSamplesPiecesAdded = {}
for key in dictSamples.keys():
    dictSamplesPiecesAdded[key] = []

manager = multiprocessing.Manager()
# --- Declare efficiency tables
dictFinalTables = manager.dict()
# --- Declare histograms
dictFinalHisto = manager.dict()
# --- Samples to save in final histo dict
samplesToSave = manager.list()
if not options.tablesOnly:
    if options.ttbarBkg:
        ttbarDataRawSampleName = "TTBarUnscaledRawFromDATA"
        nonTTbarAMCBkgSampleName = "NONTTBARBKG_amcatnloPt_amcAtNLODiboson_emujj"
        samplesToSave.extend([ttbarDataRawSampleName, nonTTbarAMCBkgSampleName])
    if options.qcdClosure:
        qcdDataSampleName = "SinglePhoton_all"
        nonQCDBkgSampleName = "ALLBKG_powhegTTBar_ZJetWJetPt_amcAtNLODiboson"  # Z, W, TTBar, SingleTop, Diboson, gamma+jets
        samplesToSave.extend([qcdDataSampleName, nonQCDBkgSampleName])

# check to make sure we have xsections for all samples
for lin in open(options.inputList):
    lin = lin.strip("\n")
    if lin.startswith("#"):
        continue
    dataset_fromInputList = lin.split("/")[-1].split(".")[0]
    dataset_fromInputList = dataset_fromInputList.replace("_tree", "")
    xsection_val = combineCommon.lookupXSection(
        combineCommon.SanitizeDatasetNameFromInputList(
            dataset_fromInputList.replace("_tree", "")
        )
    )

foundAllFiles, dictDatasetsFileNames = combineCommon.FindInputFiles(options.inputList, options.analysisCode, options.inputDir)
if not foundAllFiles:
    raise RuntimeError("Some files not found.")
else:
    print("\bDone.  All root/dat files are present.")
    print()

if not os.path.isdir(options.outputDir):
    os.makedirs(options.outputDir)

outputTableFile = open(
    options.outputDir + "/" + options.analysisCode + "_tables.dat", "w"
)
tfilePrefix = options.outputDir + "/" + options.analysisCode
sampleTFileNameTemplate = tfilePrefix+"_{}_plots.root"

# loop over samples defined in sampleListForMerging
for sample, sampleInfo in dictSamples.items():
    pieceList = sampleInfo["pieces"]
    corrLHESysts = sampleInfo["correlateLHESystematics"]
    #print("-->Look at sample named:", sample, "with piecelist=", pieceList)
    #sys.stdout.flush()
    #MakeCombinedSample([sample, pieceList, dictSamples, dictDatasetsFileNames, corrLHESysts, sampleTFileNameTemplate])
    # combine
    try:
        pool.apply_async(MakeCombinedSample, [[sample, pieceList, dictSamples, dictDatasetsFileNames, corrLHESysts, sampleTFileNameTemplate, samplesToSave, dictFinalHisto, dictFinalTables]], callback=log_result)
        jobCount += 1
        sampleCount += 1
    except KeyboardInterrupt:
        print("\n\nCtrl-C detected: Bailing.")
        pool.terminate()
        sys.exit(1)
    except Exception as e:
        print("ERROR: caught exception in job for sample: {}; exiting".format(sample))
        exit(-2)

# now close the pool and wait for jobs to finish
pool.close()
sys.stdout.write(logString.format(jobCount, sampleCount))
sys.stdout.write("\t"+str(len(result_list))+" jobs done")
sys.stdout.flush()
pool.join()
# check results?
if len(result_list) < jobCount:
    print("ERROR: {} jobs had errors. Exiting.".format(jobCount-len(result_list)))
    exit(-2)
print()
print("INFO: Done with individual samples")

if not options.tablesOnly:
    print("INFO: hadding individual samples using {} cores...".format(ncores), end=' ')
    outputTFileName = options.outputDir + "/" + options.analysisCode + "_plots.root"
    # hadd -fk207 -j4 outputFileComb.root [inputFiles]
    args = ["hadd", "-fk207", "-j "+str(ncores), outputTFileName]
    args.extend([sampleTFileNameTemplate.format(sample) for sample in dictSamples.keys()])
    #print("DEBUG: command={}".format(" ".join(args)))
    timeStarted = time.time()
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    timeDelta = time.time() - timeStarted
    if proc.returncode != 0:
        raise RuntimeError("ERROR: hadd command '{}' finished with error: '{}'; output looks like '{}'".format(" ".join(args), stderr, stdout))
    else:
        print("INFO: Finished hadd in "+str(round(timeDelta/60.0, 2))+" mins.")
    outputTfile = TFile.Open(outputTFileName)
    outputTfile.cd()
# TODO: remove individual sample files

# --- Write tables
for sample in dictSamples.keys():
   combineCommon.WriteTable(dictFinalTables[sample], sample, outputTableFile)

# now handle special backgrounds
if options.ttbarBkg:
    # special actions for TTBarFromData
    # subtract nonTTbarBkgMC from TTbarRaw
    # FIXME: we hardcode the sample names for now
    ttbarDataPredictionTable = dictFinalTables[ttbarDataRawSampleName]
    # nonTTbarAMCBkgSampleName = 'NONTTBARBKG_amcatnloPt_emujj'
    # move to amcAtNLO diboson
    nonTTbarAMCBkgTable = dictFinalTables[nonTTbarAMCBkgSampleName]
    ttBarPredName = "TTBarFromDATA"
    # Mar17 fixing muon pt and eta-->2.4
    Rfactor = 0.418559  # Ree,emu = Nee/Nemu[TTbarMC]
    errRfactor = 0.002474
    print("TTBar data-driven: Using Rfactor =", Rfactor, "+/-", errRfactor)
    print("TTBar data-driven: Using non-ttbar background sample:", nonTTbarAMCBkgSampleName)
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
    qcdDataTable = dictFinalTables[qcdDataSampleName]
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
        for n, histo in ttbarDataPredictionHistos.items():
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
        for n, histo in qcdClosureHistos.items():
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
    print("output plots at: " + options.outputDir + "/" + options.analysisCode + "_plots.root")

print("output tables at: ", options.outputDir + "/" + options.analysisCode + "_tables.dat")

# ---TODO: CREATE LATEX TABLE (PYTEX?) ---#

# for profiling
if doProfiling:
    prof.disable()  # don't profile the generation of stats
    prof.dump_stats("mystats.stats")
    print("profiling: dump stats to mystats_output.txt")
    with open("mystats_output.txt", "wt") as output:
        stats = Stats("mystats.stats", stream=output)
        stats.sort_stats("cumulative", "time")
        stats.print_stats()
