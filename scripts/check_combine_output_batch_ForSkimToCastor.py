#!/usr/bin/env python

#---Import
import sys
import string
from optparse import OptionParser
import os.path
from ROOT import *
import re
import commands

#---Option Parser
#--- TODO: WHY PARSER DOES NOT WORK IN CMSSW ENVIRONMENT? ---#
usage = "usage: %prog [options] \nExample: \n./scripts/check_combine_output_batch.py -i `pwd`/HeepStudies_v1/QCDEMEnriched/inputList2030.txt -c analysisClass_HeepElectronStudiesV1 -d `pwd`/HeepStudies_v1/QCDEMEnriched -o `pwd`/HeepStudies_v1/QCDEMEnriched -q 1nh -s /castor/cern.ch/user/s/santanas/LQ/Ntuples"

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

parser.add_option("-o", "--outputDir", dest="outputDir",
                  help="the directory OUTDIR contains the output of the program (full path required)",
                  metavar="OUTDIR")

parser.add_option("-q", "--queue", dest="queue",
                  help="name of the queue for resubmission if necessary (choose among cmst3 8nm 1nh 8nh 1nd 1nw)",
                  metavar="QUEUE")

parser.add_option("-s", "--castorDir", dest="castorDir",
                  help="castor directory where the skim output is located (full path required)",
                  metavar="CASTORDIR")

(options, args) = parser.parse_args()

if len(sys.argv)<12:
    print usage
    sys.exit()


#--- Functions


