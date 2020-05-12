from ROOT import (
    TFile,
    TH2F,
    TCanvas,
    kRed,
    kBlue,
    kSpring,
    kAzure,
    TGraphAsymmErrors,
    TH1D,
    THStack,
    TLegend,
    kWhite,
    kGreen,
)
import ROOT
import numpy
import copy
import ctypes


def GetFakeRate(lowEnd, highEnd, reg, jets, histDict, verbose=False):
    if verbose:
        print "Considering region=", reg
        print "Considering jets=", jets
        print "Considering electron Pt:", str(lowEnd) + "-" + str(highEnd), "GeV"
    histo2D_Electrons = histDict[reg]["Electrons"][jets]
    histo2D_Jets = histDict[reg]["Jets"][jets]
    histo2D_Data = histDict[reg]["Total"][jets]
    proj_Electrons = histo2D_Electrons.ProjectionY(
        "ElesTrkIso",
        histo2D_Electrons.GetXaxis().FindBin(lowEnd),
        histo2D_Electrons.GetXaxis().FindBin(highEnd) - 1,
    )
    proj_Jets = histo2D_Jets.ProjectionY(
        "JetsTrkIso",
        histo2D_Jets.GetXaxis().FindBin(lowEnd),
        histo2D_Jets.GetXaxis().FindBin(highEnd) - 1,
    )
    proj_Data = histo2D_Data.ProjectionY(
        "DataTrkIso",
        histo2D_Data.GetXaxis().FindBin(lowEnd),
        histo2D_Data.GetXaxis().FindBin(highEnd) - 1,
    )
    # proj_JetsEle_ = proj_Jets.Clone()
    # proj_JetsEle_.SetName('JetsEleTrkIso')
    ele = proj_Electrons.Integral(
        proj_Electrons.GetXaxis().FindBin(10), proj_Electrons.GetXaxis().FindBin(20) - 1
    )
    # data = proj_Data_.Integral(proj_Data_.GetXaxis().FindBin(10),proj_Data_.GetXaxis().FindBin(20)-1)
    data = proj_Data.Integral()
    jets_SB = proj_Jets.Integral(
        proj_Jets.GetXaxis().FindBin(10), proj_Jets.GetXaxis().FindBin(20) - 1
    )
    jets_SR = proj_Jets.Integral(
        proj_Jets.GetXaxis().FindBin(0), proj_Jets.GetXaxis().FindBin(5) - 1
    )
    if verbose:
        print "Considering hists:", histo2D_Electrons.GetName(), ",", histo2D_Jets.GetName(), ",", histo2D_Data.GetName()
        # print 'endcap1 N_jet>=0: Nele=',ele,'data=',data,'contam=',ele/data
        # print 'barrel N_jet>=0: Nele=',ele,'data=',data,'contam=',ele/data
        print "nHEEPprime=", ele, "jetsSR=", jets_SR, "jetsSB=", jets_SB, "data=", data
        print "FR=", ((jets_SR / jets_SB) * ele) / data
    return ((jets_SR / jets_SB) * ele), data


