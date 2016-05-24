import os, copy, math, sys, numpy
from ROOT import *

mc_filepath         = os.environ["LQDATA"] + "/RunII/eejj_analysis_opt_16may2016/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_plots.root"
qcd_data_filepath = os.environ["LQDATA"] + "/RunII/eejj_analysis_opt_16may2016/output_cutTable_lq_eejj_opt/analysisClass_lq_eejj_QCD_plots.root"
#
txt_file_path        = os.environ["LQANA"] + "/versionsOfAnalysis_eejj/20may_veryFineOptimization/optimizationCuts.txt"

jitter = 2

d_background_filepaths = { 
    # "ttbar" : [ "DATA"        , ttbar_data_filepath, 0.49 ],
    "qcd"   : [ "QCDFakes_DATA"  , qcd_data_filepath  , 1.0  ],
    "ttbar" : [ "TTbar_Madgraph"      , mc_filepath  , 1.0  ],
    #"qcd"   : [ "QCD_EMEnriched"      , mc_filepath  , 1.0  ],
    #"qcd"   : [ "QCDFakes_DATA"      , mc_filepath  , 1.0  ],
    "wjet"  : [ "WJet_Madgraph_HT"    , mc_filepath  , 1.0  ],
    "zjet"  : [ "ZJet_Madgraph_HT"    , mc_filepath  , 1.0  ],
    "stop"  : [ "SingleTop"           , mc_filepath  , 1.0  ],
    "vv"    : [ "DIBOSON"             , mc_filepath  , 1.0  ],
    "gjet"  : [ "PhotonJets_Madgraph" , mc_filepath  , 1.0  ] 
    }

d_signal_filepaths_list = [ 
    #{ "250" : ["LQ_M250", mc_filepath, 1.0 ] } ,
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

#XXX FIXME: add hist to the analysis to count total events
d_signal_totalEvents = {
    "LQ_M300" : 50000,
    "LQ_M350" : 50000,
    "LQ_M400" : 50000,
    "LQ_M450" : 47352,
    "LQ_M500" : 50000,
    "LQ_M550" : 50000,
    "LQ_M600" : 49715,
    "LQ_M650" : 50000,
    "LQ_M700" : 50000,
    "LQ_M750" : 50000,
    "LQ_M800" : 50000,
    "LQ_M850" : 49240,
    "LQ_M900" : 50000,
    "LQ_M950" : 50000,
    "LQ_M1000" : 49761,
    "LQ_M1050" : 50000,
    "LQ_M1100" : 48948,
    "LQ_M1150" : 49660,
    "LQ_M1200" : 48104,
    "LQ_M1250" : 50000,
    "LQ_M1300" : 49816,
    "LQ_M1350" : 49721,
    "LQ_M1400" : 50000,
    "LQ_M1450" : 50000,
    "LQ_M1500" : 49480,
    "LQ_M1550" : 50000,
    "LQ_M1600" : 50000,
    "LQ_M1650" : 50000,
    "LQ_M1700" : 50000,
    "LQ_M1750" : 50000,
    "LQ_M1800" : 49522,
    "LQ_M1850" : 48164,
    "LQ_M1900" : 48650,
    "LQ_M1950" : 50000,
    "LQ_M2000" : 48288,
}
#FIXME: Take this by parsing the cross section file...
d_signal_crossSections = {
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
intLumi=2570.0 # in pb

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
        #hist_name = "histo1D__" + sample_name + "__optimizer"
        
        hist = sample_file.Get(hist_name)
        print 'getting hist',hist_name,'from:',sample_file.GetName(),
        print 'entries:',hist.GetEntries()
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
    
def calculateEfficiency(nS, signal_sample):
  # optimizer nS is weighted the usual way, so unweight it before calculating the efficiency
  weight = (intLumi * d_signal_crossSections[signal_sample]) / d_signal_totalEvents[signal_sample]
  return 1.0*(nS/weight)/d_signal_totalEvents[signal_sample]
    
def evaluation ( nS, nB, efficiency ) :
  try:
    #value = nS / ( math.sqrt ( nS + nB ) )
    # switch to asymptotic formula
    #value = math.sqrt(2*((nS+nB)*math.log(1+nS/nB)-nS))
    # punzi
    nSigmas = 5
    value = efficiency/(nSigmas/2.0+math.sqrt(nB))
  except ZeroDivisionError:
    value = -999
  except ValueError:
    print 'WARNING: had a domain error calculating the value with nS=',nS,'and nB=',nB
    value = -999
  return value

def evaluate ( bin_number, d_signal, d_background, signal_sample) :
    nS = d_signal     [ bin_number ] 
    nB = d_background [ bin_number ] 
    efficiency = calculateEfficiency(nS, signal_sample)
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
# Run!
####################################################################################################
print 'Parsing txt file',txt_file_path,'...',
parse_txt_file ()
print "Parsed."

d_binNumber_nB = parse_root_file( d_background_filepaths )
d_binNumber_nD = parse_root_file( d_data_filepaths )

selectedEfficienciesByLQMass = []
lqMasses = []

verbose = False
for signal_sample in d_signal_filepaths_list: 
    d_binNumber_nS = parse_root_file( signal_sample ) 
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
        nB = d_binNumber_nB [ binNumber ] 
        nD = d_binNumber_nD [ binNumber ] 
        value = evaluate ( binNumber, d_binNumber_nS, d_binNumber_nB, signal_sample.values()[0][0] )
        if verbose:
          print 'binNumber=',binNumber,
          print 'evaluated to: nS=',nS,'nB=',nB,'value=',value
        #mejHisto.SetBinContent(binNumber,value)
        
        if value > max_value : 
            max_value = value
            max_bin = binNumber
            max_nS = nS
            max_nB = nB
            max_nD = nD
            max_string = d_binNumber_cutValuesString [ max_bin ]
            max_eff = calculateEfficiency(nS, signal_sample.values()[0][0])
            if verbose:
              print '---> NEW MAX FOUND: bin=',max_bin,'cut info=',max_string,'max value=',max_value
            
    print signal_sample.keys()[0], ": Bin with best value was bin #" + str ( max_bin ), "\tCut info was:\t" +  max_string , "\t v = %.2f" % max_value, " nS = %.2f" % max_nS, ", nB = %.2f" % max_nB, ", nD = %d" % max_nD
    signalSampleName = signal_sample.values()[0][0]
    signalSampleMass = int(signalSampleName[signalSampleName.find('_M')+2:])
    print 'LQ mass:',signalSampleMass,'had efficiency at maxOptPoint:',max_eff
    selectedEfficienciesByLQMass.append(max_eff)
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
        
        new_value_lower_jitter = evaluate ( new_max_binNumber_lower_jitter, d_binNumber_nS, d_binNumber_nB, signal_sample.values()[0][0])
        new_value_upper_jitter = evaluate ( new_max_binNumber_upper_jitter, d_binNumber_nS, d_binNumber_nB, signal_sample.values()[0][0])

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

func2 = TF1("func2", "pol2(0)", 250., 1500. )
func1 = TF1("func1", "pol1(0)", 250., 1500. )

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
        
        canvas.SaveAs(cut_variable + "_" + fit_function + ".gif" )
        canvas.SaveAs(cut_variable + "_" + fit_function + ".C" )
        canvas.Write()
        graph.Write()
        # stored with TGraph
        #function = graph.GetFunction(fit_function)
        #function.SetName('fitFunc_'+cut_variable)
        #function.Write()

optimizationRootFile.Close()

