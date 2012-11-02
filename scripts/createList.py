#!/usr/bin/env python

import os, sys, optparse, subprocess, string, re

# needed for having multiple arguments per option flag
def cb(option, opt_str, value, parser):
    args=[]
    for arg in parser.rargs:
        if arg[0] != "-":
            args.append(arg)
        else:
            del parser.rargs[:len(args)]
            break
    if len(args)==0:
        args=None
    if getattr(parser.values, option.dest):
        args.extend(getattr(parser.values, option.dest))
    setattr(parser.values, option.dest, args)


def unique(keys):
    unique = []
    for i in keys:
        if i not in unique:
            unique.append(i)
    return unique



def make_filenamelist_eos(inputDir):
    filenamelist = []
    proc = subprocess.Popen( '/afs/cern.ch/project/eos/installation/0.2.5/bin/eos.select ls ' + inputDir , shell=True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    output = proc.communicate()[0]
    if proc.returncode != 0:
        print output
        sys.exit(1)
    for line in output.splitlines():
        filenamelist.append(line.strip())

    return filenamelist

def make_filenamelist_castor(inputDir):
    filenamelist = []
    proc = subprocess.Popen( [ 'rfdir', inputDir ], stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    output = proc.communicate()[0]
    if proc.returncode != 0:
        print output
        sys.exit(1)
    for line in output.splitlines():
        filenamelist.append(line.strip().split()[8])

    return filenamelist

def make_filenamelist_default(inputDir):
    if not os.path.isdir(inputDir):
        print ('%s is not a directory'%(inputDir))
        sys.exit(1)

    filenamelist = []
    for filename in os.listdir(inputDir):
        if not os.path.isfile(os.path.join(inputDir,filename)):
            continue
        filenamelist.append(filename)

    return filenamelist


def process_input_dir(inputDir, match, filelist):
    inputDir = inputDir.rstrip('/')+'/'
    prefix = ''
    filenamelist = []

    if( re.search("^/castor/cern.ch/", inputDir) ):
        prefix = 'rfio:'
        filenamelist = make_filenamelist_castor(inputDir)
    elif( re.search("^/eos/cms/", inputDir) ):
        prefix = "root://eoscms/"
        filenamelist = make_filenamelist_eos(inputDir)
    else:
        filenamelist = make_filenamelist_default(inputDir)

    path = prefix+inputDir;

    for filename in filenamelist:
        if( not re.search('.root$', filename) ):
            continue
        if ( match!=None and not re.search(match, filename) ):
            continue
        m1 = re.search('_\d+_\d+_\w+.root', filename)
        m2 = re.search('_\d+_\d+.root', filename)
        if( m1 ):
            dataset = re.split('_\d+_\d+_\w+.root', filename)[0]
            job = filename[m1.start():].lstrip('_').replace('.root','').split('_')
            if dataset not in filelist.keys():
                filelist[dataset] = {}
                filelist[dataset][path] = {}
                filelist[dataset][path][int(job[0])] = [[int(job[1])],[job[2]]]
            else:
                if path not in filelist[dataset].keys():
                    filelist[dataset][path] = {}
                    filelist[dataset][path][int(job[0])] = [[int(job[1])],[job[2]]]
                else:
                    if int(job[0]) not in filelist[dataset][path].keys():
                        filelist[dataset][path][int(job[0])] = [[int(job[1])],[job[2]]]
                    else:
                        filelist[dataset][path][int(job[0])][0].append(int(job[1]))
                        filelist[dataset][path][int(job[0])][1].append(job[2])
        elif( m2 ):
            dataset = re.split('_\d+_\d+.root', filename)[0]
            job = filename[m2.start():].lstrip('_').replace('.root','').split('_')
            if dataset not in filelist.keys():
                filelist[dataset] = {}
                filelist[dataset][path] = {}
                filelist[dataset][path][int(job[0])] = [[int(job[1])],[]]
            else:
                if path not in filelist[dataset].keys():
                    filelist[dataset][path] = {}
                    filelist[dataset][path][int(job[0])] = [[int(job[1])],[]]
                else:
                    if int(job[0]) not in filelist[dataset][path].keys():
                        filelist[dataset][path][int(job[0])] = [[int(job[1])],[]]
                    else:
                        filelist[dataset][path][int(job[0])][0].append(int(job[1]))
        else:
            dataset = re.split('_\d+.root', filename)[0]
            job = filename[re.search('_\d+.root', filename).start():].lstrip('_').replace('.root','').split('_')
            if dataset not in filelist.keys():
                filelist[dataset] = {}
                filelist[dataset][path] = {}
                filelist[dataset][path][int(job[0])] = [[],[]]
            else:
                if path not in filelist[dataset].keys():
                    filelist[dataset][path] = {}
                    filelist[dataset][path][int(job[0])] = [[],[]]
                else:
                    if int(job[0]) not in filelist[dataset][path].keys():
                        filelist[dataset][path][int(job[0])] = [[],[]]

    return


def write_inputlists(filelist, outputDir):
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
        for path in filelist[dataset].keys():
            for job in filelist[dataset][path].keys():
                if( len(filelist[dataset][path][job][0])>0 ):
                    if( len(filelist[dataset][path][job][1])>0 ):
                        filename = (path+dataset+'_%i_%i_%s.root')%(job,max(filelist[dataset][path][job][0]),filelist[dataset][path][job][1][filelist[dataset][path][job][0].index(max(filelist[dataset][path][job][0]))])
                    else:
                        filename = (path+dataset+'_%i_%i.root')%(job,max(filelist[dataset][path][job][0]))
                else:
                    filename = (path+dataset+'_%i.root')%(job)
                inputList.write(filename+'\n')
        inputList.close()
    mainInputList.close()

    return


def main():
    parser = optparse.OptionParser(
        usage='Usage: %prog [-m MATCH] -i INPUTDIR(S) -o OUTPUTDIR',
        description='Example: createList.py -i /castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-eejj_20100518_231412 -o /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config'
    )
    parser.add_option( '-m', '--match', metavar='MATCH', action='store', help='Only files containing the MATCH string in their names will be considered' )
    parser.add_option( '-i', '--inputDirs', metavar='INPUTDIR(S)', action="callback", callback=cb, dest="inputDirs", help='Specifies the input directory (or directories separated by space) containing .root files. Please use the full path. Castor directories are also supported' )
    parser.add_option( '-o', '--outputDir', metavar='OUTPUTDIR', action='store', help='Specifies the output directory where the .txt list files will be stored. Please use the full path' )

    (options, args) = parser.parse_args(args=None)

    if ( options.inputDirs==None or options.outputDir==None ):
        print ("\nOptions -i and -o are required\n")
        parser.print_help()
        sys.exit()

    filelist = {}

    inputDirs = unique(options.inputDirs)

    for inputDir in inputDirs:
        process_input_dir(inputDir, options.match, filelist)

    write_inputlists(filelist, options.outputDir)

    print 'Output files successfully created'
    sys.exit()


if __name__ == '__main__':
    main()
