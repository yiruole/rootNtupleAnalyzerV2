#!/usr/bin/env python

#---Import
import sys
import string
from optparse import OptionParser
import os.path
from ROOT import *
import re


#---Option Parser
#--- TODO: WHY PARSER DOES NOT WORK IN CMSSW ENVIRONMENT? ---#
usage = "usage: %prog [options] \nExample: \n./combineTablesTemplate.py -i /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config/inputListAllCurrent.txt -c analysisClass_genStudies -d /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/data/output -l 100 -x /home/santanas/Data/Leptoquarks/RootNtuples/V00-00-06_2008121_163513/xsection_pb_default.txt -o /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/data/output -s /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config/sampleListForMerging.txt"

parser = OptionParser(usage=usage)

parser.add_option("-i", "--inputList", dest="inputList",
                  help="list of all datasets to be used (full path required)",
                  metavar="LIST")

parser.add_option("-c", "--code", dest="analysisCode",
                  help="name of the CODE.C code used to generate the rootfiles (which is the beginning of the root file names before ___)",
                  metavar="CODE")

parser.add_option("-d", "--inputDir", dest="inputDir",
                  help="the directory INDIR contains the rootfiles with the histograms to be combined (full path required)",
                  metavar="INDIR")

parser.add_option("-l", "--intLumi", dest="intLumi",
                  help="results are rescaled to the integrated luminosity INTLUMI (in pb-1)",
                  metavar="INTLUMI")

parser.add_option("-x", "--xsection", dest="xsection",
                  help="the file XSEC contains the cross sections (in pb) for all the datasets (full path required). Use -1 as cross section value for no-rescaling",
                  metavar="XSEC")

parser.add_option("-o", "--outputDir", dest="outputDir",
                  help="the directory OUTDIR contains the output of the program (full path required)",
                  metavar="OUTDIR")

parser.add_option("-s", "--sampleListForMerging", dest="sampleListForMerging",
                  help="put in the file SAMPLELIST the name of the sample with the associated strings which should  match with the dataset name (full path required)",
                  metavar="SAMPLELIST")

(options, args) = parser.parse_args()

if len(sys.argv)<14:
    print usage
    sys.exit()

#print options.analysisCode


#---Check if sampleListForMerging file exist
if(os.path.isfile(options.sampleListForMerging) == False):
    print "ERROR: file " + options.sampleListForMerging + " not found"
    print "exiting..."
    sys.exit()

#--- Declare efficiency tables
dictSamples = {}

for l,line in enumerate( open( options.sampleListForMerging ) ):
    line = string.strip(line,"\n")
    print line
    
    for i,piece in enumerate(line.split()):
        print "i=", i , "  piece= " , piece
        if (i == 0):
            key = piece
            dictSamples[key] = []
        else:
            dictSamples[key].append(piece)
 
dictFinalTables = {}

#--- Functions

#def AddHisto(inputHistoName, outputHisto, inputRootFileName, currentWeight,
#             rebin=int(1), currentColor=int(1), currentFillStyle=int(1001), currentMarker=int(1)):

def UpdateTable(inputTable, outputTable):
    if not outputTable:
        for j,line in enumerate( inputTable ):
            outputTable[int(j)]={'variableName': inputTable[j]['variableName'],
                                 'min1': inputTable[j]['min1'],
                                 'max1': inputTable[j]['max1'],
                                 'min2': inputTable[j]['min2'],
                                 'max2': inputTable[j]['max2'],
                                 'N':       float(inputTable[j]['N']),
                                 'errN':    pow( float(inputTable[j]['errN']), 2 ),
                                 'Npass':       float(inputTable[j]['Npass']),
                                 'errNpass':    pow( float(inputTable[j]['errNpass']), 2 ),
                                 'EffRel':      float(0),
                                 'errEffRel':   float(0),
                                 'EffAbs':      float(0),
                                 'errEffAbs':   float(0),
                                 }
    else:
        for j,line in enumerate( inputTable ):
            outputTable[int(j)]={'variableName': inputTable[j]['variableName'],
                                 'min1': inputTable[j]['min1'],
                                 'max1': inputTable[j]['max1'],
                                 'min2': inputTable[j]['min2'],
                                 'max2': inputTable[j]['max2'],
                                 'N':       float(outputTable[int(j)]['N']) + float(inputTable[j]['N']),
                                 'errN':    float(outputTable[int(j)]['errN']) + pow( float(inputTable[j]['errN']), 2 ),
                                 'Npass':       float(outputTable[int(j)]['Npass']) + float(inputTable[j]['Npass']),
                                 'errNpass':    float(outputTable[int(j)]['errNpass']) + pow( float(inputTable[j]['errNpass']), 2 ),
                                 'EffRel':      float(0),
                                 'errEffRel':   float(0),
                                 'EffAbs':      float(0),
                                 'errEffAbs':   float(0),
                                 }
    return
            

