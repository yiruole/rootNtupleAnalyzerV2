#!/usr/bin/env python

import datFileUtils
import os
import sys
import re
import string
import pandas as pd
from StringIO import StringIO
import prettytable


####################################################################################################
# Config/Run
####################################################################################################
#datFilePath = os.environ["LQDATA"] + '/2016analysis/eejj_psk_feb20_newSingTop/output_cutTable_lq_eejj/analysisClass_lq_eejj_tables.dat'
#datFilePath = os.environ["LQDATA"] + '/2016analysis/enujj_psk_mar5_removeTopPtReweight/output_cutTable_lq_enujj_MT/analysisClass_lq_enujj_MT_tables.dat'
#datFilePath = os.environ["LQDATA"] + '/2016analysis/eejj_RSK_mar5_forCutFlow/output_cutTable_lq_eejj/analysisClass_lq_eejj_tables.dat'
datFilePath = os.environ["LQDATA"] + '/2016ttbar/mar1_emujj_RedoRTrig/output_cutTable_lq_ttbar_emujj_correctTrig/analysisClass_lq_ttbarEst_tables.dat'
#datFilePath = os.environ["LQDATA"] + '/2016analysis/enujj_RSK_mar5_forCutFlow/output_cutTable_lq_enujj_MT/analysisClass_lq_enujj_MT_tables.dat'

#print 'Parsing dat file:',datFilePath,'...',
#sys.stdout.flush()
#data = ParseDatFile(datFilePath)
#print 'Done'
#print data.keys()[0]
#print data[data.keys()[0]]
toRound = 2

# transform dat file format
# Here we can unscale the sample if we want
#weight = 2.0874594 # eejj
#weight = 1.05259252909 # enujj
#sampleToUse = 'LQ_M1100'
#
#weight = 5767.4136 # eejj
#weight = 2890.12287278 # enujj
#sampleToUse = 'LQ_M300'
#
#weight = 121.23046 # eejj
#weight = 60.867220292 # enujj
#sampleToUse = 'LQ_M600'
#
#weight = 4.22762531177 # eejj
#weight = 2.11986747085 # enujj
#sampleToUse = 'LQ_M1000'
#
# backgrounds
#sampleToUse = 'WJet_amcatnlo_ptBinned'
#sampleToUse = 'TTbar_powheg'
sampleToUse = 'TTBarFromDATA'
#sampleToUse = 'ZJet_amcatnlo_ptBinned'
toRound=4
weight = -1
#
# slightly nasty since we apply the weight for one sample to the whole table; round to 2 decimal places
modLines,colNames = datFileUtils.ReadDatFile(datFilePath,weight,rounding=toRound)

#print modLines[0:9]
#df = pd.read_csv(datFilePath,delim_whitespace=True,header=1)
df = pd.DataFrame.from_records(modLines, columns=colNames)

pd.set_option('display.max_columns', None)
#pd.set_option('display.large_repr', 'truncate')
#pd.set_option('display.max_columns', 0)
#pd.set_option('display.expand_frame_repr', False)
#print(df.head())
#df.describe()
#df.head(50)
#print df.describe().to_string()

#print (df.head(100).to_string())
#with pd.option_context('display.max_rows', None, 'display.max_columns', 10):
#    print(df.head(100))

df.drop(['min1','min2','max1','max2'],axis=1,inplace=True)
#df = df.set_index('sample')

sampleList = df['sample'].unique()
#sampleToUse = sampleList[0]
print '#'*100
print 'Cutflow for',sampleToUse
print '#'*100
dfPrint = df.loc[df['sample']==sampleToUse]
dfPrint = dfPrint.drop(['sample','errEffRel','errEffAbs'],axis=1)
#dfPrint = dfPrint.head(10)



# print
output = StringIO()
dfPrint.to_csv(output,index=False)
output.seek(0)
pt = prettytable.from_csv(output)
print pt

print
print '#'*100
print 'latex table'
print '#'*100
print

print dfPrint.to_latex(index=False)
print
