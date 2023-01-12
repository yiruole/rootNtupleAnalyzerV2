#!/usr/bin/env python3
import os
from optparse import OptionParser
import subprocess

tmpCardFileNameBasePath = "/tmp/tmpDatacard_m{}_card{}_{}"
combinedOutputCardName = "combCardFile.txt"
cmsswDir = os.path.expandvars("$LQLIMITS")


def DeleteTmpFiles(allTmpFilesByMass):
    for mass, tmpFileList in allTmpFilesByMass.items():
        for tmpFile in tmpFileList:
            os.unlink(tmpFile)


def WriteTmpCard(txtFilePath, mass, cardIndex, cardContent):
    tmpCardFileName = tmpCardFileNameBasePath.format(mass, cardIndex, os.path.basename(txtFilePath))
    with open(tmpCardFileName, "w") as tmpCardFile:
        for lineToWrite in cardContent:
            tmpCardFile.write(lineToWrite+"\n")
    return tmpCardFileName


def SeparateDatacards(txtFilePath, cardIndex):
    massList = []
    tmpFileByMass = {}
    cardContent = []
    for line in open(os.path.expandvars(txtFilePath)):
        #line = line.strip()
        #if len(line) < 1:
        #    continue
        if ".txt" in line:
            if len(cardContent) > 0:
                tmpFile = WriteTmpCard(txtFilePath, mass, cardIndex, cardContent)
                tmpFileByMass[mass] = tmpFile
            cardContent = []
            mass = line.split("M")[-1].split(".txt")[0]
            massList.append(mass)
        else:
            cardContent.append(line)
    if len(cardContent) > 0:
        tmpFile = WriteTmpCard(txtFilePath, mass, cardIndex, cardContent)
        tmpFileByMass[mass] = tmpFile
    return massList, tmpFileByMass


#####################################################################################################
# RUN
#####################################################################################################
parser = OptionParser(
    usage="%prog [datacard1] [datacard2] ... [datacardN] [label1] [label2] ... [labelN]",
    )

(options, args) = parser.parse_args()
if not args:
    raise RuntimeError("No input datacards specified.")
if len(args)%2 != 0:
    raise RuntimeError("Odd number of arguments specified; must specify number of labels equal to number of datacards")

#FIXME: change this so that it uses the combineCards format of label1=card1 label2=card2
datacards = args[:len(args)//2]
labels = args[len(args)//2:]
for label in labels:
    if os.path.isfile(label):
        raise RuntimeError("Got a file {} where a label was expected instead. Must specify number of labels equal to number of datacards.".format(label))

massListByCombinedDatacard = {}
allTmpFilesByMass = {}
for index, combinedDatacard in enumerate(datacards):
    massList, tmpFilesByMass = SeparateDatacards(combinedDatacard, index)
    massListByCombinedDatacard[combinedDatacard] = massList
    for mass, tmpFile in tmpFilesByMass.items():
        if mass not in allTmpFilesByMass:
            allTmpFilesByMass[mass] = []
        allTmpFilesByMass[mass].append(tmpFile)

#print(massListByCombinedDatacard)
referenceMassList = []
referenceDatacard = ""
for combinedCard, massList in massListByCombinedDatacard.items():
    if len(referenceMassList) < 1:
        referenceMassList = sorted(massList)
        referenceDatacard = combinedCard
        continue
    if sorted(massList) != referenceMassList:
        DeleteTmpFiles(allTmpFilesByMass)
        raise RuntimeError("mass list {} from parsing {} is not the same as mass list {} from parsing {}. Can't combine the datacards.".format(massList, combinedCard, referenceMassList, referenceDatacard))

with open(combinedOutputCardName, "w") as combCardFile:
    for mass in referenceMassList:
        cardsForMass = allTmpFilesByMass[mass]
        combineCardsArgs = [label+"="+card for label, card in zip(labels, cardsForMass)]
        #TODO: support args to combineCards
        cmd = 'cd {} && eval `scram runtime -sh` && combineCards.py {}'.format(cmsswDir, " ".join(combineCardsArgs))
        #output = subprocess.check_output(cmd, env={})
        process = subprocess.Popen(['/bin/bash', '-l', '-c', cmd], env={}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        errcode = process.returncode
        if errcode != 0:
            DeleteTmpFiles(allTmpFilesByMass)
            raise RuntimeError("Command {} failed with return code {}.\nStderr: {}\n Exiting here.".format("/bin/bash -l -c "+cmd, errcode, err.decode().strip()))
        #with open("combCardFile_m{}.txt".format(mass), "w") as combCardFile:
        #    combCardFile.write(out.decode())
        #print("Wrote combined file for mass {} to {}".format(mass, "combCardFile_m{}.txt".format(mass)))
        combCardFile.write("LQ_M{}.txt\n".format(mass))
        combCardFile.write(out.decode())
        print("Wrote combination for mass {}".format(mass))
    
#DeleteTmpFiles(allTmpFilesByMass)
print("Wrote combined file {}".format(combinedOutputCardName))
