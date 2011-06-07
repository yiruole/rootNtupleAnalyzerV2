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
    print "  python castorPrune.py <local folder with .root files> <folder in castor> " 
    print "  python castorPrune.py <list of .root files>           <folder in castor> " 
    sys.exit() 

def printAndExecute ( command ): 
    print command
    os.system ( command ) 

def getCommandList_folder( local, castor_folder ):
    files = os.listdir ( local[0] ) 
    file_list = []
    command_list = []
    for file in files:
        if file[-5:] != ".root" : 
            print "WARNING: " + local[0] + "/" + file + " is not a .root file, and I won't copy it." 
        else : 
            command_list.append ( "rfcp " + local[0] + "/" + file + " " + castor_folder )
            file_list.append ( local[0] + "/" + file ) 
            
    if len ( command_list ) == 0 : 
        print "ERROR: No files to copy in folder : " + local[0] + " ... Bailing."
        sys.exit() 

    return file_list, command_list

def getCommandList_files ( local, castor_folder ): 
    files = []
    file_list = []
    command_list = []

    for file in local:
        if not os.path.isfile ( file ) :
            print "WARNING: " + file + " is not a file, and I won't copy it " 
        elif ".root" not in file:
            print "WARNING: " + file + " is not a .root file, and I won't copy it " 
        else : 
            command_list.append ( "rfcp " + file + " " + castor_folder ) 
            file_list.append ( file ) 
                
    if len ( command_list ) == 0 : 
        print "ERROR: No files to copy ... Bailing."
        sys.exit() 

    return file_list, command_list

#--------------------------------------------------------------------------------------
# Get info
#--------------------------------------------------------------------------------------

castor_folder = sys.argv[-1]
local = sys.argv [1:-1]
user = os.getenv ( "USER" )
castor_folder_expected_prefix = "/castor/cern.ch/user/" + user[0] + "/" + user + "/"

#--------------------------------------------------------------------------------------
# If input doesn't make sense, quit
#--------------------------------------------------------------------------------------

if castor_folder_expected_prefix not in castor_folder:
    print "ERROR: Castor folder must start with: "  + castor_folder_expected_prefix
    printUsage()

#--------------------------------------------------------------------------------------
# Find out if the castor folder exists
#--------------------------------------------------------------------------------------

command = "nsls " + castor_folder

output_out = subprocess.Popen ( command , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE ).communicate()[0]
output_err = subprocess.Popen ( command , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE ).communicate()[1]

castor_file_exists =  "No such file or directory" not in output_err

#--------------------------------------------------------------------------------------
# If the castor folder doesn't exist, do you want to make it?
#--------------------------------------------------------------------------------------

if not castor_file_exists:
    print castor_folder, "folder does not exist"
    create = raw_input ("Would you like to create it? [yes/no] ");
    if create == "yes" : 
        command = "rfmkdir -p " + castor_folder 
        print command 
        os.system ( command ) 
        command = "nsls " + castor_folder
        output_err = subprocess.Popen ( command , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE ).communicate()[1]
        castor_file_exists_now =  "No such file or directory" not in output_err
        if not castor_file_exists_now:
            print "ERROR: Could not create " + castor_folder + " ... bailing."
            sys.exit()
    else : 
        sys.exit()

#--------------------------------------------------------------------------------------
# Now that we have a destination, get the list of files and commands
#--------------------------------------------------------------------------------------

file_list = []
command_list = []

if len ( local ) == 1 and os.path.isdir ( local[0] ) : 
    file_list, command_list = getCommandList_folder( local, castor_folder )
else : 
    file_list, command_list = getCommandList_files ( local, castor_folder )


#--------------------------------------------------------------------------------------
# Tell the user what we're doing
#--------------------------------------------------------------------------------------

print "I will copy : " 
for file in file_list : 
    print "  ...", file
print "To CASTOR folder :", castor_folder

#--------------------------------------------------------------------------------------
# Find out how many workers to use
#--------------------------------------------------------------------------------------

n_workers = int ( raw_input ( "How many workers should I use? " ) ) 
print n_workers 

#--------------------------------------------------------------------------------------
# Execute the command 
#--------------------------------------------------------------------------------------

pool = Pool (processes = n_workers )
pool.map ( printAndExecute , command_list ) 

