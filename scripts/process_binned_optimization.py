import os, copy, math, sys, numpy
from ROOT import *

mc_filepath         = os.environ["LQDATA"] + "eejj_analysis/eejj_opt/output_cutTable_lq_eejj_Optimization/analysisClass_lq_eejj_Optimization_plots.root"
ttbar_data_filepath = os.environ["LQDATA"] + "eejj_analysis/eejj_qcd_opt/output_cutTable_lq_eejj_Optimization/analysisClass_lq_eejj_QCD_Optimization_plots.root"
qcd_data_filepath   = os.environ["LQDATA"] + "eejj_analysis/eejj-ttbar-opt-test/output_cutTable_lq_eejj_Optimization/analysisClass_lq_eejj_TTBar_Optimization_plots.root"

txt_file_path        = "/afs/cern.ch/user/e/eberry/scratch0/rootNtupleAnalyzer/CMSSW_4_2_3/src/rootNtupleAnalyzerV2/optimizationCuts.txt"

jitter = 2

d_background_filepaths = { 
    # "ttbar" : [ "DATA"        , ttbar_data_filepath, 0.49 ],
    "ttbar" : [ "TTbar_Madgraph", mc_filepath      , 1.0  ],
    "qcd"   : [ "DATA"        , qcd_data_filepath  , 1.0  ],
    "wjet"  : [ "WJet_Sherpa" , mc_filepath        , 1.0  ],
    "zjet"  : [ "ZJet_Sherpa" , mc_filepath        , 1.0  ],
    "stop"  : [ "SingleTop"   , mc_filepath        , 1.0  ],
    "vv"    : [ "DIBOSON"     , mc_filepath        , 1.0  ],
    "gjet"  : [ "PhotonJets"  , mc_filepath        , 1.0  ] 

    }

d_signal_filepaths_list = [ 
    { "250" : ["LQ_M250", mc_filepath, 1.0 ] } ,
    { "350" : ["LQ_M350", mc_filepath, 1.0 ] } ,
    { "400" : ["LQ_M400", mc_filepath, 1.0 ] } ,
    { "450" : ["LQ_M450", mc_filepath, 1.0 ] } ,
    { "500" : ["LQ_M500", mc_filepath, 1.0 ] } ,
    { "550" : ["LQ_M550", mc_filepath, 1.0 ] } ,
    { "600" : ["LQ_M600", mc_filepath, 1.0 ] } ,
    { "650" : ["LQ_M650", mc_filepath, 1.0 ] } ,
    { "750" : ["LQ_M750", mc_filepath, 1.0 ] } ,
    { "850" : ["LQ_M850", mc_filepath, 1.0 ] }  
]

d_data_filepaths =  {"DATA" : [ "DATA", mc_filepath, 1.0 ] }

cut_variables = []
cut_requirements = []
cut_values = []
bin_numbers = []

d_cutVariable_maxCutValues = {}
    
d_binNumber_cutValuesString      = {}
d_binNumber_cutVariable_cutValue = {}
d_cutVariable_cutValues          = {} 
d_cutValuesString_binNumber      = {}

def parse_txt_file ():
    
    txt_file = open ( txt_file_path, "r" ) 

    #-----------------------------------------------------------------
    # Loop over each line in the file, which corresponds to a bin number,
    # and a collection of cuts
    #-----------------------------------------------------------------

    for line in txt_file:

        #-----------------------------------------------------------------
        # First, get the important data from the line
        #-----------------------------------------------------------------

        bin_number = int ( line.split("Bin = ")[1].split()[0].strip() ) 

        cut_string = line.split("Bin = " + str ( bin_number ) )[1].strip()
        cut_info = cut_string.split()
        n_cuts = len ( cut_info ) / 3

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
            
            this_cut_info = cut_info[icut * n_cuts : icut * n_cuts + 3 ]
            
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
                sys.exit()

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

def parse_root_file( d_input ) :
    d_binNumber_nSample = {}

    made_hist = False
    
    sum_hist = TH1F()

    for sample in d_input.keys():
        
        sample_name = d_input[sample][0]
        sample_file = TFile ( d_input[sample][1] ) 
        sample_scale = float ( d_input[sample][2] ) 
        hist_name = "histo1D__" + sample_name + "__Optimizer"
        
        hist = sample_file.Get(hist_name)
        hist.Scale ( sample_scale ) 

        if not made_hist:
            sum_hist = copy.deepcopy ( hist ) 
            made_hist = True
        else:
            sum_hist.Add ( hist ) 
        
        sample_file.Close() 
        
    nbins = sum_hist.GetNbinsX() 
    
    for ibin in range (0, nbins + 1 ) :
        d_binNumber_nSample [ ibin ] = sum_hist.GetBinContent ( ibin )
    
    return d_binNumber_nSample
    
