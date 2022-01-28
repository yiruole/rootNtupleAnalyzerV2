import os
import copy
import math
import sys
import numpy
from ROOT import TFile, TH1F, TF1, TGraph, TCanvas, gROOT, gSystem, RooStats
from tabulate import tabulate

from combineCommon import ParseXSectionFile, lookupXSection, GetUnscaledTotalEvents

gROOT.SetBatch(True)
# gSystem.Load("libRooFit")


def parse_txt_file(verbose=False):

    txt_file = open(txt_file_path, "r")

    # -----------------------------------------------------------------
    # Loop over each line in the file, which corresponds to a bin number,
    # and a collection of cuts
    # -----------------------------------------------------------------

    totLines = sum(1 for line in txt_file)
    txt_file.seek(0)
    for idx, line in enumerate(txt_file):
        if (idx % 1000) == 0 or idx+1 == totLines:
            print_str = "Reading line number " + str(idx+1) + " out of " + str(totLines)
            sys.stdout.write("%s\r" % print_str)
            sys.stdout.flush()

        if idx == 0:
            cutsSplit = line.split()
            cut_info_template = [" ".join(cutsSplit[i:i+2])+" {}" for i in range(0, len(cutsSplit), 2)]
            n_cuts = len(cut_info_template)
            continue

        # -----------------------------------------------------------------
        # First, get the important data from the line
        # -----------------------------------------------------------------
        splitLine = line.split()

        bin_number = int(splitLine[0])

        # cut_string = line.split("Bin = " + str(bin_number))[1].strip()
        # cut_info = cut_string.split()
        # n_cuts = len(cut_info) / 3  # var, condition, value
        cutVals = splitLine[1:]
        cut_string = "\t".join(cut_info_template).format(*cutVals)
        cut_info = cut_string.split()

        if verbose:
            print
            print "n_cuts=", n_cuts
            print "cutVals=", cutVals
            print "cut_string=", cut_string
            print "cut_info=", cut_info
            print "bin_number=", bin_number

        # -----------------------------------------------------------------
        # Store the bin number in a list
        # -----------------------------------------------------------------

        bin_numbers.append(bin_number)

        # -----------------------------------------------------------------
        # Initialize the dictionaries that use bin number as their first key
        # -----------------------------------------------------------------

        if bin_number not in d_binNumber_cutVariable_cutValue.keys():
            d_binNumber_cutVariable_cutValue[bin_number] = {}

        d_binNumber_cutValuesString[bin_number] = cut_string
        d_cutValuesString_binNumber[cut_string] = bin_number

        # -----------------------------------------------------------------
        # Loop over the cuts in the line
        # -----------------------------------------------------------------

        for icut in range(0, n_cuts):

            # -----------------------------------------------------------------
            # Get the information from the string
            # -----------------------------------------------------------------

            this_cut_info = cut_info[icut * 3: icut * 3 + 3]

            this_cut_variable = this_cut_info[0]
            this_cut_requirement = this_cut_info[1]
            this_cut_value = float(this_cut_info[2])

            # -----------------------------------------------------------------
            # Store the cut variables
            # -----------------------------------------------------------------

            if this_cut_variable not in cut_variables:
                cut_variables.append(this_cut_variable)
                cut_requirements.append(this_cut_requirement)

            # -----------------------------------------------------------------
            # Fill the cut variable -> cut values dictionary
            # -----------------------------------------------------------------

            if this_cut_variable not in d_cutVariable_cutValues.keys():
                d_cutVariable_cutValues[this_cut_variable] = []
            if this_cut_value not in d_cutVariable_cutValues[this_cut_variable]:
                d_cutVariable_cutValues[this_cut_variable].append(this_cut_value)

            continue

            # -----------------------------------------------------------------
            # Fill the bin number, cut variable -> cut value dictionary
            # -----------------------------------------------------------------

            if (
                this_cut_variable
                not in d_binNumber_cutVariable_cutValue[bin_number].keys()
            ):
                d_binNumber_cutVariable_cutValue[bin_number][
                    this_cut_variable
                ] = this_cut_value
            else:
                print "ERROR: This should never happen!"
                txt_file.close()
                sys.exit()

    txt_file.close()
    return

    # -----------------------------------------------------------------
    # Fill the bin number, cut variable -> cut bin dictionary
    # -----------------------------------------------------------------

    d_binNumber_cutVariable_cutBin = {}
    d_cutVariable_cutBin_binNumber = {}

    for bin_number in bin_numbers:
        for cut_variable in cut_variables:

            cut_value = d_binNumber_cutVariable_cutValue[bin_number][cut_variable]
            cut_bin = d_cutVariable_cutValues[cut_variable].index(cut_value)

            if cut_variable not in d_cutVariable_cutBin_binNumber.keys():
                d_cutVariable_cutBin_binNumber[cut_variable] = {}

            if bin_number not in d_binNumber_cutVariable_cutBin.keys():
                d_binNumber_cutVariable_cutBin[bin_number] = {}

            if cut_variable not in d_binNumber_cutVariable_cutBin[bin_number].keys():
                d_binNumber_cutVariable_cutBin[bin_number][cut_variable] = cut_bin
            else:
                print "ERROR: This should never happen!"
                sys.exit()

            if cut_bin not in d_cutVariable_cutBin_binNumber[cut_variable].keys():
                d_cutVariable_cutBin_binNumber[cut_variable][cut_bin] = bin_number

    return


