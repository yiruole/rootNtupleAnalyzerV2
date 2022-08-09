#!/usr/bin/env python3
import ROOT
import copy


# def fillhist(hist, events, xs):
#     sumW = 0
#     for iev, event in enumerate(events):
#         event.getByLabel("externalLHEProducer", lheHandle)
#     hist.Scale(xs / sumW)

def AddRatioPlot(histNum, histDen):
    h_ratio = copy.deepcopy(histNum)
    h_ratio.Divide(histDen)
    h_ratio.GetXaxis().SetTitle("")
    h_ratio.GetXaxis().SetLabelSize(0.1)
    h_ratio.GetYaxis().SetRangeUser(0.0, 2)
    h_ratio.GetYaxis().SetTitle(histNum.GetTitle()+"/"+histDen.GetTitle())
    h_ratio.GetYaxis().SetLabelSize(0.1)
    h_ratio.GetYaxis().SetTitleSize(0.13)
    h_ratio.GetYaxis().SetTitleOffset(0.3)
    h_ratio.GetYaxis().SetNdivisions(504)
    h_ratio.SetMarkerStyle(1)
    h_ratio.SetLineWidth(3)
    h_ratio.GetXaxis().SetLimits(
        histNum.GetXaxis().GetXmin(),
        histNum.GetXaxis().GetXmax(),
    )
    return h_ratio


def isHardProcess(statusFlags):
    return (statusFlags >> 7) & 0x1


def fillhistgenparticles(hist, histGenParticles, tree, xs, maxEvents=-1):
    print("fillhistgenparticles:", hist.GetName())
    if maxEvents > 0:
        print("Run over", maxEvents, "events only.")
    nevents = tree.GetEntries()
    sumW = 0
    for iev, event in enumerate(tree):
        if maxEvents > 0 and iev >= maxEvents:
            break
        if iev < 10 or iev % 10000 == 0:
            print("event {}/{}".format(iev, nevents))
        weight = 1 if event.LHEWeight_originalXWGTUP > 0 else -1
        sumW += weight

        nZlep = 0
        p4 = lorentz()
        for i in range(event.nGenPart):
            if abs(event.GenPart_pdgId[i]) in [11, 13, 15] and isHardProcess(event.GenPart_statusFlags[i]):
                nZlep += 1
                p4 += lorentz(event.GenPart_pt[i], event.GenPart_eta[i], event.GenPart_phi[i], event.GenPart_mass[i])
        if nZlep == 2:
            histGenParticles.Fill(p4.pt(), weight)
        else:
            print("bad event for gen particles", iev)
            # for i in range(lheParticles.NUP):
            #    print "part %d id %d pt %f" % (i, lheParticles.IDUP[i], lhep4(i).pt())

        def lhep4(i):
            pt = event.LHEPart_pt[i]
            eta = event.LHEPart_eta[i]
            phi = event.LHEPart_phi[i]
            mass = event.LHEPart_mass[i]
            return lorentz(pt, eta, phi, mass)

        nZlep = 0
        p4 = lorentz()
        for i in range(event.nLHEPart):
            if abs(event.LHEPart_pdgId[i]) in [11, 13, 15]:
                nZlep += 1
                p4 += lhep4(i)
        if nZlep == 2:
            hist.Fill(p4.pt(), weight)
        else:
            print("bad event (LHE)")
            for i in range(event.nLHEPart):
                print("part %d id %d pt %f" % (i, event.LHEPart_pdgId[i], lhep4(i).pt()))
    if hist.GetEntries() < 1:
        raise RuntimeError("Didn't put a single entry in the histogram!")
    hist.Scale(xs / sumW)
    histGenParticles.Scale(xs / sumW)


ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

# lorentz = ROOT.Math.LorentzVector("ROOT::Math::PxPyPzE4D<double>")
lorentz = ROOT.Math.LorentzVector("ROOT::Math::PtEtaPhiM4D<double>")

hists = []
hInclusive = ROOT.TH1D("Inclusive", "Inclusive;Z p_{T};Counts / fb", 400, 0, 400)
hInclusive.SetLineColor(ROOT.kBlack)
# ROOT.SetOwnership(hInclusive, True)
hInclusiveGenParts = ROOT.TH1D(
    "InclusiveGenParts", "Inclusive (gen parts);Z p_{T};Counts / fb", 400, 0, 400
)
hInclusiveGenParts.SetLineColor(ROOT.kBlack)
hists.extend([hInclusive, hInclusiveGenParts])

