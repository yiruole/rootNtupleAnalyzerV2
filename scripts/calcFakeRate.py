from ROOT import TFile,TH2F,TProfile,TCanvas,TColor,kRed,kBlue,TGraphAsymmErrors,TH1D,THStack,TLegend,kWhite,kGreen
import math
import numpy


def GetFakeRate(lowEnd,highEnd,reg,jets,histDict):
  #print 'Considering region=',reg
  #print 'Considering jets=',jets
  #print 'Considering electron Pt:',str(lowEnd)+'-'+str(highEnd),'GeV'
  histo2D_Electrons = histDict[reg]['Electrons'][jets]
  histo2D_Jets = histDict[reg]['Jets'][jets]
  histo2D_Data = histDict[reg]['Total'][jets]
  proj_Electrons = histo2D_Electrons.ProjectionY('ElesTrkIso',histo2D_Electrons.GetXaxis().FindBin(lowEnd),histo2D_Electrons.GetXaxis().FindBin(highEnd)-1)
  proj_Jets = histo2D_Jets.ProjectionY('JetsTrkIso',histo2D_Jets.GetXaxis().FindBin(lowEnd),histo2D_Jets.GetXaxis().FindBin(highEnd)-1)
  proj_Data = histo2D_Data.ProjectionY('DataTrkIso',histo2D_Data.GetXaxis().FindBin(lowEnd),histo2D_Data.GetXaxis().FindBin(highEnd)-1)
  #proj_JetsEle_ = proj_Jets.Clone()
  #proj_JetsEle_.SetName('JetsEleTrkIso')
  ele = proj_Electrons.Integral(proj_Electrons.GetXaxis().FindBin(10),proj_Electrons.GetXaxis().FindBin(20)-1)
  #data = proj_Data_.Integral(proj_Data_.GetXaxis().FindBin(10),proj_Data_.GetXaxis().FindBin(20)-1)
  data = proj_Data.Integral()
  jets_SB = proj_Jets.Integral(proj_Jets.GetXaxis().FindBin(10),proj_Jets.GetXaxis().FindBin(20)-1)
  jets_SR = proj_Jets.Integral(proj_Jets.GetXaxis().FindBin(0),proj_Jets.GetXaxis().FindBin(5)-1)
  ##print 'endcap1 N_jet>=0: Nele=',ele,'data=',data,'contam=',ele/data
  ##print 'barrel N_jet>=0: Nele=',ele,'data=',data,'contam=',ele/data
  #print 'nHEEPprime=',ele,'jetsSR=',jets_SR,'jetsSB=',jets_SB,'data=',data
  #print 'FR=',((jets_SR/jets_SB) * ele)/data
  return ((jets_SR/jets_SB) * ele),data


def GetFakeRateMCSub(lowEnd,highEnd,reg,jets,histDict):
  #print 'GetFakeRateMCSub'
  #print '\tConsidering region=',reg
  #print '\tConsidering jets=',jets
  #print '\tConsidering electron Pt:',str(lowEnd)+'-'+str(highEnd),'GeV'
  histo2D_Electrons = histDict[reg]['Electrons'][jets]
  histo2D_MC = histDict[reg]['MC'][jets]
  histo2D_Data = histDict[reg]['Total'][jets]
  proj_Electrons = histo2D_Electrons.ProjectionY('ElesTrkIso',histo2D_Electrons.GetXaxis().FindBin(lowEnd),histo2D_Electrons.GetXaxis().FindBin(highEnd)-1)
  proj_MC = histo2D_MC.ProjectionY('TrkIso',histo2D_MC.GetXaxis().FindBin(lowEnd),histo2D_MC.GetXaxis().FindBin(highEnd)-1)
  proj_Data = histo2D_Data.ProjectionY('DataTrkIso',histo2D_Data.GetXaxis().FindBin(lowEnd),histo2D_Data.GetXaxis().FindBin(highEnd)-1)
  # number of HEEP electrons: pass trkIso < 5 GeV
  ele = proj_Electrons.Integral(proj_Electrons.GetXaxis().FindBin(0),proj_Electrons.GetXaxis().FindBin(5)-1)
  # denominator is all loose electrons in the region
  data = proj_Data.Integral()
  # MC for real electron subtraction: also trkIso < 5 GeV
  realEle = proj_MC.Integral(proj_MC.GetXaxis().FindBin(0),proj_MC.GetXaxis().FindBin(5)-1)
  #print '\tnumer:ele=',ele,'numMC=',realEle,'numMCSubd',ele-realEle,'denom:data=',data
  #print '\tFR=',(ele-realEle)/data
  return (ele-realEle),data


