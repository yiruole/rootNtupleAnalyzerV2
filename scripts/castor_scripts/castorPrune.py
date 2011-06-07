#!/usr/bin/python

import sys
import subprocess
import os
from multiprocessing import Pool

#--------------------------------------------------------------------------------------
# Define functions
#--------------------------------------------------------------------------------------

def printUsage() : 
    print "Usage: "
    print "  python castorPrune.py <folder in castor> " 
    sys.exit() 

def getJobNumber ( file_name ) : 
    return file_name.split("_")[-3]

def getTryNumber ( file_name ) : 
    return file_name.split("_")[-2]

def getBaseName ( file_name ) : 
    base_name = ""
    for field in file_name.split("_")[:-3]:
        base_name = base_name + field + "_" 
    return base_name[:-1]

def printAndExecute ( command ): 
    print command
    os.system ( command ) 

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
root_files = subprocess.Popen ( command , shell=True, stdout=subprocess.PIPE ).communicate()[0].split()

for root_file in root_files: 
    getBaseName ( root_file ) 
    if root_file[-5:] != ".root" : root_files.remove (root_file)

if len ( root_files ) == 0 : 
    print "No root files in folder "+castor_folder
    printUsage()

#--------------------------------------------------------------------------------------
# Make a dictionary:
#   keys are job numbers
#   targets are max trial numbers
#--------------------------------------------------------------------------------------

dict_baseName_jobNumber_to_maxTryNumber = {} 

for root_file in root_files:
    
    base_name  = getBaseName  ( root_file ) 
    job_number = getJobNumber ( root_file ) 
    try_number = getTryNumber ( root_file ) 


    
    if base_name not in dict_baseName_jobNumber_to_maxTryNumber.keys() :
        dict_baseName_jobNumber_to_maxTryNumber[base_name] = {}

    if job_number not in dict_baseName_jobNumber_to_maxTryNumber[base_name].keys() : 
        dict_baseName_jobNumber_to_maxTryNumber[base_name][ job_number ] = try_number
    else : 
        max_try_number = dict_baseName_jobNumber_to_maxTryNumber[base_name][ job_number ]
        if try_number > max_try_number : 
            dict_baseName_jobNumber_to_maxTryNumber[base_name][ job_number ] = try_number

#--------------------------------------------------------------------------------------
# Make a list of root files to download
#--------------------------------------------------------------------------------------

root_files_to_download = []

for root_file in root_files:
    base_name      = getBaseName  ( root_file ) 
    job_number     = getJobNumber ( root_file ) 
    try_number     = getTryNumber ( root_file ) 
    max_try_number = dict_baseName_jobNumber_to_maxTryNumber[ base_name ][ job_number ] 

    if try_number == max_try_number:
        root_files_to_download.append ( root_file ) 

#--------------------------------------------------------------------------------------
# Are there files that need to be deleted?
#--------------------------------------------------------------------------------------

if len ( root_files_to_download ) == 0 : 
    print "No files to download!" 
    sys.exit() 

#--------------------------------------------------------------------------------------
# Print root files you intend to download
#--------------------------------------------------------------------------------------

print "Consider the following " + str ( len ( root_files_to_download ) ) + " files: "

for root_file_to_download in root_files_to_download:
    print root_file_to_download

download_files = raw_input ("Is it ok if I download these "+ str ( len ( root_files_to_download ) )  + " files [yes/no]: ")
print download_files

if download_files != "yes" : sys.exit() 

#--------------------------------------------------------------------------------------
# Find out where to download the files
#--------------------------------------------------------------------------------------

target_folder = raw_input ("Where should I download them? ")
print target_folder 

if not os.path.isdir ( target_folder ) :
    print "ERROR: " + target_folder + " is not a directory. Bailing. " 
    sys.exit()

#--------------------------------------------------------------------------------------
# How many workers should I use?
#--------------------------------------------------------------------------------------

n_workers = int ( raw_input ( "How many workers should I use? " ) ) 
print n_workers 

#--------------------------------------------------------------------------------------
# Make a list of commands
#--------------------------------------------------------------------------------------

command_list =[]

for i, root_file_to_download in enumerate ( root_files_to_download ) :

    full_castor_path = castor_folder + "/" + root_file_to_download
    full_target_path = target_folder + "/" + root_file_to_download
    
    if os.path.exists ( full_target_path ) :
        castor_size_command = "nsls -l " + full_castor_path
        local_size_command  = "ls -l "   + full_target_path

        castor_size = int ( subprocess.Popen ( castor_size_command , shell=True, stdout=subprocess.PIPE ).communicate()[0].split()[4] ) 
        local_size  = int ( subprocess.Popen ( local_size_command  , shell=True, stdout=subprocess.PIPE ).communicate()[0].split()[4] ) 
        
        if castor_size != local_size : 
            print "WARNING:" 
            print "   File " + full_local_path  + " has size " + str(local_size )
            print "   It had size " + str( castor_size ) + " on castor " 

        continue

    command = "rfcp " + full_castor_path + " " + target_folder 
    
    command_list.append ( command ) 

pool = Pool (processes = n_workers )
pool.map ( printAndExecute , command_list ) 
