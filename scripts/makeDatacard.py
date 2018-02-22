#!/usr/bin/env python

import os, sys, math, re
import subprocess as sp
from optparse import OptionParser
from prettytable import PrettyTable
from ROOT import *

from combineCommon import *

def GetStatErrors(nevts, theta=1.0, nScaledEvents=-1):
    #nevts = int(nevts)
    if nScaledEvents==-1:
        # this is the case for data, as there's no scaling
        nScaledEvents=nevts
    alpha = 1.0 - 0.6827
    #print 'calculate errors on nevts=',nevts
    if nevts < 0:
      print 'ERROR: nevts < 0:',nevts
      return -999,-999
    if theta < 0:
      print 'ERROR: theta < 0:',theta
      return -999,-999
    # if nevts=0, lower error is zero
    # if scaled events is zero, lower error is also zero. For amc@NLO with negative weights, or ttbar data driven (subtracting MC),
    #   it can be the case that nevts>0 but nScaledEvents<=0 (set to zero previously)
    l = 0 if nevts==0 or nScaledEvents==0 else ROOT.Math.gamma_quantile(alpha/2.0,nevts,theta)
    u = ROOT.Math.gamma_quantile_c(alpha/2.0,nevts+1,theta)
    #return u-nevts,nevts-l
    return u-nScaledEvents,nScaledEvents-l


def GetStatErrorFromDict(statErrDict, mass):
    availMasses = sorted(statErrDict.keys())
    if mass not in availMasses and mass > availMasses[-1]:
        mass = availMasses[-1]
    return statErrDict[mass]


def GetBackgroundSyst(background_name, selectionName):
    verbose = False
    #if selectionName=='preselection':
    #  verbose=True
    if verbose:
      print 'GetBackgroundSyst('+background_name+','+selectionName+')'
    firstSyst = 0
    secondSyst = 0
    thirdSyst = 0
    if not 'QCD' in background_name and not 'data' in background_name.lower():
      for syst in signalSystDict.keys():
          if selectionName not in backgroundSystDict[syst][background_name].keys():
              if 'LQ' in selectionName:
                selectionNameBkgSyst = maxLQselectionBkg
              else:
                selectionNameBkgSyst = minLQselectionBkg
              #print 'selectionName=',selectionName,'not found in',backgroundSystDict[syst][background_name].keys()
          else:
              selectionNameBkgSyst = selectionName
          try:
            firstSyst += pow(backgroundSystDict[syst][background_name][selectionNameBkgSyst],2) # deltaX/X
            if verbose:
                print 'add',syst,'for',background_name,'at selection',selectionNameBkgSyst,'to firstSyst=',backgroundSystDict[syst][background_name][selectionNameBkgSyst]
          except KeyError:
              print 'Got a KeyError with: backgroundSystDict['+syst+']['+background_name+']['+selectionNameBkgSyst+']'

    if verbose:
      print 'firstSyst=',math.sqrt(firstSyst)

    # background-only special systs: "DYShape", "TTShape", "WShape"
    specialSysts = ["DYShape",'DY_Norm','Diboson_shape'] if doEEJJ else ["WShape","TTShape",'W_Norm','TT_Norm','Diboson_shape']
    for syst in specialSysts:
        if 'TTBarFromDATA' in background_name or 'DY' in syst and not 'DY' in background_name or 'TT' in syst and not 'TT' in background_name or 'W' in syst and not 'W' in background_name or 'Diboson' in syst and not 'Diboson' in background_name:
            continue
        if background_name not in backgroundSystDict[syst].keys():
          print 'WARNING: could not find',background_name,'in backgroundSystDict['+syst+']=',backgroundSystDict[syst].keys()
          continue
        if selectionName not in backgroundSystDict[syst][background_name].keys():
            selectionNameBkgSyst = maxLQselectionBkg
        else:
            selectionNameBkgSyst = selectionName
        try:
          secondSyst = pow(backgroundSystDict[syst][background_name][selectionNameBkgSyst],2)
          if verbose:
            print 'backgroundSystDict['+syst+']['+background_name+']['+selectionNameBkgSyst+']=',secondSyst
        except KeyError:
            print 'ERROR: Got a KeyError with: backgroundSystDict['+syst+']['+background_name+']['+selectionNameBkgSyst+']'

    if verbose:
      print 'secondSyst (TT/DYShape)=',math.sqrt(secondSyst)
        
    # XXX WARNING: hardcoded background name (ick); some checking is done at least
    if 'TTbar' in background_name:
        thirdSyst = pow(ttBarNormDeltaXOverX,2)
    elif not doEEJJ and 'W' in background_name:
        thirdSyst = pow(zJetNormDeltaXOverX,2)
    elif 'QCD' in background_name:
        thirdSyst = pow(qcdNormDeltaXOverX,2)

    if verbose:
      print 'thirdSyst (extra norm uncertainty)=',math.sqrt(thirdSyst)

    # now get the total deltaX/X
    totalSyst = math.sqrt(firstSyst+secondSyst+thirdSyst)
    return totalSyst


def GetSystDictFromFile(filename):
    # go custom text parsing :`(
    # format is like:
    # LQ300  :     0.0152215
    # selection point, 100*(deltaX/X) [rel. change in %]
    systDict = {}
    if not os.path.isfile(filename):
      print "ERROR: file'"+filename+"' not found; cannot proceed"
      exit(-1)
    with open(filename,'r') as thisFile:
        for line in thisFile:
            line = line.strip()
            #print 'line=',line,'; with length=',len(line)
            if len(line)==0:
                continue
            #print 'line.strip()="'+line.strip()+'"'
            #print 'line.strip().split(":")=',line.strip().split(':')
            items = line.split(':')
            #print 'items[0].strip()='+items[0].strip()
            #print 'items[1].strip()='+items[1].strip()
            selectionPoint = items[0].strip()
            if '_' in selectionPoint:
                bkgName = selectionPoint.split('_')[1]
                if not bkgName in syst_background_names:
                    print 'WARN: background named:',bkgName,' was not found in list of systematics background names:',syst_background_names
                    print 'selectionPoint=',selectionPoint,'from',filename
                selectionPoint = selectionPoint.split('_')[0]
                if not bkgName in systDict.keys():
                    systDict[bkgName] = {}
                try:
                  systDict[bkgName][selectionPoint] = float(items[1].strip())/100.0
                except ValueError:
                  print 'ERROR: Had ValueError exception trying to convert "'+items[1].strip()+'" to a float. From line:',line,'in file:',filename
                  exit(-1)
            # signal
            systDict[selectionPoint] = float(items[1].strip())/100.0
    return systDict


def FillSystDicts(systNames,isBackground=True):
    systDict = {}
    for syst in systNames:
        if isBackground:
          filePath = systematics_filepaths[syst]+syst+'_sys.dat'
        else:
          filePath = systematics_filepaths[syst]+'LQ'+syst+'_sys.dat'
        thisSystDict = GetSystDictFromFile(filePath)
        # this will give the form (for background):
        #   systDict['Trigger'][bkgname]['LQXXXX'] = value
        systDict[syst] = thisSystDict
    return systDict

def RoundToN(x, n):
    #if n < 1:
    #    raise ValueError("can't round to less than 1 sig digit!")
    ## number of digits given by n
    #return "%.*e" % (n-1, x)
    if isinstance(x,float):
        return round(x,n)
    else:
        return x

def GetTableEntryStr(evts,errStatUp='-',errStatDown='-',errSyst=0,latex=False):
    if evts=='-':
      return evts
    # rounding
    evtsR = RoundToN(evts,2)
    errStatUpR = RoundToN(errStatUp,2)
    errStatDownR = RoundToN(errStatDown,2)
    # add additional decimal place if it's zero after rounding
    if evtsR==0.0:
      evtsR = RoundToN(evts,3)
    if errStatUpR==0.0:
      errStatUpR = RoundToN(errStatUp,3)
    if errStatDownR==0.0:
      errStatDownR = RoundToN(errStatDown,3)
    # try again
    if evtsR==0.0:
      evtsR = RoundToN(evts,4)
    if errStatUpR==0.0:
      errStatUpR = RoundToN(errStatUp,4)
    if errStatDownR==0.0:
      errStatDownR = RoundToN(errStatDown,4)
    # handle cases where we don't specify stat or syst
    if errStatUp=='-':
      return str(evtsR)
    elif errSyst==0:
      if errStatUp==errStatDown:
          if not latex:
              return str(evtsR)+' +/- '+str(errStatUpR)
          else:
              return str(evtsR)+' \\pm '+str(errStatUpR)
      else:
          if not latex:
              return str(evtsR)+' + '+str(errStatUpR)+' - '+str(errStatDownR)
          else:
              return str(evtsR)+'^{+'+str(errStatUpR)+'}_{-'+str(errStatDownR)+'}'
    else:
      errSystR = RoundToN(errSyst,2)
      if errStatUp==errStatDown:
          if not latex:
              return str(evtsR)+' +/- '+str(errStatUpR)+' +/- '+str(errSystR)
          else:
              return str(evtsR)+' \\pm '+str(errStatUpR)+' \\pm '+str(errSystR)
      else:
        return str(evtsR)+'^{+'+str(errStatUpR)+'}_{-'+str(errStatDownR)+'} \\pm '+str(errSystR)


def GetXSecTimesIntLumi(sampleNameFromDataset):
    #print 'GetXSecTimesIntLumi(',sampleNameFromDataset+')'
    xsection = float(lookupXSection(sampleNameFromDataset,xsectionDict))
    intLumiF = float(intLumi)
    return xsection*intLumiF

def CalculateScaledRateError(sampleNameFromDataset, N_unscaled_tot, N_unscaled_pass_entries, N_unscaled_pass_integral, doScaling=True):
    #print 'CalculateScaledRateError(',sampleNameFromDataset, N_unscaled_tot, N_unscaled_pass_entries, N_unscaled_pass_integral,')'
    # binomial error
    p = N_unscaled_pass_entries/N_unscaled_tot
    q = 1-p
    w = N_unscaled_pass_integral/N_unscaled_pass_entries if N_unscaled_pass_entries != 0 else 0.0
    unscaledRateError = N_unscaled_tot*w*math.sqrt(p*q/N_unscaled_tot)
    if doScaling:
        xsecTimesIntLumi = GetXSecTimesIntLumi(sampleNameFromDataset)
        scaledRateError=unscaledRateError*(xsecTimesIntLumi/N_unscaled_tot)
    else:
        scaledRateError=unscaledRateError
    return scaledRateError


