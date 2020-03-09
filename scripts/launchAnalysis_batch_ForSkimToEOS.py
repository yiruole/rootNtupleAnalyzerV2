#!/usr/bin/python2

from optparse import OptionParser
import os,sys, errno, time
import subprocess as sp

#--------------------------------------------------------------------------------
# Helper functions
#--------------------------------------------------------------------------------


def eos_isdir ( path ) : 
    command = "/usr/bin/eos ls " + path
    rfdir_stdout, rfdir_stderr = sp.Popen ( command , shell=True, stdout=sp.PIPE,stderr=sp.PIPE ).communicate()
    if    "No such file or directory" in rfdir_stderr: return False
    elif  rfdir_stderr == "" : return True
    else :
        print "Error: " 
        print "  command = " + command 
        print "  stdout  = " + stdout
        print "  stderr  = " + stderr 
        sys.exit()

def eos_mkdir ( path ):

    if not eos_isdir ( path ) :
        os.system ( "/usr/bin/eos mkdir -p " + path ) 
    else : 
        print "  EOS folder already exists: " + path

    if not eos_isdir ( path ) :
        print "Error: Could not make this EOS folder: " + path
        sys.exit()

    return path
    
def eos_getsize ( path ) : 
    nsls_stdout, nsls_stderr = sp.Popen ( "/usr/bin/eos ls -l " + path ,shell=True,stdout=sp.PIPE,stderr=sp.PIPE ).communicate()
    
    if "No such file or directory" in nsls_stderr : 
        print "Error: No such file in EOS: " + path
        sys.exit()
            
    file_size_in_bytes = int ( nsls_stdout.split()[-5] )
    
    return int(file_size_in_bytes)

def get_min_positive_integer_in_list ( list ) :
    min_positive_integer = 1e20
    for item in list:
        if item < min_positive_integer: min_positive_integer = int(item)
    return int(min_positive_integer)

def get_n_largest_file_sizes_in_bytes_in_inputlist ( n, inputlist ) :
    
    n_largest_file_sizes_in_bytes = []
    
    sublist_file = open ( inputlist, "r" )
    for sublist_line in sublist_file : 

        is_eos = False 
        file_name = sublist_line.strip()
        file_size_in_bytes = 0

        if file_name[:15] == "root://eoscms//" : 
            is_eos = True
            file_name = file_name[15:]
            file_size_in_bytes = int(eos_getsize ( file_name ) )
        else : 
            is_eos = False
            file_size_in_bytes = int(os.path.getsize ( file_name ) )

        if len ( n_largest_file_sizes_in_bytes ) < n : 
            n_largest_file_sizes_in_bytes.append ( file_size_in_bytes ) 
        elif get_min_positive_integer_in_list ( n_largest_file_sizes_in_bytes )  < file_size_in_bytes: 
            n_largest_file_sizes_in_bytes.append ( file_size_in_bytes ) 
            n_largest_file_sizes_in_bytes.remove ( int (get_min_positive_integer_in_list ( n_largest_file_sizes_in_bytes ) ) )

    sublist_file.close()

    return n_largest_file_sizes_in_bytes

def get_mean ( list ) :
    mean = 0
    for item in list:
        mean = mean + item 
    float_mean = float (mean) / float ( len ( list ) )
    return int ( float_mean ) 

def get_n_files ( inputlist ) : 
    sublist_file = open ( inputlist, "r" )
    files = [] 
    for sublist_line in sublist_file : 
        if ".root" in sublist_line: files.append ( sublist_line ) 
    sublist_file.close()
    return len ( files ) 

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
                  help="name of the root tree",
                  metavar="TREENAME")

parser.add_option("-c", "--cutfile", dest="cutfile",
                  help="name of the cut file",
                  metavar="CUTFILE")

parser.add_option("-j", "--ijobmax", dest="ijobmax",
                  help="max number of jobs, limited automatically to the number of files in inputlist",
                  metavar="IJOBMAX")

#http://batchdocs.web.cern.ch/batchdocs/local/submit.html
parser.add_option("-q", "--queue", dest="queue",
        help="name of the queue (choose among espresso (20 min), microcentury (1 hr), longlunch (2 hrs), workday (8 hrs), etc.; see http://batchdocs.web.cern.ch/batchdocs/local/submit.html)",
                  metavar="QUEUE")

parser.add_option("-w", "--wait", dest="wait",
                  help="number of seconds to wait between dataset submissions",
                  metavar="WAIT")

parser.add_option("-d", "--eosDir", dest="eosDir",
                  help="the EOS directory where skims are stored",
                  metavar="EOSDIR")

parser.add_option("-m", "--eosHost", dest="eosHost",
                  help="root:// MGM URL for the eos host for the skim output",
                  metavar="EOSHOST", default="root://eoscms.cern.ch/")

parser.add_option("-e", "--exe", dest="executable",
                  help="executable",
                  metavar="EXECUTABLE", default="main")

parser.add_option("-r", "--reducedSkim", dest="reducedSkim",
                  help="is this a reduced skim?",
                  metavar="REDUCEDSKIM",default=False,action="store_true")



(options, args) = parser.parse_args()

if ( not options.inputlist 
     or not options.outputDir
     or not options.treeName 
     or not options.cutfile 
     or not options.ijobmax 
     or not options.queue 
     #or not options.wait 
     or not options.eosDir ) : 
    print 'One of [outputDir,treeName,cutfile,ijobmax,queue,eosDir] not specified'
    parser.print_help()
    sys.exit()

if 'eos/user' in options.eosDir:
    options.eosHost = 'root://eosuser.cern.ch/'
