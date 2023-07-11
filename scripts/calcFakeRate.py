from __future__ import print_function

from ROOT import (
    gROOT,
    TFile,
    TH2F,
    TF1,
    TPad,
    THStack,
    TCanvas,
    TColor,
    kRed,
    kBlue,
    kSpring,
    kAzure,
    kViolet,
    kCyan,
    kOrange,
    kBlack,
    TGraphAsymmErrors,
    TH1D,
    TLegend,
    TObjArray,
    TFractionFitter,
    kWhite,
    kGreen,
    kGray,
)
import ROOT
import numpy as np
import copy
import ctypes
import sys
import os
import math

# 12 distinctive colors
myColors = [
    "#76be79",
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
    "#cca58a",
]
myTColors = [TColor.GetColor(i) for i in myColors]


def GetMyColor(idx):
    return myTColors[idx]


def SetDistinctiveTColorPalette():
    SetTColorPalette(myColors)


def SetTColorPalette(colorList):
    tcolors = [TColor.GetColor(i) for i in colorList]
    # stupid hack to save custom colors, as must have at least 51 new colors defined for them to save
    for r in range(0, 60):
        ci = TColor.GetFreeColorIndex()
        tcolors.append(TColor(ci, r, r + 1, r + 2))
    # gStyle.SetPalette(len(tcolors), np.array(tcolors, dtype=np.int32))


def GetXBinsFromGraph(graph):
    bins = []
    nPoints = graph.GetN()
    for i in range(nPoints):
        bins.append(graph.GetPointX(i) - graph.GetErrorXlow(i))
    bins.append(graph.GetPointX(nPoints - 1) + graph.GetErrorXhigh(nPoints - 1))
    return bins


def GetCanvasTitle(varName, region, jetBin):
    titleStr = analysisYearStr + " FR,"
    if "post" in varName.lower():
        titleStr += " Run >= " + varName[varName.lower().find("post") + 4:] + ","
    elif "pre" in varName.lower():
        titleStr += " Run < " + varName[varName.lower().find("pre") + 3:] + ","
    varNameSplit = varName.split("_")
    for token in varNameSplit:
        if "hem" in token.lower():
            titleStr += " " + token.replace("HEM", "HEM15and16") + ","
    titleStr += " " + region.replace("End2", "Endcap2").replace(
        "End1", "Endcap1"
    ).replace("Bar", "Barrel")
    if jetBin == "":
        titleStr += ", >= 0 jets"
    elif jetBin == "1Jet_":
        titleStr += ", >= 1 jets"
    elif jetBin == "2Jet_":
        titleStr += ", >= 2 jets"
    elif "lte" in jetBin:
        titleStr += ", <= 1 jets"
    else:
        titleStr += ", " + jetBin
    # print "Created canvas title:", titleStr, "from var=", varName, "region=", reg, "jets=", jetBin
    return titleStr


def GetFakeRate(shortVarName, lowEnd, highEnd, reg, jets, histDict, verbose=False):
    verbose = True
    histo_Electrons = histDict[reg]["Electrons"][jets]
    histo_Jets = histDict[reg]["Jets"][jets]
    histo_Data = histDict[reg]["Total"][jets]
    if verbose:
        print("\t\tGetFakeRate: Considering region=", reg)
        print("\t\tGetFakeRate: Considering jets=", jets)
        print(
            "\t\tGetFakeRate: Considering electron Pt:",
            str(lowEnd) + "-" + str(highEnd),
            "GeV",
        )
        print(
            "\t\tGetFakeRate: Considering histo for electrons=>",
            histo_Electrons.GetName(),
            "; histo for jets=>",
            histo_Jets.GetName(),
            "; histo for data=>",
            histo_Data.GetName(),
        )
        sys.stdout.flush()
    if "2D" in histo_Electrons.GetName():
        proj_Electrons = histo_Electrons.ProjectionY(
            "Eles" + shortVarName,
            histo_Electrons.GetXaxis().FindBin(lowEnd),
            histo_Electrons.GetXaxis().FindBin(highEnd) - 1,
        )
        proj_Jets = histo_Jets.ProjectionY(
            "Jets" + shortVarName,
            histo_Jets.GetXaxis().FindBin(lowEnd),
            histo_Jets.GetXaxis().FindBin(highEnd) - 1,
        )
        proj_Data = histo_Data.ProjectionY(
            "Data" + shortVarName,
            histo_Data.GetXaxis().FindBin(lowEnd),
            histo_Data.GetXaxis().FindBin(highEnd) - 1,
        )
    else:
        proj_Electrons = histo_Electrons
        proj_Data = histo_Data
        proj_Jets = histo_Jets
    # proj_JetsEle_ = proj_Jets.Clone()
    # proj_JetsEle_.SetName('JetsEleTrkIso')
    if "TrkIsoHEEP7" in histo_Electrons.GetName():
        upperSBLimit = 20  # GeV
        lowerSBLimit = 10
        upperSRLimit = 5
    elif "PFRelIso" in histo_Electrons.GetName():
        if float(lowEnd) >= 500:
            lowerSBLimit = 0.15
            upperSBLimit = 0.2
        else:
            lowerSBLimit = 0.25
            upperSBLimit = 0.45
        # first take conservative value: largest signal region
        # this will be the looseID cut threshold derived from the lowest pT value
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/CutBasedElectronIdentificationRun2#Offline_selection_criteria_for_V
        if "bar" in reg.lower():
            upperSRLimit = 0.112 + 0.506 / lowEnd
        else:
            upperSRLimit = 0.108 + 0.963 / lowEnd
    else:
        raise RuntimeError(
            "Don't know how to determine SR/SB for histo named: {}".format(
                histo_Electrons.GetName()
            )
        )
    eleSBErr = ctypes.c_double()
    eleSB = proj_Electrons.IntegralAndError(
        proj_Electrons.GetXaxis().FindBin(lowerSBLimit),
        proj_Electrons.GetXaxis().FindBin(upperSBLimit) - 1,
        eleSBErr,
    )
    # data = proj_Data_.Integral(proj_Data_.GetXaxis().FindBin(10),proj_Data_.GetXaxis().FindBin(20)-1)
    dataErr = ctypes.c_double()
    data = proj_Data.IntegralAndError(
        proj_Data.GetXaxis().GetFirst(), proj_Data.GetXaxis().GetLast(), dataErr
    )
    jets_SBErr = ctypes.c_double()
    jets_SB = proj_Jets.IntegralAndError(
        proj_Jets.GetXaxis().FindBin(lowerSBLimit),
        proj_Jets.GetXaxis().FindBin(upperSBLimit) - 1,
        jets_SBErr,
    )
    jets_SRErr = ctypes.c_double()
    jets_SR = proj_Jets.IntegralAndError(
        proj_Jets.GetXaxis().GetFirst(),
        proj_Jets.GetXaxis().FindBin(upperSRLimit) - 1,
        jets_SRErr,
    )
    print("jetsSR = ",jets_SR)
    print("jetsSB = ",jets_SB)
    if jets_SB == 0:
        rJets = 0
        if jets_SR == 0:
            rJetsErr = math.sqrt(jets_SRErr.value ** 2 + jets_SBErr.value ** 2)
        else:
            rJetsErr = jets_SRErr.value / jets_SR
    else:
        rJets = jets_SR / jets_SB
        if jets_SR==0:
            rJetsErr = math.sqrt(jets_SRErr.value ** 2 + jets_SBErr.value ** 2)
        else:
            rJetsErr = (jets_SR / jets_SB) * math.sqrt(
                (jets_SRErr.value / jets_SR) ** 2 + (jets_SBErr.value / jets_SB) ** 2
            )
    numerator = rJets * eleSB
    try:
        numeratorErr = numerator * math.sqrt(
            (rJetsErr / rJets) ** 2 + (eleSBErr.value / eleSB) ** 2
        )
    except ZeroDivisionError as e:
        if eleSB == 0:
            if rJets != 0:
                numeratorErr = numerator * math.sqrt((rJetsErr / rJets) ** 2)
                print(
                    "WARN: GetFakeRate:  Had a ZeroDivisionError in numeratorError; ele==0, so ignore it in error computation"
                )
            else:
                numeratorErr = math.sqrt(rJetsErr ** 2 + eleSBErr.value ** 2)
        elif rJets == 0:
            numeratorErr = numerator * math.sqrt((eleSBErr.value / eleSB) ** 2)
            print(
                "WARN: GetFakeRate:  Had a ZeroDivisionError in numeratorError; rJets==0, so ignore it in error computation"
            )
        else:
            print(
                "ERROR in GetFakeRate:  Had a ZeroDivisionError in numeratorError; rJets=",
                rJets,
                "; eleSB=",
                eleSB,
            )
            sys.stdout.flush()
            raise e
    if verbose:
        print(
            "\t\tGetFakeRate: Considering hists:",
            histo_Electrons.GetName(),
            ",",
            histo_Jets.GetName(),
            ",",
            histo_Data.GetName(),
        )
        # print 'endcap1 N_jet>=0: Nele=',ele,'data=',data,'contam=',ele/data
        # print 'barrel N_jet>=0: Nele=',ele,'data=',data,'contam=',ele/data
        print(
            "\t\tGetFakeRate: nEle'SB=",
            eleSB,
            " +/-",
            eleSBErr.value,
            "; jetsSR=",
            jets_SR,
            "+/-",
            jets_SRErr.value,
            "; jetsSB=",
            jets_SB,
            "+/-",
            jets_SBErr.value,
            "; num=",
            numerator,
            "+/-",
            numeratorErr,
            "; data=",
            data,
            "+/-",
            dataErr.value,
        )
        sys.stdout.flush()
        print("\t\tGetFakeRate: FR=", numerator / data)
        sys.stdout.flush()
    if writeOutput:
        suffix = "_" + reg + "_" + jets + "Pt" + str(lowEnd) + "To" + str(highEnd)
        if not outputFile.cd(shortVarName + "_Electrons"):
            outputFile.mkdir(shortVarName + "_Electrons").cd()
        proj_Electrons.SetName(proj_Electrons.GetName() + suffix)
        proj_Electrons.Write()
        if not outputFile.cd(shortVarName + "_Jets"):
            outputFile.mkdir(shortVarName + "_Jets").cd()
        proj_Jets.SetName(proj_Jets.GetName() + suffix)
        proj_Jets.Write()
        if not outputFile.cd(shortVarName + "_Data"):
            outputFile.mkdir(shortVarName + "_Data").cd()
        proj_Data.SetName(proj_Data.GetName() + suffix)
        proj_Data.Write()
    return numerator, numeratorErr, data, dataErr.value


