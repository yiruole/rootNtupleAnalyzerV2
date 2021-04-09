#!/usr/bin/env python2

import os
import sys
import math
import string
from prettytable import PrettyTable
import numpy as np
import ROOT as r
import combineCommon as cc


def GetFullSignalName(signal_name, mass_point):
    verbose = False
    fullSignalName = signal_name.replace("[masspoint]", mass_point)
    if verbose:
        print "GetFullSignalName(): signal_name=", signal_name, "fullSignalName=", fullSignalName
    if "BetaHalf" in signal_name:
        signalNameForFile = "LQToUE_ENuJJFilter_M-" + mass_point + "_BetaHalf"
    elif "LQ" in signal_name:
        signalNameForFile = signalNameTemplate.format(mass_point)
        fullSignalName = "LQ_M"+str(mass_point)  # RunStatsBasicCLS requires this signal name
    elif "Stop" in signal_name:
        ctau = signal_name[signal_name.find("CTau") + 4:]
        # print 'found ctau=',ctau,'in signal_name:',signal_name,'mass point:',mass_point
        signalNameForFile = "DisplacedSUSY_StopToBL_M-" + mass_point + "_CTau-" + ctau
    return fullSignalName, signalNameForFile


def GetStatErrors(nevts, theta=1.0, nScaledEvents=-1):
    verbose = True
    # nevts = int(nevts)
    if nScaledEvents == -1:
        # this is the case for data, as there's no scaling
        nScaledEvents = nevts
    alpha = 1.0 - 0.6827
    # print 'calculate errors on nevts=',nevts
    if nevts < 0:
        print "ERROR: nevts < 0:", nevts
        return -999, -999
    if theta < 0:
        print "ERROR: theta < 0:", theta
        return -999, -999
    # if nevts=0, lower error is zero
    # if scaled events is zero, lower error is also zero. For amc@NLO with negative weights, or ttbar data driven (subtracting MC),
    #   it can be the case that nevts>0 but nScaledEvents<=0 (set to zero previously)
    lower = (
        0
        if nevts == 0 or nScaledEvents == 0
        else r.Math.gamma_quantile(alpha / 2.0, nevts, theta)
    )
    u = r.Math.gamma_quantile_c(alpha / 2.0, nevts + 1, theta)
    if verbose:
        print "calculate upper gamma quantile={} for nevts={} theta={}; scaledEvents={}; upper error={}".format(
                u, nevts, theta, nScaledEvents, u - nScaledEvents)
    # return u-nevts,nevts-l
    return u - nScaledEvents, nScaledEvents - lower


def GetStatErrorFromDict(statErrDict, mass):
    availMasses = sorted(statErrDict.keys())
    if mass not in availMasses and mass > availMasses[-1]:
        mass = availMasses[-1]
    return statErrDict[mass]


def GetSystematicsDict(rootFile, sampleName, selections, verbose=False):
    systHistName = "histo2D__{}__systematics".format(sampleName)
    systHist = rootFile.Get(systHistName)
    systDict = {}
    for selection in selections:
        # expect that selections are either "preselection" or "LQXXXX"
        finalSelection = cc.GetFinalSelection(selection, doEEJJ)
        systDict[selection] = {}
        xBin = systHist.GetXaxis().FindFixBin(finalSelection)
        if xBin < 1:
            raise RuntimeError("Could not find requested selection name '{}' in hist {} in file {}".format(finalSelection, systHistName, rootFile.GetName()))
        for yBin in range(1, systHist.GetNbinsY()+1):
            systName = systHist.GetYaxis().GetBinLabel(yBin)
            systDict[selection][systName] = systHist.GetBinContent(xBin, yBin)
    if verbose:
        print "sampleName={}: systDict={}".format(sampleName, systDict["LQ300"])
    # reindex by syst name
    systDict = {syst: {sel: systDict[sel][syst] for sel in systDict} for syst in systDict[selections[0]].keys()}
    # if verbose:
    #     print "sampleName={}: systDict=".format(sampleName)
    #     for systName, selYieldDicts in systDict.items():
    #         print "{} : {}".format(systName, selYieldDicts["LQ300"]),
    #     print
    return systDict


def GetSignalSystDeltaOverNominal(signalName, selectionName, verbose=False):
    return GetTotalSystDeltaOverNominal(signalName, selectionName, systematicsNamesSignal, d_signal_systs, verbose)


def GetBackgroundSystDeltaOverNominal(background_name, selectionName, verbose=False):
    return GetTotalSystDeltaOverNominal(background_name, selectionName, systematicsNamesBackground, d_background_systs, verbose)


def GetTotalSystDeltaOverNominal(sampleName, selectionName, systematicsNames, d_systs, verbose=False):
    totalSyst = 0
    for syst in systematicsNames:
        systEntry, deltaOverNominalUp, deltaOverNominalDown = GetSystematicEffect(syst, sampleName, selectionName, d_systs)
        deltaOverNominalMax = max(deltaOverNominalUp, deltaOverNominalDown)
        if deltaOverNominalMax > 0:
            totalSyst += deltaOverNominalMax * deltaOverNominalMax
        elif deltaOverNominalMax > 1:
            raise RuntimeError(
                    "deltaOverNominalMax > 1 for sampleName={} syst={} selection={} deltaOverNominalUp={} deltaOverNominalDown={}".format(
                        sampleName, syst, selectionName, deltaOverNominalUp, deltaOverNominalDown))
        # if verbose:
        #     print "GetSystematicEffect({}, {}, {}, {})".format(syst, sampleName, selectionName, d_systs.keys())
        #     print "\t result={}".format(GetSystematicEffect(syst, sampleName, selectionName, d_systs))
        #     print "\t totalSyst={}".format(totalSyst)
    if verbose:
        print "GetTotalSystDeltaOverNominal(): {} -- return sqrt(totalSyst) = sqrt({}) = {}".format(
                sampleName, totalSyst, math.sqrt(totalSyst))
    return math.sqrt(totalSyst)


def DoesSystematicApply(systName, sampleName):
    return systName in d_applicableSystematics[sampleName]


def GetSystematicEffect(systName, sampleName, selection, fullSystDict):
    if not DoesSystematicApply(systName, sampleName):
        return "-", -1, -1
    # systematicsNamesBackground = [
    #    "LHEPDFWeight",
    #    "Lumi",
    #    "EleTrigSF","Pileup",  "JER", "JES", "EleRecoSF", "EleHEEPSF", "EES",
    #    "EER",
    #    "TT_Norm", "DY_Norm",
    #    "DY_Shape", "TT_Shape", "Diboson_Shape",
    #    "QCD_Norm",
    systDict = fullSystDict[sampleName]
    hasUpDownVariation = True
    isFlat = False
    if "shape" in systName.lower():
        return "-", -1, -1  # FIXME TODO special handling
    elif systName == "LHEPDFWeight":
        return "-", -1, -1  # FIXME TODO special handling for PDF systematic
    elif systName == "Lumi":
        return "-", -1, -1  # FIXME TODO special handling
    elif "norm" in systName.lower():
        if "tt" in systName.lower() or "dy" in systName.lower():
            return "-", -1, -1  # FIXME TODO special handling for TT_Norm, DY_Norm
        if "qcd" in systName.lower():
            isFlat = True
    elif "eer" in systName.lower():
        hasUpDownVariation = False
    # now extract the systematic number
    if isFlat:
        # assumes that the number here is < 1
        return str(1 + systDict[systName][selection]), systDict[systName][selection], systDict[systName][selection]
    # if we get here, we should have Up/Down variations for this syst
    try:
        nominal = systDict["nominal"][selection]
    except KeyError:
        raise RuntimeError("Could not find nominal key for systName={} sampleName={} selection={}; keys={}".format(
            systName, sampleName, selection, systDict.keys())
            )
    if nominal == 0:
        # FIXME TODO: how to handle this case?
        # for now return invalid value
        return "-", -1, -1
    if hasUpDownVariation:
        try:
            systYieldUp = systDict[systName+"Up"][selection]
            systYieldDown = systDict[systName+"Down"][selection]
        except KeyError:
            raise RuntimeError("Could not find Up or Down key for syst={}; keys={}".format(systName, systDict.keys()))
        kUp = systYieldUp/nominal
        kDown = systYieldDown/nominal
        # if kUp >= 1:
        #     kUp -= 1
        # if kDown >= 1:
        #     kDown -= 1
        # if kUp == 0:
        #     return str(0), 0, kDown
        # return str(kDown/kUp), kUp, kDown
        upDelta = systYieldUp-nominal
        if upDelta >= 1:
            upDelta -= 1
        downDelta = nominal-systYieldDown
        if downDelta >= 1:
            downDelta -= 1
        return str(kDown/kUp), upDelta/nominal, downDelta/nominal
    else:
        systYield = systDict[systName][selection]
        delta = systYield-nominal
        if delta >= 1:
            delta -= 1
        return str(1 + delta/nominal), delta/nominal, delta/nominal


def RoundToN(x, n):
    # if n < 1:
    #    raise ValueError("can't round to less than 1 sig digit!")
    # # number of digits given by n
    # return "%.*e" % (n-1, x)
    if isinstance(x, float):
        return round(x, n)
    else:
        return x