def parse_root_file(d_input, verbose=False):
    d_binNumber_nSample = {}
    d_binNumber_nSampleErr = {}
    d_binNumber_nEnts = {}

    sum_hist = TH1F()
    sum_hist.Sumw2()
    sum_ents_hist = TH1F()
    sum_ents_hist.Sumw2()
    for sample in d_input.keys():

        sample_name = d_input[sample][0]
        sample_file = TFile(d_input[sample][1])
        sample_scale = float(d_input[sample][2])
        hist_name = "histo1D__" + sample_name + "__optimizer"
        hist_ents_name = "histo1D__" + sample_name + "__optimizerEntries"

        hist = sample_file.Get(hist_name)
        print "getting hist", hist_name, "from:", sample_file.GetName(),
        sys.stdout.flush()
        if not hist:
            print "ERROR: could not find hist", hist_name, "in file", sample_file.GetName()
            print "Quitting."
            exit(-1)
        print "entries:", hist.GetEntries()
        hist.Scale(sample_scale)
        # print 'bin0:',hist.GetBinContent(0)
        # print 'bin1:',hist.GetBinContent(1)

        histEnts = sample_file.Get(hist_ents_name)
        print "getting hist", hist_ents_name, "from:", sample_file.GetName(),
        sys.stdout.flush()
        if not histEnts:
            print "ERROR: could not find hist", hist_ents_name, "in file", sample_file.GetName()
            print "Quitting."
            exit(-1)
        print "entries:", histEnts.GetEntries()
        print "entries bin 5836:", histEnts.GetBinContent(5836)

        if sum_hist.GetEntries() <= 0:
            sum_hist = copy.deepcopy(hist)
        else:
            sum_hist.Add(hist)
        if "data" not in hist.GetName().lower():
            if sum_ents_hist.GetEntries() <= 0:
                sum_ents_hist = copy.deepcopy(histEnts)
            else:
                sum_ents_hist.Add(histEnts)
            if verbose:
                print "adding", histEnts.GetName(), "with", histEnts.GetEntries(), "to totalEnts hist"
                print "totalEnts hist now has", sum_ents_hist.GetEntries(), "entries"
                print "totalEnts hist now has", sum_ents_hist.GetBinContent(
                    5836
                ), "entries in bin 5836"

        sample_file.Close()

    nbins = sum_hist.GetNbinsX()
    # print 'sum_hist bin 0:',sum_hist.GetBinContent(0)
    # print 'sum_hist bin 1:',sum_hist.GetBinContent(1)

    for ibin in range(0, nbins):
        d_binNumber_nSample[ibin] = sum_hist.GetBinContent(ibin + 1)
        d_binNumber_nSampleErr[ibin] = sum_hist.GetBinError(ibin + 1)
        d_binNumber_nEnts[ibin] = sum_ents_hist.GetBinContent(ibin + 1)
        # if ibin==5836:
        #    print 'sum_ents_hist has',sum_ents_hist.GetBinContent(5836),'entries in bin',ibin

    return d_binNumber_nSample, d_binNumber_nSampleErr, d_binNumber_nEnts


def calculateEfficiency(nS, signal_sample, d_signal_totalEvents):
    # optimizer nS is weighted the usual way, so unweight it before calculating the efficiency
    weight = (intLumi * d_signal_crossSections[signal_sample]) / d_signal_totalEvents[
        signal_sample
    ]
    # print 'efficiency is: (', nS, '/', weight, ')/', d_signal_totalEvents[signal_sample], '=', 1.0*nS/d_signal_totalEvents[signal_sample]
    # print 'weight is: (', intLumi, '*', d_signal_crossSections[signal_sample], ') /', d_signal_totalEvents[signal_sample], '=', weight
    return 1.0 * (nS / weight) / d_signal_totalEvents[signal_sample]


def evaluation(nS, nB, efficiency, bkgEnts):
    # see: https://twiki.cern.ch/twiki/bin/view/CMS/FigureOfMerit
    # and https://arxiv.org/pdf/physics/0702156.pdf [1]
    try:
        # s/sqrt(s+b)
        # value = nS / ( math.sqrt ( nS + nB ) )
        tau = bkgEnts / nB
        # switch to asymptotic formula
        # NB: this approximation doesn't work well with nB < ~ 5 events
        if figureOfMerit == "asymptotic":
            value = math.sqrt(2 * ((nS + nB) * math.log(1 + nS / nB) - nS))
        elif figureOfMerit == "punzi":
            # punzi
            a = 2  # nSigmasExclusion
            b = 5  # nSigmasDiscovery
            # value = efficiency / (nSigmas / 2.0 + math.sqrt(nB))
            smin = a**2/8 + 9*b**2/13 + a*math.sqrt(nB) + (b/2)*math.sqrt(b**2 + 4*a*math.sqrt(nB) + 4*nB)
            value = efficiency / smin
        elif figureOfMerit == "zbi":
            value = RooStats.NumberCountingUtils.BinomialWithTauExpZ(nS, nB, tau)
        elif figureOfMerit == "zpl":  # [1], eqn. 25
            nOff = bkgEnts
            nOn = nS + nB
            nTot = nOff + nOn
            value = math.sqrt(2)*math.sqrt(nOn*math.log(nOn*(1+tau)/nTot) + nOff*math.log(nOff*(1+tau)/(nTot*tau)))
        else:
            raise RuntimeError("Evaluation of '{}' as figure of merit is not implemented".format(figureOfMerit))
    except ZeroDivisionError:
        value = -999
    except ValueError:
        print "WARNING: had a domain error calculating the value with nS=", nS, "and nB=", nB
        value = -999
    return value


