#!/usr/bin/env python2

import os
import sys
import math
import string
import re
from prettytable import PrettyTable
from tabulate import tabulate
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


def GetStatErrors(nevts, neff, theta=1.0):
    # use parameters as in datacard gamma distribution
    # see: https://cds.cern.ch/record/1379837/files/NOTE2011_005.pdf (eq. 18)
    verbose = False
    alpha = 1.0 - 0.682689492
    lower = (
        0 if neff == 0
        else nevts - r.Math.gamma_quantile(alpha/2, neff, theta)
    )
    upper = r.Math.gamma_quantile_c(alpha/2, neff+1, theta) - nevts
    if verbose:
        print "calculate upper gamma quantile_c for nevts={}, neff={}, theta={}; upper error={}".format(
                nevts, neff, theta, upper)
    return upper, lower


def GetStatErrorFromDict(statErrDict, mass):
    availMasses = sorted(statErrDict.keys())
    if mass not in availMasses and mass > availMasses[-1]:
        mass = availMasses[-1]
    return statErrDict[mass]


def GetStatErrorsFromDatacard(dictEntry, nevts):
    pdfType = dictEntry[0]
    if pdfType == "lnN" and len(dictEntry) == 2:
        return dictEntry[1], dictEntry[1]
    elif pdfType == "gmN" and len(dictEntry) == 3:
        # print "GetStatErrors({}, {}, {})".format(nevts, dictEntry[1], dictEntry[2])
        return GetStatErrors(nevts, dictEntry[1], dictEntry[2])
    else:
        raise RuntimeError("Could not GetStatErrorsFromDatacard: didn't understand dictEntry={}".format(dictEntry))


# returns dict like systDict[systName][selection] = yield
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
    # add special entry for branch titles
    systDict["branchTitles"] = {}
    tmapName = "tmap__{}__systematicNameToBranchesMap".format(sampleName)
    tmap = rootFile.Get(tmapName)
    for yBin in range(1, systHist.GetNbinsY()+1):
        branchTitleList = []
        systName = systHist.GetYaxis().GetBinLabel(yBin)
        mapObject = tmap.FindObject(systName)
        if not mapObject:
            # assume it's an array syst, so try to match stripping off the _N part
            mapObject = tmap.FindObject(systName[:systName.rfind("_")])
        # print "INFO: for syst {}, found matching mapObject key: {}, value: {}".format(systName, mapObject.Key(), mapObject.Value())
        branchTitleListItr = r.TIter(mapObject.Value())
        branchTitle = branchTitleListItr.Next()
        while branchTitle:
            branchTitleList.append(branchTitle.GetName())
            branchTitle = branchTitleListItr.Next()
        systDict["branchTitles"][systName] = branchTitleList
        # print "INFO: systDict[\"branchTitles\"][{}] = {}".format(systName, branchTitleList)
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
        systEntry, deltaOverNominalUp, deltaOverNominalDown = GetSystematicEffectAbs(syst, sampleName, selectionName, d_systs)
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


# return abs val of syst; also checks for deltaOverNom==1
def GetSystematicEffectAbs(systName, sampleName, selection, fullSystDict):
    entry, deltaOverNomUp, deltaOverNomDown = GetSystematicEffect(systName, sampleName, selection, fullSystDict)
    # entry is always >= 1 by construction in the function
    # if entry != "-":
    #     floatEntry = float(entry)
    #     entry = str(math.fabs(floatEntry-1)+1)
    if deltaOverNomUp == 0 and deltaOverNomDown == 0:
        return "-", 0, 0
    return entry, math.fabs(deltaOverNomUp), math.fabs(deltaOverNomDown)


def DoesSystematicApply(systName, sampleName):
    return systName in d_applicableSystematics[sampleName]


def GetSystematicEffect(systName, sampleName, selection, fullSystDict):
    if not DoesSystematicApply(systName, sampleName):
        return "-", 0, 0
    # systematicsNamesBackground = [
    #    "LHEPDFWeight",
    #    "Lumi",
    #    "EleTrigSF","Pileup",  "JER", "JES", "EleRecoSF", "EleHEEPSF", "EES",
    #    "EER",
    #    "TT_Norm", "DY_Norm",
    #    "DY_Shape", "TT_Shape", "Diboson_Shape",
    #    "QCD_Norm",
    # print "GetSystematicEffect({}, {}. {})".format(systName, sampleName, selection)
    systDict = fullSystDict[sampleName]
    if "shape" in systName.lower():
        entry, deltaNomUp, deltaNomDown = CalculateShapeSystematic("LHEScaleWeight", sampleName, selection, systDict)
    elif systName == "LHEPdfWeight":
        entry, deltaNomUp, deltaNomDown = CalculatePDFSystematic(systName, sampleName, selection, systDict)
    elif systName == "Lumi":
        entry, deltaNomUp, deltaNomDown = str(1+lumiDeltaXOverX), lumiDeltaXOverX, lumiDeltaXOverX
    elif "norm" in systName.lower():
        if "tt" in systName.lower() or "dy" in systName.lower() or "qcd" in systName.lower():
            entry, deltaNomUp, deltaNomDown = CalculateFlatSystematic(systName, systDict, selection)
    elif "eer" in systName.lower():
        entry, deltaNomUp, deltaNomDown = CalculateShiftSystematic(systName, systDict, selection, sampleName)
    else:
        entry, deltaNomUp, deltaNomDown = CalculateUpDownSystematic(systName, systDict, selection, sampleName)
    return entry, deltaNomUp, deltaNomDown


def CalculateShiftSystematic(systName, systDict, selection, sampleName):
    nominal, selection = GetSystNominalYield(systName, systDict, selection, sampleName)
    systYield = systDict[systName][selection]
    delta = math.fabs(nominal-systYield)  # always take absVal
    # print "CalculateShiftSystematic({}, {}, {}): nominal={}, systYield={}, delta={}, delta/nominal={}".format(
    #         systName, selection, sampleName, nominal, systYield, delta, delta/nominal)
    return str(1 + delta/nominal), delta/nominal, delta/nominal