def GetFakeRateFractionFit(
    shortVarName, lowEnd, highEnd, reg, jets, histDict, verbose=False
):
    verbose = True
    fractionFitXRangeMax = 0.8
    histo2D_Electrons = histDict[reg]["Electrons"][jets]
    histo2D_Jets = histDict[reg]["Jets"][jets]
    histo2D_Data = histDict[reg]["Total"][jets]
    histo2D_DYElectrons = histDict[reg]["ZJets"][jets]
    histo2D_MC = histDict[reg]["MC"][jets]
    if verbose:
        print("\t\tGetFakeRateFractionFit: Considering region=", reg)
        print("\t\tGetFakeRateFractionFit: Considering jets=", jets)
        print(
            "\t\tGetFakeRateFractionFit: Considering electron Pt:",
            str(lowEnd) + "-" + str(highEnd),
            "GeV",
        )
        print(
            "\t\tGetFakeRateFractionFit: Considering histo for electrons=>",
            histo2D_Electrons.GetName(),
            "; histo for jets=>",
            histo2D_Jets.GetName(),
            "; histo for data=>",
            histo2D_Data.GetName(),
        )
        sys.stdout.flush()
    proj_Electrons = histo2D_Electrons.ProjectionY(
        "Eles" + shortVarName,
        histo2D_Electrons.GetXaxis().FindBin(lowEnd),
        histo2D_Electrons.GetXaxis().FindBin(highEnd) - 1,
    )
    proj_Jets = histo2D_Jets.ProjectionY(
        "Jets" + shortVarName,
        histo2D_Jets.GetXaxis().FindBin(lowEnd),
        histo2D_Jets.GetXaxis().FindBin(highEnd) - 1,
    )
    proj_Data = histo2D_Data.ProjectionY(
        "Data" + shortVarName,
        histo2D_Data.GetXaxis().FindBin(lowEnd),
        histo2D_Data.GetXaxis().FindBin(highEnd) - 1,
    )
    proj_DYElectrons = histo2D_DYElectrons.ProjectionY(
        "DYElectrons" + shortVarName,
        histo2D_DYElectrons.GetXaxis().FindBin(lowEnd),
        histo2D_DYElectrons.GetXaxis().FindBin(highEnd) - 1,
    )
    proj_MC = histo2D_MC.ProjectionY(
        "MC" + shortVarName,
        histo2D_MC.GetXaxis().FindBin(lowEnd),
        histo2D_MC.GetXaxis().FindBin(highEnd) - 1,
    )
    if "TrkIsoHEEP7" in histo2D_Electrons.GetName():
        varSRMax = 5  # 5 GeV for TrkIso
    elif "PFRelIso" in histo2D_Electrons.GetName():
        # take conservative value: largest signal region
        # this will be the looseID cut threshold derived from the lowest pT value
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/CutBasedElectronIdentificationRun2#Offline_selection_criteria_for_V
        if "bar" in reg.lower():
            varSRMax = 0.112 + 0.506 / lowEnd
        else:
            varSRMax = 0.108 + 0.963 / lowEnd
    else:
        raise RuntimeError(
            "Don't know how to determine SR/SB for histo named: {}".format(
                histo2D_Electrons.GetName()
            )
        )
    dataErr = ctypes.c_double()
    data = proj_Data.IntegralAndError(1, proj_Data.GetXaxis().GetLast(), dataErr)
    # use all MC for electrons
    proj_MCElectrons = proj_MC
    # MC amc@NLO can have negative bins
    for iBin in range(0, proj_MCElectrons.GetNbinsX() + 1):
        if proj_MCElectrons.GetBinContent(iBin) < 0:
            print(
                "INFO: Found negative value in proj_MCElectrons bin:",
                iBin,
                "; set to zero",
            )
            proj_MCElectrons.SetBinContent(iBin, 0)
    proj_MCElectrons.SetLineColor(kBlue)
    proj_MCElectrons.SetMarkerColor(kBlue)
    proj_MCElectrons.SetMarkerSize(1e-100)
    proj_MCElectrons.SetLineStyle(3)
    proj_MCElectrons.SetLineWidth(2)

    myObjArr = TObjArray(2)
    myObjArr.Add(proj_MCElectrons)
    myObjArr.Add(proj_Jets)
    fracFit = TFractionFitter(proj_Electrons, myObjArr)
    fracFit.Constrain(0, 0.0, 1.0)
    fracFit.Constrain(1, 0.0, 1.0)
    fracFit.GetFitter().Config().ParSettings(0).Set("DYElectrons", 0.5, 0.01, 0, 1.0)
    fracFit.GetFitter().Config().ParSettings(1).Set("Jets", 0.5, 0.01, 0, 1.0)
    fracFit.SetRangeX(1, proj_MCElectrons.FindBin(fractionFitXRangeMax))
    status = fracFit.Fit()
    print("fit status=", status)
    if status.Status() != 0:
        print("Fit failed: fit status is {} and not 0.".format(status.Status()))
        return 0, 0, data, dataErr.value
    fitPlot = fracFit.GetPlot()
    fitPlot.SetLineColor(kGray + 2)
    fitPlot.SetMarkerColor(kGray + 2)
    fitPlot.SetLineStyle(3)
    fitPlot.SetLineWidth(2)
    fitPlot.Draw("esamehist")
    ROOT.SetOwnership(fracFit, False)
    eleFrac = ctypes.c_double()
    eleFracErr = ctypes.c_double()
    fracFit.GetResult(0, eleFrac, eleFracErr)
    # print "scale DYEles by {}*{}/{}={}".format(eleFrac.value, heepPrimeHist.Integral(), dyElesHist.Integral(), eleFrac.value*heepPrimeHist.Integral()/dyElesHist.Integral())
    # proj_MCElectrons.Scale(
    #     eleFrac.value * proj_Electrons.Integral() / proj_MCElectrons.Integral()
    # )
    proj_MCElectrons.Scale(
        eleFrac.value * proj_Electrons.Integral(1, proj_Electrons.FindFixBin(fractionFitXRangeMax)) / proj_MCElectrons.Integral(1, proj_MCElectrons.FindFixBin(fractionFitXRangeMax))
    )
    jetsFrac = ctypes.c_double()
    jetsFracErr = ctypes.c_double()
    fracFit.GetResult(1, jetsFrac, jetsFracErr)
    # print "scale jets by {}*{}/{}={}".format(jetsFrac.value, proj_Electrons.Integral(), jetsHist.Integral(), jetsFrac.value*proj_Electrons.Integral()/jetsHist.Integral())
    proj_Jets.Scale(
        jetsFrac.value * proj_Electrons.Integral(1, proj_Electrons.FindFixBin(fractionFitXRangeMax)) / proj_Jets.Integral(1, proj_Jets.FindFixBin(fractionFitXRangeMax))
    )
    predEleErr = ctypes.c_double()
    predEle = proj_MCElectrons.IntegralAndError(1, proj_MCElectrons.FindFixBin(varSRMax) - 1, predEleErr)
    jetsPredErr = ctypes.c_double()
    jetsPred = proj_Jets.IntegralAndError(1, proj_Jets.FindFixBin(varSRMax) - 1, jetsPredErr)
    if verbose:
        print(
            "\t\tGetFakeRate: Considering hists:",
            histo2D_Electrons.GetName(),
            ",",
            histo2D_Jets.GetName(),
            ",",
            histo2D_Data.GetName(),
        )
        # print 'endcap1 N_jet>=0: Nele=',ele,'data=',data,'contam=',ele/data
        # print 'barrel N_jet>=0: Nele=',ele,'data=',data,'contam=',ele/data
        print(
            "\t\tGetFakeRate: nPredEle=",
            predEle,
            " +/-",
            predEleErr.value,
            "; jets=",
            jetsPred,
            "+/-",
            jetsPredErr.value,
            "; data=",
            data,
            "+/-",
            dataErr.value,
        )
        print("\t\tGetFakeRate: FR=", predEle / data)
    if writeOutput:
        suffix = "_" + reg + "_" + jets + "Pt" + str(lowEnd) + "To" + str(highEnd)
        if not outputFile.cd(shortVarName + "_Electrons"):
            outputFile.mkdir(shortVarName + "_Electrons").cd()
        proj_Electrons.SetName(proj_Electrons.GetName() + suffix)
        proj_Electrons.Write()
        if not outputFile.cd(shortVarName + "_Jets"):
            outputFile.mkdir(shortVarName + "_Jets").cd()
        proj_Jets.SetName(proj_Jets.GetName() + suffix)
        proj_Jets.Write()
        if not outputFile.cd(shortVarName + "_Data"):
            outputFile.mkdir(shortVarName + "_Data").cd()
        proj_Data.SetName(proj_Data.GetName() + suffix)
        proj_Data.Write()
    return jetsPred, jetsPredErr, data, dataErr.value