def FindUnscaledSampleRootFile(sampleName, bkgType=''):
  #print 'FindUnscaledSampleRootFile('+sampleName+','+bkgType+')'
  if bkgType=='QCD':
    filepath = qcdFilePath
    if doEEJJ:
      analysisCode = 'analysisClass_lq_eejj_QCD'
    else:
      analysisCode = 'analysisClass_lq_enujj_QCD'
  elif bkgType=='TTData':
      return ttbar_data_filepath
  else:
    filepath = filePath
    if doEEJJ:
      analysisCode = 'analysisClass_lq_eejj'
    else:
      analysisCode = 'analysisClass_lq_enujj_MT'
  reducedSkimStrings = ['_reduced_skim','_pythia8_reduced_skim','_ext1_pythia8_reduced_skim']
  for redSkimStr in reducedSkimStrings:
      rootFilename = filepath + "/" + analysisCode + "___" + sampleName + redSkimStr + ".root"
      if os.path.isfile(rootFilename):
         #print 'return unscaled rootfile:',rootFilename
         return rootFilename
  print "ERROR:  could not find unscaled root file for sample=",sampleName
  print 'Tried:',[filepath + "/" + analysisCode + "___" + sampleName + redSkimStr + ".root" for redSkimStr in reducedSkimStrings]
  print "Exiting..."
  exit(-1)
  #rootFilename = filePath + "/" + analysisCode + "___" + sampleName + reducedSkimStrings[0] + ".root"
  #while not os.path.isfile(rootFilename) and index<len(reducedSkimStrings):
  #    index+=1
  #    rootFilename = filePath + "/" + analysisCode + "___" + sampleName + reducedSkimStrings[index] + ".root"
  #    #if not os.path.isfile(rootFilename):
  #    #    print "ERROR: file " + rootFilename + " not found"
  #    #    print "exiting..."
  #    #    exit(-1)
  #return rootFilename


def GetRatesAndErrors(unscaledRootFile,combinedRootFile,unscaledTotalEvts,sampleName,selection,isDataOrQCD=False,isTTBarFromData=False):
    verbose = False
    if verbose:
      print 'GetRatesAndErrors(',unscaledRootFile,combinedRootFile,unscaledTotalEvts,sampleName,selection,isDataOrQCD,')'
    if selection=='preselection':
        selection = 'PAS'
    if doEEJJ:
      histName = 'Mej_selected_min'
    else:
      histName = 'Mej'
    # special case of TTBar from data
    if isTTBarFromData:
        # rate calcs should be same as data/QCD
        mejHist = combinedRootFile.Get('histo1D__'+ttbarSampleName+'__'+histName+'_'+selection)
        mejUnscaledRawHist = combinedRootFile.Get('histo1D__'+ttBarUnscaledRawSampleName+'__'+histName+'_'+selection)
        mejNonTTBarHist = combinedRootFile.Get('histo1D__'+nonTTBarSampleName+'__'+histName+'_'+selection)
        if not mejNonTTBarHist:
          sys.stdout.flush()
          print 'ERROR: could not find hist histo1D__'+nonTTBarSampleName+'__'+histName+'_'+selection,' in file:',combinedRootFile.GetName()
          print 'EXIT'
          exit(-1)
        rateErr = Double(0)
        #integ = mejNonTTBarHist.IntegralAndError(1,mejNonTTBarHist.GetNbinsX(),rateErr)
        #print 'mejNonTTBar:',integ,',+/-',rateErr
        #integ = mejUnscaledRawHist.IntegralAndError(1,mejUnscaledRawHist.GetNbinsX(),rateErr)
        #print 'mejUnscaledRaw:',integ,',+/-',rateErr
        #mejNonTTBarHist.Scale(1/1000.)
        #rate = mejHist.Integral()
        rate = mejHist.IntegralAndError(1,mejHist.GetNbinsX()+1,rateErr)
        unscaledHist = mejUnscaledRawHist.Clone()
        #unscaledHist.Add(mejNonTTBarHist,-1) #LQ2 only uses emujj data events
        #integ = mejUnscaledHist.IntegralAndError(1,mejUnscaledHist.GetNbinsX(),rateErr)
        #print 'mejUnscaled:',integ,',+/-',rateErr
        #scaledHist = unscaledHist.Clone()
        #scaledHist.Scale(0.436873)
        #integ = mejScaledHist.IntegralAndError(1,mejScaledHist.GetNbinsX(),rateErr)
        #print 'mejScaled:',integ,',+/-',rateErr
        #unscaledRate = unscaledHist.Integral()
        unscaledRateErr = Double(0)
        unscaledRate = unscaledHist.IntegralAndError(1,mejHist.GetNbinsX()+1,unscaledRateErr)
        if verbose:
          print 'using unscaled (minus nonttbarMC) hist:',unscaledHist.GetName(),'from file:',combinedRootFile.GetName()
          print 'TTBARFROMDATA-->rate=',rate,'+/-',rateErr
          print 'mejUnscaled:',unscaledRate,',+/-',unscaledRateErr
          print 'using hist:',mejHist.GetName(),'from file:',combinedRootFile.GetName()
        return rate,rateErr,unscaledRate
    #mejHist = combinedRootFile.Get('histo1D__'+sampleName+histName+'_'+selection)
    #if not mejHist:
    #  print 'ERROR: could not find hist','histo1D__'+sampleName+histName+'_'+selection,' in file:',combinedRootFile.GetName()
    #  print 'EXIT'
    #  exit(-1)
    #rate = mejHist.Integral()
    mejUnscaledHist = unscaledRootFile.Get(histName+'_'+selection)
    if not mejUnscaledHist:
      print 'ERROR: could not find hist',histName+'_'+selection,' in file:',unscaledRootFile.GetName()
      print 'EXIT'
      exit(-1)
    unscaledInt = mejUnscaledHist.Integral(1,mejUnscaledHist.GetNbinsX()+1)
    unscaledRate = mejUnscaledHist.GetEntries()
    xsecTimesIntLumi = GetXSecTimesIntLumi(sampleName)
    sumOfWeightsHist = unscaledRootFile.Get('SumOfWeights')
    if not sumOfWeightsHist:
      print 'ERROR: could not find hist SumOfWeights in file:',unscaledRootFile.GetName()
      print 'EXIT'
      exit(-1)
    sumAMCatNLOweights = sumOfWeightsHist.GetBinContent(1)
    sumTopPtWeights = sumOfWeightsHist.GetBinContent(2)
    avgTopPtWeight = sumTopPtWeights/unscaledTotalEvts
    if re.search('amcatnlo',sampleName,re.IGNORECASE):
        rate = unscaledInt*xsecTimesIntLumi/sumAMCatNLOweights
        #print '[AMCATNLO detected] for sampleName',sampleName,'amcAtNLO, rate=',unscaledInt,'*',xsecTimesIntLumi,'/',sumAMCatNLOweights,'=',rate
        rateErr = CalculateScaledRateError(sampleName,sumAMCatNLOweights,unscaledRate,unscaledInt)
    elif not isDataOrQCD:
        rate = unscaledInt*xsecTimesIntLumi/unscaledTotalEvts
        rateErr = CalculateScaledRateError(sampleName,unscaledTotalEvts,unscaledRate,unscaledInt)
    else:
        #print '[DataOrQCD detected] for sampleName',sampleName,'rate=',unscaledInt
        #print 'reading 'histName+'_'+selection,'from',unscaledRootFile
        rate = unscaledInt
        rateErr = CalculateScaledRateError(sampleName,unscaledTotalEvts,unscaledRate,unscaledInt,False)
    if 'TT' in sampleName and not 'data' in sampleName.lower():
        #print 'applying extra average weight to',sampleName
        rate/=avgTopPtWeight
        rateErr/=avgTopPtWeight
    #if selection=='LQ1500':
    #  print 'INFO: hist',histName+'_'+selection,' in file:',unscaledRootFile.GetName()
    #  print 'unscaledRate=',unscaledRate,'unscaled entries=',mejUnscaledHist.GetEntries()
    #  print 'xsecTimesIntLumi=',xsecTimesIntLumi,'unscaledInt=',unscaledInt,'unscaledRate=',unscaledRate,'unscaledTotalEvts=',unscaledTotalEvts,'rate=unscaledInt*xsecTimesIntLumi/unscaledTotalEvts=',rate
    return rate,rateErr,unscaledRate

def GetUnscaledTotalEvents(unscaledRootFile,isTTBarData=False):
    if not isTTBarData:
        unscaledEvtsHist = unscaledRootFile.Get('EventsPassingCuts')
        unscaledTotalEvts = unscaledEvtsHist.GetBinContent(1)
    else:
        #scaledEvtsHist = unscaledRootFile.Get('histo1D__'+ttbarSampleName+'__EventsPassingCuts')
        unscaledEvtsHist = unscaledRootFile.Get('histo1D__'+ttBarUnscaledRawSampleName+'__EventsPassingCuts')
        #nonTTBarHist = combinedRootFile.Get('histo1D__'+nonTTBarSampleName+'__EventsPassingCuts')
        #unscaledTotalEvts = unscaledEvtsHist.GetBinContent(1)-nonTTBarHist.GetBinContent(1)
        #print 'GetUnscaledTotalEvents(): Got unscaled events=',unscaledTotalEvts,'from hist:',unscaledEvtsHist.GetName(),'in file:',unscaledRootFile.GetName()
        unscaledTotalEvts = unscaledEvtsHist.GetBinContent(1)
    return unscaledTotalEvts

