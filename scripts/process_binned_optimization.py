import os, copy, math, sys, numpy
from ROOT import TFile,TH1F,TF1,TGraph,TCanvas,gROOT
from prettytable import PrettyTable

gROOT.SetBatch(True)

def parse_txt_file (verbose=False):
    
    txt_file = open ( txt_file_path, "r" ) 

    #-----------------------------------------------------------------
    # Loop over each line in the file, which corresponds to a bin number,
    # and a collection of cuts
    #-----------------------------------------------------------------

    totLines = sum(1 for line in txt_file)
    txt_file.seek(0)
    for idx,line in enumerate(txt_file):
        if (idx%1000)==0:
            print_str = 'Reading line number '+str(idx)+' out of '+str(totLines)
            sys.stdout.write('%s\r' % print_str)
            sys.stdout.flush()

        #-----------------------------------------------------------------
        # First, get the important data from the line
        #-----------------------------------------------------------------

        bin_number = int ( line.split("Bin = ")[1].split()[0].strip() ) 

        cut_string = line.split("Bin = " + str ( bin_number ) )[1].strip()
        cut_info = cut_string.split()
        n_cuts = len ( cut_info ) / 3  # var, condition, value

        if verbose:
          print
          print 'n_cuts=',n_cuts
          print 'cut_string=',cut_string
          print 'cut_info=',cut_info
          print 'bin_number=',bin_number

        #-----------------------------------------------------------------
        # Store the bin number in a list
        #-----------------------------------------------------------------

        bin_numbers.append ( bin_number ) 

        #-----------------------------------------------------------------
        # Initialize the dictionaries that use bin number as their first key
        #-----------------------------------------------------------------
        
        if bin_number not in d_binNumber_cutVariable_cutValue.keys():
            d_binNumber_cutVariable_cutValue [ bin_number ] = {} 

        d_binNumber_cutValuesString [ bin_number ] = cut_string
        d_cutValuesString_binNumber [ cut_string ] = bin_number

        #-----------------------------------------------------------------
        # Loop over the cuts in the line 
        #-----------------------------------------------------------------
        
        for icut in range ( 0, n_cuts ) :

            #-----------------------------------------------------------------
            # Get the information from the string
            #-----------------------------------------------------------------
            
            this_cut_info = cut_info[icut * 3 : icut * 3 + 3 ]
            
            this_cut_variable    = this_cut_info[0]
            this_cut_requirement = this_cut_info[1]
            this_cut_value       = float ( this_cut_info[2]) 

            #-----------------------------------------------------------------
            # Store the cut variables
            #-----------------------------------------------------------------
            
            if this_cut_variable not in cut_variables:
                cut_variables.append ( this_cut_variable ) 
                cut_requirements.append ( this_cut_requirement ) 
                
            #-----------------------------------------------------------------
            # Fill the cut variable -> cut values dictionary
            #-----------------------------------------------------------------
            
            if this_cut_variable not in d_cutVariable_cutValues.keys():
                d_cutVariable_cutValues [ this_cut_variable ] = [] 
            if this_cut_value not in d_cutVariable_cutValues [ this_cut_variable ] :
                d_cutVariable_cutValues [ this_cut_variable ].append ( this_cut_value ) 

            continue

            #-----------------------------------------------------------------
            # Fill the bin number, cut variable -> cut value dictionary
            #-----------------------------------------------------------------

            if this_cut_variable not in d_binNumber_cutVariable_cutValue[ bin_number ].keys() :
                d_binNumber_cutVariable_cutValue [ bin_number ][ this_cut_variable ] = this_cut_value
            else:
                print "ERROR: This should never happen!"
                txt_file.close()
                sys.exit()

    txt_file.close()
    return

    #-----------------------------------------------------------------
    # Fill the bin number, cut variable -> cut bin dictionary
    #-----------------------------------------------------------------

    d_binNumber_cutVariable_cutBin = {}
    d_cutVariable_cutBin_binNumber = {}

    for bin_number in bin_numbers: 
        for cut_variable in cut_variables:
            
            cut_value = d_binNumber_cutVariable_cutValue [ bin_number ] [ cut_variable ]
            cut_bin   = d_cutVariable_cutValues[cut_variable].index ( cut_value ) 

            if cut_variable not in d_cutVariable_cutBin_binNumber.keys():
                d_cutVariable_cutBin_binNumber [ cut_variable ] = {}
            
            if bin_number not in d_binNumber_cutVariable_cutBin.keys():
                d_binNumber_cutVariable_cutBin [ bin_number ] = {}
                
            if cut_variable not in d_binNumber_cutVariable_cutBin [ bin_number ].keys():
                d_binNumber_cutVariable_cutBin [ bin_number ][ cut_variable ] = cut_bin 
            else :
                print "ERROR: This should never happen!" 
                sys.exit()

            if cut_bin not in d_cutVariable_cutBin_binNumber [ cut_variable ].keys():
                d_cutVariable_cutBin_binNumber [ cut_variable ][ cut_bin ] = bin_number

    return


