import ROOT
import os
import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lumitools import make_lumihelper, make_jsonhelper
import correctionlib
correctionlib.register_pyroot_binding()
 
ROOT.gROOT.SetBatch(True)

# for certified lumi
jsonfile = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt"
jsonhelper = make_jsonhelper(jsonfile)

# Enable multi-threading
ROOT.ROOT.EnableImplicitMT()
 
doPreVFP = True
doScaleFactors = True
print("Doing preVFP" if doPreVFP else "Doing postVFP", "with scale factors" if doScaleFactors else "")
if doPreVFP:
    filePath = "/tmp/scooper/preVFP/"
    #filePath = os.getenv("LQANA")+"/config/UL16preVFP_nanoV9_nanoSkim_29jun2022/"
    fileListsDYJ = [filePath+"DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_APV.txt", filePath+"DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8_APV.txt", filePath+"DYJetsToEE_M-50_massWgtFix_TuneCP5_13TeV-powhegMiNNLO-pythia8-photos_APV.txt"]
    fileListData = filePath+"SingleElectron_Run2016{}-HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt"
    fileListDataRunB = filePath+"SingleElectron_Run2016B-{}_HIPM_UL2016_MiniAODv2_NanoAODv9-v2.txt"
    electronSFJSON = "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/EGM/2016preVFP_UL/electron.json.gz"
    era = "2016preVFP"
else:
    filePath = "/tmp/scooper/"
    #filePath = "/tmp/scooper/testFiles/"
    #filePath = os.getenv("LQANA")+"/config/UL16postVFP_nanoV9_nanoSkim_29jun2022/"
    #filePath = "/tmp/scooper/checkAgainstNanoSkim/"
    fileListsDYJ = [filePath+"DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt", filePath+"DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8.txt", filePath+"DYJetsToEE_M-50_massWgtFix_TuneCP5_13TeV-powhegMiNNLO-pythia8-photos.txt"]
    fileListData = filePath+"SingleElectron_Run2016{}-UL2016_MiniAODv2_NanoAODv9-v1.txt"
    electronSFJSON = "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/EGM/2016postVFP_UL/electron.json.gz"
    era = "2016postVFP"
dyjSamples = ["DYJ_amcatnlo"]#, "DYJ_MLM", "DYJToEE"]

dyjCrossSectionDict = {}
dyjCrossSectionDict["DYJ_amcatnlo"] = 6077.22
dyjCrossSectionDict["DYJ_MLM"] = 6077.22
dyjCrossSectionDict["DYJToEE"] = 6006/3.0

if "/tmp/" in filePath:
    treeName = "Events"
else:
    treeName = "rootTupleTree/tree"
#chEventsData = ROOT.TChain("Events")

chainDYJDict = {}
for index, sample in enumerate(dyjSamples):
    chEventsDYJ = ROOT.TChain(treeName)
    fcDYJ = ROOT.TFileCollection("fcDYJ", "", fileListsDYJ[index])
    chEventsDYJ.AddFileInfoList(fcDYJ.GetList())
    chainDYJDict[sample] = chEventsDYJ

chEventsData = ROOT.TChain(treeName)
fcDataList = []
if doPreVFP:
    for x in ("C", "D", "E", "F"):
        fcData = ROOT.TFileCollection("fcData", "", fileListData.format(x))
        fcDataList.append(fcData)
        chEventsData.AddFileInfoList(fcDataList[-1].GetList())
    for x in ("ver1", "ver2"):
        fcData = ROOT.TFileCollection("fcData", "", fileListDataRunB.format(x))
        fcDataList.append(fcData)
        chEventsData.AddFileInfoList(fcDataList[-1].GetList())
else:
    for x in ("F", "G", "H"):
    #for x in ("F"):  # XXX only one file for testing
        fcData = ROOT.TFileCollection("fcData", "", fileListData.format(x))
        fcDataList.append(fcData)
        chEventsData.AddFileInfoList(fcDataList[-1].GetList())