def UpdateTable(inputTable, outputTable):
    if not outputTable:
        for j,line in enumerate( inputTable ):
            outputTable[int(j)]={'variableName': inputTable[j]['variableName'],
                                 'min1': inputTable[j]['min1'],
                                 'max1': inputTable[j]['max1'],
                                 'min2': inputTable[j]['min2'],
                                 'max2': inputTable[j]['max2'],
                                 'level': inputTable[j]['level'],
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
                                 'level': inputTable[j]['level'],
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
                             'level':       table[int(j)]['level'],
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
                if(Npass==N):
                    errEffRel = 0                
            
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
                           'level': table[int(j)]['level'],
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


def WriteTable(table, precutlist, file):
    for myline in precutlist:
        print>>file, myline
    print >>file, "#id".rjust(3),
    print >>file, "variableName".rjust(24),
    print >>file, "min1".rjust(14),
    print >>file, "max1".rjust(14),
    print >>file, "min2".rjust(14),
    print >>file, "max2".rjust(14),
    print >>file, "level".rjust(14),
    print >>file, "N".rjust(14),
    print >>file, "Npass".rjust(14),
    print >>file, "EffRel".rjust(14),
    print >>file, "errEffRel".rjust(14),
    print >>file, "EffAbs".rjust(14),
    print >>file, "errEffAbs".rjust(14)

    for j, line in enumerate(table):
        print >>file, repr(j).rjust(3),
        print >>file, table[j]['variableName'].rjust(24),
        print >>file, table[j]['min1'].rjust(14),
        print >>file, table[j]['max1'].rjust(14),
        print >>file, table[j]['min2'].rjust(14),
        print >>file, table[j]['max2'].rjust(14),
        print >>file, table[j]['level'].rjust(14),
        ###
        if( table[j]['N'] >= 0.1 ):
            print >>file, ("%.04f" % table[j]['N']).rjust(14),
        else:
            print >>file, ("%.04e" % table[j]['N']).rjust(14),        
        ###
        if( table[j]['Npass'] >= 0.1 ):
            print >>file, ("%.04f" % table[j]['Npass']).rjust(14),
        else:
            print >>file, ("%.04e" % table[j]['Npass']).rjust(14),
        ###
        if( table[j]['EffRel'] >= 0.1 ):
            print >>file, ("%.04f" % table[j]['EffRel']).rjust(14),
        else:
            print >>file, ("%.04e" % table[j]['EffRel']).rjust(14),
        ###
        if( table[j]['errEffRel'] >= 0.1 ):
            print >>file, ("%.04f" % table[j]['errEffRel']).rjust(14),
        else:
            print >>file, ("%.04e" % table[j]['errEffRel']).rjust(14),
        ###
        if( table[j]['EffAbs'] >= 0.1  ):
            print >>file, ("%.04f" % table[j]['EffAbs']).rjust(14),
        else:
            print >>file, ("%.04e" % table[j]['EffAbs']).rjust(14),
        ###
        if( table[j]['errEffAbs'] >=0.1 ):
            print >>file, ("%.04f" % table[j]['errEffAbs']).rjust(14)
        else:
            print >>file, ("%.04e" % table[j]['errEffAbs']).rjust(14)
            
        ##########

    print >>file, "\n"

    #--- print to screen
    
    print "\n"
    for myline in precutlist:
        print myline
    print "#id".rjust(3),
    print "variableName".rjust(24),
    print "min1".rjust(14),
    print "max1".rjust(14),
    print "min2".rjust(14),
    print "max2".rjust(14),
    print "level".rjust(14),
    print "N".rjust(14),
    print "Npass".rjust(14),
    print "EffRel".rjust(14),
    print "errEffRel".rjust(14),
    print "EffAbs".rjust(14),
    print "errEffAbs".rjust(14)

    for j, line in enumerate(table):
        print repr(j).rjust(3),
        print table[j]['variableName'].rjust(24),
        print table[j]['min1'].rjust(14),
        print table[j]['max1'].rjust(14),
        print table[j]['min2'].rjust(14),
        print table[j]['max2'].rjust(14),
        print table[j]['level'].rjust(14),
        ###
        if( table[j]['N'] >= 0.1 ):
            print ("%.04f" % table[j]['N']).rjust(14),
        else:
            print ("%.04e" % table[j]['N']).rjust(14),        
        ###
        if( table[j]['Npass'] >= 0.1 ):
            print ("%.04f" % table[j]['Npass']).rjust(14),
        else:
            print ("%.04e" % table[j]['Npass']).rjust(14),
        ###
        if( table[j]['EffRel'] >= 0.1 ):
            print ("%.04f" % table[j]['EffRel']).rjust(14),
        else:
            print ("%.04e" % table[j]['EffRel']).rjust(14),
        ###
        if( table[j]['errEffRel'] >= 0.1 ):
            print ("%.04f" % table[j]['errEffRel']).rjust(14),
        else:
            print ("%.04e" % table[j]['errEffRel']).rjust(14),
        ###
        if( table[j]['EffAbs'] >= 0.1  ):
            print ("%.04f" % table[j]['EffAbs']).rjust(14),
        else:
            print ("%.04e" % table[j]['EffAbs']).rjust(14),
        ###
        if( table[j]['errEffAbs'] >=0.1 ):
            print ("%.04f" % table[j]['errEffAbs']).rjust(14)
        else:
            print ("%.04e" % table[j]['errEffAbs']).rjust(14)

        #######################
        
    return



#--- End of Functions



#Open file containing the jobs to be resubmitted (one for all datasets)
ToBeResubmitted_name = "ToBeResubmitted.list"
ToBeResubmitted = open(ToBeResubmitted_name,'w')

#error counters
nLogFileErrors = 0
nRootFileSizeErrors = 0
nDatFileSizeErrors = 0
nJobsToBeResubmitted = 0

#---Loop over datasets
print "\n"
for n, lin in enumerate( open( options.inputList ) ):

    lin = string.strip(lin,"\n")
    #print lin
    
    dataset_mod = string.split( string.split(lin, "/" )[-1], ".")[0]
    print dataset_mod + " ... "

    #structure of the directory containing the output of the batch submission
    BatchDir = options.inputDir + "/" + options.analysisCode + "___" + dataset_mod
    inputBatchDir = BatchDir + "/" + "input"
    logBatchDir = BatchDir + "/" + "log"
    outputBatchDir = BatchDir + "/" + "output"
    scriptBatchDir = BatchDir + "/" + "src"
    castorBatchDir = options.castorDir
    #print BatchDir
    #print inputBatchDir
    #print logBatchDir
    #print outputBatchDir
    #print scriptBatchDir
    #print castorBatchDir

    #final output
    outputRootFile = options.inputDir + "/" + options.analysisCode + "___" + dataset_mod + ".root"
    outputDataFile = options.inputDir + "/" + options.analysisCode + "___" + dataset_mod + ".dat"
    #print outputRootFile
    #print outputDataFile


    ##--Check output for each job submitted in batch
    list_scriptBatchDir = os.listdir( scriptBatchDir )
    for script in list_scriptBatchDir:
        #print script
        number = string.split( string.split(script, "_" )[-1], ".")[0]
        #print number
        scriptFile =  scriptBatchDir + "/" + script
        logFile = logBatchDir + "/" + options.analysisCode + "___" + dataset_mod + "_" + number + ".log"
        rootFile = outputBatchDir + "/" + options.analysisCode + "___" + dataset_mod + "_" + number + ".root"
        datFile = outputBatchDir + "/" + options.analysisCode + "___" + dataset_mod + "_" + number + ".dat"
        skimFile = castorBatchDir + "/" + dataset_mod + "_" + number + ".root"

        resubmitThisJob = False

        # Check that for each .src you have the 4 correspondent .log, .root, .dat and skim.root files
        if(os.path.isfile(logFile) == False or os.path.isfile(rootFile) == False or os.path.isfile(datFile) == False or os.system("rfdir " + skimFile)!=0 ):
            resubmitThisJob = True
        else:
            for line in open(logFile):
                if "error" in line.lower() and "Error checking device name: LABEL" not in line:
                       resubmitThisJob = True
                       nLogFileErrors = nLogFileErrors+1
                       print logFile + "has at least one instance of the word 'error' (case insensitive)" 
                       break
                if "segmentation" in line.lower():
                       resubmitThisJob = True
                       nLogFileErrors = nLogFileErrors+1
                       print logFile + "has at least one instance of the word 'segmentation' (case insensitive)" 
                       break
                if "violation" in line.lower():
                       resubmitThisJob = True
                       nLogFileErrors = nLogFileErrors+1
                       print logFile + "has at least one instance of the word 'violation' (case insensitive)" 
                       break
            if (os.path.getsize(rootFile) == 0 ):
                resubmitThisJob = True
                nRootFileSizeErrors = nRootFileSizeErrors+1
                print rootFile, " has size equal to zero"
            if (os.path.getsize(datFile) == 0 ):
                resubmitThisJob = True
                nDatFileSizeErrors = nDatFileSizeErrors+1
                print datFile, "has size equal to zero"

        if ( resubmitThisJob == True):
            nJobsToBeResubmitted = nJobsToBeResubmitted+1
            print "--------------------------------------------------"
            print "WARNING: the output of job N. " + number + " is not complete." 
            if(os.path.isfile(logFile) == False):
                print "  - .log file not found   " # + logFile
            if(os.path.isfile(rootFile) == False):
                print "  - .root file not found  " # + rootFile
            if(os.path.isfile(datFile) == False):
                print "  - .dat file not found   " # + datFile 
                print "--------------------------------------------------"
            if(os.path.isfile(logFile) == True):
                os.system("mv -f " + logFile + " " + logFile + ".resubmit"  )
            if(os.path.isfile(rootFile) == True):
                os.system("mv -f " + rootFile + " " + rootFile + ".resubmit"  )
            if(os.path.isfile(datFile) == True):
                os.system("mv -f " + datFile + " " + datFile + ".resubmit"  )
                
            #print >> ToBeResubmitted, "rm -f " + logFile + " " + rootFile + " " + datFile 
            print >> ToBeResubmitted, "bsub -q " + options.queue + " -o " + logFile + " source " + scriptFile
            

    ##--Combine .root files
    print "merging .root files ... "
    #os.system("echo hadd -f " + outputRootFile + " " + outputBatchDir + "/*.root" )
    os.system ("rm -f hadd_tmp.txt")
    os.system("hadd -f " + outputRootFile + " " + outputBatchDir + "/*.root >& hadd_tmp.txt " )
    os.system ("rm -f hadd_tmp.txt")

    ##--Combine .dat files
    print "merging .dat files ... "
    dictFinalTable = {}
    preCutList = []



    #---Read .dat tables for current dataset
    list_outputBatchDir = os.listdir( outputBatchDir )

    countdat = -1
    
    for datfile in list_outputBatchDir:
        
        #print datfile
        datfileFullPath = outputBatchDir + "/" + datfile
        if( re.search("\.dat$", datfileFullPath) and not re.search("\.resubmit$", datfileFullPath) ):

            countdat = countdat + 1

            data={}
            column=[]
            lineCounter = int(0)

            for j,line in enumerate( open( datfileFullPath ) ):

                line = string.strip(line,"\n")

                #skip precuts 
                if( re.search("^###", line) ):
                    ############################
                    ##only once for each dataset
                    if(countdat==0):
                        preCutList.append(line)
                    ############################
                    continue

                #print "---> lineCounter: " , lineCounter
                #print line

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


            #---Create new table
            newtable={}
            Ntot = float(data[0]['N'])
    
            for j,line in enumerate( data ):
                if(j == 0):
                    newtable[int(j)]={'variableName': data[j]['variableName'],
                                      'min1': "-",
                                      'max1': "-",
                                      'min2': "-",
                                      'max2': "-",
                                      'level': "-",
                                      'N': Ntot,
                                      'errN': int(0),
                                      'Npass': Ntot ,
                                      'errNpass': int(0),
                                      }
                else:
                    N = ( float(data[j]['N'])  )
                    errN = ( float(data[j-1]["errEffAbs"]) * Ntot )
                    #print data[j]['variableName']
                    #print "errN: " , errN
                    if(str(errN) == "nan"):
                        errN = 0
                
                        #            if( float(N) > 0 and float(errN) > 0 ):
                        #                errRelN = errN / N 
                        #            else:
                        #                errRelN = float(0)
            
                    Npass = ( float(data[j]['Npass']) ) 
                    errNpass = ( float(data[j]["errEffAbs"]) * Ntot )
                    #print "errNPass " , errNpass
                    #print ""
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
                                      'level': data[j]['level'],
                                      'N':     N,
                                      'errN':  errN,
                                      'Npass': Npass,
                                      'errNpass': errNpass,
                                      }

            #print newtable

            #combine different .dat files from different jobs in one table    
            UpdateTable(newtable, dictFinalTable)

    #--- Calculate efficiency for each step of the analysis        
    CalculateEfficiency(dictFinalTable)
    #print dictFinalTable

    #--- Write tables
    outputTableFile = open(outputDataFile,'w')    
    WriteTable(dictFinalTable, preCutList, outputTableFile)
    outputTableFile.close

    #-------------------------------------
    ##-- Final output for this dataset

    print ".root file: " + outputRootFile 
    print ".dat file: " + outputDataFile 
    #-------------------------------------

    # move to another dataset


##--Close file containing the jobs to be resubmitted (one for all datasets)
ToBeResubmitted.close

#if (os.path.getsize(ToBeResubmitted_name) == 0 ): ## the size check was failing somehow... replaced with nJobsToBeResubmitted counter
if (nJobsToBeResubmitted == 0):
    print ""
    print "=== All jobs successfull!!! ==="
else:
    print "================================================="
    print "Number of log files found with at least one instance of the word 'error' or 'segmentation' or 'violation' (case insensitive) in it = ",nLogFileErrors
    print "Number of .root files found with zero size = ", nRootFileSizeErrors
    print "Number of .dat files found with zero size = ", nDatFileSizeErrors
    print "================================================="
    print "=== WARNING: "+str(nJobsToBeResubmitted)+" jobs need to be resubmitted ==="
    print "=== Check the file: " + ToBeResubmitted_name   
            