def MakeFakeRatePlot(reg,jets,histDict,dataDriven=True):
  if reg=='Bar':
    bins = [45,50,60,70,80,90,100,110,130,150,170,200,250,300,400,500,600,800,1000]
  else:
    bins = [50,75,100,125,150,200,250,300,350,500,1000]
  histNum = TH1D('num','num',len(bins)-1,numpy.array(bins,dtype=float))
  histDen = TH1D('den','den',len(bins)-1,numpy.array(bins,dtype=float))
  for index,binLow in enumerate(bins):
    if index>=(len(bins)-1):
      break
    binHigh = bins[index+1]
    if dataDriven:
      num,den = GetFakeRate(binLow,binHigh,reg,jets,histDict)
    else:
      num,den = GetFakeRateMCSub(binLow,binHigh,reg,jets,histDict)
    histNum.SetBinContent(histNum.GetXaxis().FindBin(binLow),num)
    histDen.SetBinContent(histDen.GetXaxis().FindBin(binLow),den)
    #print 'look at Pt:',str(binLow)+'-'+str(binHigh)
    #print 'num=',num,'den=',den
    #print 'set bin:',histNum.GetXaxis().FindBin(binLow),'to',num
    #print 'bin content is:',histNum.GetBinContent(histNum.GetXaxis().FindBin(binLow))
  #c = TCanvas()
  #c.cd()
  #histNum.Draw()
  #c1 = TCanvas()
  #c1.cd()
  #histDen.Draw()
  graphFR = TGraphAsymmErrors()
  graphFR.BayesDivide(histNum,histDen)
  return graphFR


def MakeFRCanvas(plotList,titleList,canTitle):
    can = TCanvas()
    can.cd()
    can.SetGridy()
    can.SetTitle(canTitle)
    colorList = [9,2,6,kBlue,kGreen]
    markerStyleList = [4,20,23,22]
    for i,plot in enumerate(plotList):
        if i==0:
            plot.Draw('ap')
            plot.GetXaxis().SetRangeUser(0,1000)
            plot.GetXaxis().SetTitle('E_{T} [GeV]')
            plot.GetYaxis().SetRangeUser(0,0.08)
            plot.GetYaxis().SetNdivisions(510)
        if 'graph' not in plot.ClassName().lower():
            plot.SetStats(0)
        plot.SetMarkerColor(colorList[i])
        plot.SetLineColor(colorList[i])
        plot.SetMarkerStyle(markerStyleList[i])
        plot.SetMarkerSize(0.9)
        if i==0:
            plot.Draw('ap')
        else:
            plot.Draw('psame')
    #hsize=0.20
    #vsize=0.35
    #leg = TLegend(0.19,0.18,0.44,0.35)
    leg = TLegend(0.38,0.71,0.63,0.88)
    leg.SetFillColor(kWhite)
    leg.SetFillStyle(1001)
    leg.SetBorderSize(0)
    leg.SetShadowColor(10)
    leg.SetMargin(0.2)
    leg.SetTextFont(132)
    for i,title in enumerate(titleList):
        leg.AddEntry(plotList[i],title,'lp')
    leg.Draw()
    can.Modified()
    can.Update()
    return can,leg


####################################################################################################
# RUN
####################################################################################################
#filename = '/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/2016fakeRate/nov20_test/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
#filename = '/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/2016fakeRate/dec8_addPreselCuts/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
#filename = '/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/2016fakeRate/dec8_noPreselCuts/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
filename = '/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/2016fakeRate/dec15_tightenJets/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root'
tfile = TFile.Open(filename)

histoBaseName = 'histo2D__{sample}__{type}_{region}_{jets}TrkIsoHEEP7vsPt_PAS'

detectorRegions = ['Bar','End1','End2']
electronTypes = ['Jets','Electrons','Total']
jetBins = ['','1Jet_','2Jet_','3Jet_']
histos = {}
for reg in detectorRegions:
  histos[reg] = {}
  for eType in electronTypes:
    histos[reg][eType] = {}
    for jet in jetBins:
      hist = tfile.Get(histoBaseName.format(sample='QCDFakes_DATA',type=eType,region=reg,jets=jet))
      histos[reg][eType][jet] = hist
      #print 'added histo:',hist.GetName(),'with entries:',hist.GetEntries(),'to','['+reg+']['+eType+']['+jet+']'