def FillDicts(rootFilename,qcdRootFilename,ttbarRootFilename):
    if len(ttbarRootFilename) > 0:
      ttbarFile = TFile(ttbarRootFilename)
    qcdTFile = TFile(qcdRootFilename)
    tfile = TFile(rootFilename)

    # backgrounds
    for i_bkg,bkg_name in enumerate(background_names):
        scaledRootFile = ''
        bkgType='MC'
        if 'TT' in bkg_name and 'data' in bkg_name.lower():
          scaledRootFile = ttbarFile
          bkgType= 'TTData'
        elif 'QCD' in bkg_name or 'SinglePhoton' in bkg_name:
          scaledRootFile = qcdTFile
          bkgType='QCD'
        else:
          scaledRootFile = tfile
        sampleList = dictSamples[bkg_name]
        sampleRate = 0
        sampleRateErr = 0
        sampleUnscaledRate = 0
        sampleUnscaledTotalEvts = 0
        #print 'PRESELECTION bkg_bame=',bkg_name
        #print 'backgroundType=',bkgType
        #print 'sampleList['+bkg_name+']=',sampleList
        for bkgSample in sampleList:
            bkgUnscaledRootFilename = FindUnscaledSampleRootFile(bkgSample,bkgType)
            bkgUnscaledRootFile = TFile.Open(bkgUnscaledRootFilename)
            if not bkgUnscaledRootFile:
              print 'ERROR: something happened when trying to open the file:',bkgUnscaledRootFilename
              exit(-1)
            unscaledTotalEvts = GetUnscaledTotalEvents(bkgUnscaledRootFile,bkgType=='TTData')
            sampleUnscaledTotalEvts+=unscaledTotalEvts
            # preselection
            #print 'PRESELECTION ------>Call GetRatesAndErrors for sampleName=',bkgSample
            rate,rateErr,unscaledRate = GetRatesAndErrors(bkgUnscaledRootFile,scaledRootFile,unscaledTotalEvts,bkgSample,'preselection',not bkgType=='MC',bkgType=='TTData')
            #print 'PRESELECTION ------>rate=',rate,'rateErr=',rateErr,'unscaledRate=',unscaledRate
            sampleRate+=rate
            sampleUnscaledRate+=unscaledRate
            sampleRateErr+=(rateErr*rateErr)
            bkgUnscaledRootFile.Close()
        sampleRateErr = math.sqrt(sampleRateErr)
        #print 'PRESELECTION sampleRate:',sampleRate,'sampleRateErr=',sampleRateErr,'sampleUnscaledRate=',sampleUnscaledRate
        bkgRatesDict = {}
        bkgRatesDict['preselection'] = sampleRate
        if bkgRatesDict['preselection'] < 0:
          print 'WARN: for sample',bkg_name,'preselection','found negative rate:',sampleRate,'; set to zero.'
          bkgRatesDict['preselection'] = 0.0
        bkgRateErrsDict = {}
        bkgRateErrsDict['preselection'] = sampleRateErr
        bkgUnscaledRatesDict = {}
        bkgUnscaledRatesDict['preselection'] = sampleUnscaledRate
        bkgTotalEvts = sampleUnscaledTotalEvts
        # final selections
        for i_signal_name, signal_name in enumerate(signal_names):
            for i_mass_point, mass_point in enumerate(mass_points):
                selectionName = 'LQ'+mass_point
                sampleList = dictSamples[bkg_name]
                sampleRate = 0
                sampleRateErr = 0
                sampleUnscaledRate = 0
                #print selectionName,'bkg_name=',bkg_name
                for bkgSample in sampleList:
                    bkgUnscaledRootFilename = FindUnscaledSampleRootFile(bkgSample,bkgType)
                    bkgUnscaledRootFile = TFile.Open(bkgUnscaledRootFilename)
                    if not bkgUnscaledRootFile:
                      print 'ERROR: file not found:',bkgUnscaledRootFilename
                      exit(-1)
                    unscaledTotalEvts = GetUnscaledTotalEvents(bkgUnscaledRootFile,bkgType=='TTData')
                    sampleUnscaledTotalEvts+=unscaledTotalEvts
                    rate,rateErr,unscaledRate = GetRatesAndErrors(bkgUnscaledRootFile,scaledRootFile,unscaledTotalEvts,bkgSample,selectionName,not bkgType=='MC',bkgType=='TTData')
                    #if bkgType=='TTData':
                    #  print '------>Called GetRatesAndErrors for sampleName=',bkgSample
                    #  print '------>rate=',rate,'rateErr=',rateErr,'unscaledRate=',unscaledRate
                    #  print '------>from file=:',bkgUnscaledRootFilename
                    #if isQCD:
                    #  print 'for sample:',bkgSample,'got unscaled entries=',unscaledRate
                    sampleRate+=rate
                    sampleUnscaledRate+=unscaledRate
                    sampleRateErr+=(rateErr*rateErr)
                    bkgUnscaledRootFile.Close()
                sampleRateErr = math.sqrt(sampleRateErr)
                #print 'sampleRate:',sampleRate,'sampleRateErr=',sampleRateErr,'sampleUnscaledRate=',sampleUnscaledRate
                bkgRatesDict[selectionName] = sampleRate
                if bkgRatesDict[selectionName] < 0:
                  print 'WARN: for sample',bkg_name,'selection',selectionName,'found negative rate:',sampleRate,'; set to zero.'
                  bkgRatesDict[selectionName] = 0.0
                bkgRateErrsDict[selectionName] = sampleRateErr
                bkgUnscaledRatesDict[selectionName] = sampleUnscaledRate
        # fill full dicts
        d_background_rates[bkg_name] = bkgRatesDict
        d_background_rateErrs[bkg_name] = bkgRateErrsDict
        d_background_unscaledRates[bkg_name] = bkgUnscaledRatesDict
        d_background_totalEvents[bkg_name] = bkgTotalEvts

    # signals
    for i_signal_name, signal_name in enumerate(signal_names):
        for i_mass_point, mass_point in enumerate(mass_points):
          if 'BetaHalf' in signal_name:
              #signalNameForFile = 'LQToUE_' #FIXME
              signalNameForFile = 'LQToUE_ENuJJFilter_M-'+mass_point+'_BetaHalf'
          else:
              signalNameForFile = 'LQToUE_M-'+mass_point+'_BetaOne'
          fullSignalName = signal_name+mass_point
          unscaledRootFilename = FindUnscaledSampleRootFile(signalNameForFile)
          unscaledRootFile = TFile.Open(unscaledRootFilename)
          unscaledTotalEvts = GetUnscaledTotalEvents(unscaledRootFile)
          # preselection
          rate,rateErr,unscaledRate = GetRatesAndErrors(unscaledRootFile,tfile,unscaledTotalEvts,signalNameForFile,'preselection')
          sigRatesDict = {}
          sigRatesDict['preselection'] = rate
          sigRateErrsDict = {}
          sigRateErrsDict['preselection'] = rateErr
          sigUnscaledRatesDict = {}
          sigUnscaledRatesDict['preselection'] = unscaledRate
          sigTotalEvts = unscaledTotalEvts
          # final selection
          for imp, mp in enumerate(mass_points):
              signalSelName = signal_name+mp
              selectionName = 'LQ'+mp
              rate,rateErr,unscaledRate = GetRatesAndErrors(unscaledRootFile,tfile,unscaledTotalEvts,signalNameForFile,selectionName)
              sigRatesDict[selectionName] = rate
              sigRateErrsDict[selectionName] = rateErr
              sigUnscaledRatesDict[selectionName] = unscaledRate
          unscaledRootFile.Close()

          # fill full dicts
          signalFullName = signal_name + mass_point
          d_signal_rates[signalFullName] = sigRatesDict
          d_signal_rateErrs[signalFullName] = sigRateErrsDict
          d_signal_unscaledRates[signalFullName] = sigUnscaledRatesDict
          d_signal_totalEvents[signalFullName] = sigTotalEvts

    # DATA
    sampleList = dictSamples['DATA']
    sampleRate = 0
    sampleRateErr = 0
    sampleUnscaledRate = 0
    sampleUnscaledTotalEvts = 0
    isQCD = False
    isData = True
    for bkgSample in sampleList:
        bkgUnscaledRootFilename = FindUnscaledSampleRootFile(bkgSample)
        bkgUnscaledRootFile = TFile.Open(bkgUnscaledRootFilename)
        if not bkgUnscaledRootFile:
          print 'ERROR: something happened when trying to open the file:',bkgUnscaledRootFilename
          exit(-1)
        unscaledTotalEvts = GetUnscaledTotalEvents(bkgUnscaledRootFile)
        sampleUnscaledTotalEvts+=unscaledTotalEvts
        # preselection
        #print '------>Call GetRatesAndErrors for sampleName=',bkgSample
        rate,rateErr,unscaledRate = GetRatesAndErrors(bkgUnscaledRootFile,scaledRootFile,unscaledTotalEvts,bkgSample,'preselection',isData)
        #print '------>rate=',rate,'rateErr=',rateErr,'unscaledRate=',unscaledRate
        sampleRate+=rate
        sampleUnscaledRate+=unscaledRate
        sampleRateErr+=(rateErr*rateErr)
        bkgUnscaledRootFile.Close()
    sampleRateErr = math.sqrt(sampleRateErr)
    #print 'DATA preselection sampleRate:',sampleRate,'sampleRateErr=',sampleRateErr,'sampleUnscaledRate=',sampleUnscaledRate
    dataRatesDict = {}
    dataRatesDict['preselection'] = sampleRate
    dataRateErrsDict = {}
    dataRateErrsDict['preselection'] = sampleRateErr
    dataUnscaledRatesDict = {}
    dataUnscaledRatesDict['preselection'] = sampleUnscaledRate
    if blinded:
      dataTotalEvts = -1
    else:
      dataTotalEvts = sampleUnscaledTotalEvts
    # final selections
    for i_signal_name, signal_name in enumerate(signal_names):
        for i_mass_point, mass_point in enumerate(mass_points):
            selectionName = 'LQ'+mass_point
            sampleList = dictSamples['DATA']
            sampleRate = 0
            sampleRateErr = 0
            sampleUnscaledRate = 0
            #print selectionName,'bkg_bame=',bkg_name
            for bkgSample in sampleList:
                bkgUnscaledRootFilename = FindUnscaledSampleRootFile(bkgSample)
                bkgUnscaledRootFile = TFile.Open(bkgUnscaledRootFilename)
                if not bkgUnscaledRootFile:
                  print 'ERROR: file not found:',bkgUnscaledRootFilename
                  exit(-1)
                unscaledTotalEvts = GetUnscaledTotalEvents(bkgUnscaledRootFile)
                sampleUnscaledTotalEvts+=unscaledTotalEvts
                # preselection
                #print '------>Call GetRatesAndErrors for sampleName=',bkgSample
                rate,rateErr,unscaledRate = GetRatesAndErrors(bkgUnscaledRootFile,scaledRootFile,unscaledTotalEvts,bkgSample,selectionName,isData)
                #print '------>rate=',rate,'rateErr=',rateErr,'unscaledRate=',unscaledRate
                #if isQCD:
                #  print 'for sample:',bkgSample,'got unscaled entries=',unscaledRate
                sampleRate+=rate
                sampleUnscaledRate+=unscaledRate
                sampleRateErr+=(rateErr*rateErr)
                bkgUnscaledRootFile.Close()
            sampleRateErr = math.sqrt(sampleRateErr)
            #print 'sampleRate:',sampleRate,'sampleRateErr=',sampleRateErr,'sampleUnscaledRate=',sampleUnscaledRate
            if blinded:
              dataRatesDict[selectionName] = -1
              dataRateErrsDict[selectionName] = 0
              dataUnscaledRatesDict[selectionName] = 0
            else:
              dataRatesDict[selectionName] = sampleRate
              dataRateErrsDict[selectionName] = sampleRateErr
              dataUnscaledRatesDict[selectionName] = sampleUnscaledRate
    # fill full dicts
    bkg_name = 'DATA'
    d_data_rates[bkg_name] = dataRatesDict
    d_data_rateErrs[bkg_name] = dataRateErrsDict
    d_data_unscaledRates[bkg_name] = dataUnscaledRatesDict
    d_data_totalEvents[bkg_name] = dataTotalEvts

    qcdTFile.Close()
    tfile.Close()
  