def CalculateUpDownSystematic(systName, systDict, selection, sampleName):
    nominal = systDict["nominal"][selection]
    # print "CalculateUpDownSystematic({}, {}); nominal yield={}".format(systName, selection, nominal)
    nominal, selection = GetSystNominalYield(systName, systDict, selection, sampleName)
    # print "CalculateUpDownSystematic(): nominal={}, selection={} after GetNominalYield({})".format(nominal, selection, systName)
    try:
        systYieldUp = systDict[systName+"Up"][selection]
        systYieldDown = systDict[systName+"Down"][selection]
    except KeyError:
        raise RuntimeError("Could not find Up or Down key for syst={}; keys={}".format(systName, systDict.keys()))
    kUp = systYieldUp/nominal
    kDown = systYieldDown/nominal
    upDelta = systYieldUp-nominal
    downDelta = nominal-systYieldDown
    # print "CalculateUpDownSystematic(): systYieldUp={}, systYieldDown={}, systNominal={}".format(systYieldUp, systYieldDown, systDict["nominal"][selection])
    # print "CalculateUpDownSystematic(): kDown/kUp = {}/{}; return '{}', {}, {}".format(kDown, kUp, str(kDown/kUp), upDelta/nominal, downDelta/nominal)
    return str(kDown/kUp), upDelta/nominal, downDelta/nominal


def CalculateFlatSystematic(systName, systDict, selection):
    # assumes that the number here is < 1
    # print "d_applicableSystematics["+sampleName+"]=", d_applicableSystematics[sampleName]
    # print "for sample={}, systName={}, systDict.keys()={}".format(sampleName, systName, systDict.keys())
    return str(1 + systDict[systName][selection]), systDict[systName][selection], systDict[systName][selection]


def GetSystNominalYield(systName, systDict, selection, sampleName):
    try:
        nominal = systDict["nominal"][selection]
    except KeyError:
        raise RuntimeError("Could not find nominal key for systName={} sampleName={} selection={}; keys={}".format(
            systName, sampleName, selection, systDict.keys())
            )
    if nominal == 0:
        # take the last selection for which we have some rate, and use that for systematic evaluation
        lastNonzeroSelection, rate, err = GetNearestNonzeroSelectionYields(sampleName, selection)
        nominal = rate
        selection = lastNonzeroSelection
    return nominal, selection


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
        pdfType = "mc"
        pdfName = "PDF4LHC15_nnlo_30_pdfas"
    else:
        raise RuntimeError("Can't determine whether branch title '{}' is a Hessian or MC set".format(branchTitle))
    return pdfType, pdfName


def GetBranchTitle(systName, sampleName, selection, systDict):
    pdfKeys = [syst for syst in systDict.keys() if syst == systName]
    if len(pdfKeys) == 1:
        return "", pdfKeys
    if len(pdfKeys) < 1:
        # try for an array branch
        pdfKeys = [syst for syst in systDict.keys() if syst[:syst.rfind("_")] == systName]
    # here we have to handle the PDF syst somehow
    branchTitleLists = [systDict[key]["branchTitles"] for key in pdfKeys]
    branchTitleLists = [list(item) for item in set(tuple(titleList) for titleList in branchTitleLists)]
    # branchTitleLists = set(tuple(titleList) for titleList in branchTitleLists)
    if len(branchTitleLists) > 1:
        raise RuntimeError("For sample {}, found multiple branch title lists for the PDF syst variations: {}".format(sampleName, branchTitleLists))
    if len(branchTitleLists) < 1:
        raise RuntimeError("For sample {}, found zero branch title lists for the PDF syst variations; systDict.keys()={}".format(sampleName, systDict.keys()))
    branchTitleList = branchTitleLists[0]
    if len(branchTitleList) > 1:
        raise RuntimeError("For sample {}, found multiple branch titles for the PDF syst variations: {}".format(sampleName, branchTitleList))
    branchTitle = branchTitleList[0]
    return branchTitle, pdfKeys


def CalculatePDFSystematic(systName, sampleName, selection, systDict):
    branchTitle, pdfKeys = GetBranchTitle(systName, sampleName, selection, systDict)
    if len(pdfKeys) == 1:
        # we have an exactly matching PDF syst key; hwe manually specified a flat syst
        # assumes that the number here is < 1
        return str(1 + systDict[systName][selection]), systDict[systName][selection], systDict[systName][selection]
    # print "INFO: For sampleName={}, systName={}, found branch title={}".format(sampleName, systName, branchTitle)
    # print len(pdfKeys), "sorted(pdfKeys)=", sorted(pdfKeys, key=lambda x: int(x[x.rfind("_")+1:]))
    pdfVariationType, pdfName = GetPDFVariationType(branchTitle)
    # print "INFO: For sampleName={}, systName={}, found branch title={} and PDFType={}".format(sampleName, systName, branchTitle, pdfVariationType)
    if pdfVariationType != "mcNoCentral":
        pdfKeys.remove("LHEPdfWeight_0")  # don't consider index 0, central value
    if "mc" in pdfVariationType:
        return CalculatePDFVariationMC(systDict, sampleName, selection, pdfKeys)
    #elif pdfVariationType == "hessian":
    #    CalculatePDFVariationHessian()


def CalculatePDFVariationMC(systDict, sampleName, selection, pdfKeys):
    pdfKeys = sorted(pdfKeys, key=lambda x: int(x[x.rfind("_")+1:]))
    # now, if we still have over 100, remove the last two
    if len(pdfKeys) > 100:
        pdfKeys = pdfKeys[:-2]
    elif len(pdfKeys) == 32:
        pdfKeys = pdfKeys[:-2]
    nominal = systDict["nominal"][selection]
    if nominal == 0:
        # take the last selection for which we have some rate, and use that for systematic evaluation
        lastNonzeroSelection, rate, err, events = GetLastNonzeroSelectionYields(sampleName)
        nominal = rate
        selection = lastNonzeroSelection
    # print "INFO: we now have {} pdf variations to consider".format(len(pdfKeys))
    # Order the 100 yields and take the 84th and 16th.
    # See eq. 25 here: https://arxiv.org/pdf/1510.03865.pdf
    pdfYields = sorted([systDict[pdfKey][selection] for pdfKey in pdfKeys])
    if len(pdfKeys) == 100:
        pdfUp = pdfYields[83]
        pdfDown = pdfYields[15]
    elif len(pdfKeys) == 30:
        pdfUp = pdfYields[27]
        pdfDown = pdfYields[5]
    kDown = pdfDown/nominal
    kUp = pdfUp/nominal
    # if "boson" in sampleName.lower():
    #     print "for sampleName={}, selection={}, pdfYields={}, nominal={}; pdfUp={}, pdfDown={}; (pdfUp-nominal)/nominal={}".format(
    #             sampleName, selection, pdfYields, nominal, pdfUp, pdfDown, (pdfUp-nominal)/nominal)
    if kDown < 0:
        return str(1 + (pdfUp-nominal)/nominal), (pdfUp-nominal)/nominal, (pdfUp-nominal)/nominal
    elif kUp < 0:
        return str(1 + (pdfDown-nominal)/nominal), (pdfDown-nominal)/nominal, (pdfDown-nominal)/nominal
    else:
        return str(kDown/kUp), (pdfUp-nominal)/nominal, (pdfDown-nominal)/nominal