def GetFakeRateMCSub(shortVarName, lowEnd, highEnd, reg, jets, histDict, verbose=False):
    if verbose:
        print("\t\tGetFakeRateMCSub")
        print("\t\t\tConsidering region=", reg)
        print("\t\t\tConsidering jets=", jets)
        print("\t\t\tConsidering electron Pt:", str(lowEnd) + "-" + str(highEnd), "GeV")
    histo_Electrons = histDict[reg]["Electrons"][jets]
    histo_MC = histDict[reg]["MC"][jets]
    mcHists = [histDict[reg][y][jets] for y in mcNames]
    histo_Data = histDict[reg]["Total"][jets]
    # make TrkIso for DY MC
    histo_DYElectrons = histDict[reg]["ZJets"][jets]
    if verbose:
        print(
            '\t\t\thistDict[{}]["Total"][{}]={}'.format(reg, jets, histo_Data.GetName())
        )
    if "2D" in histo_Electrons.GetName():
        # need to do projections
        proj_Electrons = histo_Electrons.ProjectionY(
            "Eles" + shortVarName,
            histo_Electrons.GetXaxis().FindBin(lowEnd),
            histo_Electrons.GetXaxis().FindBin(highEnd) - 1,
        )
        proj_MC = histo_MC.ProjectionY(
            shortVarName + "MC",
            histo_MC.GetXaxis().FindBin(lowEnd),
            histo_MC.GetXaxis().FindBin(highEnd) - 1,
        )
        mcProjs = [
            histo2D.ProjectionY(
                shortVarName + "Proj" + histo2D.GetName(),
                histo2D.GetXaxis().FindBin(lowEnd),
                histo2D.GetXaxis().FindBin(highEnd) - 1,
            )
            for histo2D in mcHists
        ]
        proj_Data = histo_Data.ProjectionY(
            "Data" + shortVarName,
            histo_Data.GetXaxis().FindBin(lowEnd),
            histo_Data.GetXaxis().FindBin(highEnd) - 1,
        )
        proj_DYElectrons = histo_DYElectrons.ProjectionY(
            "DYEles" + shortVarName,
            histo_DYElectrons.GetXaxis().FindBin(lowEnd),
            histo_DYElectrons.GetXaxis().FindBin(highEnd) - 1,
        )
    else:
        proj_Electrons = histo_Electrons
        proj_MC = histo_MC
        proj_Data = histo_Data
        mcProjs = mcHists
        proj_DYElectrons = histo_DYElectrons
    if "TrkIsoHEEP7" in histo_Electrons.GetName():
        upperSRLimit = 5  # 5 GeV for TrkIso
    elif "PFRelIso" in histo_Electrons.GetName():
        # take conservative value: largest signal region
        # this will be the looseID cut threshold derived from the lowest pT value
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/CutBasedElectronIdentificationRun2#Offline_selection_criteria_for_V
        if "bar" in reg.lower():
            upperSRLimit = 0.112 + 0.506 / lowEnd
        else:
            upperSRLimit = 0.108 + 0.963 / lowEnd
    else:
        raise RuntimeError(
            "Don't know how to determine SR/SB for histo named: {}".format(
                histo_Electrons.GetName()
            )
        )
    upperSRLimitBin = proj_Electrons.GetXaxis().FindBin(upperSRLimit) - 1
    lowerSRLimitBin = proj_Electrons.GetXaxis().GetFirst()
    # denominator is all loose electrons in the region
    dataErr = ctypes.c_double()
    data = proj_Data.IntegralAndError(
        proj_Data.GetXaxis().GetFirst(), proj_Data.GetXaxis().GetLast(), dataErr
    )
    # number of ele' in SR
    eleErr = ctypes.c_double()
    ele = proj_Electrons.IntegralAndError(lowerSRLimitBin, upperSRLimitBin, eleErr)
    # MC for real electron subtraction: real eles in same SR
    realEleErr = ctypes.c_double()
    realEle = proj_MC.IntegralAndError(lowerSRLimitBin, upperSRLimitBin, realEleErr)
    realEleMCList = [
        proj.Integral(lowerSRLimitBin, upperSRLimitBin) for proj in mcProjs
    ]
    realEleMCErrList = [
        ctypes.c_double() for proj in mcProjs
    ]
    for idx, proj in enumerate(mcProjs):
        proj.IntegralAndError(lowerSRLimitBin, upperSRLimitBin, realEleMCErrList[idx])
    numerator = ele - realEle
    numeratorErr = math.sqrt((eleErr.value) ** 2 + (realEleErr.value) ** 2)
    if verbose:
        print(
            "\t\t\tnumer:ele=",
            ele,
            "+/-",
            eleErr.value,
            ";numMC=",
            realEle,
            "+/-",
            realEleErr.value,
            "; numMCSubd=",
            numerator,
            "+/-",
            numeratorErr,
            "; denom:data=",
            data,
            "+/-",
            dataErr.value,
        )
        if realEle > ele:
            print("\t\t\tbreakdown of MC:")
            for i, sample in enumerate(mcNames):
                print("\t\t\t\t" + sample, realEleMCList[i], "+/-", realEleMCErrList[i].value)
            print("histo_Electrons has name:", histo_Electrons.GetName())
            print("histo_Electrons has entries:", histo_Electrons.GetEntries())
        print("\t\t\tFR=", numerator / data)
    if writeOutput:
        suffix = "_" + reg + "_" + jets + "Pt" + str(lowEnd) + "To" + str(highEnd)
        if not outputFile.Get(shortVarName + "_DYElectrons"):
            outputFile.mkdir(shortVarName + "_DYElectrons").cd()
        else:
            outputFile.cd(shortVarName + "_DYElectrons")
        proj_DYElectrons.SetName(proj_DYElectrons.GetName() + suffix)
        proj_DYElectrons.Write()
        if not outputFile.Get(shortVarName + "_MCElectrons"):
            outputFile.mkdir(shortVarName + "_MCElectrons").cd()
        else:
            outputFile.cd(shortVarName + "_MCElectrons")
        proj_MC.SetName(proj_MC.GetName() + suffix)
        proj_MC.Write()
    return numerator, numeratorErr, data, dataErr.value


def MakeFakeRatePlot(
    varName, reg, jets, bins, histDict, verbose=False, dataDriven=True, fractionFit=True
):
    if verbose:
        print(
            "MakeFakeRatePlot:varName=",
            varName,
            "reg=",
            reg,
            "jets=",
            jets,
            "dataDriven=",
            dataDriven,
            "fractionFit=",
            fractionFit
        )
        sys.stdout.flush()
    if reg == "End2":
        bins = ptBinsHighEndcap
    else:
        bins = ptBinsEndcap
    typeString = "mcSub"
    if dataDriven:
        typeString = "dataDrivenRatio"
        if fractionFit:
            typeString = "dataDrivenFracFit"
    histNum = TH1D(
        varName
        + "_num_"
        + reg
        + "_"
        + jets
        + typeString,
        varName
        + "_num_"
        + reg
        + "_"
        + jets
        + typeString,
        len(bins) - 1,
        np.array(bins, dtype=float),
    )
    histDen = TH1D(
        varName
        + "_den_"
        + reg
        + "_"
        + jets
        + typeString,
        varName
        + "_den_"
        + reg
        + "_"
        + jets
        + typeString,
        len(bins) - 1,
        np.array(bins, dtype=float),
    )
    for index, binLow in enumerate(bins):
        if index >= (len(bins) - 1):
            break
        binHigh = bins[index + 1]
        if verbose:
            print("\tMakeFakeRatePlot:look at Pt:", str(binLow) + "-" + str(binHigh))
            sys.stdout.flush()
        shortVarName = varName.split("vs")[0]
        if dataDriven:
            if fractionFit:
                num, numErr, den, denErr = GetFakeRateFractionFit(
                    shortVarName, binLow, binHigh, reg, jets, histDict, verbose
                )
            else:
                num, numErr, den, denErr = GetFakeRate(
                    shortVarName, binLow, binHigh, reg, jets, histDict, verbose
                )
        else:
            num, numErr, den, denErr = GetFakeRateMCSub(
                shortVarName, binLow, binHigh, reg, jets, histDict, verbose
            )
        histNum.SetBinContent(histNum.GetXaxis().FindBin(binLow), num)
        histDen.SetBinContent(histDen.GetXaxis().FindBin(binLow), den)
        histNum.SetBinError(histNum.GetXaxis().FindBin(binLow), numErr)
        histDen.SetBinError(histDen.GetXaxis().FindBin(binLow), denErr)
        if verbose:
            print("\tMakeFakeRatePlot:num=", num, "den=", den)
            # print(
            #     "\tMakeFakeRatePlot:set bin:",
            #     histNum.GetXaxis().FindBin(binLow),
            #     "to",
            #     num,
            # )
            # print(
            #     "\tMakeFakeRatePlot:bin content is:",
            #     histNum.GetBinContent(histNum.GetXaxis().FindBin(binLow)),
            # )
            # sys.stdout.flush()
    # c = TCanvas()
    # c.SetName('num'+reg+jets)
    # c.SetTitle('num'+reg+jets)
    # c.cd()
    # histNum.Draw()
    # c1 = TCanvas()
    # c1.SetName('den'+reg+jets)
    # c1.SetTitle('den'+reg+jets)
    # c1.cd()
    # histDen.Draw()

    graphFR = TGraphAsymmErrors()
    graphFR.BayesDivide(histNum, histDen)
    if analysisYear != 2018:
        graphFR.SetName(
            "fr{reg}_{jets}{method}".format(
                reg=reg, jets=jets, method=typeString
            )
        )
    else:
        # a bit nasty to hardcode the varName in the below
        graphFR.SetName(
            "fr{reg}_{var}_{jets}{method}".format(
                reg=reg,
                var=varName.replace("TrkIsoHEEP7vsHLTPt_", ""),
                jets=jets,
                method=typeString
            )
        )
    return graphFR, histNum, histDen


def MakeFRCanvas(plotList, titleList, canTitle):
    if len(titleList) != len(plotList):
        print(
            "ERROR: titleList and plotList passed into MakeFRCanvas are different lengths!"
        )
    can = TCanvas()
    can.cd()
    can.SetGridy()
    can.SetTitle(canTitle)
    can.SetName(
        "y"
        + canTitle.lower()
        .replace(",", "")
        .replace(" ", "_")
        .replace(">=", "gte")
        .replace("<=", "lte")
    )
    colorList = [1, kSpring - 1, kAzure + 1, kBlue, kGreen]
    markerStyleList = [8, 25, 23, 22, 21]
    for i, plot in enumerate(plotList):
        if i == 0:
            plot.Draw("ap0")
            plot.GetXaxis().SetRangeUser(0, 1000)
            plot.GetXaxis().SetTitle("E_{T} [GeV]")
            if "barrel" in canTitle.lower():
                plot.GetYaxis().SetRangeUser(0, 0.1)
            else:
                plot.GetYaxis().SetRangeUser(0, 0.3)
            plot.GetYaxis().SetNdivisions(510)
            plot.GetYaxis().SetTitle("fake rate")
            plot.SetTitle(canTitle)
        if "graph" not in plot.ClassName().lower():
            plot.SetStats(0)
        plot.SetMarkerColor(colorList[i])
        plot.SetLineColor(colorList[i])
        plot.SetMarkerStyle(markerStyleList[i])
        plot.SetMarkerSize(0.9)
        if i == 0:
            plot.Draw("ap0")
        else:
            plot.Draw("psame0")
    # hsize=0.20
    # vsize=0.35
    # leg = TLegend(0.19,0.18,0.44,0.35)
    leg = TLegend(0.38, 0.71, 0.63, 0.88)
    if len(plotList) > 1:
        leg.SetFillColor(kWhite)
        leg.SetFillStyle(1001)
        leg.SetBorderSize(0)
        leg.SetShadowColor(10)
        leg.SetMargin(0.2)
        leg.SetTextFont(132)
        for i, title in enumerate(titleList):
            leg.AddEntry(plotList[i], title, "lp")
            # print "For canvas titled:", canTitle, ", added entry in legend for plot:", plotList[
            #     i
            # ].GetName(), "setting title to:", title
        leg.Draw()
    can.Modified()
    can.Update()
    return can, leg


