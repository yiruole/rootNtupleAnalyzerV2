#!/usr/bin/env python
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True
from DataFormats.FWLite import Handle, Runs, Lumis, Events
import sys
import math

lorentz = ROOT.Math.LorentzVector('ROOT::Math::PxPyPzE4D<double>')

lheHandle = Handle('LHEEventProduct')
genPartHandle = Handle('vector<reco::GenParticle>')

tfile = ROOT.TFile("ptStitch.root","recreate")
tfile.cd()
hInclusive = ROOT.TH1D("Inclusive", "Inclusive;Z p_{T};Counts / fb", 400, 0, 400)
hInclusive.SetLineColor(ROOT.kBlack)
hInclusiveGenParts = ROOT.TH1D("InclusiveGenParts", "Inclusive (gen parts);Z p_{T};Counts / fb", 400, 0, 400)
hInclusiveGenParts.SetLineColor(ROOT.kBlack)
h50to100 = ROOT.TH1D("h50to100", "50 #leq p_{T} #leq 100;Z p_{T};Counts / fb", 400, 0, 400)
h50to100.SetLineColor(ROOT.kRed)
h50to100GenParts = ROOT.TH1D("h50to100GenParts", "50 #leq p_{T} #leq 100 (gen parts);Z p_{T};Counts / fb", 400, 0, 400)
h50to100GenParts.SetLineColor(ROOT.kRed)
h100to250 = ROOT.TH1D("h100to250", "100 #leq p_{T} #leq 250;Z p_{T};Counts / fb", 400, 0, 400)
h100to250.SetLineColor(ROOT.kGreen)
h100to250GenParts= ROOT.TH1D("h100to250GenParts", "100 #leq p_{T} #leq 250 (gen parts);Z p_{T};Counts / fb", 400, 0, 400)
h100to250GenParts.SetLineColor(ROOT.kGreen)
h250to400 = ROOT.TH1D("h250to400", "250 #leq p_{T} #leq 400;Z p_{T};Counts / fb", 400, 0, 400)
h250to400.SetLineColor(ROOT.kBlue)
h250to400GenParts= ROOT.TH1D("h250to400GenParts", "250 #leq p_{T} #leq 400 (gen parts);Z p_{T};Counts / fb", 400, 0, 400)
h250to400GenParts.SetLineColor(ROOT.kBlue)

def fillhist(hist, events, xs):
    sumW = 0
    for iev, event in enumerate(events):
        event.getByLabel('externalLHEProducer', lheHandle)
    hist.Scale(xs/sumW)


def fillhistgenparticles(hist, histGenParticles, events, xs):
    sumW = 0
    for iev, event in enumerate(events):
        event.getByLabel('prunedGenParticles', genPartHandle)
        genParts = genPartHandle.product()
        #
        event.getByLabel('externalLHEProducer', lheHandle)
        lhe = lheHandle.product()
        weight = 1 if lhe.originalXWGTUP() > 0 else -1
        sumW += weight

        nZlep = 0
        p4 = lorentz()
        for part in genParts:
            if abs(part.pdgId()) in [11,13,15] and part.isHardProcess():
                nZlep += 1
                p4 += lorentz(part.px(),part.py(),part.pz(),part.energy())
        if nZlep == 2:
            histGenParticles.Fill(p4.pt(), weight)
        else:
            print "bad event for gen particles",iev
            #for i in range(lheParticles.NUP):
            #    print "part %d id %d pt %f" % (i, lheParticles.IDUP[i], lhep4(i).pt())

        lheParticles = lhe.hepeup()
        def lhep4(i):
            px = lheParticles.PUP.at(i)[0]
            py = lheParticles.PUP.at(i)[1]
            pz = lheParticles.PUP.at(i)[2]
            pE = lheParticles.PUP.at(i)[3]
            return lorentz(px, py, pz, pE)

        nZlep = 0
        p4 = lorentz()
        for i in range(lheParticles.NUP):
            if abs(lheParticles.IDUP[i]) in [11, 13, 15]:
                nZlep += 1
                p4 += lhep4(i)
        if nZlep == 2:
            hist.Fill(p4.pt(), weight)
        else:
            print "bad event (LHE)"
            for i in range(lheParticles.NUP):
                print "part %d id %d pt %f" % (i, lheParticles.IDUP[i], lhep4(i).pt())
    hist.Scale(xs/sumW)
    histGenParticles.Scale(xs/sumW)