def GetFakeRateMCSub(lowEnd, highEnd, reg, jets, histDict, verbose=False):
    if verbose:
        print "GetFakeRateMCSub"
        print "\tConsidering region=", reg
        print "\tConsidering jets=", jets
        print "\tConsidering electron Pt:", str(lowEnd) + "-" + str(highEnd), "GeV"
    histo2D_Electrons = histDict[reg]["Electrons"][jets]
    histo2D_MC = histDict[reg]["MC"][jets]
    mc2DHists = [histDict[reg][y][jets] for y in mcNames]
    histo2D_Data = histDict[reg]["Total"][jets]
    proj_Electrons = histo2D_Electrons.ProjectionY(
        "ElesTrkIso",
        histo2D_Electrons.GetXaxis().FindBin(lowEnd),
        histo2D_Electrons.GetXaxis().FindBin(highEnd) - 1,
    )
    proj_MC = histo2D_MC.ProjectionY(
        "TrkIsoMC",
        histo2D_MC.GetXaxis().FindBin(lowEnd),
        histo2D_MC.GetXaxis().FindBin(highEnd) - 1,
    )
    mcProjs = [
        histo2D.ProjectionY(
            "TrkIsoProj" + histo2D.GetName(),
            histo2D.GetXaxis().FindBin(lowEnd),
            histo2D.GetXaxis().FindBin(highEnd) - 1,
        )
        for histo2D in mc2DHists
    ]
    proj_Data = histo2D_Data.ProjectionY(
        "DataTrkIso",
        histo2D_Data.GetXaxis().FindBin(lowEnd),
        histo2D_Data.GetXaxis().FindBin(highEnd) - 1,
    )
    # number of HEEP electrons: pass trkIso < 5 GeV
    ele = proj_Electrons.Integral(
        proj_Electrons.GetXaxis().FindBin(0), proj_Electrons.GetXaxis().FindBin(5) - 1
    )
    # denominator is all loose electrons in the region
    data = proj_Data.Integral()
    # MC for real electron subtraction: also trkIso < 5 GeV
    realEle = proj_MC.Integral(
        proj_MC.GetXaxis().FindBin(0), proj_MC.GetXaxis().FindBin(5) - 1
    )
    realEleMCList = [
        proj.Integral(proj.GetXaxis().FindBin(0), proj.GetXaxis().FindBin(5) - 1)
        for proj in mcProjs
    ]
    if verbose:
        print "\tnumer:ele=", ele, "numMC=", realEle, "numMCSubd", ele - realEle, "denom:data=", data
        if realEle > ele:
            print "\tbreakdown of MC:"
            for i, sample in enumerate(mcNames):
                print "\t\t" + sample, realEleMCList[i]
            print "histo2D_Electrons has name:", histo2D_Electrons.GetName()
            print "histo2D_Electrons has entries:", histo2D_Electrons.GetEntries()
        print "\tFR=", (ele - realEle) / data
    return (ele - realEle), data


def MakeFakeRatePlot(reg, jets, histDict, dataDriven=True):
    verbose = False
    if verbose:
        print "MakeFakeRatePlot:reg=", reg, "jets=", jets, "dataDriven=", dataDriven
    if reg == "Bar":
        bins = ptBinsBarrel
    else:
        bins = ptBinsEndcap
    histNum = TH1D(
        "num" + reg + jets + str(dataDriven),
        "num" + reg + jets + str(dataDriven),
        len(bins) - 1,
        numpy.array(bins, dtype=float),
    )
    histDen = TH1D(
        "den" + reg + jets + str(dataDriven),
        "den" + reg + jets + str(dataDriven),
        len(bins) - 1,
        numpy.array(bins, dtype=float),
    )
    for index, binLow in enumerate(bins):
        if index >= (len(bins) - 1):
            break
        binHigh = bins[index + 1]
        if dataDriven:
            num, den = GetFakeRate(binLow, binHigh, reg, jets, histDict, verbose)
        else:
            num, den = GetFakeRateMCSub(binLow, binHigh, reg, jets, histDict, verbose)
        histNum.SetBinContent(histNum.GetXaxis().FindBin(binLow), num)
        histDen.SetBinContent(histDen.GetXaxis().FindBin(binLow), den)
        if verbose:
            print "look at Pt:", str(binLow) + "-" + str(binHigh)
            print "num=", num, "den=", den
            print "set bin:", histNum.GetXaxis().FindBin(binLow), "to", num
            print "bin content is:", histNum.GetBinContent(
                histNum.GetXaxis().FindBin(binLow)
            )
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
    graphFR.SetName(
        "fr{reg}_{jets}{dataDriven}".format(
            reg=reg, jets=jets, dataDriven="template" if dataDriven else "MCsub"
        )
    )
    return graphFR, histNum, histDen