def LoadHistosData(histos, varName, sample):
    for reg in detectorRegions:
        histos[reg] = {}
        for eType in electronTypes:
            histos[reg][eType] = {}
            for jet in jetBins:
                hist = tfile.Get(
                    histoBaseName.format(
                        sample=sample, type=eType, region=reg, jets=jet, varName=varName
                    )
                )
                histos[reg][eType][jet] = hist
                # print 'added histo:',hist.GetName(),'with entries:',hist.GetEntries(),'to','['+reg+']['+eType+']['+jet+']'


def LoadHistosMC(histos, varName):
    # we only care about electrons in the MC
    eType = "Electrons"
    for reg in detectorRegions:
        histos[reg]["MC"] = {}
        for name in mcNames:
            histos[reg][name] = {}
        for jet in jetBins:
            mcTotalHist = 0
            for i, name in enumerate(mcNames):
                histName = histoBaseName.format(
                    type=eType,
                    region=reg,
                    jets=jet,
                    sample=mcSamples[i],
                    varName=varName,
                )
                hist = tfile.Get(histName)
                if not hist:
                    raise RuntimeError(
                        "Could not get hist '"
                        + histName
                        + "' from file: "
                        + tfile.GetName()
                    )
                histos[reg][name][jet] = hist
                if not mcTotalHist:
                    # mcTotalHist = hist.Clone()
                    mcTotalHist = copy.deepcopy(hist)
                    mcTotalHist.SetName(
                        histoBaseName.format(
                            type=eType,
                            region=reg,
                            jets=jet,
                            sample="MCTotal",
                            varName=varName,
                        )
                    )
                else:
                    mcTotalHist.Add(hist)
            histos[reg]["MC"][jet] = mcTotalHist


def GetJetBin(histName):
    if "Jet" in histName:
        return histName[histName.find("Jet") - 1: histName.find("Jet") + 3]
    else:
        return "0Jets"


# make FR 2D plot from FR TGraphAsymmErrors returned from MakeFakeRatePlot (frGraph)
# frGraph has x-axis: Pt and y-axis FR
# so we need to know the eta region here
def MakeFR2D(FRhistos, detectorRegions, bins):
    
    etaBins = [0, 1.4442, 1.566, 2.0, 2.5]
    frHist2d = TH2F(
        "test",
        "test",
        len(etaBins) - 1,
        np.array(etaBins, dtype=float),
        len(bins) - 1,
        np.array(bins, dtype=float),
    )
    for reg in detectorRegions:
        if reg == "Bar":
            bins = ptBinsBarrel
            etaToFill = 1
        elif reg == "End1":
            bins = ptBinsEndcap
            etaToFill = 1.7
        elif reg == "End2":
            bins = ptBinsHighEndcap
            etaToFill = 2
        else:
            print("ERROR: could not understand region given:", reg, "; return empty hist")
        # print 'consider frGraph with name {}'.format(frGraph.GetName())
        frGraph = FRhistos[reg]
        if "lte" in frGraph.GetName():
            jets = "lte1Jet_"
        else:
            jets = GetJetBin(frGraph.GetName())
        name = "fr2D_{jets}".format(jets=jets)
        frHist2d.SetNameTitle(name, name)
        frHist2d.GetXaxis().SetTitle("SuperCluster #eta")
        frHist2d.GetYaxis().SetTitle("p_{T} [GeV]")
        for iPoint in range(frGraph.GetN()):
            pt = ctypes.c_double()
            fr = ctypes.c_double()
            frGraph.GetPoint(iPoint, pt, fr)
            etaBin = frHist2d.GetXaxis().FindBin(etaToFill)
            ptBin = frHist2d.GetYaxis().FindBin(pt.value)
            binErr = frGraph.GetErrorY(iPoint)
            frHist2d.SetBinContent(
                etaBin,
                ptBin,
                fr.value,
            )
            frHist2d.SetBinError(
                etaBin,
                ptBin,
                binErr,
            )
#            print("pt: ",pt.value," fr: ",fr.value," binErr: ",binErr)
            #the last two pt bins in end2 need to have the same value bc we combined them
            #In the above code, the very highest ptBin gets filled, so I need to set the
            #next to highest bin to the same value.
            if reg == "End2" and pt.value > 600:
               frHist2d.SetBinContent(
                   etaBin,
                   ptBin-1,
                   fr.value
               )
               frHist2d.SetBinError(
                   etaBin,
                   ptBin-1,
                   binErr,
               )

    return frHist2d


####################################################################################################
# RUN
####################################################################################################
# filename = "$LQDATA/nanoV6/2016/qcdFakeRateCalc/17jul2020/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"
# filename = "$LQDATA/nanoV6/2017/qcdFakeRateCalc/20jul2020/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"
# filename = "$LQDATA/nanoV6/2018/qcdFakeRateCalc/20jul2020/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"
# filename = "$LQDATA/nanoV7/2016/qcdFakeRateCalc/15nov2021/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots_unscaled.root"  # for HEEP-based FR
# filename = "$LQDATA/nanoV7/2016/qcdFakeRateCalc/19nov2021/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"  # also unscaled
# filename = "$LQDATA/nanoV7/2016/qcdFakeRateCalc/26nov2021/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots_unscaled.root"
# filename = "$LQDATA/nanoV7/2016/qcdFakeRateCalc/inconsistenIDs_14mar2022/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"  # test for validation
# filename = "$LQDATA/nanoV7/2016/qcdFakeRateCalc/calcFR_egmoose_19mar2022/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"  # fixed vloose ID for EGMLoose
# filename = "$LQDATA/2016/qcdFakeRateCalc/calcFR_2016Pre_06dec2022/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"
# filename = "/eos/user/e/eipearso/LQ/lqData/2016/Seths_old_data.root"
# filename = "/eos/user/e/eipearso/LQ/lqData/2016/qcdFakeRateCalc/calcFR_2016postMay2023/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"
# filename = "/eos/user/e/eipearso/LQ/lqData/2016/qcdFakeRateCalc/combinePlotsTest/analysisClass_lq_QCD_FakeRateCalculation_plots.root"
filename = "/eos/user/e/eipearso/LQ/lqData/2016/qcdFakeRateCalc/calcFR_2016postJune2023newPrescale/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"

print("Opening file:", filename)
tfile = TFile.Open(filename)
if not tfile or tfile.IsZombie():
    raise RuntimeError("TFile is zombie. Quitting here.")

if "2016" in filename:
    analysisYear = 2016
    if "pre" in filename.lower():
        analysisYearStr = "2016 preVFP"
    if "post" in filename.lower():
        analysisYearStr = "2016 postVFP"
elif "2017" in filename:
    analysisYear = 2017
    analysisYearStr = "2017"
elif "2018" in filename:
    analysisYear = 2018
    analysisYearStr = "2018"

outputFileName = "$LQDATA/2016/qcdFakeRateCalc/calcFR_2016postJune2023newPrescale/fakeRate_plots.root"
pdf_folder = "$LQDATA/2016/qcdFakeRateCalc/calcFR_2016postJune2023newPrescale/fakeRate_plots"
fr2Dfilename = "$LQDATA/2016/qcdFakeRateCalc/calcFR_2016postJune2023newPrescale/fr2D_lte1Jet_postVFP.root"

gROOT.SetBatch(True)
writeOutput = True
doMuz = False  # do Muzamil's plots
plotZprimeFR = True
doMCSubFR = True
doDataDrivenFR = True
doFractionFit = False
doHEEPBasedFR = True

histoBaseName = "histo2D__{sample}__{type}_{region}_{jets}{varName}"
dataSampleName = "QCDFakes_DATA"
electronTypes = ["Jets", "Electrons", "Total"]
# probably eventually expand to BarPlus, BarMinus, etc.
detectorRegions = ["Bar", "End1", "End2"]
regTitleDict = {}
# jetBins = ["", "1Jet_", "2Jet_", "3Jet_"]
#jetBins = ["", "1Jet_", "2Jet_"]
jetBins = ["lte1Jet_"] # NJet <= 1 for the closure test
# for MC
if "2016" in filename:
    mcSamples = [
        "ZJet_amcatnlo_ptBinned_IncStitch",
        # "ZJet_amcatnlo_ptBinned",
        # "ZJet_amcatnlo_Inc",
        # "WJet_amcatnlo_ptBinned",
        # "WJet_Madgraph_Inc",
        "WJet_amcatnlo_Inc",
        "TTbar_powheg",
        "SingleTop",
        "PhotonJets_Madgraph",
        "DIBOSON_nlo",
    ]
else:
    mcSamples = [
        "ZJet_jetAndPtBinned",
        "WJet_amcatnlo_jetBinned",
        "TTbar_powheg",
        "SingleTop",
        "PhotonJets_Madgraph",
        "DIBOSON_nlo",
    ]
mcNames = ["ZJets", "WJets", "TTBar", "ST", "GJets", "Diboson"]

# varNameList = ["TrkIsoHEEP7vsHLTPt_PAS", "TrkIsoHEEP7vsMTenu_PAS"]
if analysisYear != 2018:
    # for heep-based FR
    if doHEEPBasedFR:
        varNameList = ["TrkIsoHEEP7vsHLTPt_PAS"]
    else:
        varNameList = ["PFRelIsoAllvsPt_PAS"]
        # varNameList = ["Full5x5SigmaIEtaIEtavsPt_PAS"]
        # histoBaseName = histoBaseName.replace("histo2D", "histo1D")
