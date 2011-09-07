#!/usr/bin/python

#-------------------------------------------------------
# Define imports
#-------------------------------------------------------

import os, sys
import subprocess

#-------------------------------------------------------
# Define functions 
#-------------------------------------------------------

def print_usage() :
    print "Usage:",sys.argv[0],"<input list path>" 
    sys.exit()

def file_len(fname):    
    length = 0
    f = open ( fname,"r" )
    for l in f : 
        length = length + 1
    f.close()
    return length

def recover ( command , stderr ) : 

    print "Non-empty stderr from stage command:" 
    print "  Command = " + command 
    print "  Error   = [" + stderr + "]"

    if "Maximum number of requests exceeded" in stderr : 
        print "Sleeping for 500 seconds, then retrying the command." 
        print 
        os.system ( "sleep 500" ) 
        print "... I am awake again.  Retrying the command."
        output = subprocess.Popen ( command , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        stdout, stderr_new = output.communicate() 

        if stderr_new != "" :
            stdout = recover ( command, stderr_new ) 
        else : 
            return stdout

        print "... Command submitted. Continuing as usual."
    else :
        print "Bailing."
        sys.exit() 

#-------------------------------------------------------
# Get your lists, dictionaries, and counters ready
#-------------------------------------------------------

sub_txt_file_paths = []
root_file_paths    = []
root_file_statuses = {}

n_staged_total   = 0 
n_unstaged_total = 0
n_staging_total  = 0 

#-------------------------------------------------------
# There should be only one argument (input list)
#-------------------------------------------------------

if len (sys.argv) != 2 : print_usage()

txt_file_path = sys.argv[1]

#-------------------------------------------------------
# Does the file exist?
#-------------------------------------------------------

if not os.path.exists ( txt_file_path ) :
    print "ERROR: file \"",txt_file_path,"\" does not exist"
    print_usage()

#-------------------------------------------------------
# Open the file
#-------------------------------------------------------

txt_file = open ( txt_file_path, "r" ) 

#-------------------------------------------------------
# Get lists of root files or subordinate txt files
#-------------------------------------------------------

n_root_files = 0
n_queries = 0

for entry in txt_file :
    if entry[-1] == "\n"    : entry = entry[:-1]
    if entry[:5] == "rfio:" : entry = entry[5: ]

    entry_suffix = entry.split(".")[-1]

    if   entry_suffix == "txt"  : 
        sub_txt_file_paths.append ( entry ) 

    elif entry_suffix == "root" : 

        command = "stager_qry -M "+entry 

        output = subprocess.Popen ( command , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        stdout, stderr = output.communicate()
        
        if stderr != "": 
            stdout = recover ( command, stderr ) 
            
        status = stdout.split()[2]

        if   ( status == "STAGED"  ) : n_staged_total    = n_staged_total   + 1 
        elif ( status == "STAGEIN" ) : n_staging_total   = n_staging_total  + 1 
        else                         : 
            command = "stager_get -M "+entry 
            output = subprocess.Popen ( command , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            stdout, stderr = output.communicate() 
            if stderr != "" :
                stdout = recover ( command, stderr ) 
            n_unstaged_total  = n_unstaged_total + 1

        root_file_paths.append    ( entry )
        root_file_statuses[entry] = status
        n_root_files = n_root_files + 1
        
    else :
        print "ERROR: your input file must contain only .txt files and .root files"
        print "  --> file",txt_file_path,"contains the entry:", entry 
        print "  --> Bailing."
        sys.exit() 

txt_file.close()

print "I have found",n_root_files,"root files in your file:",txt_file_path

#-------------------------------------------------------
# Loop over sub_txt file paths and get root files out
#-------------------------------------------------------

for i, sub_txt_file_path in enumerate(sub_txt_file_paths):

    sub_txt_file = open ( sub_txt_file_path, "r" )
    
    n_staged   = 0
    n_unstaged = 0
    n_staging  = 0

    # Logging...
    print "File [",i+1,"/",len (sub_txt_file_paths),"]:",sub_txt_file_path,"has", file_len ( sub_txt_file_path ), "files"
    
    for entry in sub_txt_file : 
        if entry[-1]            == "\n"    : entry = entry[:-1]
        if entry[:5]            == "rfio:" : entry = entry[5: ]
        if entry.split(".")[-1] != "root"  : 
            print "ERROR: your input file must contain either .root files or .txt lists of .root files"
            print "  --> file",sub_txt_file_path,", listed in file",txt_file_path,"contains the entry:", entry
            print "  --> Bailing."
            sys.exit() 
            
        command = "stager_qry -M "+entry 

        output = subprocess.Popen ( command , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        stdout, stderr = output.communicate() 

        if stderr != "":
            stdout = recover ( command, stderr ) 

        if ( len ( stdout.split() ) >= 3 ):

            status = stdout.split()[2]
            
            if   ( status == "STAGED" ) : 
                n_staged         = n_staged         + 1 
                n_staged_total   = n_staged_total   + 1 
            elif ( status == "STAGEIN" ) : 
                n_staging        = n_staging        + 1
                n_staging_total  = n_staging_total  + 1
            else                     : 
                n_unstaged       = n_unstaged       + 1
                n_unstaged_total = n_unstaged_total + 1
                subprocess.Popen ( "stager_get -M "+entry , shell=True, stdout=subprocess.PIPE )
                #print "LIST: " + entry

        else : 
            print "ERROR:"
            print "\t command = " + command 
            print "\t stdout  = " + output 

        root_file_paths.append ( entry ) 
        root_file_statuses[entry] = status
    
    print "  -->", n_staged  , "files staged"
    if n_staging  != 0 : print "  -->", n_staging , "files already staging"
    if n_unstaged != 0 : print "  -->", n_unstaged, "files NOT staging, stage command issued"
    
#-------------------------------------------------------
# Loop over files and stage the ones that need staging
#-------------------------------------------------------

print "I have found",len(root_file_paths),"root files in total"
print "  -->", n_staged_total  , "files were staged"
if n_staging_total  != 0 : print "  -->", n_staging_total , "files were staging"
if n_unstaged_total != 0 : print "  -->", n_unstaged_total, "files were NOT staged, but a stage command was issued"
