#!/usr/bin/python
# If you're processing a smaller amount of data (as in the 2F region of the closure test) it's faster to use this, so I updated it. -Emma
#----------------------------------------------------------------
# Imports
#----------------------------------------------------------------

import optparse
import sys
import os
import multiprocessing
from multiprocessing import Pool

#----------------------------------------------------------------
# Define functions
#----------------------------------------------------------------

def printAndExecute ( command ): 
    print (command)
    os.system ( command ) 

#----------------------------------------------------------------
# Get user options
#----------------------------------------------------------------

parser = optparse.OptionParser(description='Launch the analysis')
parser.add_option ("--input_list", "-i" , dest = "input_list", type=str, help="Text file containing paths of input lists with .root files for analysis")
parser.add_option ("--output_dir", "-o" , dest = "output_dir", type=str, help="Directory where output will be stored" ) 
parser.add_option ("--tree_name" , "-n" , dest = "tree_name" , type=str, help="Name of TTree in .root files to be analyzed")
parser.add_option ("--cut_file"  , "-c" , dest = "cut_file"  , type=str, help="Text file containing cut values" ) 
parser.add_option ("--ncores"    , "-p" , dest = "ncores"    , type=int, help="Number of processor cores to be used to run the job" )
parser.add_option ("--exe"       , "-e" , dest = "execut"    , type=str, help="name of exec" )
parser.add_option ("--code_name" , "-k" , dest = "code_name" , type=str, help="code name" )

(options, args) = parser.parse_args()

if not options.input_list : parser.print_help(); sys.exit()
if not options.output_dir : parser.print_help(); sys.exit()
if not options.tree_name  : parser.print_help(); sys.exit()
if not options.cut_file   : parser.print_help(); sys.exit()
if not options.code_name  : parser.print_help(); sys.exit()

ncores = multiprocessing.cpu_count()
if options.ncores :
    ncores = options.ncores

executable = "main"
if options.execut:
  executable = options.execut

#----------------------------------------------------------------
# Bail if the cut file doesn't exist:
#----------------------------------------------------------------

if not os.path.isfile ( options.cut_file ) :
    print ("ERROR.  Cut file does not exist: " + options.cut_file)
    sys.exit() 

#----------------------------------------------------------------
# Bail if the input list doesn't exist:
#----------------------------------------------------------------

if not os.path.isfile ( options.input_list ) : 
    print ("ERROR.  Input list does not exist: " + options.input_list)
    sys.exit() 

#----------------------------------------------------------------
# Make the output directory if it doesn't exist
#----------------------------------------------------------------

if not os.path.isdir ( options.output_dir ) : 
    print ("Making directory: " + options.output_dir)
    #os.mkdir ( options.output_dir )
    os.makedirs ( options.output_dir ) 

#----------------------------------------------------------------
# Can you find a JSON file? If so, save it
#----------------------------------------------------------------

cut_file = open ( options.cut_file, "r" ) 
found_json = False
for line in cut_file:
    line = line.split()
    if line[0:4] == "JSON":

        json_file_path = ""

        if found_json:
            print ("ERROR.  Cut file contains multiple JSON files")
            print ("   Cut file is: " + options.cut_file)
            sys.exit()
        elif len (line.split() ) != 2 : 
            print ("ERROR.  Cut file contains bad syntax about JSON file.")
            print ("   Cut file is: " + options.cut_file)
            print ("   Line should read: JSON <path to JSON file>")
            print ("   Line reads      : " + line)
            sys.exit()
        elif not os.path.isfile ( line.split()[1] ) :
            print ("ERROR. JSON file in cut file does not exist")
            print ("   Cut file is:  " + options.cut_file)
            print ("   JSON path is: " + line.split()[1])
            sys.exit() 
        else : 
            command = "cp " + line.split()[1] + " " + options.output_dir 
            print (command)
            os.system ( command ) 
            found_json = True

cut_file.close() 

#----------------------------------------------------------------
# Is the analysisClass.C file a symbolic link?
# If it is, what is the name of the real .C file?
#----------------------------------------------------------------
#
#code_name = ""
#if not os.path.islink ("src/analysisClass.C" ) :
#    print "ERROR.  src/analysisClass.C is not a symbolic link!" 
#    sys.exit() 
#else : 
#    code_name = os.path.realpath ( "src/analysisClass.C" ).split("/")[-1][:-2]

#----------------------------------------------------------------
# Loop over the input list and get a command for each file
#----------------------------------------------------------------

input_list = open ( options.input_list, "r" ) 
command_list = []

for line in input_list:
    if line.startswith('#'):
      continue
    dataset = line.strip().split("/")[-1][:-4]
    output_file_name = options.output_dir + "/" + options.code_name + "___" + dataset    
    command = "./" + executable
    command += " " + line.strip() + " " + options.cut_file + " " + options.tree_name + " " + output_file_name + " " + output_file_name
    command_list.append ( command ) 

#----------------------------------------------------------------
# Execute using all available CPUs.  Quit on Ctrl-C.
#----------------------------------------------------------------

pool = Pool ( ncores ) 
try:
    pool.map_async( printAndExecute, command_list ).get(99999999)
except KeyboardInterrupt:
    print ("\n\nCtrl-C detected: Bailing.") 
    pool.terminate()
    sys.exit(1) 