def GetTableEntryStr(evts, errStatUp="-", errStatDown="-", errSyst=0, latex=False):
    if evts == "-":
        return evts
    # rounding
    evtsR = RoundToN(evts, 2)
    errStatUpR = RoundToN(errStatUp, 2)
    errStatDownR = RoundToN(errStatDown, 2)
    # add additional decimal place if it's zero after rounding
    if evtsR == 0.0:
        evtsR = RoundToN(evts, 3)
    if errStatUpR == 0.0:
        errStatUpR = RoundToN(errStatUp, 3)
    if errStatDownR == 0.0:
        errStatDownR = RoundToN(errStatDown, 3)
    # try again
    if evtsR == 0.0:
        evtsR = RoundToN(evts, 4)
    if errStatUpR == 0.0:
        errStatUpR = RoundToN(errStatUp, 4)
    if errStatDownR == 0.0:
        errStatDownR = RoundToN(errStatDown, 4)
    # handle cases where we don't specify stat or syst
    if errStatUp == "-":
        return str(evtsR)
    elif errSyst == 0:
        if errStatUp == errStatDown:
            if not latex:
                return str(evtsR) + " +/- " + str(errStatUpR)
            else:
                return str(evtsR) + " \\pm " + str(errStatUpR)
        else:
            if not latex:
                return str(evtsR) + " + " + str(errStatUpR) + " - " + str(errStatDownR)
            else:
                return (
                    str(evtsR)
                    + "^{+"
                    + str(errStatUpR)
                    + "}_{-"
                    + str(errStatDownR)
                    + "}"
                )
    else:
        errSystR = RoundToN(errSyst, 2)
        if errStatUp == errStatDown:
            if not latex:
                return str(evtsR) + " +/- " + str(errStatUpR) + " +/- " + str(errSystR)
            else:
                return (
                    str(evtsR) + " \\pm " + str(errStatUpR) + " \\pm " + str(errSystR)
                )
        else:
            return (
                str(evtsR)
                + "^{+"
                + str(errStatUpR)
                + "}_{-"
                + str(errStatDownR)
                + "} \\pm "
                + str(errSystR)
            )


# def CalculateScaledRateError(
#     sampleNameFromDataset,
#     N_unscaled_tot,
#     N_unscaled_pass_entries,
#     N_unscaled_pass_integral,
#     doScaling=True,
# ):
#     # print 'CalculateScaledRateError(', sampleNameFromDataset, N_unscaled_tot, N_unscaled_pass_entries, N_unscaled_pass_integral, ')'
#     # sys.stdout.flush()
#     # binomial error
#     p = N_unscaled_pass_entries / N_unscaled_tot
#     q = 1 - p
#     w = (
#         N_unscaled_pass_integral / N_unscaled_pass_entries
#         if N_unscaled_pass_entries != 0
#         else 0.0
#     )
#     unscaledRateError = N_unscaled_tot * w * math.sqrt(p * q / N_unscaled_tot)
#     if doScaling:
#         xsecTimesIntLumi = GetXSecTimesIntLumi(sampleNameFromDataset)
#         scaledRateError = unscaledRateError * (xsecTimesIntLumi / N_unscaled_tot)
#     else:
#         scaledRateError = unscaledRateError
#     return scaledRateError


def FillDicts(rootFilename, sampleNames, bkgType):
    isData = False if "mc" in bkgType.lower() or "signal" in bkgType.lower() else True
    scaledRootFile = r.TFile.Open(rootFilename)
    if not scaledRootFile or scaledRootFile.IsZombie():
        raise RuntimeError("Could not open root file: {}".format(scaledRootFile.GetName()))
    d_rates = {}
    d_rateErrs = {}
    d_unscaledRates = {}
    d_totalEvents = {}
    d_systematics = {}
    selectionPoints = ["preselection"] + mass_points
    selectionNames = ["LQ"+sel if "preselection" not in sel else sel for sel in selectionPoints]
    # start sample
    for i_sample, sampleName in enumerate(sampleNames):
        unscaledTotalEvts = cc.GetUnscaledTotalEvents(scaledRootFile, sampleName)
        if unscaledTotalEvts < 0:
            print "WARN: for sample {}, found negative sampleUnscaledTotalEvents: {}; set to zero.".format(sampleName, unscaledTotalEvts)
            unscaledTotalEvts = 0.0
        ratesDict = {}
        rateErrsDict = {}
        unscaledRatesDict = {}
        # do all selections
        for i_signal_name, signal_name in enumerate(signal_names):
            for i_mass_point, mass_point in enumerate(selectionPoints):
                selectionName = selectionNames[i_mass_point]
                # print '------>Call GetRatesAndErrors for sampleName=',bkgSample
                sampleRate, sampleRateErr, sampleUnscaledRate = cc.GetRatesAndErrors(
                    scaledRootFile,
                    sampleName,
                    selectionName,
                    doEEJJ,
                    isData,
                    bkgType == "TTData"
                )
                # print '------>rate=',rate,'rateErr=',rateErr,'unscaledRate=',unscaledRate
                # if isQCD:
                #  print 'for sample:',bkgSample,'got unscaled entries=',unscaledRate
                # print 'sampleName={}, sampleRate:',sampleRate,'sampleRateErr=',sampleRateErr,'sampleUnscaledRate=',sampleUnscaledRate
                if selectionName == "preselection":
                    print "INFO: for sampleName={}, PRESELECTION ------>rate={} rateErr={} unscaledRate={} unscaledTotalEvts={}".format(sampleName, sampleRate, sampleRateErr, sampleUnscaledRate, unscaledTotalEvts)
                elif selectionName == "LQ300" and "300" in sampleName:
                    print "INFO: for sampleName={}, LQ300 ------>rate={} rateErr={} unscaledRate={} unscaledTotalEvts={}".format(sampleName, sampleRate, sampleRateErr, sampleUnscaledRate, unscaledTotalEvts)
                ratesDict[selectionName] = sampleRate
                if ratesDict[selectionName] < 0:
                    print "WARN: for sample {}, selection {}: found negative rate: {}; set to zero.".format(sampleName, selectionName, sampleRate)
                    ratesDict[selectionName] = 0.0
                rateErrsDict[selectionName] = sampleRateErr
                unscaledRatesDict[selectionName] = sampleUnscaledRate
                if unscaledRatesDict[selectionName] < 0:
                    print "WARN: for sample {}, selection {}: found negative unscaled rate: {}; set to zero.".format(sampleName, selectionName, sampleUnscaledRate)
                    unscaledRatesDict[selectionName] = 0.0
        if not isData and doSystematics:
            d_systematics[sampleName] = GetSystematicsDict(scaledRootFile, sampleName, selectionNames)  # , sampleName == "LQToDEle_M-300_pair")
        elif sampleName == "QCDFakes_DATA":
            # special handling for QCDFakes_DATA
            d_selsAndSysts = {sel: qcdNormDeltaXOverX for sel in selectionNames}
            d_systematics[sampleName] = {"QCD_Norm": d_selsAndSysts}
        # fill full dicts
        d_rates[sampleName] = ratesDict
        d_rateErrs[sampleName] = rateErrsDict
        d_unscaledRates[sampleName] = unscaledRatesDict
        d_totalEvents[sampleName] = unscaledTotalEvts
    scaledRootFile.Close()
    return d_rates, d_rateErrs, d_unscaledRates, d_totalEvents, d_systematics


###################################################################################################
# CONFIGURABLES
###################################################################################################

blinded = True
doSystematics = True
doEEJJ = True
doRPV = False  # to do RPV, set doEEJJ and doRPV to True
forceGmNNormBkgStatUncert = False
#signalNameTemplate = "LQToUE_M-{}_BetaOne"
signalNameTemplate = "LQToDEle_M-{}_pair"
year = 2016

sampleListForMerging = "$LQANA/config/sampleListForMerging_13TeV_eejj_{}.txt"
#
sampleListsForMergingQCD = {}
sampleListsForMergingQCD[2016] = "$LQANA/config/sampleListForMerging_13TeV_QCD_dataDriven_2016.txt"
sampleListsForMergingQCD[2017] = "$LQANA/config/sampleListForMerging_13TeV_QCD_dataDriven_2017.txt"
sampleListsForMergingQCD[2018] = "$LQANA/config/sampleListForMerging_13TeV_QCD_dataDriven_2017.txt"
#
inputLists = {}
#inputLists[2016] = "$LQANA/config/oldInputLists/nanoV7/2016/nanoV7_2016_pskEEJJ_16oct2020_comb/inputListAllCurrent.txt"
#inputLists[2016] = "$LQANA/config/nanoV7_2016_pskEEJJ_9nov2020_comb/inputListAllCurrent.txt"
inputLists[2016] = "$LQANA/config/nanoV7_2016_pskEEJJ_16mar2021_comb/inputListAllCurrent.txt"
inputLists[2017] = "$LQANA/config/nanoV7_2017_pskEEJJ_20oct2020_comb/inputListAllCurrent.txt"
#
qcdFilePaths = {}
#qcdFilePaths[2016] = "$LQDATA/nanoV7/2016/analysis/qcdYield_eejj_20oct2020_optFinalSels/output_cutTable_lq_eejj_QCD/"
#qcdFilePaths[2016] = "$LQDATA/nanoV7/2016/analysis/qcdYield_eejj_2mar2021_oldOptFinalSels/output_cutTable_lq_eejj_QCD/"
qcdFilePaths[2016] = "$LQDATA/nanoV7/2016/analysis/qcdYield_eejj_23mar2021_oldOptFinalSels/output_cutTable_lq_eejj_QCD/"
qcdFilePaths[2017] = "$LQDATA/nanoV7/2017/analysis/qcdYield_eejj_23oct2020_optFinalSels/output_cutTable_lq_eejj_QCD/"
#
filePaths = {}
#filePaths[2016] = "$LQDATA/nanoV7/2016/analysis/eejj_20oct2020_optFinalSels/output_cutTable_lq_eejj/"
#filePaths[2016] = "$LQDATA/nanoV7/2016/analysis/eejj_9nov2020_optFinalSelsOld/output_cutTable_lq_eejj/"
filePaths[2016] = "$LQDATA/nanoV7/2016/analysis/precomputePrefire_looserPSK_eejj_16mar2021_oldOptFinalSels/output_cutTable_lq_eejj/"
filePaths[2017] = "$LQDATA/nanoV7/2017/analysis/prefire_eejj_23oct2020_optFinalSels/output_cutTable_lq_eejj/"
#
xsecFiles = {}
# xsecFiles[2016] = "$LQANA/versionsOfAnalysis/2016/nanoV7/eejj/aug26/unscaled/xsection_13TeV_2015_Mee_PAS_TTbar_Mee_PAS_DYJets.txt"
xsecFiles[2016] = "$LQANA/config/xsection_13TeV_2015.txt"
xsecFiles[2017] = "$LQANA/versionsOfAnalysis/2017/nanoV7/eejj/aug27/unscaled/xsection_13TeV_2015_Mee_PAS_TTbar_Mee_PAS_DYJets.txt"