def parse_root_file( d_input,verbose=False ) :
    d_binNumber_nSample = {}
    d_binNumber_nSampleErr = {}
    d_binNumber_nEnts = {}

    sum_hist = TH1F()
    sum_ents_hist = TH1F()
    for sample in d_input.keys():
        
        sample_name = d_input[sample][0]
        sample_file = TFile ( d_input[sample][1] ) 
        sample_scale = float ( d_input[sample][2] ) 
        hist_name = "histo1D__" + sample_name + "__optimizer"
        hist_ents_name = "histo1D__" + sample_name + "__optimizerEntries"
        
        hist = sample_file.Get(hist_name)
        print 'getting hist',hist_name,'from:',sample_file.GetName(),
        sys.stdout.flush()
        if not hist:
          print 'ERROR: could not find hist',hist_name,'in file',sample_file.GetName()
          print 'Quitting.'
          exit(-1)
        print 'entries:',hist.GetEntries()
        hist.Scale ( sample_scale ) 
        #print 'bin0:',hist.GetBinContent(0)
        #print 'bin1:',hist.GetBinContent(1)

        histEnts = sample_file.Get(hist_ents_name)
        print 'getting hist',hist_ents_name,'from:',sample_file.GetName(),
        sys.stdout.flush()
        if not histEnts:
          print 'ERROR: could not find hist',hist_ents_name,'in file',sample_file.GetName()
          print 'Quitting.'
          exit(-1)
        print 'entries:',histEnts.GetEntries()
        print 'entries bin 5836:',histEnts.GetBinContent(5836)

        if sum_hist.GetEntries()<=0:
            sum_hist = copy.deepcopy ( hist ) 
        else:
            sum_hist.Add ( hist )
        if not 'data' in hist.GetName().lower():
          if sum_ents_hist.GetEntries()<=0:
              sum_ents_hist = copy.deepcopy ( histEnts )
          else:
              sum_ents_hist.Add ( histEnts )
          if verbose:
            print 'adding',histEnts.GetName(),'with',histEnts.GetEntries(),'to totalEnts hist'
            print 'totalEnts hist now has',sum_ents_hist.GetEntries(),'entries'
            print 'totalEnts hist now has',sum_ents_hist.GetBinContent(5836),'entries in bin 5836'
        
        sample_file.Close() 
        
    nbins = sum_hist.GetNbinsX() 
    #print 'sum_hist bin 0:',sum_hist.GetBinContent(0)
    #print 'sum_hist bin 1:',sum_hist.GetBinContent(1)
    
    for ibin in range (0, nbins ) :
        d_binNumber_nSample [ ibin ] = sum_hist.GetBinContent ( ibin+1 )
        d_binNumber_nSampleErr [ ibin ] = sum_hist.GetBinError ( ibin+1 )
        d_binNumber_nEnts   [ ibin ] = sum_ents_hist.GetBinContent ( ibin+1 )
        #if ibin==5836:
        #    print 'sum_ents_hist has',sum_ents_hist.GetBinContent(5836),'entries in bin',ibin
    
    return d_binNumber_nSample,d_binNumber_nSampleErr,d_binNumber_nEnts


def calculateEfficiency(nS, signal_sample, d_signal_totalEvents):
  # optimizer nS is weighted the usual way, so unweight it before calculating the efficiency
  weight = (intLumi * d_signal_crossSections[signal_sample]) / d_signal_totalEvents[signal_sample]
  return 1.0*(nS/weight)/d_signal_totalEvents[signal_sample]
    
def evaluation ( nS, nB, efficiency ) :
  try:
    # s/sqrt(s+b)
    #value = nS / ( math.sqrt ( nS + nB ) )
    # switch to asymptotic formula
    if not usePunzi:
      value = math.sqrt(2*((nS+nB)*math.log(1+nS/nB)-nS))
    else:
      # punzi
      nSigmas = 5
      value = efficiency/(nSigmas/2.0+math.sqrt(nB))
  except ZeroDivisionError:
    value = -999
  except ValueError:
    print 'WARNING: had a domain error calculating the value with nS=',nS,'and nB=',nB
    value = -999
  return value

def evaluate ( bin_number, d_signal, d_background, signal_sample, d_signal_totalEvents) :
    nS = d_signal     [ bin_number ] 
    nB = d_background [ bin_number ] 
    ## For amc@NLO.
    #if nS < 0:
    #  nS = 0
    if nB < 0:
      nB = 0
    efficiency = calculateEfficiency(nS, signal_sample,d_signal_totalEvents)
    #print 'efficiency is:',nS,'/',d_signal_totalEvents[signal_sample],'=',1.0*nS/d_signal_totalEvents[signal_sample]
    v  = evaluation ( nS, nB, efficiency ) 
    #print 'value=',v
    return v 

def string_to_bins ( cut_string ) :
    bins = []
    cut_values = []

    string_fields = cut_string.split() 
    
    for cut_variable in cut_variables:
        if cut_variable not in string_fields:
            print "ERROR: I identified " + cut_variable + " as a cut variable, based on " + txt_file_path
            print "       But I can't find " + cut_variable + " in this string: " + cut_string
            sys.exit()
        cut_variable_index_in_string = string_fields.index ( cut_variable ) 
        cut_value = float ( string_fields [ cut_variable_index_in_string + 2 ] ) 
        cut_bin = d_cutVariable_cutValues[cut_variable].index ( cut_value ) 
        bins.append ( cut_bin ) 
    return bins

def bins_to_string ( cut_bins ) : 
    
    cut_string = ""

    if len ( cut_bins ) != len ( cut_variables ):
        print "ERROR: You are asking for the cut string for", len ( cut_bins ), " cut bins, but there are", len (cut_variables ), " cut variables "
        sys.exit()

    for i,cut_variable in enumerate(cut_variables):
        cut_bin = cut_bins [i]
        cut_value_int = int ( d_cutVariable_cutValues [ cut_variable ][cut_bin] )
        cut_value_float = float ( d_cutVariable_cutValues [ cut_variable ][cut_bin] )
        if cut_value_int==cut_value_float:
          cut_value = cut_value_int
        else:
          cut_value = cut_value_float
        cut_requirement = cut_requirements [i]
        cut_string = cut_string + cut_variable + " " + cut_requirement + " " + str( cut_value ) + "\t"
        
    cut_string = cut_string.strip()

    return cut_string
    

