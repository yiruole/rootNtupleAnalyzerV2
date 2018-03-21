#!/usr/bin/env python

from ROOT import *
import os
import array
import numpy


# ST thresholds: LQmass, ST threshold
stCutsEEJJ = {
        350: 550,
        400: 630,
        450: 705,
        500: 780,
        550: 855,
        600: 930,
        650: 1000,
        700: 1075,
        750: 1145,
        800: 1215,
        850: 1290,
        900: 1360,
        950: 1425,
        1000: 1495,
        1050: 1565,
}
stCutsENuJJ = {
        'preselection':300,
        200: 345,
        250: 440,
        300: 535,
        350: 630,
        400: 720,
        450: 805,
        500: 890,
        550: 970,
        600: 1045,
        650: 1125,
        700: 1195,
        750: 1265,
        800: 1330,
        850: 1395,
        900: 1460,
        950: 1515,
        1000: 1570,
        1050: 1625,
        1100: 1675,
        1150: 1720,
        1200: 1765,
}

# scaled
#File_preselectionEEJJ = TFile(os.environ["LQDATA"] + "/2016analysis/eejj_psk_jan26_gsfEtaCheck_finalSels/output_cutTable_lq_eejj/analysisClass_lq_eejj_plots.root")
#File_preselectionEEJJ = TFile(os.environ["LQDATA"] + "/2016analysis/eejj_psk_feb10_bugfix/output_cutTable_lq_eejj/analysisClass_lq_eejj_plots.root")
File_preselectionEEJJ = TFile(os.environ["LQDATA"] + "/2016analysis/eejj_psk_feb20_newSingTop/output_cutTable_lq_eejj/analysisClass_lq_eejj_plots.root")

#File_preselectionENuJJ = TFile(os.environ["LQDATA"] + "/2016analysis/enujj_psk_feb10_v237_bugfix/output_cutTable_lq_enujj_MT/analysisClass_lq_enujj_MT_plots.root")
File_preselectionENuJJ = TFile(os.environ["LQDATA"] + "/2016analysis/enujj_psk_feb14_dPhiEleMet0p8/output_cutTable_lq_enujj_MT/analysisClass_lq_enujj_MT_plots.root")



histoBaseName_userDef = "histo1D__SAMPLE__VARIABLE"

# make ST plot
doEEJJ=True
if doEEJJ:
    stCuts = stCutsEEJJ
    File_preselection = File_preselectionEEJJ
else:
    stCuts = stCutsENuJJ
    File_preselection = File_preselectionENuJJ
varName = 'sT_PAS'

####################################################################################################
# Configure which sample to use and its last threshold with at least one event
####################################################################################################
fitMin=300
# eejj: last cut with nonzero event yield
# LQ750, --> ST > 1145 GeV
# scaling: int_STCutToInf_orig*SF = yield
#sample = 'SingleTop'
#evtYield = 1.4026892
#sTcut = stCuts[750]
#
#sample='PhotonJets_Madgraph'
#evtYield = 4.71
#sTcut = stCuts[400]
#
# last cut with at least 5 MC events
sample='PhotonJets_Madgraph'
evtYield = 7.52 
mass = 350
sTcut = stCuts[mass]
#
#sample = 'SingleTop'
#evtYield = 9.24
#mass = 550
#sTcut = stCuts[mass]
#
#sample = 'WJet_amcatnlo_ptBinned'
#evtYield = 0.3903156
#mass = 750
#sTcut = stCuts[mass] # 19 events
#fitMin=600
######################
# ENuJJ
######################
#sample='PhotonJets_Madgraph'
#evtYield = 3.3
#mass = 600
#sTcut = stCuts[mass]
##
#sample='SingleTop'
##evtYield = 6.63
##mass = 700
##evtYield = 1.33
##evtYield = 14.73
##mass = 600
#evtYield = 1.33
#mass = 1200
##evtYield = 30.35
##mass = 500

#evtYield = 127.9
#mass = 350
#evtYield = 6122.69
#mass = 'preselection'
sTcut = stCuts[mass]
#fitMin=sTcut

renormalizeAfterParameterShifts = True

# Run
hname = (histoBaseName_userDef.replace("SAMPLE", sample)).replace("VARIABLE", varName)
histo = File_preselection.Get(hname)
if not histo:
    print "ERROR: histo " + hName + " not found in " + File_preselection.GetName()

# rebin histo
histo.Rebin(4)
#histo.Rebin(6)
#bins = range(0,1050,50)
#bins.extend(range(1100,1650,50))
#bins.extend([1700,1800,1900,2000,2200,2400,2600,2800,3000])
#histo = histo.Rebin(len(bins)-1,'histo2',array.array('d',bins))
foundBin = histo.FindBin(sTcut)
#print 'bin for',sTcut,'GeV has low edge:',histo.GetBinLowEdge(foundBin),'and width',histo.GetBinWidth(foundBin)
#scaleFact = evtYield/histo.Integral(histo.FindBin(1290),histo.GetNbinsX())
#print 'scaleFact = ',evtYield,'/Int1290ToEnd','=',evtYield,'/',histo.Integral(histo.FindBin(1290),histo.GetNbinsX()),'=',scaleFact
#histo.Scale(scaleFact)
binWidth = histo.GetBinWidth(foundBin)
# fit
stitchPoint = fitMin
if doEEJJ:
  expFitFunc = TF1("expFitFunc","expo",fitMin,stitchPoint)
  expFitFuncTail = TF1("expFitFunc","expo",stitchPoint,1565)
  fitFuncTotal = TF1("fitFuncTotal","expo(0)+expo(2)",fitMin,1565)