eventsInclusive = Events([
  'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/005ED0EB-79F1-E611-B6DA-02163E011C2B.root',
  'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/00E54BE4-21E5-E611-BD4D-0025905A60B6.root',
  'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/00FDA2F7-B4E3-E611-95C1-FA163EA38D84.root',
  'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/02021E37-7CF1-E611-BC63-02163E0145C4.root',
  'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/0218D123-CAE3-E611-8C5D-0025907277BE.root',
  'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/028E0C9A-6CF1-E611-B270-02163E019D38.root',
  'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/0428BB30-7FE4-E611-9E20-00266CFCCBC8.root',
  'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/043F2AAA-57E4-E611-9A99-B083FED18596.root',
  'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/045CF731-5CE6-E611-B2B5-0025904C66EC.root',
  'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/04BE60BB-4BE3-E611-B951-0CC47A4C8F1C.root',
])
fillhistgenparticles(hInclusive, hInclusiveGenParts, eventsInclusive, 5938. * 1e3)
#fillhist(hInclusive, eventsInclusive, 5938. * 1e3)

events50to100 = Events([
    'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-50To100_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/100000/00E3D7B3-9DCE-E611-A42D-0025905A609A.root',
    'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-50To100_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/100000/0462F883-C0CE-E611-8CEE-0CC47A4D764A.root',
    'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-50To100_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/100000/0E1E6882-A0CE-E611-BB4A-0CC47A7452D0.root',
    'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-50To100_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/100000/0EC51971-9FCE-E611-A1FE-0025905B85FC.root',
])
#fillhist(h50to100, events50to100, 354.6 * 1e3)
fillhistgenparticles(h50to100, h50to100GenParts, events50to100, 354.6 * 1e3)

events100to250 = Events([
    'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-100To250_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/120000/104AF025-6DCB-E611-BFB4-0025904B8708.root',
    'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-100To250_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/120000/2029BD2C-7DCB-E611-8E08-0025904A87E2.root',
    'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-100To250_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/120000/20E39922-6ECB-E611-8C93-0025904C7F80.root',
    'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-100To250_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/120000/28BA2C57-7CCB-E611-BECC-0025901D4894.root',
])
#fillhist(h100to250, events100to250, 83.05 * 1e3)
fillhistgenparticles(h100to250, h100to250GenParts, events100to250, 83.05 * 1e3)

events250to400 = Events([
    'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-250To400_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/120000/0A953D30-0BCD-E611-B4CB-0CC47AD99112.root',
])
#fillhist(h250to400, events250to400, 3.043 * 1e3)
fillhistgenparticles(h250to400, h250to400GenParts, events250to400, 3.043 * 1e3)

hInclusive.Draw('histex0')
h50to100.Draw('histex0same')
h100to250.Draw('histex0same')
h250to400.Draw('histex0same')
hstitched = h50to100.Clone("stitched")
hstitched.Add(h100to250)
hstitched.Add(h250to400)
hstitched.SetTitle("Stitched")
hstitched.SetLineColor(ROOT.kBlack)
hstitched.SetLineStyle(ROOT.kDashed)
hstitched.Draw('histex0same')
tfile.cd()
hInclusive.Write()
h50to100.Write()
h100to250.Write()
h250to400.Write()
hstitched.Write()
hInclusiveGenParts.Write()
h50to100GenParts.Write()
h100to250GenParts.Write()
h250to400GenParts.Write()
#tfile.Write()
tfile.Close()

### wait for input to keep the GUI (which lives on a ROOT event dispatcher) alive
#if __name__ == '__main__':
#   rep = ''
#   while not rep in [ 'q', 'Q' ]:
#      rep = raw_input( 'enter "q" to quit: ' )
#      if 1 < len(rep):
#         rep = rep[0]
#
#ROOT.gPad.Print("ptStitch.root")