####################################################################################################
# Configurables
####################################################################################################
intLumi=35867.0 # in pb
# these have rescaling applied
#mc_filepath         = os.environ["LQDATA"] + "/2016opt/eejj_crab_psk_apr11_ele27OrEle115/analysisClass_lq_eejj_plots.root"
#mc_filepath         = os.environ["LQDATA"] + "/2016opt/enujj_crab_psk_apr6_topPtWeight_recoHeepSF_reminiAOD_sele27wptightEta2p1CurveMC/analysisClass_lq_enujj_MT_plots.root"
#mc_filepath         = os.environ["LQDATA"] + "/2016opt/eejj_crab_psk_may23_ele27OrEle115/analysisClass_lq_eejj_plots.root"
#mc_filepath         = os.environ["LQDATA"] + "/2016opt/eejj_crab_psk_may30_properEle27OrEle115OrPhoton175/analysisClass_lq_eejj_plots.root"
#mc_filepath         = os.environ["LQDATA"] + "/2016opt/eejj_psk_oct4_ptEECut/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
mc_filepath         = os.environ["LQDATA"] + "/2016opt/eejj_psk_nov27_fixTrigEff_finalSels_muonVetoDef20GeV_nEleGte2/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
#mc_filepath_enujj   = os.environ["LQDATA"] + "/2016opt/enujj_psk_jun1_reminiAOD_ele27wptightOREle115ORPhoton175/output_cutTable_lq_enujj_MT_opt/analysisClass_lq_enujj_MT_plots.root"
#mc_filepath_enujj   = os.environ["LQDATA"] + "/2016opt/enujj_psk_oct6/output_cutTable_lq_enujj_MT_opt/analysisClass_lq_enujj_MT_plots.root"
mc_filepath_enujj   = os.environ["LQDATA"] + "/2016opt/enujj_psk_jan19/output_cutTable_lq_enujj_MT_opt/analysisClass_lq_enujj_MT_plots.root"

#k_jun1_reminiAOD_ele27wptightOREle115ORPhoton175/output_cutTable_lq_enujj_MT_opt/analysisClass_lq_enujj_MT_plots.rootejj_crab_psk_may30_properEle27OrEle115OrPhoton175/analysisClass_lq_eejj_plots.rootqcd_data_filepath = os.environ["LQDATA"] + "/2016opt/qcd_eejj_apr13_ele27wptightOrEle115/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_QCD_plots.root"
#qcd_data_filepath = os.environ["LQDATA"] + "/2016opt/qcd_enujj_apr11/output_cutTable_lq_enujj_MT_QCD_opt/analysisClass_lq_enujj_QCD_plots.root"
#qcd_data_filepath = os.environ["LQDATA"] + "/2016opt/eejjQCD_psk_crab_may22/analysisClass_lq_eejj_QCD_plots.root"
#qcd_data_filepath = os.environ["LQDATA"] + "/2016opt/qcd_eejj_may29_ele27wptightOrEle115OrPhoton175/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_QCD_plots.root"
#qcd_data_filepath = os.environ["LQDATA"] + "/2016opt/eejj_QCD_psk_oct4_ptEECut/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_QCD_plots.root"
qcd_data_filepath = os.environ["LQDATA"] + "/2016opt/eejj_QCD_psk_nov27_finalSels_muonVeto35GeV_nEleGte2/output_cutTable_lq_eejj_QCD_opt/analysisClass_lq_eejj_QCD_plots.root"
#qcd_data_filepath_enujj = os.environ["LQDATA"] + "/2016opt/qcd_enujj_psk_jun1_ele27wptightOREle115ORPhoton175/output_cutTable_lq_enujj_MT_QCD_opt/analysisClass_lq_enujj_QCD_plots.root"
qcd_data_filepath_enujj = os.environ["LQDATA"] + "/2016opt/enujj_QCD_jan19/output_cutTable_lq_enujj_MT_QCD_opt/analysisClass_lq_enujj_QCD_plots.root"

# for eejj
#ttbar_data_filepath = os.environ["LQDATA"] + "/2016opt/eejjTTBar_crab_psk_apr11_ele27OrEle115/analysisClass_lq_ttbarEst_plots.root"
#ttbar_data_filepath = os.environ["LQDATA"] + "/2016opt/may22_ttbarBkg_emujj/output_cutTable_lq_ttbar_emujj_correctTrig_opt/analysisClass_lq_ttbarEst_plots.root"
#ttbar_data_filepath = os.environ["LQDATA"] + "/2016opt/may30_ttbarBkg_emujj/output_cutTable_lq_ttbar_emujj_correctTrig_opt/analysisClass_lq_ttbarEst_plots.root"
#ttbar_data_filepath = os.environ["LQDATA"] + "/2016opt/oct2_emujj_ptEE_eejjOptFinalSels/output_cutTable_lq_ttbar_emujj_correctTrig_opt/analysisClass_lq_ttbarEst_plots.root"
ttbar_data_filepath = os.environ["LQDATA"] + "/2016opt/nov19_emujj_ttbar/output_cutTable_lq_ttbar_emujj_correctTrig_opt/analysisClass_lq_ttbarEst_plots.root"
#
#txt_file_path        = os.environ["LQANA"] + "/versionsOfAnalysis_eejj/apr11_ele27OrEle115/optimization/optimizationCuts.txt"
#txt_file_path        = os.environ["LQANA"] + "/versionsOfAnalysis_eejj/may23/opt/optimizationCuts.txt"
#txt_file_path        = os.environ["LQANA"] + "/versionsOfAnalysis_enujj/apr11_testOpt/optimizationCuts.txt"
txt_file_path_eejj   = os.environ["LQANA"] + "/versionsOfAnalysis_eejj/2017/may30/opt/optimizationCuts.txt"
#txt_file_path_enujj  = os.environ["LQANA"] + "/versionsOfAnalysis_enujj/jun2/opt/optimizationCuts.txt"
txt_file_path_enujj  = os.environ["LQANA"] + "/versionsOfAnalysis_enujj/jan17/opt_jan19/optimizationCuts.txt"
#
doEEJJ = True
# if false, uses asymptotic significance formula
usePunzi = True

jitter = 2

