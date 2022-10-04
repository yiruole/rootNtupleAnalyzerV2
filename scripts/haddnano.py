#!/bin/env python
import ROOT
import numpy
import sys
import time

if len(sys.argv) < 3 :
        print("Syntax: haddnano.py out.root input1.root input2.root ...")
ofname=sys.argv[1]
files=sys.argv[2:]

def zeroFill(tree,brName,brObj,allowNonBool=False) :
        # typename: (numpy type code, root type code)
        branch_type_dict = {'Bool_t':('?','O'), 'Float_t':('f4','F'), 'UInt_t':('u4','i'), 'Long64_t':('i8','L'), 'Double_t':('f8','D')}
        brType = brObj.GetLeaf(brName).GetTypeName()
        if (not allowNonBool) and (brType != "Bool_t") :
                print("Did not expect to back fill non-boolean branches",tree,brName,brObj.GetLeaf(br).GetTypeName())
        else :
                if brType not in branch_type_dict: raise RuntimeError('Impossible to backfill branch of type %s'%brType)
                buff=numpy.zeros(1,dtype=numpy.dtype(branch_type_dict[brType][0]))
                b=tree.Branch(brName,buff,brName+"/"+branch_type_dict[brType][1])
                b.SetBasketSize(tree.GetEntries()*2) #be sure we do not trigger flushing
                for x in range(0,tree.GetEntries()):    
                        b.Fill()
                b.ResetAddress()
fileHandles=[]
goFast=True
start = time.time()
for fn in files :
    print("Adding file",fn)
    fileHandles.append(ROOT.TFile.Open(fn))
    if fileHandles[-1].GetCompressionSettings() != fileHandles[0].GetCompressionSettings() :
        goFast=False
        print("Disabling fast merging as inputs have different compressions")
of=ROOT.TFile(ofname,"recreate")
if goFast :
        of.SetCompressionSettings(fileHandles[0].GetCompressionSettings())
of.cd()

for e in fileHandles[0].GetListOfKeys() :
        name=e.GetName()
        if name=='rootTupleTree':
            obj=fileHandles[0].Get("rootTupleTree/tree")
            obj.SetTitle("tree")
            obj.SetName("tree")
        else:
            obj=e.ReadObj()
        print("Merging" ,name)
        inputs=ROOT.TList()
        inputs.SetName("inputsList")
        dirInputs=dict()
        #isDir=ROOT.TClass.GetClass(e.GetClassName())=='TDirectoryFile'
        isDir=obj.IsA().InheritsFrom(ROOT.TDirectoryFile.Class())
        if isDir:
            for dirObj in obj.GetListOfKeys():
                thisObj = dirObj.ReadObj()
                dirInputs[thisObj.GetName()] = ROOT.TList()
                dirInputs[thisObj.GetName()].SetName(thisObj.GetName()+"list")
        isTree= obj.IsA().InheritsFrom(ROOT.TTree.Class())
        if isTree:
                branchNames=set([x.GetName() for x in obj.GetListOfBranches()])
                obj=obj.CloneTree(-1,"fast" if goFast else "")
        for fh in fileHandles[1:] :
                if name!='rootTupleTree':
                    otherObj=fh.GetListOfKeys().FindObject(name).ReadObj()
                else:
                    otherObj=fh.Get("rootTupleTree/tree")
                inputs.Add(otherObj)
                if isTree and (obj.GetName()=='Events' or obj.GetName()=='tree'): 
                        otherObj.SetAutoFlush(0)
                        otherBranches=set([ x.GetName() for x in otherObj.GetListOfBranches() ])
                        missingBranches=list(branchNames-otherBranches)
                        additionalBranches=list(otherBranches-branchNames)
                        print("missing:",missingBranches,"\n Additional:",additionalBranches)
                        for br in missingBranches :
                                #fill "Other"
                                zeroFill(otherObj,br,obj.GetListOfBranches().FindObject(br))
                        for br in additionalBranches :
                                #fill main
                                branchNames.add(br)
                                zeroFill(obj,br,otherObj.GetListOfBranches().FindObject(br))
                        #merge immediately for trees
                if isTree and obj.GetName()=='Runs':
                        otherObj.SetAutoFlush(0)
                        otherBranches=set([ x.GetName() for x in otherObj.GetListOfBranches() ])
                        missingBranches=list(branchNames-otherBranches)
                        additionalBranches=list(otherBranches-branchNames)
                        print("missing:",missingBranches,"\n Additional:",additionalBranches)
                        for br in missingBranches :
                                #fill "Other"
                                zeroFill(otherObj,br,obj.GetListOfBranches().FindObject(br),allowNonBool=True)
                        for br in additionalBranches :
                                #fill main
                                branchNames.add(br)
                                zeroFill(obj,br,otherObj.GetListOfBranches().FindObject(br),allowNonBool=True)
                        #merge immediately for trees
                if isTree:
                        obj.Merge(inputs,"fast" if goFast else "")
                        inputs.Clear()
                if isDir:
                    for objName in dirInputs.keys():
                        otherDirObj = otherObj.GetListOfKeys().FindObject(objName).ReadObj()
                        dirInputs[objName].Add(otherDirObj)
        
        if isTree  and obj.GetTitle()=="tree":
            of.mkdir("rootTupleTree")
            of.cd("rootTupleTree")
            obj.Write()
            of.cd()
        elif isTree:
            obj.Write()
        elif isDir:
            of.mkdir(e.GetName())
            of.cd(e.GetName())
            for dirObj in obj.GetListOfKeys():
                thisObj = dirObj.ReadObj()
                thisObj.Merge(dirInputs[thisObj.GetName()])
                thisObj.Write()
            of.cd()
        elif obj.IsA().InheritsFrom(ROOT.TH1.Class()) :         
                obj.Merge(inputs)
                obj.Write()
        elif obj.IsA().InheritsFrom(ROOT.TObjString.Class()) :  
                for st in inputs:
                        if  st.GetString()!=obj.GetString():
                                print("Strings are not matching")
                obj.Write()
        else:
                print("Cannot handle ", obj.IsA().GetName())
        
print("Time used for hadding files: %.2f s" % (time.time() - start))
