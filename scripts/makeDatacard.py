#!/usr/bin/env python

import os, sys, math
import subprocess as sp
from ROOT import *

#class SignalPoint:
#   def __init__(self, *args, **kwargs):
#       self.mass = kwargs.get('mass',-1)
#       self.beta = kwargs.get('beta','1.0')
#       self.data = kwargs.get('data','1.0')
#       self.

def FillDicts(rootFilename,qcdRootFilename):
    qcdTFile = TFile(qcdRootFilename)
    tfile = TFile(rootFilename)
    tfile.cd()
    for i_signal_name, signal_name in enumerate(signal_names):
        for i_mass_point, mass_point in enumerate(mass_points):
            mejHist = tfile.Get('histo1D__LQ_M'+mass_point+'__Mej_selected_min_LQ'+mass_point)
            entriesHist = tfile.Get('histo1D__LQ_M'+mass_point+'__EventsPassingCuts')
            sigEvtsErr = Double(0.0)
            sigEvts = mejHist.IntegralAndError(1,mejHist.GetNbinsX(),sigEvtsErr)
            totalEntries = entriesHist.GetBinContent(1)
            eventYieldList = []
            eventYieldErrList = []
            totalEntriesList = []
            eventYieldList.append(sigEvts)
            eventYieldErrList.append(sigEvtsErr)
            totalEntriesList.append(totalEntries)
            for i_bkg,bkg_name in enumerate(background_names):
                mejHistName = 'histo1D__'+bkg_name+'__Mej_selected_min_LQ'+mass_point
                entriesHistName = 'histo1D__'+bkg_name+'__EventsPassingCuts'
                if not 'QCD' in bkg_name:
                    tfile.cd()
                    mejHist = tfile.Get(mejHistName)
                    entriesHist = tfile.Get(entriesHistName)
                else:
                    qcdTFile.cd()
                    mejHist = qcdTFile.Get(mejHistName)
                    entriesHist = qcdTFile.Get(entriesHistName)
                if not entriesHist:
                  print 'ERROR: could not get hist named:',entriesHistName
                  exit(-1)
                if not mejHist:
                  print 'ERROR: could not get hist named:',mejHistName
                  exit(-1)
                totalEntries = entriesHist.GetBinContent(1)
                eventsErr = Double(0.0)
                events = mejHist.IntegralAndError(1,mejHist.GetNbinsX(),eventsErr)
                eventYieldList.append(events)
                eventYieldErrList.append(eventsErr)
                totalEntriesList.append(totalEntries)
            signalFullName = signal_name + mass_point
            d_events_bySignalName[signalFullName] = eventYieldList
            d_eventErrs_bySignalName[signalFullName] = eventYieldErrList
            d_totalEvents_bySignalName[signalFullName] = totalEntriesList

    qcdTFile.Close()
    tfile.Close()
                

###################################################################################################
# CONFIGURABLES
###################################################################################################

#signal_names = [ "LQ_BetaHalf_M", "LQ_M" ] 
signal_names = [ "LQ_M" ] 
mass_points = [ "300", "350", "400", "450", "500", "550", "600", "650", "700", "750", "800", "850", "900", "950", "1000", "1050", "1100", "1150", "1200" ]
systematics = [ "jes", "ees", "shape", "norm", "lumi", "eer", "jer", "pu", "ereco", "pdf" ]
#FIXME systematics
background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTbar_Madgraph", "WJet_Madgraph_HT", "ZJet_Madgraph_HT", "DIBOSON","SingleTop"  ]

n_background = len ( background_names  )
n_systematics = len ( systematics ) + n_background + 1
n_channels = 1

d_data = {}
d_events_bySignalName = {}
d_eventErrs_bySignalName = {}
d_totalEvents_bySignalName = {}
d_systematics_enujj = {}
d_systematics_eejj = {}

#FIXME TODO SYSTEMATICS                        

dataMC_filepath   = os.environ["LQDATA"] + "/RunII/eejj_analysis_finalSels_22may2016/output_cutTable_lq_eejj/analysisClass_lq_eejj_plots.root"
qcd_data_filepath = os.environ["LQDATA"] + "/RunII/eejj_analysis_finalSels_22may2016/output_cutTable_lq_eejj/analysisClass_lq_eejj_QCD_plots.root"


###################################################################################################
# RUN
###################################################################################################

FillDicts(dataMC_filepath,qcd_data_filepath)

card_file_path = "tmp_card_file.txt"
card_file = open ( card_file_path, "w" ) 