###################################################################################################
# CONFIGURABLES
###################################################################################################

blinded=True
doEEJJ=False

#mass_points = [str(i) for i in range(300,1550,50)] # go from 300-1500 in 50 GeV steps
#mass_points = [str(i) for i in range(200,1550,50)] # go from 200-1500 in 50 GeV steps
mass_points = [str(i) for i in range(200,2050,50)] # go from 200-2000 in 50 GeV steps
#systematics = [ "jes", "ees", "shape", "norm", "lumi", "eer", "jer", "pu", "ereco", "pdf" ]
if doEEJJ:
  signal_names = [ "LQ_M_" ] 
  systematicsNamesBackground = [ "Trigger", "Reco", "PU", "PDF", "Lumi", "JER", "JEC", "HEEP", "E_scale", "EER", "DYShape", 'DY_Norm', "Diboson_shape" ]
  #background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTBarFromDATA", "ZJet_amcatnlo_ptBinned", "WJet_amcatnlo_ptBinned", "DIBOSON","SingleTop"  ]
  background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTBarFromDATA", "ZJet_amcatnlo_ptBinned", "WJet_amcatnlo_ptBinned", "DIBOSON_amcatnlo","SingleTop" ]
  syst_background_names = ['GJets', 'QCDFakes_DATA', 'TTBarFromDATA', 'DY', 'WJets', 'Diboson', 'Singletop']
  maxLQselectionBkg = 'LQ1200' # max background selection point used
  systematicsNamesSignal = [ "Trigger", "Reco", "PU", "PDF", "Lumi", "JER", "JEC", "HEEP", "E_scale", "EER" ]
else:
  signal_names = [ "LQ_BetaHalf_M_" ] 
  systematicsNamesBackground = [ "Trigger", "Reco", "PU", "PDF", "Lumi", "JER", "JEC", "HEEP", "E_scale", "EER", "MET", "WShape", 'W_Norm', "TTShape", 'TT_Norm', "Diboson_shape" ]
  #background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTbar_amcatnlo_Inc", "ZJet_amcatnlo_ptBinned", "WJet_amcatnlo_ptBinned", "DIBOSON","SingleTop"  ]
  #background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTbar_powheg", "ZJet_amcatnlo_ptBinned", "WJet_amcatnlo_ptBinned", "DIBOSON","SingleTop"  ]
  background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTbar_powheg", "ZJet_amcatnlo_ptBinned", "WJet_amcatnlo_ptBinned", "DIBOSON_amcatnlo","SingleTop" ]
  syst_background_names = ['GJets', 'QCDFakes_DATA', 'TTbar', 'DY', 'WJets', 'Diboson', 'Singletop']
  maxLQselectionBkg = 'LQ900' # max background selection point used
  systematicsNamesSignal = [ "Trigger", "Reco", "PU", "PDF", "Lumi", "JER", "JEC", "HEEP", "E_scale", "EER", "MET" ]

minLQselectionBkg='LQ200'

# add Wjets scale factor norm for enujj
if not doEEJJ:
  #zjetsSF = 0.823
  #zjetsSFerr = 0.008
  zjetsSF = 0.8678
  zjetsSFerrStat = 0.013 # this is taken into account by the norm syst
  zjetsSFerrSystBtag = 0.03 # extra 3% syst from btag SF variation [see Feb 20 result]
  zjetsSFerrSystMT = 0.0 #FIXME
  zjetsSFerr = math.sqrt(pow(zjetsSFerrSystBtag,2)+pow(zjetsSFerrSystMT,2))
  zJetNormDeltaXOverX=zjetsSFerr/zjetsSF
# for ttbar, we have 0.037 stat error on the scale factor of 0.83
# min SF is 0.665 (wrt dataDriven)
# absolute error is 0.165 = nominalSF - minSF
# add in quad with 0.037 -> 0.169
# so we have 0.83 +/- 0.169
# deltaX/X is then 
#ttbarSF = 0.83
#ttbarSFerr = 0.037
#lowestSF = 0.665
#additionalSystAbs = ttbarSF-lowestSF
#totalTTbarNormSystAbs = math.sqrt(ttbarSFerr*ttbarSFerr + additionalSystAbs*additionalSystAbs)
#ttBarNormDeltaXOverX = totalTTbarNormSystAbs/ttbarSF # about 0.2
if doEEJJ:
  ttBarNormDeltaXOverX = 0.01
  ttbarSampleName='TTBarFromDATA'
  ttBarUnscaledRawSampleName='TTBarUnscaledRawFromDATA'
  #nonTTBarSampleName='NONTTBARBKG_amcatnloPt_emujj'
  nonTTBarSampleName='NONTTBARBKG_amcatnloPt_amcAtNLODiboson_emujj'
else:
  ttBarSF = 0.9533
  #ttBarSFErrStat = 0.01
  ttBarSFErrSystBtag = 0.03 # extra 3% syst from btag SF variation [see Feb 20 result]
  #FIXME additional syst?
  ttBarSFErr = math.sqrt(pow(ttBarSFErrSystBtag,2))
  ttBarNormDeltaXOverX = ttBarSFErr/ttBarSF
  ttbarSampleName='TTbar_powheg'
  ttBarUnscaledRawSampleName='TTbar_powheg'
  #nonTTBarSampleName='NONTTBARBKG_amcatnloPt'

# update to 2016 analysis numbers
# QCDNorm is 0.50 [50% norm uncertainty for eejj = uncertaintyPerElectron*2]
if doEEJJ:
  qcdNormDeltaXOverX = 0.50
else:
  qcdNormDeltaXOverX = 0.25

n_background = len ( background_names  )
# all bkg systematics, plus stat 'systs' for all bkg plus signal plus 3 backNormSysts
n_systematics = len ( systematicsNamesBackground ) + n_background + 1 + 3
n_channels = 1

d_background_rates = {}
d_background_rateErrs = {}
d_background_unscaledRates = {}
d_background_totalEvents = {}
d_signal_rates = {}
d_signal_rateErrs = {}
d_signal_unscaledRates = {}
d_signal_totalEvents = {}
d_data_rates = {}
d_data_rateErrs = {}
d_data_unscaledRates = {}
d_data_totalEvents = {}

intLumi = 35867.0

if doEEJJ:
  sampleListForMerging = os.environ["LQANA"]+'/config/sampleListForMerging_13TeV_eejj.txt'
  sampleListForMergingQCD = os.environ["LQANA"]+'/config/sampleListForMerging_13TeV_QCD_dataDriven.txt'
  sampleListForMergingTTBar = os.environ["LQANA"]+'/config/sampleListForMerging_13TeV_ttbarBkg_emujj.txt'
  #inputList = os.environ["LQANA"]+'/config/PSKeejj_oct2_SEleL_reminiaod_v236_eoscms/inputListAllCurrent.txt'
  #xsection = os.environ["LQANA"]+'/versionsOfAnalysis_eejj/sep29_ptEE/unscaled/xsection_13TeV_2015_Mee_PAS.txt'
  #filePath = os.environ["LQDATA"] + '/2016analysis/eejj_psk_oct6_ptEECut_updateFinalSels/output_cutTable_lq_eejj/'
  #qcdFilePath = os.environ["LQDATA"] + '/2016qcd/eejj_psk_oct6_ptEECut_actualUpdateFinalSels/output_cutTable_lq_eejj_QCD/'
  #ttbarFilePath = os.environ["LQDATA"] + '/2016ttbar/oct6_emujj_ptEE_updateFinalSels/output_cutTable_lq_ttbar_emujj_correctTrig/'
  #
  #inputList = os.environ["LQANA"]+'/config/PSKeejj_nov15_SEleL_reminiaod_v236_eoscms_comb/inputListAllCurrent.txt'
  #xsection = os.environ["LQANA"]+'/versionsOfAnalysis_eejj/nov24_muonVeto35GeV/unscaled/xsection_13TeV_2015_Mee_PAS.txt'
  #filePath = os.environ["LQDATA"] + '/2016analysis/eejj_psk_jan20_updateFinalSels/output_cutTable_lq_eejj/'
  #qcdFilePath = os.environ["LQDATA"] + '/2016analysis/eejj_QCD_jan20_finalSels/output_cutTable_lq_eejj_QCD/'
  #ttbarFilePath = os.environ["LQDATA"] + '/2016ttbar/jan20_emujj_correctTrig_finalSelections/output_cutTable_lq_ttbar_emujj_correctTrig/'
  ##filePath = os.environ["LQDATA"] + '/2016analysis/eejj_psk_jan19_updateFinalSels/output_cutTable_lq_eejj/'
  ##qcdFilePath = os.environ["LQDATA"] + '/2016analysis/eejj_QCD_jan19_finalSels/output_cutTable_lq_eejj_QCD/'
  ##ttbarFilePath = os.environ["LQDATA"] + '/2016ttbar/jan19_emujj_correctTrig_finalSelections/output_cutTable_lq_ttbar_emujj_correctTrig/'
  #
  inputList = os.environ["LQANA"]+'/config/PSKeejj_jan22_SEleL_v237_eoscms_comb/inputListAllCurrent.txt'
  #xsection = os.environ["LQANA"]+'/versionsOfAnalysis_eejj/feb1/unscaled/xsection_13TeV_2015_Mee_PAS.txt'
  #filePath = os.environ["LQDATA"] + '/2016analysis/eejj_psk_jan26_gsfEtaCheck_finalSels/output_cutTable_lq_eejj/'
  #qcdFilePath = os.environ["LQDATA"] + '/2016qcd/eejj_QCD_jan26_gsfEtaCheck_finalSels/output_cutTable_lq_eejj_QCD/'
  #ttbarFilePath = os.environ["LQDATA"] + '/2016ttbar/feb2_newSkim_emujj_correctTrig_finalSelections/output_cutTable_lq_ttbar_emujj_correctTrig/'
  #
  #xsection = os.environ["LQANA"]+'/versionsOfAnalysis_eejj/feb11/unscaled/xsection_13TeV_2015_Mee_PAS.txt'
  #filePath = os.environ["LQDATA"] + '/2016analysis/eejj_psk_feb10_bugfix/output_cutTable_lq_eejj/'
  qcdFilePath = os.environ["LQDATA"] + '/2016qcd/eejj_QCD_feb10_bugfix/output_cutTable_lq_eejj_QCD/'
  ttbarFilePath = os.environ["LQDATA"] + '/2016ttbar/feb11_emujj_correctTrig/output_cutTable_lq_ttbar_emujj_correctTrig/'
  filePath = os.environ["LQDATA"] + '/2016analysis/eejj_psk_feb20_newSingTop/output_cutTable_lq_eejj/'
  xsection = os.environ["LQANA"]+'/versionsOfAnalysis_eejj/feb20/unscaled/xsection_13TeV_2015_Mee_PAS.txt'
  # calculated with fitForStatErrs.py script. mass, stat. uncert.
  #statErrorsSingleTop = { 800: 1.10, 850: 0.85, 900: 0.67, 950: 0.53, 1000: 0.42, 1050: 0.33 }
  # here we increased the fit range
  statErrorsPhotonJets = { 400:0.23, 450:0.33 ,500:0.36 ,550:0.35 ,600:0.32 ,650:0.28 ,700:0.24 ,750:0.21 ,800:0.17 ,850:0.14 ,900:0.12 ,950:0.095 ,1000:0.077 ,1050:0.062  }