else:
  expFitFunc = TF1("expFitFunc","expo",fitMin,stitchPoint)
  expFitFuncTail = TF1("expFitFunc","expo",stitchPoint,5000)

#fitFuncTotal = TF1("fitFuncTotal","expo(0)*(x<="+str(stitchPoint)+")+expo(2)*(x>="+str(stitchPoint)+")",fitMin,1765)
#fitFuncTotal = TF1("fitFuncTotal","[2]*exp([3]-[1])*exp([1]*x)*(x<="+str(stitchPoint)+")+[2]*exp([3]*x)*(x>="+str(stitchPoint)+")",fitMin,1765)

#expFitFunc = TF1("expFitFunc","expo(x)",700,3000);
#if 'PhotonJets' in sample and doEEJJ:
#  expFitFunc = TF1("expFitFunc","expo(x)",200,3000);
#expFitFunc.SetParameters(9,-1e-2)

#expFitFunc.SetLineColor(kBlue)
#expFitFuncTail.SetLineColor(kGreen+1)
#histo.Fit(expFitFunc,"R")
fitFuncTotal = expFitFuncTail
#histo.Fit(expFitFuncTail,"L",'',stitchPoint,1765)
histo.Fit(expFitFuncTail,"L",'',stitchPoint,5000)

#params = expFitFunc.GetParameters()
#paramsTail = expFitFuncTail.GetParameters()
#print 'params=',params
#for i in range(0,2):
#    #fitFuncTotal.SetParameter(i,params[i])
#    fitFuncTotal.SetParameter(i+2,paramsTail[i])
print 'fitting fitFuncTotal'
#histo.Fit(fitFuncTotal,"R")

print 'fitFunc param vals=',fitFuncTotal.GetParameter(0),'+/-',fitFuncTotal.GetParError(0),';',fitFuncTotal.GetParameter(1),'+/-',fitFuncTotal.GetParError(1)
fitParam0 = fitFuncTotal.GetParameter(0)
fitParam1 = fitFuncTotal.GetParameter(1)
print 'histoIntegral above',sTcut,':',histo.Integral(histo.FindBin(sTcut),histo.GetNbinsX())
print 'unscaled fit function integral above',sTcut,'[LQ'+str(mass)+']',fitFuncTotal.Integral(sTcut,histo.GetXaxis().GetXmax())/binWidth
scaleFact = evtYield/(fitFuncTotal.Integral(sTcut,histo.GetXaxis().GetXmax())/binWidth)
#print '[rescaled] Fit function integral above',sTcut,' [LQ750]',scaleFact*fitFuncTotal.Integral(sTcut,histo.GetXaxis().GetXmax())/binWidth
#print '[rescaled] Fit function integral above 1360 [LQ900]',scaleFact*fitFuncTotal.Integral(1360,histo.GetXaxis().GetXmax())/binWidth
fitYields = dict()
for mass in sorted(stCuts.keys()):
  #print '[rescaled] Fit function integral above',stCuts[mass],'[LQ'+str(mass)+']',scaleFact*fitFuncTotal.Integral(stCuts[mass],histo.GetXaxis().GetXmax())/binWidth
  fitYields[mass] = scaleFact*fitFuncTotal.Integral(stCuts[mass],histo.GetXaxis().GetXmax())/binWidth
# shift up
fitFuncTotal.SetParameter(0,fitParam0+fitFuncTotal.GetParError(0))
fitFuncTotal.SetParameter(1,fitParam1+fitFuncTotal.GetParError(1))
if renormalizeAfterParameterShifts:
  scaleFact = evtYield/(fitFuncTotal.Integral(sTcut,histo.GetXaxis().GetXmax())/binWidth)
fitYieldsUpShift = dict()
for mass in sorted(stCuts.keys()):
  #print '[rescaled] Fit function integral above',stCuts[mass],'[LQ'+str(mass)+'] orig=',fitYields[mass],'shiftedUp:',scaleFact*fitFuncTotal.Integral(stCuts[mass],histo.GetXaxis().GetXmax())/binWidth
  fitYieldsUpShift[mass] = scaleFact*fitFuncTotal.Integral(stCuts[mass],histo.GetXaxis().GetXmax())/binWidth - fitYields[mass]
# shift down
fitFuncTotal.SetParameter(0,fitParam0-fitFuncTotal.GetParError(0))
fitFuncTotal.SetParameter(1,fitParam1-fitFuncTotal.GetParError(1))
if renormalizeAfterParameterShifts:
  scaleFact = evtYield/(fitFuncTotal.Integral(sTcut,histo.GetXaxis().GetXmax())/binWidth)
