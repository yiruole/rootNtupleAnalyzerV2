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


#---Read .dat table
def ParseDatFile(datFilename):
  data=OrderedDict()
  colNames = OrderedDict()
  lineCounter = int(0)

  #print '(opening:',inputDataFile,
  sys.stdout.flush()
  with open(datFilename) as datFile:
    for j,line in enumerate(datFile):
        # ignore comments
        if( re.search("^###", line) ):
            continue
        line = string.strip(line,"\n")
        #print "---> lineCounter: " , lineCounter
        #print line
        split = line.split()
        if len(split)==1:
            # new sample
            sampleName=split[0]
            data[sampleName] = OrderedDict()
            justFoundNewSample = True
        else:
            if justFoundNewSample:
                colNames[sampleName] = OrderedDict()
                for i,piece in enumerate(split):
                    colNames[sampleName][i] = piece
                    data[sampleName][ colNames[sampleName][i] ] = piece
                justFoundNewSample = False

            for i,piece in enumerate(split):
                varName = ''
                if i==0:
                    varName = piece
                else:
                    data[sampleName][varName] = piece
                #print data[row][ column[i] ] 

  return data


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
        else:
            if 'variableName' in line:
                if len(colNames) < 1:
                    colNamesFromLine = line.split()
                    colNames = ['sample']+colNamesFromLine
                continue
            else:
                #print 'line looks line:"'+line+'" with length=',len(line)
                lineToAdd = [sample]+line.split()
                #modLines.append(tuple(sample+'\t'+line))
                modLines.append(tuple(x for x in lineToAdd))

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
df = df.set_index('sample')
# print
output = StringIO()
df.head(10).to_csv(output)
output.seek(0)
pt = prettytable.from_csv(output)
print pt

