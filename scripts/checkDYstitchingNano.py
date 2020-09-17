#!/usr/bin/env python3
import ROOT


# def fillhist(hist, events, xs):
#     sumW = 0
#     for iev, event in enumerate(events):
#         event.getByLabel("externalLHEProducer", lheHandle)
#     hist.Scale(xs / sumW)


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

maxEvents = 100000
filesInclusive = [
    "root://eoscms//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/100000/DFAFA074-2ED1-6B4F-B3D7-F7E22D2BC603.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/100000/DFAFA074-2ED1-6B4F-B3D7-F7E22D2BC603.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/260000/31CC190A-4B71-E544-A60A-1EF827027278.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/110000/0F1A65AE-5E93-664E-A444-E7FD0D01CA9F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/77A243F9-2277-1B4F-A655-A6849D33DD31.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/F479D52F-776F-E146-81CD-96777B8D724E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/62385117-0680-514C-B437-41F68813CF35.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/804A1FE1-6C27-704A-B132-9746927B9C84.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/2A4867A9-97FD-8F45-B1FF-4C70ED1D147A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/68242B02-ADF8-3B45-AA2B-4B1C53889FD0.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/49BCFF65-DF08-2342-ADB3-E56048464BED.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/3B2A2025-40C0-214B-89E2-182F2F007FDC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/2194097F-B7E8-E54B-BADD-8ABA8EE577FE.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/81A2D327-BDD2-8C45-843B-134A875145CF.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/E4A8F2FD-0B8E-3E46-B9F2-A4FDB55B74F3.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/FE955B1A-5ABB-E248-8BF1-A9087AD19608.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/110000/884409F6-6E83-2441-8421-14E41DBE7BD5.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/E8B97C1B-0C6F-B548-8319-F217CDE8A1AB.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/130000/4E9552BD-C181-8A43-A742-C8174062D159.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/1B34D825-A61E-D849-B6FF-8FD500110078.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/110000/C1CF1076-D5FE-0A46-B476-0F3DDEB6C430.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/130000/03874067-38A5-B042-8FD9-A52AFCB1D7AC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/270000/C0A54FD3-86CB-A84C-B43A-27D9421BAB92.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/260000/B62CAACC-FD31-0445-9FF5-19ADDE9E4885.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/110000/0070F291-F0F2-3246-9BFC-56FFF01CFE33.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/130000/975FF603-3B60-6D42-B8FB-D0E96DA277F2.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/100000/A595AB5C-33FF-3F48-9762-FCA4C27F6F69.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/110000/ACAD19BB-1EA8-874C-856D-EDFCE2C43C91.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/120000/423BE467-D27D-D44E-A639-547056A3386F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/60000/03FAA518-BBC9-2E4C-9CB4-576EE9EA9D37.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/24701041-0053-3E40-A116-21B65A75C8BD.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/130000/5C701AB8-9DDD-7B40-BD90-D3B261A59F22.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/130000/73B50F6A-9E25-8142-B6D0-9B54861566B5.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/130000/EC8970E5-EB7D-8F47-9131-5E657A729944.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/130000/20E0F694-25AD-E143-8C4B-5407605035B4.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/70000/4F6941EF-7C79-844B-867A-34FDD2DA736C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/260000/76ED1BA0-0831-504F-AF67-30AABF6EA837.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/130000/EFA0528F-89A9-BD49-B8A8-D972BE696BCD.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/130000/D942AEAD-490D-2349-9FB1-C0A16B11E69E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/100000/E9FBBA8B-0CCD-A040-8E59-ABA6033ED350.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/130000/BEF5E572-DEFE-C64A-B6F9-0F329E255792.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/260000/FDDFB5AD-2087-0343-8BBA-184CEDD943AF.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/130000/1B7A0938-12E3-F84D-A57D-B03DA963551A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1/130000/E73F1BD8-3A3D-6F47-BA5E-3A23AFA1945C.root",
]
treeInclusive = ROOT.TChain("Events")
for tfile in filesInclusive:
    treeInclusive.Add(tfile)
fillhistgenparticles(hInclusive, hInclusiveGenParts, treeInclusive, 5938.0 * 1e3, maxEvents)
# fillhist(hInclusive, eventsInclusive, 5938. * 1e3)