def evaluation ( nS, nB ) :
    value = nS / ( math.sqrt ( nS + nB ) )
    return value

def evaluate ( bin_number, d_signal, d_background ) :
    nS = d_signal     [ bin_number ] 
    nB = d_background [ bin_number ] 
    v  = evaluation ( nS, nB ) 
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
        cut_value = int ( d_cutVariable_cutValues [ cut_variable ][cut_bin] )
        cut_requirement = cut_requirements [i]
        cut_string = cut_string + cut_variable + " " + cut_requirement + " " + str( cut_value ) + "\t"
        
    cut_string = cut_string.strip()

    return cut_string
    

print "Parsing txt file..."
parse_txt_file ()
print "...Parsed txt file"

d_binNumber_nB = parse_root_file( d_background_filepaths )
d_binNumber_nD = parse_root_file( d_data_filepaths )

for signal_sample in d_signal_filepaths_list: 
    d_binNumber_nS = parse_root_file( signal_sample ) 

    max_bin = -999
    max_value = -999
    max_nS = -999
    max_nB = -999
    max_nD = -999
    max_string = ""

    for binNumber in bin_numbers:
        nS = d_binNumber_nS [ binNumber ] 
        nB = d_binNumber_nB [ binNumber ] 
        nD = d_binNumber_nD [ binNumber ] 
        value = evaluate ( binNumber, d_binNumber_nS, d_binNumber_nB )
        
        if value > max_value : 
            max_value = value
            max_bin = binNumber
            max_nS = nS
            max_nB = nB
            max_nD = nD
            max_string = d_binNumber_cutValuesString [ max_bin ]
            
    print signal_sample.keys()[0], ": Bin with best value was bin #" + str ( max_bin ), "\tCut info was:\t" +  max_string , "\t v = %.2f" % max_value, " nS = %.2f" % max_nS, ", nB = %.2f" % max_nB, ", nD = %d" % max_nD

    max_bins = string_to_bins ( max_string ) 
    test_max_string = bins_to_string ( max_bins ) 
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
        
        new_value_lower_jitter = evaluate ( new_max_binNumber_lower_jitter, d_binNumber_nS, d_binNumber_nB )
        new_value_upper_jitter = evaluate ( new_max_binNumber_upper_jitter, d_binNumber_nS, d_binNumber_nB )

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
        
        d_cutVariable_maxCutValues[ cut_variable].append ( this_cut_value ) 


print "\n\n"

x_array = []
d_cutVariable_yArray = {}

to_print = "LQ mass \t"
for signal_sample in d_signal_filepaths_list:
    to_print = to_print + signal_sample.keys()[0] + "\t"
print to_print
print "-------------------------------------------------------------------------------------------"

for cut_variable in cut_variables:
    d_cutVariable_yArray [cut_variable ] = []
    to_print = cut_variable + "\t"
    for i, signal_sample in enumerate(d_signal_filepaths_list):
        lq_mass = int ( signal_sample.keys()[0] )
        cut_value = int (d_cutVariable_maxCutValues[cut_variable][i])
        to_print = to_print + str(cut_value ) + "\t"

        if ( lq_mass not in x_array ) : x_array.append ( float ( lq_mass ) )
        d_cutVariable_yArray [cut_variable ].append ( float ( cut_value )  )

    print to_print


print "\n\n"

    
func2 = TF1("func2", "pol2(0)", 250., 850. )
func1 = TF1("func1", "pol1(0)", 250., 850. )

fit_functions = [ "func1", "func2" ]


for cut_variable in cut_variables:
    for fit_function in fit_functions:

        canvas = TCanvas()
        canvas.cd()
    
        graph = TGraph( len ( x_array ), numpy.array ( x_array ), numpy.array ( d_cutVariable_yArray[cut_variable ] ) )

        
        graph.Draw("AP")
        
        graph.GetXaxis().SetTitle("LQ mass [GeV]")
        graph.GetYaxis().SetTitle(cut_variable)
        graph.GetXaxis().SetRangeUser(0, 1500)

        maximum = graph.GetHistogram().GetMaximum()
        graph.GetHistogram().SetMaximum ( maximum * 1.5 ) 
        
        graph.Fit ( fit_function )
        
        graph.Draw("AP")
        
        canvas.SaveAs(cut_variable + "_" + fit_function + ".gif" )