def MakeFRCanvas(plotList, titleList, canTitle):
    can = TCanvas()
    can.cd()
    can.SetGridy()
    can.SetTitle(canTitle)
    can.SetName(canTitle.lower().replace(',', '').replace(' ', '_').replace('>=', 'gte'))
    colorList = [1, kSpring-1, kAzure+1, kBlue, kGreen]
    markerStyleList = [8, 25, 23, 22]
    for i, plot in enumerate(plotList):
        if i == 0:
            plot.Draw("ap")
            plot.GetXaxis().SetRangeUser(0, 1000)
            plot.GetXaxis().SetTitle("E_{T} [GeV]")
            plot.GetYaxis().SetRangeUser(0, 0.08)
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
            plot.Draw("ap")
        else:
            plot.Draw("psame")
    # hsize=0.20
    # vsize=0.35
    # leg = TLegend(0.19,0.18,0.44,0.35)
    leg = TLegend(0.38, 0.71, 0.63, 0.88)
    leg.SetFillColor(kWhite)
    leg.SetFillStyle(1001)
    leg.SetBorderSize(0)
    leg.SetShadowColor(10)
    leg.SetMargin(0.2)
    leg.SetTextFont(132)
    if len(titleList) != len(plotList):
        print "ERROR: titleList and plotList passed into MakeFRCanvas are different lengths!"
    for i, title in enumerate(titleList):
        leg.AddEntry(plotList[i], title, "lp")
        print "For canvas titled:", canTitle, ", added entry in legend for plot:", plotList[
            i
        ].GetName(), "setting title to:", title
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
                    print "ERROR: could not get hist '"+histName+"' from file: "+tfile.GetName()
                    exit(-1)
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
def MakeFR2D(frGraph, reg):
    if reg == "Bar":
        bins = ptBinsBarrel
        etaToFill = 1
    elif reg == "End1":
        bins = ptBinsEndcap
        etaToFill = 1.7
    elif reg == "End2":
        bins = ptBinsEndcap
        etaToFill = 2
    else:
        print "ERROR: could not understand region given:", reg, "; return empty hist"
        return
    etaBins = [-2.5, -2.0, -1.566, -1.4442, 0, 1.4442, 1.566, 2.0, 2.5]
    frHist2d = TH2F(
        "test",
        "test",
        len(etaBins) - 1,
        numpy.array(etaBins, dtype=float),
        len(bins) - 1,
        numpy.array(bins, dtype=float),
    )
    # print 'consider frGraph with name {}'.format(frGraph.GetName())
    jets = GetJetBin(frGraph.GetName())
    name = "fr2D_{reg}_{jets}".format(reg=reg, jets=jets)
    frHist2d.SetNameTitle(name, name)
    frHist2d.GetXaxis().SetTitle("SuperCluster #eta")
    frHist2d.GetYaxis().SetTitle("p_{T} [GeV]")
    for iPoint in range(frGraph.GetN()):
        x = ctypes.c_double()
        y = ctypes.c_double()
        frGraph.GetPoint(iPoint, x, y)
        frHist2d.SetBinContent(
            frHist2d.GetXaxis().FindBin(etaToFill), frHist2d.GetYaxis().FindBin(x.value), y.value
        )
        # TODO set error
    return frHist2d


