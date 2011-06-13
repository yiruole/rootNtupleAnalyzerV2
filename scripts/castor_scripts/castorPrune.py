#!/usr/bin/python

import sys
import subprocess
import os
import time, signal
from multiprocessing import Pool

#--------------------------------------------------------------------------------------
# Define functions
#--------------------------------------------------------------------------------------

def printUsage() : 
    print "Usage: "
    print "  python castorPrune.py <folder in castor> " 
    print "  python castorPrune.py <txt file with list of commands> "
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

def checkFile ( castor_file_path, local_file_path, verbose ) :
    if os.path.exists ( local_file_path ) :
        castor_size_command = "rfdir " + castor_file_path
        local_size_command  = "ls -l " + local_file_path

        castor_size = int ( subprocess.Popen ( castor_size_command , shell=True, stdout=subprocess.PIPE ).communicate()[0].split()[4] ) 
        local_size  = int ( subprocess.Popen ( local_size_command  , shell=True, stdout=subprocess.PIPE ).communicate()[0].split()[4] ) 
        
        if castor_size != local_size: 
            if verbose:
                print "WARNING:" 
                print "   File " + local_file_path  + " has size " + str(local_size )
                print "   It had size " + str( castor_size ) + " on castor " 
                print "   I WILL re-download it"
            return -2 

        else : 
            if verbose:
                print "WARNING:" 
                print "   File : " + local_file_path + " was already downloaded successfully"
                print "   I WILL NOT re-download it"
            return 0
            
    else :
        return -1

def printAndExecute ( command ): 
    print command
    os.system ( command ) 

def getCommandList_fromFile ( file_name ) : 
    command_list =[]
    
    in_file = open ( file_name, "r") 
    for line in in_file:
        command_list.append ( line[:-1] ) 

    return command_list

def getCommandList_fromFolder ( castor_folder ) :


    command_list = []
    command = "rfdir "+ castor_folder
    output = subprocess.Popen ( command , shell=True, stdout=subprocess.PIPE ).communicate()[0].split()
    root_files = []
    
    for entry in output: 
        if ".root" not in entry : continue
        root_files.append ( entry ) 
        
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
# Are there files that need to be downloaded?
#--------------------------------------------------------------------------------------

    if len ( root_files_to_download ) == 0 : 
        print "No files to download!" 
        sys.exit() 
    
#--------------------------------------------------------------------------------------
# Find out where to download the files
#--------------------------------------------------------------------------------------

    target_folder = raw_input ("To what local disk folder should I download files? " )
    print target_folder 
    
    if not os.path.isdir ( target_folder ) :
        print "ERROR: " + target_folder + " is not a directory. Bailing. " 
        sys.exit()

#--------------------------------------------------------------------------------------
# Make a list of commands
#--------------------------------------------------------------------------------------

    for i, root_file_to_download in enumerate ( root_files_to_download ) :

        full_castor_path = castor_folder + "/" + root_file_to_download
        full_target_path = target_folder + "/" + root_file_to_download

        status = checkFile ( full_castor_path, full_target_path, True ) 
        if ( status < 0 ) :
            command = "nice rfcp " + full_castor_path + " " + target_folder 
            command_list.append ( command ) 

    return command_list
            
#--------------------------------------------------------------------------------------
# If input doesn't make sense, quit
#--------------------------------------------------------------------------------------

if len ( sys.argv ) != 2: 
    print "Syntax error"
    printUsage() 

if os.path.isfile ( sys.argv[1] ) :
    in_file_name = sys.argv[1]
    print "The user has specified a file: " + in_file_name 
    command_list = getCommandList_fromFile ( in_file_name ) 
    print "I will execute " + str( len ( command_list ) ) + " commands from this file " 

else: 
    castor_folder = sys.argv[1]
    print "This is not a file: " + castor_folder
    print "So I will treat it as a CASTOR folder" 
    command_list = getCommandList_fromFolder ( castor_folder ) 

if len ( command_list ) == 0 :
    print "I cannot find any files to download!  Maybe all of the files were already downloaded?"
    sys.exit(1) 

else : 
    print "I found " + str ( len ( command_list ) ) + " files to download: " 
    for entry in command_list : 
        for field in entry.split() : 
            if ".root" in field and "castor" in field:
                print field

#--------------------------------------------------------------------------------------
# How many workers should I use?
#--------------------------------------------------------------------------------------

n_workers = int ( raw_input ( "How many workers should I use? " ) ) 
print n_workers 
    
#--------------------------------------------------------------------------------------
# Make a pool to execute the commands
#--------------------------------------------------------------------------------------

pool = Pool (n_workers)

#--------------------------------------------------------------------------------------
# Try to get the pool of commands to run.
# If the user wants to quit, save the remaining copies to a file.
#--------------------------------------------------------------------------------------

try:
    pool.map_async( printAndExecute, command_list ).get(99999999)

except KeyboardInterrupt:

#--------------------------------------------------------------------------------------
# First, terminate the pool
#--------------------------------------------------------------------------------------

    pool.terminate()

#--------------------------------------------------------------------------------------
# Now write the remaining commands to a .txt file
#--------------------------------------------------------------------------------------

    print "\n"
    print "\n"
    print "WARNING: User hit ^C.  Script is quitting.  Please be patient... "
   
    file_name = "commands.txt"
    
    file = open ( file_name , "w" )
    
    n_remaining_files = 0

    for command in command_list :

        castor_path =  command.split()[-2]
        local_path  =  command.split()[-1] + "/" + command.split()[-2].split("/")[-1]
        status = checkFile ( castor_path, local_path, False ) 
        if ( status < 0 ) : 
            file.write ( command + "\n") 
            n_remaining_files += 1
    file.close()

    if n_remaining_files == 0 : 
        print "All files have been copied!  You're done!" 
        os.system ( "rm " + file_name ) 
        sys.exit(1) 

#--------------------------------------------------------------------------------------
# Finally, tell the user what to do:
#--------------------------------------------------------------------------------------
    print "\n"
    print "Wrote commands to copy " + str ( n_remaining_files ) + " remaining files to " + file_name + " .  To retry, do: "
    print "\n"
    print "   python " + sys.argv[0] + " " + file_name
    print "\n"
    print "\n"
    sys.exit(1)
    