else:
    varNameList = [
        "TrkIsoHEEP7vsHLTPt_PAS",
        "TrkIsoHEEP7vsHLTPt_pre319077",
        "TrkIsoHEEP7vsHLTPt_post319077",
        "TrkIsoHEEP7vsHLTPt_noHEM_post319077",
        "TrkIsoHEEP7vsHLTPt_HEMonly_post319077",
    ]

# ptBinsBarrel = [
# #    35,
# #    40,
#     45,
#     50,
#     60,
#     70,
#     80,
#     90,
#     100,
#     110,
#     130,
#     150,
#     170,
#     200,
#     250,
#     300,
#     400,
#     500,
#     600,
#     800,
#     1000,
# ]
# 2016: Photon22, 30, 36, 50, 75, 90, 120, 175
# 2017: Photon25, 33, 50, 75, 90, 120, 150, 175, 200
# 2018: Photon    33, 50, 75, 90, 120, 150, 175, 200
# ptBinsBarrel = [
#      45,
#      60,
#      75,
#      90,
#      105,
#      120,
#      135,
#      150,
#      170,
#      200,
#      250,
#      300,
#      400,
#      500,
#      600,
#      800,
#      1000,
# ]
# ptBinsEndcap = [35, 50, 75, 100, 125, 150, 200, 250, 300, 350, 500, 1000]
# Z' binning -- 2016
# ptBinsEndcap = [36, 47, 50, 62, 75, 82, 90, 105, 120, 140, 175, 200, 225, 250, 300, 350, 400, 500, 600, 1000]
if analysisYear == 2016:
    ptBinsEndcap = [
        36,
        50,
        75,
        90,
        120,
        140,
        175,
        200,
        225,
        250,
        300,
        350,
        400,
        500,
        600,
        1000,
    ]
    ptBinsHighEndcap = [
        36,
        50,
        75,
        90,
        120,
        140,
        175,
        200,
        225,
        250,
        300,
        350,
        400,
        500,
        1000,
    ]

else:
    ptBinsEndcap = [
        36,
        50,
        75,
        90,
        120,
        150,
        175,
        200,
        225,
        250,
        300,
        350,
        400,
        500,
        600,
        1000,
    ]
# 2018
ptBinsEndcapHEM1516Only = [
    36,
    50,
    75,
    90,
    120,
    150,
    175,
    200,
    225,
    250,
    300,
    350,
    400,
    500,
    1000,
]
# use same barrel/endcap binning
ptBinsBarrel = ptBinsEndcap
ptBinsDict = {}
for varName in varNameList:
    ptBinsDict[varName] = {}
    #for reg in detectorRegions:
        #ptBinsDict[varName][reg] = ptBinsEndcap
    ptBinsDict[varName]["End2"] = ptBinsHighEndcap
    ptBinsDict[varName]["End1"] = ptBinsEndcap
    ptBinsDict[varName]["Bar"] = ptBinsEndcap

if analysisYear == 2018:
    ptBinsDict["TrkIsoHEEP7vsHLTPt_HEMonly_post319077"][
        "End1"
    ] = ptBinsEndcapHEM1516Only
    ptBinsDict["TrkIsoHEEP7vsHLTPt_HEMonly_post319077"][
        "End2"
    ] = ptBinsEndcapHEM1516Only

allHistos = {}
for varName in varNameList:
    allHistos[varName] = {}
    LoadHistosData(allHistos[varName], varName, dataSampleName)
    LoadHistosMC(allHistos[varName], varName)

histList = []
myCanvases = []
if writeOutput:
    outputFile = TFile(outputFileName, "recreate")
    outputFile.cd()
# TEST end2 FR plots
# if doMuz:
#     # get Muzamil's hists
#     tfileMuzamilTwoJ = TFile(
#         "/afs/cern.ch/user/m/mbhat/work/public/Fakerate_files_2016/FR2D2JetScEt.root"
#     )
#     tfileMuzamilZeroJ = TFile(
#         "/afs/cern.ch/user/m/mbhat/work/public/Fakerate_files_2016/FR0JET_HLT.root"
#     )
#     muzHist2DZeroJ = tfileMuzamilZeroJ.Get("Endcap_Fake_Rate")
#     muzHist2DZeroJBar = tfileMuzamilZeroJ.Get("Barrel_Fake_Rate")
#     muzHistEnd2ZeroJ = muzHist2DZeroJ.ProjectionX("projMuzEnd2_0Jets", 2, 2)
#     muzHistEnd1ZeroJ = muzHist2DZeroJ.ProjectionX("projMuzEnd1_0Jets", 1, 1)
#     muzHistBarZeroJ = muzHist2DZeroJBar.ProjectionX("projMuzBar_0Jets")
# get Sam's hists
tfileZPrime = TFile(
    "/afs/cern.ch/user/s/scooper/work/public/Leptoquarks/QCDFakeRate/heepV7p0_2016_reminiAOD_noEleTrig_fakerate.root"
)
if tfileZPrime.IsZombie():
    raise RuntimeError("zprime tfile is zombie:", tfileZPrime.GetName())
zprimeHistEnd2ZeroJ = tfileZPrime.Get("frHistEEHigh")
zprimeHistEnd1ZeroJ = tfileZPrime.Get("frHistEELow")
zprimeHistBarZeroJ = tfileZPrime.Get("frHistEB")
histList.extend([zprimeHistEnd2ZeroJ, zprimeHistEnd1ZeroJ, zprimeHistBarZeroJ])
zprimeHistDict = {}
zprimeHistDict["End2"] = {}
zprimeHistDict["End2"][""] = zprimeHistEnd2ZeroJ
zprimeHistDict["End1"] = {}
zprimeHistDict["End1"][""] = zprimeHistEnd1ZeroJ
zprimeHistDict["Bar"] = {}
zprimeHistDict["Bar"][""] = zprimeHistBarZeroJ
# print(zprimeHistBarZeroJ.GetEntries())

# make list of histos to use for FR
# histos = [allHistos[varNameList[0]]]
# if '2018' in filename:
#     histos = allHistos

histDict = {}
numerHistDict = {}
denomHistDict = {}
for varName in allHistos:
    histos = allHistos[varName]
    histDict[varName] = {}
    numerHistDict[varName] = {}
    denomHistDict[varName] = {}
    for reg in detectorRegions:
        histDict[varName][reg] = {}
        numerHistDict[varName][reg] = {}
        denomHistDict[varName][reg] = {}
        bins = ptBinsDict[varName][reg]
        for jetBin in jetBins:
            histDict[varName][reg][jetBin] = {}
            numerHistDict[varName][reg][jetBin] = {}
            denomHistDict[varName][reg][jetBin] = {}
            if doDataDrivenFR:
                histFR, histNum, histDen = MakeFakeRatePlot(
                    varName,
                    reg,
                    jetBin,
                    bins,
                    histos,
                    verbose=True,
                    dataDriven=True,
                    fractionFit=False,
                )
                histDict[varName][reg][jetBin]["data"] = histFR
                numerHistDict[varName][reg][jetBin]["data"] = histNum
                denomHistDict[varName][reg][jetBin]["data"] = histDen
                if doFractionFit:
                    histFR, histNum, histDen = MakeFakeRatePlot(
                        varName,
                        reg,
                        jetBin,
                        bins,
                        histos,
                        verbose=True,
                        dataDriven=True,
                        fractionFit=True,
                    )
                    histDict[varName][reg][jetBin]["dataFracFit"] = histFR
                    numerHistDict[varName][reg][jetBin]["dataFracFit"] = histNum
                    denomHistDict[varName][reg][jetBin]["dataFracFit"] = histDen
            if doMCSubFR:
                histFRMC, histNumMC, histDenMC = MakeFakeRatePlot(
                    varName, reg, jetBin, bins, histos, verbose=True, dataDriven=False
                )
                histDict[varName][reg][jetBin]["mc"] = histFRMC
                numerHistDict[varName][reg][jetBin]["mc"] = histNumMC
                denomHistDict[varName][reg][jetBin]["mc"] = histDenMC
"""
#comparing MC sub and ratio methods
c = TCanvas()
c.cd()
c.SetLogy()
c.SetGridx()
c.SetGridy()
mcSubNum = numerHistDict["TrkIsoHEEP7vsHLTPt_PAS"]["Bar"][""]["mc"]
mcSubNum.SetStats(0)
mcSubNum.SetTitle("Barrel 0Jet")
mcSubNum.SetMinimum(10)
mcSubNum.SetMaximum(1e9)
mcSubNum.SetLineWidth(2)
mcSubNum.GetXaxis().SetTitle("pT (GeV)")
mcSubDenom = denomHistDict["TrkIsoHEEP7vsHLTPt_PAS"]["Bar"][""]["mc"]
mcSubDenom.SetLineWidth(2)
mcSubDenom.SetLineColor(kRed)
dataNum = numerHistDict["TrkIsoHEEP7vsHLTPt_PAS"]["Bar"][""]["data"]
dataNum.SetLineWidth(2)
dataNum.SetLineColor(kGreen+1)
mcSubNum.Draw()
mcSubDenom.Draw("same")
dataNum.Draw("same")
l = TLegend(0.38, 0.71, 0.63, 0.88)
l.AddEntry(mcSubNum, "MC sub numerator","lp")
l.AddEntry(dataNum, "Ratio method numerator", "lp")
l.AddEntry(mcSubDenom, "Denominator","lp")
l.Draw("same")
c.Print(pdf_folder+"/mcSubNumDen_Bar_0Jet.pdf")
"""
for varName in allHistos:
    for reg in detectorRegions:
        for jetBin in jetBins:
            varRegJetHistList = []
            titleList = []
            if doDataDrivenFR:
                varRegJetHistList.append(histDict[varName][reg][jetBin]["data"])
                titleList.append("Ratio")
            if doMCSubFR:
                varRegJetHistList.append(histDict[varName][reg][jetBin]["mc"])
                titleList.append("MCSub")
            if jetBin == "" and (varName == "TrkIsoHEEP7vsHLTPt_PAS" or plotZprimeFR):
                varRegJetHistList.append(zprimeHistDict[reg][jetBin])
                titleList.append("2016 Zprime (E_{T}^{HLT}, HEEP)")
            if doDataDrivenFR and doFractionFit:
                varRegJetHistList.append(histDict[varName][reg][jetBin]["dataFracFit"])
                titleList.append("FractionFit")
            myCanvases.append(
                MakeFRCanvas(
                    varRegJetHistList, titleList, GetCanvasTitle(varName, reg, jetBin)
                )
            )
            histList.extend(varRegJetHistList)