def CalculateEfficiency(table):
    for j,line in enumerate( table ):
        if( j == 0):
            table[int(j)] = {'variableName':       table[int(j)]['variableName'],
                             'min1':        table[int(j)]['min1'],
                             'max1':        table[int(j)]['max1'],
                             'min2':        table[int(j)]['min2'],
                             'max2':        table[int(j)]['max2'],
                             'N':          float(table[j]['N']) ,
                             'errN':       int(0), 
                             'Npass':      float(table[j]['Npass']) ,
                             'errNpass':   int(0), 
                             'EffRel':     int(1),
                             'errEffRel':  int(0),
                             'EffAbs':     int(1),
                             'errEffAbs':  int(0),
                             }
        else:
            N = float(table[j]['N']) 
            errN = sqrt(float(table[j]["errN"]))
            if( float(N) > 0 ):
                errRelN = errN / N 
            else:
                errRelN = float(0)

            Npass = float(table[j]['Npass']) 
            errNpass = sqrt(float(table[j]["errNpass"]))
            if( float(Npass) > 0 ):
                errRelNpass = errNpass / Npass
            else:
                errRelNpass = float(0)

            if(Npass > 0  and N >0 ):
                EffRel = Npass / N
                errRelEffRel = sqrt( errRelNpass*errRelNpass + errRelN*errRelN )
                errEffRel = errRelEffRel * EffRel
            
                EffAbs = Npass / float(table[0]['N'])
                errEffAbs = errNpass / float(table[0]['N'])
            else:
                EffRel = 0
                errEffRel = 0
                EffAbs = 0
                errEffAbs = 0 
            
            table[int(j)]={'variableName': table[int(j)]['variableName'],
                           'min1': table[int(j)]['min1'],
                           'max1': table[int(j)]['max1'],
                           'min2': table[int(j)]['min2'],
                           'max2': table[int(j)]['max2'],
                           'N':       N,
                           'errN':    errN, 
                           'Npass':       Npass,
                           'errNpass':    errNpass, 
                           'EffRel':      EffRel,
                           'errEffRel':   errEffRel,
                           'EffAbs':      EffAbs,
                           'errEffAbs':   errEffAbs,
                           }
            #print table[j]
    return


#--- TODO: FIX TABLE FORMAT (NUMBER OF DECIMAL PLATES AFTER THE 0)