####################################################################################################
# RUN
####################################################################################################
# filename = '$LQDATA/2016fakeRate/nov20_test/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
# filename = '$LQDATA/2016fakeRate/dec8_addPreselCuts/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
# filename = '$LQDATA/2016fakeRate/dec8_noPreselCuts/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
# filename = '$LQDATA/2016fakeRate/dec15_tightenJets/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
# filename = '$LQDATA/2016fakeRate/dec17_tightenJetsAddMET55cut/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
# filename = '$LQDATA/2016fakeRate/dec18_tightenJetsNoMET55cut/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
# filename = '$LQDATA/2016fakeRate/dec19_mtPlots_tightenJetsNoMET55cut/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
# filename = '$LQDATA/2016fakeRate/jan15_addLTE1JetRegion/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
# filename = '$LQDATA/2016fakeRate/jan16_addLTE1JetRegion/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
# filename = '$LQDATA/nano/2016/qcdFakeRate//output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
# filename = "$LQDATA/nano/2016/qcdFakeRate/jan30_fixEnd2DenBug/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"
#
# filename = "$LQDATA/nanoV6/2017/qcdFakeRateCalc/apr7_attempt1/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"
# filename = "$LQDATA/nanoV6/2017/qcdFakeRateCalc/apr17_attempt2/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"
filename = "$LQDATA/nanoV6/2018/qcdFakeRateCalc/apr17_attempt1/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root"

outputFileName = "plots.root"

print "Opening file:", filename
tfile = TFile.Open(filename)

ROOT.gROOT.SetBatch(True)
writeOutput = True
doMuz = False  # do Muzamil's plots

histoBaseName = "histo2D__{sample}__{type}_{region}_{jets}{varName}"
dataSampleName = "QCDFakes_DATA"

ptBinsBarrel = [
    35,
    40,
    45,
    50,
    60,
    70,
    80,
    90,
    100,
    110,
    130,
    150,
    170,
    200,
    250,
    300,
    400,
    500,
    600,
    800,
    1000,
]
ptBinsEndcap = [35, 50, 75, 100, 125, 150, 200, 250, 300, 350, 500, 1000]
electronTypes = ["Jets", "Electrons", "Total"]
# probably eventually expand to BarPlus, BarMinus, etc.
detectorRegions = ["Bar", "End1", "End2"]
jetBins = ["", "1Jet_", "2Jet_", "3Jet_"]
# for MC
mcSamples = [
    # "ZJet_amcatnlo_ptBinned",
    "ZJet_amcatnlo_Inc",
    # "WJet_amcatnlo_ptBinned",
    "WJet_Madgraph_Inc",
    "TTbar_powheg",
    "SingleTop",
    "PhotonJets_Madgraph",
    "DIBOSON",
]
mcNames = ["ZJets", "WJets", "TTBar", "ST", "GJets", "Diboson"]

varNameList = ["TrkIsoHEEP7vsPt_PAS", "TrkIsoHEEP7vsMTenu_PAS"]

allHistos = {}
for varName in varNameList:
    allHistos[varName] = {}
    LoadHistosData(allHistos[varName], varName, dataSampleName)
    LoadHistosMC(allHistos[varName], varName)


myCanvases = []
if writeOutput:
    outputFile = TFile(outputFileName, "recreate")
    outputFile.cd()
# TEST end2 FR plots
if doMuz:
    # get Muzamil's hists
    tfileMuzamilTwoJ = TFile(
        "/afs/cern.ch/user/m/mbhat/work/public/Fakerate_files_2016/FR2D2JetScEt.root"
    )
    tfileMuzamilZeroJ = TFile(
        "/afs/cern.ch/user/m/mbhat/work/public/Fakerate_files_2016/FR0JET_HLT.root"
    )
    muzHist2DZeroJ = tfileMuzamilZeroJ.Get("Endcap_Fake_Rate")
    muzHist2DZeroJBar = tfileMuzamilZeroJ.Get("Barrel_Fake_Rate")
    muzHistEnd2ZeroJ = muzHist2DZeroJ.ProjectionX("projMuzEnd2_0Jets", 2, 2)
    muzHistEnd1ZeroJ = muzHist2DZeroJ.ProjectionX("projMuzEnd1_0Jets", 1, 1)
    muzHistBarZeroJ = muzHist2DZeroJBar.ProjectionX("projMuzBar_0Jets")
