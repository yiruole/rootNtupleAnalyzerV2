from optparse import OptionParser
import os,sys, errno, time
import subprocess as sp

#--------------------------------------------------------------------------------
# Helper functions
#--------------------------------------------------------------------------------

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            print "  Local folder already exists: " + path
            pass
        else: raise

def castor_isdir ( path ) : 
    command = "rfdir " + path
    rfdir_stdout, rfdir_stderr = sp.Popen ( command , shell=True, stdout=sp.PIPE,stderr=sp.PIPE ).communicate()
    if    "No such file or directory" in rfdir_stderr: return False
    elif  rfdir_stderr == "" : return True
    else :
        print "Error: " 
        print "  command = " + command 
        print "  stdout  = " + stdout
        print "  stderr  = " + stderr 
        sys.exit()

def castor_mkdir ( path ):

    currentPath = os.getenv ( "CASTOR_HOME" )
    fullCastorPath = currentPath + "/" + path
    
    if not castor_isdir ( fullCastorPath ) :
        os.system ( "rfmkdir -p " + fullCastorPath ) 
    else : 
        print "  CASTOR folder already exists: " + fullCastorPath

    if not castor_isdir ( fullCastorPath ) :
        print "Error: Could not make this CASTOR folder: " + fullCastorPath
        sys.exit()

    return fullCastorPath
    
def castor_getsize ( path ) : 
    nsls_stdout, nsls_stderr = sp.Popen ( "nsls -l " + path ,shell=True,stdout=sp.PIPE,stderr=sp.PIPE ).communicate()
    
    if "No such file or directory" in nsls_stderr : 
        print "Error: No such file in castor: " + path
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

        is_castor = False 
        file_name = sublist_line.strip()
        file_size_in_bytes = 0

        if file_name[:5] == "rfio:" : 
            is_castor = True
            file_name = file_name[5:]
            file_size_in_bytes = int(castor_getsize ( file_name ) )
        else : 
            is_castor = False
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

usage = "usage: %prog [options] \nExample: python ./scripts/launchAnalysis_batch_ForSkimToCastor.py <options>"

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

parser.add_option("-q", "--queue", dest="queue",
                  help="name of the queue (choose among cmst3 8nm 1nh 8nh 1nd 1nw)",
                  metavar="QUEUE")

parser.add_option("-w", "--wait", dest="wait",
                  help="number of seconds to wait between dataset submissions",
                  metavar="WAIT")

parser.add_option("-d", "--castorDir", dest="castorDir",
                  help="the CASTOR directory where skims are stored",
                  metavar="CASTORDIR")


(options, args) = parser.parse_args()

if ( not options.inputlist 
     or not options.outputDir
     or not options.treeName 
     or not options.cutfile 
     or not options.ijobmax 
     or not options.queue 
     or not options.wait 
     or not options.castorDir ) : 
    parser.print_help()
    sys.exit()

#--------------------------------------------------------------------------------
# Make the CASTOR dir
#--------------------------------------------------------------------------------

print "Making the CASTOR output directory..."

fullCastorPath = castor_mkdir ( options.castorDir ) 

print "... done"
    
#--------------------------------------------------------------------------------
# Make the output directory
#--------------------------------------------------------------------------------

print "Making the local output directory..."

mkdir_p ( options.outputDir ) 

if not os.path.isdir ( options.outputDir ) : 
    print "Error: I can't make this folder: " + options.outputDir 
    sys.exit() 

print "... done "

#--------------------------------------------------------------------------------
# Look for the cut file.  If it exists, move it to the output directory
#--------------------------------------------------------------------------------

print "Moving the cutfile to the local output directory..."

if not os.path.isfile ( options.cutfile ) : 
    print "Error: No cut file here: " + options.cutfile 
    sys.exit() 
else : 
    os.system ( "cp " + options.cutfile + " " + options.outputDir + "/" )

print "... done "

#--------------------------------------------------------------------------------
# Look for the inputList file
#--------------------------------------------------------------------------------

print "Moving the inputlist to the local output directory..."

if not os.path.isfile ( options.inputlist ) : 
    print "Error: No input list here: " + options.inputlist 
    sys.exit() 
else : 
    os.system ( "cp " + options.inputlist + " " + options.outputDir + "/" )

print "... done "

#--------------------------------------------------------------------------------
# Get JSON file from cut file and copy it to the output directory
#--------------------------------------------------------------------------------

print "Moving the JSON file to the local output directory..."

cutfile = open ( options.cutfile , "r" )
found_json = False 
for line in cutfile:
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

print "... done "
                   
#--------------------------------------------------------------------------------
# Check if path is a link
#--------------------------------------------------------------------------------

print "Checking the link to analysisClass.C..."

if not os.path.islink ( "src/analysisClass.C" ) :
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

for line in inputlist_file: 
    dataset = line.strip().split("/")[-1].split(".txt")[0]
    
    sublist = line.strip()

    n_largest_file_sizes_in_bytes = get_n_largest_file_sizes_in_bytes_in_inputlist ( 5, sublist )
    n_files = get_n_files ( sublist ) 
    n_largest_file_sizes_in_bytes_mean = get_mean ( n_largest_file_sizes_in_bytes  )
    effective_size = int(n_largest_file_sizes_in_bytes_mean * n_files)
    suggested_jobs = int(effective_size / 10000000000) + 1 
    jobs_to_submit = min ( suggested_jobs, int(options.ijobmax))
    
    print sublist
    print "mean size        =", n_largest_file_sizes_in_bytes_mean
    print "effective size   =", effective_size
    print "n files          =", n_files
    print "n jobs suggested =", suggested_jobs
    print "n jobs allowed   =", options.ijobmax
    print "n jobs to submit =", jobs_to_submit
    
    total_jobs = total_jobs + jobs_to_submit

    command = "./scripts/submit_batch_ForSkimToCastor.py"
    command = command + " -i " + line.strip() 
    command = command + " -c " + options.cutfile 
    command = command + " -t " + options.treeName 
    command = command + " -o " + options.outputDir + "/" + code_name + "___" + dataset
    command = command + " -n " + str(jobs_to_submit)
    command = command + " -q " + options.queue
    command = command + " -d " + fullCastorPath
    
    print command
    
    os.system  ( command ) 
    time.sleep (  float( options.wait ) ) 

inputlist_file.close() 

print "total jobs =", total_jobs