if doEEJJ:
    sampleListForMerging = os.path.expandvars(sampleListForMerging.format(year))
    sampleListForMergingQCD = os.path.expandvars(sampleListsForMergingQCD[year])
    # SIC 6 Jul 2020 remove
    # sampleListForMergingTTBar = (
    #     os.environ["LQANA"] + "/config/sampleListForMerging_13TeV_ttbarBkg_emujj.txt"
    # )
    inputList = os.path.expandvars(inputLists[year])
    qcdFilePath = os.path.expandvars(qcdFilePaths[year])
    filePath = os.path.expandvars(filePaths[year])
    xsection = os.path.expandvars(xsecFiles[year])
    # ttbarFilePath = (
    #     os.environ["LQDATA"]
    #     + "/2016ttbar/mar17_emujj_fixMuons/output_cutTable_lq_ttbar_emujj_correctTrig/"
    # )
    # # calculated with fitForStatErrs.py script. mass, stat. uncert.
    # # statErrorsSingleTop = { 800: 1.10, 850: 0.85, 900: 0.67, 950: 0.53, 1000: 0.42, 1050: 0.33 }
    # # here we increased the fit range
    # statErrorsPhotonJets = {
    #     400: 0.23,
    #     450: 0.33,
    #     500: 0.36,
    #     550: 0.35,
    #     600: 0.32,
    #     650: 0.28,
    #     700: 0.24,
    #     750: 0.21,
    #     800: 0.17,
    #     850: 0.14,
    #     900: 0.12,
    #     950: 0.095,
    #     1000: 0.077,
    #     1050: 0.062,
    # }
else:
    sampleListForMerging = (
        os.environ["LQANA"] + "/config/sampleListForMerging_13TeV_enujj.txt"
    )
    sampleListForMergingQCD = (
        os.environ["LQANA"] + "/config/sampleListForMerging_13TeV_QCD_dataDriven.txt"
    )
    # inputList = os.environ["LQANA"]+'/config/PSKenujj_oct2_SEleL_reminiaod_v236_eoscms/inputListAllCurrent.txt'
    inputList = (
        os.environ["LQANA"]
        + "/config/PSKenujj_mar16_v237_local_comb/inputListAllCurrent.txt"
    )
    filePath = (
        os.environ["LQDATA"]
        + "/2016analysis/enujj_psk_mar16_fixMuons/output_cutTable_lq_enujj_MT/"
    )
    xsection = (
        os.environ["LQANA"]
        + "/versionsOfAnalysis_enujj/mar17/unscaled/newSingleTop/xsection_13TeV_2015_MTenu_50_110_gteOneBtaggedJet_TTbar_MTenu_50_110_noBtaggedJets_WJets.txt"
    )
    qcdFilePath = (
        os.environ["LQDATA"]
        + "/2016qcd/enujj_mar16_fixMuons/output_cutTable_lq_enujj_MT_QCD/"
    )
    # # calculated with fitForStatErrs.py script. mass, stat. uncert.
    # statErrorsSingleTop = { 650:0.213, 700:0.330, 750:0.399, 800:0.431, 850:0.442, 900:0.438, 950:0.425, 1000:0.407, 1050:0.385, 1100:0.363, 1150:0.342, 1200:0.321 }

# this has the TopPtReweight+updatedSF and the Z+jets St corrections at final selections
# filePath = os.environ["LQDATA"] + '/RunII/eejj_analysis_zJetsStCorrectionFinalSelections_21jul/output_cutTable_lq_eejj/'

dataMC_filepath = filePath + (
    "analysisClass_lq_eejj_plots.root"
    if doEEJJ
    else "analysisClass_lq_enujj_MT_plots.root"
)
qcd_data_filepath = qcdFilePath + (
    "analysisClass_lq_eejj_QCD_plots.root"
    if doEEJJ
    else "analysisClass_lq_enujj_QCD_plots.root"
)
if doEEJJ:
    # ttbar_data_filepath = ttbarFilePath + "analysisClass_lq_ttbarEst_plots.root"
    # SIC 6 Jul 2020 remove
    ttbar_data_filepath = ""
else:
    ttbar_data_filepath = ""
    # ttbarFilePath = filePath

if year == 2016:
    do2016 = True
    cc.intLumi = 35867.0
elif year == 2017:
    do2017 = True
    cc.intLumi = 41540.0
elif year == 2018:
    do2018 = True
    cc.intLumi = 59399.0
else:
    print "ERROR: could not find one of 2017/2017/2018 in inputfile path. cannot do year-specific customizations. quitting."
    exit(-1)
if doRPV:
    mass_points = [
        str(i) for i in range(200, 1250, 100)
    ]  # go from 200-1200 in 100 GeV steps
else:
    # LQ case
    mass_points = [
        str(i) for i in range(300, 3100, 100)
    ]  # go from 300-2000 in 100 GeV steps
    # mass_points.extend(["3500", "4000"])
    mass_points.remove("2500")  # FIXME 2016
    # mass_points.remove("3000")  # FIXME 2017

if doEEJJ:
    if doRPV:
        signal_names = [
            "Stop_M[masspoint]_CTau1000",
            "Stop_M[masspoint]_CTau100",
            "Stop_M[masspoint]_CTau10",
            "Stop_M[masspoint]_CTau1",
        ]
        # signal_names = [ "Stop_M[masspoint]_CTau10","Stop_M[masspoint]_CTau1"]
        # put in some more signals that don't fit the general pattern
        # signal_names = ['Stop_M100_CTau100','Stop_M125_CTau100','Stop_M150_CTau100','Stop_M175_CTau100','Stop_M200_CTau50'] + signal_names
    else:
        signal_names = [signalNameTemplate]
    maxLQSelectionMass = 1200  # max background selection point used
    systematicsNamesBackground = [
        "EleTrigSF",
        "Pileup",
        "LHEPDFWeight",
        "Lumi",
        "JER",
        "JES",
        "EleRecoSF",
        "EleHEEPSF",
        "EES",
        "EER",
        "TT_Norm",
        "DY_Norm",
        "DY_Shape",
        "TT_Shape",
        "Diboson_Shape",
        "QCD_Norm",
    ]
    # background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTBarFromDATA", "ZJet_amcatnlo_ptBinned", "WJet_amcatnlo_ptBinned", "DIBOSON","SingleTop"  ]
    background_names = [
        "ZJet_amcatnlo_ptBinned" if do2016 else "ZJet_jetAndPtBinned",
        "QCDFakes_DATA",
        # "TTBarFromDATA",
        "TTbar_powheg",
        # "WJet_amcatnlo_ptBinned",
        "WJet_amcatnlo_jetBinned",
        # "DIBOSON_amcatnlo",
        "DIBOSON_nlo",
        "TRIBOSON",
        "TTW",
        "TTZ",
        "SingleTop",
        "PhotonJets_Madgraph",
    ]
    background_fromMC_names = [bkg for bkg in background_names if "data" not in bkg.lower()]
    background_QCDfromData = [bkg for bkg in background_names if "data" in bkg.lower() and "qcd" in bkg.lower()]
    systematicsNamesSignal = [syst for syst in systematicsNamesBackground if "shape" not in syst.lower() and "norm" not in syst.lower()]
    d_systTitles = {
            "EleTrigSF": "Trigger",
            "Pileup": "Pileup",
            "LHEPDFWeight": "PDF",
            "Lumi": "Lumi",
            "JER": "Jet energy resolution",
            "JES": "Jet energy scale",
            "EleRecoSF": "Electron reconstruction",
            "EleHEEPSF": "Electron identification",
            "EES": "Electron energy scale",
            "EER": "Electron energy resolution",
            "TT_Norm": "TTbar normalization",
            "DY_Norm": "DYJ normalization",
            "DY_Shape": "DYJ shape",
            "TT_Shape": "TTbar shape",
            "Diboson_Shape" : "Diboson shape",
            "QCD_Norm": "QCD background normalization",
    }
