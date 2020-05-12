from ROOT import TFile

filename1 = "root://eoscms.cern.ch//eos/cms/store/group/phys_exotica/leptonsPlusJets/LQ/scooper/nanoPostProc/2018/EGamma/Run2018B-Nano25Oct2019-v1/200406_071800/0000/EGamma_Run2018B-Nano25Oct2019-v1_41.root"
filename2 = "/tmp/scooper/EGamma_Run2018B-Nano25Oct2019-v1_42.root"

print "file1 is: "+filename1
print "file2 is: "+filename2

file1 = TFile.Open(filename1)
file2 = TFile.Open(filename2)

tree1 = file1.Get("Events")
tree2 = file2.Get("Events")

branchList1 = tree1.GetListOfBranches()
branchList2 = tree2.GetListOfBranches()
branchNames1 = [branch.GetName() for branch in branchList1]
branchNames2 = [branch.GetName() for branch in branchList2]

for branchName in branchNames1:
    if branchName not in branchNames2:
        print "WARNING: Found branch "+branchName+" in file1 that I could not find in file2"

file1.Close()
file2.Close()

