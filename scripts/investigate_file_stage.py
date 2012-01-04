
import os, sys
import subprocess as sp

if len ( sys.argv ) != 2:
    print "Usage: python investigate_file_stage.py <file staging in castor>"
    sys.exit()

file = sys.argv[1]

print "Examining file: " + file

def get_stdout ( command ) :
    output = sp.Popen ( command, shell=True, stdout=sp.PIPE).communicate()[0].strip()
    return output 

#----------------------------------------------------------------
# Confirm that the file exists:
#----------------------------------------------------------------

print "  Confirming that the file exists...\t\t\t\t",

nsls_command = "nsls " + file 
nsls_output = get_stdout ( nsls_command ) 

if nsls_output == file : print "OK"
else : 
    print "\nERROR.  File does not exist:", file
    sys.exit()

#----------------------------------------------------------------
# Find out what the staging status is
#----------------------------------------------------------------

print "  Determining the staging status of the file...\t\t\t", 

stagerqry_command = "stager_qry -M " + file 
stagerqry_output  = get_stdout ( stagerqry_command ).split()[-1]

if stagerqry_output == "class)" : stagerqry_output = "<not staging>"

print stagerqry_output

if stagerqry_output != "STAGEIN":
    print "For now, only consider staging files (STAGEIN staging status)" 
    sys.exit()

#----------------------------------------------------------------
# Find out what the tape ID is
#----------------------------------------------------------------

print "  Determining the tape ID for this file...\t\t\t",
tapeid_command = "nsls -T " + file
tapeid_output = get_stdout ( tapeid_command ).split()[3]
print tapeid_output

#----------------------------------------------------------------
# Confirm that the tape exists
#----------------------------------------------------------------

print "  Confirming that the tape exists...\t\t\t\t",
tapeexist_command = "vmgrlisttape -V " + tapeid_output
tapeexist_output = get_stdout ( tapeexist_command ) 

if "No such tape" not in tapeexist_output :
    print "OK"
else: 
    print "TAPE DOES NOT EXIST!"
    print "\n\n*** Error summary: " 
    print "\n\nI am examining a file:\n"
    print file
    print "\n\nThe file is staging:\n" 
    print stagerqry_command 
    os.system ( stagerqry_command ) 
    print "\n\nThe tape it is stored on is: " + tapeid_output + "\n"
    print tapeid_command
    os.system ( tapeid_command ) 
    print "\n\nBut this tape does not exist:\n"
    print tapeexist_command 
    os.system ( tapeexist_command ) 
    print "\n\n"
    sys.exit()

#----------------------------------------------------------------
# Is the tape in the queues?
#----------------------------------------------------------------

print "  Confirming that this tape is queued or running...\t\t",

tapeq_command = "showqueues -x | grep " + tapeid_output
tapeq_output = get_stdout ( tapeq_command ).strip() 

queued = False
running = False
tapeq_status = ""

if tapeq_output != "": 
    tapeq_status = tapeq_output.split()[0]
    if ( tapeq_status == "Q" ) :
        print "OK, status = " + tapeq_status + " (queued)"
        queued = True
    elif ( tapeq_status == "DA" ) :
        print "OK, status = " + tapeq_status + " (running)"
        running = True

if not queued and not running:
    print "TAPE IS NOT QUEUED OR RUNNING!" 
    
    print "\n\n*** Error summary: " 
    print "\n\nI am examining a file:\n"
    print file
    print "\n\nThe file is staging:\n" 
    print stagerqry_command 
    os.system ( stagerqry_command ) 
    print "\n\nThe tape it is stored on is: " + tapeid_output + "\n"
    print tapeid_command
    os.system ( tapeid_command ) 
    print "\n\nThis tape exists:\n"
    print tapeexist_command 
    os.system ( tapeexist_command ) 
    print "\n\nBut it is not queued or running:\n"
    print tapeq_command
    os.system ( tapeq_command ) 
    print "\n\n"
    sys.exit()

if running:
    print "\n\nThis tape is running, and the file should be available soon!" 
    sys.exit()

time_queued = 0
if queued: time_queued = int(tapeq_output.split()[-1])

print "  Determining how long this tape has been queued...\t\t", time_queued, "seconds"

#----------------------------------------------------------------
# Get the tape type
#----------------------------------------------------------------

tape_type = tapeq_output.split()[1]
print "  Determining the tape type for this file...\t\t\t", tape_type

#----------------------------------------------------------------
# Find the other tapes of this type that are queued
#----------------------------------------------------------------

findtapes_command = "showqueues -x | grep " + tape_type 
findtapes_output  = get_stdout ( findtapes_command ).split("\n")

n_queued = 0
n_running = 0
longest_time_queued = -1

for tape in findtapes_output:
    status = tape.split()[0].strip()
    if status == "DA":
        n_running = n_running + 1
    if status == "Q":
        tmp_time_queued = int ( tape.split()[-1] ) 
        if tmp_time_queued > longest_time_queued: longest_time_queued = tmp_time_queued
        n_queued = n_queued + 1

if n_queued == 1:
    print "  Determining how many tapes of this type are queued...\t\t", n_queued, "(only this tape)"
    sys.exit()

wait_in_seconds = longest_time_queued - time_queued
seconds = longest_time_queued
minutes = seconds // 60
hours = minutes // 60

print "  Determining how many tapes of this type are queued...\t\t", n_queued, "tapes of type", tape_type, "are queued"
print "  Determining how many tapes of this type are running...\t" , n_running, "tapes of type", tape_type, "are running"
print "  Determining longest queue time for this tape type...\t\t", longest_time_queued, "seconds (" + "%02dh, %02dm, %02ds" % (hours, minutes % 60, seconds % 60) + " longer than this tape's queue time)"