def evaluate(bin_number, d_signal, d_background, signal_sample, d_signal_totalEvents, d_backgroundRawEvents):
    nS = d_signal[bin_number]
    nB = d_background[bin_number]
    nBEnts = d_backgroundRawEvents[bin_number]
    ## For amc@NLO.
    # if nS < 0:
    #  nS = 0
    if nB < 0:
        nB = 0
    efficiency = calculateEfficiency(nS, signal_sample, d_signal_totalEvents)
    v = evaluation(nS, nB, efficiency, nBEnts)
    # print 'value=',v
    return v


def string_to_bins(cut_string):
    bins = []
    # cut_values = []

    string_fields = cut_string.split()

    for cut_variable in cut_variables:
        if cut_variable not in string_fields:
            print "ERROR: I identified " + cut_variable + " as a cut variable, based on " + txt_file_path
            print "       But I can't find " + cut_variable + " in this string: " + cut_string
            sys.exit()
        cut_variable_index_in_string = string_fields.index(cut_variable)
        cut_value = float(string_fields[cut_variable_index_in_string + 2])
        cut_bin = d_cutVariable_cutValues[cut_variable].index(cut_value)
        bins.append(cut_bin)
    return bins


def bins_to_string(cut_bins):

    cut_string = ""

    if len(cut_bins) != len(cut_variables):
        print "ERROR: You are asking for the cut string for", len(
            cut_bins
        ), " cut bins, but there are", len(cut_variables), " cut variables "
        sys.exit()

    for i, cut_variable in enumerate(cut_variables):
        cut_bin = cut_bins[i]
        cut_value_int = int(d_cutVariable_cutValues[cut_variable][cut_bin])
        cut_value_float = float(d_cutVariable_cutValues[cut_variable][cut_bin])
        if cut_value_int == cut_value_float:
            cut_value = cut_value_int
        else:
            cut_value = cut_value_float
        cut_requirement = cut_requirements[i]
        cut_string = (
            cut_string
            + cut_variable
            + " "
            + cut_requirement
            + " "
            + str(cut_value)
            + "\t"
        )

    cut_string = cut_string.strip()

    return cut_string