files50to100 = [
    "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/1E6BB2D4-5D7D-F044-8622-EE5B618E3E41.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/901C947E-4E07-444E-A4D6-17B6FB56096D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/7D68FA37-7095-2B45-9BA4-D87D2BA23259.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/42EAB861-D079-804A-9638-9428F88847DB.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/4BA0420E-831A-BE48-9347-A0EA5A6EDAA5.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/7E2486F8-2929-0D45-9600-46DFDB82B303.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/4997BD94-39B8-4C4A-9EB2-D3E761528DEB.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/E01D5CC4-B03A-C244-9492-A449543E8E1F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/9E141467-BE85-154E-96B0-331418C52094.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/4E021570-7299-734C-9768-A8BCB65F488C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/170C554C-1A80-1D43-899D-2BCF3E286578.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/F7999E38-7B31-9D4E-8D4E-DB07DD730895.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/265A543A-FB52-AD4A-AAF2-38131FD00044.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/BB5B0CD4-762A-F649-8399-3DB3C689B945.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/867A3400-B738-414F-B302-EC96A9E90FA7.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/8BBDAACC-5EF3-9247-90FD-D5DC127F222E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/A4202864-CD91-A34D-80DD-10994EA57007.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/CD7F6867-5656-554E-B39F-E71B5D15562A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/E66A19D3-9BF0-B746-94D6-791A969ADD30.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/4B3D6C72-D133-914A-AB78-8096EC5A3F43.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/A2AB96DF-8899-D84C-BE69-BC71EC3426E4.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/354B8F5B-0D98-3A4A-A7E8-B674BF0AD977.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/FA76998C-7779-3A49-861C-30DE4EA0BC7B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/67C1CD6B-DD0B-AC42-B520-48E2B257F021.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/AB10DC6D-1C33-E64E-B324-7D526B241D29.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/01A95A53-38A1-2946-A18E-B59D9314B1BF.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/F52DC94E-8CEF-FD42-99D2-A7CE4AC99C6F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/5ACB90FD-5129-E04D-AAE8-4A73297ECF88.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/E5AC8166-30D5-6745-B225-7E2D5FD85993.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/B8A271FA-5A70-3647-BBA1-59D968156537.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/FC04CF7E-5652-104B-BE2A-2BA194063797.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/069BFC8C-AD9E-054C-9408-21F4E71BD2D1.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/0E937C29-AB07-3E4D-8B23-3EB044A40526.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/5EB28A52-484E-EB44-929E-D493BF42F1E6.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/876DF109-F422-3E4B-AAC2-415BFD1E9DA3.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/B6105549-805A-7A48-9361-C7E683DBF619.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/56B19F65-73DE-5540-ADDD-0FF4DFCDB413.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/D0F58421-DDF8-C349-9BD0-65686C22548E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/6C73589C-B3F8-4247-87E9-205904B84135.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/D2C66E86-FF5F-E147-93DF-1393A26CD5D2.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/850C5A09-181C-9A4A-A8B4-CFA9B9732D2C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/4F4559A6-3902-5B4A-9BAE-B1A58F1DDD71.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/7ACFF71E-9C1F-644E-82D0-D6391CFFA91C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/BB60AE9C-075D-6641-95AF-644336761114.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/9D50A5E7-9F81-CE41-B5F6-FDC84DBA4DEE.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/7F276E39-50A0-D044-AA1A-8DC36992D9CE.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/1F97CA11-A9E4-E543-A807-5EAB3C8253A7.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/E6FEA66D-7000-3E43-974C-E776A587D8DD.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/8C133307-532F-2942-87CE-17A04D9E94AC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/7BFBD888-E4E0-9B47-9047-9CADCBAEB210.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/398EBC56-7B23-974A-8D79-2711AECD6A1D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/9528CBA4-F4E4-204A-BEC4-274559A623D9.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/D005E2EC-DF24-F04E-B13D-5C945AD5F1D9.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/4F1D8826-06D8-454A-A2FC-61F78020539C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/6232DDF1-AE9B-474D-9074-93FA4C029562.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/D78AA780-1C29-254B-B3C0-D70BD64FCC6E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/E7B469A3-21C1-E742-AF0B-2C159143EB85.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/EC5C40D1-A3D1-704F-9D0F-BF4AE6B5FB5B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/6486D331-9FD7-0044-8BED-D7CDEC167CCC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/742A8905-DEB6-CC40-A9D2-15AE6CA6312A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/F058B857-D24C-4E47-B283-39210141811A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/6CE76816-4A4F-A140-8C60-9DD7C925E1EF.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/A2EC1B20-E99D-3240-BD0A-F104BBCCFC06.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/352210AF-52DA-644E-8336-4F8D236D74DE.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/FDD0B490-CBF6-C54F-AD9B-232251B282D3.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/3D83B3E0-4B87-A740-8B0E-D5F0E9F608BE.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/ED1D0D3E-45FC-BA41-A822-727F7070BA0B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/26724DEA-0565-8E4D-8946-E18A85D932BD.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/AF3984D2-1630-8E46-AB78-4B936CB1CBF7.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/528816DA-F0C5-5145-807F-FF6D1341B9B2.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/2C0F70AC-580B-9948-ABD0-68CEEB0D0652.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/C36E3BED-C633-4048-97A9-016AFAE82D03.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/4773A4E3-72BB-5246-B7FE-B9952337DD6E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/0008CE9F-A1EF-D242-AFA5-34BC3BCC625B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/214D6023-F13B-8245-A7BE-778B60BF6491.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/4CDDBFCA-CDD1-F649-80CE-9E791865A45E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/6983A5D5-DBC1-3841-A229-7C4A0E24C3F5.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/B55EA544-1F1B-4A49-804D-5C411FBC8F43.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/EF38DE25-C3F3-A243-9C53-C532C5BE791B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/C7BE6F95-E82A-284A-82A0-D5EC7029DAAB.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/3347126B-9A3E-BB4A-9478-7FA6DC32473F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/17ED1244-7FF1-9141-ADCA-229BDA5FE883.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/A0E9EC93-BC55-B542-A50F-7A27A0D547A9.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/F7D2B165-8D8E-AF4F-B3A8-430240613E75.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/F9FAAD71-F9F7-FF40-816C-41A359B8CCBC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/CA262BD8-FECA-C54C-925B-EB2A26F158E9.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/22724CC7-07A6-FB43-A299-9A54D17DACA8.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/297BBA63-FC64-1F48-A092-ABABC21C9D29.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/B6CF951D-46F5-5C46-B99D-DF0591E184B8.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/1F59C245-5158-5C48-B5D1-317BCAA760D6.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/D5A31C38-AA1B-734D-973B-9B717724BCCA.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/FD34C46A-18B5-1146-9C16-A4AAB6D904D6.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/50741295-D468-0243-8E68-5C756D0D8F72.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/42709031-A34F-B848-A7B6-32C4F5F8D5A3.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/1F989A7B-FD5B-D241-B5C4-D8EAE975321F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/0D869C3A-C28C-8948-B77A-BC34C33A769A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/8D62BFC3-55F8-9945-A464-5632B96E4AE4.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/61124229-79E1-FE48-A1C7-311AA03DE6A5.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/A9A947BC-DF83-D44F-AE83-833EB593374C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/82A2CF5B-2186-C943-AC82-865410258DFB.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/2D8BA2B1-AAD8-C64A-B854-978303A8FEB8.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/C595DD18-3278-4043-B53C-9E449F39125D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/1C30BACE-4150-C240-BE24-A790FF7013D2.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/45206F0E-8764-EC40-BA4B-EB9757B77AD3.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/427D2AFE-97BF-6B40-B2F6-8C2290851BAD.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/12819259-EAA6-D941-94F3-F884A079B358.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/DF16C0BF-857E-E142-9B93-27262417A5C4.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/520B5A97-4D61-624A-BACA-4FA074988A88.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/1E7BC4F4-C779-DF48-AD95-7AAF1984342F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/C8D2210F-3067-F64E-8A30-A5138526D28C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/53126A39-A399-8B48-BCC3-655312821215.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/A54274CA-959D-EF4A-A410-6588ABF1C055.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/0589167C-0B66-4E44-956A-C39EC47E11BB.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/D2E442E4-EF0B-AD47-B2D6-71B15EE5D0C8.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/8AEA7F35-8EE5-DD41-8484-2C0CA99D994D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/F49F42EF-33B9-EF40-B534-3D92168807D0.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/02C6900A-5D0F-4C40-8A14-8B55EE8D2819.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/4A6C9B81-EC7D-314C-B1B5-365F890E84AA.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/AFBC2C96-9209-0349-A47E-12406323542E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/E692F4BD-51F4-EC4A-A7B7-741C6C1C553D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/E2BE6285-74EB-7644-B8B2-F52C3E9005A8.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/3D181934-E544-954D-806E-5687A4A10644.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/54726DF5-B7F6-E546-9179-C6537E3EB81F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/D32D832B-A27D-2F41-9FE2-D5C20141A150.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/C84883A8-341C-4B49-BF08-88AE24CBC261.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/1AEA8DF7-006D-7649-B406-986AB3D06540.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/8044169C-5829-1148-A4E1-0B331580BF8C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/3B23F3FB-B3C9-2449-A168-F6CB09142109.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/B1ABDE52-5C90-4443-BD50-3E36DA9357E9.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/0973A8AA-D612-8049-97CE-C7576755DFAE.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/0DAD8DE5-A324-5F4A-8168-023A6692D13A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/112FEE8A-D550-4642-B7BE-2D71682947C7.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/5C9DD9D4-226F-A04E-8DBD-F13333DCEC14.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/4F2BD3A0-22B9-8C43-845C-E00F352F1982.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/3F15D769-C490-CC47-B526-3E0BF7B56B29.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/A6051C5F-1EDD-564E-9CCA-010FF131A358.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/2216BFFF-B30F-F545-B652-E18BB02EAC1A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/42DBE2F8-7977-984E-9FB8-4BE04B59ACDE.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/EEA6D8B0-322D-BD44-8624-3232783651CC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/9F08FD35-CC92-CC47-B922-E5C5DDFFFFF0.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/0FFB6809-5D31-E94B-8743-FFEA0FABF74E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/75388206-92B0-E04A-ADD7-864F48BC0C69.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/BBEB87B2-D150-E14A-A7EE-F7B4175B2022.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/5BB09504-AC61-194C-8F1E-25805A060B9B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/5A5386D9-DA79-0945-BF93-FA11E2FC4AEC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/1ADD88A9-97C0-8147-BCD1-4EC9697FBCA0.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/82277AA2-9BAA-0447-9A07-318DD71A26AC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/4C462D0C-4AF3-1F4E-9E45-8A148D8AF380.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/6E291942-B091-BC42-AF86-AE568C20D631.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/1F682227-F6DD-AF48-871D-F5C9DDF669FE.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/CE14D923-49CE-7144-8B3C-033FE39D708A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/3FF0FEC2-B515-6C4D-B612-6BCAFAD3F275.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/8E25897B-3A8C-1B49-8713-F6CA1D4AFCB2.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/3A6E5C6B-B7B3-E943-9009-6AF8DED920FB.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/84CAA989-FF18-8545-AB85-099152CD97C0.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/FDD39D5B-6CB1-7643-B3BF-C70975FAB639.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/2F5AE424-58E6-B848-98C1-B8AE33D7C19D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/0AD6E2F3-DAD2-EF41-A87E-76BEB8802C2A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/7FCFDB63-CBA3-C54B-AE27-0A4ACD987F78.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/268FF132-AF7C-0640-BFB4-BD7E26EAC007.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/C9EA4CD2-5D95-A845-8C5E-3B759D533747.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/88358B66-E27B-DE47-BFA5-B4815E5929FC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/C80FE683-AEA8-3D48-B7EA-679D917C0629.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/8D60C836-3C16-0A4C-809C-E9824DBE1658.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/FB8316B2-C36D-8D42-8350-6B1C28712316.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/D4257A16-F98B-6F44-AF4F-6D24FFFC3F22.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/936824FF-7028-E146-A5AE-A0CFDE51B9FF.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/0F4C71B3-31E4-1644-8532-E1C73523C8F7.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/4BB5492D-294C-FC43-8811-486199AD96E9.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/0F00193C-D3CD-274B-A9DF-CAC2BF38526A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/7AE8F9C9-0CD6-9A49-BE4C-9F53CC026014.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/96BF6E76-2D17-F449-9391-CE053DBC5CBE.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/0805B17E-F145-0143-9475-05565E254BF7.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/C256B964-29DC-0449-9639-E3CAE7ECA9BE.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/4E3C65CB-11BA-5246-9F86-F0DE1F3F8A85.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/81544124-E98C-494E-93A6-CE42E8C29202.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/C1141260-73E5-C640-99DB-69427EA44003.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/795F6E15-2612-FF40-8F09-75862ABD3855.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/9E762444-B69F-1740-9C90-19D2029D3F45.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/EA0D0BF5-3B91-AB45-A10C-4A8A2116BF48.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/F168BB45-2297-B94D-8B12-9FCA1FA9791C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/B9126451-5AEB-1745-A87E-C174AF8C4967.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/F4C44A00-5C5F-9348-8EC7-81CAB40D48AE.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/DE9C2D6C-4CFB-134A-B1E8-27FB085AC0B4.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/3D1C82FA-7886-BB4B-8F21-46874432CB4B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/D0CDD671-40B9-C443-BDF1-7E773A247E2D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/EE59D1FF-1C91-A94E-B9E2-D5C90A77A579.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/B40E8DE1-3E97-E246-B16D-90696B2F5DCB.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/BFE6A0FA-34DF-6345-8BF6-DEBDD6FE7300.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/E77B763F-F3B3-914A-8B9C-381B23F0859B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/CF516E0E-7ED9-AE4D-AA04-98ED5FEAF515.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/6AFB031E-5AD7-0349-A1F2-93073B87700C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/7565DA3F-49CC-CE4A-A380-AB95CAD61A99.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/59CCB0E5-58FD-9245-A1F5-114DB153641B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/E28C27CB-315C-E540-8E4B-0880D1591FE0.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/FF83866F-CD70-FF43-9284-AB787ADFD423.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/CD498E22-5086-F14E-A3B3-DD49A3F12477.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/008CBEC1-65FB-0848-85A9-ED76FFD037B0.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/3BFCE8BF-C693-C84B-9B8F-7F633ADA085E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/07BCE4BB-EC9C-8D4B-AE2C-84E79E35A6CD.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/E0C421CC-07AD-AB42-B759-F9504A2E9FEF.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/BD490688-CC2A-4F41-89B8-51259C23AF8A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/EAABBB03-4579-7244-9B1C-209802F9AF70.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/AA04D83F-C4DB-6246-B392-14E131064932.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/67BFA1B8-B0AD-734A-8901-6C3B87DBB700.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/5268DD19-4CA4-E44F-8A1E-E25836F97134.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/3C7AF5E6-6877-CE4A-AF47-09EA5D6391FC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/9817B236-13A2-874E-AFB8-5EE1D247336F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/54F879D8-296F-FC47-BFDF-8086A211FB32.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/3DEE002C-1C2E-ED44-9EB0-0D76EDBBADB0.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/1342B941-38A7-554F-98A1-7B535568DEB7.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/15F28F8D-424A-2644-B515-DB691A030FF9.root",
]
tree50to100 = ROOT.TChain("Events")
for tfile in files50to100:
    tree50to100.Add(tfile)