else:
  sampleListForMerging = os.environ["LQANA"]+'/config/sampleListForMerging_13TeV_enujj.txt'
  sampleListForMergingQCD = os.environ["LQANA"]+'/config/sampleListForMerging_13TeV_QCD_dataDriven.txt'
  inputList = os.environ["LQANA"]+'/config/PSKenujj_oct2_SEleL_reminiaod_v236_eoscms/inputListAllCurrent.txt'
  #xsection = os.environ["LQANA"]+'/versionsOfAnalysis_enujj/oct6_finerTrigEff/unscaled/btagCR/xsection_13TeV_2015_TTbarRescale_WJetsRescale.txt'
  #xsection = os.environ["LQANA"]+'/versionsOfAnalysis_enujj/oct6_finerTrigEff/unscaled/njetCR/xsection_13TeV_2015_TTbarRescale_WJetsRescale.txt'
  #filePath = os.environ["LQDATA"] + '/2016analysis/enujj_psk_oct6_finerBinnedTrigEff_updateFinalSels/output_cutTable_lq_enujj_MT/'
  #qcdFilePath = os.environ["LQDATA"] + '/2016qcd/enujj_psk_oct6_updateFinalSels/output_cutTable_lq_enujj_MT_QCD/'
  #filePath = os.environ["LQDATA"] + '/2016analysis/enujj_psk_sep13_ele27wptightOREle115ORPhoton175_enujjPowhegOptFinalSels/output_cutTable_lq_enujj_MT/'
  #qcdFilePath = os.environ["LQDATA"] + '/2016qcd/enujj_psk_jul1_ele27wptightOREle115ORPhoton175_enujjOptFinalSels/output_cutTable_lq_enujj_MT_QCD/'
  #
  #filePath = os.environ["LQDATA"] + '/2016analysis/enujj_psk_jan20_usePtHeep_finalSels/output_cutTable_lq_enujj_MT/'
  #xsection = os.environ["LQANA"]+'/versionsOfAnalysis_enujj/jan17/unscaled/xsection_13TeV_2015_TTbarRescale_WJetsRescale.txt'
  #qcdFilePath = os.environ["LQDATA"] + '/2016qcd/enujj_newRsk237_jan20_finalSels/output_cutTable_lq_enujj_MT_QCD/'
  #
  #filePath = os.environ["LQDATA"] + '/2016analysis/enujj_psk_feb4_v237_MET100_PtEMET70/output_cutTable_lq_enujj_MT/'
  #xsection = os.environ["LQANA"]+'/versionsOfAnalysis_enujj/feb4_ptEMet/unscaled/xsection_13TeV_2015_TTbarRescale_WJetsRescale.txt'
  #qcdFilePath = os.environ["LQDATA"] + '/2016qcd/enujj_newRsk237_feb4_gsfEtaCheck_MET100_PtEMET70/output_cutTable_lq_enujj_MT_QCD/'
  #
  #filePath = os.environ["LQDATA"] + '/2016analysis/enujj_psk_feb10_v237_bugfix/output_cutTable_lq_enujj_MT/'
  #xsection = os.environ["LQANA"]+'/versionsOfAnalysis_enujj/feb11/unscaled/xsection_13TeV_2015_MTenu_50_110_gteOneBtaggedJet_TTbar_MTenu_50_110_noBtaggedJets_WJets.txt'
  #qcdFilePath = os.environ["LQDATA"] + '/2016qcd/enujj_feb10_bugfix//output_cutTable_lq_enujj_MT_QCD/'
  #
  #filePath = os.environ["LQDATA"] + '/2016analysis/enujj_psk_feb14_dPhiEleMet0p8/output_cutTable_lq_enujj_MT/'
  #xsection = os.environ["LQANA"]+'/versionsOfAnalysis_enujj/feb14/unscaled/xsection_13TeV_2015_MTenu_50_110_gteOneBtaggedJet_TTbar_MTenu_50_110_noBtaggedJets_WJets.txt'
  #qcdFilePath = os.environ["LQDATA"] + '/2016qcd/enujj_feb14_dPhiEleMET0p8/output_cutTable_lq_enujj_MT_QCD/'
  #
  filePath = os.environ["LQDATA"] + '/2016analysis/enujj_psk_feb20_dPhiEleMet0p8_newSingTop/output_cutTable_lq_enujj_MT/'
  xsection = os.environ["LQANA"]+'/versionsOfAnalysis_enujj/feb20/unscaled/xsection_13TeV_2015_MTenu_50_110_gteOneBtaggedJet_TTbar_MTenu_50_110_noBtaggedJets_WJets.txt'
  qcdFilePath = os.environ["LQDATA"] + '/2016qcd/enujj_feb14_dPhiEleMET0p8/output_cutTable_lq_enujj_MT_QCD/'
  ## calculated with fitForStatErrs.py script. mass, stat. uncert.
  #statErrorsSingleTop = { 650:0.213, 700:0.330, 750:0.399, 800:0.431, 850:0.442, 900:0.438, 950:0.425, 1000:0.407, 1050:0.385, 1100:0.363, 1150:0.342, 1200:0.321 }

# this has the TopPtReweight+updatedSF and the Z+jets St corrections at final selections
#filePath = os.environ["LQDATA"] + '/RunII/eejj_analysis_zJetsStCorrectionFinalSelections_21jul/output_cutTable_lq_eejj/'

dataMC_filepath   = filePath+('analysisClass_lq_eejj_plots.root' if doEEJJ else 'analysisClass_lq_enujj_MT_plots.root')
qcd_data_filepath = qcdFilePath+('analysisClass_lq_eejj_QCD_plots.root' if doEEJJ else 'analysisClass_lq_enujj_QCD_plots.root')
if doEEJJ:
  ttbar_data_filepath = ttbarFilePath+'analysisClass_lq_ttbarEst_plots.root'
else:
  ttbar_data_filepath = ''
  #ttbarFilePath = filePath
systematics_filepaths = {}
for systName in systematicsNamesBackground:
  if doEEJJ:
    systematics_filepaths[systName] = '/afs/cern.ch/user/m/mbhat/work/public/Systematics_4eejj_DibosonAMCATNLO_18_02_2018/'
    #systematics_filepaths[systName] = '/afs/cern.ch/user/m/mbhat/work/public/Systematics_4eejj_05_09_2017/'
    #systematics_filepaths[systName] = '/afs/cern.ch/user/m/mbhat/work/public/Systematics_txtfiles_20_07_2016/'
  #systematics_filepaths['EER'] = '/afs/cern.ch/user/m/mbhat/work/public/Systematics_textfiles_28_07_2016/'
  else:
    systematics_filepaths[systName] = '/afs/cern.ch/user/m/mbhat/work/public/Systematics_4enujj_DibosonamcATnlo_18_02_2018/'
    #systematics_filepaths[systName] = '/afs/cern.ch/user/m/mbhat/work/public/Systematics_4enujj_1_09_2017/'


###################################################################################################
# RUN
###################################################################################################

#---Check if sampleListForMerging file exist
if(os.path.isfile(sampleListForMerging) == False):
    print "ERROR: file " + sampleListForMerging + " not found"
    print "exiting..."
    sys.exit()

#---Check if sampleListForMergingQCD file exist
if(os.path.isfile(sampleListForMergingQCD) == False):
    print "ERROR: file " + sampleListForMergingQCD + " not found"
    print "exiting..."
    sys.exit()

#---Check if xsection file exist
if(os.path.isfile(xsection) == False):
    print "ERROR: file " + xsection + " not found"
    print "exiting..."
    sys.exit()

print 'Launched like:'
for arg in sys.argv:
  print '\t'+arg
print 'Using tables:'
print '\t Data/MC:',dataMC_filepath
print '\t QCD(data):',qcd_data_filepath
print 'Using systematics files:',systematics_filepaths

# get xsections
xsectionDict = ParseXSectionFile(xsection)
dictSamples = GetSamplesToCombineDict(sampleListForMerging)
dictSamplesQCD  = GetSamplesToCombineDict(sampleListForMergingQCD)
dictSamples.update(dictSamplesQCD)
if doEEJJ:
  dictSamplesTTBarRaw = GetSamplesToCombineDict(sampleListForMergingTTBar)
  # only care about the TTBar parts
  dictSamplesTTBar = {}
  #for key in dictSamplesTTBarRaw.iterkeys():
  #  if 'ttbar' in key.lower():
  #    if 'ttbarunscaledrawfromdata' in key.lower():
  #      print 'set dictSamplesTTBar[TTBarFromDATA] =',dictSamplesTTBarRaw[key],'for key:',key
  #      dictSamplesTTBar['TTBarFromDATA'] = dictSamplesTTBarRaw[key]
  # NB: we rely on this exact sample name for the total TTBar data-driven sample
  #dictSamplesTTBar['TTBarFromDATA'] = dictSamplesTTBarRaw['TTBarUnscaledRawFromDATA']
  #dictSamplesTTBar['TTBarFromDATA'] = ['TTBarFromDATA']
  dictSamplesTTBar[ttbarSampleName] = [ttbarSampleName]
  dictSamples.update(dictSamplesTTBar)
  print 'found ttbar samples:',dictSamplesTTBar

# check to make sure we have xsections for all samples
for lin in open( inputList ):
    lin = string.strip(lin,"\n")
    if lin.startswith('#'):
      continue
    dataset_fromInputList = string.split( string.split(lin, "/" )[-1], ".")[0]
    xsection_val = lookupXSection(SanitizeDatasetNameFromInputList(dataset_fromInputList),xsectionDict)


# rates/etc.
FillDicts(dataMC_filepath,qcd_data_filepath,ttbar_data_filepath)
# systematics
backgroundSystDict = FillSystDicts(systematicsNamesBackground)
signalSystDict = FillSystDicts(systematicsNamesSignal,False)
# print one of them for checking
#for syst in backgroundSystDict.keys():
#    print 'Syst is:',syst
#    print 'selection\t\tvalue'
#    for selection in sorted(backgroundSystDict[syst].keys()):
#        print selection+'\t\t'+str(backgroundSystDict[syst][selection])
#    break
#print signalSystDict
#print backgroundSystDict

