from optparse import OptionParser
import sys

from dbs.apis.dbsClient import DbsApi
from dbs.exceptions.dbsClientException import dbsClientException


def GetParents(dataset):
    try:
        api = DbsApi(url = 'https://cmsweb.cern.ch/dbs/prod/global/DBSReader/')
        parents = api.listDatasetParents(dataset=dataset)
    except dbsClientException, ex:
        print "Caught API Exception %s: %s "  % (ex.name,ex)
        exit(-1)
    return parents

def CheckForMultipleParents(parents):
    if len(parents) == 1:
        return True
    elif len(parents) > 1:
        print 'ERROR: got multiple parents for dataset:'
        for parent in parents:
            print parent['parent_dataset']
        print 'ERROR: not sure how to continue.'
        return False
    else:
        print 'ERROR: got no parents for dataset:'
        for parent in parents:
            print parent['parent_dataset']
        print 'ERROR: not sure how to continue.'
        return False


parser = OptionParser()

parser.add_option(
    "-d",
    "--datasets",
    dest="datasets",
    help="datasets to check (comma-separated list)",
    metavar="DATASETS",
    default=None,
)
parser.add_option(
    "-f",
    "--file",
    dest="filename",
    help="filename containing datasets to check",
    metavar="FILENAME",
    default=None,
)

(options, args) = parser.parse_args()

if options.datasets is None and options.filename is None:
    print 'ERROR: must specify dataset with -d or --dataset or filename with -f or --file'
    exit(-1)

if options.datasets is not None:
    datasetpath = options.datasets
    #print datasetpath
    if ',' in datasetpath:
        datasetList = datasetpath.split(',')
    else:
        datasetList = [datasetpath]
else:
    datasetList = []
    with open(options.filename,"r") as theFile:
        for line in theFile:
            split = line.split()
            if len(split) <= 0:
                continue
            if "#" in split[0]:  # skip comments
                # print 'found comment:',line
                continue
            dataset = split[0]
            datasetList.append(dataset)

for dataset in datasetList:
    # print 'Examining dataset:',dataset,
    print dataset,
    parents = GetParents(dataset)
    if not CheckForMultipleParents(parents):
        continue
    
    parentDataset = parents[0]['parent_dataset']
    # print '\tparent dataset='+parentDataset
    
    nextParents = GetParents(parentDataset)
    if not CheckForMultipleParents(nextParents):
        continue
    
    parentOfParent = nextParents[0]['parent_dataset']
    # print '\tparent of parent dataset=',parentOfParent
    
    if 'PU2017' in parentOfParent:
        print '\tPU OK'
    else:
        print '\tWrong PU was used in AOD dataset!'

