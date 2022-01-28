# Seth I. Cooper
# June 2021
#
# setup: cern-get-sso-cookie -u https://cms-pdmv.cern.ch/mcm/ -o ~/private/prod-cookie.txt --krb --reprocess
# see, for example: https://github.com/cms-PdmV/mcm_scripts/blob/master/get_requests.py
# out of date, but has prereq info: https://twiki.cern.ch/twiki/bin/view/CMS/PdmVMcMScript#Pre_Requisite

import sys
from collections import OrderedDict
import argparse
from tabulate import tabulate
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM

parser = argparse.ArgumentParser("")
parser.add_argument("-d", "--dataset", type=str, default="", help="start dataset to look for, e.g., ww")
parser.add_argument("-l", "--datasetList", type=str, default="", help="file containing datasets to look for")
parser.add_argument("-c", "--campaign", type=str, default="", help="campaign to search in, e.g., RunIISummer20UL16*GEN*")
args = parser.parse_args()
dataset = args.dataset.lower()
datasetList = args.datasetList
memberOfCampaign = args.campaign
if len(dataset) < 1 and len(datasetList) < 1:
    parser.print_help()
    raise RuntimeError("Must specify dataset to look for")
if len(memberOfCampaign) < 1:
    parser.print_help()
    raise RuntimeError("Must specify campaign to look for")

# def GenerateCaseInsensitiveDatasetQuery(datasetName):
if datasetList != "":
    with open(datasetList, "r") as listFile:
        myDatasets = listFile.read().splitlines()
else:
    myDatasets = [dataset]

mcmFieldsToTitles = OrderedDict([("prepid", "Prep ID"), ("dataset_name", "Dataset name"), ("approval", "Approval"), ("status", "Status"),
                                ("member_of_campaign", "Member of campaign"), ("total_events", "Total events")])  # , ("output_dataset", "Output dataset")])

mcmFields = mcmFieldsToTitles.keys()
mcmTitles = mcmFieldsToTitles.values()

# myQuery = "member_of_campaign=RunIISummer20UL18GEN"
# myQueries = ["dataset_name=WW*&prepid=*20UL*GEN*"]
# myQueries.append("dataset_name=ww*&prepid=*20UL*GEN*")
# myQueries = ["member_of_campaign=RunIISummer20UL16*GEN*"]
myQueries = ["member_of_campaign="+memberOfCampaign]

mcm = McM(dev=False)

for myQuery in myQueries:
    matchingRequests = mcm.get('requests', query=myQuery)
    # print "[INFO] query='{}': got {} total requests".format(myQuery, len(matchingRequests))
    for dataset in myDatasets:
        # if r['pwg']!='SUS' : continue
        # if r['status']!='done': continue
        # print r['prepid']
        # print r
        # print "append result to table"
        table = []
        for r in matchingRequests:
            # if dataset in r["dataset_name"].lower():
            if r["dataset_name"].lower().startswith(dataset):
                table.append([r[key] for key in mcmFields])
        print "datasets starting with '{}' in query'{}':".format(dataset, myQuery)
        print tabulate(table, headers=mcmTitles, tablefmt="github", floatfmt=".1f")
        print

# print "Results for query='{}'".format(myQuery)
# print tabulate(table, headers=mcmTitles, tablefmt="github", floatfmt=".1f")