card_file_path = "tmp_card_file.txt"
card_file = open ( card_file_path, "w" ) 

for i_signal_name, signal_name in enumerate(signal_names):
    for i_mass_point, mass_point in enumerate(mass_points):
        fullSignalName = signal_name + mass_point
        selectionName = 'LQ'+mass_point
        
        txt_file_name = fullSignalName + ".txt\n"

        card_file.write ( txt_file_name + "\n\n" )
        card_file.write ( "imax " + str ( n_channels    ) + "\n" ) 
        card_file.write ( "jmax " + str ( n_background  ) + "\n" ) 
        card_file.write ( "kmax " + str ( n_systematics ) + "\n\n" ) 
        
        #card_file.write ( "bin 1\n\n" )
        card_file.write ( "bin bin1\n\n" )

        #XXX FiXME TODO handle betaHalf data somehow
        if "BetaHalf" in signal_name: 
            if blinded:
              card_file.write ( "observation " + str ( -1 ) + "\n\n" )
            else:
              #total_data = enujj_data["DATA"][i_mass_point]
              total_data = d_data_rates["DATA"][selectionName]
              card_file.write ( "observation " + str ( total_data ) + "\n\n" )
        else : 
            if blinded:
              card_file.write ( "observation " + str ( -1 ) + "\n\n" )
            else:
              total_data = d_data_rates["DATA"][selectionName]
              card_file.write ( "observation " + str ( total_data ) + "\n\n" )
        
        line = "bin " 
        for i_channel in range (0, n_background + 1) :
            #line = line + "1 " 
            line = line + "bin1 " 
        card_file.write (line + "\n") 

        line = "process " + signal_name + mass_point + " "
        for background_name in background_names:
            line = line + background_name + " "
        card_file.write (line + "\n") 

        line = "process 0 "
        for background_name in background_names:
            line = line + "1 "
        card_file.write (line + "\n\n") 

        # rate line
        line = "rate "
        total_bkg = 0.0
        total_signal = d_signal_rates[fullSignalName][selectionName]
        line = line + str(total_signal) + " "
        for ibkg,background_name in enumerate(background_names):
            thisBkgEvts = d_background_rates[background_name][selectionName]
            line += str(thisBkgEvts) + " "
            total_bkg += float(thisBkgEvts) 
        card_file.write ( line + "\n\n")

        #print signal_name, mass_point, total_signal, total_bkg, total_data
        #print signal_name+str(mass_point), total_signal, total_bkg

        # recall the form: signal --> sysDict['Trigger']['LQXXXX'] = value
        #             backgrounds --> sysDict['Trigger'][bkgName]['LQXXXX'] = value
        for syst in signalSystDict.keys():
            line = syst + ' lnN '
            if selectionName not in signalSystDict[syst].keys():
                selectionNameSigSyst = maxLQselectionBkg
            else:
                selectionNameSigSyst = selectionName
            line += str(1+signalSystDict[syst][selectionNameSigSyst])
            line += ' '
            #else:
            #    print 'ERROR: could not find syst "',syst,'" in signalSystDict.keys():',signalSystDict.keys()
            for ibkg,background_name in enumerate(syst_background_names):
                #print 'try to lookup backgroundSystDict['+syst+']['+background_name+']['+selectionName+']'
                #print 'syst="'+syst+'"'
                if background_name=='' or 'QCD' in background_name or 'TTBarFromDATA' in background_name:
                    #print 'empty background_name; use - and continue'
                    line += ' - '
                    continue
                if selectionName not in backgroundSystDict[syst][background_name].keys():
                    selectionNameBkgSyst = maxLQselectionBkg
                else:
                    selectionNameBkgSyst = selectionName
                try:
                  line += str(1+backgroundSystDict[syst][background_name][selectionNameBkgSyst])+' '
                except KeyError:
                    print 'Got a KeyError with: backgroundSystDict['+syst+']['+background_name+']['+selectionNameBkgSyst+']'
            card_file.write(line+'\n')

        # background-only special systs: "DYShape", "TTShape"
        specialSysts = ["DYShape",'DY_Norm','Diboson_shape'] if doEEJJ else ["WShape","TTShape",'W_Norm','TT_Norm','Diboson_shape']
        for syst in specialSysts:
            line = syst + ' lnN - '
            for ibkg,background_name in enumerate(syst_background_names):
                if 'TTBarFromDATA' in background_name or 'DY' in syst and not 'DY' in background_name or 'TT' in syst and not 'TT' in background_name or 'W' in syst and not 'W' in background_name or 'Diboson' in syst and not 'Diboson' in background_name:
                    #print 'empty background_name; use - and continue'
                    line += ' - '
                    continue
                try:
                  selections = backgroundSystDict[syst][background_name].keys()
                except KeyError:
                  print 'Got a KeyError with: backgroundSystDict['+syst+']['+background_name+']'
                  print 'backgroundSystDict.keys()=',backgroundSystDict.keys()
                  print 'backgroundSystDict['+syst+']=',backgroundSystDict[syst]
                  print 'backgroundSystDict['+syst+'].keys()=',backgroundSystDict[syst].keys()
                if selectionName not in backgroundSystDict[syst][background_name].keys():
                    selectionNameBkgSyst = maxLQselectionBkg
                else:
                    selectionNameBkgSyst = selectionName
                try:
                  line += str(1+backgroundSystDict[syst][background_name][selectionNameBkgSyst])+' '
                except KeyError:
                    print 'Got a KeyError with: backgroundSystDict['+syst+']['+background_name+']['+selectionNameBkgSyst+']'
            card_file.write(line+'\n')
        
        # background norm systs
        foundTTBar = False
        foundZJet = False if not doEEJJ else True
        foundQCD = False
        for ibkg,background_name in enumerate(syst_background_names):
            # XXX WARNING: hardcoded background name (ick); some checking is done at least
            if 'ttbar' in background_name.lower() and not foundTTBar:
                line = 'norm_ttbar lnN - '
                line += ' - '*(ibkg)
                line += str(1+ttBarNormDeltaXOverX)+' '
                line += ' - '*(len(syst_background_names)-ibkg-1)+'\n'
                card_file.write(line)
                foundTTBar = True
            elif not doEEJJ and 'W' in background_name and not foundZJet:
                line = 'norm_wjet lnN - '
                line += ' - '*(ibkg)
                line += str(1+zJetNormDeltaXOverX)+' '
                line += ' - '*(len(syst_background_names)-ibkg-1)+'\n'
                card_file.write(line)
                foundZJet = True
            elif 'QCD' in background_name and not foundQCD:
                line = 'norm_QCD lnN - '
                line += ' - '*(ibkg)
                line += str(1+qcdNormDeltaXOverX)+' '
                line += ' - '*(len(syst_background_names)-ibkg-1)+'\n'
                card_file.write(line)
                foundQCD = True
        if not foundTTBar or not foundZJet or not foundQCD:
            print 'ERROR: could not find one or more of [ttbar,zjet/wjet,QCD] background names for normalization syst; check background names'
            exit(-1)

        card_file.write("\n")

        # background stat error part
        for i_background_name ,background_name in enumerate(background_names):
            thisBkgEvts = d_background_rates[background_name][selectionName]
            thisBkgEvtsErr = d_background_rateErrs[background_name][selectionName]
            thisBkgTotalEntries = d_background_unscaledRates[background_name][selectionName]
            forceLogNorm = False

            if thisBkgEvts != 0.0: 
                lnN_f = 1.0 + 1.0/math.sqrt(thisBkgTotalEntries+1) # Poisson becomes Gaussian, approx by logN with this kappa
                gmN_weight = thisBkgEvts / thisBkgTotalEntries # for small uncertainties, use gamma distribution with alpha=(factor to go to signal region from control/MC)
                #if not doEEJJ and background_name=='SingleTop' and int(selectionName.replace('LQ','')) >= 650:
                #   statErr = GetStatErrorFromDict(statErrorsSingleTop,int(selectionName.replace('LQ','')))
                #   lnN_f = 1.0 + statErr/thisBkgEvts
                #   forceLogNorm = True
            else: 
                # for small uncertainties, use gamma distribution with alpha=(factor to go to signal region from control/MC)
                # since we can't compute evts/entries, we use it from the preselection (following LQ2)
                #gmN_weight = d_background_rates[background_name]['preselection'] / d_background_unscaledRates[background_name]['preselection']
                # change: find last selection with at least 1 bkg event and use its scale factor
                massPointsRev = list(reversed(mass_points))
                idx = 0
                bkgRate = 0
                while bkgRate==0:
                  lastSelectionName = 'LQ'+massPointsRev[idx]
                  bkgEvents = d_background_unscaledRates[background_name][lastSelectionName]
                  bkgRate = d_background_rates[background_name][lastSelectionName]
                  idx+=1
                print 'INFO: for background:',background_name,'at selection:',selectionName,'found last selection:',lastSelectionName,'with',bkgEvents,'unscaled MC events. use this for the scale factor.'
                gmN_weight = bkgRate / bkgEvents

                ## special handling of stat errors for small backgrounds
                #if doEEJJ and background_name=='SingleTop':
                #    gmN_weight = GetStatErrorFromDict(statErrorsSingleTop,int(selectionName.replace('LQ','')))
                if doEEJJ and background_name=='PhotonJets_Madgraph':
                    gmN_weight = GetStatErrorFromDict(statErrorsPhotonJets,int(selectionName.replace('LQ','')))

            
            line_ln = "stat_" + background_name + " lnN -"
            line_gm = "stat_" + background_name + " gmN " + str(int(thisBkgTotalEntries)) + " -"
            for i_tmp in range ( 0, i_background_name ):
                line_ln = line_ln + " -"
                line_gm = line_gm + " -"
            line_ln = line_ln + " " + str(lnN_f)
            line_gm = line_gm + " " + str(gmN_weight)
            for i_tmp in range ( i_background_name, len(background_names) -1 ):
                line_ln = line_ln + " -"
                line_gm = line_gm + " -"

            if thisBkgTotalEntries > 10 or forceLogNorm:
                card_file.write (line_ln + "\n")
            else:
                card_file.write (line_gm + "\n")
            #if background_name=='TTbar_Madgraph':
            #    print 'selectionName=',selectionName
            #    print 'thisBkgEvts=',thisBkgEvts
            #    print 'thisBkgEvtsErr=',thisBkgEvtsErr
            #    print 'thisBkgTotalEntries=',thisBkgTotalEntries
            #    print 'line_gm=',line_gm
            
        # signal stat error part
        # always use lnN error
        thisSigEvts = d_signal_rates[fullSignalName][selectionName]
        thisSigEvtsErr = d_signal_rateErrs[fullSignalName][selectionName]
        thisSigTotalEntries =d_signal_unscaledRates[fullSignalName][selectionName]
        #if thisSigEvts == 0.0: 
        #  print 'ERROR: signal events for this signal (',fullSignalName,'came out to be zero...stat error not supported. Quitting!'
        #  exit(-1)
        if thisSigEvts != 0.0:
          lnN_f = 1.0 + 1.0/math.sqrt(thisSigTotalEntries+1) # Poisson becomes Gaussian, approx by logN with this kappa
          gmN_weight = thisSigEvts / thisSigTotalEntries
        else:
          # THIS IS BROKEN FIXME ???
          gmN_weight = d_signal_rates[background_name]['preselection'] / d_signal_unscaledRates[background_name]['preselection']
        line_ln = "stat_Signal lnN " + str(lnN_f)
        line_gm = "stat_Signal gmN " + str(int(thisBkgTotalEntries)) + " " + str(gmN_weight)
        for i_background_name ,background_name in enumerate(background_names):
            line_ln = line_ln + " -"
            line_gm = line_ln + " -"
        if thisSigTotalEntries > 10:
            card_file.write (line_ln + "\n")
        else:
            card_file.write (line_gm + "\n")

        # DONE!
        card_file.write("\n\n\n")