d_eejj_background_filepaths = { 
     "ttbar" : [ "TTBarFromDATA" , ttbar_data_filepath, 1.0 ],
    "qcd"   : [ "QCDFakes_DATA"  , qcd_data_filepath  , 1.0  ],
    #"ttbar" : [ "TTbar_Madgraph"      , mc_filepath  , 1.0  ],
    #"qcd"   : [ "QCD_EMEnriched"      , mc_filepath  , 1.0  ],
    "wjet"  : [ "WJet_amcatnlo_ptBinned"    , mc_filepath  , 1.0  ],
    "zjet"  : [ "ZJet_amcatnlo_ptBinned"    , mc_filepath  , 1.0  ],
    "stop"  : [ "SingleTop"           , mc_filepath  , 1.0  ],
    "vv"    : [ "DIBOSON_amcatnlo"    , mc_filepath  , 1.0  ],
    "gjet"  : [ "PhotonJets_Madgraph" , mc_filepath  , 1.0  ] 
}

d_enujj_background_filepaths = { 
    #"ttbar" : [ "TTbar_amcatnlo_Inc"  , mc_filepath_enujj, 1.0 ],
    "ttbar" : [ "TTbar_powheg"  , mc_filepath_enujj, 1.0 ],
    "qcd"   : [ "QCDFakes_DATA"  , qcd_data_filepath_enujj  , 1.0  ],
    #"ttbar" : [ "TTbar_Madgraph"      , mc_filepath_enujj  , 1.0  ],
    #"qcd"   : [ "QCD_EMEnriched"      , mc_filepath_enujj  , 1.0  ],
    "wjet"  : [ "WJet_amcatnlo_ptBinned"    , mc_filepath_enujj  , 1.0  ],
    "zjet"  : [ "ZJet_amcatnlo_ptBinned"    , mc_filepath_enujj  , 1.0  ],
    "stop"  : [ "SingleTop"           , mc_filepath_enujj  , 1.0  ],
    "vv"    : [ "DIBOSON_amcatnlo"    , mc_filepath_enujj  , 1.0  ],
    "gjet"  : [ "PhotonJets_Madgraph" , mc_filepath_enujj  , 1.0  ] 
}

d_eejj_signal_filepaths_list = [ 
    { "200" : ["LQ_M200", mc_filepath, 1.0 ] } ,
    { "250" : ["LQ_M250", mc_filepath, 1.0 ] } ,
    { "300" : ["LQ_M300", mc_filepath, 1.0 ] } ,
    { "350" : ["LQ_M350", mc_filepath, 1.0 ] } ,
    { "400" : ["LQ_M400", mc_filepath, 1.0 ] } ,
    { "450" : ["LQ_M450", mc_filepath, 1.0 ] } ,
    { "500" : ["LQ_M500", mc_filepath, 1.0 ] } ,
    { "550" : ["LQ_M550", mc_filepath, 1.0 ] } ,
    { "600" : ["LQ_M600", mc_filepath, 1.0 ] } ,
    { "650" : ["LQ_M650", mc_filepath, 1.0 ] } ,
    { "700" : ["LQ_M700", mc_filepath, 1.0 ] } ,
    { "750" : ["LQ_M750", mc_filepath, 1.0 ] } ,
    { "800" : ["LQ_M800", mc_filepath, 1.0 ] } ,
    { "850" : ["LQ_M850", mc_filepath, 1.0 ] } ,  
    { "900" : ["LQ_M900", mc_filepath, 1.0 ] } , 
    { "950" : ["LQ_M950", mc_filepath, 1.0 ] } , 
    { "1000" : ["LQ_M1000", mc_filepath, 1.0 ] } , 
    { "1050" : ["LQ_M1050", mc_filepath, 1.0 ] } , 
    { "1100" : ["LQ_M1100", mc_filepath, 1.0 ] } , 
    { "1150" : ["LQ_M1150", mc_filepath, 1.0 ] } , 
    { "1200" : ["LQ_M1200", mc_filepath, 1.0 ] } , 
    { "1250" : ["LQ_M1250", mc_filepath, 1.0 ] } , 
    { "1300" : ["LQ_M1300", mc_filepath, 1.0 ] } , 
    { "1350" : ["LQ_M1350", mc_filepath, 1.0 ] } , 
    { "1400" : ["LQ_M1400", mc_filepath, 1.0 ] } , 
    { "1450" : ["LQ_M1450", mc_filepath, 1.0 ] } , 
    { "1500" : ["LQ_M1500", mc_filepath, 1.0 ] } , 
    { "1550" : ["LQ_M1550", mc_filepath, 1.0 ] } , 
    { "1600" : ["LQ_M1600", mc_filepath, 1.0 ] } , 
    { "1650" : ["LQ_M1650", mc_filepath, 1.0 ] } , 
    { "1700" : ["LQ_M1700", mc_filepath, 1.0 ] } , 
    { "1750" : ["LQ_M1750", mc_filepath, 1.0 ] } , 
    { "1800" : ["LQ_M1800", mc_filepath, 1.0 ] } , 
    { "1850" : ["LQ_M1850", mc_filepath, 1.0 ] } , 
    { "1900" : ["LQ_M1900", mc_filepath, 1.0 ] } , 
    { "1950" : ["LQ_M1950", mc_filepath, 1.0 ] } , 
    { "2000" : ["LQ_M2000", mc_filepath, 1.0 ] } , 
]
d_enujj_signal_filepaths_list = [ 
    { "200" : ["LQ_M200", mc_filepath_enujj, 1.0 ] } ,
    { "250" : ["LQ_M250", mc_filepath_enujj, 1.0 ] } ,
    { "300" : ["LQ_M300", mc_filepath_enujj, 1.0 ] } ,
    { "350" : ["LQ_M350", mc_filepath_enujj, 1.0 ] } ,
    { "400" : ["LQ_M400", mc_filepath_enujj, 1.0 ] } ,
    { "450" : ["LQ_M450", mc_filepath_enujj, 1.0 ] } ,
    { "500" : ["LQ_M500", mc_filepath_enujj, 1.0 ] } ,
    { "550" : ["LQ_M550", mc_filepath_enujj, 1.0 ] } ,
    { "600" : ["LQ_M600", mc_filepath_enujj, 1.0 ] } ,
    { "650" : ["LQ_M650", mc_filepath_enujj, 1.0 ] } ,
    { "700" : ["LQ_M700", mc_filepath_enujj, 1.0 ] } ,
    { "750" : ["LQ_M750", mc_filepath_enujj, 1.0 ] } ,
    { "800" : ["LQ_M800", mc_filepath_enujj, 1.0 ] } ,
    { "850" : ["LQ_M850", mc_filepath_enujj, 1.0 ] } ,  
    { "900" : ["LQ_M900", mc_filepath_enujj, 1.0 ] } , 
    { "950" : ["LQ_M950", mc_filepath_enujj, 1.0 ] } , 
    { "1000" : ["LQ_M1000", mc_filepath_enujj, 1.0 ] } , 
    { "1050" : ["LQ_M1050", mc_filepath_enujj, 1.0 ] } , 
    { "1100" : ["LQ_M1100", mc_filepath_enujj, 1.0 ] } , 
    { "1150" : ["LQ_M1150", mc_filepath_enujj, 1.0 ] } , 
    { "1200" : ["LQ_M1200", mc_filepath_enujj, 1.0 ] } , 
    { "1250" : ["LQ_M1250", mc_filepath_enujj, 1.0 ] } , 
    { "1300" : ["LQ_M1300", mc_filepath_enujj, 1.0 ] } , 
    { "1350" : ["LQ_M1350", mc_filepath_enujj, 1.0 ] } , 
    { "1400" : ["LQ_M1400", mc_filepath_enujj, 1.0 ] } , 
    { "1450" : ["LQ_M1450", mc_filepath_enujj, 1.0 ] } , 
    { "1500" : ["LQ_M1500", mc_filepath_enujj, 1.0 ] } , 
    { "1550" : ["LQ_M1550", mc_filepath_enujj, 1.0 ] } , 
    { "1600" : ["LQ_M1600", mc_filepath_enujj, 1.0 ] } , 
    { "1650" : ["LQ_M1650", mc_filepath_enujj, 1.0 ] } , 
    { "1700" : ["LQ_M1700", mc_filepath_enujj, 1.0 ] } , 
    { "1750" : ["LQ_M1750", mc_filepath_enujj, 1.0 ] } , 
    { "1800" : ["LQ_M1800", mc_filepath_enujj, 1.0 ] } , 
    { "1850" : ["LQ_M1850", mc_filepath_enujj, 1.0 ] } , 
    { "1900" : ["LQ_M1900", mc_filepath_enujj, 1.0 ] } , 
    { "1950" : ["LQ_M1950", mc_filepath_enujj, 1.0 ] } , 
    { "2000" : ["LQ_M2000", mc_filepath_enujj, 1.0 ] } , 
]

