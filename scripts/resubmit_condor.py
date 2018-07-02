#! /usr/bin/env python

import os
import sys
import string
import re

argv = sys.argv[1:]

while argv:
        errFileFullPath = argv.pop()
        print 'consider errFile=',errFileFullPath
        # example: mar15_tuplev237_rskQCD/analysisClass_lq1_skim___DYJetsToLL_Pt-250To400_ext5_amcatnloFXFX/error/51.err
        errFile = errFileFullPath.split('/')[-1]
        jobNum = errFile.split('.')[0]
        datasetpath = '/'.join(errFileFullPath.split('/')[:-2])
        origCwd = os.getcwd()
        outputmain = os.path.abspath(origCwd+'/'+datasetpath)
        #print 'outputmain=',outputmain
        os.chdir(outputmain)

        # write condor submit file
        condorFileName = 'condorResubmit.sub'
        oldCondorSubFileTxt = open('condorSubmit.sub','r').readlines()
        for i,line in enumerate(oldCondorSubFileTxt):
            if 'N' in line:
                #print 'found N in line:',line
                if 'queue' in line:
                    #print 'found queue in line:',line
                    oldCondorSubFileTxt[i] = 'queue\n'
                    continue
                elif 'N =' in line:
                    #print 'found N = in line:',line
                    oldCondorSubFileTxt[i] = '\n'
                    continue
            oldCondorSubFileTxt[i] = line.replace('$(Process)',str(jobNum))

        with open(condorFileName,'w') as condorFile:
            for line in oldCondorSubFileTxt:
                condorFile.write(line)

        #print 'here, we would submit the new condorFile:',condorFileName
        os.system('condor_submit '+condorFileName)
        os.chdir(origCwd)
