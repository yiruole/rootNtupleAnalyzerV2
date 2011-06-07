#!/usr/bin/python

import sys
import subprocess
import os

#--------------------------------------------------------------------------------------
# Define functions
#--------------------------------------------------------------------------------------

def printUsage() : 
    print "Usage: "
    print "  python castorClean.py <folder in castor> " 
    sys.exit() 

def getJobNumber ( file_name ) : 
    return file_name.split("_")[-3]

def getTryNumber ( file_name ) : 
    return file_name.split("_")[-2]

#--------------------------------------------------------------------------------------
# If input doesn't make sense, quit
#--------------------------------------------------------------------------------------

if len ( sys.argv ) != 2: 
    print "Syntax error"
    printUsage() 

#--------------------------------------------------------------------------------------
# Get the castor folder and the root files in it
#--------------------------------------------------------------------------------------

castor_folder = sys.argv[1]
command = "nsls "+ castor_folder
root_files = output = subprocess.Popen ( command , shell=True, stdout=subprocess.PIPE ).communicate()[0].split()

if len ( root_files ) == 0 : 
    print "No root files in folder "+castor_folder
    printUsage()

#--------------------------------------------------------------------------------------
# Make a dictionary:
#   keys are job numbers
#   targets are max trial numbers
#--------------------------------------------------------------------------------------

dict_jobNumber_to_maxTryNumber = {} 
dict_jobNumber_to_maxTryFileName = {}

for root_file in root_files:
    job_number = getJobNumber ( root_file ) 
    try_number = getTryNumber ( root_file ) 

    if job_number not in dict_jobNumber_to_maxTryNumber : 
        dict_jobNumber_to_maxTryNumber   [ job_number ] = try_number
        dict_jobNumber_to_maxTryFileName [ job_number ] = root_file
    else : 
        max_try_number = dict_jobNumber_to_maxTryNumber [ job_number ]
        if try_number > max_try_number : 
            dict_jobNumber_to_maxTryNumber   [ job_number ] = try_number
            dict_jobNumber_to_maxTryFileName [ job_number ] = root_file

#--------------------------------------------------------------------------------------
# Make a list of root files to delete
#--------------------------------------------------------------------------------------

root_files_to_delete = []

for root_file in root_files:

    job_number     = getJobNumber ( root_file ) 
    try_number     = getTryNumber ( root_file ) 
    max_try_number = dict_jobNumber_to_maxTryNumber [ job_number ] 

    if try_number < max_try_number:
        root_files_to_delete.append ( root_file ) 

#--------------------------------------------------------------------------------------
# Are there files that need to be deleted?
#--------------------------------------------------------------------------------------

if len ( root_files_to_delete ) == 0 : 
    print "No files to delete!" 
    sys.exit() 

#--------------------------------------------------------------------------------------
# Print root files you intend to delete
#--------------------------------------------------------------------------------------

print "Consider the following files: "

for root_file_to_delete in root_files_to_delete:
    print root_file_to_delete 
    print "  This file has a higher trial number: " + dict_jobNumber_to_maxTryFileName [ getJobNumber ( root_file_to_delete ) ]

delete_files = raw_input ("Is it ok if I delete these files [yes/no]: ")
print delete_files

if delete_files != "yes" : sys.exit() 

#--------------------------------------------------------------------------------------
# Delete the files
#--------------------------------------------------------------------------------------

for root_file_to_delete in root_files_to_delete:
    full_path = castor_folder + "/" + root_file_to_delete 
    command = "nsrm -f " + full_path 
    print command 
    os.system ( command ) 