def CalculateShapeSystematic(systName, sampleName, selection, systDict):
    verbose = False
    if "DIBOSON" in sampleName:
        verbose = True
    branchTitle, shapeKeys = GetBranchTitle(systName, sampleName, selection, systDict)
    if verbose:
        print "INFO: For sampleName={}, systName={}, found branch title={} and shapeKeys={}".format(sampleName, systName, branchTitle, shapeKeys)
        # print "INFO: For sampleName={}, systName={}, found branch title={}".format(sampleName, systName, branchTitle)
    sys.stdout.flush()
    validIndices, shapeTitles = ParseShapeBranchTitle(branchTitle)
    validShapeKeys = [shapeKey for shapeKey in shapeKeys if shapeKey[shapeKey.rfind("_")+1:] in validIndices]
    nominal = systDict["nominal"][selection]
    if nominal == 0:
        # take the last selection for which we have some rate, and use that for systematic evaluation
        lastNonzeroSelection, rate = GetLastNonzeroSelectionYields(sampleName)
        nominal = rate
        selection = lastNonzeroSelection
    shapeYields = [systDict[shapeKey][selection] for shapeKey in validShapeKeys]
    if verbose:
        print "INFO: For sampleName={}, systName={}, found validShapeKeys={}, valid shapeTitles={} and shapeYields={}".format(
                sampleName, systName, validShapeKeys, shapeTitles, shapeYields)
    deltas = [math.fabs(shapeYield-nominal) for shapeYield in shapeYields]
    maxDelta = max(deltas)
    if verbose:
        print "INFO: For sampleName={}, systName={}, found deltas={} with maxDelta={} and nominal={}".format(
                sampleName, systName, deltas, maxDelta, nominal)
    return str(1+maxDelta/nominal), maxDelta/nominal, maxDelta/nominal


def ParseShapeBranchTitle(branchTitle):
    validIndices = []
    validTitles = []
    # one format of title: "LHE scale variation weights (w_var / w_nominal); [0] is muR=0.50000E+00 muF=0.50000E+00 ; [1] is muR=0.50000E+00 muF=0.10000E+01 ; " ... "[7] is muR=0.20000E+01 muF=0.10000E+01 ; [8] is muR=0.20000E+01 muF=0.20000E+01"
    # a second format: "LHE scale variation weights (w_var / w_nominal); [0] is renscfact=0.5d0 facscfact=0.5d0 ; [1] is renscfact=0.5d0 facscfact=1d0 ; " ... "[7] is renscfact=2d0 facscfact=1d0 ; [8] is renscfact=2d0 facscfact=2d0"
    # if "muR" in branchTitle:
    #     regEx = re.compile(r"\[(\d+)\] is muR=([0-9.+E]+) muF=([0-9.+E]+)")
    regEx = re.compile(r"\[(\d+)\][\D\s]+=([0-9.+Ed]+)[\D\s]+=([0-9.+Ed]+)")
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


def GetLatexHeaderFromColumnNames(columnNames):
    headers = []
    for col in columnNames:
        if "mlq" in col.lower():
            headers.append("$M_{LQ}$")
        elif "ttbar" in col.lower():
            headers.append(r"$t\bar{t}$")
        else:
            headers.append(col)
    headerLine = " & ".join(headers) + r" \\"
    return headerLine


def GetLastNonzeroSelectionYieldsFromDicts(rateDict, rateErrDict, unscaledRateDict):
    massPointsRev = list(reversed(mass_points))
    idx = 0
    rate = 0
    err = 0
    while rate == 0 or err == 0:
        lastSelectionName = "LQ" + massPointsRev[idx]
        rate = rateDict[lastSelectionName]
        err = rateErrDict[lastSelectionName]
        rawEvents = unscaledRateDict[lastSelectionName]
        idx += 1
    return lastSelectionName, rate, err, rawEvents


def GetLastNonzeroSelectionYields(sampleName):
    if sampleName in d_background_rates.keys():
        return GetLastNonzeroSelectionYieldsFromDicts(
                d_background_rates[sampleName], d_background_rateErrs[sampleName], d_background_unscaledRates[sampleName])
    if sampleName in d_signal_rates.keys():
        return GetLastNonzeroSelectionYieldsFromDicts(
                d_signal_rates[sampleName], d_signal_rateErrs[sampleName], d_signal_unscaledRates[sampleName])
    raise RuntimeError("Could not find sampleName={} in background keys={} or signal keys={}".format(
        sampleName, d_background_rates.keys(), d_signal_rates.keys()))


def GetNearestNonzeroSelectionYieldsFromDicts(rateDict, rateErrDict, selection):
    massPointsRev = list(reversed(mass_points))
    idx = massPointsRev.index(selection.replace("LQ", ""))
    rate = 0
    err = 0
    # just look below given selection
    while rate == 0 or err == 0:
        lastSelectionName = "LQ" + massPointsRev[idx]
        rate = rateDict[lastSelectionName]
        err = rateErrDict[lastSelectionName]
        idx += 1
    return lastSelectionName, rate, err