# get Sam's hists
tfileZPrime = TFile(
    "/afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleAnalyzerV2/heepV7p0_2016_reminiAOD_noEleTrig_fakerate.root"
)
zprimeHistEnd2ZeroJ = tfileZPrime.Get("frHistEEHigh")
zprimeHistEnd1ZeroJ = tfileZPrime.Get("frHistEELow")
zprimeHistBarZeroJ = tfileZPrime.Get("frHistEB")
# my hists
histos = allHistos["TrkIsoHEEP7vsPt_PAS"]
graphEnd2ZeroJ, histNumEnd2ZeroJ, histDenEnd2ZeroJ = MakeFakeRatePlot(
    "End2", "", histos
)
graphEnd2ZeroJMC, histNumEnd2ZeroJMC, histDenEnd2ZeroJMC = MakeFakeRatePlot(
    "End2", "", histos, False
)
graphEnd1ZeroJ, histNumEnd1ZeroJ, histDenEnd1ZeroJ = MakeFakeRatePlot(
    "End1", "", histos
)
graphEnd1ZeroJMC, histNumEnd1ZeroJMC, histDenEnd1ZeroJMC = MakeFakeRatePlot(
    "End1", "", histos, False
)
graphBarZeroJ, histNumBarZeroJ, histDenBarZeroJ = MakeFakeRatePlot("Bar", "", histos)
graphBarZeroJMC, histNumBarZeroJMC, histDenBarZeroJMC = MakeFakeRatePlot(
    "Bar", "", histos, False
)
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

# for writing output
if doMuz:
    histList = [
        graphEnd2ZeroJ,
        graphEnd2ZeroJMC,
        muzHistEnd2ZeroJ,
        zprimeHistEnd2ZeroJ,
        graphEnd1ZeroJ,
        graphEnd1ZeroJMC,
        muzHistEnd1ZeroJ,
        zprimeHistEnd1ZeroJ,
        graphBarZeroJ,
        graphBarZeroJMC,
        muzHistBarZeroJ,
        zprimeHistBarZeroJ,
    ]
else:
    histList = [
        graphEnd2ZeroJ,
        graphEnd2ZeroJMC,
        zprimeHistEnd2ZeroJ,
        graphEnd1ZeroJ,
        graphEnd1ZeroJMC,
        zprimeHistEnd1ZeroJ,
        graphBarZeroJ,
        graphBarZeroJMC,
        zprimeHistBarZeroJ,
    ]

if doMuz:
    titleList = [
        "Data-driven",
        "MCSub",
        "Muzamil (E_{T}^{HLT})",
        "2016 Zprime (E_{T}^{HLT})",
    ]
    myCanvases.append(
        MakeFRCanvas(
            [graphEnd2ZeroJ, graphEnd2ZeroJMC, muzHistEnd2ZeroJ, zprimeHistEnd2ZeroJ],
            titleList,
            "Endcap2, >=0 jets",
        )
    )
    myCanvases.append(
        MakeFRCanvas(
            [graphEnd1ZeroJ, graphEnd1ZeroJMC, muzHistEnd1ZeroJ, zprimeHistEnd1ZeroJ],
            titleList,
            "Endcap1, >=0 jets",
        )
    )
    myCanvases.append(
        MakeFRCanvas(
            [graphBarZeroJ, graphBarZeroJMC, muzHistBarZeroJ, zprimeHistBarZeroJ],
            titleList,
            "Barrel, >=0 jets",
        )
    )
else:
    titleList = ["Data-driven", "MCSub", "2016 Zprime (E_{T}^{HLT})"]
    myCanvases.append(
        MakeFRCanvas(
            [graphEnd2ZeroJ, graphEnd2ZeroJMC, zprimeHistEnd2ZeroJ],
            titleList,
            "Endcap2, >=0 jets",
        )
    )
    myCanvases.append(
        MakeFRCanvas(
            [graphEnd1ZeroJ, graphEnd1ZeroJMC, zprimeHistEnd1ZeroJ],
            titleList,
            "Endcap1, >=0 jets",
        )
    )
    myCanvases.append(
        MakeFRCanvas(
            [graphBarZeroJ, graphBarZeroJMC, zprimeHistBarZeroJ],
            titleList,
            "Barrel, >=0 jets",
        )
    )