# Create a ROOT dataframe for each dataset
df = {}
df["data"] = ROOT.RDataFrame(chEventsData)
for sample in dyjSamples:
    df[sample] = ROOT.RDataFrame(chainDYJDict[sample])
processes = list(df.keys())
 
dyjSumWeights = {}
#for sample in dyjSamples:
#    if "DYJToEE" in sample:
#        df[sample] = df[sample].Define("signOfGenWeight", "genWeight < 0 ? -1 : 1")
#        dyjSumWeights[sample] = df[sample].Sum("signOfGenWeight").GetValue()
#    else:
#        dyjSumWeights[sample] = df[sample].Sum("genWeight").GetValue()
#    print("sample={}, sumWeights={}".format(sample, dyjSumWeights[sample]))
if doPreVFP:
    dyjSumWeights["DYJ_amcatnlo"] = 1545707971038.0645
    dyjSumWeights["DYJ_MLM"] = 95170542.0
    dyjSumWeights["DYJToEE"] = 99650222.0
else:
    dyjSumWeights["DYJ_amcatnlo"] = 1220934619655.4375
    dyjSumWeights["DYJ_MLM"] = 82448537.0
    dyjSumWeights["DYJToEE"] = 81998375.0


# Apply scale factors and MC weight for simulated events and a weight of 1 for the data
#for p in ["ggH", "VBF"]:
#    df[p] = df[p].Define("weight",
#            "scaleFactor_PHOTON * scaleFactor_PhotonTRIGGER * scaleFactor_PILEUP * mcWeight");
df["data"] = df["data"].Define("genWeight", "1.0")
 
# Select the events for the analysis
for p in processes:
    # NanoSkim: vloose electron requirement 
    df[p] = df[p].Define("Electron_hoeUncorr", "Electron_hoe*Electron_eCorr")
    df[p] = df[p].Define("vlooseElectrons", "Electron_hoeUncorr < 0.15")
    df[p] = df[p].Filter("Sum(vlooseElectrons) > 0", "Require >= 1 vloose electrons - Passing uncorrected H/E < 0.15")
    df[p] = df[p].Define("Electron_ptUncorr", "Electron_pt/Electron_eCorr")
    df[p] = df[p].Define("vlooseElectronsPtCut", "Electron_ptUncorr[vlooseElectrons] >= 10")
    df[p] = df[p].Filter("Sum(vlooseElectronsPtCut) > 0", "Require >= 1 vloose electron with pT >= 10 GeV")
    df[p] = df[p].Define("Electron_scEta", "Electron_deltaEtaSC+Electron_eta")

    df[p] = df[p].Define("Electron_passHEEP_scEta", "0x1 & (Electron_vidNestedWPBitmapHEEP/2)")
    df[p] = df[p].Define("Electron_passEGMMissingHits", "Electron_lostHits <= 1")
    df[p] = df[p].Define("Electron_passSigmaIetaIeta", "(abs(Electron_scEta) < 1.479 && Electron_sieie < 0.013) || (abs(Electron_scEta) >= 1.479 && Electron_sieie < 0.0425)")
    df[p] = df[p].Define("Electron_passHoE", "(abs(Electron_scEta) < 1.479 && Electron_hoeUncorr < 0.15) || (abs(Electron_scEta) >= 1.479 && Electron_hoeUncorr < 0.10)")
    df[p] = df[p].Define("looseElectrons", "Electron_passHEEP_scEta && Electron_passEGMMissingHits && Electron_passSigmaIetaIeta && Electron_passHoE")
    df[p] = df[p].Filter("Sum(looseElectrons) > 0", "Require >= 1 loose electron")
    df[p] = df[p].Define("looseElectronsPtCut", "Electron_ptUncorr[looseElectrons] > 40")
    df[p] = df[p].Filter("Sum(looseElectronsPtCut) > 0", "Require >= 1 loose electron with pT > 40 GeV")

    if "data" in p:
        df[p] = df[p].Filter(jsonhelper, ["run", "luminosityBlock"], "jsonhelper")

    # trigger
    df[p] = df[p].Filter("HLT_Ele27_WPTight_Gsf", "Pass Ele27_WPTight")
 
    # Find two good barrel electrons
    #df[p] = df[p].Define("goodElectrons", "Electron_cutBased > 1 && abs(Electron_eta) < 1.4442")\
                 #.Filter("Sum(goodElectrons) >= 2", "Require >= 2 electrons in EB and passing cut-based loose ID")\
    df[p] = df[p].Define("goodElectrons", "Electron_cutBased > 1 && Electron_passHEEP_scEta")\
                 .Define("goodElectrons_ptCut", "Electron_pt[goodElectrons] > 35")\
                 .Filter("Sum(goodElectrons_ptCut) > 1", "Require > 1 electrons passing cut-based loose ID with pT > 35")\
                 .Filter("Electron_pt[goodElectrons][0] > 35", "Lead electron pT > 35 GeV")\
                 .Filter("Electron_pt[goodElectrons][1] > 20", "Sublead electron pT > 20 GeV")
 
