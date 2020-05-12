from ROOT import TFile

filename = "root://eoscms.cern.ch//eos/cms/store/group/phys_exotica/leptonsPlusJets/LQ/scooper/nanoPostProc/2018/EGamma/Run2018B-Nano25Oct2019-v1/200406_071800/0000/EGamma_Run2018B-Nano25Oct2019-v1_41.root"
# filename = "/tmp/scooper/EGamma_Run2018B-Nano25Oct2019-v1_42.root"
# filename = "root://cms-xrd-global//store/data/Run2018B/EGamma/NANOAOD/Nano25Oct2019-v1/230000/EC63B4EC-42E2-514C-BA93-9A6CB25A06DE.root"
myFile = TFile.Open(filename)
myTree = myFile.Get("Events")
myTree.SetBranchStatus("*", 0)
myTree.SetBranchStatus("run", 1)


entry = 0
runList = set()
for ev in myTree:
    #if entry % 50000 == 0:
    #    print "event: "+str(entry)
    runList.add(ev.run)
    entry += 1

print "list of runs in file: "+filename
print sorted(runList)