# # for drawing num/den hists
# numDenHistList = [histNumEnd2ZeroJ,histDenEnd2ZeroJ,histNumEnd1ZeroJ,histDenEnd1ZeroJ,histNumBarZeroJ,histDenBarZeroJ]
# for idx,hist in enumerate(numDenHistList):
#    if idx%2 != 0:
#        continue
#    if idx > len(numDenHistList)-2:
#        break
#    print 'consider hist:',hist.GetName(),'and',numDenHistList[idx+1].GetName()
#    c = TCanvas()
#    c.SetName(hist.GetName())
#    c.SetTitle(hist.GetTitle())
#    c.cd()
#    c.SetLogx()
#    c.SetLogy()
#    c.SetGridx()
#    c.SetGridy()
#    numDenHistList[idx+1].SetLineWidth(2)
#    numDenHistList[idx+1].SetLineColor(4)
#    numDenHistList[idx+1].SetMarkerColor(4)
#    numDenHistList[idx+1].Draw()
#    numDenHistList[idx+1].GetYaxis().SetRangeUser(2e-1,1e12)
#    hist.SetLineWidth(2)
#    hist.SetLineColor(2)
#    hist.SetMarkerColor(2)
#    hist.Draw('sames')

if writeOutput:
    outputFile.cd()
    if not os.path.isdir(pdf_folder) and pdf_folder != "":
        "Making directory", pdf_folder
        os.mkdir(pdf_folder)
for canLeg in myCanvases:
    canv = canLeg[0]
    canv.Draw()  # canvas
    # canLeg[-1][1].Draw() #legend
    if writeOutput:
        canv.Write()
        canv.Print(pdf_folder + "/" + canv.GetName() + ".pdf")


#Make 2D fake rate plots:
frGraphs = {}
fr2Dfile = TFile(fr2Dfilename, "recreate")
fr2Dfile.cd()

c = TCanvas()
for jets in jetBins:
    for reg in detectorRegions:
        frGraphs[reg] = histDict["TrkIsoHEEP7vsHLTPt_PAS"][reg][jets]["data"]       
    if jets=='':
        plotTitle = "fake rate 0Jet_"
        pdfTitle = pdf_folder + "/FakeRate2D_0Jet_.pdf"
        canvasName = "fakeRate2D_0Jet_"
    else:
        plotTitle = "fake rate " + jets
        pdfTitle = pdf_folder + "/FakeRate2D_"+jets+".pdf"
        canvasName = "fakeRate2D_"+jets
    c.SetName(canvasName)
    fakeRate2D = MakeFR2D(frGraphs,detectorRegions,ptBinsEndcap)
    c.SetRightMargin(0.13)
    fakeRate2D.SetStats(0)
    fakeRate2D.Draw("colzTEXT")
    fakeRate2D.SetTitle(plotTitle)
    fakeRate2D.GetYaxis().SetRangeUser(25,1000)
    c.Update()
    c.Write()
    c.Print(pdfTitle)
    fakeRate2D.Write()
fr2Dfile.Close()

#make stack plots for MC
for reg in detectorRegions:
    stack = THStack()
    canv = TCanvas()
    canv.cd()
    canv.SetLogy()
    histsForStack = {}
    for name in mcNames:
        hist = histos[reg][name][""]
        print("making stack plot hist for "+name)
        projection = hist.ProjectionX(
            "Et"+name,
             hist.GetYaxis().FindBin(0),
             hist.GetYaxis().FindBin(5) -1,
        )
        projection.Rebin(20)
        histsForStack[name] = projection

    histsForStack["ZJets"].SetLineColor(kCyan+1)
    histsForStack["ZJets"].SetFillColor(kCyan+1)
    histsForStack["ZJets"].SetLineWidth(2)
    histsForStack["ZJets"].SetMarkerColor(kCyan+1)
    stack.Add(histsForStack["ZJets"])

    histsForStack["WJets"].SetLineColor(kRed)
    histsForStack["WJets"].SetFillColor(kRed)
    histsForStack["WJets"].SetLineWidth(2)
    histsForStack["WJets"].SetMarkerColor(kRed)
    stack.Add(histsForStack["WJets"])

    histsForStack["TTBar"].SetLineColor(kGray)
    histsForStack["TTBar"].SetFillColor(kGray)
    histsForStack["TTBar"].SetLineWidth(2)
    histsForStack["TTBar"].SetMarkerColor(kGray)
    stack.Add(histsForStack["TTBar"])

    histsForStack["ST"].SetLineColor(kBlue)
    histsForStack["ST"].SetFillColor(kBlue)
    histsForStack["ST"].SetLineWidth(2)
    histsForStack["ST"].SetMarkerColor(kBlue)
    stack.Add(histsForStack["ST"])

    histsForStack["GJets"].SetLineColor(kViolet+6)
    histsForStack["GJets"].SetFillColor(kViolet+6)
    histsForStack["GJets"].SetLineWidth(2)
    histsForStack["GJets"].SetMarkerColor(kViolet+6)
    stack.Add(histsForStack["GJets"])

    histsForStack["Diboson"].SetLineColor(kBlack)
    histsForStack["Diboson"].SetFillColor(kBlack)
    histsForStack["Diboson"].SetLineWidth(2)
    histsForStack["Diboson"].SetMarkerColor(kBlack)
    stack.Add(histsForStack["Diboson"])

    stack.SetMinimum(1e-1)
    stack.SetMaximum(1e8)
    stack.Draw("hist")
    stack.GetXaxis().SetTitle("pT [GeV]")
    stack.SetTitle(reg+" 0Jet")
    stack.Draw("hist")

    histo_data_prime = histos[reg]["Electrons"][""]
    projection_data_prime = histo_data_prime.ProjectionX(
        "EtDataPrime",
         histo_data_prime.GetYaxis().FindBin(0),
         histo_data_prime.GetYaxis().FindBin(5) - 1,
    )
    projection_data_prime.Rebin(20)
    projection_data_prime.SetLineColor(kGreen)
    projection_data_prime.SetMarkerColor(kGreen)
    projection_data_prime.SetLineWidth(2)
    projection_data_prime.Draw("same")

    histo_data_loose = histos[reg]["Total"][""]
    projection_data_loose = histo_data_loose.ProjectionX(
        "EtDataLoose",
        histo_data_loose.GetYaxis().FindBin(0),
        histo_data_loose.GetYaxis().FindBin(5) - 1,
    )
    projection_data_loose.Rebin(20)
    projection_data_loose.SetMaximum(1e8)
    projection_data_loose.SetLineColor(kGreen+2)
    projection_data_loose.SetMarkerColor(kGreen+2)
    projection_data_loose.SetLineWidth(2)
    projection_data_loose.Draw("same")

#    mcTotProj.Draw("same")

    l = TLegend(0.38, 0.71, 0.63, 0.88)
    for name in mcNames:
        l.AddEntry(histsForStack[name], name, "lp")
    l.AddEntry(projection_data_prime, "ele' electrons", "lp")
    l.AddEntry(projection_data_loose, "loose electrons","lp")
    l.Draw("same")
    canv.Update()
    canv.Print(pdf_folder+"/stackPlot"+reg+".pdf")