####################################################################################################
# Configurables
####################################################################################################
massPoints = [
    str(i) for i in range(300, 3100, 100)
]  # go from 300-2000 in 100 GeV steps
massPoints.extend(["3500", "4000"])
massPoints.remove("2500")  # FIXME 2016
# massPoints.remove("3000")  # FIXME 2017
signalNameTemplate = "LQToDEle_M-{0}_pair"
# signalNameTemplate = "LQToBEle_M-{0}_pair"
xsectionFile = "$LQANA/config/xsection_13TeV_2015.txt"
# these have rescaling applied
mc_filepath = (
    # "$LQDATA/nanoV6/2016/opt/eejj_10jul2020/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
    # "$LQDATA/nanoV6/2017/opt/eejj_10jul2020/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
    # "$LQDATA/nanoV6/2018/opt/eejj_2jul2020/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
    # "$LQDATA/nanoV6/2018/opt/eejj_10jul2020/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
    # nanoV7
    # "$LQDATA/nanoV7/2016/opt/eejj_14sep2020/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
    # "$LQDATA/nanoV7/2017/opt/eejj_14sep2020/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
    # "$LQDATA/nanoV7/2018/opt/eejj_14sep2020/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
    #
    # "$LQDATA/nanoV7/2016/opt/eejj_16oct2020/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
    # "$LQDATA/nanoV7/2017/opt/eejj_22oct2020/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
    # b-tag studies
    # "$LQDATA/nanoV7/2016/opt/eejj_23jun2021_opt/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
    # "$LQDATA/nanoV7/2016/opt/eejj_gteOneBtag_btagLoose_9jul2021/output_cutTable_lq_eejj_oneBTag_opt/analysisClass_lq_eejj_oneBTag_plots.root"
    # "$LQDATA/nanoV7/2016/opt/eejj_gteOneBtag_btagMed_9jul2021/output_cutTable_lq_eejj_oneBTag_opt/analysisClass_lq_eejj_oneBTag_plots.root"
    # "$LQDATA/nanoV7/2016/opt/eejj_gteTwoBtags_btagLoose_13jul2021/output_cutTable_lq_eejj_twoBTags_opt/analysisClass_lq_eejj_oneBTag_plots.root"
    # "$LQDATA/nanoV7/2016/opt/eejj_gteTwoBtags_btagMed_13jul2021/output_cutTable_lq_eejj_twoBTags_opt/analysisClass_lq_eejj_oneBTag_plots.root"
    # other studies
    # "$LQDATA/nanoV7/2016/opt/eejj_loosenMee_10aug2021/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
    # "$LQDATA/nanoV7/2016/opt/eejj_loosenMee_addMasym_10aug2021/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
    # "$LQDATA/nanoV7/2016/opt/eejj_loosenMee_addMasym_addMET_10aug2021/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
    "$LQDATA/nanoV7/2016/opt/eejj_opt_egLoose_18jan2022/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
)
qcd_data_filepath = (
    # "$LQDATA//nanoV6/2016/opt/qcdOpt_10jul2020/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_QCD_plots.root"
    # "$LQDATA/nanoV6/2017/opt/qcdOpt_10jul2020/output_cutTable_lq_eejj_QCD_opt/analysisClass_lq_eejj_QCD_plots.root"
    # "$LQDATA/nanoV6/2018/opt/qcdOpt_10jul2020/output_cutTable_lq_eejj_QCD_opt/analysisClass_lq_eejj_QCD_plots.root"
    # nanoV7
    # "$LQDATA/nanoV7/2016/opt/qcdOpt_14sep2020/output_cutTable_lq_eejj_QCD_opt/analysisClass_lq_eejj_QCD_plots.root"
    # "$LQDATA/nanoV7/2017/opt/qcdOpt_14sep2020/output_cutTable_lq_eejj_QCD_opt/analysisClass_lq_eejj_QCD_plots.root"
    # "$LQDATA/nanoV7/2018/opt/qcdOpt_14sep2020/output_cutTable_lq_eejj_QCD_opt/analysisClass_lq_eejj_QCD_plots.root"
    # "$LQDATA/nanoV7/2017/opt/qcdOpt_22oct2020/output_cutTable_lq_eejj_QCD_opt/analysisClass_lq_eejj_QCD_plots.root"
    # b-tag studies
    # "$LQDATA/nanoV7/2016/opt/eejj_23jun2021/output_cutTable_lq_eejj_QCD_opt/analysisClass_lq_eejj_QCD_plots.root"
    # "$LQDATA/nanoV7/2016/opt/qcd_eejj_btagLoose_gteOneBTag_13jul2021/output_cutTable_lq_eejj_QCD_oneBTag_opt/analysisClass_lq_eejj_QCD_oneBTag_plots.root"
    # "$LQDATA/nanoV7/2016/opt/qcd_eejj_btagMed_gteOneBTag_13jul2021/output_cutTable_lq_eejj_QCD_oneBTag_opt/analysisClass_lq_eejj_QCD_oneBTag_plots.root"
    # "$LQDATA/nanoV7/2016/opt/qcd_eejj_btagLoose_gtetwoBTags_13jul2021/output_cutTable_lq_eejj_QCD_twoBTags_opt/analysisClass_lq_eejj_QCD_oneBTag_plots.root"
    # "$LQDATA/nanoV7/2016/opt/qcd_eejj_btagMed_gtetwoBTags_13jul2021/output_cutTable_lq_eejj_QCD_twoBTags_opt/analysisClass_lq_eejj_QCD_oneBTag_plots.root"
    # other studies
    # "$LQDATA/nanoV7/2016/opt/qcd_eejj_loosenMee_10aug2021/output_cutTable_lq_eejj_QCD_opt/analysisClass_lq_eejj_QCD_plots.root"
    # "$LQDATA/nanoV7/2016/opt/qcd_eejj_loosenMee_addMasym_10aug2021/output_cutTable_lq_eejj_QCD_opt/analysisClass_lq_eejj_QCD_plots.root"
    # "$LQDATA/nanoV7/2016/opt/qcd_eejj_loosenMee_addMasym_addMET_10aug2021/output_cutTable_lq_eejj_QCD_opt/analysisClass_lq_eejj_QCD_plots.root"
    "$LQDATA/nanoV7/2016/opt/qcd_eejj_optEGLooseFR_17jan2022/output_cutTable_lq_eejj_QCD_opt/analysisClass_lq_eejj_QCD_plots.root"
)
txt_file_path_eejj = (
    # "$LQDATA/nanoV6/2016/opt/eejj_10jul2020/condor/optimizationCuts.txt"
    # "$LQDATA/nanoV6/2016/opt/prefire_2jul2020/output_cutTable_lq_eejj_opt/optimizationCuts.txt"
    # "$LQDATA/nanoV6/2017/opt/prefire_2jul2020/output_cutTable_lq_eejj_opt/optimizationCuts.txt"
    # "$LQDATA/nanoV6/2018/opt/eejj_2jul2020/output_cutTable_lq_eejj_opt/optimizationCuts.txt"
    # nanoV7
    # "$LQDATA/nanoV7/2016/opt/eejj_14sep2020/output_cutTable_lq_eejj_opt/optimizationCuts.txt"
    # "$LQANA/versionsOfOptimization/nanoV7/2016/eejj_23jun2021/optimizationCuts.txt"
    #
    # "$LQANA/versionsOfOptimization/nanoV7/2016/eejj_11aug_loosenMee/optimizationCuts.txt"
    # "$LQANA/versionsOfOptimization/nanoV7/2016/eejj_11aug_loosenMee_addMasym/optimizationCuts.txt"
    # "/tmp/scooper/optimizationCuts.txt"
    # "$LQANA/versionsOfOptimization/nanoV7/2016/eejj_11aug_loosenMee_addMasym_addPFMET/optimizationCuts.txt"
    "$LQANA/versionsOfOptimization/nanoV7/2016/eejj_17jan_egmLooseID/optimizationCuts.txt"
)
# # for eejj only
# ttbar_data_filepath = (
#     os.environ["LQDATA"]
#     + "/2016opt/nov19_emujj_ttbar/output_cutTable_lq_ttbar_emujj_correctTrig_opt/analysisClass_lq_ttbarEst_plots.root"
# )

