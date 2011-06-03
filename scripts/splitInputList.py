#!/usr/bin/python

#----------------------------------------------------------------------------
# Do imports
#----------------------------------------------------------------------------

import sys, os, math

#----------------------------------------------------------------------------
# Define functions
#----------------------------------------------------------------------------

def printUsage(): 
    print "Usage: " 
    print "./splitInputList <some input list>"
    sys.exit() 

#----------------------------------------------------------------------------
# Make sure the input makes sense
#----------------------------------------------------------------------------

if len ( sys.argv ) !=2 : 
    print "ERROR: Give a .txt file containing a list of .root files"
    printUsage() 

old_input_list_path = sys.argv[1]

if not os.path.exists ( old_input_list_path ) : 
    print "ERROR: \"" + old_input_list_path + "\" does not exist!"
    printUsage() 

#----------------------------------------------------------------------------
# Open the .txt and get a list of .root files
#----------------------------------------------------------------------------
 
old_input_list_file = open ( old_input_list_path, "r" ) 

all_files = []
for line in old_input_list_file: 
    if ".root" in line : all_files.append( line[:-1] ) 
n_total_files = len ( all_files ) 

old_input_list_file.close() 

#----------------------------------------------------------------------------
# Tell the user what's going on, and ask how many splits to make
#----------------------------------------------------------------------------

print "You have " + str(n_total_files) + " total files in the original dataset."
number_of_splits = int ( raw_input(  "Into how many pieces do you want to split the original dataset? " ) )

#----------------------------------------------------------------------------
# Split the list of files into lists of "splits"
#----------------------------------------------------------------------------

list_of_splits = []
n_files_in_most_splits = int ( math.ceil ( float ( n_total_files ) / float ( number_of_splits ) ) )

for i in range ( 0, number_of_splits - 1 ) :
    list_to_append = all_files[ i * n_files_in_most_splits : (i+1) * n_files_in_most_splits ]
    if len ( list_to_append ) != 0 :  list_of_splits.append ( list_to_append )

list_to_append = all_files[ (number_of_splits - 1) * n_files_in_most_splits : ]
if ( len ( list_to_append ) != 0 ) : list_of_splits.append ( list_to_append )

#----------------------------------------------------------------------------
# Write those new lists of splits to a new file
#----------------------------------------------------------------------------

for i,split in enumerate ( list_of_splits ) :
    new_input_list_path = old_input_list_path[:-4] + "_" + str ( i + 1 ) + ".txt" 
    new_input_list_file = open ( new_input_list_path, "w" ) 
    for file in split : 
        new_input_list_file.write ( file + "\n" ) 
    new_input_list_file.close()

    print "Wrote input list: " + new_input_list_path + " with " + str ( len ( split ) )  + " .root files in it"

print "... Done!" 
