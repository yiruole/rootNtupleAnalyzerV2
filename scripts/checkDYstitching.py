#!/usr/bin/env python
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True
from DataFormats.FWLite import Handle, Runs, Lumis, Events

lorentz = ROOT.Math.LorentzVector("ROOT::Math::PxPyPzE4D<double>")

lheHandle = Handle("LHEEventProduct")
genPartHandle = Handle("vector<reco::GenParticle>")

tfile = ROOT.TFile("ptStitch.root", "recreate")
tfile.cd()
hInclusive = ROOT.TH1D("Inclusive", "Inclusive;Z p_{T};Counts / fb", 400, 0, 400)
hInclusive.SetLineColor(ROOT.kBlack)
hInclusiveGenParts = ROOT.TH1D(
    "InclusiveGenParts", "Inclusive (gen parts);Z p_{T};Counts / fb", 400, 0, 400
)
hInclusiveGenParts.SetLineColor(ROOT.kBlack)
h50to100 = ROOT.TH1D(
    "h50to100", "50 #leq p_{T} #leq 100;Z p_{T};Counts / fb", 400, 0, 400
)
h50to100.SetLineColor(ROOT.kRed)
h50to100GenParts = ROOT.TH1D(
    "h50to100GenParts",
    "50 #leq p_{T} #leq 100 (gen parts);Z p_{T};Counts / fb",
    400,
    0,
    400,
)
h50to100GenParts.SetLineColor(ROOT.kRed)
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


def fillhist(hist, events, xs):
    sumW = 0
    for iev, event in enumerate(events):
        event.getByLabel("externalLHEProducer", lheHandle)
    hist.Scale(xs / sumW)


def fillhistgenparticles(hist, histGenParticles, events, xs):
    print "fillhistgenparticles:", hist.GetName()
    nevents = events.size()
    sumW = 0
    for iev, event in enumerate(events):
        if iev < 10 or iev % 10000 == 0:
            print "event {}/{}".format(iev, nevents)
        event.getByLabel("prunedGenParticles", genPartHandle)
        genParts = genPartHandle.product()
        #
        event.getByLabel("externalLHEProducer", lheHandle)
        lhe = lheHandle.product()
        weight = 1 if lhe.originalXWGTUP() > 0 else -1
        sumW += weight

        nZlep = 0
        p4 = lorentz()
        for part in genParts:
            if abs(part.pdgId()) in [11, 13, 15] and part.isHardProcess():
                nZlep += 1
                p4 += lorentz(part.px(), part.py(), part.pz(), part.energy())
        if nZlep == 2:
            histGenParticles.Fill(p4.pt(), weight)
        else:
            print "bad event for gen particles", iev
            # for i in range(lheParticles.NUP):
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
    hist.Scale(xs / sumW)
    histGenParticles.Scale(xs / sumW)


eventsInclusive = Events(
    [
        "root://eoscms//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/00000/CE864285-6D1C-E911-B09D-34E6D7BDDECE.root",
        "root://eoscms//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/40000/CC4D4979-F736-E911-9AE1-90E2BACC5EEC.root",
        "root://eoscms//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/90000/282A4EC8-BB36-E911-AA75-90E2BAD4912C.root",
        "root://eoscms//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/90000/66DD4E86-AB37-E911-85F4-68B59972C37E.root",
        "root://eoscms//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/40000/66F2283A-0135-E911-A1E4-1CB72C1B2EF4.root",
        "root://eoscms//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/40000/E8F1C063-4035-E911-B53B-AC1F6B8DBE02.root",
        "root://eoscms//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/40000/3E58AC7C-0B36-E911-A451-0425C5902FCA.root",
        "root://eoscms//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/90000/9AF1A53D-9632-E911-BD9A-AC1F6B4D245C.root",
        "root://eoscms//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/90000/D4158DA0-4233-E911-B703-C0BFC0E56866.root",
        "root://eoscms//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/90000/724D5D61-A933-E911-A513-68CC6EA5BE82.root",
    ]
)
fillhistgenparticles(hInclusive, hInclusiveGenParts, eventsInclusive, 5938.0 * 1e3)
# fillhist(hInclusive, eventsInclusive, 5938. * 1e3)

