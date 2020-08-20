#!/usr/bin/env python2

import operator
from prettytable import PrettyTable

filename = "/tmp/scooper/treeLogTest.txt"
branchNameToSizeDict = {}
with open(filename, "r") as theFile:
    currentBranchName = ""
    for line in theFile:
        if "Br " in line:
            currentBranchName = line.split(":")[1].strip()
        if "File Size  = " in line:
            size = int(line.split()[-2])  # bytes
            branchNameToSizeDict[currentBranchName] = size/1024.0/1024.0  # MB

# sort
sortedList = sorted(branchNameToSizeDict.items(), key=operator.itemgetter(1), reverse=True)
totalSize = sum([thisSize for name, thisSize in sortedList])
sortedList = sortedList[:100]  # limit number of items to 100

# print
print "total file size:", totalSize, "(MB)"
print "space used by 100 largest branches:"
t = PrettyTable(["Branch name", "size (MB)", "% of total"])
t.float_format = "4.3"
t.align["Branch name"] = "l"
t.align["Size"] = "r"
for brNameSize in sortedList:
    t.add_row([brNameSize[0], brNameSize[1], brNameSize[1]/(1.0*totalSize)])
print t