# fillhist(h50to100, events50to100, 354.6 * 1e3)
fillhistgenparticles(h50to100, h50to100GenParts, tree50to100, 354.6 * 1e3, maxEvents)

files100to250 = [
    "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/B00F84D9-120C-7848-8A49-0EE67E80A60B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/986A02FA-446E-A04E-9596-8CB8517C2116.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/7180012D-7A7C-FC4F-8F35-26D3E3DF61C1.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/4ACED8E5-285E-B448-93BB-2E8D9FA8556E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/1D5ABC3D-973D-7F47-9B61-65204129BC75.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/A668680E-B8D5-AD4F-9C36-054344CAD569.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/83773AEA-CF43-E14A-8EB2-442284D86A0C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/23C0EE43-E4D1-864B-A34B-15CAA5BC60B4.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/465C2F64-B45B-FA46-A2C5-B66021A78626.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/2294AB03-F099-0C40-8008-C21F4F58447D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/0CDCF2B1-79F3-544B-916B-FE09DE5FB089.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/0F85946F-74B9-E545-8E95-6CD6E1D0B483.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/CCA844B7-F36E-D748-8540-8C5F70F77748.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/94460DDD-D58D-814F-BE57-B31542CA86B8.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/131EF4A3-8B4F-7143-B7C6-CEC58DC9C1AB.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/6F69E3EE-ECA1-B143-B6C0-92ED7F1EF537.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/7D1AD45E-FA96-0541-90A7-3766A048B8DC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/C5BDA661-DA3C-944E-9080-543422E66BF5.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/01583706-A7FB-F74F-BDDA-14288893DE9A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/08D0BA2C-36E8-DA47-95FB-FF25C5B5F30A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/7D0292C9-34B5-6F4C-A83B-55380C68CA76.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/DD16488E-6A91-6541-A84C-AA56A4CA51D4.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/0B39D1BD-69E1-DD4A-8E1F-B7D9149DDC72.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/3C541978-9BD9-9F48-B2BC-3BAC19EC92D2.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/90B11CB0-D804-BA49-9732-3AE09E97C744.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/6746DA75-AFE3-B141-9903-403FA1A4E3EC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/D9F298F6-350F-0042-A10E-D4D428AC95B5.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/98587A6E-3279-0547-8B13-A2FF9329C0CB.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/281252A3-9E73-024B-B821-F0D22ADCF982.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/10F8FA91-0232-7446-B9E4-EEEC80697DF3.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/28BB59E8-9E77-B249-8662-4CAC8168BD68.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/3D2AA10E-E27C-7745-B1A3-9C3EC4706CAD.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/19F794EC-7DA0-DD45-903A-BB78D7A5A3B8.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/879560CB-55DF-AC4B-BD9D-525C62513465.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/AEF13E74-549A-AE41-8C71-F50E1A9E2B7B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/D864CF17-7421-814F-835E-9741C956A48C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/65B1B77A-036F-7C40-9D78-FCDC3F760CB4.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/F20BD973-7A91-824B-87FA-629AA4DF1EAF.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/B6968E95-D61C-AD44-999A-75121B663EF8.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/30E98EF2-3F3C-DF48-9536-F150DEFBCFDB.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/DE5EDDEC-6572-2841-A915-83D0465375EF.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/95C02B0C-7F35-ED41-9F8F-B0405509D301.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/8309ECA3-C4C6-AA4B-8D27-7F3430875719.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/94BA9700-44D3-3F42-AABE-5D97847C288F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/267EEA56-3F6B-D843-A41A-8DFAE05A6077.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/B046D586-4818-494C-8E72-BEE80CB774F8.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/775DAF7C-4873-5740-8C36-46132042A9BC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/CC873E69-D8BD-1B4B-A88C-70A6803157BC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/34A04F7D-0849-EE4F-ADD8-7BB15E360E34.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/C3FA68EF-C183-0A46-8352-3E14C70ACBF6.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/5618BF03-CCF1-374E-A5D6-1889EA5D6634.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/575B2561-EDAE-8B4D-A5D6-B2EE07E25DE0.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/4F65DDC9-2551-7648-A176-9CA6DA1F951F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/853BEE10-DE7C-8F44-81D5-6C91F0DBEE41.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/034A4CB1-F895-5E40-AC57-82307428FD5D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/D6362C53-F765-D44A-BB04-BA930220BFF1.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/18EC381D-268F-E64B-937F-D88795876DE6.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/304BED4E-AA16-8442-8F74-1404A504B900.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/05139E86-392B-1144-935F-EAABAB4EBFB0.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/A920BAA5-46A0-324E-9E71-284EFD07F9CD.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/BAD80695-E298-9E46-B1ED-7281B86EF00C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/F0AEF239-DB32-7440-A22B-10FD3FB38FC6.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/B572C144-91BA-C94A-B459-F7D01E7C97E4.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/3F94CB9F-75DF-CB42-85B1-34E888F4AE68.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/6AED8528-21AF-4C42-8DB4-584767697827.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/3E8011AB-56C9-7840-91A8-AD4A30274570.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/AA62859E-3F44-EC40-A64C-E1A616E26074.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/29984084-B7C5-0D4A-85A5-4A9D9DE68C10.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/23E5A1AD-6A0B-9D41-81CF-9C13834BEAD3.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/633E4C63-B759-6543-9DFB-4337CEAF7EA3.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/A4D88FEB-7906-F04B-BD16-5C7E60DEFE49.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/7682B9C0-37D3-A94F-9683-77249613BC15.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/8B3F7024-1F86-3E43-AEFD-FC1E640D7F2E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/D506F096-5C48-2B46-BB38-C0EC3BEED8C8.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/AC19C175-DDF6-3C4C-B3F7-02F56546F7F7.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/E5D804A0-8760-A248-944C-32CF074F4E07.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/2036477E-068A-5045-B2CE-4BF19B168679.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/7F29BE21-ED6B-3E42-8990-DB5B5A8FDEB1.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/BB1F4E69-CF5C-B441-A92C-02A49FDC1D11.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/20A8AB54-71EF-8A40-BAA2-9B8642533C12.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/F10F2A1D-86E2-AF49-A971-1E8EAB55654F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/29BE7F3E-A67A-AB41-92C4-12E91EDC076D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/A3456811-0135-5A42-9E89-297C6B0AEB5D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/EB74C8B9-885B-DA4F-AB95-8A7F92DE955E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/3F8DC01F-AB0B-624B-962D-1F803FE19D62.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/ED27BC6A-A74A-0E44-9CE1-D59E8C85E90A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/4E74C7C1-B453-F04A-AD9B-D21BBD5C76C7.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/2B78A844-9117-7D47-BE47-8792AA88715D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/55F66B01-0AB5-B64F-B5F6-DDADC94A4041.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/D0219DC8-A6E3-B449-BAFA-A2E066DF9FF3.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/76F19AC4-7B5E-184F-BB15-F1F4463F814B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/4D8E0BE3-66EC-524D-AA57-61C83977B414.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/59BACFC0-B58B-A34F-91D8-C82A0A15E464.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/C81D1C90-6ED8-0847-8542-001AFDC67E10.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/3098A9BA-2C95-9B43-986C-BA0D938B473A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/7CD248E1-E473-714E-A839-C7C6974FC702.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/91A60936-9A9C-B84E-A4D2-902DEC388012.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/5B54AA61-809F-9C4A-9991-46B5C6495F6C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/AC9A0D94-4000-074A-A792-DEDE40A3CBB3.root",
]
tree100to250 = ROOT.TChain("Events")
for tfile in files100to250:
    tree100to250.Add(tfile)