# for MC
histoNameZ = 'histo2D__ZJet_amcatnlo_ptBinned__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
histoNameW = 'histo2D__WJet_amcatnlo_ptBinned__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
histoNameTTBar = 'histo2D__TTbar_powheg__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
histoNameST = 'histo2D__SingleTop__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
histoNameGJets = 'histo2D__PhotonJets_Madgraph__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
histoNameDiboson = 'histo2D__DIBOSON_amcatnlo__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
detectorRegions = ['Bar','End1','End2']
jetBins = ['','1Jet_','2Jet_','3Jet_']
for reg in detectorRegions:
  histos[reg]['MC'] = {}
  for jet in jetBins:
    histZ = tfile.Get(histoNameZ.format(type=eType,region=reg,jets=jet))
    histW = tfile.Get(histoNameW.format(type=eType,region=reg,jets=jet))
    histTTBar = tfile.Get(histoNameTTBar.format(type=eType,region=reg,jets=jet))
    histST = tfile.Get(histoNameST.format(type=eType,region=reg,jets=jet))
    histGJets = tfile.Get(histoNameGJets.format(type=eType,region=reg,jets=jet))
    histDiboson = tfile.Get(histoNameDiboson.format(type=eType,region=reg,jets=jet))
    hist = histZ.Clone()
    hist.Add(histW)
    hist.Add(histTTBar)
    hist.Add(histST)
    hist.Add(histGJets)
    hist.Add(histDiboson)
    histos[reg]['MC'][jet] = hist


myCanvases = []
#TEST end2 FR plots
# get Muzamil's hist
#tfileMuzamil = TFile('/afs/cern.ch/user/m/mbhat/work/public/Fakerate_files_2016/FR2D2JetScEt.root')
tfileMuzamil = TFile('/afs/cern.ch/user/m/mbhat/work/public/Fakerate_files_2016/FR0JET_HLT.root')
muzHist2D = tfileMuzamil.Get('Endcap_Fake_Rate')
muzHistEnd2ZeroJ = muzHist2D.ProjectionX('projMuzEnd2_0Jets',2,2)
# get Sam's hist
tfileZPrime = TFile('/afs/cern.ch/user/s/scooper/work/private/cmssw/8011/TestRootNTuplizerRecipe/src/Leptoquarks/analyzer/rootNtupleAnalyzerV2/versionsOfAnalysis_fakeRateCalc/dec8/heepV7p0_2016_reminiAOD_noEleTrig_fakerate.root')
zprimeHistEnd2ZeroJ = tfileZPrime.Get('frHistEEHigh')
graphEnd2ZeroJ = MakeFakeRatePlot('End2','',histos)
graphEnd2ZeroJMC = MakeFakeRatePlot('End2','',histos,False)
titleList = ['Seth','Seth (MCSub)','Muzamil (E_{T}^{HLT})','Zprime (E_{T}^{HLT})']
myCanvases.append(MakeFRCanvas([graphEnd2ZeroJ,graphEnd2ZeroJMC,muzHistEnd2ZeroJ,zprimeHistEnd2ZeroJ],titleList,'Endcap2, >=0 jets'))

myCanvases[-1][0].Draw()
myCanvases[-1][1].Draw()