mc_filepath_enujj = (
    os.environ["LQDATA"]
    + "/2016opt/enujj_psk_jan19/output_cutTable_lq_enujj_MT_opt/analysisClass_lq_enujj_MT_plots.root"
)
qcd_data_filepath_enujj = (
    os.environ["LQDATA"]
    + "/2016opt/enujj_QCD_jan19/output_cutTable_lq_enujj_MT_QCD_opt/analysisClass_lq_enujj_QCD_plots.root"
)
txt_file_path_enujj = (
    os.environ["LQANA"]
    + "/versionsOfAnalysis_enujj/jan17/opt_jan19/optimizationCuts.txt"
)
#
doEEJJ = True
# supported figures of merit: punzi, zbi, zpl, asymptotic
figureOfMerit = "punzi"

jitter = 2

if "2016" in mc_filepath:
    # wjet = "WJet_amcatnlo_Inc"
    # wjet = "WJet_amcatnlo_jetBinned"
    wjet = "WJet_amcatnlo_ptBinned"
    zjet = "ZJet_amcatnlo_ptBinned"
    # 1/pb
    intLumi = 35867.0  # 2016
elif "2017" in mc_filepath:
    intLumi = 41540.0  # 2017
    wjet = "WJet_amcatnlo_jetBinned"
    zjet = "ZJet_jetAndPtBinned"
elif "2018" in mc_filepath:
    intLumi = 59736.0  # 2018
    wjet = "WJet_amcatnlo_jetBinned"
    zjet = "ZJet_jetAndPtBinned"
diboson = "DIBOSON_nlo"
ttbar = "TTbar_powheg"

d_eejj_background_filepaths = {
    "ttbar": [ttbar, mc_filepath, 1.0],
    # "ttbar": ["TTBarFromDATA", ttbar_data_filepath, 1.0],
    "qcd": ["QCDFakes_DATA", qcd_data_filepath, 1.0],
    # "ttbar" : [ "TTbar_Madgraph"      , mc_filepath  , 1.0  ],
    # "qcd"   : [ "QCD_EMEnriched"      , mc_filepath  , 1.0  ],
    "wjet": [wjet, mc_filepath, 1.0],
    "zjet": [zjet, mc_filepath, 1.0],
    "stop": ["SingleTop", mc_filepath, 1.0],
    "vv": [diboson, mc_filepath, 1.0],
    "gjet": ["PhotonJets_Madgraph", mc_filepath, 1.0],
}

d_enujj_background_filepaths = {
    # "ttbar" : [ "TTbar_amcatnlo_Inc"  , mc_filepath_enujj, 1.0 ],
    "ttbar": ["TTbar_powheg", mc_filepath_enujj, 1.0],
    "qcd": ["QCDFakes_DATA", qcd_data_filepath_enujj, 1.0],
    # "ttbar" : [ "TTbar_Madgraph"      , mc_filepath_enujj  , 1.0  ],
    # "qcd"   : [ "QCD_EMEnriched"      , mc_filepath_enujj  , 1.0  ],
    "wjet": ["WJet_amcatnlo_ptBinned", mc_filepath_enujj, 1.0],
    "zjet": ["ZJet_amcatnlo_ptBinned", mc_filepath_enujj, 1.0],
    "stop": ["SingleTop", mc_filepath_enujj, 1.0],
    "vv": ["DIBOSON_amcatnlo", mc_filepath_enujj, 1.0],
    "gjet": ["PhotonJets_Madgraph", mc_filepath_enujj, 1.0],
}

d_eejj_signal_filepaths_list = [{str(mass): [signalNameTemplate.format(mass), mc_filepath, 1.0]} for mass in massPoints]

d_enujj_signal_filepaths_list = [{str(mass): [signalNameTemplate.format(mass), mc_filepath_enujj, 1.0]} for mass in massPoints]

searchDir = os.path.dirname(mc_filepath)
totalEventList = [GetUnscaledTotalEvents(TFile.Open(mc_filepath), signalNameTemplate.format(mass)) for mass in massPoints]
d_eejj_signal_totalEvents = {signalNameTemplate.format(mass): value for (mass, value) in zip(massPoints, totalEventList)}

xsectionDict = ParseXSectionFile(xsectionFile)
xsecList = [float(lookupXSection(signalNameTemplate.format(mass))) for mass in massPoints]
d_signal_crossSections = {signalNameTemplate.format(mass): value for (mass, value) in zip(massPoints, xsecList)}

# for eejj
if doEEJJ:
    d_signal_totalEvents = d_eejj_signal_totalEvents
    d_signal_filepaths_list = d_eejj_signal_filepaths_list
    d_background_filepaths = d_eejj_background_filepaths
    d_data_filepaths = {"DATA": ["DATA", mc_filepath, 1.0]}
    txt_file_path = txt_file_path_eejj