#XXX FIXME: add hist to the analysis to count total events
d_eejj_signal_totalEvents = {
    "LQ_M200" : 50000,
    "LQ_M250" : 50000,
    "LQ_M300" : 50000,
    "LQ_M350" : 50000,
    "LQ_M400" : 50000,
    "LQ_M450" : 49721,
    "LQ_M500" : 50000,
    "LQ_M550" : 50000,
    "LQ_M600" : 50000,
    "LQ_M650" : 49815,
    "LQ_M700" : 50000,
    "LQ_M750" : 50000,
    "LQ_M800" : 50000,
    "LQ_M850" : 49242,
    "LQ_M900" : 50000,
    "LQ_M950" : 49834,
    "LQ_M1000" : 49716,
    "LQ_M1050" : 49782,
    "LQ_M1100" : 50000,
    "LQ_M1150" : 49909,
    "LQ_M1200" : 50000,
    "LQ_M1250" : 49841,
    "LQ_M1300" : 50000,
    "LQ_M1350" : 49808,
    "LQ_M1400" : 49835,
    "LQ_M1450" : 50000,
    "LQ_M1500" : 50000,
    "LQ_M1550" : 50000,
    "LQ_M1600" : 50000,
    "LQ_M1650" : 50000,
    "LQ_M1700" : 50000,
    "LQ_M1750" : 49416,
    "LQ_M1800" : 50000,
    "LQ_M1850" : 50000,
    "LQ_M1900" : 49111,
    "LQ_M1950" : 49871,
    "LQ_M2000" : 49881,
}
d_enujj_signal_totalEvents = {
    "LQ_M200" : 49745,
    "LQ_M250" : 49183,
    "LQ_M300" : 49889,
    "LQ_M350" : 50009,
    "LQ_M400" : 49578,
    "LQ_M450" : 50244,
    "LQ_M500" : 49908,
    "LQ_M550" : 49850,
    "LQ_M600" : 49783,
    "LQ_M650" : 50059,
    "LQ_M700" : 49876,
    "LQ_M750" : 49865,
    "LQ_M800" : 50059,
    "LQ_M850" : 50003,
    "LQ_M900" : 50099,
    "LQ_M950" : 49556,
    "LQ_M1000" : 49524,
    "LQ_M1050" : 50222,
    "LQ_M1100" : 49579,
    "LQ_M1150" : 49369,
    "LQ_M1200" : 50229,
    "LQ_M1250" : 50017,
    "LQ_M1300" : 49807,
    "LQ_M1350" : 49806,
    "LQ_M1400" : 49315,
    "LQ_M1450" : 48988,
    "LQ_M1500" : 49730,
    "LQ_M1550" : 48783,
    "LQ_M1600" : 49900,
    "LQ_M1650" : 49891,
    "LQ_M1700" : 48730,
    "LQ_M1750" : 49619,
    "LQ_M1800" : 49694,
    "LQ_M1850" : 48965,
    "LQ_M1900" : 50003,
    "LQ_M1950" : 49843,
    "LQ_M2000" : 49284,
}
#FIXME: Take this by parsing the cross section file...
d_eejj_signal_crossSections = {
    "LQ_M200" : 6.06E+01,
    "LQ_M250" : 2.03E+01,
    "LQ_M300" : 8.04E+00,
    "LQ_M350" : 3.59E+00,
    "LQ_M400" : 1.74E+00,
    "LQ_M450" : 9.06E-01,
    "LQ_M500" : 4.96E-01,
    "LQ_M550" : 2.84E-01,
    "LQ_M600" : 1.69E-01,
    "LQ_M650" : 1.03E-01,
    "LQ_M700" : 6.48E-02,
    "LQ_M750" : 4.16E-02,
    "LQ_M800" : 2.73E-02,
    "LQ_M850" : 1.82E-02,
    "LQ_M900" : 1.23E-02,
    "LQ_M950" : 8.45E-03,
    "LQ_M1000" : 5.86E-03,
    "LQ_M1050" : 4.11E-03,
    "LQ_M1100" : 2.91E-03,
    "LQ_M1150" : 2.08E-03,
    "LQ_M1200" : 1.50E-03,
    "LQ_M1250" : 1.09E-03,
    "LQ_M1300" : 7.95E-04,
    "LQ_M1350" : 5.85E-04,
    "LQ_M1400" : 4.33E-04,
    "LQ_M1450" : 3.21E-04,
    "LQ_M1500" : 2.40E-04,
    "LQ_M1550" : 1.80E-04,
    "LQ_M1600" : 1.35E-04,
    "LQ_M1650" : 1.02E-04,
    "LQ_M1700" : 7.74E-05,
    "LQ_M1750" : 5.88E-05,
    "LQ_M1800" : 4.48E-05,
    "LQ_M1850" : 3.43E-05,
    "LQ_M1900" : 2.62E-05,
    "LQ_M1950" : 2.01E-05,
    "LQ_M2000" : 1.55E-05,
}
d_enujj_signal_crossSections = {
    "LQ_M200" : 30.3,
    "LQ_M250" : 10.15,
    "LQ_M300" : 4.02,
    "LQ_M350" : 1.795,
    "LQ_M400" : 0.87,
    "LQ_M450" : 0.453,
    "LQ_M500" : 0.248,
    "LQ_M550" : 0.142,
    "LQ_M600" : 0.0845,
    "LQ_M650" : 0.0515,
    "LQ_M700" : 0.0324,
    "LQ_M750" : 0.0208,
    "LQ_M800" : 0.01365,
    "LQ_M850" : 0.0091,
    "LQ_M900" : 0.00615,
    "LQ_M950" : 0.004225,
    "LQ_M1000" : 0.00293,
    "LQ_M1050" : 0.002055,
    "LQ_M1100" : 0.001455,
    "LQ_M1150" : 0.00104,
    "LQ_M1200" : 0.00075,
    "LQ_M1250" : 0.000545,
    "LQ_M1300" : 0.0003975,
    "LQ_M1350" : 0.0002925,
    "LQ_M1400" : 0.0002165,
    "LQ_M1450" : 0.0001605,
    "LQ_M1500" : 0.00012,
    "LQ_M1550" : 9e-05,
    "LQ_M1600" : 6.75e-05,
    "LQ_M1650" : 5.1e-05,
    "LQ_M1700" : 3.87e-05,
    "LQ_M1750" : 2.94e-05,
    "LQ_M1800" : 2.24e-05,
    "LQ_M1850" : 1.715e-05,
    "LQ_M1900" : 1.31e-05,
    "LQ_M1950" : 1.005e-05,
    "LQ_M2000" : 7.75e-06,
}

