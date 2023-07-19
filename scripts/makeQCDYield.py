#!/usr/bin/env python3

import os
import sys
import glob
import math
import copy
from pathlib import Path
from optparse import OptionParser
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
        print("INFO: found {} hists for sample {}".format(len(sampleHistos), sample))
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
            doubleBinContent = limit*singleBinContent
            #FIXME ERROR? Probably still OK to take the double FR weights into the errors sums as usual.
        binError = math.sqrt(singleBinErrorSqr + doubleBinErrorSqr)
        singleFRHistoNew.SetBinContent(globalBin, singleBinContent - doubleBinContent)
        singleFRHistoNew.SetBinError(globalBin, binError)
    return singleFRHistoNew


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
singleFRDYJHistos = GetSampleHistosFromTFile(singleFRPlotsFile, zjetMCSampleName)
# Try to find the 2FR plots and tables
doubleFRPlotsFile = FindFile(options.doubleFakeRateEstimateDir, "*_plots.root")
doubleFRTablesFile = FindFile(options.doubleFakeRateEstimateDir, "*_tables.dat")
doubleFRQCDHistos = GetSampleHistosFromTFile(doubleFRPlotsFile, qcdSampleName)
#FIXME TODO TABLES AS WELL

# now we need to do 1FR - 2FR, where the subtraction is limited to 1FR/2
subbedHistos = DoHistoSubtraction(singleFRQCDHistos, doubleFRQCDHistos, singleFRDYJHistos)

tfilePath = options.outputDir+"/"+options.fileName
print("INFO: Writing subtracted plots to {}...".format(tfilePath))
tfile = TFile.Open(tfilePath, "recreate", "", 207)
tfile.cd()
for histo in subbedHistos:
    histo.Write()
tfile.Close()
print("Done.")
