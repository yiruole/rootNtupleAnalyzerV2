#!/usr/bin/env python

#logFile = 'lq500_rskSEleE.log'
logFile = 'stop500_ctau100_rskSEleE.log'

nPassingElectrons = 0
nFailingElectrons = 0
failedCutCounts = dict()
failedCutN1Counts = dict()

with open(logFile,'r') as f:
    insideEleBlock = False
    for line in f:
        # start of electron ID info block
        if 'Electron' in line:
            if 'PASS' in line:
                nPassingElectrons+=1
            else:
                nFailingElectrons+=1
                insideEleBlock = True
                failedCutList = []
        elif insideEleBlock:
            split = line.split()
            failed = True if 'FAIL' in split[0] else False
            cutName = split[1]
            if failed:
                if not cutName in failedCutCounts.keys():
                    failedCutCounts[cutName] = 0
                failedCutCounts[cutName]+=1
                failedCutList.append(cutName)
            if cutName=='caloIsolation': # last cut in list
                if len(failedCutList)==1:
                    cutName = failedCutList[0]
                    if not cutName in failedCutN1Counts.keys():
                        failedCutN1Counts[cutName] = 0
                    failedCutN1Counts[cutName]+=1
                insideEleBlock = False


print 'logFile:',logFile
print 'nPassingElectrons:',nPassingElectrons
print 'nFailingElectrons:',nFailingElectrons
print 'failedCutCounts:',failedCutCounts
print 'failedCutN-1Counts:',failedCutN1Counts