# for eejj
if doEEJJ:
  d_signal_totalEvents = d_eejj_signal_totalEvents
  d_signal_filepaths_list = d_eejj_signal_filepaths_list
  d_signal_crossSections = d_eejj_signal_crossSections
  d_background_filepaths = d_eejj_background_filepaths
  d_data_filepaths =  {"DATA" : [ "DATA", mc_filepath, 1.0 ] }
  txt_file_path = txt_file_path_eejj
else:
  d_signal_totalEvents = d_enujj_signal_totalEvents
  d_signal_filepaths_list = d_enujj_signal_filepaths_list
  d_signal_crossSections = d_enujj_signal_crossSections
  d_background_filepaths = d_enujj_background_filepaths
  d_data_filepaths =  {"DATA" : [ "DATA", mc_filepath_enujj, 1.0 ] }
  txt_file_path = txt_file_path_enujj

cut_variables = []
cut_requirements = []
cut_values = []
bin_numbers = []

d_cutVariable_maxCutValues = {}
    
d_binNumber_cutValuesString      = {}
d_binNumber_cutVariable_cutValue = {}
d_cutVariable_cutValues          = {} 
d_cutValuesString_binNumber      = {}


####################################################################################################
# Run!
####################################################################################################
print 'Parsing txt file',txt_file_path,'...'
sys.stdout.flush()
parse_txt_file ()
print "Parsed."

verbose = False
d_binNumber_nB,d_binNumber_nBErr,d_binNumber_nBMCEnts = parse_root_file( d_background_filepaths,verbose )
#print 'd_binNumber_nBMCEnts[5836]=',d_binNumber_nBMCEnts[5836]
d_binNumber_nD,d_binNumber_nDErr,d_binNumber_nDEnts = parse_root_file( d_data_filepaths )

selectedEfficienciesByLQMass = []
selectedNsByLQMass = []
selectedNbByLQMass = []
lqMasses = []