else:
    signal_names = ["LQ_BetaHalf_M[masspoint]"]
    systematicsNamesBackground = [
        "Trigger",
        "Reco",
        "PU",
        "PDF",
        "Lumi",
        "JER",
        "JEC",
        "HEEP",
        "E_scale",
        "EER",
        "MET",
        "WShape",
        "W_Norm",
        "W_btag_Norm",
        "W_RMt_Norm",
        "TTShape",
        "TT_Norm",
        "TTbar_btag_Norm",
        "Diboson_shape",
    ]
    # background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTbar_amcatnlo_Inc", "ZJet_amcatnlo_ptBinned", "WJet_amcatnlo_ptBinned", "DIBOSON","SingleTop"  ]
    # background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTbar_powheg", "ZJet_amcatnlo_ptBinned", "WJet_amcatnlo_ptBinned", "DIBOSON","SingleTop"  ]
    background_names = [
        "PhotonJets_Madgraph",
        "QCDFakes_DATA",
        "TTbar_powheg",
        "ZJet_amcatnlo_ptBinned",
        "WJet_amcatnlo_ptBinned",
        "DIBOSON_amcatnlo",
        "SingleTop",
    ]
    syst_background_names = [
        "GJets",
        "QCDFakes_DATA",
        "TTbar",
        "DY",
        "WJets",
        "Diboson",
        "Singletop",
    ]
    maxLQSelectionMass = 900  # max background selection point used
    systematicsNamesSignal = [
        "Trigger",
        "Reco",
        "PU",
        "PDF",
        "Lumi",
        "JER",
        "JEC",
        "HEEP",
        "E_scale",
        "EER",
        "MET",
    ]

minLQselectionBkg = "LQ200"

# SIC 6 Jul 2020 remove
# if doEEJJ:
#     ttBarNormDeltaXOverX = 0.01
#     ttbarSampleName = "TTBarFromDATA"
#     ttBarUnscaledRawSampleName = "TTBarUnscaledRawFromDATA"
#     # nonTTBarSampleName='NONTTBARBKG_amcatnloPt_emujj'
#     nonTTBarSampleName = "NONTTBARBKG_amcatnloPt_amcAtNLODiboson_emujj"

# update to 2016 analysis numbers
# QCDNorm is 0.50 [50% norm uncertainty for eejj = uncertaintyPerElectron*2]
if doEEJJ:
    qcdNormDeltaXOverX = 0.50
else:
    qcdNormDeltaXOverX = 0.25

n_background = len(background_names)
# all bkg systematics, plus stat 'systs' for all bkg plus signal plus 3 backNormSysts
# update July/Sep 2020: no more data-driven TBar, so only 1 extra syst for eejj
if doSystematics:
    if doEEJJ:
        # n_systematics = len(systematicsNamesBackground) + n_background + 1 + 2
        n_systematics = len(systematicsNamesBackground) + n_background + 1 + 1
    else:
        n_systematics = (
            len(systematicsNamesBackground) + n_background + 1 + 1
        )  # QCD norm only
else:
    n_systematics = n_background + 1
n_channels = 1

signalNameList = [GetFullSignalName(signalNameTemplate, massPoint)[1] for massPoint in mass_points]
allBkgSysts = [syst for syst in systematicsNamesBackground if "norm" not in syst.lower() and "shape" not in syst.lower()]
d_applicableSystematics = {bkg: allBkgSysts for bkg in background_fromMC_names}
d_applicableSystematics.update({bkg: "QCD_Norm" for bkg in background_QCDfromData})
# FIXME TODO ADD shape/norm for DY/TTBar
d_applicableSystematics.update({sig: systematicsNamesSignal for sig in signalNameList})
datacard_filePath = "tmp_card_file.txt"
plots_filePath = "plots.root"
###################################################################################################
# RUN
###################################################################################################

# ---Check if sampleListForMerging file exist
if os.path.isfile(sampleListForMerging) is False:
    print "ERROR: file " + sampleListForMerging + " not found"
    print "exiting..."
    sys.exit()

# ---Check if sampleListForMergingQCD file exist
if os.path.isfile(sampleListForMergingQCD) is False:
    print "ERROR: file " + sampleListForMergingQCD + " not found"
    print "exiting..."
    sys.exit()

# ---Check if xsection file exist
if os.path.isfile(xsection) is False:
    print "ERROR: file " + xsection + " not found"
    print "exiting..."
    sys.exit()

print "Launched like:"
for arg in sys.argv:
    print "\t" + arg
print "Using tables:"
print "\t Data/MC:", dataMC_filepath
print "\t QCD(data):", qcd_data_filepath

# get xsections
cc.ParseXSectionFile(xsection)
dictSamples = cc.GetSamplesToCombineDict(sampleListForMerging)
dictSamplesQCD = cc.GetSamplesToCombineDict(sampleListForMergingQCD)
dictSamples.update(dictSamplesQCD)
# expand
dictSamples = cc.ExpandSampleDict(dictSamples)

d_systUpDeltas = {}
d_systDownDeltas = {}
d_systNominals = {} # same as rates, but more conveniently indexed

# SIC 6 Jul 2020 remove
# if doEEJJ:
#     dictSamplesTTBarRaw = GetSamplesToCombineDict(sampleListForMergingTTBar)
#     # only care about the TTBar parts
#     dictSamplesTTBar = {}
#     # for key in dictSamplesTTBarRaw.iterkeys():
#     #  if 'ttbar' in key.lower():
#     #    if 'ttbarunscaledrawfromdata' in key.lower():
#     #      print 'set dictSamplesTTBar[TTBarFromDATA] =',dictSamplesTTBarRaw[key],'for key:',key
#     #      dictSamplesTTBar['TTBarFromDATA'] = dictSamplesTTBarRaw[key]
#     # NB: we rely on this exact sample name for the total TTBar data-driven sample
#     # dictSamplesTTBar['TTBarFromDATA'] = dictSamplesTTBarRaw['TTBarUnscaledRawFromDATA']
#     # dictSamplesTTBar['TTBarFromDATA'] = ['TTBarFromDATA']
#     dictSamplesTTBar[ttbarSampleName] = [ttbarSampleName]
#     dictSamples.update(dictSamplesTTBar)
#     print "found ttbar samples:", dictSamplesTTBar

# check to make sure we have xsections for all samples
for lin in open(inputList):
    lin = string.strip(lin, "\n")
    if lin.startswith("#"):
        continue
    dataset_fromInputList = string.split(string.split(lin, "/")[-1], ".")[0]
    xsection_val = cc.lookupXSection(
        cc.SanitizeDatasetNameFromInputList(dataset_fromInputList)
    )

# rates/etc.
print "INFO: Filling background [MC] information..."
d_background_rates, d_background_rateErrs, d_background_unscaledRates, d_background_totalEvents, d_background_systs = FillDicts(dataMC_filepath, background_fromMC_names, "MC")
print "INFO: Filling background [data] information..."
bgFromData_rates, bgFromData_rateErrs, bgFromData_unscaledRates, bgFromData_totalEvents, bgFromData_systs = FillDicts(qcd_data_filepath, background_QCDfromData, "DATA")
d_background_rates.update(bgFromData_rates)
d_background_rateErrs.update(bgFromData_rateErrs)
d_background_unscaledRates.update(bgFromData_unscaledRates)
d_background_totalEvents.update(bgFromData_totalEvents)
d_background_systs.update(bgFromData_systs)
# above would be similar for TTBarFromDATA
print "INFO: Filling signal information..."
d_signal_rates, d_signal_rateErrs, d_signal_unscaledRates, d_signal_totalEvents, d_signal_systs = FillDicts(dataMC_filepath, signalNameList, "signal")
print "INFO: Filling data information..."
d_data_rates, d_data_rateErrs, d_data_unscaledRates, d_data_totalEvents, d_data_systs_garbage = FillDicts(dataMC_filepath, ["DATA"], "DATA")
# print one of the systematics for checking
# for syst in backgroundSystDict.keys():
#    print 'Syst is:',syst
#    print 'selection\t\tvalue'
#    for selection in sorted(backgroundSystDict[syst].keys()):
#        print selection+'\t\t'+str(backgroundSystDict[syst][selection])
#    break
# print signalSystDict
# print backgroundSystDict

print "INFO: Preparing datacard..."

card_file_path = datacard_filePath
card_file = open(card_file_path, "w")

