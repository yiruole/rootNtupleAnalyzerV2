#!/usr/bin/env python

import combineCommon
import os
import sys
import re
import string
from collections import OrderedDict
import pandas as pd
from StringIO import StringIO
import prettytable


####################################################################################################
# Config/Run
####################################################################################################
#datFilePath = os.environ["LQDATA"] + '/2016analysis/eejj_psk_feb20_newSingTop/output_cutTable_lq_eejj/analysisClass_lq_eejj_tables.dat'
datFilePath = 'test_table.dat'

#print 'Parsing dat file:',datFilePath,'...',
#sys.stdout.flush()
#data = ParseDatFile(datFilePath)
#print 'Done'
#print data.keys()[0]
#print data[data.keys()[0]]

# transform dat file format
modLines = []
colNames = []
with open(datFilePath) as datFile:
    for j,line in enumerate(datFile):
        line = line.strip()
        if len(line.split())==1:
            sample = line.split()[0]
            lastLineForSampleReached = False
        else:
            if 'variableName' in line:
                if len(colNames) < 1:
                    colNamesFromLine = line.split()
                    colNames = ['sample']+colNamesFromLine
                continue
            elif not lastLineForSampleReached:
                splitLine = line.split()
                if 'opt' in splitLine[0]:
                    lastLineForSampleReached = True
                    splitLine[0] = 'preselection'
                #print 'line looks line:"'+line+'" with length=',len(line)
                lineToAdd = [sample]+splitLine
                #modLines.append(tuple(sample+'\t'+line))
                modLines.append(tuple(x for x in lineToAdd))
                # stop reading table for this sample after 'opt' vars

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
sampleToUse = sampleList[0]
print '#'*100
print 'Cutflow for',sampleToUse
print '#'*100
dfPrint = df.loc[df['sample']==sampleToUse]
dfPrint = dfPrint.drop(['sample'],axis=1)
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