events50to100 = Events(
    [
        "file:/tmp/scooper/56D1543D-4EF3-E911-89BB-0CC47A5450DA.root"
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/230000/56D1543D-4EF3-E911-89BB-0CC47A5450DA.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/230000/8838022A-D4F3-E911-8703-0CC47A5450DA.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/230000/A8663628-21F4-E911-A024-0025904CF972.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/230000/B09DFDC5-36F4-E911-A6AB-0025904AAADC.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/230000/F03A7FFA-3EF4-E911-BE37-0CC47A206FCC.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/230000/CE631322-40F4-E911-BFF1-0CC47A206FCC.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/230000/02F7BF07-55F4-E911-93DA-0CC47A544F5A.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/230000/3E5AF60E-55F4-E911-BCAA-0CC47A544F5A.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/230000/CE19D655-5CF4-E911-BAC9-0CC47A545060.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/230000/E496B560-5CF4-E911-8264-0CC47A544E12.root",
    ]
)
# fillhist(h50to100, events50to100, 354.6 * 1e3)
fillhistgenparticles(h50to100, h50to100GenParts, events50to100, 354.6 * 1e3)

events100to250 = Events(
    [
        "file:/tmp/scooper/9E13A5E8-FDF4-E911-AA49-0CC47A166D66.root"
        #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/9E13A5E8-FDF4-E911-AA49-0CC47A166D66.root",
        #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/F672A768-36F6-E911-B8A2-0CC47A545062.root",
        #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/206E3D80-E1FA-E911-A732-B4E10FA31EFB.root",
        #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/DA27F6B0-88FB-E911-9D1D-AC1F6B23C86A.root",
        #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/EA2181B9-74F9-E911-B6FB-AC1F6B23C812.root",
        #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/528140DC-21F8-E911-A3C5-B4E10FA326F5.root",
        #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/F046C874-89F8-E911-A7D8-0CC47AB64E82.root",
        #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/240000/72D46964-B4FF-E911-971C-9CDC7149F810.root",
        #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/240000/3203817B-3101-EA11-AF39-5065F3810301.root",
        #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/240000/04E1D919-2200-EA11-9E97-90B11C4F4FDD.root",
    ]
)
# fillhist(h100to250, events100to250, 83.05 * 1e3)
fillhistgenparticles(h100to250, h100to250GenParts, events100to250, 83.05 * 1e3)

events250to400 = Events(
    [
        "file:/tmp/scooper/DA15F363-55EB-E911-91C9-FA163ECA5E6C.root"
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/DA15F363-55EB-E911-91C9-FA163ECA5E6C.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/96B7586A-68EB-E911-919F-FA163EE2F234.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/2AD7CEAD-78EB-E911-89BC-FA163E3EDAC5.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/C85D4CD5-86EB-E911-9BC4-FA163ECF53CC.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/92915792-8EEB-E911-85EB-FA163EE9E154.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/6ABE0930-A8EB-E911-B837-FA163EA4B9E2.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/061D34A9-B9EB-E911-9CEE-FA163EB3C8D0.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/FED51120-D2EB-E911-8BDD-FA163EEA7CAB.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/9E5E6569-E4EB-E911-A245-FA163EE16739.root",
        # "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/D2ADFA26-0EEC-E911-9647-FA163EC9EBE1.root",
    ]
)
# fillhist(h250to400, events250to400, 3.043 * 1e3)
fillhistgenparticles(h250to400, h250to400GenParts, events250to400, 3.043 * 1e3)

hInclusive.Draw("histex0")
h50to100.Draw("histex0same")
h100to250.Draw("histex0same")
h250to400.Draw("histex0same")
hstitched = h50to100.Clone("stitched")
hstitched.Add(h100to250)
hstitched.Add(h250to400)
hstitched.SetTitle("Stitched")
hstitched.SetLineColor(ROOT.kBlack)
hstitched.SetLineStyle(ROOT.kDashed)
hstitched.Draw("histex0same")
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
# tfile.Write()
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