h0to50 = ROOT.TH1D(
    "h0to50", "0 #leq p_{T} #leq 50;Z p_{T};Counts / fb", 400, 0, 400
)
h0to50.SetLineColor(ROOT.kRed)
h0to50GenParts = ROOT.TH1D(
    "h0to50GenParts",
    "0 #leq p_{T} #leq 50 (gen parts);Z p_{T};Counts / fb",
    400,
    0,
    400,
)
h0to50GenParts.SetLineColor(ROOT.kRed)
hists.extend([h0to50, h0to50GenParts])

h50to100 = ROOT.TH1D(
    "h50to100", "50 #leq p_{T} #leq 100;Z p_{T};Counts / fb", 400, 0, 400
)
h50to100.SetLineColor(ROOT.kCyan)
h50to100GenParts = ROOT.TH1D(
    "h50to100GenParts",
    "50 #leq p_{T} #leq 100 (gen parts);Z p_{T};Counts / fb",
    400,
    0,
    400,
)
h50to100GenParts.SetLineColor(ROOT.kCyan)
hists.extend([h50to100, h50to100GenParts])

h100to250 = ROOT.TH1D(
    "h100to250", "100 #leq p_{T} #leq 250;Z p_{T};Counts / fb", 400, 0, 400
)
h100to250.SetLineColor(ROOT.kGreen)
h100to250GenParts = ROOT.TH1D(
    "h100to250GenParts",
    "100 #leq p_{T} #leq 250 (gen parts);Z p_{T};Counts / fb",
    400,
    0,
    400,
)
h100to250GenParts.SetLineColor(ROOT.kGreen)
hists.extend([h100to250, h100to250GenParts])

h250to400 = ROOT.TH1D(
    "h250to400", "250 #leq p_{T} #leq 400;Z p_{T};Counts / fb", 400, 0, 400
)
h250to400.SetLineColor(ROOT.kBlue)
h250to400GenParts = ROOT.TH1D(
    "h250to400GenParts",
    "250 #leq p_{T} #leq 400 (gen parts);Z p_{T};Counts / fb",
    400,
    0,
    400,
)
h250to400GenParts.SetLineColor(ROOT.kBlue)
hists.extend([h250to400, h250to400GenParts])

filesInclusive = [
    "root://xrootd-cms.infn.it//store/mc/RunIISummer20UL16NanoAODAPVv9/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_preVFP_v11-v1/280000/C525CC6D-E4E1-8049-8026-F83981CFDAD0.root",
    "root://xrootd-cms.infn.it//store/mc/RunIISummer20UL16NanoAODAPVv9/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_preVFP_v11-v1/130000/C8960732-51C4-ED4A-949E-9D350691F86A.root"
]
treeInclusive = ROOT.TChain("Events")
for tfile in filesInclusive:
    treeInclusive.Add(tfile)
fillhistgenparticles(hInclusive, hInclusiveGenParts, treeInclusive, 6077.22 * 1e3, -1)  # run over all events in inclusive files
# fillhist(hInclusive, eventsInclusive, 5938. * 1e3)

maxEvents = 100000
files0to50 = [
    "root://xrootd-cms.infn.it//store/mc/RunIISummer20UL16NanoAODAPVv9/DYJetsToLL_LHEFilterPtZ-0To50_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_preVFP_v11-v1/40000/89D88E5C-9C5A-FA43-9E74-DA095E3971FA.root"
]
tree0to50 = ROOT.TChain("Events")
for tfile in files0to50:
    tree0to50.Add(tfile)
# fillhist(h0to50, events0to50, 354.6 * 1e3)
fillhistgenparticles(h0to50, h0to50GenParts, tree0to50, 1413.28 * 1e3, maxEvents)