else:
    searchDirENuJJ = os.path.dirname(mc_filepath_enujj)
    totalEventListENuJJ = [GetUnscaledTotalEvents(TFile.Open(mc_filepath_enujj), signalNameTemplate.format(mass)) for mass in massPoints]
    d_enujj_signal_totalEvents = {signalNameTemplate.format(mass): value for (mass, value) in zip(massPoints, totalEventListENuJJ)}
    d_signal_totalEvents = d_enujj_signal_totalEvents
    d_signal_filepaths_list = d_enujj_signal_filepaths_list
    d_background_filepaths = d_enujj_background_filepaths
    d_data_filepaths = {"DATA": ["DATA", mc_filepath_enujj, 1.0]}
    txt_file_path = txt_file_path_enujj
txt_file_path = os.path.expandvars(txt_file_path)

cut_variables = []
cut_requirements = []
cut_values = []
bin_numbers = []

d_cutVariable_maxCutValues = {}

d_binNumber_cutValuesString = {}
d_binNumber_cutVariable_cutValue = {}
d_cutVariable_cutValues = {}
d_cutValuesString_binNumber = {}


####################################################################################################
# Run!
####################################################################################################
if not os.path.isfile(txt_file_path):
    print "ERROR: optimization cuts txt file not found:", txt_file_path
    exit(-1)
print "Parsing txt file", txt_file_path, "..."
sys.stdout.flush()
parse_txt_file()
print "Parsed."

print "Figure of merit: {}".format(figureOfMerit)

verbose = False
d_binNumber_nB, d_binNumber_nBErr, d_binNumber_nBMCEnts = parse_root_file(
    d_background_filepaths, verbose
)
# print 'd_binNumber_nBMCEnts[5836]=',d_binNumber_nBMCEnts[5836]
d_binNumber_nD, d_binNumber_nDErr, d_binNumber_nDEnts = parse_root_file(
    d_data_filepaths
)

selectedEfficienciesByLQMass = []
selectedNsByLQMass = []
selectedNbByLQMass = []
selectedNbMCEntsByLQMass = []
selectedValueByLQMass = []
lqMasses = []

# print 'Checking for signal histograms'
# for signal_sample in d_signal_filepaths_list:
#    parse_root_file( signal_sample )