'''
##################################################
# var vs PU plot
##################################################
SetDistinctiveTColorPalette()
varName = "PFRelIsoAllvsNvtx_PAS"
sampleNameData = "QCDFakes_DATA"
categories = ["Total", "Electrons", "Jets"]
histoName = "histo2D__{sampleName}__{category}_{region}_{jets}" + varName
shortVarName = varName.split("vs")[0]
for sample in mcSamples:
    if "zjet" in sample.lower():
        sampleNameZJet = sample
histosPU = {}
puBins = [1, 10, 20, 30, 40, 50, 60]
for reg in detectorRegions:
    # histosPt[reg] = {}
    # histosPt[reg]["ZElectrons"] = {}
    # histosPt[reg]["WElectrons"] = {}
    # histosPt[reg]["DataLooseElectrons"] = {}
    # histosPt[reg]["DataElectrons"] = {}
    for jet in jetBins:
        for cat in categories:
            histsThisCategory = {}
            histsThisCategory[sampleNameZJet] = []
            histsThisCategory[sampleNameData] = []
            for idx, puBin in enumerate(puBins):
                histo2D = tfile.Get(
                    histoName.format(
                        region=reg, jets=jet, sampleName=sampleNameZJet, category=cat
                    )
                )
                profName = histo2D.GetName().replace("histo2D__", "")
                highPUBin = puBins[idx + 1]
                # FIXME name is incorrect
                proj_Z = histo2D.ProjectionY(
                    profName + "_PU" + str(puBin) + "to" + str(highPUBin),
                    histo2D.GetXaxis().FindBin(puBin),
                    histo2D.GetXaxis().FindBin(highPUBin) - 1,
                )
                histsThisCategory[sampleNameZJet].append(proj_Z)
                # histosPt[reg]["ZElectrons"][jet] = proj_MC
                # histosPt[reg]["WElectrons"][jet] = proj_MC
                histo2D = tfile.Get(
                    histoName.format(
                        region=reg, jets=jet, sampleName=sampleNameData, category=cat
                    )
                )
                profName = histo2D.GetName().replace("histo2D__", "")
                proj_data = histo2D.ProjectionY(
                    profName + "_PU" + str(puBin) + "to" + str(highPUBin),
                    histo2D.GetXaxis().FindBin(puBin),
                    histo2D.GetXaxis().FindBin(highPUBin) - 1,
                )
                histsThisCategory[sampleNameData].append(proj_data)
                # print "append proj_data with name={}".format(proj_data.GetName())
                if writeOutput:
                    # if not outputFile.cd(shortVarName+"_Electrons_PU"):
                    #     outputFile.mkdir(shortVarName+"_Electrons_PU").cd()
                    if not outputFile.cd(shortVarName + "_profiles_PU"):
                        outputFile.mkdir(shortVarName + "_profiles_PU").cd()
                    proj_Z.Write()
                    proj_data.Write()
                if idx >= len(puBins) - 2:
                    break
            if writeOutput:
                for sample in histsThisCategory.keys():
                    can = TCanvas("", "", 1400, 800)
                    can.SetName(sample + "_" + reg + "_" + jet + cat)
                    can.SetTitle(sample + "_" + reg + "_" + jet + cat)
                    can.cd()
                    can.SetLogy()
                    can.SetTitle(
                        (
                            "puOverlay_{sample}_{category}_{region}_{jets}" + varName
                        ).format(sample=sample, category=cat, region=reg, jets=jet)
                    )
                    leg = TLegend(0.65, 0.71, 0.89, 0.88)
                    leg.SetFillColor(kWhite)
                    leg.SetFillStyle(1001)
                    leg.SetBorderSize(0)
                    leg.SetShadowColor(10)
                    leg.SetMargin(0.2)
                    # leg.SetTextFont(132)
                    for idx, hist in enumerate(histsThisCategory[sample]):
                        # print "for hist={} GetMyColor({})={}".format(hist.GetName(), idx, GetMyColor(idx))
                        hist.Rebin(8)
                        hist.SetStats(0)
                        hist.GetXaxis().SetTitle(shortVarName)
                        hist.GetXaxis().SetTitleOffset(1.1)
                        hist.SetTitle("")
                        hist.SetLineColor(GetMyColor(idx))
                        hist.SetMarkerColor(GetMyColor(idx))
                        if idx == 0:
                            hist.DrawNormalized()
                        else:
                            hist.DrawNormalized("same")
                        leg.AddEntry(hist, hist.GetName(), "lp")
                    leg.Draw()
                    can.Write()
                    can.Print(pdf_folder + "/" + can.GetName() + ".pdf")
'''
##################################################
# make Et plot
##################################################
'''
histoNameZ = 'histo2D__ZJet_amcatnlo_ptBinned__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
histoNameW = 'histo2D__WJet_amcatnlo_ptBinned__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
# histoNameData = 'histo2D__QCDFakes_DATA__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
histoNameDataLoose = "histo2D__QCDFakes_DATA__Total_{region}_{jets}TrkIsoHEEP7vsPt_PAS"
histosPt = {}
for reg in detectorRegions:
    histosPt[reg] = {}
    histosPt[reg]["ZElectrons"] = {}
    histosPt[reg]["WElectrons"] = {}
    histosPt[reg]["DataLooseElectrons"] = {}
    histosPt[reg]["DataElectrons"] = {}
    for jet in jetBins:
#        histo2D_MC = tfile.Get(histoNameZ.format(region=reg,jets=jet))
        histo2D_MC = histos[reg]["ZJets"][jet]
        proj_MC = histo2D_MC.ProjectionX(
            "EtZ",
            histo2D_MC.GetYaxis().FindBin(0),
            histo2D_MC.GetYaxis().FindBin(5) - 1,
        )
        histosPt[reg]["ZElectrons"][jet] = proj_MC
#        histo2D_MC = tfile.Get(histoNameW.format(region=reg,jets=jet))
        histo2D_MC = histos[reg]["WJets"][jet]
        proj_MC = histo2D_MC.ProjectionX(
            "EtW",
            histo2D_MC.GetYaxis().FindBin(0),
            histo2D_MC.GetYaxis().FindBin(5) - 1,
        )
        histosPt[reg]["WElectrons"][jet] = proj_MC
        histo2D_data = tfile.Get(histoNameDataLoose.format(region=reg, jets=jet))
        proj_data = histo2D_data.ProjectionX(
            "EtDataLoose",
            histo2D_data.GetYaxis().FindBin(0),
            histo2D_data.GetYaxis().FindBin(5) - 1,
        )
        histosPt[reg]["DataLooseElectrons"][jet] = proj_data
        # histo2D_data = tfile.Get(histoNameData.format(region=reg,jets=jet))
        histo2D_data = histos[reg]["Electrons"][jet]
        if "2D" in histo2D_data.GetName():
            proj_data = histo2D_data.ProjectionX(
                "EtData",
                histo2D_data.GetYaxis().FindBin(0),
                histo2D_data.GetYaxis().FindBin(5) - 1,
            )
        else:
            proj_data = histo2D_data
        histosPt[reg]["DataElectrons"][jet] = proj_data
        # print 'added histo:',hist.GetName(),' to ','['+reg+']['+eType+']['+jet+']'

canvasEt = TCanvas()
canvasEt.cd()
canvasEt.SetLogy()
reg = "Bar"
jets = ""
rebinFactor = 20
histData = histosPt[reg]["DataElectrons"][jets]
histData.Rebin(rebinFactor)
histDataLoose = histosPt[reg]["DataLooseElectrons"][jets]
histDataLoose.Rebin(rebinFactor)
histDataLoose.SetMarkerColor(kRed)
histDataLoose.SetLineColor(kRed)
histDataLoose.SetLineStyle(2)

stack = THStack()
stack.SetTitle("Barrel 0Jet")
histZ = histosPt[reg]["ZElectrons"][jets]
histZ.Rebin(rebinFactor)
histZ.SetLineColor(7)
histZ.SetLineWidth(2)
histZ.SetFillColor(7)
histZ.SetMarkerColor(7)
stack.Add(histZ)
histW = histosPt[reg]["WElectrons"][jets]
# print 'W entries:',histW.GetEntries()
histW.Rebin(rebinFactor)
histW.SetLineColor(kBlue)
histW.SetLineWidth(2)
histW.SetFillColor(kBlue)
histW.SetMarkerColor(kBlue)
stack.Add(histW)
stack.Draw("hist")
stack.SetMaximum(1.2 * histData.GetMaximum())
stack.SetMinimum(1e-1)
stack.GetXaxis().SetTitle("Et [GeV]")
stack.Draw("hist")
histData.Draw("psame")
histDataLoose.Draw("psame")
legEt = TLegend(0.38, 0.71, 0.63, 0.88)
legEt.SetFillColor(kWhite)
legEt.SetFillStyle(1001)
legEt.SetBorderSize(0)
legEt.SetShadowColor(10)
legEt.SetMargin(0.2)
legEt.SetTextFont(132)
legEt.AddEntry(histZ, "MC (ZJets)", "lp")
legEt.AddEntry(histW, "MC (WJets)", "lp")
legEt.AddEntry(histData, "Data (ele' electrons)", "lp")
legEt.AddEntry(histDataLoose, "Data (loose electrons)", "lp")
legEt.Draw()
canvasEt.Modified()
canvasEt.Update()
canvasEt.Print(pdf_folder+"/stackPlot.pdf")
'''
#low = 800
#high = 1000
#print("integrals in 800-1000:")
#print(
#    "dataLoose=",
#    histDataLoose.Integral(histDataLoose.FindBin(low), histDataLoose.FindBin(high) - 1),
#)
#print("dataEle=", histData.Integral(histData.FindBin(low), histData.FindBin(high) - 1))


if writeOutput:
    outputFile.cd()
    endcap2dHists = []
    for hist in histList:
        hist.Write()
        if "template" in hist.GetName():
            reg = hist.GetName()[2: hist.GetName().find("_")]
            bins = GetXBinsFromGraph(hist)
            hist2d = MakeFR2D(hist, reg, bins)
            if "End" in hist2d.GetName():
                endcap2dHists.append(hist2d)
            else:
                hist2d.Write()
    histNamesDone = []
    for i in range(len(endcap2dHists)):
        hist = endcap2dHists[i]
        name = hist.GetName()
        if name in histNamesDone:
            continue
        reg = name[2: name.find("_")]
        jets = GetJetBin(name)
        for j in range(len(endcap2dHists)):
            hist2 = endcap2dHists[j]
            name2 = hist2.GetName()
            if name == name2:
                continue
            reg2 = name2[2: name2.find("_")]
            jets2 = GetJetBin(name2)
            if reg == reg2 and jets == jets2:
                hist.Add(hist2)
                histNamesDone.extend([name, name2])
                name = name.replace("End1", "End")
                name = name.replace("End2", "End")
                hist.SetNameTitle(name, name)
                hist.Write()
                break

    outputFile.Close()