#canEnd2ZeroJ = TCanvas()
#canEnd2ZeroJ.cd()
#canEnd2ZeroJ.SetGridy()
#canEnd2ZeroJ.SetTitle('Endcap2, >=0 jets')
#graphEnd2ZeroJ.Draw('ap')
#graphEnd2ZeroJ.GetXaxis().SetRangeUser(0,1000)
#graphEnd2ZeroJ.GetXaxis().SetTitle('E_{T} [GeV]')
#graphEnd2ZeroJ.GetYaxis().SetRangeUser(0,0.08)
#graphEnd2ZeroJ.GetYaxis().SetNdivisions(510)
#graphEnd2ZeroJ.SetMarkerColor(9)
#graphEnd2ZeroJ.SetMarkerStyle(4)
#graphEnd2ZeroJ.SetMarkerSize(0.8)
#graphEnd2ZeroJ.SetLineColor(9)
#graphEnd2ZeroJ.Draw('ap')
# not data-driven but MC sub
#graphEnd2ZeroJMC.SetMarkerColor(2)
#graphEnd2ZeroJMC.SetLineColor(2)
#graphEnd2ZeroJMC.SetLineStyle(2)
#graphEnd2ZeroJMC.Draw('psames')
#
#zprimeHist.SetLineColor(kBlue)
#zprimeHist.SetMarkerColor(kBlue)
#zprimeHist.SetMarkerStyle(23)
#zprimeHist.SetMarkerSize(0.9)
#zprimeHist.SetStats(0)
#zprimeHist.Draw('psames')
#
#muzHist.SetLineColor(6)
#muzHist.SetMarkerColor(6)
#muzHist.SetMarkerStyle(22)
#muzHist.SetMarkerSize(0.9)
#muzHist.SetStats(0)
#muzHist.Draw('psames')
#hsize=0.20
#vsize=0.35
##leg = TLegend(0.19,0.18,0.44,0.35)
#leg = TLegend(0.38,0.71,0.63,0.88)
#leg.SetFillColor(kWhite)
#leg.SetFillStyle(1001)
##leg.SetBorderSize(0)
#leg.SetShadowColor(10)
#leg.SetMargin(0.2)
#leg.SetTextFont(132)
#leg.AddEntry(graphEnd2ZeroJ,'Seth','lp')
#leg.AddEntry(graphEnd2ZeroJMC,'Seth (MCSub)','lp')
#leg.AddEntry(zprimeHist,'Zprime (E_{T}^{HLT})','lp')
#leg.AddEntry(muzHist,'Muzamil (E_{T}^{HLT})','lp')
#leg.Draw('same')
#canEnd2ZeroJ.Modified()
#canEnd2ZeroJ.Update()
##
##TEST end1
##
#graphEnd1ZeroJ = MakeFakeRatePlot('End1','',histos)
#canEnd1ZeroJ = TCanvas()
#canEnd1ZeroJ.cd()
#canEnd1ZeroJ.SetGridy()
#canEnd1ZeroJ.SetTitle('Endcap1, >=0 jets')
#graphEnd1ZeroJ.Draw('ap')
#graphEnd1ZeroJ.GetXaxis().SetRangeUser(0,1000)
#graphEnd1ZeroJ.GetYaxis().SetRangeUser(0,0.1)
#graphEnd1ZeroJ.GetYaxis().SetNdivisions(516)
#graphEnd1ZeroJ.Draw('ap')
## not data-driven but MC sub
#graphEnd1ZeroJMC = MakeFakeRatePlot('End1','',histos,False)
#graphEnd1ZeroJMC.SetMarkerColor(2)
#graphEnd1ZeroJMC.SetLineColor(2)
#graphEnd1ZeroJMC.SetLineStyle(2)
#graphEnd1ZeroJMC.Draw('psames')
## get Sam's hist
#zprimeEnd1Hist = tfileZPrime.Get('frHistEELow')
#zprimeEnd1Hist.SetLineColor(kBlue)
#zprimeEnd1Hist.SetMarkerColor(kBlue)
#zprimeEnd1Hist.Draw('psames')
## get Muzamil's hist
#muzEnd1HistHist2D = tfileMuzamil.Get('Endcap_Fake_Rate')
#muzEnd1Hist = muzHist2D.ProjectionX('projMuzEnd1',1,1)
#muzEnd1Hist.SetLineColor(6)
#muzEnd1Hist.SetMarkerColor(6)
#muzEnd1Hist.Draw('psames')
#canEnd1ZeroJ.Modified()
#canEnd1ZeroJ.Update()
##
##graphEnd2ZeroJMC.GetXaxis().SetRangeUser(0,1000)
##graphEnd2ZeroJMC.GetYaxis().SetRangeUser(0,0.1)
##graphEnd2ZeroJMC.GetYaxis().SetNdivisions(516)
##graphEnd2ZeroJMC.Draw('ap')
###
## >= 2 jet
#graphEnd2TwoJ = MakeFakeRatePlot('End2','2Jet_',histos)
#canEnd2TwoJ = TCanvas()
#canEnd2TwoJ.cd()
#canEnd2TwoJ.SetGridy()
#canEnd2TwoJ.SetTitle('Endcap2, >=2 jets')
#graphEnd2TwoJ.Draw('ap')
#graphEnd2TwoJ.GetXaxis().SetRangeUser(0,1000)
#graphEnd2TwoJ.GetYaxis().SetRangeUser(0,0.1)
#graphEnd2TwoJ.GetYaxis().SetNdivisions(516)
#graphEnd2TwoJ.Draw('ap')
##
#graphEnd2TwoJMC = MakeFakeRatePlot('End2','2Jet_',histos,False)
#graphEnd2TwoJMC.SetMarkerColor(2)
#graphEnd2TwoJMC.SetLineColor(2)
#graphEnd2TwoJMC.SetLineStyle(2)
#graphEnd2TwoJMC.Draw('psames')
## get Muzamil's hist
#muzEnd2Hist2Jets2D = tfileMuzamil.Get('Endcap_Fake_Rate')
#muzEnd2Hist2Jets = muzHist2D.ProjectionX('projMuzEnd2_2Jets',1,1)
#muzEnd2Hist2Jets.SetLineColor(6)
#muzEnd2Hist2Jets.SetMarkerColor(6)
#muzEnd2Hist2Jets.Draw('psames')
#canEnd2TwoJ.Modified()
#canEnd2TwoJ.Update()

