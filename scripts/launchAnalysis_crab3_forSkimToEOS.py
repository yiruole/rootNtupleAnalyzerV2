#!/usr/bin/env python

from optparse import OptionParser
import os,sys, errno, time
import subprocess as sp
try:
  from CRABClient.UserUtilities import config, getUsernameFromSiteDB
except ImportError:
  print
  print 'ERROR: Could not load CRABClient.UserUtilities.  Please source the crab3 setup:'
  print 'source /cvmfs/cms.cern.ch/crab3/crab.sh'
  exit(-1)

import deleteCrabSandboxes

#-------------------------------------------------------------------------------------------------------------
# Notes
# Use this script first, which then calls the submit_crab3 script to actually submit the jobs for each dataset
#-------------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------
# Parse options
#--------------------------------------------------------------------------------

usage = "usage: %prog [options] \nExample: python ./scripts/launchAnalysis_batch_ForSkimToEOS.py <options>"

parser = OptionParser(usage=usage)

parser.add_option("-i", "--inputlist", dest="inputlist",
                  help="list of all datasets to be used",
                  metavar="LIST")

parser.add_option("-o", "--output", dest="outputDir",
                  help="the directory OUTDIR contains the output of the program",
                  metavar="OUTDIR")

parser.add_option("-n", "--treeName", dest="treeName",
                  help="name of the root tree; defaults to rootTupleTree/tree",
                  metavar="TREENAME")

parser.add_option("-c", "--cutfile", dest="cutfile",
                  help="name of the cut file",
                  metavar="CUTFILE")

parser.add_option("-j", "--ijobmax", dest="ijobmax",
                  help="max number of jobs, limited automatically to the number of files in inputlist",
                  metavar="IJOBMAX")

# TODO: eventually support this by using the crab scheduler?
#parser.add_option("-q", "--queue", dest="queue",
#                  help="name of the queue (choose among cmst3 8nm 1nh 8nh 1nd 1nw)",
#                  metavar="QUEUE")

parser.add_option("-d", "--eosDir", dest="eosDir",
                  help="the EOS directory where skims are stored",
                  metavar="EOSDIR")


(options, args) = parser.parse_args()

if ( not options.inputlist 
     or not options.outputDir
     or not options.cutfile 
     #or not options.ijobmax 
     #or not options.queue 
     or not options.eosDir ) : 
    parser.print_help()
    sys.exit()

if not options.treeName:
  options.treeName='rootTupleTree/tree'

#--------------------------------------------------------------------------------
# Delete crab sandboxes
#--------------------------------------------------------------------------------
print 'First, delete existing crab sandboxes'
deleteCrabSandboxes.main()
print 'Done'

#--------------------------------------------------------------------------------
# Make the output directory
#--------------------------------------------------------------------------------

print "Making the local output directory..."

if not os.path.isdir ( options.outputDir ) : 
    os.system ( "mkdir -p " + options.outputDir )

if not os.path.isdir ( options.outputDir ) : 
    print "Error: I can't make this folder: " + options.outputDir 
    sys.exit() 

print "... done "

#--------------------------------------------------------------------------------
# Look for the cut file.  If it exists, move it to the output directory
#--------------------------------------------------------------------------------

print "Moving the cutfile to the local output directory..."

if not os.path.isfile ( options.cutfile ) : 
    print "Error: No cut file here: " + options.cutfile 
    sys.exit() 
else : 
    os.system ( "cp " + options.cutfile + " " + options.outputDir + "/" )

print "... done "

#--------------------------------------------------------------------------------
# Look for the inputList file
#--------------------------------------------------------------------------------

print "Moving the inputlist to the local output directory..."

if not os.path.isfile ( options.inputlist ) : 
    print "Error: No input list here: " + options.inputlist 
    sys.exit() 
else : 
    os.system ( "cp " + options.inputlist + " " + options.outputDir + "/" )

print "... done "

#--------------------------------------------------------------------------------
# Get JSON file from cut file and copy it to the output directory
#--------------------------------------------------------------------------------

print "Moving the JSON file to the local output directory..."

cutfile = open ( options.cutfile , "r" )
found_json = False 
for line in cutfile:
    if line.strip() == "" : continue
    if line.split()[0] == "#" : continue
    if line.strip()[:4] == "JSON":
        if found_json == True:
            print "Error: You are only allowed to have one JSON file per cut file."
            print "cut file = " + options.cutfile 
            sys.exit()
        if len (line.split()) != 2 : 
            print "Error: this line in your cut file does not make sense:"
            print line
            print "cut file = " + options.cutfile 
            sys.exit()
        json_file = line.split()[1]
        if not os.path.isfile( json_file ) : 
            print "Error: No JSON file here: " + json_file 
            sys.exit()
        else :
            os.system ( "cp " + json_file + " " + options.outputDir )
            found_json = True

print "... done "
                   
#--------------------------------------------------------------------------------
# Check if path is a link
#--------------------------------------------------------------------------------

print "Checking the link to analysisClass.C..."

if not os.path.islink ( "src/analysisClass.C" ) :
    print "Error: src/analysisClass.C is not a symbolic link"
    sys.exit()
code_name = os.readlink ( "./src/analysisClass.C" ).split("/")[-1].split(".C")[0]

print "... done"

#--------------------------------------------------------------------------------
# Launch
#--------------------------------------------------------------------------------

print "Launching jobs..."

inputlist_file = file ( options.inputlist,"r" )

total_jobs = 0
failedCommands = ''

for line in inputlist_file: 
    if line[0] == "#" : continue
    dataset = line.strip().split("/")[-1].split(".txt")[0]
    
    sublist = line.strip()

    #jobs_to_submit = int(options.ijobmax)
    
    #total_jobs = total_jobs + jobs_to_submit

    command = "./scripts/submit_crab3_forSkimToEOS.py"
    command = command + " -i " + line.strip() 
    command = command + " -c " + options.outputDir+'/'+options.cutfile.split('/')[-1]
    command = command + " -t " + options.treeName 
    command = command + " -o " + options.outputDir + "/" + code_name + "___" + dataset
    #command = command + " -n " + str(jobs_to_submit)
    #command = command + " -q " + options.queue
    command = command + " -d " + options.eosDir
    
    print command
    ret = os.system  ( command ) 
    if ret != 0:
      print 'ERROR: something went wrong when running the command:'
      print '\t'+command
      print 'add to list'
      failedCommands+=command
      failedCommands+='\n'
    #time.sleep (  float( options.wait ) ) 

inputlist_file.close() 

print 'list of failed commands:'
print failedCommands
#print "total jobs =", total_jobs

