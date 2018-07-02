# import ROOT in batch mode
import sys
#oldargv = sys.argv[:]
#sys.argv = [ '-b-' ]
import ROOT
#ROOT.gROOT.SetBatch(True)
#sys.argv = oldargv

import math

# load FWLite C++ libraries
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.FWLiteEnabler.enable()

# load FWlite python libraries
from DataFormats.FWLite import Handle, Events

handlePruned  = Handle ("std::vector<reco::GenParticle>")
handlePacked  = Handle ("std::vector<reco::GenParticle>")
labelPruned = ("prunedGenParticles")
labelPacked = ("packedGenParticles")

# open file (you can use 'edmFileUtil -d /store/whatever.root' to get the physical file name)
#events = Events("file:Output_amcAtNLO.root")
events = Events("file:Output_pythia.root")

histo = ROOT.TH1D('MT','MT;MT(e,#nu) [GeV]',1000,0,1000)
for iev,event in enumerate(events):
    event.getByLabel (labelPruned, handlePruned)

    pruned = handlePruned.product()

    t_ele1 = ROOT.TLorentzVector()
    t_nu1 = ROOT.TLorentzVector()
    hasEle = False
    hasNu = False
    for p in pruned:
        #if abs(p.pdgId()) > 500 and abs(p.pdgId()) < 600 :
        #    print "PdgId : %s   pt : %s  eta : %s   phi : %s" %(p.pdgId(),p.pt(),p.eta(),p.phi())    
        #    print "     daughters"
        #    for pa in packed:
        #        mother = pa.mother(0)
        #        if mother and isAncestor(p,mother) :
        #            print "     PdgId : %s   pt : %s  eta : %s   phi : %s" %(pa.pdgId(),pa.pt(),pa.eta(),pa.phi())
       if abs(p.pdgId())==11 and p.isHardProcess() and not hasEle:
           hasEle = True
           t_ele1.SetPtEtaPhiM( p.pt(), p.eta(), p.phi(), 0.0 )
       elif (abs(p.pdgId())==12 or abs(p.pdgId())==14 or abs(p.pdgId())==16) and p.isHardProcess() and not hasNu:
           hasNu = True
           t_nu1.SetPtEtaPhiM( p.pt(), p.eta(), p.phi(), 0.0 )

    MT_Ele1MET = math.sqrt ( 2.0 * t_ele1.Pt() * t_nu1.Pt() * ( 1.0 - math.cos( t_nu1.DeltaPhi(t_ele1))));
    histo.Fill(MT_Ele1MET)

histo.Draw()
