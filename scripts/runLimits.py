#!/usr/bin/env python3
import os
from optparse import OptionParser
import subprocess
import shlex
import glob
from termcolor import colored
import time
import datetime
import numpy as np
import re
from pathlib import Path
from ROOT import TFile
from combineCommon import SeparateDatacards
from BR_Sigma_EE_vsMass import BR_Sigma_EE_vsMass

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def RunCommand(cmd, workingDir=None):
    print(colored("\t{}".format(cmd), "green"))
    try:
        process = subprocess.run(shlex.split(cmd), check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=workingDir)
    except subprocess.CalledProcessError as e:
        result = ansi_escape.sub('', e.output.decode())
        print(colored("RunCommand had an error; output: {}".format(result), "red"), flush=True)
        raise e
    print(process.stdout.decode(), flush=True)
    #print(process.stderr.decode())


def ConvertDatacardToWorkspace(datacard):
    workspaceFileName = datacard+".root"
    cmd = 'text2workspace.py {} -o {}'.format(datacard, workspaceFileName)
    RunCommand(cmd)
    return Path(workspaceFileName).resolve()


def FindCardWorkspace(cardFile):
    listOfToyFiles = sorted(glob.glob(cardFile+'.root'), key=os.path.getmtime)
    if len(listOfToyFiles) > 0:
        return Path(listOfToyFiles[-1]).resolve()


def GenerateAsimovToyData(workspace, mass, toysDir):
    cmd = 'combine -M GenerateOnly {} -t -1 --seed -1 --saveToys -n .asimov -m {}'.format(workspace, mass)
    RunCommand(cmd, toysDir)
    return Path(sorted(glob.glob(toysDir+'/higgsCombine.asimov.GenerateOnly.mH{}.*.root'.format(mass)), key=os.path.getmtime)[-1]).resolve()


def FindAsimovToyData(mass, toysDir):
    listOfToyFiles = sorted(glob.glob(toysDir+'/higgsCombine.asimov.GenerateOnly.mH{}.*.root'.format(mass)), key=os.path.getmtime)
    if len(listOfToyFiles) > 0:
        return Path(listOfToyFiles[-1]).resolve()


def RunHybridNew(workspace, mass, dirName, quantile=-1, genAsimovToyFile=""):
    rAbsAcc = 0.0001
    toys = 4000
    cmd = 'combine -M HybridNew {}'.format(workspace)
    cmd += ' --LHCmode LHC-limits'
    cmd += ' --saveHybridResult'
    cmd += ' --rAbsAcc {}'.format(rAbsAcc)
    cmd += ' -T {}'.format(toys)
    cmd += ' -m {}'.format(mass)
    cmd += ' -H AsymptoticLimits'
    cmd += ' --fork 4'
    if quantile > 0:
        cmd += ' --expectedFromGrid {}'.format(quantile)
        if genAsimovToyFile != "":
            cmd += ' -D {}:toys/toy_asimov'.format(genAsimovToyFile)
    RunCommand(cmd, dirName)
    quantileString = "quant{:.3f}.".format(quantile) if quantile > 0 else "."
    rootFileName = dirName+"/higgsCombineTest.HybridNew.mH{}.{}root".format(mass, quantileString)
    return Path(rootFileName).resolve()


def ExtractLimitResult(rootFile):
    # higgsCombineTest.MethodName.mH$MASS.[word$WORD].root
    # higgsCombineTest.HybridNew.mH120.quant0.500.root
    if not os.path.isfile(rootFile):
        raise RuntimeError("ERROR: Did not find the root file {}. Exiting.".format(rootFile))
    tfile = TFile.Open(str(rootFile))
    limitTree = tfile.Get("limit")
    bytesRead = limitTree.GetEntry(0)
    if bytesRead <= 0:
        raise RuntimeError("ERROR: Something went wrong: read {} bytes from 'limit' tree in file {}. Exiting.".format(bytesRead, tfile))
    limit = limitTree.limit
    limitErr = limitTree.limitErr
    quantile = limitTree.quantileExpected
    tfile.Close()
    return limit, limitErr, quantile


def ReadXSecFile(filename):
    xsThByMass = {}
    yPDFupByMass = {}
    yPDFdownByMass = {}
    with open(os.path.expandvars(filename), "r") as xsecFile:
        for line in xsecFile:
            line = line.strip()
            if line.startswith("#"):
                continue
            split = line.split()
            if len(split) != 7:
                raise RuntimeError("length of this line is not 7; don't know how to handle it. Quitting.  Line looks like '"+line+"'")
            mass = float(split[0])
            xs = float(split[1])
            xsThByMass[mass] =  xs
            yPDFupByMass[mass] = xs*(1+float(split[5])/100.)
            yPDFdownByMass[mass] = xs*(1-float(split[6])/100.)
    return xsThByMass, yPDFupByMass, yPDFdownByMass