for signal_sample in d_signal_filepaths_list:
    d_binNumber_nS, d_binNumber_nSErr, d_binNumber_nSEnts = parse_root_file(
        signal_sample
    )
    print "looking at", signal_sample
    # XXX SIC make histo
    # mejHisto = TH1F('mej_hist',',mej_hist',len(bin_numbers),0,len(bin_numbers)+1)

    max_bin = -999
    max_value = -999
    max_nS = -999
    max_nB = -999
    max_nBMCEnts = -999
    max_nD = -999
    max_string = ""
    max_eff = -1.0

    for binNumber in bin_numbers:
        nS = d_binNumber_nS[binNumber]
        nSErr = d_binNumber_nSErr[binNumber]
        nB = d_binNumber_nB[binNumber]
        nBErr = d_binNumber_nBErr[binNumber]
        nBMCEnts = d_binNumber_nBMCEnts[binNumber]
        nD = d_binNumber_nD[binNumber]
        # if nS < 0:
        #  nS = 0
        # if nB < 0:
        #  nB = 0
        ##XXX ignore any set of cuts with nB<0.01
        # if nB < 0.01:
        #  continue
        ##XXX ignore any cuts with less than 5 background events
        # if nBMCEnts < 5:
        #  continue
        ##XXX ignore any set of cuts with nB < 0
        if nB < 0:
            continue
        ## ignore any set of cuts if the nBErr/nB > 50%
        # if nBErr/nB > 0.5:
        #  continue
        if verbose:
            print "binNumber=", binNumber,
            print "evaluated to: nS=", nS, "nB=", nB, "MCents=", nBMCEnts, ";",
        value = evaluate(
            binNumber,
            d_binNumber_nS,
            d_binNumber_nB,
            signal_sample.values()[0][0],
            d_signal_totalEvents,
            d_binNumber_nBMCEnts
        )
        if verbose:
            # print 'final evaluation: nS=',nS,'nB=',nB,'value=',value,
            print "value=", value,
            print "eff=", calculateEfficiency(
                nS, signal_sample.values()[0][0], d_signal_totalEvents
            )
            print d_binNumber_cutValuesString[binNumber]
        # mejHisto.SetBinContent(binNumber,value)

        if value > max_value:
            max_value = value
            max_bin = binNumber
            max_nS = nS
            max_nB = nB
            max_nBMCEnts = nBMCEnts
            max_nD = nD
            max_string = d_binNumber_cutValuesString[max_bin]
            max_eff = calculateEfficiency(
                nS, signal_sample.values()[0][0], d_signal_totalEvents
            )
            if verbose:
                print "---> NEW MAX FOUND: bin=", max_bin, "cut info=", max_string, "max value=", max_value, "eff=", max_eff
                print "     evaluated to: nS=", nS, "nB=", nB, "nBMCEnts=", nBMCEnts
                print "     d_binNumber_nBMCEnts [ max_bin ] =", d_binNumber_nBMCEnts[
                    max_bin
                ]

    print signal_sample.keys()[0], ": Bin with best value was bin #" + str(
        max_bin
    ), "\tCut info was:\t" + max_string, "\t value = %.4f" % max_value, " nS = %.2f" % max_nS, ", nB = %.2f" % max_nB  # , ", nD = %d" % max_nD
    signalSampleName = signal_sample.values()[0][0]
    if "_M-" in signalSampleName:
        signalSampleMass = int(signalSampleName[signalSampleName.find("_M-") + 3: signalSampleName.rfind("_")])
    else:
        signalSampleName = int(signalSampleName[signalSampleName.find("_M") + 2:])
    print "LQ mass:", signalSampleMass, "had efficiency at maxOptPoint:", max_eff
    selectedEfficienciesByLQMass.append(max_eff)
    selectedNsByLQMass.append(max_nS)
    selectedNbByLQMass.append(max_nB)
    selectedNbMCEntsByLQMass.append(max_nBMCEnts)
    selectedValueByLQMass.append(max_value)
    lqMasses.append(signalSampleMass)

    max_bins = string_to_bins(max_string)
    test_max_string = bins_to_string(max_bins)
    print "max_bins=", max_bins, "test_max_string=", test_max_string
    test_binNumber = d_cutValuesString_binNumber[test_max_string]

    if test_max_string != max_string:
        print "ERROR: Something is wrong with how you map strings to bins (string test)"
        sys.exit()

    if test_binNumber != max_bin:
        print "ERROR: Something is wrong with how you map strings to bins (bin test)"
        sys.exit()

    for i, cut_variable in enumerate(cut_variables):

        if cut_variable not in d_cutVariable_maxCutValues.keys():
            d_cutVariable_maxCutValues[cut_variable] = []

        this_bin = max_bins[i]

        this_cut_value = d_cutVariable_cutValues[cut_variable][this_bin]

        n_bins = len(d_cutVariable_cutValues[cut_variable])

        lower_jitter_bin = max(0, this_bin - jitter)
        upper_jitter_bin = min(n_bins - 1, this_bin + jitter)

        new_max_bins_lower_jitter = (
            max_bins[:i] + [lower_jitter_bin] + max_bins[i + 1:]
        )
        new_max_bins_upper_jitter = (
            max_bins[:i] + [upper_jitter_bin] + max_bins[i + 1:]
        )

        new_max_string_lower_jitter = bins_to_string(new_max_bins_lower_jitter)
        new_max_string_upper_jitter = bins_to_string(new_max_bins_upper_jitter)

        new_max_binNumber_lower_jitter = d_cutValuesString_binNumber[
            new_max_string_lower_jitter
        ]
        new_max_binNumber_upper_jitter = d_cutValuesString_binNumber[
            new_max_string_upper_jitter
        ]

        new_value_lower_jitter = evaluate(
            new_max_binNumber_lower_jitter,
            d_binNumber_nS,
            d_binNumber_nB,
            signal_sample.values()[0][0],
            d_signal_totalEvents,
            d_binNumber_nBMCEnts
        )
        new_value_upper_jitter = evaluate(
            new_max_binNumber_upper_jitter,
            d_binNumber_nS,
            d_binNumber_nB,
            signal_sample.values()[0][0],
            d_signal_totalEvents,
            d_binNumber_nBMCEnts
        )

        lower_jitter_percent_change = (
            100.0 * (new_value_lower_jitter - max_value) / max_value
        )
        upper_jitter_percent_change = (
            100.0 * (new_value_upper_jitter - max_value) / max_value
        )

        to_print = ""
        to_print = to_print + "\t" + "Jitter " + cut_variable + "\t" + "["
        to_print = (
            to_print
            + str(int(d_cutVariable_cutValues[cut_variable][lower_jitter_bin]))
            + ", "
        )
        to_print = (
            to_print
            + str(int(d_cutVariable_cutValues[cut_variable][upper_jitter_bin]))
            + " ]"
        )
        to_print = to_print + "\t" + "value % change:" + " ["
        to_print = to_print + "%.2f" % lower_jitter_percent_change
        to_print = to_print + ", "
        to_print = to_print + "%.2f" % upper_jitter_percent_change
        to_print = to_print + "]"

        print to_print
        print

        d_cutVariable_maxCutValues[cut_variable].append(this_cut_value)


print "\n\n"

x_array = []
d_cutVariable_yArray = {}

# to_print = "LQ mass \t"
# for signal_sample in d_signal_filepaths_list:
#    to_print = to_print + signal_sample.keys()[0] + "\t"
# print to_print
# print "-------------------------------------------------------------------------------------------"
#
# for cut_variable in cut_variables:
#    d_cutVariable_yArray [cut_variable ] = []
#    to_print = cut_variable + "\t"
#    for i, signal_sample in enumerate(d_signal_filepaths_list):
#        lq_mass = int ( signal_sample.keys()[0] )
#        cut_value = int (d_cutVariable_maxCutValues[cut_variable][i])
#        to_print = to_print + str(cut_value ) + "\t"
#
#        if ( lq_mass not in x_array ) : x_array.append ( float ( lq_mass ) )
#        d_cutVariable_yArray [cut_variable ].append ( float ( cut_value )  )
#
#    print to_print