files50to100 = [
    "root://xrootd-cms.infn.it//store/mc/RunIISummer20UL16NanoAODAPVv9/DYJetsToLL_LHEFilterPtZ-50To100_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_preVFP_v11-v1/2430000/34805E2E-21CE-904C-AFBD-AB3947EB0A59.root"
]
tree50to100 = ROOT.TChain("Events")
for tfile in files50to100:
    tree50to100.Add(tfile)
# fillhist(h50to100, events50to100, 354.6 * 1e3)
fillhistgenparticles(h50to100, h50to100GenParts, tree50to100, 377.081 * 1e3, maxEvents)

files100to250 = [
    "root://xrootd-cms.infn.it//store/mc/RunIISummer20UL16NanoAODAPVv9/DYJetsToLL_LHEFilterPtZ-100To250_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_preVFP_v11-v1/70000/20F86E63-3AFA-6B40-9561-FDFC83F27D58.root"
]
tree100to250 = ROOT.TChain("Events")
for tfile in files100to250:
    tree100to250.Add(tfile)
# fillhist(h100to250, events100to250, 83.05 * 1e3)
fillhistgenparticles(h100to250, h100to250GenParts, tree100to250, 91.6837 * 1e3, maxEvents)

files250to400 = [
    "root://xrootd-cms.infn.it//store/mc/RunIISummer20UL16NanoAODAPVv9/DYJetsToLL_LHEFilterPtZ-250To400_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_preVFP_v11-v1/50000/906A04B4-0FE8-4E4E-B4FA-B6D1633B2935.root"
]
tree250to400 = ROOT.TChain("Events")
for tfile in files250to400:
    tree250to400.Add(tfile)
# fillhist(h250to400, events250to400, 3.043 * 1e3)
fillhistgenparticles(h250to400, h250to400GenParts, tree250to400, 3.53037 * 1e3, maxEvents)

tfile = ROOT.TFile("ptStitchNano.root", "recreate")
tfile.cd()
can = ROOT.TCanvas()
can.cd()
hInclusive.Draw("histex0")
h0to50.Draw("histex0same")
h50to100.Draw("histex0same")
h100to250.Draw("histex0same")
h250to400.Draw("histex0same")
hstitched = h0to50.Clone("stitched")
hstitched.Add(h50to100)
hstitched.Add(h100to250)
hstitched.Add(h250to400)
hstitched.SetTitle("Stitched")
hstitched.SetLineColor(ROOT.kBlack)
hstitched.SetLineStyle(ROOT.kDashed)
hstitched.Draw("histex0same")
tfile.cd()
histRatio = AddRatioPlot(hInclusive, hstitched)
can.cd()
fPads1 = ROOT.TPad("pad1", "", 0.00, 0.20, 0.99, 0.99)
fPads2 = ROOT.TPad("pad2", "", 0.00, 0.00, 0.99, 0.20)
fPads1.SetFillColor(0)
fPads1.SetLineColor(0)
fPads2.SetFillColor(0)
fPads2.SetLineColor(0)
fPads1.Draw()
fPads2.Draw()
fPads1.cd()
hInclusive.Draw("histex0")
h0to50.Draw("histex0same")
h50to100.Draw("histex0same")
h100to250.Draw("histex0same")
h250to400.Draw("histex0same")
hstitched.Draw("histex0same")
fPads2.cd()
# fPads2.SetLogy()
fPads2.SetGridy()
histRatio.Draw("e0p")
lineAtOne = ROOT.TLine(histRatio.GetXaxis().GetXmin(), 1, histRatio.GetXaxis().GetXmax(), 1)
lineAtOne.SetLineColor(2)
lineAtOne.Draw()
can.Write("overlayStitchedAndComponents")
hInclusive.Write()
h0to50.Write()
h50to100.Write()
h100to250.Write()
h250to400.Write()
hstitched.Write()
hInclusiveGenParts.Write()
h0to50GenParts.Write()
h50to100GenParts.Write()
h100to250GenParts.Write()
h250to400GenParts.Write()
tfile.Close()

### wait for input to keep the GUI (which lives on a ROOT event dispatcher) alive
# if __name__ == '__main__':
#   rep = ''
#   while not rep in [ 'q', 'Q' ]:
#      rep = raw_input( 'enter "q" to quit: ' )
#      if 1 < len(rep):
#         rep = rep[0]
#
# ROOT.gPad.Print("ptStitch.root")