if writeOutput:
    outputFile.cd()
for canLeg in myCanvases:
    canv = canLeg[0]
    canv.Draw()  # canvas
    # canLeg[-1][1].Draw() #legend
    if writeOutput:
        canv.Write()
        canv.Print(canv.GetName()+".png")

##################################################
# >= 1 jet
##################################################
##################################################
if writeOutput:
    outputFile.cd()
# my hists
graphEnd2OneJ = MakeFakeRatePlot("End2", "1Jet_", histos)[0]
graphEnd2OneJMC = MakeFakeRatePlot("End2", "1Jet_", histos, False)[0]
graphEnd1OneJ = MakeFakeRatePlot("End1", "1Jet_", histos)[0]
graphEnd1OneJMC = MakeFakeRatePlot("End1", "1Jet_", histos, False)[0]
graphBarOneJ = MakeFakeRatePlot("Bar", "1Jet_", histos)[0]
graphBarOneJMC = MakeFakeRatePlot("Bar", "1Jet_", histos, False)[0]
# for writing output
histList.extend(
    [
        graphEnd2OneJ,
        graphEnd2OneJMC,  # muzHistEnd2OneJ,zprimeHistEnd2OneJ,
        graphEnd1OneJ,
        graphEnd1OneJMC,  # muzHistEnd1OneJ,zprimeHistEnd1OneJ,
        graphBarOneJ,
        graphBarOneJMC,
    ]
)  # ,muzHistBarOneJ,zprimeHistBarOneJ])

##################################################
# >= 2 jet
##################################################
if writeOutput:
    outputFile.cd()
if doMuz:
    # Muzamil's plots
    muzHist2DTwoJ = tfileMuzamilTwoJ.Get("Endcap_Fake_Rate")
    muzHist2DTwoJBar = tfileMuzamilTwoJ.Get("Barrel_Fake_Rate")
    muzHistEnd2TwoJ = muzHist2DTwoJ.ProjectionX("projMuzEnd2_2Jets", 2, 2)
    muzHistEnd1TwoJ = muzHist2DTwoJ.ProjectionX("projMuzEnd1_2Jets", 1, 1)
    muzHistBarTwoJ = muzHist2DTwoJBar.ProjectionX("projMuzBar_2Jets")
# my hists
graphEnd2TwoJ = MakeFakeRatePlot("End2", "2Jet_", histos)[0]
graphEnd2TwoJMC = MakeFakeRatePlot("End2", "2Jet_", histos, False)[0]
graphEnd1TwoJ = MakeFakeRatePlot("End1", "2Jet_", histos)[0]
graphEnd1TwoJMC = MakeFakeRatePlot("End1", "2Jet_", histos, False)[0]
graphBarTwoJ = MakeFakeRatePlot("Bar", "2Jet_", histos)[0]
graphBarTwoJMC = MakeFakeRatePlot("Bar", "2Jet_", histos, False)[0]
# for writing output
if doMuz:
    histList.extend(
        [
            graphEnd2TwoJ,
            graphEnd2TwoJMC,
            muzHistEnd2TwoJ,
            graphEnd1TwoJ,
            graphEnd1TwoJMC,
            muzHistEnd1TwoJ,
            graphBarTwoJ,
            graphBarTwoJMC,
            muzHistBarTwoJ,
        ]
    )
else:
    histList.extend(
        [
            graphEnd2TwoJ,
            graphEnd2TwoJMC,
            graphEnd1TwoJ,
            graphEnd1TwoJMC,
            graphBarTwoJ,
            graphBarTwoJMC,
        ]
    )