def CreateArraysForPlotting(xsecLimitsByMassAndQuantile):
    massList = sorted(list(xsecLimitsByMassAndQuantile.keys()))
    shadeMassList = []
    xs_medExpList = []
    xs_oneSigmaExpList = []
    xs_twoSigmaExpList = []
    xs_obsList = []
    if str(-1) in xsecLimitsByMassAndQuantile[list(xsecLimitsByMassAndQuantile.keys())[0]].keys():
        hasObserved = True
    else:
        hasObserved = False
    for mass in massList:
        xs_medExpList.append(xsecLimitsByMassAndQuantile[mass][str(0.5)])
        if hasObserved:
            xs_obsList.append(xsecLimitsByMassAndQuantile[mass][str(-1)])
        xs_oneSigmaExpList.append(xsecLimitsByMassAndQuantile[mass][str(0.16)])
        xs_twoSigmaExpList.append(xsecLimitsByMassAndQuantile[mass][str(0.025)])
    for mass in reversed(massList):
        xs_oneSigmaExpList.append(xsecLimitsByMassAndQuantile[mass][str(0.84)])
        xs_twoSigmaExpList.append(xsecLimitsByMassAndQuantile[mass][str(0.975)])
    masses = np.array(massList, dtype="f")
    shadeMasses = np.concatenate([masses, np.flip(masses)])
    xsMedExp = np.array(xs_medExpList, dtype="f")
    xsObs = np.array(xs_obsList, dtype="f")
    xsOneSigmaExp = np.array(xs_oneSigmaExpList, dtype="f")
    xsTwoSigmaExp = np.array(xs_twoSigmaExpList, dtype="f")
    return masses, shadeMasses, xsMedExp, xsOneSigmaExp, xsTwoSigmaExp, xsObs


####################################################################################################
# Run
####################################################################################################
quantilesExpected = [0.025, 0.16, 0.5, 0.84, 0.975]
xsThFilename = "$LQANA/config/xsection_theory_13TeV_scalarPairLQ.txt"

parser = OptionParser(
    usage="%prog datacard",
)
parser.add_option(
    "-d",
    "--datacard",
    dest="datacard",
    help="combined datacard",
    metavar="datacard",
)
parser.add_option(
    "-n",
    "--name",
    dest="name",
    help="name of limit calculation (for bookkeeping)",
    metavar="name",
)
(options, args) = parser.parse_args()
if options.datacard is None:
    raise RuntimeError("Option -d to specify datacard is required")
if options.name is None:
    raise RuntimeError("Option -n to specify name of limit results dir is required")

dirName = options.name
xsThByMass, yPDFUpByMass, yPDFDownByMass = ReadXSecFile(xsThFilename)
rLimitsByMassAndQuantile = {}
xsecLimitsByMassAndQuantile = {}
startTime = time.time()
combinedDatacard = options.datacard
#TODO: check for previous datacards?
separateDatacardsDir = dirName+"/datacards"
asimovToysDir = dirName+"/asimovData"
if not os.path.isdir(dirName):
    print("INFO: Making directory", dirName)
    Path(dirName).mkdir(exist_ok=True)
if not os.path.isdir(separateDatacardsDir):
    print("INFO: Making directory", separateDatacardsDir)
    Path(separateDatacardsDir).mkdir(exist_ok=True)
if not os.path.isdir(asimovToysDir):
    print("INFO: Making directory", asimovToysDir)
    Path(asimovToysDir).mkdir(exist_ok=True)
massList,cardFilesByMass = SeparateDatacards(combinedDatacard, 0, separateDatacardsDir)
for mass, cardFile in cardFilesByMass.items():
    print("INFO: Computing limits for mass {}".format(mass))
    rLimitsByMassAndQuantile[mass] = {}
    xsecLimitsByMassAndQuantile[mass] = {}
    cardWorkspace = FindCardWorkspace(cardFile)
    if cardWorkspace is not None:
        print("INFO: Using previously-generated card workspace: {}".format(cardWorkspace))
    else:
        cardWorkspace = ConvertDatacardToWorkspace(cardFile)
    asimovToyFile = FindAsimovToyData(mass, asimovToysDir)
    if asimovToyFile is not None:
        print("INFO: Using previously-generated Asimov toy file: {}".format(asimovToyFile))
    else:
        asimovToyFile = GenerateAsimovToyData(cardWorkspace, mass, asimovToysDir)
    for quantileExp in quantilesExpected:
        rootFileName = RunHybridNew(cardWorkspace, mass, dirName, quantile=quantileExp, genAsimovToyFile=asimovToyFile)
        limit, limitErr, quantile = ExtractLimitResult(rootFileName)
        rLimitsByMassAndQuantile[mass][str(quantileExp)] = limit
        xsecLimitsByMassAndQuantile[mass][str(quantileExp)] = limit * xsThByMass[float(mass)]

masses, shadeMasses, xsMedExp, xsOneSigmaExp, xsTwoSigmaExp, xsObs = CreateArraysForPlotting(xsecLimitsByMassAndQuantile)
print("mData =", list(masses))
print("x_shademasses =", list(shadeMasses))
print("xsUp_expected =", list(xsMedExp))
print("xsUp_observed =", list(xsObs))
print("y_1sigma =", list(xsOneSigmaExp))
print("y_2sigma =", list(xsTwoSigmaExp))
stopTime = time.time()
delta = datetime.timedelta(seconds=stopTime - startTime)
hours, rem = divmod(delta.seconds, 3600)
minutes, seconds = divmod(rem, 60)
execTimeStr = "{}s".format(seconds)
if minutes > 0:
    execTimeStr = "{}m".format(minutes) + execTimeStr
if hours > 0:
    execTimeStr = "{}h".format(hours) + execTimeStr
print("Limit calculation execution time:", execTimeStr)
print("Make plot and calculate mass limit")
BR_Sigma_EE_vsMass(dirName, masses, shadeMasses, xsMedExp, xsObs, xsOneSigmaExp, xsTwoSigmaExp)
