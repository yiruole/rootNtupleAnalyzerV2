#!/usr/bin/env python

import os
import sys
from ROOT import *

hltTreeEntryNumberDict = {}
ntupleTreeEntryNumberDict = {}

def FillDict(dict,tree,runBranch,lsBranch,lsLeaf,evBranch):
  for entry in range(0,tree.GetEntries()):
    runBranch.GetEntry(entry)
    lsBranch.GetEntry(entry)
    ls = lsLeaf.GetValue()
    evBranch.GetEntry(entry)
    dict[tree.run,ls,tree.event] = entry
    #print 'fill [',tree.run,',',ls,',',tree.event,'] =',entry


##################
# RUN
##################
# set filenames
ntupleFileName = '/afs/cern.ch/user/s/scooper/work/private/cmssw/723p1/LQRootTuple723p1/src/Leptoquarks/RootTupleMakerV2/test/testNoStatus70sKeep50GenParticles_LQ1_M300_13TeV_pythia8_phys14_MiniAOD_noPU.root'
hltNtupleFileName = '/afs/cern.ch/user/s/scooper/work/private/cmssw/741/ReRunHLTLQSignals741/src/Leptoquarks/RootTupleMakerV2/test/file.root'
combinedFileName = 'lq1_m300_741HLT_combinedNtuple.root'
# which branches to keep?
#branchNameToKeepPrefix = '741'
# keep all
branchNameToKeepPrefix = ''
treeName = 'rootTupleTree/tree'

# open files
ntupleFile=TFile(ntupleFileName)
ntupleTree=ntupleFile.Get(treeName)

# get the trees
hltNtupleFile=TFile(hltNtupleFileName)
hltNtupleTree=hltNtupleFile.Get(treeName)

# make a new file
combinedNtupleFile = TFile(combinedFileName,'recreate')
combinedTreeDir = combinedNtupleFile.mkdir('rootTupleTree')
combinedTreeDir.cd()
#combinedNtupleTree = ntupleTree.CloneTree(0)
newNtupleTree = ntupleTree.CloneTree()
del ntupleTree
ntupleFile.Close()
ntupleTree = newNtupleTree
#newNtupleTree.Write()

newHLTntupleTree = hltNtupleTree.CloneTree(0)
newHLTntupleTree.SetName('newHltTree')

## get list of branches to add
## by default, don't add branches that have exactly the same name in the non-HLT ntuple
#branchesList = ntupleTree.GetListOfBranches()
#branchesNamesList = [branch.GetName() for branch in branchesList]
#hltBranchesList = hltNtupleTree.GetListOfBranches()
##branchesToAdd = TObjArray()
##for branch in hltBranchesList:
##  if len(branchNameToKeepPrefix) > 0 and not branchNameToKeepPrefix in branch.GetName():
##    continue
##  if branch.GetName() in branchesNamesList:
##    continue
##  branchesToAdd.Add(branch)
##  print 'add branch:',branch.GetName(),'to combined tree'
### make the new branches, 1 per hlt branch
##ntupleTree.Branch(branchesToAdd,1)
#newBranchesList = []
#addressObjList = []
#for branch in hltBranchesList:
#  if len(branchNameToKeepPrefix) > 0 and not branchNameToKeepPrefix in branch.GetName():
#    continue
#  if branch.GetName() in branchesNamesList:
#    continue
#  #newBranchesList.append(branch.Clone())
#  #SetAddress(newBranchesList[-1],branch)
#  ##ntupleTree.Branch(branch.GetName(),branch.GetAddress())
#  ##newBranchesList[len(newBranchesList)-1].SetAddress(0)
#  ##ntupleTree.SetBranchAddress(branch.GetName(),branch.GetAddress())
#  #ntupleTree.GetListOfBranches().Add(newBranchesList[-1])
#  AddTreeBranch(ntupleTree,branch)
#  newBranchesList.append(branch)
#ntupleTree.Write()

