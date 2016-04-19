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


def sortByNumber(x):
  r = re.compile('(\d+)')
  l = r.split(x)
  return [int(y) if y.isdigit() else y for y in l]


# NB: now use eos find to find the files in subdirectories, and (therefore) returns full paths
def make_filenamelist_eos(inputDir):
    #path = inputDir
    filenamelist = []
    #proc = subprocess.Popen( '/afs/cern.ch/project/eos/installation/pro/bin/eos.select ls ' + inputDir , shell=True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    proc = subprocess.Popen( '/afs/cern.ch/project/eos/installation/pro/bin/eos.select find -f ' + inputDir , shell=True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    # this gives the full path though
    output = proc.communicate()[0]
    if proc.returncode != 0:
        print output
        sys.exit(1)
    for line in output.splitlines():
        # ignore failed jobs
        if 'failed' in line:
          continue
        filename = os.path.split(line)[1]
        # if it's not a root file, forget about it
        if re.search('.root$', filename) is None:
            continue
        #print 'line=',line
        filenamelist.append(line)
        #filenamelist.append(filename)
        ##print 'added:',filenamelist[-1]
        #dirname=os.path.split(line)[0]
        #if path != dirname:
        #  path = dirname
        #  path+='/'

    return filenamelist

#FIXME now should return the full path
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

#FIXME now should return the full path
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
        #filenamelist = make_filenamelist_castor(inputDir)
        print 'ERROR: unsupported access protocol'
        exit(-1)
    elif( re.search("^/eos/cms/", inputDir) ):
        prefix = "root://cms-xrd-global.cern.ch/"
        filenamelist = make_filenamelist_eos(inputDir)
    elif( re.search("^/store/", inputDir) ):
        prefix = "root://cms-xrd-global.cern.ch/"
        filenamelist = make_filenamelist_eos(inputDir)
    else:
        #filenamelist = make_filenamelist_default(inputDir)
        print 'ERROR: unsupported access protocol'
        exit(-1)

    for fullfilepath in filenamelist:
        path = prefix+os.path.split(fullfilepath)[0]+'/'
        filename = os.path.split(fullfilepath)[1]
        if 'LQToCMu' in path or 'MuEnriched' in path:
            continue
        #print re.search('.root$',filename)
        if re.search('.root$', filename) is None:
            continue
        if ( match!=None and not re.search(match, filename) ):
            continue

        dataset = ''
        if '_reduced_skim' in filename:
            dataset = filename[0:filename.find('_reduced_skim')+len('_reduced_skim')]
        else:
            # try to find [number(s)].root
            m = re.search('_\d+.root', filename)
            dataset = filename[0:m.start()]
        # handle root files with same name, but actually different datasets
        # get the dataset info from the full path
        if 'amcatnloFXFX' in path and not 'amcatnloFXFX' in filename:
          dataset+='_amcatnloFXFX'
        elif 'madgraphMLM' in path and not 'madgraphMLM' in filename:
          dataset+='_madgraphMLM'
        elif 'pythia8' in path and not 'pythia8' in filename:
          dataset+='_pythia8'
        # for data, add secondary dataset name
        elif 'Run2015' in path and not 'Run2015' in filename:
          dataset+='__'
          dataset+=path[path.find('Run2015'):path.find('/',path.find('Run2015'))]

        if dataset not in filelist.keys():
            filelist[dataset] = []
            filelist[dataset].append(prefix+fullfilepath)
        else:
            filelist[dataset].append(prefix+fullfilepath)

    return


def write_inputlists(filelist, outputDir):
    outputDir = outputDir.rstrip('/')+'/'

    keys = filelist.keys()
    if( len(keys)==0 ):
        print 'No matching .root files found'
        sys.exit()

    os.system('mkdir -p '+outputDir)
    mainInputList = open(outputDir+'inputListAllCurrent.txt','w')

    for dataset in sorted(filelist.iterkeys()):
        files = filelist[dataset]
        inputListName = outputDir+dataset+'.txt'
        mainInputList.write(inputListName+'\n')
        inputList = open(inputListName,'w')
        filesSorted = sorted(files,key=sortByNumber)
        for path in filesSorted:
             inputList.write(path+'\n')
        inputList.close()

    mainInputList.close()

    return


def main():
    parser = optparse.OptionParser(
        usage='Usage: %prog [-m MATCH] -i INPUTDIR(S) -o OUTPUTDIR',
        description='Example: createList.py -i /castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-eejj_20100518_231412 -o /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config'
    )
    parser.add_option( '-m', '--match', metavar='MATCH', action='store', help='Only files containing the MATCH string in their names will be considered',default='' )
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