## make Et plot
#histoNameZ = 'histo2D__ZJet_amcatnlo_ptBinned__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
#histoNameW = 'histo2D__WJet_amcatnlo_ptBinned__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
#histoNameData = 'histo2D__QCDFakes_DATA__Electrons_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
#histoNameDataLoose = 'histo2D__QCDFakes_DATA__Total_{region}_{jets}TrkIsoHEEP7vsPt_PAS'
#histosPt = {}
#for reg in detectorRegions:
#  histosPt[reg] = {}
#  histosPt[reg]['ZElectrons'] = {}
#  histosPt[reg]['WElectrons'] = {}
#  histosPt[reg]['DataLooseElectrons'] = {}
#  histosPt[reg]['DataElectrons'] = {}
#  for jet in jetBins:
#    histo2D_MC = tfile.Get(histoNameZ.format(region=reg,jets=jet))
#    proj_MC = histo2D_MC.ProjectionX('EtZ',histo2D_MC.GetYaxis().FindBin(0),histo2D_MC.GetYaxis().FindBin(5)-1)
#    histosPt[reg]['ZElectrons'][jet] = proj_MC
#    histo2D_MC = tfile.Get(histoNameW.format(region=reg,jets=jet))
#    proj_MC = histo2D_MC.ProjectionX('EtW',histo2D_MC.GetYaxis().FindBin(0),histo2D_MC.GetYaxis().FindBin(5)-1)
#    histosPt[reg]['WElectrons'][jet] = proj_MC
#    histo2D_data = tfile.Get(histoNameDataLoose.format(region=reg,jets=jet))
#    proj_data = histo2D_data.ProjectionX('EtDataLoose',histo2D_data.GetYaxis().FindBin(0),histo2D_data.GetYaxis().FindBin(5)-1)
#    histosPt[reg]['DataLooseElectrons'][jet] = proj_data
#    histo2D_data = tfile.Get(histoNameData.format(region=reg,jets=jet))
#    proj_data = histo2D_data.ProjectionX('EtData',histo2D_data.GetYaxis().FindBin(0),histo2D_data.GetYaxis().FindBin(5)-1)
#    histosPt[reg]['DataElectrons'][jet] = proj_data
#    #print 'added histo:',hist.GetName(),' to ','['+reg+']['+eType+']['+jet+']'
#canvasEt = TCanvas()
#canvasEt.cd()
#canvasEt.SetLogy()
#reg = 'Bar'
#jets = ''
#rebinFactor = 20
#histData = histosPt[reg]['DataElectrons'][jets]
#histData.Rebin(rebinFactor)
#stack = THStack()
#histZ = histosPt[reg]['ZElectrons'][jets]
#histZ.Rebin(rebinFactor)
#histZ.SetLineColor(7)
#histZ.SetLineWidth(2)
#histZ.SetFillColor(7)
#histZ.SetMarkerColor(7)
#stack.Add(histZ)
#histW = histosPt[reg]['WElectrons'][jets]
#print 'W entries:',histW.GetEntries()
#histW.Rebin(rebinFactor)
#histW.SetLineColor(kBlue)
#histW.SetLineWidth(2)
#histW.SetFillColor(kBlue)
#histW.SetMarkerColor(kBlue)
#stack.Add(histW)
#stack.Draw('hist')
#stack.SetMaximum(1.2*histData.GetMaximum())
#stack.SetMinimum(1e-1)
#stack.GetXaxis().SetTitle('Et [GeV]')
#stack.Draw('hist')
#histData.Draw('psame')