hltRunBranch = hltNtupleTree.GetBranch('run')
runBranch = ntupleTree.GetBranch('run')
hltLsLeaf = hltNtupleTree.GetLeaf('ls')
hltLsBranch = hltLsLeaf.GetBranch()
lsLeaf = ntupleTree.GetLeaf('ls')
lsBranch = lsLeaf.GetBranch()
hltEventBranch = hltNtupleTree.GetBranch('event')
eventBranch = ntupleTree.GetBranch('event')
# disable unneeded branches
ntupleTree.SetBranchStatus('*',False)
ntupleTree.SetBranchStatus('run',True)
ntupleTree.SetBranchStatus('ls',True)
ntupleTree.SetBranchStatus('event',True)
#for branch in newBranchesList:
#  ntupleTree.SetBranchStatus(branch.GetName(),True)
# make the indices
#FillDict(ntupleTreeEntryNumberDict,ntupleTree,runBranch,lsBranch,lsLeaf,eventBranch)
FillDict(hltTreeEntryNumberDict,hltNtupleTree,hltRunBranch,hltLsBranch,hltLsLeaf,hltEventBranch)

nentries = ntupleTree.GetEntries()
if nentries < 50:
  steps = nentries
else:
  steps = 50
progressString = '0% ['+' '*steps+'] 100%'
print progressString,
print '\b'*(len(progressString)-3),
sys.stdout.flush()

for entry in range(0,ntupleTree.GetEntries()):
  if (entry % (nentries/steps))==0:
    print '\b.',
    sys.stdout.flush()
  ntupleTree.GetEntry(entry)
  eventBranch.GetEntry(entry)
  runBranch.GetEntry(entry)
  lsBranch.GetEntry(entry)
  ls = lsLeaf.GetValue()
  try:
    hltNtupleTree.GetEntry(hltTreeEntryNumberDict[ntupleTree.run,ls,ntupleTree.event])
    hltLsBranch.GetEntry(hltTreeEntryNumberDict[ntupleTree.run,ls,ntupleTree.event])
    hltLs = hltLsLeaf.GetValue()
  except KeyError:
    print 'Entry does not exist in hltNtupleTree: run,ls,event:',ntupleTree.run,ls,ntupleTree.event,'; skip it'
    continue
  #print 'Get: HLT run,ls,event:',hltNtupleTree.run,hltLs,hltNtupleTree.event
  #ntupleTree.GetEntry(ntupleTreeEntryNumberDict[hltNtupleTree.run,hltLs,hltNtupleTree.event])
  #lsBranch.GetEntry(ntupleTreeEntryNumberDict[hltNtupleTree.run,hltLs,hltNtupleTree.event])
  #ls = lsLeaf.GetValue()
  if hltNtupleTree.run != ntupleTree.run or hltLs != ls or hltNtupleTree.event != ntupleTree.event:
    print 'ERROR: HLT run,ls,event:',hltNtupleTree.run,hltLs,hltNtupleTree.event,'!=','run,ls,event:',ntupleTree.run,ls,ntupleTree.event
    continue
  ## now we have the matching entries, fill it up
  #print 'HLT run,ls,event:',hltNtupleTree.run,hltLs,hltNtupleTree.event,'==','run,ls,event:',ntupleTree.run,ls,ntupleTree.event
  ##combinedNtupleTree.Fill()
  ##for branch in branchesToAdd:
  #for branch in newBranchesList:
  #  ntupleTree.GetBranch(branch.GetName()).Fill()
  newHLTntupleTree.Fill()

print '\b] 100%'

combinedNtupleFile.cd()
newNtupleTree.AddFriend(newHLTntupleTree)
#newHLTntupleTree.Write()
#newNtupleTree.Write()
combinedNtupleFile.Write()

##combinedNtupleTree.Write()
## reenable branches
#ntupleTree.SetBranchStatus('*',True)
#ntupleTree.Write()
combinedNtupleFile.Close()

#ntupleFile.Close()
hltNtupleFile.Close()

exit()