# fillhist(h100to250, events100to250, 83.05 * 1e3)
fillhistgenparticles(h100to250, h100to250GenParts, tree100to250, 83.05 * 1e3, maxEvents)

files250to400 = [
    "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/DC6F1D9E-50D0-FA4E-8C23-B8CEF562ABB5.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/FC09F586-00CC-7F43-BED2-2267DF425280.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/25D66F6A-B3EC-754E-9C6E-75367BA5DD4F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/455A3019-BAF1-5943-8405-4989A2E080D9.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/B86BBE5A-C3ED-D244-BDE3-9862A75CB3EA.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/9E663462-38F9-D04D-B79C-AE98E13F7282.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/2C97F27E-943B-EF47-87B9-F8EFE563ABF7.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/34850AFC-7CCC-914A-838A-4035CEBEC106.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/475DFB43-27CE-484E-8025-CD3C5E370E80.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/B70677B1-2732-5845-8B50-4C309E703515.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/D9BC16F2-A43A-6D4E-B58F-DDAED8939E30.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/6E2209FE-895F-3A4C-B1DE-03BB28FF946B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/7C30FADB-FDFA-BA40-B398-63FD01E89798.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/A4C2AE6E-CD5D-FD4E-A1C0-E8B3371B7FBF.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/A7D92277-F4CF-D243-A921-7B1B8EC1A3E9.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/D29149F4-C733-BF40-9FBF-BE14127A37E7.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/050724B7-884B-F245-BEB5-96D57E5BEB60.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/C462FD84-4DE6-974A-9947-0406A98C3707.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/5F276531-3EAA-E040-9E3F-7072A695A1E4.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/C9CC047C-2D37-ED49-8D35-926E1108CD4D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/08CEE5C2-9FBF-B246-B47F-0751225D5F99.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/C6F29325-C1CB-CF41-810B-E8401E7AF55B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/E7D8D4BE-F68B-CF42-BA63-45ECF5C4A9C4.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/7D53B28B-CD0B-7645-9969-40A34C5B0439.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/2D049262-B66C-F743-AEEB-F9135FFD62B1.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/4BF06AA4-FE12-7943-9C18-AEBEF6F91A53.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/F85FECA6-B47B-0640-9734-68A088E65FE0.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/29B3215C-B2B2-BB45-A2D4-D3806A0449C6.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/C59C5E6C-EB36-B84F-B569-E3849923FAC5.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/3A25DAC7-61AE-BE4B-A4D1-F8C7056E0BB6.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/6B8D2009-A755-1F4F-B4BC-797E197FBC27.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/6DBA1E05-4825-EC48-AC96-317AD81A9879.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/B46C4799-90B4-9E43-92D1-1ECD84BBF129.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/CD9A0980-418F-934D-918F-C66F1D413B17.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/361770E4-DFF9-8940-AF8A-60805FE18697.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/B5D38753-AF6F-8244-93F2-5DE760DB8D52.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/28DF3FF6-A1FF-BD45-BFFB-2764DD539ED4.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/D7C598A3-092E-6247-A0B1-84A527550EA4.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/3FAD8186-EE1E-C641-AC14-171D20307E21.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/F2639EAA-925C-1741-BB47-806DB7425752.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/32956856-21F1-644C-9C01-A30C7612027D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/11DDF8C5-A74E-3D4F-8BAE-27E95D2C1B12.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/9270CFDF-766A-7244-B471-80E02F811B07.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/0943C7C9-21E6-C84F-B3BE-6F3379614FDA.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/181D030B-D860-6C49-9734-17E60CDECBE8.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/333F96D8-4C82-7D44-815C-31F46B867CCA.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/6B8EB7A9-DC0F-234D-AE1E-7D38BE667C17.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/1064E190-58EF-F54A-B7DC-8A8C77D2240C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/39FAD5CB-70CE-B34D-B9CE-A14228A80370.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/7A9CB27E-E139-E94A-AA57-FDB80A3311B9.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/0670A317-8DCB-8C4B-A47B-1DF84B519EC3.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/909C91A7-DA75-CA49-9456-D0A1FACAB0DD.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/F2F820E2-B474-5E41-A0A5-FABA8678974D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/B607D54F-E2B8-1E41-836A-03514E7F3D85.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/53784890-E3F2-4B4E-BD66-4C56A402E37C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/67896F17-240B-EF4C-9D73-FA6958737C3B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/E44D408E-E440-6847-B125-4D1EDA637F03.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/155E3D7D-951A-5744-9401-A03F445B7011.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/25D0C3FC-37F7-B243-BAA4-DB9CF8934979.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/28AB5E7F-406E-9146-B238-38DA7B097311.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/8673E4CD-9417-AC46-BCA3-4B8386AAB6D3.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/BD5F6064-2195-BB40-8200-3F789F13CE27.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/28834ED6-46DA-D240-BECE-35E633E1AADA.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/D423238F-5BC4-1F42-9893-92AA14CA0B91.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/EC3C3CA5-BEBB-0B4E-85D7-F1958B77E27B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/437759D4-9675-A746-B909-4B176FB2C6BF.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/965FB27B-999E-6340-B1AB-74764EF94522.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/10D9518F-5C24-184D-A71B-15E7136E727F.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/8F8918FD-1DDC-484D-B1D6-CA8A0E4B594A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/C4FF8374-483C-344F-9E3A-DFF830B8A208.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/C58FC6E1-FB20-F04D-A366-ABB167896370.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/2BAC110A-008A-624E-84B0-F2A5324DAC33.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/8771B088-FF07-5F44-A40F-66B691822FDC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/725F777D-D720-AE45-BD7F-892D730FA84A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/38B5C7A3-EAB8-9647-90EE-1C104763C515.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/08B650B5-34AC-504B-A5E7-A554E1565486.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/F0F2392C-20C9-0A45-8456-5FB1B971AB3B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/C63544C4-5B4F-5C4C-91C0-4F1798FFB00E.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/E7189D79-DD95-424E-A67F-F335AC13185B.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/418C61F4-224D-FE4B-87F4-223EE99CCD98.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/85DDA42B-5B2B-7E40-B157-9BDB9CB790B9.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/60000/6CB89AAC-8828-FD48-A8C4-D103362D5EB8.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/260000/1CB041F1-ABA2-FB46-9B95-F193FB1C3ACC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/F4D27F51-D0BA-DB49-8574-8CBEDCD2B331.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/08CFC80A-4DBF-DB48-88F4-BD747536F1B1.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/2482424F-EFDC-BA49-8AB8-B5807A1A5848.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/2342B1E0-DBAA-8E46-8129-F9FDD71BAD15.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/8938AF75-7F20-8C4D-BCE9-FF6CC5B8F71C.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/70000/6CF1B5A3-B216-4D44-8F9C-CAD54C582111.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/1D9AD92A-B97E-B744-BE01-C05FDE18F281.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/4549B24B-949F-B94D-9AA8-36AD783D5CD0.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/100000/E6EC9DBE-7DEB-6040-BAFA-F058A3CBA48D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/130000/A4263991-A5C5-D14B-B9AC-3380E5098EA6.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/5174C06B-500E-2B41-9755-87E308546A3D.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/270000/737913E2-F738-FD40-96F2-2AAC237E7B24.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/110000/9B24096E-4875-0848-922C-6D4F71B20F80.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/EF041751-A61F-AA4E-BF96-EAFDFC50C0E6.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/E0AE85C9-1F1A-D34E-A8A3-3AE4374F0CBC.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/D7406A99-2471-A44B-88A0-A85AE6A58A9A.root",
    #"root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv7/DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/120000/D6425368-1067-0749-932A-6573242EB75D.root",
]
tree250to400 = ROOT.TChain("Events")
for tfile in files250to400:
    tree250to400.Add(tfile)
# fillhist(h250to400, events250to400, 3.043 * 1e3)
fillhistgenparticles(h250to400, h250to400GenParts, tree250to400, 3.043 * 1e3, maxEvents)

tfile = ROOT.TFile("ptStitchNano.root", "recreate")
tfile.cd()
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