def WriteTable(table, name, file):
    print >>file, name
    print >>file, "variableName".rjust(25),
    print >>file, "min1".rjust(15),
    print >>file, "max1".rjust(15),
    print >>file, "min2".rjust(15),
    print >>file, "max2".rjust(15),
    print >>file, "Npass".rjust(17),
    print >>file, "errNpass".rjust(17),
    print >>file, "EffRel".rjust(15),
    print >>file, "errEffRel".rjust(15),
    print >>file, "EffAbs".rjust(15),
    print >>file, "errEffAbs".rjust(15)

    for j, line in enumerate(table):
        print >>file, table[j]['variableName'].rjust(25),
        print >>file, table[j]['min1'].rjust(15),
        print >>file, table[j]['max1'].rjust(15),
        print >>file, table[j]['min2'].rjust(15),
        print >>file, table[j]['max2'].rjust(15),
        ###
        if( table[j]['Npass'] >= 0.1 ):
            print >>file, ("%.04f" % table[j]['Npass']).rjust(17),
        else:
            print >>file, ("%.04e" % table[j]['Npass']).rjust(17),
        ### 
        if( table[j]['errNpass'] >= 0.1):    
            print >>file, ("%.04f" % table[j]['errNpass']).rjust(17),
        else:
            print >>file, ("%.04e" % table[j]['errNpass']).rjust(17),
        ### 
        if( table[j]['EffRel'] >= 0.1 ):
            print >>file, ("%.04f" % table[j]['EffRel']).rjust(15),
        else:
            print >>file, ("%.04e" % table[j]['EffRel']).rjust(15),
        ### 
        if( table[j]['errEffRel'] >= 0.1 ):
            print >>file, ("%.04f" % table[j]['errEffRel']).rjust(15),    
        else:
            print >>file, ("%.04e" % table[j]['errEffRel']).rjust(15),
        ### 
        if( table[j]['EffAbs'] >= 0.1 ):
            print >>file, ("%.04f" % table[j]['EffAbs']).rjust(15),
        else:
            print >>file, ("%.04e" % table[j]['EffAbs']).rjust(15),
        ### 
        if( table[j]['errEffAbs'] >= 0.1 ):
            print >>file, ("%.04f" % table[j]['errEffAbs']).rjust(15)
        else:
            print >>file, ("%.04e" % table[j]['errEffAbs']).rjust(15)         
        ###
            
    print >>file, "\n"

    #--- print to screen
    
    print "\n"
    print name
    print "variableName".rjust(25),
    print "min1".rjust(15),
    print "max1".rjust(15),
    print "min2".rjust(15),
    print "max2".rjust(15),
    print "Npass".rjust(17),
    print "errNpass".rjust(17),
    print "EffRel".rjust(15),
    print "errEffRel".rjust(15),
    print "EffAbs".rjust(15),
    print "errEffAbs".rjust(15)

    for j, line in enumerate(table):
        print table[j]['variableName'].rjust(25),
        print table[j]['min1'].rjust(15),
        print table[j]['max1'].rjust(15),
        print table[j]['min2'].rjust(15),
        print table[j]['max2'].rjust(15),
        ###
        if( table[j]['Npass'] >= 0.1 ):
            print ("%.04f" % table[j]['Npass']).rjust(17),
        else:
            print ("%.04e" % table[j]['Npass']).rjust(17),
        ### 
        if( table[j]['errNpass'] >= 0.1):    
            print ("%.04f" % table[j]['errNpass']).rjust(17),
        else:
            print ("%.04e" % table[j]['errNpass']).rjust(17),
        ### 
        if( table[j]['EffRel'] >= 0.1 ):
            print ("%.04f" % table[j]['EffRel']).rjust(15),
        else:
            print ("%.04e" % table[j]['EffRel']).rjust(15),
        ### 
        if( table[j]['errEffRel'] >= 0.1 ):
            print ("%.04f" % table[j]['errEffRel']).rjust(15),    
        else:
            print ("%.04e" % table[j]['errEffRel']).rjust(15),
        ### 
        if( table[j]['EffAbs'] >= 0.1 ):
            print ("%.04f" % table[j]['EffAbs']).rjust(15),
        else:
            print ("%.04e" % table[j]['EffAbs']).rjust(15),
        ### 
        if( table[j]['errEffAbs'] >= 0.1 ):
            print ("%.04f" % table[j]['errEffAbs']).rjust(15)
        else:
            print ("%.04e" % table[j]['errEffAbs']).rjust(15)         
        ###

    return