# set eos mgm url
print 'INFO: Using',options.eosHost,'as eosHost'
os.environ['EOS_MGM_URL'] = options.eosHost

#--------------------------------------------------------------------------------
# Make the EOS dir
#--------------------------------------------------------------------------------

print "Making the EOS output directory...",

eosPath = eos_mkdir ( options.eosDir ) 

print "... done"
    
#--------------------------------------------------------------------------------
# Make the output directory
#--------------------------------------------------------------------------------

print "Making the local output directory...",

if not os.path.isdir ( options.outputDir ) : 
    os.system ( "mkdir -p " + options.outputDir )

if not os.path.isdir ( options.outputDir ) : 
    print "Error: I can't make this folder: " + options.outputDir 
    sys.exit() 

print "... done "

#--------------------------------------------------------------------------------
# Look for the cut file.  If it exists, move it to the output directory
#--------------------------------------------------------------------------------

print "Moving the cutfile to the local output directory...",

if not os.path.isfile ( options.cutfile ) : 
    print "Error: No cut file here: " + options.cutfile 
    sys.exit() 
else : 
    os.system ( "cp " + options.cutfile + " " + options.outputDir + "/" )

print "... done "

#--------------------------------------------------------------------------------
# Look for the exe file.  If it exists, move it to the output directory
#--------------------------------------------------------------------------------


if os.path.isfile ( options.executable ) : 
    print "Moving the exe to the local output directory...",
    os.system ( "cp " + options.executable + " " + options.outputDir + "/" )
    print "... done "
else : 
    print "Warning: No file here: '" + options.executable + "'" + "; proceeding anyway"
    #sys.exit() 



#--------------------------------------------------------------------------------
# Look for the inputList file
#--------------------------------------------------------------------------------

print "Moving the inputlist to the local output directory...",

if not os.path.isfile ( options.inputlist ) : 
    print "Error: No input list here: " + options.inputlist 
    sys.exit() 
else : 
    os.system ( "cp " + options.inputlist + " " + options.outputDir + "/" )

print "... done "

#--------------------------------------------------------------------------------
# Get JSON file from cut file and copy it to the output directory
#--------------------------------------------------------------------------------

print "Moving the JSON file to the local output directory...",

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
            jsonFile = options.outputDir+'/'+json_file.split('/')[-1]

print "... done "
                   
#--------------------------------------------------------------------------------
# Check if path is a link
#--------------------------------------------------------------------------------

print "Checking the link to analysisClass.C...",

if not os.path.islink ( "src/analysisClass.C" ) :
    print
    print "Error: src/analysisClass.C is not a symbolic link"
    sys.exit()
code_name = os.readlink ( "./src/analysisClass.C" ).split("/")[-1].split(".C")[0]

print "... done"

#--------------------------------------------------------------------------------
# Launch
#--------------------------------------------------------------------------------

print "Launching jobs!"

inputlist_file = file ( options.inputlist,"r" )

total_jobs = 0

failedCommands = list()

for line in inputlist_file: 
    if not len(line.strip()) > 0:
        continue
    if line.startswith('#'):
        continue

    dataset = line.strip().split("/")[-1].split(".txt")[0]
    
    sublist = line.strip()

    # n_largest_file_sizes_in_bytes = get_n_largest_file_sizes_in_bytes_in_inputlist ( 5, sublist )
    # n_files = get_n_files ( sublist ) 
    # n_largest_file_sizes_in_bytes_mean = get_mean ( n_largest_file_sizes_in_bytes  )
    # effective_size = int(n_largest_file_sizes_in_bytes_mean * n_files)
    # suggested_jobs = int(effective_size / 10000000000) + 1 
    # jobs_to_submit = min ( suggested_jobs, int(options.ijobmax))
    jobs_to_submit = int(options.ijobmax)
    
    # print sublist
    # print "mean size        =", n_largest_file_sizes_in_bytes_mean
    # print "effective size   =", effective_size
    # print "n files          =", n_files
    # print "n jobs suggested =", suggested_jobs
    # print "n jobs allowed   =", options.ijobmax
    # print "n jobs to submit =", jobs_to_submit
    
    total_jobs = total_jobs + jobs_to_submit

    command = "./scripts/submit_batch_ForSkimToEOS.py"
    command = command + " -i " + line.strip() 
    #command = command + " -c " + options.cutfile 
    command = command + " -c " + options.outputDir+'/'+options.cutfile.split('/')[-1]
    command = command + " -t " + options.treeName 
    command = command + " -o " + options.outputDir + "/" + code_name + "___" + dataset
    command = command + " -n " + str(jobs_to_submit)
    command = command + " -q " + options.queue
    command = command + " -d " + eosPath
    #command = command + " -e " + os.path.realpath(options.executable)
    command = command + " -e " + options.outputDir+'/'+options.executable.split('/')[-1]
    command = command + " -m " + options.eosHost
    command = command + " -j " + os.path.realpath(jsonFile)
    if options.reducedSkim:
        command = command + " -r "
    
    print command
    
    #os.system  ( command ) 
    exitCode = os.WEXITSTATUS(os.system( command ))
    if exitCode != 0:
        print 'Failed submitting jobs for this dataset; add to failedCommands list'
        failedCommands.append(command)
    if options.wait is not None:
        time.sleep (  float( options.wait ) ) 

inputlist_file.close() 

# FIXME this is not the correct number
print "submitted a _maximum_ of jobs =", total_jobs

if len(failedCommands) > 0:
    print 'list of failed commands:'
    for cmd in failedCommands:
        print cmd