for i_signal_name, signal_name in enumerate(signal_names):
    doMassPointLoop = True
    for i_mass_point, mass_point in enumerate(mass_points):
        # fullSignalName = signal_name.replace('[masspoint]',mass_point)
        fullSignalName, signalNameForFile = GetFullSignalName(signal_name, mass_point)
        # print "consider fullSignalName={}".format(fullSignalName)
        selectionName = "LQ" + mass_point
        # this will need to be fixed later if needed
        # else:
        #     # figure out mass point from name. currently the only case for this is RPV stop, where they are like 'Stop_M100_CTau100'
        #     mass = int(signal_name.split("_")[1].replace("M", ""))
        #     if mass < 200:
        #         mass = 200
        #     selectionName = "LQ" + str(mass)
        #     # print 'use selection name=',selectionName,'for fullSignalName=',fullSignalName
        #     doMassPointLoop = False

        txt_file_name = fullSignalName + ".txt\n"

        card_file.write(txt_file_name + "\n\n")
        card_file.write("imax " + str(n_channels) + "\n")
        card_file.write("jmax " + str(n_background) + "\n")
        card_file.write("kmax " + str(n_systematics) + "\n\n")

        card_file.write("bin bin1\n\n")

        if "BetaHalf" in signal_name:
            total_data = d_data_rates["DATA"][selectionName]
            card_file.write("observation " + str(total_data) + "\n\n")
        else:
            total_data = d_data_rates["DATA"][selectionName]
            card_file.write("observation " + str(total_data) + "\n\n")

        line = "bin "
        for i_channel in range(0, n_background + 1):
            line = line + "bin1 "
        card_file.write(line + "\n")

        line = "process " + fullSignalName + " "
        for background_name in background_names:
            line = line + background_name + " "
        card_file.write(line + "\n")

        line = "process 0 "
        for background_name in background_names:
            line = line + "1 "
        card_file.write(line + "\n\n")

        # rate line
        line = "rate "
        total_bkg = 0.0
        total_signal = d_signal_rates[signalNameForFile][selectionName]
        # if selectionName == "LQ300":
        #     print "d_signal_rates={}".format(d_signal_rates[signalNameForFile][selectionName])
        #     print "total_signal={}".format(total_signal)
        line = line + str(total_signal) + " "
        for ibkg, background_name in enumerate(background_names):
            thisBkgEvts = d_background_rates[background_name][selectionName]
            line += str(thisBkgEvts) + " "
            total_bkg += float(thisBkgEvts)
        card_file.write(line + "\n\n")

        # print signal_name, mass_point, total_signal, total_bkg, total_data
        # print signal_name+str(mass_point), total_signal, total_bkg

        # recall the form: systDict['PileupUp'/systematicFromHist]['ZJet_amcatnlo_ptBinned'/sampleName]['LQXXXX'/selection] = yield
        # for RPV, select proper signalSystDict based on ctau of signal
        # FIXME
        # if doRPV:
        #     ctau = int(signal_name[signal_name.find("CTau") + 4:])
        #     signalSystDict = signalSystDictByCTau[ctau]
        if doSystematics:
            for syst in systematicsNamesBackground:
                # XXX do we really need this?
                if int(mass_point) > maxLQSelectionMass:
                    selectionNameSyst = "LQ"+str(maxLQSelectionMass)
                else:
                    selectionNameSyst = selectionName
                line = syst + " lnN "
                if syst in systematicsNamesSignal:
                    if signalNameForFile not in d_systNominals.keys():
                        d_systNominals[signalNameForFile] = {}
                        d_systUpDeltas[signalNameForFile] = {}
                        d_systDownDeltas[signalNameForFile] = {}
                    if syst not in d_systNominals[signalNameForFile].keys():
                        d_systNominals[signalNameForFile][syst] = {}
                        d_systUpDeltas[signalNameForFile][syst] = {}
                        d_systDownDeltas[signalNameForFile][syst] = {}
                    systEntry, deltaOverNominalUp, deltaOverNominalDown = GetSystematicEffect(syst, signalNameForFile, selectionNameSyst, d_signal_systs)
                    thisSigEvts = d_signal_rates[signalNameForFile][selectionNameSyst]
                    thisSigSystUp = deltaOverNominalUp*thisSigEvts
                    thisSigSystDown = deltaOverNominalDown*thisSigEvts
                    d_systNominals[signalNameForFile][syst][selectionNameSyst] = thisSigEvts
                    d_systUpDeltas[signalNameForFile][syst][selectionNameSyst] = thisSigSystUp
                    d_systDownDeltas[signalNameForFile][syst][selectionNameSyst] = thisSigSystDown
                    line += str(systEntry) + " "
                else:
                    line += "- "
                for ibkg, background_name in enumerate(background_names):
                    if background_name not in d_systNominals.keys():
                        d_systNominals[background_name] = {}
                        d_systUpDeltas[background_name] = {}
                        d_systDownDeltas[background_name] = {}
                    if syst not in d_systNominals[background_name].keys():
                        d_systNominals[background_name][syst] = {}
                        d_systUpDeltas[background_name][syst] = {}
                        d_systDownDeltas[background_name][syst] = {}
                    systEntry, deltaOverNominalUp, deltaOverNominalDown = GetSystematicEffect(syst, background_name, selectionNameSyst, d_background_systs)
                    thisBkgEvts = d_background_rates[background_name][selectionNameSyst]
                    thisBkgSystUp = deltaOverNominalUp*thisBkgEvts
                    thisBkgSystDown = deltaOverNominalDown*thisBkgEvts
                    d_systNominals[background_name][syst][selectionNameSyst] = thisBkgEvts
                    d_systUpDeltas[background_name][syst][selectionNameSyst] = thisBkgSystUp
                    d_systDownDeltas[background_name][syst][selectionNameSyst] = thisBkgSystDown
                    line += str(systEntry) + " "
                card_file.write(line + "\n")

        # background stat error part
        for i_background_name, background_name in enumerate(background_names):
            thisBkgEvts = d_background_rates[background_name][selectionName]
            thisBkgEvtsErr = d_background_rateErrs[background_name][selectionName]
            thisBkgTotalEntries = d_background_unscaledRates[background_name][
                selectionName
            ]
            # print '[datacard] INFO:  for selection:',selectionName,' and background:',background_name,' total unscaled events=',thisBkgTotalEntries

            if thisBkgEvts != 0.0:
                lnN_f = 1.0 + 1.0 / math.sqrt(
                    thisBkgTotalEntries + 1
                )  # Poisson becomes Gaussian, approx by logN with this kappa
                gmN_weight = (
                    thisBkgEvts / thisBkgTotalEntries
                )  # for small uncertainties, use gamma distribution with alpha=(factor to go to signal region from control/MC)
                # if not doEEJJ and background_name=='SingleTop' and int(selectionName.replace('LQ','')) >= 650:
                #   statErr = GetStatErrorFromDict(statErrorsSingleTop,int(selectionName.replace('LQ','')))
                #   lnN_f = 1.0 + statErr/thisBkgEvts
                #   forceLogNormBkgStatUncert = True
            else:
                # print '[datacard] INFO:  for selection:', selectionName, 'and background:', background_name,
                # 'total unscaled events=', thisBkgTotalEntries, 'rate=', thisBkgEvts
                # for small uncertainties, use gamma distribution with alpha=(factor to go to signal region from control/MC)
                # since we can't compute evts/entries, we use it from the preselection (following LQ2)
                # gmN_weight = d_background_rates[background_name]['preselection'] / d_background_unscaledRates[background_name]['preselection']
                # change: find last selection with at least 1 bkg event and use its scale factor
                massPointsRev = list(reversed(mass_points))
                idx = 0
                bkgRate = 0
                while bkgRate == 0:
                    lastSelectionName = "LQ" + massPointsRev[idx]
                    bkgEvents = d_background_unscaledRates[background_name][
                        lastSelectionName
                    ]
                    bkgRate = d_background_rates[background_name][lastSelectionName]
                    idx += 1
                # ? TODO ?
                #if background_name != "PhotonJets_Madgraph":
                #    print "[datacard] INFO: for background:", background_name, "at selection:", selectionName, "found last selection:", lastSelectionName, "with", bkgEvents, "unscaled MC events. use this for the scale factor."
                gmN_weight = bkgRate / bkgEvents
                # if thisBkgTotalEntries != 0.0 and "TTBarFromDATA" in background_name:
                #     print "[datacard] WARN: for background:", background_name, "at selection:", selectionName, "setting thisBkgTotalEntries=", thisBkgTotalEntries, "to zero!"
                #     thisBkgTotalEntries = 0.0

                # # special handling of stat errors for small backgrounds
                # if doEEJJ and background_name=='SingleTop':
                #    gmN_weight = GetStatErrorFromDict(statErrorsSingleTop,int(selectionName.replace('LQ','')))
                # TODO: check photon jets
                # if doEEJJ and background_name == "PhotonJets_Madgraph":
                #     gmN_weight = GetStatErrorFromDict(
                #         statErrorsPhotonJets, int(selectionName.replace("LQ", ""))
                #     )

            line_ln = "stat_" + background_name + " lnN -"
            line_gm = (
                "stat_"
                + background_name
                + " gmN "
                + str(int(thisBkgTotalEntries))
                + " -"
            )
            for i_tmp in range(0, i_background_name):
                line_ln = line_ln + " -"
                line_gm = line_gm + " -"
            line_ln = line_ln + " " + str(lnN_f)
            line_gm = line_gm + " " + str(gmN_weight)
            for i_tmp in range(i_background_name, len(background_names) - 1):
                line_ln = line_ln + " -"
                line_gm = line_gm + " -"

            if thisBkgTotalEntries > 10 and not forceGmNNormBkgStatUncert:
                card_file.write(line_ln + "\n")
            else:
                card_file.write(line_gm + "\n")
            # if background_name=='TTbar_Madgraph':
            #    print 'selectionName=',selectionName
            #    print 'thisBkgEvts=',thisBkgEvts
            #    print 'thisBkgEvtsErr=',thisBkgEvtsErr
            #    print 'thisBkgTotalEntries=',thisBkgTotalEntries
            #    print 'line_gm=',line_gm

        # signal stat error part
        # always use lnN error
        thisSigEvts = d_signal_rates[signalNameForFile][selectionName]
        thisSigEvtsErr = d_signal_rateErrs[signalNameForFile][selectionName]
        thisSigTotalEntries = d_signal_unscaledRates[signalNameForFile][selectionName]
        # if thisSigEvts == 0.0:
        #  print 'ERROR: signal events for this signal (',fullSignalName,'came out to be zero...stat error not supported. Quitting!'
        #  exit(-1)
        if thisSigEvts != 0.0:
            lnN_f = 1.0 + 1.0 / math.sqrt(
                thisSigTotalEntries + 1
            )  # Poisson becomes Gaussian, approx by logN with this kappa
            gmN_weight = thisSigEvts / thisSigTotalEntries
        else:
            # THIS IS BROKEN FIXME ???
            print "WARN: found zero signal events [" + str(
                thisSigEvts
            ) + "] for this signal:", fullSignalName, "and selection:", selectionName
            # gmN_weight = d_signal_rates[background_name]['preselection'] / d_signal_unscaledRates[background_name]['preselection']
            gmN_weight = 0.0
        line_ln = "stat_Signal lnN " + str(lnN_f)
        line_gm = (
            "stat_Signal gmN " + str(int(thisBkgTotalEntries)) + " " + str(gmN_weight)
        )
        for i_background_name, background_name in enumerate(background_names):
            line_ln = line_ln + " -"
            line_gm = line_ln + " -"
        if thisSigTotalEntries > 10:
            card_file.write(line_ln + "\n")
        else:
            card_file.write(line_gm + "\n")

        # DONE!
        card_file.write("\n\n\n")
        if not doMassPointLoop:
            break