#histo2D_DY_zeroJ = tfile.Get('histo2D__ZJet_amcatnlo_ptBinned__Electrons_End1_TrkIsoHEEP7vsPt_PAS')
#histo2D_Jets_zeroJ = tfile.Get('histo2D__QCDFakes_DATA__Jets_End1_TrkIsoHEEP7vsPt_PAS')
#histo2D_Electrons_zeroJ = tfile.Get('histo2D__QCDFakes_DATA__Electrons_End1_TrkIsoHEEP7vsPt_PAS')
#histo2D_Data_zeroJ = tfile.Get('histo2D__QCDFakes_DATA__Total_End1_TrkIsoHEEP7vsPt_PAS')
##histo2D_DY_zeroJ = tfile.Get('histo2D__ZJet_amcatnlo_ptBinned__Electrons_bar_TrkIsoHEEP7vsPt_PAS')
##histo2D_Jets_zeroJ = tfile.Get('histo2D__QCDFakes_DATA__Jets_Bar_TrkIsoHEEP7vsPt_PAS')
##histo2D_Electrons_zeroJ = tfile.Get('histo2D__QCDFakes_DATA__Electrons_Bar_TrkIsoHEEP7vsPt_PAS')
##histo2D_Data_zeroJ = tfile.Get('histo2D__QCDFakes_DATA__Total_Bar_TrkIsoHEEP7vsPt_PAS')
#
#lowEnd=350 # GeV
#highEnd=500
##lowEnd=60 # GeV
##highEnd=70
#print
#print
#print 'Template plot section'
#print
#print 'Considering electron Pt:',str(lowEnd)+'-'+str(highEnd),'GeV'
#proj_DY_zeroJ = histo2D_DY_zeroJ.ProjectionY('DYZeroJTrkIso',histo2D_DY_zeroJ.GetXaxis().FindBin(lowEnd),histo2D_DY_zeroJ.GetXaxis().FindBin(highEnd))
#proj_Electrons_zeroJ = histo2D_Electrons_zeroJ.ProjectionY('ElesZeroJTrkIso',histo2D_Electrons_zeroJ.GetXaxis().FindBin(lowEnd),histo2D_Electrons_zeroJ.GetXaxis().FindBin(highEnd)-1)
#proj_Jets_zeroJ = histo2D_Jets_zeroJ.ProjectionY('JetsZeroJTrkIso',histo2D_Jets_zeroJ.GetXaxis().FindBin(lowEnd),histo2D_Jets_zeroJ.GetXaxis().FindBin(highEnd)-1)
#proj_Data_zeroJ = histo2D_Data_zeroJ.ProjectionY('DataZeroJTrkIso',histo2D_Data_zeroJ.GetXaxis().FindBin(lowEnd),histo2D_Data_zeroJ.GetXaxis().FindBin(highEnd)-1)
#print 'Using bin range:',histo2D_Data_zeroJ.GetXaxis().FindBin(lowEnd),'to',histo2D_Data_zeroJ.GetXaxis().FindBin(highEnd)-1
#can1 = TCanvas()
#can1.cd()
#proj_Data_zeroJ.Draw()
#
#proj_DY_zeroJ.SetLineColor(kBlue)
#proj_DY_zeroJ.SetMarkerColor(kBlue)
#proj_DY_zeroJ.SetLineStyle(2)
#proj_DY_zeroJ.SetLineWidth(2)
#proj_Jets_zeroJ.SetLineColor(kRed)
#proj_Jets_zeroJ.SetMarkerColor(kRed)
#proj_Jets_zeroJ.SetLineStyle(2)
#proj_Jets_zeroJ.SetLineWidth(2)
#proj_Data_zeroJ.SetLineColor(kBlue)
#proj_Data_zeroJ.SetMarkerColor(kBlue)
#
## ugly copy paste
#histo2D_DY_twoJ = tfile.Get('histo2D__ZJet_amcatnlo_ptBinned__Electrons_End1_2Jet_TrkIsoHEEP7vsPt_PAS')
#histo2D_Jets_twoJ = tfile.Get('histo2D__QCDFakes_DATA__Jets_End1_2Jet_TrkIsoHEEP7vsPt_PAS')
#histo2D_Electrons_twoJ = tfile.Get('histo2D__QCDFakes_DATA__Electrons_End1_2Jet_TrkIsoHEEP7vsPt_PAS')
#histo2D_Data_twoJ = tfile.Get('histo2D__QCDFakes_DATA__Total_End1_2Jet_TrkIsoHEEP7vsPt_PAS')
##histo2D_Jets_twoJ = tfile.Get('histo2D__QCDFakes_DATA__Jets_Bar_2Jet_TrkIsoHEEP7vsPt_PAS')
##histo2D_Electrons_twoJ = tfile.Get('histo2D__QCDFakes_DATA__Electrons_Bar_2Jet_TrkIsoHEEP7vsPt_PAS')
##histo2D_Data_twoJ = tfile.Get('histo2D__QCDFakes_DATA__Total_Bar_2Jet_TrkIsoHEEP7vsPt_PAS')
#
#proj_DY_twoJ = histo2D_DY_twoJ.ProjectionY('DYTwoJTrkIso',histo2D_DY_twoJ.GetXaxis().FindBin(lowEnd),histo2D_DY_twoJ.GetXaxis().FindBin(highEnd))
#proj_Electrons_twoJ = histo2D_Electrons_twoJ.ProjectionY('ElesTwoJTrkIso',histo2D_Electrons_twoJ.GetXaxis().FindBin(lowEnd),histo2D_Electrons_twoJ.GetXaxis().FindBin(highEnd)-1)
#proj_Jets_twoJ = histo2D_Jets_twoJ.ProjectionY('JetsTwoJTrkIso',histo2D_Jets_twoJ.GetXaxis().FindBin(lowEnd),histo2D_Jets_twoJ.GetXaxis().FindBin(highEnd)-1)
#proj_Data_twoJ = histo2D_Data_twoJ.ProjectionY('DataTwoJTrkIso',histo2D_Data_twoJ.GetXaxis().FindBin(lowEnd),histo2D_Data_twoJ.GetXaxis().FindBin(highEnd)-1)
#
#proj_DY_twoJ.SetLineColor(kBlue)
#proj_DY_twoJ.SetMarkerColor(kBlue)
#proj_DY_twoJ.SetLineStyle(2)
#proj_DY_twoJ.SetLineWidth(2)
#proj_Jets_twoJ.SetLineColor(kRed)
#proj_Jets_twoJ.SetMarkerColor(kRed)
#proj_Jets_twoJ.SetLineStyle(2)
#proj_Jets_twoJ.SetLineWidth(2)
#proj_Data_twoJ.SetLineColor(kBlue)
#proj_Data_twoJ.SetMarkerColor(kBlue)
#
#
#dyZeroJ = proj_DY_zeroJ.Integral(proj_DY_zeroJ.GetXaxis().FindBin(10),proj_DY_zeroJ.GetXaxis().FindBin(20)-1)
#eleZeroJ = proj_Electrons_zeroJ.Integral(proj_Electrons_zeroJ.GetXaxis().FindBin(10),proj_Electrons_zeroJ.GetXaxis().FindBin(20)-1)
#dataZeroJ_SB = proj_Data_zeroJ.Integral(proj_Data_zeroJ.GetXaxis().FindBin(10),proj_Data_zeroJ.GetXaxis().FindBin(20)-1)
#dataZeroJ = proj_Data_zeroJ.Integral()
#jetsZeroJ_SB = proj_Jets_zeroJ.Integral(proj_Jets_zeroJ.GetXaxis().FindBin(10),proj_Jets_zeroJ.GetXaxis().FindBin(20)-1)
#jetsZeroJ_SR = proj_Jets_zeroJ.Integral(proj_Jets_zeroJ.GetXaxis().FindBin(0),proj_Jets_zeroJ.GetXaxis().FindBin(5)-1)
##print 'endcap1 N_jet>=0: Nele=',eleZeroJ,'data=',dataZeroJ,'contam=',eleZeroJ/dataZeroJ
#print 'barrel N_jet>=0: Nele=',eleZeroJ,'data=',dataZeroJ,'contam=',eleZeroJ/dataZeroJ_SB
#print 'barrel N_jet>=0: nHEEPprime=',eleZeroJ,'jetsSR=',jetsZeroJ_SR,'jetsSB=',jetsZeroJ_SB,'data=',dataZeroJ
#print 'FR=',((jetsZeroJ_SR/jetsZeroJ_SB) * eleZeroJ)/dataZeroJ
#
#dyTwoJ = proj_DY_twoJ.Integral(proj_DY_twoJ.GetXaxis().FindBin(10),proj_DY_twoJ.GetXaxis().FindBin(20)-1)
#eleTwoJ = proj_Electrons_twoJ.Integral(proj_Electrons_twoJ.GetXaxis().FindBin(10),proj_Electrons_twoJ.GetXaxis().FindBin(20)-1)
#dataTwoJ_SB = proj_Data_twoJ.Integral(proj_Data_twoJ.GetXaxis().FindBin(10),proj_Data_twoJ.GetXaxis().FindBin(20)-1)
#dataTwoJ = proj_Data_twoJ.Integral()
#jetsTwoJ_SB = proj_Jets_twoJ.Integral(proj_Jets_twoJ.GetXaxis().FindBin(10),proj_Jets_twoJ.GetXaxis().FindBin(20)-1)
#jetsTwoJ_SR = proj_Jets_twoJ.Integral(proj_Jets_twoJ.GetXaxis().FindBin(0),proj_Jets_twoJ.GetXaxis().FindBin(5)-1)
##print 'endcap1 N_jet>=2: Nele=',eleTwoJ,'data=',dataTwoJ,'contam=',eleTwoJ/dataTwoJ
#print 'barrel N_jet>=2: Nele=',eleTwoJ,'data=',dataTwoJ,'contam=',eleTwoJ/dataTwoJ_SB
#print 'barrel N_jet>=2: nHEEPprime=',eleTwoJ,'jetsSR=',jetsTwoJ_SR,'jetsSB=',jetsTwoJ_SB,'data=',dataTwoJ
#print 'FR=',((jetsTwoJ_SR/jetsTwoJ_SB) * eleTwoJ)/dataTwoJ
#
#
#can = TCanvas()
#can.cd()
#can.SetLogy()
#proj_Jets_zeroJ.Scale(eleZeroJ/jetsZeroJ_SB)
#proj_JetsEle_zeroJ = proj_Jets_zeroJ.Clone()
#proj_JetsEle_zeroJ.SetName('JetsEleZeroJTrkIso')
#proj_JetsEle_zeroJ.Add(proj_Electrons_zeroJ)
#proj_JetsEle_zeroJ.SetLineStyle(2)
#proj_JetsEle_zeroJ.SetLineWidth(1)
#proj_JetsEle_zeroJ.SetLineColor(1)
#proj_JetsEle_zeroJ.SetMarkerColor(1)
#proj_Data_zeroJ.Draw()
##proj_Data_zeroJ.GetXaxis().SetRangeUser(0,50)
#proj_Data_zeroJ.GetYaxis().SetRangeUser(1e0,2e7)
#proj_DY_zeroJ.Draw('samehist')
#proj_Jets_zeroJ.Draw('samehist')
#proj_JetsEle_zeroJ.Draw('samehist')
#proj_Electrons_zeroJ.Draw('samehist')
#
#can2 = TCanvas()
#can2.cd()
#can2.SetLogy()
#proj_Jets_twoJ.Scale(eleTwoJ/jetsTwoJ_SB)
#proj_JetsEle_twoJ = proj_Jets_twoJ.Clone()
#proj_JetsEle_twoJ.SetName('JetsEleTwoJTrkIso')
#proj_JetsEle_twoJ.Add(proj_Electrons_twoJ)
#proj_JetsEle_twoJ.SetLineStyle(2)
#proj_JetsEle_twoJ.SetLineWidth(1)
#proj_JetsEle_twoJ.SetLineColor(1)
#proj_JetsEle_twoJ.SetMarkerColor(1)
#proj_Data_twoJ.Draw()
##proj_Data_twoJ.GetXaxis().SetRangeUser(0,50)
#proj_Data_twoJ.GetYaxis().SetRangeUser(1e0,2e7)
#proj_DY_twoJ.Draw('samehist')
#proj_Jets_twoJ.Draw('samehist')
#proj_JetsEle_twoJ.Draw('samehist')
#proj_Electrons_twoJ.Draw('samehist')
#