print 'datacard written to:',card_file_path

# make final selection tables
if doEEJJ:
  #columnNames = ['MLQ','signal','Z+jets','ttbar(data)','QCD(data)','Other','Total BG','Data']
  columnNames = ['MLQ','signal','Z+jets','ttbar(data)','QCD(data)','DIBOSON','SingleTop','W+Jets','PhotonJets','Total BG','Data']
else:
  #columnNames = ['MLQ','signal','W+jets','ttbar(powheg)','QCD(data)','Other','Total BG','Data']
  columnNames = ['MLQ','signal','W+jets','ttbar(powheg)','QCD(data)','DIBOSON','SingleTop','Z+Jets','PhotonJets','Total BG','Data']
## FOR TESTING
#columnNames = ['MLQ']
#for bn in background_names:
#  columnNames.append(bn)
if doEEJJ:
  otherBackgrounds = ['PhotonJets_Madgraph','WJet_amcatnlo_ptBinned','DIBOSON_amcatnlo','SingleTop']
else:
  otherBackgrounds = ['PhotonJets_Madgraph','ZJet_amcatnlo_ptBinned','DIBOSON_amcatnlo','SingleTop']
#background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTbar_Madgraph", "WJet_Madgraph_HT", "ZJet_Madgraph_HT", "DIBOSON","SingleTop"  ]
latexRowsAN = []
latexRowsPaper = []
t = PrettyTable(columnNames)
t.float_format = "4.3"
selectionNames = ['LQ'+mass_point for mass_point in mass_points]
selectionNames.insert(0,'preselection')
for i_signal_name, signal_name in enumerate(signal_names):
    for selectionName in selectionNames:
        massPoint = selectionName.replace('LQ','')
        fullSignalName = signal_name + massPoint
        # signal events
        thisSigEvts = '-'
        thisSigEvtsErr = '-'
        #print 'selectionName=',selectionName
        if selectionName!='preselection':
            thisSigEvts = d_signal_rates[fullSignalName][selectionName]
            thisSigEvtsErr = d_signal_rateErrs[fullSignalName][selectionName]
        #print 'd_data_rates[data]['+selectionName+']'
        thisDataEvents = d_data_rates['DATA'][selectionName]
        backgroundEvts = {}
        backgroundEvtsErrUp = {}
        backgroundEvtsErrDown = {}
        backgroundEvtsErrIsAsymm = {}
        totalBackground = 0.0
        totalBackgroundErrStatUp = 0.0
        totalBackgroundErrStatDown = 0.0
        totalBackgroundErrSyst = 0.0
        otherBackground = 0.0
        otherBackgroundErrStatUp = 0.0
        otherBackgroundErrStatDown = 0.0
        for i_background_name ,background_name in enumerate(background_names):
            thisBkgEvts = d_background_rates[background_name][selectionName]
            thisBkgEvtsErr = d_background_rateErrs[background_name][selectionName]
            thisBkgEvtsErrUp = d_background_rateErrs[background_name][selectionName]
            thisBkgEvtsErrDown = thisBkgEvtsErrUp
            thisBkgTotalEntries = d_background_unscaledRates[background_name][selectionName]
            backgroundEvtsErrIsAsymm[background_name] = False
            print 'INFO:  for selection:',selectionName,' and background:',background_name,' total unscaled events=',thisBkgTotalEntries
            forceSymmErr = False
            if thisBkgTotalEntries <= 10.0:
                if thisBkgEvts > 0.0:
                    thisBkgEvtsErrUp,thisBkgEvtsErrDown = GetStatErrors(thisBkgTotalEntries,thisBkgEvts/thisBkgTotalEntries,thisBkgEvts)
                    if thisBkgTotalEntries < 5:
                      print 'INFO:  using:',background_name,': thisBkgTotalEntries=',thisBkgTotalEntries,'selection',selectionName,' thisBkgEvts=',thisBkgEvts,'thisBkgEvtsErr=',thisBkgEvtsErr
                      print 'INFO:      thisBkgEvtsErrUp=',thisBkgEvtsErrUp,'; thisBkgEvtsErrDown=',thisBkgEvtsErrDown,'nevts=',thisBkgTotalEntries,'theta=',thisBkgEvts/thisBkgTotalEntries
                    if thisBkgEvtsErrUp < 0 or thisBkgEvtsErrDown < 0:
                        print 'ERROR:  thisBkgEvtsErrUp=',thisBkgEvtsErrUp,'; thisBkgEvtsErrDown=',thisBkgEvtsErrDown,'nevts=',thisBkgTotalEntries,'theta=',thisBkgEvts/thisBkgTotalEntries
                        print 'ERROR:      using:',background_name,': selection',selectionName,'thisBkgEvts=',thisBkgEvts,'thisBkgTotalEntries=',thisBkgTotalEntries,'thisBkgEvtsErr=',thisBkgEvtsErr
                        #exit(-1)
                    ## special fit extrap errors
                    #if not doEEJJ and background_name=='SingleTop' and int(selectionName.replace('LQ','')) >= 650:
                    #   thisBkgEvtsErrUp = GetStatErrorFromDict(statErrorsSingleTop,int(selectionName.replace('LQ','')))
                    #   thisBkgEvtsErrDown = thisBkgEvtsErrUp
                    #   forceSymmErr = True
                else:
                    massPointsRev = list(reversed(mass_points))
                    idx = 0
                    bkgRate = 0
                    while bkgRate==0:
                      lastSelectionName = 'LQ'+massPointsRev[idx]
                      bkgEvents = d_background_unscaledRates[background_name][lastSelectionName]
                      bkgRate = d_background_rates[background_name][lastSelectionName]
                      idx+=1
                    print 'INFO: for background:',background_name,'at selection:',selectionName,'found last selection:',lastSelectionName,'with',bkgEvents,'unscaled MC events. use this for the scale factor.'
                    rateOverUnscaledRatePresel = bkgRate/bkgEvents
                    #print 'Call GetStatErrors(',thisBkgTotalEntries,rateOverUnscaledRatePresel,thisBkgEvts,')'
                    thisBkgEvtsErrUp,thisBkgEvtsErrDown = GetStatErrors(thisBkgTotalEntries,rateOverUnscaledRatePresel,thisBkgEvts)
                    ## special handling of stat errors for small backgrounds
                    #if doEEJJ and background_name=='SingleTop':
                    #    thisBkgEvtsErrDown=0
                    #    thisBkgEvtsErrUp = GetStatErrorFromDict(statErrorsSingleTop,int(selectionName.replace('LQ','')))
                    if doEEJJ and background_name=='PhotonJets_Madgraph':
                        thisBkgEvtsErrDown=0
                        thisBkgEvtsErrUp = GetStatErrorFromDict(statErrorsPhotonJets,int(selectionName.replace('LQ','')))
                    print 'INFO:  using:',background_name,': selection',selectionName,' thisBkgEvts=',thisBkgEvts,'thisBkgTotalEntries=',thisBkgTotalEntries,'thisBkgEvtsErr=',thisBkgEvtsErr
                    print 'INFO:      thisBkgEvtsErrUp=',thisBkgEvtsErrUp,'; thisBkgEvtsErrDown=',thisBkgEvtsErrDown,'nevts=',thisBkgTotalEntries,'theta=',rateOverUnscaledRatePresel,'[preselection]'
                    if thisBkgEvtsErrUp < 0 or thisBkgEvtsErrDown < 0:
                        print 'ERROR:  thisBkgEvtsErrUp=',thisBkgEvtsErrUp,'; thisBkgEvtsErrDown=',thisBkgEvtsErrDown,'nevts=',thisBkgTotalEntries,'theta=',rateOverUnscaledRatePresel,'[preselection]'
                        print 'ERROR:      using:',background_name,': selection',selectionName,' thisBkgEvts=',thisBkgEvts,'thisBkgTotalEntries=',thisBkgTotalEntries,'thisBkgEvtsErr=',thisBkgEvtsErr
                        #exit(-1)
                #rateOverUnscaledRatePresel = d_background_rates[background_name]['preselection'] / d_background_unscaledRates[background_name]['preselection']
                #thisBkgEvtsErrUp,thisBkgEvtsErrDown = GetStatErrors(thisBkgTotalEntries,rateOverUnscaledRatePresel)
                ##rateOverUnscaledRatePresel = d_background_rates[background_name]['preselection'] / d_background_unscaledRates[background_name]['preselection']
                ##thisBkgEvtsErrUp *= rateOverUnscaledRatePresel
                ##thisBkgEvtsErrDown *= rateOverUnscaledRatePresel
                backgroundEvtsErrIsAsymm[background_name] = True if not forceSymmErr else False
                backgroundEvtsErrUp[background_name] = thisBkgEvtsErrUp
                backgroundEvtsErrDown[background_name] = thisBkgEvtsErrDown
                #print background_name,': selection',selectionName,'rateOverUnscaledRatePresel=',rateOverUnscaledRatePresel,'thisBkgEvtsErr=',thisBkgEvtsErr
            thisBkgSyst = GetBackgroundSyst(syst_background_names[i_background_name],selectionName)
            thisBkgSystErr = thisBkgEvts*thisBkgSyst
            totalBackground+=thisBkgEvts
            totalBackgroundErrStatUp+=(thisBkgEvtsErrUp*thisBkgEvtsErrUp)
            totalBackgroundErrStatDown+=(thisBkgEvtsErrDown*thisBkgEvtsErrDown)
            totalBackgroundErrSyst+=(thisBkgSystErr*thisBkgSystErr)
            print 'background:',background_name,'thisBkgEvents =',thisBkgEvts,'+',thisBkgEvtsErrUp,'-',thisBkgEvtsErrDown,'GetBackgroundSyst(syst_background_names['+str(i_background_name)+'],'+selectionName+')=',thisBkgSyst
            #if selectionName=='preselection':
            #  print 'background:',background_name,'thisBkgEvents =',thisBkgEvts,'GetBackgroundSyst(syst_background_names['+str(i_background_name)+'],'+selectionName+')=',thisBkgSyst
            #  print 'thisBkgSystErr=',math.sqrt(thisBkgSystErr)
            #  print 'updated totalBackgroundErrSyst',math.sqrt(totalBackgroundErrSyst)
            #  #print 'totalBackgound=',totalBackground
            if background_name in otherBackgrounds:
              otherBackground+=thisBkgEvts
              otherBackgroundErrStatUp+=(thisBkgEvtsErrUp*thisBkgEvtsErrUp)
              otherBackgroundErrStatDown+=(thisBkgEvtsErrDown*thisBkgEvtsErrDown)
            if thisBkgEvts < 0:
              print 'WARNING: Found',thisBkgEvts,'events for',background_name,'; setting to zero'
              thisBkgEvts = 0.0
            backgroundEvts[background_name] = thisBkgEvts
            backgroundEvtsErrUp[background_name] = thisBkgEvtsErrUp
            backgroundEvtsErrDown[background_name] = thisBkgEvtsErrDown
        totalBackgroundErrStatUp = math.sqrt(totalBackgroundErrStatUp)
        totalBackgroundErrStatDown = math.sqrt(totalBackgroundErrStatDown)
        totalBackgroundErrSyst = math.sqrt(totalBackgroundErrSyst)
        otherBackgroundErrStatUp = math.sqrt(otherBackgroundErrStatUp)
        otherBackgroundErrStatDown = math.sqrt(otherBackgroundErrStatDown)
        row = [selectionName]
        # test to see all backgrounds
        #for bn in background_names:
        #  row.append(GetTableEntryStr(backgroundEvts[bn],backgroundEvtsErrUp[bn],backgroundEvtsErrDown[bn]))
        # actual
        row = [selectionName,
            GetTableEntryStr(thisSigEvts,thisSigEvtsErr,thisSigEvtsErr), # assumes we always have > 0 signal events
            ]
        if doEEJJ:
          row.extend([
            GetTableEntryStr(backgroundEvts['ZJet_amcatnlo_ptBinned'],backgroundEvtsErrUp['ZJet_amcatnlo_ptBinned'],backgroundEvtsErrDown['ZJet_amcatnlo_ptBinned']),
            GetTableEntryStr(backgroundEvts['TTBarFromDATA'],backgroundEvtsErrUp['TTBarFromDATA'],backgroundEvtsErrDown['TTBarFromDATA'])
            ])
        else:
          row.extend([
            GetTableEntryStr(backgroundEvts['WJet_amcatnlo_ptBinned'],backgroundEvtsErrUp['WJet_amcatnlo_ptBinned'],backgroundEvtsErrDown['WJet_amcatnlo_ptBinned']),
            #GetTableEntryStr(backgroundEvts['TTbar_amcatnlo_Inc'],backgroundEvtsErrUp['TTbar_amcatnlo_Inc'],backgroundEvtsErrDown['TTbar_amcatnlo_Inc'])
            GetTableEntryStr(backgroundEvts['TTbar_powheg'],backgroundEvtsErrUp['TTbar_powheg'],backgroundEvtsErrDown['TTbar_powheg'])
            ])
        row.extend([
            GetTableEntryStr(backgroundEvts['QCDFakes_DATA'],backgroundEvtsErrUp['QCDFakes_DATA'],backgroundEvtsErrDown['QCDFakes_DATA']),
            #GetTableEntryStr(otherBackground,otherBackgroundErrStatUp,otherBackgroundErrStatDown),
            GetTableEntryStr(backgroundEvts['DIBOSON_amcatnlo'],backgroundEvtsErrUp['DIBOSON_amcatnlo'],backgroundEvtsErrDown['DIBOSON_amcatnlo']),
            GetTableEntryStr(backgroundEvts['SingleTop'],backgroundEvtsErrUp['SingleTop'],backgroundEvtsErrDown['SingleTop']),
            ])
        if doEEJJ:
            row.append(GetTableEntryStr(backgroundEvts['WJet_amcatnlo_ptBinned'],backgroundEvtsErrUp['WJet_amcatnlo_ptBinned'],backgroundEvtsErrDown['WJet_amcatnlo_ptBinned']))
        else:
            row.append(GetTableEntryStr(backgroundEvts['ZJet_amcatnlo_ptBinned'],backgroundEvtsErrUp['ZJet_amcatnlo_ptBinned'],backgroundEvtsErrDown['ZJet_amcatnlo_ptBinned']))
        row.extend([
          GetTableEntryStr(backgroundEvts['PhotonJets_Madgraph'],backgroundEvtsErrUp['PhotonJets_Madgraph'],backgroundEvtsErrDown['PhotonJets_Madgraph']),
          GetTableEntryStr(totalBackground,totalBackgroundErrStatUp,totalBackgroundErrStatDown,totalBackgroundErrSyst),
          GetTableEntryStr(thisDataEvents),
          ])
        t.add_row(row)
        # latex tables
        latexRow = [selectionName.replace('LQ',''),
            GetTableEntryStr(thisSigEvts,thisSigEvtsErr,thisSigEvtsErr,latex=True), # assumes we always have > 0 signal events
            ]
        if doEEJJ:
          latexRow.extend([
            GetTableEntryStr(backgroundEvts['ZJet_amcatnlo_ptBinned'],backgroundEvtsErrUp['ZJet_amcatnlo_ptBinned'],backgroundEvtsErrDown['ZJet_amcatnlo_ptBinned'],latex=True),
            GetTableEntryStr(backgroundEvts['TTBarFromDATA'],backgroundEvtsErrUp['TTBarFromDATA'],backgroundEvtsErrDown['TTBarFromDATA'],latex=True)
            ])
        else:
          latexRow.extend([
            GetTableEntryStr(backgroundEvts['WJet_amcatnlo_ptBinned'],backgroundEvtsErrUp['WJet_amcatnlo_ptBinned'],backgroundEvtsErrDown['WJet_amcatnlo_ptBinned'],latex=True),
            #GetTableEntryStr(backgroundEvts['TTbar_amcatnlo_Inc'],backgroundEvtsErrUp['TTbar_amcatnlo_Inc'],backgroundEvtsErrDown['TTbar_amcatnlo_Inc'],latex=True)
            GetTableEntryStr(backgroundEvts['TTbar_powheg'],backgroundEvtsErrUp['TTbar_powheg'],backgroundEvtsErrDown['TTbar_powheg'],latex=True)
            ])
        latexRowPaper = list(latexRow) # copy the list
        # for the paper, we want VV, W/Z, single t, GJets in a single column; then background and data
        latexRowPaper.extend([
            GetTableEntryStr(backgroundEvts['QCDFakes_DATA'],backgroundEvtsErrUp['QCDFakes_DATA'],backgroundEvtsErrDown['QCDFakes_DATA'],latex=True),
            GetTableEntryStr(otherBackground,otherBackgroundErrStatUp,otherBackgroundErrStatDown,latex=True),
            GetTableEntryStr(totalBackground,totalBackgroundErrStatUp,totalBackgroundErrStatDown,totalBackgroundErrSyst,True),
            GetTableEntryStr(thisDataEvents,latex=True)])
        # for the AN, break down the other backgrounds
        latexRow.extend([
            GetTableEntryStr(backgroundEvts['QCDFakes_DATA'],backgroundEvtsErrUp['QCDFakes_DATA'],backgroundEvtsErrDown['QCDFakes_DATA'],latex=True),
            #GetTableEntryStr(otherBackground,otherBackgroundErrStatUp,otherBackgroundErrStatDown,latex=True),
            GetTableEntryStr(backgroundEvts['DIBOSON_amcatnlo'],backgroundEvtsErrUp['DIBOSON_amcatnlo'],backgroundEvtsErrDown['DIBOSON_amcatnlo'],latex=True),
            GetTableEntryStr(backgroundEvts['SingleTop'],backgroundEvtsErrUp['SingleTop'],backgroundEvtsErrDown['SingleTop'],latex=True),
            ])
        if doEEJJ:
            latexRow.append(GetTableEntryStr(backgroundEvts['WJet_amcatnlo_ptBinned'],backgroundEvtsErrUp['WJet_amcatnlo_ptBinned'],backgroundEvtsErrDown['WJet_amcatnlo_ptBinned'],latex=True))
        else:
            latexRow.append(GetTableEntryStr(backgroundEvts['ZJet_amcatnlo_ptBinned'],backgroundEvtsErrUp['ZJet_amcatnlo_ptBinned'],backgroundEvtsErrDown['ZJet_amcatnlo_ptBinned'],latex=True))
        latexRow.extend([
            GetTableEntryStr(backgroundEvts['PhotonJets_Madgraph'],backgroundEvtsErrUp['PhotonJets_Madgraph'],backgroundEvtsErrDown['PhotonJets_Madgraph'],latex=True),
            GetTableEntryStr(totalBackground,totalBackgroundErrStatUp,totalBackgroundErrStatDown,totalBackgroundErrSyst,True),
            GetTableEntryStr(thisDataEvents,latex=True),
            ])
        latexRow = ['$'+entry+'$' if not 'LQ' in entry and not 'pres' in entry else entry for entry in latexRow ]
        latexRowPaper = ['$'+entry+'$' if not 'LQ' in entry and not 'pres' in entry else entry for entry in latexRowPaper ]
        for i,rowEntry in enumerate(latexRow):
            if i<len(latexRow)-1:
                #rowEntry+=' & '
                latexRow[i]+=' & '
            else:
                #rowEntry+=' \\\\ '
                latexRow[i]+=' \\\\ '
        latexRowsAN.append(''.join(latexRow))
        #
        for i,rowEntry in enumerate(latexRowPaper):
            if i<len(latexRowPaper)-1:
                latexRowPaper[i]+=' & '
            else:
                latexRowPaper[i]+=' \\\\ '
        latexRowsPaper.append(''.join(latexRowPaper))
        if selectionName=='preselection':
          latexRowsAN.append('\\hline')
          latexRowsPaper.append('\\hline')
print t

print
print 'Latex table: AN'
print
# latex table -- AN
for line in latexRowsAN:
  print(line)
print

print
print 'Latex table: Paper'
print
# latex table -- Paper
for line in latexRowsPaper:
  print(line)
print
exit(0)

