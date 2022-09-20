import ROOT
import os
 
ROOT.gROOT.SetBatch(True)

# Enable multi-threading
ROOT.ROOT.EnableImplicitMT()
 
filePath = "/tmp/scooper/"
dyjSamples = ["DYJ_amcatnlo", "DYJ_MLM", "DYJToEE"]
fileListsDYJ = [filePath+"DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8.txt", filePath+"DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8.txt", filePath+"DYJetsToEE_M-50_massWgtFix_TuneCP5_13TeV-powhegMiNNLO-pythia8-photos.txt"]
fileListData = filePath+"SingleElectron_Run2016{}-UL2016_MiniAODv2_NanoAODv9-v1.txt"

dyjCrossSectionDict = {}
dyjCrossSectionDict["DYJ_amcatnlo"] = 6077.22
dyjCrossSectionDict["DYJ_MLM"] = 6077.22
dyjCrossSectionDict["DYJToEE"] = 6077.22/3.0

chainDYJDict = {}
for index, sample in enumerate(dyjSamples):
    chEventsDYJ = ROOT.TChain("Events")
    fcDYJ = ROOT.TFileCollection("fcDYJ", "", fileListsDYJ[index])
    chEventsDYJ.AddFileInfoList(fcDYJ.GetList())
    chainDYJDict[sample] = chEventsDYJ

chEventsData = ROOT.TChain("Events")
fcDataList = []
for x in ("F", "G", "H"):
    fcData = ROOT.TFileCollection("fcData", "", fileListData.format(x))
    fcDataList.append(fcData)
    chEventsData.AddFileInfoList(fcDataList[-1].GetList())

# Create a ROOT dataframe for each dataset
df = {}
df["data"] = ROOT.RDataFrame(chEventsData)
#df["dyj"] = ROOT.RDataFrame(chEventsDYJ)
for sample in dyjSamples:
    df[sample] = ROOT.RDataFrame(chainDYJDict[sample])
processes = list(df.keys())
 
#sumWeightsDYJ = df["dyj"].Sum("genWeight").GetValue()
dyjSumWeights = {}
for sample in dyjSamples:
    dyjSumWeights[sample] = df[sample].Sum("genWeight").GetValue()


# Apply scale factors and MC weight for simulated events and a weight of 1 for the data
#for p in ["ggH", "VBF"]:
#    df[p] = df[p].Define("weight",
#            "scaleFactor_PHOTON * scaleFactor_PhotonTRIGGER * scaleFactor_PILEUP * mcWeight");
df["data"] = df["data"].Define("genWeight", "1.0")
 
# Select the events for the analysis
for p in processes:
    df[p] = df[p].Filter("HLT_Ele27_WPTight_Gsf")
 
    # Find two good barrel electrons
    df[p] = df[p].Define("goodElectrons", "Electron_cutBased > 1 && abs(Electron_eta) < 1.4442")\
                 .Filter("Sum(goodElectrons) >= 2")\
                 .Filter("Electron_pt[goodElectrons][0] > 35")
 
# Compile a function to compute the invariant mass
ROOT.gInterpreter.Declare(
"""
using namespace ROOT;
float ComputeInvariantMass(RVecF pt, RVecF eta, RVecF phi, RVecF m) {
    ROOT::Math::PtEtaPhiMVector p1(pt[0], eta[0], phi[0], m[0]);
    ROOT::Math::PtEtaPhiMVector p2(pt[1], eta[1], phi[1], m[1]);
    return (p1 + p2).mass();
}
""")
 
# Define a new column with the invariant mass and perform final event selection
hists = {}
for p in processes:
    # Make four vectors and compute invariant mass
    df[p] = df[p].Define("m_ee", "ComputeInvariantMass(Electron_pt[goodElectrons], Electron_eta[goodElectrons], Electron_phi[goodElectrons], Electron_mass[goodElectrons])")
 
    # Make additional kinematic cuts and select mass window
    #df[p] = df[p].Filter("photon_pt[goodphotons][0] / 1000.0 / m_yy > 0.35")\
    #             .Filter("photon_pt[goodphotons][1] / 1000.0 / m_yy > 0.25")\
    #             .Filter("m_yy > 105 && m_yy < 160")
    df[p] = df[p].Filter("m_ee > 80 && m_ee < 100")
 
    # Book histogram of the invariant mass with this selection
    hists[p] = df[p].Histo1D(
            ROOT.RDF.TH1DModel(p, "Dielectron invariant mass; m_{ee} [GeV];Events", 60, 70, 110),
            "m_ee", "genWeight")
 
# Run the event loop
 
# RunGraphs allows to run the event loops of the separate RDataFrame graphs
# concurrently. This results in an improved usage of the available resources
# if each separate RDataFrame can not utilize all available resources, e.g.,
# because not enough data is available.
ROOT.RDF.RunGraphs([hists[s] for s in dyjSamples+["data"]])
 
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
    # and merge to single Higgs signal
    lumi = 16812.151722000
    dyjHists[sample].Scale(lumi * dyjCrossSectionDict[sample] / dyjSumWeights[sample])
    dyjHists[sample].SetLineColor(2)
    dyjHists[sample].SetLineStyle(1)
    dyjHists[sample].SetLineWidth(2)
    dyjHists[sample].Draw("HIST SAME")
     
    # Draw ratio
    lower_pad.cd()
    lower_pad.SetGridy()
     
    ratiobkg = data.Clone()
    ratiobkg.Divide(dyjHists[sample])
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
    legend.AddEntry(dyjHists[sample], sample, "l")
    legend.Draw()
     
    # Add ATLAS label
    text = ROOT.TLatex()
    text.SetNDC()
    text.SetTextFont(72)
    text.SetTextSize(0.05)
    text.DrawLatex(0.18, 0.84, "CMS")
    text.SetTextFont(42)
    text.DrawLatex(0.18 + 0.13, 0.84, "Preliminary")
    text.SetTextSize(0.04)
    text.DrawLatex(0.18, 0.78, "#sqrt{s} = 13 TeV, 16.8 fb^{-1}")
     
    # Save the plot
    c.SaveAs("mee_"+sample+".png")
    c.SaveAs("mee_"+sample+".root")
    print("Saved figures for sample={}".format(sample))