for i_signal_name, signal_name in enumerate(signal_names):
    for i_mass_point, mass_point in enumerate(mass_points):
        fullSignalName = signal_name + mass_point
        
        txt_file_name = fullSignalName + ".txt\n"

        card_file.write ( txt_file_name + "\n\n" )
        card_file.write ( "imax " + str ( n_channels    ) + "\n" ) 
        card_file.write ( "jmax " + str ( n_background  ) + "\n" ) 
        card_file.write ( "kmax " + str ( n_systematics ) + "\n\n" ) 
        
        card_file.write ( "bin 1\n\n" )

        if "BetaHalf" in signal_name: 
            #FIXME for unblinding
            #total_data = enujj_data["data"][i_mass_point]
            #card_file.write ( "observation " + str ( enujj_data["data"][i_mass_point] ) + "\n\n" )
            card_file.write ( "observation " + str ( -1 ) + "\n\n" )
        else : 
            #FIXME for unblinding
            #total_data = eejj_data["data"][i_mass_point]
            #card_file.write ( "observation " + str ( eejj_data["data"][i_mass_point] ) + "\n\n" )
            card_file.write ( "observation " + str ( -1 ) + "\n\n" )
        
        line = "bin " 
        for i_channel in range (0, n_background + 1) :
            line = line + "1 " 
        card_file.write (line + "\n") 

        line = "process " + signal_name + "_" + mass_point + " "
        for background_name in background_names:
            line = line + background_name + " "
        card_file.write (line + "\n") 

        line = "process 0 "
        for background_name in background_names:
            line = line + "1 "
        card_file.write (line + "\n\n") 

        # rate line
        line = "rate "
        total_bkg = 0.0
        total_signal = d_events_bySignalName[fullSignalName][0] # index zero are the signal events
        line = line + str(total_signal) + " "
        for ibkg,background_name in enumerate(background_names):
            thisBkgEvts = d_events_bySignalName[fullSignalName][ibkg+1]
            line += str(thisBkgEvts) + " "
            total_bkg += float(thisBkgEvts) 
        card_file.write ( line + "\n\n")

        #print signal_name, mass_point, total_signal, total_bkg, total_data
        print signal_name, mass_point, total_signal, total_bkg

        #FIXME systs
        #for systematic in systematics :
        #    
        #    line = systematic + " lnN "
        #    if "BetaHalf" in signal_name: 
        #        line = line + str(1.0 + d_systematics_enujj[systematic]["LQ"][i_mass_point] / 100.) + " "
        #        for background_name in background_names:
        #            line = line + str(1.0 + d_systematics_enujj[systematic][background_name][i_mass_point] / 100.) + " "
        #    else:
        #        line = line + str(1.0 + d_systematics_eejj[systematic]["LQ"][i_mass_point] / 100.) + " "
        #        for background_name in background_names:
        #            line = line + str(1.0 + d_systematics_eejj[systematic][background_name][i_mass_point] / 100.) + " "
        #            
        #    card_file.write ( line + "\n")
        
        card_file.write("\n")

        # background stat error part
        for i_background_name ,background_name in enumerate(background_names):

            #if "BetaHalf" in signal_name: 
            #    n       = float (enujj_n[background_name][i_mass_point]       )
            #    e       = float (enujj_e[background_name][i_mass_point]       )
            #    entries = float (enujj_entries [background_name][i_mass_point])
            #else:
            #    n       = float (eejj_n[background_name][i_mass_point]       )
            #    e       = float (eejj_e[background_name][i_mass_point]       )
            #    entries = float (eejj_entries [background_name][i_mass_point])

            thisBkgEvts = d_events_bySignalName[fullSignalName][i_background_name+1]
            thisBkgEvtsErr = d_eventErrs_bySignalName[fullSignalName][i_background_name+1]
            thisBkgTotalEntries = d_totalEvents_bySignalName[fullSignalName][i_background_name+1]

            if thisBkgEvts != 0.0: 
                lnN_f = 1.0 + 1.0/math.sqrt(thisBkgTotalEntries+1) # Poisson becomes Gaussian, approx by logN with this kappa
                gmN_weight = thisBkgEvts / thisBkgTotalEntries # for small uncertainties, use gamma distribution with alpha=(factor to go to signal region from control/MC)
            else: 
                # FIXME: how to get these weights?
                if background_name == "vv":
                    lnN_f = "blah"
                    gmN_weight = 0.111
                elif background_name == "stop":
                    lnN_f = "blah"
                    gmN_weight = 0.438
                elif background_name == "wjet":
                    lnN_f = "blah"
                    gmN_weight = "1.20"
                elif background_name == "zjet":
                    lnN_f = "blah"
                    gmN_weight = "1.20"
                elif background_name == "ttbar":
                    lnN_f = "blah"
                    gmN_weight = "0.19"
                else:
                    lnN_f = "blah"
                    gmN_weight = "blah"
            
            line_ln = "stat_" + background_name + " lnN -"
            line_gm = "stat_" + background_name + " gmN " + str(int(thisBkgTotalEntries)) + " -"
            for i_tmp in range ( 0, i_background_name ):
                line_ln = line_ln + " -"
                line_gm = line_gm + " -"
            line_ln = line_ln + " " + str(lnN_f)
            line_gm = line_gm + " " + str(gmN_weight)
            for i_tmp in range ( i_background_name, len(background_names) -1 ):
                line_ln = line_ln + " -"
                line_gm = line_gm + " -"

            if thisBkgTotalEntries > 10:
                card_file.write (line_ln + "\n")
            else:
                card_file.write (line_gm + "\n")
            
        # signal stat error part
        # always use lnN error
        thisSigEvts = d_events_bySignalName[fullSignalName][0]
        thisSigEvtsErr = d_eventErrs_bySignalName[fullSignalName][0]
        thisSigTotalEntries = d_totalEvents_bySignalName[fullSignalName][0]
        if thisSigEvts == 0.0: 
          print 'ERROR: signal events for this signal (',fullSignalName,'came out to be zero...stat error not supported. Quitting!'
          exit(-1)
        lnN_f = 1.0 + 1.0/math.sqrt(thisSigTotalEntries+1) # Poisson becomes Gaussian, approx by logN with this kappa
        line_ln = "stat_Signal lnN " + str(lnN_f)
        for i_background_name ,background_name in enumerate(background_names):
            line_ln = line_ln + " -"
        card_file.write (line_ln + "\n")

        # DONE!
        card_file.write("\n\n\n")

print 'datacard written to:',card_file_path
exit(0)