# histo2D_DY_zeroJ = tfile.Get('histo2D__ZJet_amcatnlo_ptBinned__Electrons_End1_TrkIsoHEEP7vsPt_PAS')
# histo2D_Jets_zeroJ = tfile.Get('histo2D__QCDFakes_DATA__Jets_End1_TrkIsoHEEP7vsPt_PAS')
# histo2D_Electrons_zeroJ = tfile.Get('histo2D__QCDFakes_DATA__Electrons_End1_TrkIsoHEEP7vsPt_PAS')
# histo2D_Data_zeroJ = tfile.Get('histo2D__QCDFakes_DATA__Total_End1_TrkIsoHEEP7vsPt_PAS')
##histo2D_DY_zeroJ = tfile.Get('histo2D__ZJet_amcatnlo_ptBinned__Electrons_bar_TrkIsoHEEP7vsPt_PAS')
##histo2D_Jets_zeroJ = tfile.Get('histo2D__QCDFakes_DATA__Jets_Bar_TrkIsoHEEP7vsPt_PAS')
##histo2D_Electrons_zeroJ = tfile.Get('histo2D__QCDFakes_DATA__Electrons_Bar_TrkIsoHEEP7vsPt_PAS')
##histo2D_Data_zeroJ = tfile.Get('histo2D__QCDFakes_DATA__Total_Bar_TrkIsoHEEP7vsPt_PAS')
#
# lowEnd=350 # GeV
# highEnd=500
##lowEnd=60 # GeV
##highEnd=70
# print
# print
# print 'Template plot section'
# print
# print 'Considering electron Pt:',str(lowEnd)+'-'+str(highEnd),'GeV'
# proj_DY_zeroJ = histo2D_DY_zeroJ.ProjectionY('DYZeroJTrkIso',histo2D_DY_zeroJ.GetXaxis().FindBin(lowEnd),histo2D_DY_zeroJ.GetXaxis().FindBin(highEnd))
# proj_Electrons_zeroJ = histo2D_Electrons_zeroJ.ProjectionY('ElesZeroJTrkIso',histo2D_Electrons_zeroJ.GetXaxis().FindBin(lowEnd),histo2D_Electrons_zeroJ.GetXaxis().FindBin(highEnd)-1)
# proj_Jets_zeroJ = histo2D_Jets_zeroJ.ProjectionY('JetsZeroJTrkIso',histo2D_Jets_zeroJ.GetXaxis().FindBin(lowEnd),histo2D_Jets_zeroJ.GetXaxis().FindBin(highEnd)-1)
# proj_Data_zeroJ = histo2D_Data_zeroJ.ProjectionY('DataZeroJTrkIso',histo2D_Data_zeroJ.GetXaxis().FindBin(lowEnd),histo2D_Data_zeroJ.GetXaxis().FindBin(highEnd)-1)
# print 'Using bin range:',histo2D_Data_zeroJ.GetXaxis().FindBin(lowEnd),'to',histo2D_Data_zeroJ.GetXaxis().FindBin(highEnd)-1
# can1 = TCanvas()
# can1.cd()
# proj_Data_zeroJ.Draw()
#
# proj_DY_zeroJ.SetLineColor(kBlue)
# proj_DY_zeroJ.SetMarkerColor(kBlue)
# proj_DY_zeroJ.SetLineStyle(2)
# proj_DY_zeroJ.SetLineWidth(2)
# proj_Jets_zeroJ.SetLineColor(kRed)
# proj_Jets_zeroJ.SetMarkerColor(kRed)
# proj_Jets_zeroJ.SetLineStyle(2)
# proj_Jets_zeroJ.SetLineWidth(2)
# proj_Data_zeroJ.SetLineColor(kBlue)
# proj_Data_zeroJ.SetMarkerColor(kBlue)
#
## ugly copy paste
# histo2D_DY_twoJ = tfile.Get('histo2D__ZJet_amcatnlo_ptBinned__Electrons_End1_2Jet_TrkIsoHEEP7vsPt_PAS')
# histo2D_Jets_twoJ = tfile.Get('histo2D__QCDFakes_DATA__Jets_End1_2Jet_TrkIsoHEEP7vsPt_PAS')
# histo2D_Electrons_twoJ = tfile.Get('histo2D__QCDFakes_DATA__Electrons_End1_2Jet_TrkIsoHEEP7vsPt_PAS')
# histo2D_Data_twoJ = tfile.Get('histo2D__QCDFakes_DATA__Total_End1_2Jet_TrkIsoHEEP7vsPt_PAS')
##histo2D_Jets_twoJ = tfile.Get('histo2D__QCDFakes_DATA__Jets_Bar_2Jet_TrkIsoHEEP7vsPt_PAS')
##histo2D_Electrons_twoJ = tfile.Get('histo2D__QCDFakes_DATA__Electrons_Bar_2Jet_TrkIsoHEEP7vsPt_PAS')
##histo2D_Data_twoJ = tfile.Get('histo2D__QCDFakes_DATA__Total_Bar_2Jet_TrkIsoHEEP7vsPt_PAS')
#
# proj_DY_twoJ = histo2D_DY_twoJ.ProjectionY('DYTwoJTrkIso',histo2D_DY_twoJ.GetXaxis().FindBin(lowEnd),histo2D_DY_twoJ.GetXaxis().FindBin(highEnd))
# proj_Electrons_twoJ = histo2D_Electrons_twoJ.ProjectionY('ElesTwoJTrkIso',histo2D_Electrons_twoJ.GetXaxis().FindBin(lowEnd),histo2D_Electrons_twoJ.GetXaxis().FindBin(highEnd)-1)
# proj_Jets_twoJ = histo2D_Jets_twoJ.ProjectionY('JetsTwoJTrkIso',histo2D_Jets_twoJ.GetXaxis().FindBin(lowEnd),histo2D_Jets_twoJ.GetXaxis().FindBin(highEnd)-1)
# proj_Data_twoJ = histo2D_Data_twoJ.ProjectionY('DataTwoJTrkIso',histo2D_Data_twoJ.GetXaxis().FindBin(lowEnd),histo2D_Data_twoJ.GetXaxis().FindBin(highEnd)-1)
#
# proj_DY_twoJ.SetLineColor(kBlue)
# proj_DY_twoJ.SetMarkerColor(kBlue)
# proj_DY_twoJ.SetLineStyle(2)
# proj_DY_twoJ.SetLineWidth(2)
# proj_Jets_twoJ.SetLineColor(kRed)
# proj_Jets_twoJ.SetMarkerColor(kRed)
# proj_Jets_twoJ.SetLineStyle(2)
# proj_Jets_twoJ.SetLineWidth(2)
# proj_Data_twoJ.SetLineColor(kBlue)
# proj_Data_twoJ.SetMarkerColor(kBlue)
#
#
# dyZeroJ = proj_DY_zeroJ.Integral(proj_DY_zeroJ.GetXaxis().FindBin(10),proj_DY_zeroJ.GetXaxis().FindBin(20)-1)
# eleZeroJ = proj_Electrons_zeroJ.Integral(proj_Electrons_zeroJ.GetXaxis().FindBin(10),proj_Electrons_zeroJ.GetXaxis().FindBin(20)-1)
# dataZeroJ_SB = proj_Data_zeroJ.Integral(proj_Data_zeroJ.GetXaxis().FindBin(10),proj_Data_zeroJ.GetXaxis().FindBin(20)-1)
# dataZeroJ = proj_Data_zeroJ.Integral()
# jetsZeroJ_SB = proj_Jets_zeroJ.Integral(proj_Jets_zeroJ.GetXaxis().FindBin(10),proj_Jets_zeroJ.GetXaxis().FindBin(20)-1)
# jetsZeroJ_SR = proj_Jets_zeroJ.Integral(proj_Jets_zeroJ.GetXaxis().FindBin(0),proj_Jets_zeroJ.GetXaxis().FindBin(5)-1)
##print 'endcap1 N_jet>=0: Nele=',eleZeroJ,'data=',dataZeroJ,'contam=',eleZeroJ/dataZeroJ
# print 'barrel N_jet>=0: Nele=',eleZeroJ,'data=',dataZeroJ,'contam=',eleZeroJ/dataZeroJ_SB
# print 'barrel N_jet>=0: nHEEPprime=',eleZeroJ,'jetsSR=',jetsZeroJ_SR,'jetsSB=',jetsZeroJ_SB,'data=',dataZeroJ
# print 'FR=',((jetsZeroJ_SR/jetsZeroJ_SB) * eleZeroJ)/dataZeroJ
#
# dyTwoJ = proj_DY_twoJ.Integral(proj_DY_twoJ.GetXaxis().FindBin(10),proj_DY_twoJ.GetXaxis().FindBin(20)-1)
# eleTwoJ = proj_Electrons_twoJ.Integral(proj_Electrons_twoJ.GetXaxis().FindBin(10),proj_Electrons_twoJ.GetXaxis().FindBin(20)-1)
# dataTwoJ_SB = proj_Data_twoJ.Integral(proj_Data_twoJ.GetXaxis().FindBin(10),proj_Data_twoJ.GetXaxis().FindBin(20)-1)
# dataTwoJ = proj_Data_twoJ.Integral()
# jetsTwoJ_SB = proj_Jets_twoJ.Integral(proj_Jets_twoJ.GetXaxis().FindBin(10),proj_Jets_twoJ.GetXaxis().FindBin(20)-1)
# jetsTwoJ_SR = proj_Jets_twoJ.Integral(proj_Jets_twoJ.GetXaxis().FindBin(0),proj_Jets_twoJ.GetXaxis().FindBin(5)-1)
##print 'endcap1 N_jet>=2: Nele=',eleTwoJ,'data=',dataTwoJ,'contam=',eleTwoJ/dataTwoJ
# print 'barrel N_jet>=2: Nele=',eleTwoJ,'data=',dataTwoJ,'contam=',eleTwoJ/dataTwoJ_SB
# print 'barrel N_jet>=2: nHEEPprime=',eleTwoJ,'jetsSR=',jetsTwoJ_SR,'jetsSB=',jetsTwoJ_SB,'data=',dataTwoJ
# print 'FR=',((jetsTwoJ_SR/jetsTwoJ_SB) * eleTwoJ)/dataTwoJ
#
#
# can = TCanvas()
# can.cd()
# can.SetLogy()
# proj_Jets_zeroJ.Scale(eleZeroJ/jetsZeroJ_SB)
# proj_JetsEle_zeroJ = proj_Jets_zeroJ.Clone()
# proj_JetsEle_zeroJ.SetName('JetsEleZeroJTrkIso')
# proj_JetsEle_zeroJ.Add(proj_Electrons_zeroJ)
# proj_JetsEle_zeroJ.SetLineStyle(2)
# proj_JetsEle_zeroJ.SetLineWidth(1)
# proj_JetsEle_zeroJ.SetLineColor(1)
# proj_JetsEle_zeroJ.SetMarkerColor(1)
# proj_Data_zeroJ.Draw()
##proj_Data_zeroJ.GetXaxis().SetRangeUser(0,50)
# proj_Data_zeroJ.GetYaxis().SetRangeUser(1e0,2e7)
# proj_DY_zeroJ.Draw('samehist')
# proj_Jets_zeroJ.Draw('samehist')
# proj_JetsEle_zeroJ.Draw('samehist')
# proj_Electrons_zeroJ.Draw('samehist')
#
# can2 = TCanvas()
# can2.cd()
# can2.SetLogy()
# proj_Jets_twoJ.Scale(eleTwoJ/jetsTwoJ_SB)
# proj_JetsEle_twoJ = proj_Jets_twoJ.Clone()
# proj_JetsEle_twoJ.SetName('JetsEleTwoJTrkIso')
# proj_JetsEle_twoJ.Add(proj_Electrons_twoJ)
# proj_JetsEle_twoJ.SetLineStyle(2)
# proj_JetsEle_twoJ.SetLineWidth(1)
# proj_JetsEle_twoJ.SetLineColor(1)
# proj_JetsEle_twoJ.SetMarkerColor(1)
# proj_Data_twoJ.Draw()
##proj_Data_twoJ.GetXaxis().SetRangeUser(0,50)
# proj_Data_twoJ.GetYaxis().SetRangeUser(1e0,2e7)
# proj_DY_twoJ.Draw('samehist')
# proj_Jets_twoJ.Draw('samehist')
# proj_JetsEle_twoJ.Draw('samehist')
# proj_Electrons_twoJ.Draw('samehist')
#