if doMuz:
    titleList = ["Data-driven", "MCSub", "Muzamil (E_{T}^{HLT})"]
    myCanvases.append(
        MakeFRCanvas(
            [graphEnd2TwoJ, graphEnd2TwoJMC, muzHistEnd2TwoJ],
            titleList,
            "Endcap2, >=2 jets",
        )
    )
    myCanvases.append(
        MakeFRCanvas(
            [graphEnd1TwoJ, graphEnd1TwoJMC, muzHistEnd1TwoJ],
            titleList,
            "Endcap1, >=2 jets",
        )
    )
    myCanvases.append(
        MakeFRCanvas(
            [graphBarTwoJ, graphBarTwoJMC, muzHistBarTwoJ],
            titleList,
            "Barrel, >=2 jets",
        )
    )
else:
    titleList = ["Data-driven", "MCSub"]
    graphEnd2TwoJ.Print()
    graphEnd2TwoJMC.Print()
    myCanvases.append(
        MakeFRCanvas([graphEnd2TwoJ, graphEnd2TwoJMC], titleList, "Endcap2, >=2 jets")
    )
    myCanvases.append(
        MakeFRCanvas([graphEnd1TwoJ, graphEnd1TwoJMC], titleList, "Endcap1, >=2 jets")
    )
    myCanvases.append(
        MakeFRCanvas([graphBarTwoJ, graphBarTwoJMC], titleList, "Barrel, >=2 jets")
    )

if writeOutput:
    outputFile.cd()
for canLeg in myCanvases:
    canv = canLeg[0]
    canv.Draw()  # canvas
    # canLeg[-1][1].Draw() #legend
    if writeOutput:
        canv.Write()
        canv.Print(canv.GetName()+".png")


##################################################
# make Et plot
##################################################
# histoNameZ = 'histo2D__ZJet_amcatnlo_ptBinned__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
# histoNameW = 'histo2D__WJet_amcatnlo_ptBinned__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
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
        # histo2D_MC = tfile.Get(histoNameZ.format(region=reg,jets=jet))
        histo2D_MC = histos[reg]["ZJets"][jet]
        proj_MC = histo2D_MC.ProjectionX(
            "EtZ",
            histo2D_MC.GetYaxis().FindBin(0),
            histo2D_MC.GetYaxis().FindBin(5) - 1,
        )
        histosPt[reg]["ZElectrons"][jet] = proj_MC
        # histo2D_MC = tfile.Get(histoNameW.format(region=reg,jets=jet))
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
        proj_data = histo2D_data.ProjectionX(
            "EtData",
            histo2D_data.GetYaxis().FindBin(0),
            histo2D_data.GetYaxis().FindBin(5) - 1,
        )
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
#
stack = THStack()
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
legEt.AddEntry(histZ, "ZJets", "lp")
legEt.AddEntry(histW, "WJets", "lp")
legEt.AddEntry(histData, "Data", "lp")
legEt.AddEntry(histDataLoose, "Data (loose e)", "lp")
legEt.Draw()
canvasEt.Modified()
canvasEt.Update()
low = 800
high = 1000
print "integrals in 800-1000:"
print "dataLoose=", histDataLoose.Integral(
    histDataLoose.FindBin(low), histDataLoose.FindBin(high) - 1
)
print "dataEle=", histData.Integral(histData.FindBin(low), histData.FindBin(high) - 1)
print "WEle=", histW.Integral(histW.FindBin(low), histW.FindBin(high) - 1)
print "ZEle=", histZ.Integral(histZ.FindBin(low), histZ.FindBin(high) - 1)


if writeOutput:
    endcap2dHists = []
    for hist in histList:
        hist.Write()
        if "template" in hist.GetName():
            hist2d = MakeFR2D(hist, hist.GetName()[2: hist.GetName().find("_")])
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
