import sys, os

def printUsage(): 
    print "Usage: " 
    print "./removeFilesFromList.py <list of files>"
    sys.exit() 

if len ( sys.argv ) == 1 : 
    print "ERROR: Give a list of files."
    printUsage() 

raw_files = sys.argv[1:]
txt_files = []

print raw_files

for raw_file in raw_files:
    if not os.path.exists ( raw_file ) :
        print "WARNING: " + raw_file + " not found ... skipping" 
        continue
    if raw_file[-4:] != ".txt" :
        print "WARNING: " +raw_file + " is not a .txt file ... skipping"
        continue
    txt_files.append ( raw_file ) 

print "I will skim these txt files: " 
for txt_file in txt_files:
    print txt_file

keep_every_nth_file = int ( raw_input ( "I will keep every nth .root file, where n = " )  ) 

for txt_file in txt_files:
    old_file_name = txt_file
    new_file_name = txt_file[:-4] + "_skimmed.txt"

    old_file = open ( txt_file    , "r" )
    new_file = open ( new_file_name, "w") 

    iLine = 0

    for old_line in old_file:
        if iLine % keep_every_nth_file == 0: 
            new_file.write ( old_line ) 
        iLine = iLine + 1
    
    new_file.close()
    old_file.close()

    if not os.path.exists ( new_file_name ) :
        print "Did not create new file: " + new_file_name 
        sys.exit() 

    if not os.path.exists ( old_file_name ) :
        print "Can not find old file: " + old_file_name 
        sys.exit() 

    command1 = "mv "+ old_file_name + " " + txt_file[:-4] + "_old.txt" 
    command2 = "mv "+ new_file_name + " " + old_file_name 

    print command1
    os.system ( command1 )

    print command2
    os.system ( command2 ) 
        
