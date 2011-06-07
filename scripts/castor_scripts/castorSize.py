#!/usr/bin/python

import sys
import subprocess
import os

#--------------------------------------------------------------------------------------
# Define functions
#--------------------------------------------------------------------------------------

def printUsage() : 
    print "Usage: "
    print "  python castorPrune.py <folder in castor> " 
    sys.exit() 

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
    if root_file[-5:] != ".root" : root_files.remove (root_file)

if len ( root_files ) == 0 : 
    print "No root files in folder "+castor_folder
    printUsage()

#--------------------------------------------------------------------------------------
# Get the sizes 
#--------------------------------------------------------------------------------------

total_size_in_bytes = 0

for i,root_file in enumerate(root_files):
    print "Analyzing file # " + str( i + 1 ) + " / " + str ( len ( root_files ) )
    command = "nsls -l "+ castor_folder + "/" + root_file 
    file_size_in_bytes = int ( subprocess.Popen ( command , shell=True, stdout=subprocess.PIPE ).communicate()[0].split()[4] ) 
    total_size_in_bytes = total_size_in_bytes + file_size_in_bytes

total_size_in_gigabytes_bin = float ( total_size_in_bytes ) / 1073741824.0
total_size_in_gigabytes_dec = float ( total_size_in_bytes ) / 1000000000.0

print "Total size = " + str ( total_size_in_bytes ) + " Bytes " 
print "Total size = " + str ( '%.2f' % total_size_in_gigabytes_bin ) + " GB [bin]"
print "Total size = " + str ( '%.2f' % total_size_in_gigabytes_dec ) + " GB [dec]"