card_file.close()
print "datacard written to: {}".format(card_file_path)

selectionNames = ["preselection"]
selectionNames.extend(["LQ"+str(mass) for mass in mass_points])
if doSystematics:
    # make the plots
    plots_tfile = r.TFile(plots_filePath, "recreate")
    systDir = plots_tfile.mkdir("systematics")
    for sampleName in d_systNominals.keys():
        for syst in d_systNominals[sampleName].keys():
            systDir.cd()
            systDir.mkdir(syst, syst, True).cd()
            massList = []
            nominals = []
            upVariation = []
            downVariation = []
            for selection, value in sorted(d_systNominals[sampleName][syst].iteritems(), key=lambda x: float(x[0].replace("LQ", ""))):
                massList.append(float(selection.replace("LQ", "")))
                nominals.append(0.0)  # nominals.append(float(value))
                if value > 0:
                    upVariation.append(100*float(d_systUpDeltas[sampleName][syst][selection])/value)
                    downVariation.append(100*float(d_systDownDeltas[sampleName][syst][selection])/value)
                else:
                    # FIXME TODO
                    upVariation.append(0.0)
                    downVariation.append(0.0)
            # if "Z" in sampleName:
            #     if "EES" in syst:
            #         print "INFO for sampleName={} syst={}".format(sampleName, syst)
            #         print "massList:", massList
            #         print "nominals:", nominals
            #         print "downVariation:", downVariation
            #         print "upVariation:", upVariation
            plots_tfile.cd("systematics/"+syst)
            systGraph = r.TGraphAsymmErrors(len(massList), np.array(massList), np.array(nominals), np.array([0.0]*len(massList)),
                                            np.array([0.0]*len(massList)), np.array(downVariation), np.array(upVariation))
            systGraph.SetNameTitle("uncertVsMass_{}".format(sampleName))
            systGraph.GetXaxis().SetTitle("M_{LQ} [GeV]")
            systGraph.GetYaxis().SetTitle(syst+" Uncertainty [%]")
            systGraph.SetFillColor(9)
            systGraph.SetFillStyle(3003)
            systGraph.Write()
    plots_tfile.Close()
    print "plots written to: {}".format(plots_filePath)

    # tables
    columnNames = ["Systematic", "Signal (%)", "Background (%)"]
    for selectionName in selectionNames:
        if selectionName == "preselection":  # change this if we want to see systematics at preselection
            continue
        table = PrettyTable(columnNames)
        table.align["Systematic"] = "l"
        table.float_format = "4.3"
        for syst in systematicsNamesBackground:
            if "QCD" in syst:
                continue  # don't need to print the flat QCD syst in each table
            selectionNameSyst = selectionName
            if selectionName != "preselection":
                massPoint = selectionName.replace("LQ", "")
                if int(massPoint) > maxLQSelectionMass:
                    selectionNameSyst = "LQ"+str(maxLQSelectionMass)
            if syst in systematicsNamesSignal:
                for i_signal_name, signal_name in enumerate(signal_names):
                    fullSignalName, signalNameForFile = GetFullSignalName(signal_name, massPoint)
                    entry, sigSystDeltaOverNominalUp, sigSystDeltaOverNominalDown = GetSystematicEffect(syst, signalNameForFile, selectionNameSyst, d_signal_systs)
                    if entry == "-":
                        thisSigSystPercent = -1
                        continue
                    thisSigSyst = max(sigSystDeltaOverNominalUp, sigSystDeltaOverNominalDown)
                    thisSigSystPercent = 100*thisSigSyst
            else:
                thisSigSystPercent = "  - "
            totalBkgSyst = 0
            totalBkgNominal = 0
            for background_name in background_names:
                entry, bkgSystDeltaOverNominalUp, bkgSystDeltaOverNominalDown = GetSystematicEffect(syst, background_name, selectionNameSyst, d_background_systs)
                if entry != "-":
                    thisBkgSyst = max(bkgSystDeltaOverNominalUp, bkgSystDeltaOverNominalDown)
                    totalBkgNominal += d_systNominals[background_name][syst][selectionNameSyst]
                    thisBkgDelta = thisBkgSyst*d_systNominals[background_name][syst][selectionNameSyst]
                    totalBkgSyst += thisBkgDelta*thisBkgDelta
            if totalBkgNominal > 0:
                totalBkgSystPercent = 100*(math.sqrt(totalBkgSyst))/totalBkgNominal
            else:
                totalBkgSystPercent = -1
            table.add_row([d_systTitles[syst], thisSigSystPercent, totalBkgSystPercent])
        print "Selection: {}".format(selectionName)
        print table

# make final selection tables
if doEEJJ:
    # columnNames = ['MLQ','signal','Z+jets','ttbar(data)','QCD(data)','Other','Total BG','Data']
    columnNames = [
        "MLQ",
        "signal",
        "Z+jets",
        "ttbar",
        "QCD(data)",
        "DIBOSON",
        "TRIBOSON",
        "TTW",
        "TTZ",
        "SingleTop",
        "W+Jets",
        "PhotonJets",
        "Total BG",
        "Data",
    ]
else:
    # columnNames = ['MLQ','signal','W+jets','ttbar(powheg)','QCD(data)','Other','Total BG','Data']
    columnNames = [
        "MLQ",
        "signal",
        "W+jets",
        "ttbar(powheg)",
        "QCD(data)",
        "DIBOSON",
        "SingleTop",
        "Z+Jets",
        "PhotonJets",
        "Total BG",
        "Data",
    ]
## FOR TESTING
# columnNames = ['MLQ']
# for bn in background_names:
#  columnNames.append(bn)
if doEEJJ:
    otherBackgrounds = [
        "PhotonJets_Madgraph",
        "WJet_amcatnlo_jetBinned",
        "DIBOSON_nlo",
        "TRIBOSON",
        "TTW",
        "TTZ",
        "SingleTop",
    ]
else:
    otherBackgrounds = [
        "PhotonJets_Madgraph",
        "ZJet_amcatnlo_ptBinned",
        "DIBOSON_amcatnlo",
        "SingleTop",
    ]