#print 'Checking for signal histograms'
#for signal_sample in d_signal_filepaths_list: 
#    parse_root_file( signal_sample ) 

for signal_sample in d_signal_filepaths_list: 
    d_binNumber_nS,d_binNumber_nSErr,d_binNumber_nSEnts = parse_root_file( signal_sample ) 
    print "looking at",signal_sample
    # XXX SIC make histo
    #mejHisto = TH1F('mej_hist',',mej_hist',len(bin_numbers),0,len(bin_numbers)+1)

    max_bin = -999
    max_value = -999
    max_nS = -999
    max_nB = -999
    max_nD = -999
    max_string = ""
    max_eff = -1.0

    for binNumber in bin_numbers:
        nS = d_binNumber_nS [ binNumber ] 
        nSErr = d_binNumber_nSErr [ binNumber ] 
        nB = d_binNumber_nB [ binNumber ] 
        nBErr = d_binNumber_nBErr [ binNumber ] 
        nBMCEnts = d_binNumber_nBMCEnts [ binNumber ] 
        nD = d_binNumber_nD [ binNumber ] 
        #if nS < 0:
        #  nS = 0
        #if nB < 0:
        #  nB = 0
        ##XXX ignore any set of cuts with nB<0.01
        #if nB < 0.01:
        #  continue
        ##XXX ignore any cuts with less than 5 background events
        #if nBMCEnts < 5:
        #  continue
        ##XXX ignore any set of cuts with nB < 0
        if nB < 0:
          continue
        ## ignore any set of cuts if the nBErr/nB > 50%
        #if nBErr/nB > 0.5:
        #  continue
        if verbose:
          print 'binNumber=',binNumber,
          print 'evaluated to: nS=',nS,'nB=',nB,';',
        value = evaluate ( binNumber, d_binNumber_nS, d_binNumber_nB, signal_sample.values()[0][0],d_signal_totalEvents )
        if verbose:
          #print 'final evaluation: nS=',nS,'nB=',nB,'value=',value,
          print 'value=',value,
          print 'eff=',calculateEfficiency(nS, signal_sample.values()[0][0],d_signal_totalEvents)
          print d_binNumber_cutValuesString [ binNumber ]
        #mejHisto.SetBinContent(binNumber,value)
        
        if value > max_value : 
            max_value = value
            max_bin = binNumber
            max_nS = nS
            max_nB = nB
            max_nD = nD
            max_string = d_binNumber_cutValuesString [ max_bin ]
            max_eff = calculateEfficiency(nS, signal_sample.values()[0][0],d_signal_totalEvents)
            if verbose:
              print '---> NEW MAX FOUND: bin=',max_bin,'cut info=',max_string,'max value=',max_value,'eff=',max_eff
              print '     evaluated to: nS=',nS,'nB=',nB,'nBMCEnts=',nBMCEnts
              print '     d_binNumber_nBMCEnts [ max_bin ] =',d_binNumber_nBMCEnts [ max_bin ] 
            
    print signal_sample.keys()[0], ": Bin with best value was bin #" + str ( max_bin ), "\tCut info was:\t" +  max_string , "\t v = %.2f" % max_value, " nS = %.2f" % max_nS, ", nB = %.2f" % max_nB#, ", nD = %d" % max_nD
    signalSampleName = signal_sample.values()[0][0]
    signalSampleMass = int(signalSampleName[signalSampleName.find('_M')+2:])
    print 'LQ mass:',signalSampleMass,'had efficiency at maxOptPoint:',max_eff
    selectedEfficienciesByLQMass.append(max_eff)
    selectedNsByLQMass.append(max_nS)
    selectedNbByLQMass.append(max_nB)
    lqMasses.append(signalSampleMass)

    max_bins = string_to_bins ( max_string ) 
    test_max_string = bins_to_string ( max_bins ) 
    print 'max_bins=',max_bins,'test_max_string=',test_max_string
    test_binNumber = d_cutValuesString_binNumber [ test_max_string ]

    if test_max_string != max_string:
        print "ERROR: Something is wrong with how you map strings to bins (string test)"
        sys.exit()

    if test_binNumber != max_bin : 
        print "ERROR: Something is wrong with how you map strings to bins (bin test)"
        sys.exit()
        
    for i,cut_variable in enumerate(cut_variables):

        if cut_variable not in d_cutVariable_maxCutValues.keys():
            d_cutVariable_maxCutValues[ cut_variable ] = []

        this_bin = max_bins[i]

        this_cut_value = d_cutVariable_cutValues[ cut_variable][this_bin]

        n_bins = len ( d_cutVariable_cutValues [ cut_variable ] ) 

        lower_jitter_bin = max ( 0     , this_bin - jitter ) 
        upper_jitter_bin = min ( n_bins - 1, this_bin + jitter ) 
        
        new_max_bins_lower_jitter = max_bins[:i] + [ lower_jitter_bin ] + max_bins[i+1:]
        new_max_bins_upper_jitter = max_bins[:i] + [ upper_jitter_bin ] + max_bins[i+1:]
        
        new_max_string_lower_jitter = bins_to_string ( new_max_bins_lower_jitter )
        new_max_string_upper_jitter = bins_to_string ( new_max_bins_upper_jitter )

        new_max_binNumber_lower_jitter = d_cutValuesString_binNumber[ new_max_string_lower_jitter ] 
        new_max_binNumber_upper_jitter = d_cutValuesString_binNumber[ new_max_string_upper_jitter ] 
        
        new_value_lower_jitter = evaluate ( new_max_binNumber_lower_jitter, d_binNumber_nS, d_binNumber_nB, signal_sample.values()[0][0], d_signal_totalEvents)
        new_value_upper_jitter = evaluate ( new_max_binNumber_upper_jitter, d_binNumber_nS, d_binNumber_nB, signal_sample.values()[0][0], d_signal_totalEvents)

        lower_jitter_percent_change = 100. * ( new_value_lower_jitter - max_value ) / max_value
        upper_jitter_percent_change = 100. * ( new_value_upper_jitter - max_value ) / max_value

        to_print = ""
        to_print = to_print + "\t" + "Jitter " + cut_variable + "\t" + "["
        to_print = to_print + str(int ( d_cutVariable_cutValues [cut_variable][lower_jitter_bin])) + ", " 
        to_print = to_print + str(int ( d_cutVariable_cutValues [cut_variable][upper_jitter_bin])) + " ]"
        to_print = to_print + "\t" + "value % change:" + " ["
        to_print = to_print + "%.2f" % lower_jitter_percent_change 
        to_print = to_print + ", " 
        to_print = to_print + "%.2f" % upper_jitter_percent_change 
        to_print = to_print + "]" 

        print to_print
        print
        
        d_cutVariable_maxCutValues[ cut_variable].append ( this_cut_value ) 


