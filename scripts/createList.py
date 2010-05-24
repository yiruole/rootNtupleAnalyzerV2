#!/usr/bin/env python

import os, sys, optparse, subprocess, string, re

# for files on Castor
def filelist_castor(inputDir, match):
    proc = subprocess.Popen( [ 'rfdir', inputDir ], stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    output = proc.communicate()[0]
    if proc.returncode != 0:
        print output
        sys.exit(1)

    filelist = {}

    for line in output.splitlines():
        filename = line.strip().split()[8]
        if( not re.search('.root$', filename) ):
            continue
        if ( match!=None and not re.search(match, filename) ):
            continue
        m = re.search('_\d+_\d+.root', filename)
        if( m ):
            dataset = re.split('_\d+_\d+.root', filename)[0]
            job = filename[m.start():].lstrip('_').rstrip('.root').split('_')
            if dataset not in filelist.keys():
                filelist[dataset] = {}
                if int(job[0]) not in filelist[dataset].keys():
                    filelist[dataset][int(job[0])] = [int(job[1])]
                else:
                    filelist[dataset][int(job[0])].append(int(job[1]))
            else:
                if int(job[0]) not in filelist[dataset].keys():
                    filelist[dataset][int(job[0])] = [int(job[1])]
                else:
                    filelist[dataset][int(job[0])].append(int(job[1]))
        else:
            dataset = re.split('_\d+.root', filename)[0]
            job = filename[re.search('_\d+.root', filename).start():].lstrip('_').rstrip('.root').split('_')
            if dataset not in filelist.keys():
                filelist[dataset] = {}
                if int(job[0]) not in filelist[dataset].keys():
                    filelist[dataset][int(job[0])] = []
            else:
                if int(job[0]) not in filelist[dataset].keys():
                    filelist[dataset][int(job[0])] = []

    return filelist


# for files on locally mounted disk space
def filelist_default(inputDir, match):
    if not os.path.isdir(inputDir):
        print ('%s is not a directory'%(inputDir))
        sys.exit(1)

    filelist = {}

    for filename in os.listdir(inputDir):
        if not os.path.isfile(os.path.join(inputDir,filename)):
            continue
        if( not re.search('.root$', filename) ):
            continue
        if ( match!=None and not re.search(match, filename) ):
            continue
        m = re.search('_\d+_\d+.root', filename)
        if( m ):
            dataset = re.split('_\d+_\d+.root', filename)[0]
            job = filename[m.start():].lstrip('_').rstrip('.root').split('_')
            if dataset not in filelist.keys():
                filelist[dataset] = {}
                if int(job[0]) not in filelist[dataset].keys():
                    filelist[dataset][int(job[0])] = [int(job[1])]
                else:
                    filelist[dataset][int(job[0])].append(int(job[1]))
            else:
                if int(job[0]) not in filelist[dataset].keys():
                    filelist[dataset][int(job[0])] = [int(job[1])]
                else:
                    filelist[dataset][int(job[0])].append(int(job[1]))
        else:
            dataset = re.split('_\d+.root', filename)[0]
            job = filename[re.search('_\d+.root', filename).start():].lstrip('_').rstrip('.root').split('_')
            if dataset not in filelist.keys():
                filelist[dataset] = {}
                if int(job[0]) not in filelist[dataset].keys():
                    filelist[dataset][int(job[0])] = []
            else:
                if int(job[0]) not in filelist[dataset].keys():
                    filelist[dataset][int(job[0])] = []

    return filelist


def write_inputlists(filelist, prefix, inputDir, outputDir):
    inputDir = inputDir.rstrip('/')+'/'
    outputDir = outputDir.rstrip('/')+'/'

    keys = filelist.keys()
    if( len(keys)==0 ):
        print 'No matching .root files found'
        sys.exit()

    os.system('mkdir -p '+outputDir)
    mainInputList = open(outputDir+'inputListAllCurrent.txt','w')

    keys.sort()
    for dataset in keys:
        inputListName = outputDir+dataset+'.txt'
        mainInputList.write(inputListName+'\n')
        inputList = open(inputListName,'w')
        for job in filelist[dataset].keys():
            if( len(filelist[dataset][job])>0 ):
                filename = (prefix+inputDir+dataset+'_%i_%i.root')%(job,max(filelist[dataset][job]))
            else:
                filename = (prefix+inputDir+dataset+'_%i.root')%(job)
            inputList.write(filename+'\n')


def main():
    parser = optparse.OptionParser(
        usage='Usage: %prog [-m MATCH] -i INPUTDIR -o OUTPUTDIR',
        description='Example: createList.py -i /castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-eejj_20100518_231412 -o /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config')
    parser.add_option( '-m', '--match', metavar='MATCH', action='store', help='Only files containing the MATCH string in their names will be considered' )
    parser.add_option( '-i', '--inputDir', metavar='INPUTDIR', action='store', help='Specifies the input directory containing .root files. Please use the full path. Castor directories are also supported' )
    parser.add_option( '-o', '--outputDir', metavar='OUTPUTDIR', action='store', help='Specifies the output directory where the .txt list files will be stored. Please use the full path' )

    (options, args) = parser.parse_args(args=None)

    if ( options.inputDir==None or options.outputDir==None ):
        print ("Options -i and -o are required\n")
        parser.print_help()
        sys.exit()

    filelist = {}

    if( re.search("^/castor/cern.ch/", options.inputDir) ):
        filelist = filelist_castor(options.inputDir, options.match)
        write_inputlists(filelist, 'rfio:', options.inputDir, options.outputDir)
    else:
        filelist = filelist_default(options.inputDir, options.match)
        write_inputlists(filelist, '', options.inputDir, options.outputDir)

    print 'Output files successfully created'


if __name__ == '__main__':
    main()