columnNames = ["LQ mass (GeV)"]
columnNames.extend(
    [signal_sample.keys()[0] for signal_sample in d_signal_filepaths_list]
)
table = []
for cut_variable in cut_variables:
    d_cutVariable_yArray[cut_variable] = []
    # to_print = cut_variable + "\t"
    row = [cut_variable]
    for i, signal_sample in enumerate(d_signal_filepaths_list):
        lq_mass = int(signal_sample.keys()[0])
        # cut_value = int(d_cutVariable_maxCutValues[cut_variable][i])
        cut_value = round(float(d_cutVariable_maxCutValues[cut_variable][i]), 3)
        # to_print = to_print + str(cut_value ) + "\t"
        row.append(cut_value)

        if lq_mass not in x_array:
            x_array.append(float(lq_mass))
        d_cutVariable_yArray[cut_variable].append(float(cut_value))
    table.append(row)
nbRow = ["nB"] + [round(nb, 3) for nb in selectedNbByLQMass]
nbMCEntsRow = ["nBMCEnts"] + [round(nbMC, 3) for nbMC in selectedNbMCEntsByLQMass]
nsRow = ["nS"] + [round(ns, 3) for ns in selectedNsByLQMass]
valRow = [figureOfMerit] + [round(val, 4) for val in selectedValueByLQMass]
table.append(nbRow)
table.append(nbMCEntsRow)
table.append(nsRow)
table.append(valRow)

print tabulate(table, headers=columnNames, tablefmt="github")
print tabulate(table, headers=columnNames, tablefmt="latex")

print "\n\n"

# get max fit range
maxFitMass = 0.0
for i, mass in enumerate(lqMasses):
    nB = selectedNbByLQMass[i]
    if nB > 1:
        maxFitMass = mass
    else:
        break
print "maxFitMass=", maxFitMass

func2 = TF1("func2", "pol2(0)", 150.0, maxFitMass)
func1 = TF1("func1", "pol1(0)", 150.0, maxFitMass)

fit_functions = ["func1", "func2"]

optimizationRootFile = TFile("optimization.root", "recreate")
optimizationRootFile.cd()
# MEJ HIST
# mejHisto.Write()

canvas = TCanvas()
canvas.cd()
graph = TGraph(
    len(lqMasses),
    numpy.array(lqMasses).astype("float"),
    numpy.array(selectedEfficienciesByLQMass),
)
graph.Draw("AP")
graph.GetXaxis().SetTitle("LQ mass [GeV]")
graph.GetYaxis().SetTitle("eff*acc")
graph.GetXaxis().SetRangeUser(0, 2000)
maximum = graph.GetHistogram().GetMaximum()
graph.GetHistogram().SetMaximum(maximum * 1.5)
graph.Draw("AP")
graph.SetName("efficiencyTimesAcceptance")
graph.Write()

canvas = TCanvas()
canvas.cd()
graph = TGraph(
    len(lqMasses),
    numpy.array(lqMasses).astype("float"),
    numpy.array(selectedNsByLQMass),
)
graph.Draw("AP")
graph.GetXaxis().SetTitle("LQ mass [GeV]")
graph.GetYaxis().SetTitle("nS")
graph.GetXaxis().SetRangeUser(0, 2000)
maximum = graph.GetHistogram().GetMaximum()
graph.GetHistogram().SetMaximum(maximum * 1.5)
graph.Draw("AP")
graph.SetName("nS")
graph.Write()

canvas = TCanvas()
canvas.cd()
graph = TGraph(
    len(lqMasses),
    numpy.array(lqMasses).astype("float"),
    numpy.array(selectedNbByLQMass),
)
graph.Draw("AP")
graph.GetXaxis().SetTitle("LQ mass [GeV]")
graph.GetYaxis().SetTitle("nB")
graph.GetXaxis().SetRangeUser(0, 2000)
maximum = graph.GetHistogram().GetMaximum()
graph.GetHistogram().SetMaximum(maximum * 1.5)
graph.Draw("AP")
graph.SetName("nB")
graph.Write()

for cut_variable in cut_variables:
    for fit_function in fit_functions:

        canvas = TCanvas()
        canvas.cd()

        graph = TGraph(
            len(x_array),
            numpy.array(x_array),
            numpy.array(d_cutVariable_yArray[cut_variable]),
        )
        graph.SetName("graph_" + cut_variable + "_" + fit_function)
        canvas.SetName("canvas_" + cut_variable + "_" + fit_function)

        graph.Draw("AP")

        graph.GetXaxis().SetTitle("LQ mass [GeV]")
        graph.GetYaxis().SetTitle(cut_variable)
        graph.GetXaxis().SetRangeUser(0, 2000)

        maximum = graph.GetHistogram().GetMaximum()
        graph.GetHistogram().SetMaximum(maximum * 1.5)

        graph.Fit(fit_function, "R")

        graph.Draw("AP")

        canvas.SaveAs(cut_variable + "_" + fit_function + ".png")
        canvas.SaveAs(cut_variable + "_" + fit_function + ".C")
        canvas.Write()
        graph.Write()
        # stored with TGraph
        # function = graph.GetFunction(fit_function)
        # function.SetName('fitFunc_'+cut_variable)
        # function.Write()

optimizationRootFile.Close()