# Compile a function to compute the invariant mass
ROOT.gInterpreter.Declare(
"""
using namespace ROOT;
float ComputeInvariantMass(RVecF pt, RVecF eta, RVecF phi, RVecF m) {
    ROOT::Math::PtEtaPhiMVector p1(pt[0], eta[0], phi[0], 0.0);
    ROOT::Math::PtEtaPhiMVector p2(pt[1], eta[1], phi[1], 0.0);
    return (p1 + p2).mass();
}
""")

ROOT.gInterpreter.Declare('auto csetEl = correction::CorrectionSet::from_file("'+electronSFJSON+'");')
ROOT.gInterpreter.Declare('auto csetElCorrections = csetEl->at("UL-Electron-ID-SF");') 

# Define a new column with the invariant mass and perform final event selection
hists = {}
for p in processes:
    # Make four vectors and compute invariant mass
    #df[p] = df[p].Define("m_ee", "ComputeInvariantMass(Electron_pt[goodElectrons], Electron_eta[goodElectrons], Electron_phi[goodElectrons], Electron_mass[goodElectrons])")
    df[p] = df[p].Define("m_ee", "ComputeInvariantMass(Electron_pt[goodElectrons], Electron_eta[goodElectrons], Electron_phi[goodElectrons], Electron_mass[goodElectrons])")
 
    # Make additional kinematic cuts and select mass window
    #df[p] = df[p].Filter("photon_pt[goodphotons][0] / 1000.0 / m_yy > 0.35")\
    #             .Filter("photon_pt[goodphotons][1] / 1000.0 / m_yy > 0.25")\
    #             .Filter("m_yy > 105 && m_yy < 160")
    df[p] = df[p].Filter("m_ee > 80 && m_ee < 100", "80 < M(ee) < 100 GeV")\
                 .Filter("abs(Electron_eta[goodElectrons][0]) < 1.4442", "Lead electron in barrel")\
                 .Filter("abs(Electron_eta[goodElectrons][1]) < 1.4442", "Sublead electron in barrel")

    if "data" in p:
        df[p] = df[p].Define("totWeight", "1.0")
    else:
        if "DYJToEE" in p:
            df[p] = df[p].Redefine("genWeight", "genWeight < 0 ? -1 : 1")
        if doScaleFactors:
            df[p] = df[p].Define(
                    "elRecoSFLead",
                    ('csetElCorrections->evaluate({"'+era+'", "sf", "RecoAbove20", Electron_scEta[goodElectrons][0], Electron_pt[goodElectrons][0]})'))
            df[p] = df[p].Define(
                    "elIDSFLead",
                    ('csetElCorrections->evaluate({"'+era+'", "sf", "Loose", Electron_scEta[goodElectrons][0], Electron_pt[goodElectrons][0]})'))
            df[p] = df[p].Define(
                    "elRecoSFSublead",
                    ('csetElCorrections->evaluate({"'+era+'", "sf", "RecoAbove20", Electron_scEta[goodElectrons][1], Electron_pt[goodElectrons][1]})'))
            df[p] = df[p].Define(
                    "elIDSFSublead",
                    ('csetElCorrections->evaluate({"'+era+'", "sf", "Loose", Electron_scEta[goodElectrons][1], Electron_pt[goodElectrons][1]})'))
            df[p] = df[p].Define("totWeight", "genWeight*elRecoSFLead*elRecoSFSublead*elIDSFLead*elIDSFSublead")
        else:
            df[p] = df[p].Define("totWeight", "genWeight")

    hists[p] = df[p].Histo1D(
            ROOT.RDF.TH1DModel(p, "Dielectron invariant mass; m_{ee} [GeV];Events", 60, 70, 110),
            "m_ee", "totWeight")
 