print "\n\n"

x_array = []
d_cutVariable_yArray = {}

#to_print = "LQ mass \t"
#for signal_sample in d_signal_filepaths_list:
#    to_print = to_print + signal_sample.keys()[0] + "\t"
#print to_print
#print "-------------------------------------------------------------------------------------------"
#
#for cut_variable in cut_variables:
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

columnNames = ["LQ mass"]
columnNames.extend([signal_sample.keys()[0] for signal_sample in d_signal_filepaths_list])
table = PrettyTable(columnNames)
table.float_format = "4.3"
for cut_variable in cut_variables:
    d_cutVariable_yArray [cut_variable ] = []
    #to_print = cut_variable + "\t"
    row = [cut_variable]
    for i, signal_sample in enumerate(d_signal_filepaths_list):
        lq_mass = int ( signal_sample.keys()[0] )
        cut_value = int (d_cutVariable_maxCutValues[cut_variable][i])
        #to_print = to_print + str(cut_value ) + "\t"
        row.append(str(cut_value))

        if ( lq_mass not in x_array ) : x_array.append ( float ( lq_mass ) )
        d_cutVariable_yArray [cut_variable ].append ( float ( cut_value )  )
    table.add_row(row)

print table

print "\n\n"

# get max fit range
maxFitMass = 0.0
for i,mass in enumerate(lqMasses):
  nB = selectedNbByLQMass[i]
  if nB > 1:
    maxFitMass = mass
  else:
    break
print 'maxFitMass=',maxFitMass
    
func2 = TF1("func2", "pol2(0)", 150., maxFitMass )
func1 = TF1("func1", "pol1(0)", 150., maxFitMass )

fit_functions = [ "func1", "func2" ]

optimizationRootFile = TFile('optimization.root','recreate')
optimizationRootFile.cd()
#MEJ HIST
#mejHisto.Write()

canvas = TCanvas()
canvas.cd()
graph = TGraph(len(lqMasses),numpy.array(lqMasses).astype('float'),numpy.array(selectedEfficienciesByLQMass))
graph.Draw("AP")
graph.GetXaxis().SetTitle("LQ mass [GeV]")
graph.GetYaxis().SetTitle('eff*acc')
graph.GetXaxis().SetRangeUser(0, 2000)
maximum = graph.GetHistogram().GetMaximum()
graph.GetHistogram().SetMaximum( maximum * 1.5 ) 
graph.Draw("AP")
graph.SetName('efficiencyTimesAcceptance')
graph.Write()

canvas = TCanvas()
canvas.cd()
graph = TGraph(len(lqMasses),numpy.array(lqMasses).astype('float'),numpy.array(selectedNsByLQMass))
graph.Draw("AP")
graph.GetXaxis().SetTitle("LQ mass [GeV]")
graph.GetYaxis().SetTitle('nS')
graph.GetXaxis().SetRangeUser(0, 2000)
maximum = graph.GetHistogram().GetMaximum()
graph.GetHistogram().SetMaximum( maximum * 1.5 ) 
graph.Draw("AP")
graph.SetName('nS')
graph.Write()

canvas = TCanvas()
canvas.cd()
graph = TGraph(len(lqMasses),numpy.array(lqMasses).astype('float'),numpy.array(selectedNbByLQMass))
graph.Draw("AP")
graph.GetXaxis().SetTitle("LQ mass [GeV]")
graph.GetYaxis().SetTitle('nB')
graph.GetXaxis().SetRangeUser(0, 2000)
maximum = graph.GetHistogram().GetMaximum()
graph.GetHistogram().SetMaximum( maximum * 1.5 ) 
graph.Draw("AP")
graph.SetName('nB')
graph.Write()

for cut_variable in cut_variables:
    for fit_function in fit_functions:

        canvas = TCanvas()
        canvas.cd()
    
        graph = TGraph( len ( x_array ), numpy.array ( x_array ), numpy.array ( d_cutVariable_yArray[cut_variable ] ) )
        graph.SetName('graph_'+cut_variable+'_'+fit_function)
        canvas.SetName('canvas_'+cut_variable+'_'+fit_function)

        
        graph.Draw("AP")
        
        graph.GetXaxis().SetTitle("LQ mass [GeV]")
        graph.GetYaxis().SetTitle(cut_variable)
        graph.GetXaxis().SetRangeUser(0, 2000)

        maximum = graph.GetHistogram().GetMaximum()
        graph.GetHistogram().SetMaximum ( maximum * 1.5 ) 
        
        graph.Fit ( fit_function, 'R' )
        
        graph.Draw("AP")
        
        canvas.SaveAs(cut_variable + "_" + fit_function + ".png" )
        canvas.SaveAs(cut_variable + "_" + fit_function + ".C" )
        canvas.Write()
        graph.Write()
        # stored with TGraph
        #function = graph.GetFunction(fit_function)
        #function.SetName('fitFunc_'+cut_variable)
        #function.Write()

optimizationRootFile.Close()

