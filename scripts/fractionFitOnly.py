from __future__ import print_function

from ROOT import(
    gROOT,
    TFile,
    TFractionFitter,
    TH2F,
    TF1,
    TCanvas,
    TColor,
    kRed,
    kBlue,
    kSpring,
    kAzure,
    TGraphAsymmErrors,
    TH1D,
    TLegend,
    TObjArray,
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

def GetFakeRateFractionFit(
    shortVarName, lowEnd, highEnd, reg, jets, histDict, verbose=False
):
    verbose = True
    #I don't know what this does, but making it smaller seemed to make it more likely to converge
    #to a reasonable value. 
    fractionFitXRangeMax = 0.075
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
    #These seem to be the best starting parameters
    fracFit.GetFitter().Config().ParSettings(0).Set("DYElectrons", 0.56, 0.001, 0, 1.0)
    fracFit.GetFitter().Config().ParSettings(1).Set("Jets", 0.44, 0.001, 0, 1.0)
    fracFit.SetRangeX(1, proj_MCElectrons.FindBin(fractionFitXRangeMax))
    status = fracFit.Fit()
    print("fit status=", status)
    if status.Status() != 0:
        print("Fit failed: fit status is {} and not 0.".format(status.Status()))
        return 0, 0, data, dataErr.value, status
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

    return jetsPred, jetsPredErr, data, dataErr.value, status


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

# in case I decide to make plots later:
def MakeFakeRatePlot(
    varName, reg, jets, bins, histDict, verbose=True
):
    if verbose:
        print(
            "MakeFakeRatePlot:varName=",
            varName,
            "reg=",
            reg,
            "jets=",
            jets,
        )
        sys.stdout.flush()
    bins = ptBins 
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
        num, numErr, den, denErr = GetFakeRateFractionFit(
                    shortVarName, binLow, binHigh, reg, jets, histDict, verbose
                )
        histNum.SetBinContent(histNum.GetXaxis().FindBin(binLow), num)
        histDen.SetBinContent(histDen.GetXaxis().FindBin(binLow), den)
        histNum.SetBinError(histNum.GetXaxis().FindBin(binLow), numErr)
        histDen.SetBinError(histDen.GetXaxis().FindBin(binLow), denErr)
        print("****************************************************************")
    graphFR = TGraphAsymmErrors()
    graphFR.BayesDivide(histNum, histDen)
    graphFR.SetName(
            "fr{reg}_{jets}{method}".format(
                reg=reg, jets=jets, method=typeString
            )
    )
    return graphFR, histNum, histDen

###############################################################################
# RUN
###############################################################################

input_file = "/eos/user/e/eipearso/LQ/lqData/2016/qcdFakeRateCalc/calcFR_2016Pre_06dec2022/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"
print("Opening file: ", input_file)
tfile = TFile.Open(input_file)

gROOT.SetBatch(True)

histoBaseName = "histo2D__{sample}__{type}_{region}_{jets}{varName}"
varName = "PFRelIsoAllvsPt_PAS"
dataSampleName = "QCDFakes_DATA"
detectorRegions = ["Bar", "End1", "End2"]
electronTypes = ["Jets", "Electrons", "Total"]
jetBins = ["", "1Jet_", "2Jet_"]
mcNames = ["ZJets", "WJets", "TTBar", "ST", "GJets", "Diboson"]

if "2016" in input_file:
    mcSamples = [
        "ZJet_amcatnlo_ptBinned",
        # "ZJet_amcatnlo_Inc",
        # "WJet_amcatnlo_ptBinned",
        # "WJet_Madgraph_Inc",
        "WJet_amcatnlo_Inc",
        "TTbar_powheg",
        "SingleTop",
        "PhotonJets_Madgraph",
        "DIBOSON_nlo",
    ]

ptBins = [
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

histos = {}
histos["PFRelIsoAllvsPt_PAS"] = {}
LoadHistosData(histos[varName], varName, dataSampleName)
LoadHistosMC(histos[varName], varName)

numConverged = 0
numGoodFits = 0
#Do fraction fit for all of the pt bins in the barrel for 0 jets:
for lowEndIdx in range(len(ptBins)-1):
    highEndIdx = lowEndIdx+1
    ptLow = ptBins[lowEndIdx]
    ptHigh = ptBins[highEndIdx]
    num, numErr, den, denErr, fit_status = GetFakeRateFractionFit("PFRelIsoAll", ptLow, ptHigh, "Bar", "", histos[varName], verbose=True)
    if fit_status == 0:
        numConverged+=1
        if num >= 100:
            numGoodFits+=1
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

print("Number of converged bins: ", numConverged)
#yesterday we saw a lot of stuff that converged but the number of jets was ridiculously small
#so I thought that would also be a good thing to check.
print("Number of converged bins with a meaningful number of jets: ", numGoodFits)  

