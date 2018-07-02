#!/usr/bin/env python

import datFileUtils
import os
import sys
#import re
import string
import math
import pandas as pd
import ROOT as r
import numpy as np
#from StringIO import StringIO
#import prettytable

def format_for_print(df):    
    table = prettytable.PrettyTable([''] + list(df.columns))
    for row in df.itertuples():
        table.add_row(row)
    return str(table)


####################################################################################################
# Config/Run
####################################################################################################
#datFilePath1 = os.environ["LQDATA"] + '/2016analysis/enujj_psk_mar5_removeTopPtReweight/output_cutTable_lq_enujj_MT/analysisClass_lq_enujj_MT_tables.dat'
#datFilePath2 = os.environ["LQDATA"] + '/2016analysis/enujj_psk_feb27_dPhiEleMet0p8_fixMETPlot/output_cutTable_lq_enujj_MT/analysisClass_lq_enujj_MT_tables.dat'
#datFilePath1 = '/afs/cern.ch/work/s/scooper/private/data/Leptoquarks/2016analysis/eejj_RSK_mar5_forCutFlow/output_cutTable_lq_eejj/analysisClass_lq_eejj_tables.dat'
#datFilePath2 = datFilePath1
#datFilePath1 = '/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/2016ttbar/mar1_emujj_RedoRTrig/output_cutTable_lq_ttbar_emujj_correctTrig/analysisClass_lq_ttbarEst_tables.dat'
#datFilePath2 = '/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/2016ttbar/mar20_emujj_extraSFForSyst/output_cutTable_lq_ttbar_emujj_correctTrig/analysisClass_lq_ttbarEst_tables.dat'

datFilePath1 = '/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/2016analysis/eejj_psk_mar20_fixPlots/output_cutTable_lq_eejj/analysisClass_lq_eejj_tables.dat'
datFilePath2 = '/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/2016analysis/eejj_psk_mar26_muonVetoSyst/output_cutTable_lq_eejj/analysisClass_lq_eejj_tables.dat'

#datFilePath1 = '/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/2016analysis/enujj_psk_mar20_addPlots/output_cutTable_lq_enujj_MT/analysisClass_lq_enujj_MT_tables.dat'
#datFilePath2 = '/afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/2016analysis/enujj_psk_mar26_muonVetoUncert/output_cutTable_lq_enujj_MT/analysisClass_lq_enujj_MT_tables.dat'

doEEJJ = True

# transform dat file format
modLines,colNames = datFileUtils.ReadDatFile(datFilePath1,stopAtPreselection=False)
#print modLines[0:9]
#df = pd.read_csv(datFilePath,delim_whitespace=True,header=1)
df1 = pd.DataFrame.from_records(modLines, columns=colNames)
df1.drop(['min1','min2','max1','max2'],axis=1,inplace=True)

#sampleToUse = 'TTbar_powheg'
#sampleToUse = 'LQ_M200'
#sampleToUse = 'TTBarFromDATA'
#sampleToUse = 'ZJet_amcatnlo_ptBinned'
#sampleToUse = 'SingleTop'
#sampleToUse = 'DIBOSON_amcatnlo'
#sampleToUse = 'WJet_amcatnlo_ptBinned'
sampleToUse = 'ALLBKG_powhegTTBar_ZJetWJetPt_amcAtNLODiboson'
#sampleForPlotLabel = 'DYJets'
sampleForPlotLabel = 'AllMCBackground'
#print '#'*100
#print 'Cutflow for',sampleToUse
#print '#'*100
df1 = df1.loc[df1['sample']==sampleToUse]
print df1.head(10)
#dfPrint = dfPrint.head(10)

# transform dat file format
modLines,colNames = datFileUtils.ReadDatFile(datFilePath2,stopAtPreselection=False)
#print modLines[0:9]
#df = pd.read_csv(datFilePath,delim_whitespace=True,header=1)
df2 = pd.DataFrame.from_records(modLines, columns=colNames)
df2.drop(['min1','min2','max1','max2'],axis=1,inplace=True)
# reset sample to use if needed
sampleToUseDF2 = sampleToUse
#sampleToUseDF2 = 'Stop_M200_CTau1'
df2Print = df2.loc[df2['sample']==sampleToUseDF2]
print df2Print.head(10)

if sampleToUseDF2==sampleToUse:
  df1Print = df1.drop(['sample'],axis=1)
  df2Print = df2Print.drop(['sample','variableName'],axis=1)
  result = pd.concat([df1Print, df2Print], axis=1)
else:
  df1Print = df1
  result = pd.merge(df1Print, df2Print, right_on='variableName', left_on='variableName',left_index=True)
  result.drop(['Npass_x','errNpass_x','Npass_y','errNpass_y'],axis=1,inplace=True)

# delta based on NPass
result['delta'] = (df1Print['Npass']-df2Print['Npass'])/df1Print['Npass']
#result['errDelta'] = result['delta']*( (df2Print['errNpass']**2+df1Print['errNpass']**2)/(df1Print['Npass']-df2Print['Npass'])**2 + (df2Print['errNpass']/df2Print['Npass'])**2 )**0.5
result['errDelta'] = ( df1Print['errNpass']**2*(df2Print['Npass']/(df1Print['Npass'])**2)**2 + (1/df1Print['Npass'])**2*(df2Print['errNpass'])**2)**0.5
result.drop(['EffRel','errEffRel','EffAbs','errEffAbs'],axis=1,inplace=True)

## delta based on effRel
#if sampleToUse == sampleToUseDF2:
#  result['deltaEffRel'] = (df1Print['EffRel']-df2Print['EffRel'])/df2Print['EffRel']
#  result['errDelta'] = result['deltaEffRel']*( (df2Print['errEffRel']**2+df1Print['errEffRel']**2)/(df1Print['EffRel']-df2Print['EffRel'])**2 + (df2Print['errEffRel']/df2Print['EffRel'])**2 )**0.5
#else:
#  result['deltaEffRel'] = result['EffRel_x']/result['EffRel_y']
#  result['errDelta'] = result['deltaEffRel']*( (df1Print['errEffRel']/df1Print['EffRel']) + (df2Print['errEffRel']/df2Print['EffRel'])**2 )**0.5



# print
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 250)
#output = StringIO()
#result.to_csv(output,index=False)
#output.seek(0)
#pt = prettytable.from_csv(output)
#print pt

#print format_for_print(result)
print result.head(200)

print
print '#'*100
print 'latex table'
print '#'*100
print

print result.to_latex(index=False)
print

# make graph
if doEEJJ:
    idx = result.loc[result['variableName'].str.contains('sT_eejj_LQ200')].index.tolist()[0]
else:
    idx = result.loc[result['variableName'].str.contains('ST_LQ200')].index.tolist()[0]

result = result[result.index > idx]
if doEEJJ:
  result = result.loc[result['variableName'].str.contains('M_ej')]
else:
  result = result.loc[result['variableName'].str.contains('MT')]
mejVals = result['variableName'].map(lambda x: float(str(x).split('_')[-1].replace('LQ','')))

#print result.head(50)

c = r.TCanvas()
c.cd()
graph = r.TGraphErrors(len(result['delta']),np.array(mejVals),np.array(result['delta']),np.array([0]*len(result['delta'])),np.array(result['errDelta']))
graph.Draw('ap')
graph.GetXaxis().SetTitle('LQ mass [GeV]')
graph.GetYaxis().SetTitle('Relative change in '+sampleForPlotLabel+' yield')
graph.SetTitle('')
graph.Draw('ap')
c.Print('relativeDiffGraph.pdf')
c.Print('relativeDiffGraph.png')