# background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTbar_Madgraph", "WJet_Madgraph_HT", "ZJet_Madgraph_HT", "DIBOSON","SingleTop"  ]
latexRowsAN = []
latexRowsPaper = []
t = PrettyTable(columnNames)
t.float_format = "4.3"
selectionNames = ["preselection"]
selectionNames.extend(["LQ"+str(mass) for mass in mass_points])
for i_signal_name, signal_name in enumerate(signal_names):
    for i_sel_name, selectionName in enumerate(selectionNames):
        # signal events
        thisSigEvts = "-"
        thisSigEvtsErr = "-"
        if selectionName != "preselection":
            massPoint = selectionName.replace("LQ", "")
            fullSignalName, signalNameForFile = GetFullSignalName(signal_name, massPoint)
            thisSigEvts = d_signal_rates[signalNameForFile][selectionName]
            thisSigEvtsErr = d_signal_rateErrs[signalNameForFile][selectionName]
        # print 'INFO: thisSignal=',fullSignalName,'selection=',selectionName
        # print 'd_data_rates[data]['+selectionName+']'
        if blinded:
            thisDataEvents = -1
        else:
            thisDataEvents = d_data_rates["DATA"][selectionName]
        backgroundEvts = {}
        backgroundEvtsErrUp = {}
        backgroundEvtsErrDown = {}
        backgroundEvtsErrIsAsymm = {}
        totalBackground = 0.0
        totalBackgroundErrStatUp = 0.0
        totalBackgroundErrStatDown = 0.0
        totalBackgroundErrSyst = 0.0
        otherBackground = 0.0
        otherBackgroundErrStatUp = 0.0
        otherBackgroundErrStatDown = 0.0
        for i_background_name, background_name in enumerate(background_names):
            thisBkgEvts = d_background_rates[background_name][selectionName]
            # print "INFO:  background_name={}, d_background_rates[{}]=".format(background_name, background_name), d_background_rates[background_name]
            thisBkgEvtsErr = d_background_rateErrs[background_name][selectionName]
            thisBkgEvtsErrUp = d_background_rateErrs[background_name][selectionName]
            thisBkgEvtsErrDown = thisBkgEvtsErrUp
            thisBkgTotalEntries = d_background_unscaledRates[background_name][
                selectionName
            ]
            backgroundEvtsErrIsAsymm[background_name] = False
            # print "INFO:  for selection:", selectionName, " and background:", background_name, " total unscaled events=", thisBkgTotalEntries
            forceSymmErr = False
            if thisBkgTotalEntries <= 10.0:
                if thisBkgEvts > 0.0:
                    thisBkgEvtsErrUp, thisBkgEvtsErrDown = GetStatErrors(
                        thisBkgTotalEntries,
                        thisBkgEvts / thisBkgTotalEntries,
                        thisBkgEvts,
                    )
                    if thisBkgTotalEntries < 5:
                        print "INFO:  using:", background_name, ": thisBkgTotalEntries=", thisBkgTotalEntries, "selection", selectionName, " thisBkgEvts=", thisBkgEvts, "thisBkgEvtsErr=", thisBkgEvtsErr
                        print "INFO:      thisBkgEvtsErrUp=", thisBkgEvtsErrUp, "; thisBkgEvtsErrDown=", thisBkgEvtsErrDown, "nevts=", thisBkgTotalEntries, "theta=", thisBkgEvts / thisBkgTotalEntries
                    if thisBkgEvtsErrUp < 0 or thisBkgEvtsErrDown < 0:
                        print "ERROR:  thisBkgEvtsErrUp=", thisBkgEvtsErrUp, "; thisBkgEvtsErrDown=", thisBkgEvtsErrDown, "nevts=", thisBkgTotalEntries, "theta=", thisBkgEvts / thisBkgTotalEntries
                        print "ERROR:      using:", background_name, ": selection", selectionName, "thisBkgEvts=", thisBkgEvts, "thisBkgTotalEntries=", thisBkgTotalEntries, "thisBkgEvtsErr=", thisBkgEvtsErr
                        # exit(-1)
                    ## special fit extrap errors
                    # if not doEEJJ and background_name=='SingleTop' and int(selectionName.replace('LQ','')) >= 650:
                    #   thisBkgEvtsErrUp = GetStatErrorFromDict(statErrorsSingleTop,int(selectionName.replace('LQ','')))
                    #   thisBkgEvtsErrDown = thisBkgEvtsErrUp
                    #   forceSymmErr = True
                else:
                    massPointsRev = list(reversed(mass_points))
                    idx = 0
                    bkgRate = 0
                    while bkgRate == 0:
                        lastSelectionName = "LQ" + massPointsRev[idx]
                        bkgEvents = d_background_unscaledRates[background_name][
                            lastSelectionName
                        ]
                        bkgRate = d_background_rates[background_name][lastSelectionName]
                        idx += 1
                    print "INFO: for background:", background_name, "at selection:", selectionName, "found last selection:", lastSelectionName, "with", bkgEvents, "unscaled MC events. use this for the scale factor."
                    rateOverUnscaledRatePresel = bkgRate / bkgEvents
                    print "[table] Call GetStatErrors(", thisBkgTotalEntries, rateOverUnscaledRatePresel, thisBkgEvts, ")"
                    thisBkgEvtsErrUp, thisBkgEvtsErrDown = GetStatErrors(
                        thisBkgTotalEntries, rateOverUnscaledRatePresel, thisBkgEvts
                    )
                    ## special handling of stat errors for small backgrounds
                    # if doEEJJ and background_name=='SingleTop':
                    #    thisBkgEvtsErrDown=0
                    #    thisBkgEvtsErrUp = GetStatErrorFromDict(statErrorsSingleTop,int(selectionName.replace('LQ','')))
                    # if doEEJJ and background_name == "PhotonJets_Madgraph":
                    #     thisBkgEvtsErrDown = 0
                    #     thisBkgEvtsErrUp = GetStatErrorFromDict(
                    #         statErrorsPhotonJets, int(selectionName.replace("LQ", ""))
                    #     )
                    print "INFO:  using:", background_name, ": selection", selectionName, " thisBkgEvts=", thisBkgEvts, "thisBkgTotalEntries=", thisBkgTotalEntries, "thisBkgEvtsErr=", thisBkgEvtsErr
                    print "INFO:      thisBkgEvtsErrUp=", thisBkgEvtsErrUp, "; thisBkgEvtsErrDown=", thisBkgEvtsErrDown, "nevts=", thisBkgTotalEntries, "theta=", rateOverUnscaledRatePresel, "[preselection]"
                    if thisBkgEvtsErrUp < 0 or thisBkgEvtsErrDown < 0:
                        print "ERROR:  thisBkgEvtsErrUp=", thisBkgEvtsErrUp, "; thisBkgEvtsErrDown=", thisBkgEvtsErrDown, "nevts=", thisBkgTotalEntries, "theta=", rateOverUnscaledRatePresel, "[preselection]"
                        print "ERROR:      using:", background_name, ": selection", selectionName, " thisBkgEvts=", thisBkgEvts, "thisBkgTotalEntries=", thisBkgTotalEntries, "thisBkgEvtsErr=", thisBkgEvtsErr
                        # exit(-1)
                # rateOverUnscaledRatePresel = d_background_rates[background_name]['preselection'] / d_background_unscaledRates[background_name]['preselection']
                # thisBkgEvtsErrUp,thisBkgEvtsErrDown = GetStatErrors(thisBkgTotalEntries,rateOverUnscaledRatePresel)
                ##rateOverUnscaledRatePresel = d_background_rates[background_name]['preselection'] / d_background_unscaledRates[background_name]['preselection']
                ##thisBkgEvtsErrUp *= rateOverUnscaledRatePresel
                ##thisBkgEvtsErrDown *= rateOverUnscaledRatePresel
                backgroundEvtsErrIsAsymm[background_name] = (
                    True if not forceSymmErr else False
                )
                backgroundEvtsErrUp[background_name] = thisBkgEvtsErrUp
                backgroundEvtsErrDown[background_name] = thisBkgEvtsErrDown
                # print background_name,': selection',selectionName,'rateOverUnscaledRatePresel=',rateOverUnscaledRatePresel,'thisBkgEvtsErr=',thisBkgEvtsErr
            thisBkgSyst = GetBackgroundSystDeltaOverNominal(background_name, selectionName)
            thisBkgSystErr = thisBkgEvts * thisBkgSyst
            totalBackground += thisBkgEvts
            totalBackgroundErrStatUp += thisBkgEvtsErrUp * thisBkgEvtsErrUp
            totalBackgroundErrStatDown += thisBkgEvtsErrDown * thisBkgEvtsErrDown
            totalBackgroundErrSyst += thisBkgSystErr * thisBkgSystErr
            print "background:", background_name, "thisBkgEvents =", thisBkgEvts, "+", thisBkgEvtsErrUp, "-", thisBkgEvtsErrDown, "GetBackgroundSystDeltaOverNominal(systematicsNamesBackground[" + str(
                i_background_name
            ) + "]," + selectionName + ")=", thisBkgSyst
            # if selectionName=='preselection':
            #  print 'background:',background_name,'thisBkgEvents =',thisBkgEvts,'GetBackgroundSystDeltaOverNominal(systematicsNamesBackground['+str(i_background_name)+'],'+selectionName+')=',thisBkgSyst
            #  print 'thisBkgSystErr=',math.sqrt(thisBkgSystErr)
            #  print 'updated totalBackgroundErrSyst',math.sqrt(totalBackgroundErrSyst)
            #  #print 'totalBackgound=',totalBackground
            if background_name in otherBackgrounds:
                otherBackground += thisBkgEvts
                otherBackgroundErrStatUp += thisBkgEvtsErrUp * thisBkgEvtsErrUp
                otherBackgroundErrStatDown += thisBkgEvtsErrDown * thisBkgEvtsErrDown
            if thisBkgEvts < 0:
                print "WARNING: Found", thisBkgEvts, "events for", background_name, "; setting to zero"
                thisBkgEvts = 0.0
            backgroundEvts[background_name] = thisBkgEvts
            backgroundEvtsErrUp[background_name] = thisBkgEvtsErrUp
            backgroundEvtsErrDown[background_name] = thisBkgEvtsErrDown
        totalBackgroundErrStatUp = math.sqrt(totalBackgroundErrStatUp)
        totalBackgroundErrStatDown = math.sqrt(totalBackgroundErrStatDown)
        totalBackgroundErrSyst = math.sqrt(totalBackgroundErrSyst)
        otherBackgroundErrStatUp = math.sqrt(otherBackgroundErrStatUp)
        otherBackgroundErrStatDown = math.sqrt(otherBackgroundErrStatDown)
        row = [selectionName]
        # test to see all backgrounds
        # for bn in background_names:
        #  row.append(GetTableEntryStr(backgroundEvts[bn],backgroundEvtsErrUp[bn],backgroundEvtsErrDown[bn]))
        # actual
        row = [
            selectionName.replace("LQ", ""),
            GetTableEntryStr(
                thisSigEvts, thisSigEvtsErr, thisSigEvtsErr
            ),  # assumes we always have > 0 signal events
        ]
        # FIXME: unhardcode all of these
        if doEEJJ:
            row.extend(
                [
                    GetTableEntryStr(
                        backgroundEvts["ZJet_amcatnlo_ptBinned"],
                        backgroundEvtsErrUp["ZJet_amcatnlo_ptBinned"],
                        backgroundEvtsErrDown["ZJet_amcatnlo_ptBinned"],
                    ) if do2016 else
                    GetTableEntryStr(
                        backgroundEvts["ZJet_jetAndPtBinned"],
                        backgroundEvtsErrUp["ZJet_jetAndPtBinned"],
                        backgroundEvtsErrDown["ZJet_jetAndPtBinned"],
                    ),
                    GetTableEntryStr(
                        # backgroundEvts["TTBarFromDATA"],
                        # backgroundEvtsErrUp["TTBarFromDATA"],
                        # backgroundEvtsErrDown["TTBarFromDATA"],
                        backgroundEvts["TTbar_powheg"],
                        backgroundEvtsErrUp["TTbar_powheg"],
                        backgroundEvtsErrDown["TTbar_powheg"],
                    ),
                ]
            )
        else:
            row.extend(
                [
                    GetTableEntryStr(
                        backgroundEvts["WJet_amcatnlo_ptBinned"],
                        backgroundEvtsErrUp["WJet_amcatnlo_ptBinned"],
                        backgroundEvtsErrDown["WJet_amcatnlo_ptBinned"],
                    ),
                    # GetTableEntryStr(backgroundEvts['TTbar_amcatnlo_Inc'],backgroundEvtsErrUp['TTbar_amcatnlo_Inc'],backgroundEvtsErrDown['TTbar_amcatnlo_Inc'])
                    GetTableEntryStr(
                        backgroundEvts["TTbar_powheg"],
                        backgroundEvtsErrUp["TTbar_powheg"],
                        backgroundEvtsErrDown["TTbar_powheg"],
                    ),
                ]
            )
        row.extend(
            [
                GetTableEntryStr(
                    backgroundEvts["QCDFakes_DATA"],
                    backgroundEvtsErrUp["QCDFakes_DATA"],
                    backgroundEvtsErrDown["QCDFakes_DATA"],
                ),
                # GetTableEntryStr(otherBackground,otherBackgroundErrStatUp,otherBackgroundErrStatDown),
                GetTableEntryStr(
                    backgroundEvts["DIBOSON_nlo"],
                    backgroundEvtsErrUp["DIBOSON_nlo"],
                    backgroundEvtsErrDown["DIBOSON_nlo"],
                ),
                GetTableEntryStr(
                    backgroundEvts["TRIBOSON"],
                    backgroundEvtsErrUp["TRIBOSON"],
                    backgroundEvtsErrDown["TRIBOSON"],
                ),
                GetTableEntryStr(
                    backgroundEvts["TTW"],
                    backgroundEvtsErrUp["TTW"],
                    backgroundEvtsErrDown["TTW"],
                ),
                GetTableEntryStr(
                    backgroundEvts["TTZ"],
                    backgroundEvtsErrUp["TTZ"],
                    backgroundEvtsErrDown["TTZ"],
                ),
                GetTableEntryStr(
                    backgroundEvts["SingleTop"],
                    backgroundEvtsErrUp["SingleTop"],
                    backgroundEvtsErrDown["SingleTop"],
                ),
            ]
        )
        if doEEJJ:
            row.append(
                GetTableEntryStr(
                    backgroundEvts["WJet_amcatnlo_jetBinned"],
                    backgroundEvtsErrUp["WJet_amcatnlo_jetBinned"],
                    backgroundEvtsErrDown["WJet_amcatnlo_jetBinned"],
                )
            )
        else:
            row.append(
                GetTableEntryStr(
                    backgroundEvts["ZJet_amcatnlo_ptBinned"],
                    backgroundEvtsErrUp["ZJet_amcatnlo_ptBinned"],
                    backgroundEvtsErrDown["ZJet_amcatnlo_ptBinned"],
                )
            )
        row.extend(
            [
                GetTableEntryStr(
                    backgroundEvts["PhotonJets_Madgraph"],
                    backgroundEvtsErrUp["PhotonJets_Madgraph"],
                    backgroundEvtsErrDown["PhotonJets_Madgraph"],
                ),
                GetTableEntryStr(
                    totalBackground,
                    totalBackgroundErrStatUp,
                    totalBackgroundErrStatDown,
                    totalBackgroundErrSyst,
                ),
                GetTableEntryStr(thisDataEvents),
            ]
        )
        t.add_row(row)
        # latex tables
        latexRow = [
            selectionName.replace("LQ", ""),
            GetTableEntryStr(
                thisSigEvts, thisSigEvtsErr, thisSigEvtsErr, latex=True
            ),  # assumes we always have > 0 signal events
        ]
        if doEEJJ:
            latexRow.extend(
                [
                    GetTableEntryStr(
                        backgroundEvts["ZJet_amcatnlo_ptBinned"],
                        backgroundEvtsErrUp["ZJet_amcatnlo_ptBinned"],
                        backgroundEvtsErrDown["ZJet_amcatnlo_ptBinned"],
                        latex=True,
                    ) if do2016 else
                    GetTableEntryStr(
                        backgroundEvts["ZJet_jetAndPtBinned"],
                        backgroundEvtsErrUp["ZJet_jetAndPtBinned"],
                        backgroundEvtsErrDown["ZJet_jetAndPtBinned"],
                        latex=True,
                    ),
                    GetTableEntryStr(
                        backgroundEvts["TTbar_powheg"],
                        backgroundEvtsErrUp["TTbar_powheg"],
                        backgroundEvtsErrDown["TTbar_powheg"],
                        latex=True,
                    ),
                ]
            )
        else:
            latexRow.extend(
                [
                    GetTableEntryStr(
                        backgroundEvts["WJet_amcatnlo_ptBinned"],
                        backgroundEvtsErrUp["WJet_amcatnlo_ptBinned"],
                        backgroundEvtsErrDown["WJet_amcatnlo_ptBinned"],
                        latex=True,
                    ),
                    # GetTableEntryStr(backgroundEvts['TTbar_amcatnlo_Inc'],backgroundEvtsErrUp['TTbar_amcatnlo_Inc'],backgroundEvtsErrDown['TTbar_amcatnlo_Inc'],latex=True)
                    GetTableEntryStr(
                        backgroundEvts["TTbar_powheg"],
                        backgroundEvtsErrUp["TTbar_powheg"],
                        backgroundEvtsErrDown["TTbar_powheg"],
                        latex=True,
                    ),
                ]
            )
        latexRowPaper = list(latexRow)  # copy the list
        # for the paper, we want VV, W/Z, single t, GJets in a single column; then background and data
        latexRowPaper.extend(
            [
                GetTableEntryStr(
                    backgroundEvts["QCDFakes_DATA"],
                    backgroundEvtsErrUp["QCDFakes_DATA"],
                    backgroundEvtsErrDown["QCDFakes_DATA"],
                    latex=True,
                ),
                GetTableEntryStr(
                    otherBackground,
                    otherBackgroundErrStatUp,
                    otherBackgroundErrStatDown,
                    latex=True,
                ),
                GetTableEntryStr(
                    totalBackground,
                    totalBackgroundErrStatUp,
                    totalBackgroundErrStatDown,
                    totalBackgroundErrSyst,
                    True,
                ),
                GetTableEntryStr(thisDataEvents, latex=True),
            ]
        )
        # for the AN, break down the other backgrounds
        latexRow.extend(
            [
                GetTableEntryStr(
                    backgroundEvts["QCDFakes_DATA"],
                    backgroundEvtsErrUp["QCDFakes_DATA"],
                    backgroundEvtsErrDown["QCDFakes_DATA"],
                    latex=True,
                ),
                # GetTableEntryStr(otherBackground,otherBackgroundErrStatUp,otherBackgroundErrStatDown,latex=True),
                GetTableEntryStr(
                    backgroundEvts["DIBOSON_nlo"],
                    backgroundEvtsErrUp["DIBOSON_nlo"],
                    backgroundEvtsErrDown["DIBOSON_nlo"],
                    latex=True,
                ),
                GetTableEntryStr(
                    backgroundEvts["TRIBOSON"],
                    backgroundEvtsErrUp["TRIBOSON"],
                    backgroundEvtsErrDown["TRIBOSON"],
                    latex=True,
                ),
                GetTableEntryStr(
                    backgroundEvts["TTW"],
                    backgroundEvtsErrUp["TTW"],
                    backgroundEvtsErrDown["TTW"],
                    latex=True,
                ),
                GetTableEntryStr(
                    backgroundEvts["TTZ"],
                    backgroundEvtsErrUp["TTZ"],
                    backgroundEvtsErrDown["TTZ"],
                    latex=True,
                ),
                GetTableEntryStr(
                    backgroundEvts["SingleTop"],
                    backgroundEvtsErrUp["SingleTop"],
                    backgroundEvtsErrDown["SingleTop"],
                    latex=True,
                ),
            ]
        )
        if doEEJJ:
            latexRow.append(
                GetTableEntryStr(
                    backgroundEvts["WJet_amcatnlo_jetBinned"],
                    backgroundEvtsErrUp["WJet_amcatnlo_jetBinned"],
                    backgroundEvtsErrDown["WJet_amcatnlo_jetBinned"],
                    latex=True,
                )
            )
        else:
            latexRow.append(
                GetTableEntryStr(
                    backgroundEvts["ZJet_amcatnlo_ptBinned"],
                    backgroundEvtsErrUp["ZJet_amcatnlo_ptBinned"],
                    backgroundEvtsErrDown["ZJet_amcatnlo_ptBinned"],
                    latex=True,
                )
            )
        latexRow.extend(
            [
                GetTableEntryStr(
                    backgroundEvts["PhotonJets_Madgraph"],
                    backgroundEvtsErrUp["PhotonJets_Madgraph"],
                    backgroundEvtsErrDown["PhotonJets_Madgraph"],
                    latex=True,
                ),
                GetTableEntryStr(
                    totalBackground,
                    totalBackgroundErrStatUp,
                    totalBackgroundErrStatDown,
                    totalBackgroundErrSyst,
                    True,
                ),
                GetTableEntryStr(thisDataEvents, latex=True),
            ]
        )
        latexRow = [
            "$" + entry + "$" if "LQ" not in entry and "pres" not in entry else entry
            for entry in latexRow
        ]
        latexRowPaper = [
            "$" + entry + "$" if "LQ" not in entry and "pres" not in entry else entry
            for entry in latexRowPaper
        ]
        for i, rowEntry in enumerate(latexRow):
            if i < len(latexRow) - 1:
                # rowEntry+=' & '
                latexRow[i] += " & "
            else:
                # rowEntry+=' \\\\ '
                latexRow[i] += " \\\\ "
        latexRowsAN.append("".join(latexRow))
        #
        for i, rowEntry in enumerate(latexRowPaper):
            if i < len(latexRowPaper) - 1:
                latexRowPaper[i] += " & "
            else:
                latexRowPaper[i] += " \\\\ "
        latexRowsPaper.append("".join(latexRowPaper))
        if selectionName == "preselection":
            latexRowsAN.append("\\hline")
            latexRowsPaper.append("\\hline")
print t

print
print "Latex table: AN"
print
# latex table -- AN
for line in latexRowsAN:
    print (line)
print

print
print "Latex table: Paper"
print
# latex table -- Paper
for line in latexRowsPaper:
    print (line)
print
exit(0)