#---Loop over datasets
print "\n"
for n, lin in enumerate( open( options.inputList ) ):

    lin = string.strip(lin,"\n")
    #print lin
    
    dataset_mod = string.split( string.split(lin, "/" )[-1], ".")[0]
    print dataset_mod + " ... "

    inputRootFile = options.inputDir + "/" + options.analysisCode + "___" + dataset_mod + ".root"
    inputDataFile = options.inputDir + "/" + options.analysisCode + "___" + dataset_mod + ".dat"

    #print inputRootFile
    #print inputDataFile

    #---Check if .root and .dat file exist
    if(os.path.isfile(inputRootFile) == False):
        print "ERROR: file " + inputRootFile + " not found in " + options.inputDir
        print "exiting..."
        sys.exit()

    if(os.path.isfile(inputDataFile) == False):
        print "ERROR: file " + inputDataFile + " not found in " + options.inputDir
        print "exiting..."
        sys.exit()

    #---Find xsection correspondent to the current dataset
    if(os.path.isfile(options.xsection) == False):
        print "ERROR: file " + options.xsection + " not found"
        print "exiting..."
        sys.exit()

    for lin1 in open( options.xsection ):

        lin1 = string.strip(lin1,"\n")

        (dataset , xsection_val) = string.split(lin1)
        print dataset + " " + xsection_val

        dataset_mod_1 = dataset[1:].replace('/','__')
        #print dataset_mod_1 + " " + xsection_val

        if(dataset_mod_1 == dataset_mod):
            xsectionIsFound = True
            break

    if(xsectionIsFound == False):
        print "ERROR: xsection for dataset" + dataset + " not found in " + options.xsection
        print "exiting..."
        sys.exit()
        
    #this is the current cross section
    #print xsection_val

    #---Read .dat table for current dataset
    data={}
    column=[]
    lineCounter = int(0)

    for j,line in enumerate( open( inputDataFile ) ):

        if( re.search("^###", line) ):
            continue

        line = string.strip(line,"\n")
        #print "---> lineCounter: " , lineCounter
        print line

        if lineCounter == 0:
            for i,piece in enumerate(line.split()):
                column.append(piece)
        else:
            for i,piece in enumerate(line.split()):
                if i == 0:
                    data[int(piece)] = {}
                    row = int(piece)
                else:
                    data[row][ column[i] ] = piece
                    #print data[row][ column[i] ] 

        lineCounter = lineCounter+1

    # example
    #Ntot = int(data[0]['N'])
    #print Ntot

    #---Calculate weight
    #Ntot = int(data[0]['N'])
    Ntot = float(data[0]['N'])
    if( xsection_val == "-1" ):
        weight = 1.0
        xsection_X_intLumi = Ntot
    else:
        xsection_X_intLumi = float(xsection_val) * float(options.intLumi)
        if( Ntot == 0 ):
            weight = float(0)
        else:
            weight = xsection_X_intLumi / Ntot 
    print "weight: " + str(weight)
    
    #---Create new table using weight
    newtable={}
    
    for j,line in enumerate( data ):
        if(j == 0):
            newtable[int(j)]={'variableName': data[j]['variableName'],
                              'min1': "-",
                              'max1': "-",
                              'min2': "-",
                              'max2': "-",
                              'N': ( Ntot * weight ),
                              'errN': int(0),
                              'Npass': ( Ntot * weight ),
                              'errNpass': int(0),
                              }

        else:
            N = ( float(data[j]['N']) * weight )
            errN = ( float(data[j-1]["errEffAbs"]) * xsection_X_intLumi )
            print data[j]['variableName']
            print "errN: " , errN
            if(str(errN) == "nan"):
                errN = 0
                
                #            if( float(N) > 0 and float(errN) > 0 ):
                #                errRelN = errN / N 
                #            else:
                #                errRelN = float(0)
            
            Npass = ( float(data[j]['Npass']) * weight) 
            errNpass = ( float(data[j]["errEffAbs"]) * xsection_X_intLumi )
            print "errNPass " , errNpass
            print ""
            if(str(errNpass) == "nan"):
                errNpass = 0

                #            if( float(Npass) > 0 and float(errNpass) > 0 ):
                #                errRelNpass = errNpass / Npass
                #            else:
                #                errRelNpass = float(0)
            
            newtable[int(j)]={'variableName': data[j]['variableName'],
                              'min1': data[j]['min1'],
                              'max1': data[j]['max1'],
                              'min2': data[j]['min2'],
                              'max2': data[j]['max2'],
                              'N':         N,
                              'errN':      errN,
                              'Npass':     Npass,
                              'errNpass':  errNpass,
                              }

            #print newtable


    #---Combine tables from different datasets
    
    # loop over samples
    for S,sample in enumerate( dictSamples ):
        #print "current sample is : " , sample

        if( n == 0): 
            dictFinalTables[sample] = {}

        toBeUpdated = False
        for mS, matchString in enumerate (dictSamples[sample]):
            #print matchString
            if( re.search(matchString, dataset_mod) ):
                #print "toBeUpdated"
                toBeUpdated = True
                break

        #print toBeUpdated
        if(toBeUpdated):
            UpdateTable(newtable, dictFinalTables[sample])

    #---End of the loop over datasets---#

outputTableFile = open(options.outputDir + "/" + options.analysisCode + "_tables.dat",'w')

for S,sample in enumerate( dictSamples ):
    #print "current sample is: ", sample
    #print dictFinalTables[sample]

    #---Create final tables 
    CalculateEfficiency(dictFinalTables[sample])
    #--- Write tables
    WriteTable(dictFinalTables[sample], sample, outputTableFile)

outputTableFile.close

print "output tables at: ", options.outputDir + "/" + options.analysisCode + "_tables.dat"

#---TODO: CREATE LATEX TABLE (PYTEX?) ---#