# Run the event loop
 
# RunGraphs allows to run the event loops of the separate RDataFrame graphs
# concurrently. This results in an improved usage of the available resources
# if each separate RDataFrame can not utilize all available resources, e.g.,
# because not enough data is available.
ROOT.RDF.RunGraphs([hists[s] for s in dyjSamples+["data"]])

cols = ROOT.vector('string')()
cols.push_back("run")
cols.push_back("luminosityBlock")
cols.push_back("event")
cols.push_back("goodElectrons")
cols.push_back("Electron_pt")
cols.push_back("Electron_eta")
cols.push_back("Electron_phi")
cols.push_back("m_ee")
cols.push_back("elRecoSFLead")
cols.push_back("elRecoSFSublead")
cols.push_back("elIDSFLead")
cols.push_back("elIDSFSublead")
#display = df["DYJ_amcatnlo"].Display(cols, 10)  # 10 rows to show
#print(display.AsString())
print(100*"="+" Report on DYJ amc@NLO:")
df["DYJ_amcatnlo"].Report().Print()
print(100*"="+" Report on data:")
df["data"].Report().Print()
#print("After report.Print()")
 
#dyj = hists["dyj"].GetValue()
dyjHists = {}
for sample in dyjSamples:
    dyjHists[sample] = hists[sample].GetValue()
data = hists["data"].GetValue()
 
ROOT.gStyle.SetAxisColor(1, "XYZ")
ROOT.gStyle.SetStripDecimals(True)
ROOT.gStyle.SetTickLength(0.03, "XYZ")
ROOT.gStyle.SetNdivisions(510, "XYZ")
ROOT.gStyle.SetPadTickX(1)  # To get tick marks on the opposite side of the frame
ROOT.gStyle.SetPadTickY(1)

