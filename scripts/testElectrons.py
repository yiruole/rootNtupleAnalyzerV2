# import ROOT in batch mode
import sys
from DataFormats.FWLite import Handle, Events
import ROOT

oldargv = sys.argv[:]
sys.argv = ["-b-"]

ROOT.gROOT.SetBatch(True)
sys.argv = oldargv

# load FWLite C++ libraries
ROOT.gSystem.Load("libFWCoreFWLite.so")
ROOT.gSystem.Load("libDataFormatsFWLite.so")
ROOT.FWLiteEnabler.enable()

electrons, electronLabel = Handle("std::vector<pat::Electron>"), "slimmedElectrons"

events = Events(sys.argv[1])

for iev, event in enumerate(events):
    event.getByLabel(electronLabel, electrons)

    print "\nEvent %d: run %6d, lumi %4d, event %12d" % (
        iev,
        event.eventAuxiliary().run(),
        event.eventAuxiliary().luminosityBlock(),
        event.eventAuxiliary().event(),
    )

    # Electrons
    for i, el in enumerate(electrons.product()):
        if el.pt() < 5:
            continue
        #print "elec %2d: pt %4.1f, supercluster eta %+5.3f, sigmaIetaIeta %.3f (full5x5), ecalTrkEnergyPreCorr %4.1f, ecalTrkEnergyPostCorr %4.1f, ecalEnergyPreCorr %4.1f, ecalEnergyPostCorr %4.1f" % (
        #            i, el.pt(), el.superCluster().eta(), el.full5x5_sigmaIetaIeta(), el.userFloat("ecalTrkEnergyPreCorr"), el.userFloat("ecalTrkEnergyPostCorr"), el.userFloat("ecalEnergyPreCorr"), el.userFloat("ecalEnergyPostCorr"))
        # for eleid in el.electronIDs():
        #     print "\t%s %s" % (eleid.first, eleid.second)
        ptCorr = el.pt()*el.userFloat("ecalTrkEnergyPostCorr")/el.energy()
        ptCorr2 = el.pt()*el.userFloat("ecalTrkEnergyPostCorr")/el.userFloat("ecalTrkEnergyPreCorr")
        print "elec %2d: pt %4.1f, supercluster eta %+5.3f, sigmaIetaIeta %.3f (full5x5), ptCorr %4.1f, ptCorr2 %4.1f, ecalTrkEnergyPostCorr/ecalTrkEnergyPreCorr %4.3f, ecalEnergyPostCorr/ecalEnergyPreCorr %4.3f" % (
                    i, el.pt(), el.superCluster().eta(), el.full5x5_sigmaIetaIeta(), ptCorr, ptCorr2, el.userFloat("ecalTrkEnergyPostCorr")/el.userFloat("ecalTrkEnergyPreCorr"), el.userFloat("ecalEnergyPostCorr")/el.userFloat("ecalEnergyPreCorr"))