fitYieldsDownShift = dict()
for mass in sorted(stCuts.keys()):
  #print '[rescaled] Fit function integral above',stCuts[mass],'[LQ'+str(mass)+']',scaleFact*fitFuncTotal.Integral(stCuts[mass],histo.GetXaxis().GetXmax())/binWidth
  fitYieldsDownShift[mass] = fitYields[mass] - scaleFact*fitFuncTotal.Integral(stCuts[mass],histo.GetXaxis().GetXmax())/binWidth

for mass in sorted(stCuts.keys()):
  print '[rescaled] Fit function integral above',stCuts[mass],'[LQ'+str(mass)+']',fitYields[mass],'+',fitYieldsUpShift[mass],'-',fitYieldsDownShift[mass]
print
print

maxDev = dict()
for mass in sorted(stCuts.keys()):
  maxDev[mass] = max(abs(fitYieldsUpShift[mass]),abs(fitYieldsDownShift[mass]))
print 'LQ cut, fit yield, and max up/down varaiation from fit yield'
for mass in sorted(stCuts.keys()):
  print '[LQ'+str(mass)+']',fitYields[mass],'+/-',maxDev[mass],'relative=',maxDev[mass]/fitYields[mass]

#can = TCanvas()
#can.cd()
#histo.Draw()
c1.SetLogy()
histo.GetXaxis().SetTitle('sT [GeV]')
ps = c1.GetPrimitive("stats")
ps.SetY1NDC(0.68)
ps.SetY2NDC(0.99578)
c1.Modified()
c1.Update()
c1.Print(varName+'_'+sample+'_'+('eejj' if doEEJJ else 'enujj')+'.pdf')
c1.Print(varName+'_'+sample+'_'+('eejj' if doEEJJ else 'enujj')+'.png')

# make plot of yields
can = TCanvas()
can.cd()
if 'preselection' in fitYields.keys():
  del fitYields['preselection']
  del maxDev['preselection']
sortedMasses = sorted(fitYields.keys())
sortedFitYields = [fitYields[mass] for mass in sortedMasses]
sortedMaxDev = [maxDev[mass] for mass in sortedMasses]
fitGraph = TGraphErrors(len(sortedFitYields),array.array('d',sortedMasses),array.array('d',sortedFitYields),array.array('d',[0]*len(fitYields)),array.array('d',sortedMaxDev))
## from table
#eventYields = { 200: 5143.31, 250:507.36, 300:244.05, 350:127.9, 400:61.77, 450:40.23, 500:30.35, 550:21.35, 600:14.73, 650:10.77, 700:6.63, 750:4.0, 800:4.0, 850:2.65, 900:2.65, 950:2.65, 1000:2.65, 1050:2.65, 1100:1.33, 1150:1.33, 1200:1.33}
#eventErrs = { 200: 74.31, 250:24.91, 300:17.33, 350:12.73, 400:9.01, 450:7.23, 500:6.35, 550:5.34, 600:4.44, 650:5.31, 700:4.48, 750:3.89, 800:3.89, 850:3.49, 900:3.49, 950:3.49, 1000:3.49, 1050:3.49, 1100:3.05, 1150:3.05, 1200:3.05  }
# eejj gamma+jets ST, feb20
eventYields = { 200:37.65, 250:20.82, 300:12.83, 350:7.52, 400:4.71, 450:0.0, 500:0.0, 550:0.0, 600:0.0, 650:0.0, 700:0.0, 750:0.0, 800:0.0, 850:0.0, 900:0.0, 950:0.0, 1000:0.0, 1050:0.0}
eventErrs = { 200:10.94, 250:7.45, 300:5.86, 350:5.09, 400:4.58, 450:2.89, 500:2.89, 550:2.89, 600:2.89, 650:2.89, 700:2.89, 750:2.89, 800:2.89, 850:2.89, 900:2.89, 950:2.89, 1000:2.89, 1050:2.89}
sortedEventYields = [eventYields[mass] for mass in sortedMasses]
sortedEventErrs = [eventErrs[mass] for mass in sortedMasses]
mcGraph = TGraphErrors(len(sortedEventYields),array.array('d',sortedMasses),array.array('d',sortedEventYields),array.array('d',[0]*len(fitYields)),array.array('d',sortedEventErrs))
fitGraph.SetLineColor(kRed)
fitGraph.SetLineStyle(2)
fitGraph.SetMarkerColor(kRed)
mcGraph.SetTitle('')
mcGraph.Draw('ap')
#mcGraph.GetYaxis().SetRangeUser(1,1e5)
mcGraph.GetYaxis().SetRangeUser(1e-2,1e3)
mcGraph.GetXaxis().SetTitle('M_{LQ} [GeV]')
can.SetLogy()
fitGraph.Draw('samep')
leg = TLegend(0.2,0.2,0.4,0.4)
leg.SetBorderSize(0)
leg.AddEntry(mcGraph,'MC yield','l')
leg.AddEntry(fitGraph,'Fit yield','l')
leg.Draw('same')


#File_preselection.Close()