# Create the plots
for doNorm in [True, False]:
    for sample in dyjSamples:
        # Create canvas with pads for main plot and data/MC ratio
        c = ROOT.TCanvas("c_"+sample, "c_"+sample, 700, 750)
        upper_pad = ROOT.TPad("upper_pad_"+sample, "upper_pad_"+sample, 0, 0.35, 1, 1)
        lower_pad = ROOT.TPad("lower_pad_"+sample, "lower_pad_"+sample, 0, 0, 1, 0.35)
        for p in [upper_pad, lower_pad]:
            p.SetLeftMargin(0.14)
            p.SetRightMargin(0.05)
            p.SetTickx(False)
            p.SetTicky(False)
        upper_pad.SetBottomMargin(0)
        lower_pad.SetTopMargin(0)
        lower_pad.SetBottomMargin(0.3)
        upper_pad.Draw()
        lower_pad.Draw()
         
        # Draw data
        upper_pad.cd()
        data.SetMarkerStyle(20)
        data.SetMarkerSize(1.2)
        data.SetLineWidth(2)
        data.SetLineColor(ROOT.kBlack)
        data.SetMinimum(1e-3)
        data.SetMaximum(6e5)
        data.GetYaxis().SetLabelSize(0.045)
        data.GetYaxis().SetTitleSize(0.05)
        data.SetStats(0)
        data.SetTitle("")
        data.Draw("E")
         
        # Scale simulated events with luminosity * cross-section / sum of weights
        if doPreVFP:
            lumi = 19501.601622
        else:
            lumi = 16812.151722000
        dyjHist = dyjHists[sample].Clone()
        dyjHist.Scale(lumi * dyjCrossSectionDict[sample] / dyjSumWeights[sample])
        # norm to data
        if doNorm:
            print("Applying normalization scale factor of {}/{}={} to {} sample.".format(data.Integral(), dyjHist.Integral(), data.Integral()/dyjHist.Integral(), sample))
            dyjHist.Scale(data.Integral()/dyjHist.Integral())
        dyjHist.SetLineColor(2)
        dyjHist.SetLineStyle(1)
        dyjHist.SetLineWidth(2)
        dyjHist.Draw("HIST SAME")
         
        # Draw ratio
        lower_pad.cd()
        lower_pad.SetGridy()
         
        ratiobkg = data.Clone()
        ratiobkg.Divide(dyjHist)
        ratiobkg.SetMinimum(0.8)
        ratiobkg.SetMaximum(1.2)
        ratiobkg.GetXaxis().SetLabelSize(0.08)
        ratiobkg.GetXaxis().SetTitleSize(0.12)
        ratiobkg.GetXaxis().SetTitleOffset(1.0)
        ratiobkg.GetYaxis().SetLabelSize(0.08)
        ratiobkg.GetYaxis().SetTitleSize(0.09)
        ratiobkg.GetYaxis().SetTitle("Data/MC")
        ratiobkg.GetYaxis().CenterTitle()
        ratiobkg.GetYaxis().SetTitleOffset(0.7)
        #ratiobkg.GetYaxis().SetNdivisions(503, False)
        #ratiobkg.GetYaxis().ChangeLabel(-1, -1, 0)
        ratiobkg.GetXaxis().SetTitle("m_{ee} [GeV]")
        ratiobkg.Draw("e0p")
         
        # Add legend
        upper_pad.cd()
        legend = ROOT.TLegend(0.7, 0.60, 0.89, 0.85)
        legend.SetTextFont(42)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        #legend.SetTextSize(0.05)
        #legend.SetTextAlign(32)
        legend.AddEntry(data, "Data" ,"lep")
        if doNorm:
            legend.AddEntry(dyjHist, sample+" (norm)", "l")
        else:
            legend.AddEntry(dyjHist, sample, "l")
        legend.Draw()
         
        # Add labels
        text = ROOT.TLatex()
        text.SetNDC()
        text.SetTextFont(72)
        text.SetTextSize(0.05)
        text.DrawLatex(0.18, 0.84, "CMS")
        text.SetTextFont(42)
        text.DrawLatex(0.18 + 0.13, 0.84, "Preliminary")
        text.SetTextSize(0.04)
        if doPreVFP:
            text.DrawLatex(0.18, 0.78, "#sqrt{s} = 13 TeV, 19.5 fb^{-1}")
        else:
            text.DrawLatex(0.18, 0.78, "#sqrt{s} = 13 TeV, 16.8 fb^{-1}")
         
        # Save the plot
        plotName = "mee_"+sample
        if doPreVFP:
            plotName+="_2016preVFP"
        else:
            plotName+="_2016postVFP"
        if doNorm:
            plotName+="_normed"
        if doScaleFactors:
            plotName+="_withIDRecoScaleFactors"
        c.SaveAs(plotName+".png")
        c.SaveAs(plotName+".root")
        print("Saved {} for sample={}".format(plotName, sample))
