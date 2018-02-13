#!/usr/bin/env python

from ROOT import *
import os

# ST thresholds: LQmass, ST threshold
stCutsEEJJ = {
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
File_preselectionEEJJ = TFile(os.environ["LQDATA"] + "/2016analysis/eejj_psk_feb10_bugfix/output_cutTable_lq_eejj/analysisClass_lq_eejj_plots.root")

File_preselectionENuJJ = TFile(os.environ["LQDATA"] + "/2016analysis/enujj_psk_feb10_v237_bugfix/output_cutTable_lq_enujj_MT/analysisClass_lq_enujj_MT_plots.root")



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
# eejj: last cut with nonzero event yield
# LQ750, --> ST > 1145 GeV
# scaling: int_STCutToInf_orig*SF = yield
#sample = 'SingleTop'
#evtYield = 1.4026892
#sTcut = stCuts[750]
#
sample='PhotonJets_Madgraph'
evtYield = 4.71
sTcut = stCuts[400]


# Run
hname = (histoBaseName_userDef.replace("SAMPLE", sample)).replace("VARIABLE", varName)
histo = File_preselection.Get(hname)
if not histo:
    print "ERROR: histo " + hName + " not found in " + File_preselection.GetName()

# rebin histo
histo.Rebin(2)
foundBin = histo.FindBin(sTcut)
#print 'bin for',sTcut,'GeV has low edge:',histo.GetBinLowEdge(foundBin),'and width',histo.GetBinWidth(foundBin)
#scaleFact = evtYield/histo.Integral(histo.FindBin(1290),histo.GetNbinsX())
#print 'scaleFact = ',evtYield,'/Int1290ToEnd','=',evtYield,'/',histo.Integral(histo.FindBin(1290),histo.GetNbinsX()),'=',scaleFact
#histo.Scale(scaleFact)
binWidth = histo.GetBinWidth(foundBin)
# fit
#expFitFunc = TF1("expFitFunc","expo(x)",300,3000);
expFitFunc = TF1("expFitFunc","expo(x)",700,3000);
if 'PhotonJets' in sample and doEEJJ:
  expFitFunc = TF1("expFitFunc","expo(x)",200,3000);
#expFitFunc.SetParameters(9,-1e-2)
histo.Fit(expFitFunc,"R")
print 'fitFunc param vals=',expFitFunc.GetParameter(0),expFitFunc.GetParameter(1)
print 'histoIntegral above',sTcut,':',histo.Integral(histo.FindBin(sTcut),histo.GetNbinsX())
print 'Fit function integral above',sTcut,' [LQ750]',expFitFunc.Integral(sTcut,histo.GetXaxis().GetXmax())/binWidth
scaleFact = evtYield/(expFitFunc.Integral(sTcut,histo.GetXaxis().GetXmax())/binWidth)
#print '[rescaled] Fit function integral above',sTcut,' [LQ750]',scaleFact*expFitFunc.Integral(sTcut,histo.GetXaxis().GetXmax())/binWidth
#print '[rescaled] Fit function integral above 1360 [LQ900]',scaleFact*expFitFunc.Integral(1360,histo.GetXaxis().GetXmax())/binWidth
for mass in sorted(stCuts.keys()):
  print '[rescaled] Fit function integral above',stCuts[mass],'[LQ'+str(mass)+']',scaleFact*expFitFunc.Integral(stCuts[mass],histo.GetXaxis().GetXmax())/binWidth
#can = TCanvas()
#can.cd()
#histo.Draw()
#c1.SetLogy()
histo.GetXaxis().SetTitle('sT [GeV]')
c1.Modified()
c1.Update()
c1.Print(varName+'_'+sample+'_'+('eejj' if doEEJJ else 'enujj')+'.pdf')
c1.Print(varName+'_'+sample+'_'+('eejj' if doEEJJ else 'enujj')+'.png')

#File_preselection.Close()