def GetNearestNonzeroSelectionYields(sampleName, selection):
    if sampleName in d_background_rates.keys():
        return GetNearestNonzeroSelectionYieldsFromDicts(
                d_background_rates[sampleName], d_background_rateErrs[sampleName], selection)
    if sampleName in d_signal_rates.keys():
        return GetNearestNonzeroSelectionYieldsFromDicts(
                d_signal_rates[sampleName], d_signal_rateErrs[sampleName], selection)
    raise RuntimeError("Could not find sampleName={} in background keys={} or signal keys={}".format(
        sampleName, d_background_rates.keys(), d_signal_rates.keys()))

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
            if "zjet" in sampleName.lower():
                d_systematics[sampleName].update({"DY_Norm": {sel: dyNormDeltaXOverX for sel in selectionNames}})
            if "ttbar" in sampleName.lower():
                d_systematics[sampleName].update({"TT_Norm": {sel: ttBarNormDeltaXOverX for sel in selectionNames}})
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
#inputLists[2016] = "$LQANA/config/nanoV7_2016_pskEEJJ_16mar2021_comb/inputListAllCurrent.txt"
inputLists[2016] = "$LQANA/config/nanoV7_2016_pskEEJJ_12apr2021/inputListAllCurrent.txt"
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
#filePaths[2016] = "$LQDATA/nanoV7/2016/analysis/precomputePrefire_looserPSK_eejj_16mar2021_oldOptFinalSels/output_cutTable_lq_eejj/"
filePaths[2016] = "$LQDATA/nanoV7/2016/analysis/precomputePrefire_looserPSK_eejj_12apr2021_oldOptFinalSels/output_cutTable_lq_eejj/"
filePaths[2017] = "$LQDATA/nanoV7/2017/analysis/prefire_eejj_23oct2020_optFinalSels/output_cutTable_lq_eejj/"
#
xsecFiles = {}
# xsecFiles[2016] = "$LQANA/versionsOfAnalysis/2016/nanoV7/eejj/aug26/unscaled/xsection_13TeV_2015_Mee_PAS_TTbar_Mee_PAS_DYJets.txt"
# xsecFiles[2016] = "$LQANA/config/xsection_13TeV_2015.txt"
# xsecFiles[2017] = "$LQANA/versionsOfAnalysis/2017/nanoV7/eejj/aug27/unscaled/xsection_13TeV_2015_Mee_PAS_TTbar_Mee_PAS_DYJets.txt"
xsecFiles[2016] = "$LQANA/versionsOfAnalysis/2016/nanoV7/eejj/apr16/xsection_13TeV_2015_Mee_PAS_gteTwoBtaggedJets_TTbar_Mee_PAS_DYJets.txt"

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
        "LHEPdfWeight",
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
        # "TTBarFromDATA",
        "TTbar_powheg",
        "QCDFakes_DATA",
        # "WJet_amcatnlo_ptBinned",
        # "DIBOSON_amcatnlo",
        "DIBOSON_nlo",
        "TRIBOSON",
        "TTW",
        "TTZ",
        "SingleTop",
        "WJet_amcatnlo_jetBinned",
        "PhotonJets_Madgraph",
    ]
    background_fromMC_names = [bkg for bkg in background_names if "data" not in bkg.lower()]
    background_QCDfromData = [bkg for bkg in background_names if "data" in bkg.lower() and "qcd" in bkg.lower()]
    systematicsNamesSignal = [syst for syst in systematicsNamesBackground if "shape" not in syst.lower() and "norm" not in syst.lower()]
    d_systTitles = {
            "EleTrigSF": "Trigger",
            "Pileup": "Pileup",
            "LHEPdfWeight": "PDF",
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
            "Diboson_Shape": "Diboson shape",
            "QCD_Norm": "QCD bkg. normalization",
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

selectionPoints = ["preselection"] + mass_points
selectionNames = ["LQ"+sel if "preselection" not in sel else sel for sel in selectionPoints]
additionalBkgSystsDict = {}
# update to 2016 analysis numbers
# QCDNorm is 0.50 [50% norm uncertainty for eejj = uncertaintyPerElectron*2]
if doEEJJ:
    qcdNormDeltaXOverX = 0.50
    # from: https://arxiv.org/pdf/1506.04072.pdf tables 1-3: 5% is probably good enough for SingleTop PDF syst
    additionalBkgSystsDict["SingleTop"] = {"LHEPdfWeight": {sel: 0.10 for sel in selectionNames}}
    if do2016:
        lumiDeltaXOverX = 0.012  # new number from https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM#SummaryTable
        dyNormDeltaXOverX = 0.01  # rounded up
        ttBarNormDeltaXOverX = 0.03
else:
    qcdNormDeltaXOverX = 0.25

n_background = len(background_names)
# all bkg systematics, plus stat 'systs' for all bkg plus signal plus 3 backNormSysts
# update July/Sep 2020: no more data-driven TBar, so only 1 extra syst for eejj
if doSystematics:
    if doEEJJ:
        # systematics + stat_errors_background + stat_errors_signal
        n_systematics = len(systematicsNamesBackground) + n_background + 1
    else:
        n_systematics = (
            len(systematicsNamesBackground) + n_background + 1 + 1
        )  # QCD norm only
else:
    n_systematics = n_background + 1
n_channels = 1

signalNameList = [GetFullSignalName(signalNameTemplate, massPoint)[1] for massPoint in mass_points]
allBkgSysts = [syst for syst in systematicsNamesBackground if "norm" not in syst.lower() and "shape" not in syst.lower()]
d_applicableSystematics = {bkg: list(allBkgSysts) for bkg in background_fromMC_names}
d_applicableSystematics.update({bkg: "QCD_Norm" for bkg in background_QCDfromData})
if do2016:
    d_applicableSystematics["ZJet_amcatnlo_ptBinned"].append("DY_Norm")
    d_applicableSystematics["ZJet_amcatnlo_ptBinned"].append("DY_Shape")
else:
    d_applicableSystematics["ZJet_jetAndPtBinned"].append("DY_Norm")
    d_applicableSystematics["ZJet_jetAndPtBinned"].append("DY_Shape")
d_applicableSystematics["TTbar_powheg"].append("TT_Norm")
d_applicableSystematics["TTbar_powheg"].append("TT_Shape")
d_applicableSystematics["DIBOSON_nlo"].append("Diboson_Shape")
d_applicableSystematics.update({sig: systematicsNamesSignal for sig in signalNameList})
datacard_filePath = "tmp_card_file.txt"
plots_filePath = "plots.root"
tables_filePath = "tables.txt"
systematics_dictFilePath = "systematics_dict.txt"
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
d_systNominals = {}  # same as rates, but more conveniently indexed
d_systematicsApplied = {}
d_datacardStatErrs = {}

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
for sampleName in additionalBkgSystsDict.iterkeys():
    d_background_systs[sampleName].update(additionalBkgSystsDict[sampleName])
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

print "INFO: Preparing datacard...",

card_file_path = datacard_filePath
card_file = open(card_file_path, "w")

selectionNames = ["preselection"]
selectionNames.extend(["LQ"+str(mass) for mass in mass_points])
for i_signal_name, signal_name in enumerate(signal_names):
    doMassPointLoop = True
    #for i_mass_point, mass_point in enumerate(mass_points):
    for iSel, selectionName in enumerate(selectionNames):
        # fullSignalName = signal_name.replace('[masspoint]',mass_point)
        mass_point = selectionName.replace("LQ", "") if "LQ" in selectionName else "0"
        fullSignalName, signalNameForFile = GetFullSignalName(signal_name, mass_point)
        # print "consider fullSignalName={}".format(fullSignalName)
        #selectionName = "LQ" + mass_point
        # this will need to be fixed later if needed
        # else:
        #     # figure out mass point from name. currently the only case for this is RPV stop, where they are like 'Stop_M100_CTau100'
        #     mass = int(signal_name.split("_")[1].replace("M", ""))
        #     if mass < 200:
        #         mass = 200
        #     selectionName = "LQ" + str(mass)
        #     # print 'use selection name=',selectionName,'for fullSignalName=',fullSignalName
        #     doMassPointLoop = False

        if selectionName != "preselection":
            txt_file_name = fullSignalName + ".txt\n"

            card_file.write(txt_file_name + "\n\n")
            card_file.write("imax " + str(n_channels) + "\n")
            card_file.write("jmax " + str(n_background) + "\n")
            card_file.write("kmax " + str(n_systematics) + "\n\n")

            card_file.write("bin bin1\n\n")

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
            d_systematicsApplied[selectionName] = {}
            d_systematicsApplied[selectionName][signalNameForFile] = []
            for syst in systematicsNamesBackground:
                if int(mass_point) > maxLQSelectionMass:
                    selectionNameSyst = "LQ"+str(maxLQSelectionMass)
                else:
                    selectionNameSyst = selectionName
                line = syst + " lnN "
                if syst in systematicsNamesSignal and selectionName != "preselection":
                    if signalNameForFile not in d_systNominals.keys():
                        d_systNominals[signalNameForFile] = {}
                        d_systUpDeltas[signalNameForFile] = {}
                        d_systDownDeltas[signalNameForFile] = {}
                    if syst not in d_systNominals[signalNameForFile].keys():
                        d_systNominals[signalNameForFile][syst] = {}
                        d_systUpDeltas[signalNameForFile][syst] = {}
                        d_systDownDeltas[signalNameForFile][syst] = {}
                    systEntry, deltaOverNominalUp, deltaOverNominalDown = GetSystematicEffectAbs(syst, signalNameForFile, selectionNameSyst, d_signal_systs)
                    thisSigEvts = d_signal_rates[signalNameForFile][selectionNameSyst]
                    thisSigSystUp = deltaOverNominalUp*thisSigEvts
                    thisSigSystDown = deltaOverNominalDown*thisSigEvts
                    d_systNominals[signalNameForFile][syst][selectionNameSyst] = thisSigEvts
                    d_systUpDeltas[signalNameForFile][syst][selectionNameSyst] = thisSigSystUp
                    d_systDownDeltas[signalNameForFile][syst][selectionNameSyst] = thisSigSystDown
                    if systEntry != "-":
                        if "pdf" in syst.lower():
                            d_systematicsApplied[selectionName][signalNameForFile].append(
                                    "PDF: " + GetPDFVariationType(GetBranchTitle(syst, signalNameForFile, selectionNameSyst, d_signal_systs[signalNameForFile])[0])[1])
                        else:
                            d_systematicsApplied[selectionName][signalNameForFile].append(syst)
                    line += str(systEntry) + " "
                else:
                    line += "- "
                for ibkg, background_name in enumerate(background_names):
                    if background_name not in d_systematicsApplied[selectionName]:
                        d_systematicsApplied[selectionName][background_name] = []
                    if background_name not in d_systNominals.keys():
                        d_systNominals[background_name] = {}
                        d_systUpDeltas[background_name] = {}
                        d_systDownDeltas[background_name] = {}
                    if syst not in d_systNominals[background_name].keys():
                        d_systNominals[background_name][syst] = {}
                        d_systUpDeltas[background_name][syst] = {}
                        d_systDownDeltas[background_name][syst] = {}
                    systEntry, deltaOverNominalUp, deltaOverNominalDown = GetSystematicEffectAbs(syst, background_name, selectionNameSyst, d_background_systs)
                    thisBkgEvts = d_background_rates[background_name][selectionNameSyst]
                    thisBkgSystUp = deltaOverNominalUp*thisBkgEvts
                    thisBkgSystDown = deltaOverNominalDown*thisBkgEvts
                    d_systNominals[background_name][syst][selectionNameSyst] = thisBkgEvts
                    d_systUpDeltas[background_name][syst][selectionNameSyst] = thisBkgSystUp
                    d_systDownDeltas[background_name][syst][selectionNameSyst] = thisBkgSystDown
                    if systEntry != "-":
                        if "pdf" in syst.lower():
                            branchTitle = GetBranchTitle(syst, background_name, selectionNameSyst, d_background_systs[background_name])[0]
                            # print "syst={}, background_name={}, selectionNameSyst={}, branchTitle={}".format(
                            #         syst, background_name, selectionNameSyst, branchTitle)
                            if len(branchTitle) > 0:
                                d_systematicsApplied[selectionName][background_name].append(
                                        "PDF: " + GetPDFVariationType(branchTitle)[1])
                            else:
                                d_systematicsApplied[selectionName][background_name].append(
                                        "PDF: flat deltaX/X = {}".format(d_background_systs[background_name][syst][selectionNameSyst]))
                        else:
                            d_systematicsApplied[selectionName][background_name].append(syst)
                    line += str(systEntry) + " "
                    # if "ZJet" in background_name and "800" in selectionNameSyst and "EES" in syst:
                    #     print "INFO: For sample={} selection={} syst={}, thisBkgEvts={}, d_systUpDeltas={}, d_systDownDeltas={}".format(
                    #             background_name, selectionNameSyst, syst, thisBkgEvts, thisBkgSystUp, thisBkgSystDown)
                if selectionName != "preselection":
                    card_file.write(line + "\n")

        # background stat error part
        d_datacardStatErrs[selectionName] = {}
        for i_background_name, background_name in enumerate(background_names):
            thisBkgEvts = d_background_rates[background_name][selectionName]
            thisBkgEvtsErr = d_background_rateErrs[background_name][selectionName]
            thisBkgTotalEntries = d_background_unscaledRates[background_name][selectionName]
            thisBkgEffEntries = thisBkgEvts**2/thisBkgEvtsErr**2 if thisBkgEvtsErr != 0 else 0
            # print "[datacard] INFO:  for selection:", selectionName, " and background:", background_name, " rate=", thisBkgEvts, "+/-", thisBkgEvtsErr, "; effEntries=", thisBkgEffEntries

            if thisBkgEvts != 0.0 and thisBkgEvtsErr != 0.0:
                lnN_f = 1.0 + thisBkgEvtsErr / thisBkgEvts
                gmN_weight = thisBkgEvtsErr**2 / thisBkgEvts
                # if not doEEJJ and background_name=='SingleTop' and int(selectionName.replace('LQ','')) >= 650:
                #   statErr = GetStatErrorFromDict(statErrorsSingleTop,int(selectionName.replace('LQ','')))
                #   lnN_f = 1.0 + statErr/thisBkgEvts
                #   forceLogNormBkgStatUncert = True
            else:
                # print '[datacard] INFO:  for selection:', selectionName, 'and background:', background_name,
                # 'total unscaled events=', thisBkgTotalEntries, 'rate=', thisBkgEvts
                # since we can't compute evts/entries, we find the last selection with at least 1 bkg event and use its scale factor
                lastNonzeroSelection, bkgRate, bkgErr, bkgEvents = GetLastNonzeroSelectionYields(background_name)
                # if background_name != "PhotonJets_Madgraph":
                #     print "[datacard] INFO: for background:", background_name, "at selection:", selectionName, "found last selection:", lastSelectionName, "with", bkgEvents, "+/- {} unscaled MC events. use this for the scale factor.".format(bkgErr)
                gmN_weight = bkgErr**2/bkgRate
                lnN_f = -1
                # if thisBkgTotalEntries != 0.0 and "TTBarFromDATA" in background_name:
                #     print "[datacard] WARN: for background:", background_name, "at selection:", selectionName, "setting thisBkgTotalEntries=", thisBkgTotalEntries, "to zero!"
                #     thisBkgTotalEntries = 0.0

                # # special handling of stat errors for small backgrounds
                # if doEEJJ and background_name=='SingleTop':
                #    gmN_weight = GetStatErrorFromDict(statErrorsSingleTop,int(selectionName.replace('LQ','')))
                # check photon jets
                # if doEEJJ and background_name == "PhotonJets_Madgraph":
                #     gmN_weight = GetStatErrorFromDict(
                #         statErrorsPhotonJets, int(selectionName.replace("LQ", ""))
                #     )

            line_ln = "stat_" + background_name + " lnN -"
            line_gm = (
                "stat_"
                + background_name
                + " gmN "
                + str(int(np.rint(thisBkgEffEntries)))
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

            if thisBkgEffEntries > 10 and not forceGmNNormBkgStatUncert:
                if lnN_f == -1:
                    raise RuntimeError("For background {}, selection {}, had effEntries={} > 10 but scaled rate {} apparently zero.".format(
                        background_name, selectionName, thisBkgEffEntries, thisBkgEvts))
                if selectionName != "preselection":
                    card_file.write(line_ln + "\n")
                d_datacardStatErrs[selectionName][background_name] = ["lnN", thisBkgEvtsErr]
            else:
                if selectionName != "preselection":
                    card_file.write(line_gm + "\n")
                d_datacardStatErrs[selectionName][background_name] = ["gmN", int(np.rint(thisBkgEffEntries)), gmN_weight]

            # if background_name=='TTbar_Madgraph':
            #    print 'selectionName=',selectionName
            #    print 'thisBkgEvts=',thisBkgEvts
            #    print 'thisBkgEvtsErr=',thisBkgEvtsErr
            #    print 'thisBkgTotalEntries=',thisBkgTotalEntries
            #    print 'line_gm=',line_gm

        # signal stat error part
        if selectionName != "preselection":
            thisSigEvts = d_signal_rates[signalNameForFile][selectionName]
            thisSigEvtsErr = d_signal_rateErrs[signalNameForFile][selectionName]
            thisSigEffEntries = thisSigEvts**2/thisSigEvtsErr**2 if thisSigEvtsErr != 0 else 0
            if thisSigEvts != 0.0 and thisSigEvtsErr != 0.0:
                lnN_f = 1.0 + thisSigEvtsErr / thisSigEvts
                gmN_weight = thisSigEvtsErr**2 / thisSigEvts
            else:
                raise RuntimeError(
                        "Found zero signal events or error [{} +/- {}] for the signal {} with selection {}".format(
                            thisSigEvts, thisSigEvtsErr, fullSignalName, selectionName))
            line_ln = "stat_Signal lnN " + str(lnN_f)
            line_gm = (
                "stat_Signal gmN " + str(int(np.rint(thisSigEffEntries))) + " " + str(gmN_weight)
            )
            for i_background_name, background_name in enumerate(background_names):
                line_ln = line_ln + " -"
                line_gm = line_ln + " -"
            if thisSigEffEntries > 10:
                card_file.write(line_ln + "\n")
                d_datacardStatErrs[selectionName][signalNameForFile] = ["lnN", thisSigEvtsErr]
            else:
                card_file.write(line_gm + "\n")
                d_datacardStatErrs[selectionName][signalNameForFile] = ["gmN", int(np.rint(thisSigEffEntries)), gmN_weight]

            # DONE!
            card_file.write("\n\n\n")
        if not doMassPointLoop:
            break

card_file.close()
print "Done"

table_file = open(tables_filePath, "w")

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
            for selection, value in sorted(d_systNominals[sampleName][syst].iteritems(), key=lambda x: float(x[0].replace("LQ", "").replace("preselection", "0"))):
                if selection == "preselection":
                    continue
                massList.append(float(selection.replace("LQ", "")))
                nominals.append(0.0)  # nominals.append(float(value))
                if value > 0:
                    upVariation.append(100*float(d_systUpDeltas[sampleName][syst][selection])/value)
                    downVariation.append(100*float(d_systDownDeltas[sampleName][syst][selection])/value)
                else:
                    lastSelection, rate, err, events = GetLastNonzeroSelectionYields(background_name)
                    value = rate
                    upVariation.append(100*float(d_systUpDeltas[sampleName][syst][lastSelection])/value)
                    downVariation.append(100*float(d_systDownDeltas[sampleName][syst][lastSelection])/value)
                # if "ZJet" in sampleName and "800" in selection and "EES" in syst:
                #     print "INFO: For sample={} selection={} syst={}, nominal={}, d_systUpDeltas={}, d_systDownDeltas={}".format(
                #             sampleName, selection, syst, value, d_systUpDeltas[sampleName][syst][selection],
                #             d_systDownDeltas[sampleName][syst][selection])
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
    print

    # tables
    columnNames = ["Systematic", "Signal (%)", "Background (%)"]
    for selectionName in selectionNames:
        table = []
        for syst in systematicsNamesBackground:
            selectionNameSyst = selectionName
            if selectionName != "preselection":
                massPoint = selectionName.replace("LQ", "")
                if int(massPoint) > maxLQSelectionMass:
                    selectionNameSyst = "LQ"+str(maxLQSelectionMass)
            if syst in systematicsNamesSignal and selectionName != "preselection":
                for i_signal_name, signal_name in enumerate(signal_names):
                    fullSignalName, signalNameForFile = GetFullSignalName(signal_name, massPoint)
                    thisEntry, sigSystDeltaOverNominalUp, sigSystDeltaOverNominalDown = GetSystematicEffectAbs(syst, signalNameForFile, selectionNameSyst, d_signal_systs)
                    if thisEntry == "-":
                        thisSigSystPercent = 0
                        continue
                    thisSigSyst = max(sigSystDeltaOverNominalUp, sigSystDeltaOverNominalDown)
                    thisSigSystPercent = round(100*thisSigSyst, 1)
            else:
                thisSigSystPercent = "  - "
            totalBkgSyst = 0
            totalBkgNominal = 0
            for background_name in background_names:
                # compute effect of this systematic on the total background yield
                totalBkgNominal += d_systNominals[background_name][syst][selectionNameSyst]
                thisEntry, bkgSystDeltaOverNominalUp, bkgSystDeltaOverNominalDown = GetSystematicEffectAbs(syst, background_name, selectionNameSyst, d_background_systs)
                if thisEntry != "-":
                    thisBkgSyst = max(bkgSystDeltaOverNominalUp, bkgSystDeltaOverNominalDown)
                    thisBkgDelta = thisBkgSyst*d_systNominals[background_name][syst][selectionNameSyst]
                    totalBkgSyst += thisBkgDelta*thisBkgDelta
            if totalBkgNominal > 0:
                totalBkgSystPercent = 100*(math.sqrt(totalBkgSyst))/totalBkgNominal
            else:
                totalBkgSystPercent = -1
            table.append([d_systTitles[syst], thisSigSystPercent, totalBkgSystPercent])
        print "Selection: {}".format(selectionName)
        print tabulate(table, headers=columnNames, tablefmt="github", floatfmt=".1f")
        print tabulate(table, headers=columnNames, tablefmt="latex", floatfmt=".1f")
        print
        table_file.write("Selection: {}\n".format(selectionName))
        table_file.write(tabulate(table, headers=columnNames, tablefmt="github", floatfmt=".1f"))
        table_file.write("\n")
        table_file.write(tabulate(table, headers=columnNames, tablefmt="latex", floatfmt=".1f"))
        table_file.write("\n\n")

    # print info on systematics used
    print "For selection LQ300"
    lq300systsDict = d_systematicsApplied["LQ300"]
    print "{0:40}\t{1}".format("sampleName", "systematics applied")
    for sampleName in sorted(lq300systsDict.keys()):
        if "LQ" in sampleName:
            continue
        print "{0:40}\t{1}".format(sampleName, lq300systsDict[sampleName])
    for sampleName in sorted(lq300systsDict.keys()):
        if "LQ" not in sampleName:
            continue
        print "{0:40}\t{1}".format(sampleName, lq300systsDict[sampleName])
    print

    # compute total syst for all backgrounds at each selection
    d_totalSystDeltaXOverX = {}
    for selectionName in selectionNames:
        if selectionName not in d_totalSystDeltaXOverX.keys():
            d_totalSystDeltaXOverX[selectionName] = {}
        for background_name in background_names:
            thisBkgTotalSystOverNom = 0
            for syst in systematicsNamesBackground:
                selectionNameSyst = selectionName
                if selectionName != "preselection":
                    massPoint = selectionName.replace("LQ", "")
                    if int(massPoint) > maxLQSelectionMass:
                        selectionNameSyst = "LQ"+str(maxLQSelectionMass)
                #totalBkgNominal = d_systNominals[background_name][syst][selectionNameSyst]
                thisEntry, bkgSystDeltaOverNominalUp, bkgSystDeltaOverNominalDown = GetSystematicEffectAbs(syst, background_name, selectionNameSyst, d_background_systs)
                if thisEntry != "-":
                    thisBkgSystOverNom = max(bkgSystDeltaOverNominalUp, bkgSystDeltaOverNominalDown)
                    print "INFO: selection={}, background_name={}, syst={}, deltaX/X={}".format(selectionName, background_name, syst, thisBkgSystOverNom)
                    thisBkgTotalSystOverNom += thisBkgSystOverNom*thisBkgSystOverNom
            d_totalSystDeltaXOverX[selectionName][background_name] = math.sqrt(thisBkgTotalSystOverNom)

    with open(systematics_dictFilePath, "w") as systematics_dictFile:
        systematics_dictFile.write(str(d_totalSystDeltaXOverX))
    print "systematics dict written to {}".format(systematics_dictFilePath)

# make final selection tables
if doEEJJ:
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
        "Total BG (stat) (syst)",
        "Data",
    ]
else:
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
        thisSigEvtsErrUp = "-"
        thisSigEvtsErrDown = "-"
        if selectionName != "preselection":
            massPoint = selectionName.replace("LQ", "")
            fullSignalName, signalNameForFile = GetFullSignalName(signal_name, massPoint)
            thisSigEvts = d_signal_rates[signalNameForFile][selectionName]
            thisSigEvtsErrUp, thisSigEvtsErrDown = GetStatErrorsFromDatacard(d_datacardStatErrs[selectionName][signalNameForFile], thisSigEvts)
        # print 'INFO: thisSignal=',fullSignalName,'selection=',selectionName
        # print 'd_data_rates[data]['+selectionName+']'
        if blinded:
            thisDataEvents = -1
        else:
            thisDataEvents = d_data_rates["DATA"][selectionName]
        backgroundEvts = {}
        backgroundEvtsErrUp = {}
        backgroundEvtsErrDown = {}
        totalBackground = 0.0
        totalBackgroundErrStatUp = 0.0
        totalBackgroundErrStatDown = 0.0
        totalBackgroundErrSyst = 0.0
        otherBackground = 0.0
        otherBackgroundErrStatUp = 0.0
        otherBackgroundErrStatDown = 0.0
        for i_background_name, background_name in enumerate(background_names):
            thisBkgEvts = d_background_rates[background_name][selectionName]
            thisBkgEvtsErr = d_background_rateErrs[background_name][selectionName]
            thisBkgEvtsErrUp, thisBkgEvtsErrDown = GetStatErrorsFromDatacard(d_datacardStatErrs[selectionName][background_name], thisBkgEvts)
            # print "GetStatErrorsFromDatacard for selection={}, background={}, thisBkgEvts={} + {} - {}".format(selectionName, background_name, thisBkgEvts, thisBkgEvtsErrUp, thisBkgEvtsErrDown)
            thisBkgTotalEntries = d_background_unscaledRates[background_name][selectionName]
            thisBkgEffEntries = thisBkgEvts**2/thisBkgEvtsErr**2 if thisBkgEvtsErr != 0 else 0
            thisBkgSyst = GetBackgroundSystDeltaOverNominal(background_name, selectionName)
            thisBkgSystErr = thisBkgEvts * thisBkgSyst
            totalBackground += thisBkgEvts
            totalBackgroundErrStatUp += thisBkgEvtsErrUp * thisBkgEvtsErrUp
            totalBackgroundErrStatDown += thisBkgEvtsErrDown * thisBkgEvtsErrDown
            totalBackgroundErrSyst += thisBkgSystErr * thisBkgSystErr
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
        row = [
            selectionName.replace("LQ", ""),
            GetTableEntryStr(
                thisSigEvts, thisSigEvtsErrUp, thisSigEvtsErrDown
            ),  # assumes we always have > 0 signal events
        ]
        for background_name in background_names:
            row.append(
                GetTableEntryStr(
                    backgroundEvts[background_name],
                    backgroundEvtsErrUp[background_name],
                    backgroundEvtsErrDown[background_name],
                )
            )
        row.append(
                GetTableEntryStr(
                    totalBackground,
                    totalBackgroundErrStatUp,
                    totalBackgroundErrStatDown,
                    totalBackgroundErrSyst,
                    )
                )
        row.append(GetTableEntryStr(thisDataEvents))
        t.add_row(row)
        # latex tables
        latexRow = [
            selectionName.replace("LQ", ""),
            GetTableEntryStr(
                thisSigEvts, thisSigEvtsErrUp, thisSigEvtsErrDown, latex=True
            ),  # assumes we always have > 0 signal events
        ]
        latexRowPaper = list(latexRow)
        for background_name in background_names:
            thisEntry = GetTableEntryStr(
                    backgroundEvts[background_name],
                    backgroundEvtsErrUp[background_name],
                    backgroundEvtsErrDown[background_name],
                    latex=True,
                    )
            if background_name not in otherBackgrounds:
                latexRowPaper.append(thisEntry)
            latexRow.append(thisEntry)
        latexRowPaper.append(
                GetTableEntryStr(
                    otherBackground,
                    otherBackgroundErrStatUp,
                    otherBackgroundErrStatDown,
                    latex=True,
                    )
                )
        totalBkgEntry = GetTableEntryStr(
                totalBackground,
                totalBackgroundErrStatUp,
                totalBackgroundErrStatDown,
                totalBackgroundErrSyst,
                True,
                )
        dataEntry = GetTableEntryStr(thisDataEvents, latex=True)
        latexRow.append(totalBkgEntry)
        latexRow.append(dataEntry)
        latexRowPaper.append(totalBkgEntry)
        latexRowPaper.append(dataEntry)

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
table_txt = t.get_string()
table_file.write(table_txt+"\n\n")

print
print "Latex table: AN"
print
table_file.write("Latex table: AN\n")
# latex table -- AN
prelims = [r"\setlength\tabcolsep{2pt}"]
prelims.append(r"\resizebox{\textwidth}{!}{")
prelims.append(r"\begin{tabular}{| l | c | c | c | c | c | c | c | c | c | c | c | c | c |}")
for line in prelims:
    print line
    table_file.write(line+"\n")
headers = GetLatexHeaderFromColumnNames(columnNames)
print headers
print r"\hline"
table_file.write(headers+"\n")
table_file.write(r"\hline\n")
for line in latexRowsAN:
    print (line)
    table_file.write(line+"\n")
ending = r"\end{tabular}}"  # extra } to end resizebox
print ending
table_file.write(ending+"\n")
print
table_file.write("\n")

print
print "Latex table: Paper"
print
table_file.write("Latex table: Paper\n")
# latex table -- Paper
for line in latexRowsPaper:
    print (line)
    table_file.write(line+"\n")
print
table_file.write("\n")

table_file.close()
print "datacard written to {}".format(card_file_path)
print "tables written to {}".format(tables_filePath)
