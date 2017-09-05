#!/usr/bin/env python

import os, sys, math, re
import subprocess as sp
from optparse import OptionParser
from prettytable import PrettyTable
from ROOT import *

from combineCommon import *

def GetStatErrors(nevts):
    nevts = int(nevts)
    alpha = 1.0 - 0.6827
    #print 'calculate errors on nevts=',nevts
    l = 0 if nevts==0 else ROOT.Math.gamma_quantile(alpha/2.0,nevts,1.0)
    u = ROOT.Math.gamma_quantile_c(alpha/2.0,nevts+1,1.0)
    return u-nevts,nevts-l


def GetBackgroundSyst(background_name, selectionName):
    verbose = False
    if selectionName=='preselection':
      verbose=True
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

    # background-only special systs: "DYShape", "TTShape"
    for syst in ["DYShape","TTShape"]:
        if syst=='DYShape' and not 'DY' in background_name or syst=='TTShape' and not 'TT' in background_name:
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
          #print 'backgroundSystDict['+syst+']['+background_name+']['+selectionNameBkgSyst+']=',secondSyst
        except KeyError:
            print 'ERROR: Got a KeyError with: backgroundSystDict['+syst+']['+background_name+']['+selectionNameBkgSyst+']'

    if verbose:
      print 'secondSyst (TT/DYShape)=',math.sqrt(secondSyst)
        
    # XXX WARNING: hardcoded background name (ick); some checking is done at least
    if 'TTbar' in background_name:
        thirdSyst = pow(ttBarNormDeltaXOverX,2)
    elif 'DY' in background_name:
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
                    print 'ERROR: background named:',bkgName,' was not found in list of systematics background names:',syst_background_names
                    print 'selectionPoint=',selectionPoint,'from',filename
                selectionPoint = selectionPoint.split('_')[0]
                if not bkgName in systDict.keys():
                    systDict[bkgName] = {}
                systDict[bkgName][selectionPoint] = float(items[1].strip())/100.0
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
  #filePath
  if bkgType=='QCD':
    filepath = qcdFilePath
    if doEEJJ:
      analysisCode = 'analysisClass_lq_eejj_QCD'
    else:
      analysisCode = 'analysisClass_lq_enujj_MT_QCD'
  elif bkgType=='TTData':
      return ttbar_data_filepath
  else:
    filepath = filePath
    if doEEJJ:
      analysisCode = 'analysisClass_lq_eejj'
    else:
      analysisCode = 'analysisClass_lq_enujj_MT'
  reducedSkimStrings = ['_reduced_skim','_pythia8_reduced_skim']
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
    #print 'GetRatesAndErrors(',unscaledRootFile,combinedRootFile,unscaledTotalEvts,sampleName,selection,isDataOrQCD,')'
    if selection=='preselection':
        selection = 'PAS'
    # special case of TTBar from data
    if isTTBarFromData:
        # rate calcs should be same as data/QCD
        mejHist = combinedRootFile.Get('histo1D__'+ttbarSampleName+'__Mej_selected_min_'+selection)
        mejUnscaledRawHist = combinedRootFile.Get('histo1D__'+ttBarUnscaledRawSampleName+'__Mej_selected_min_'+selection)
        mejNonTTBarHist = combinedRootFile.Get('histo1D__'+nonTTBarSampleName+'__Mej_selected_min_'+selection)
        rateErr = Double(0)
        #integ = mejNonTTBarHist.IntegralAndError(1,mejNonTTBarHist.GetNbinsX(),rateErr)
        #print 'mejNonTTBar:',integ,',+/-',rateErr
        #integ = mejUnscaledRawHist.IntegralAndError(1,mejUnscaledRawHist.GetNbinsX(),rateErr)
        #print 'mejUnscaledRaw:',integ,',+/-',rateErr
        #mejNonTTBarHist.Scale(1/1000.)
        #rate = mejHist.Integral()
        rate = mejHist.IntegralAndError(1,mejHist.GetNbinsX(),rateErr)
        unscaledHist = mejUnscaledRawHist.Clone()
        unscaledHist.Add(mejNonTTBarHist,-1)
        #integ = mejUnscaledHist.IntegralAndError(1,mejUnscaledHist.GetNbinsX(),rateErr)
        #print 'mejUnscaled:',integ,',+/-',rateErr
        #scaledHist = unscaledHist.Clone()
        #scaledHist.Scale(0.436873)
        #integ = mejScaledHist.IntegralAndError(1,mejScaledHist.GetNbinsX(),rateErr)
        #print 'mejScaled:',integ,',+/-',rateErr
        unscaledRate = unscaledHist.Integral()
        unscaledRateErr = mejHist.IntegralAndError(1,mejHist.GetNbinsX(),rateErr)
        #print 'TTBARFROMDATA-->rate=',rate,'+/-',rateErr
        #print 'using hist:',mejHist.GetName(),'from file:',combinedRootFile
        return rate,rateErr,unscaledRate
    #mejHist = combinedRootFile.Get('histo1D__'+sampleName+'__Mej_selected_min_'+selection)
    #if not mejHist:
    #  print 'ERROR: could not find hist','histo1D__'+sampleName+'__Mej_selected_min_'+selection,' in file:',combinedRootFile.GetName()
    #  print 'EXIT'
    #  exit(-1)
    #rate = mejHist.Integral()
    mejUnscaledHist = unscaledRootFile.Get('Mej_selected_min_'+selection)
    if not mejUnscaledHist:
      print 'ERROR: could not find hist','Mej_selected_min_'+selection,' in file:',unscaledRootFile.GetName()
      print 'EXIT'
      exit(-1)
    unscaledInt = mejUnscaledHist.Integral()
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
        #print 'reading Mej_selected_min_'+selection,'from',unscaledRootFile
        rate = unscaledInt
        rateErr = CalculateScaledRateError(sampleName,unscaledTotalEvts,unscaledRate,unscaledInt,False)
    if 'TT' in sampleName and not 'data' in sampleName.lower():
        #print 'applying extra average weight to',sampleName
        rate/=avgTopPtWeight
        rateErr/=avgTopPtWeight
    #if selection=='LQ1500':
    #  print 'INFO: hist','Mej_selected_min_'+selection,' in file:',unscaledRootFile.GetName()
    #  print 'unscaledRate=',unscaledRate,'unscaled entries=',mejUnscaledHist.GetEntries()
    #  print 'xsecTimesIntLumi=',xsecTimesIntLumi,'unscaledInt=',unscaledInt,'unscaledRate=',unscaledRate,'unscaledTotalEvts=',unscaledTotalEvts,'rate=unscaledInt*xsecTimesIntLumi/unscaledTotalEvts=',rate
    return rate,rateErr,unscaledRate

def GetUnscaledTotalEvents(unscaledRootFile,isTTBarData=False):
    if not isTTBarData:
        unscaledEvtsHist = unscaledRootFile.Get('EventsPassingCuts')
        unscaledTotalEvts = unscaledEvtsHist.GetBinContent(1)
    else:
        unscaledEvtsHist = unscaledRootFile.Get('histo1D__TTBarFromDATA__EventsPassingCuts')
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
                #print selectionName,'bkg_bame=',bkg_name
                for bkgSample in sampleList:
                    bkgUnscaledRootFilename = FindUnscaledSampleRootFile(bkgSample,bkgType)
                    bkgUnscaledRootFile = TFile.Open(bkgUnscaledRootFilename)
                    unscaledTotalEvts = GetUnscaledTotalEvents(bkgUnscaledRootFile,bkgType=='TTData')
                    sampleUnscaledTotalEvts+=unscaledTotalEvts
                    # preselection
                    #print '------>Call GetRatesAndErrors for sampleName=',bkgSample
                    rate,rateErr,unscaledRate = GetRatesAndErrors(bkgUnscaledRootFile,scaledRootFile,unscaledTotalEvts,bkgSample,selectionName,not bkgType=='MC',bkgType=='TTData')
                    #print '------>rate=',rate,'rateErr=',rateErr,'unscaledRate=',unscaledRate
                    #if isQCD:
                    #  print 'for sample:',bkgSample,'got unscaled entries=',unscaledRate
                    sampleRate+=rate
                    sampleUnscaledRate+=unscaledRate
                    sampleRateErr+=(rateErr*rateErr)
                    bkgUnscaledRootFile.Close()
                sampleRateErr = math.sqrt(sampleRateErr)
                #print 'sampleRate:',sampleRate,'sampleRateErr=',sampleRateErr,'sampleUnscaledRate=',sampleUnscaledRate
                bkgRatesDict[selectionName] = sampleRate
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

#signal_names = [ "LQ_BetaHalf_M", "LQ_M" ] 
signal_names = [ "LQ_M_" ] 
blinded=True
doEEJJ=False

#mass_points = [str(i) for i in range(300,1550,50)] # go from 300-1500 in 50 GeV steps
#mass_points = [str(i) for i in range(200,1550,50)] # go from 200-1500 in 50 GeV steps
mass_points = [str(i) for i in range(200,2050,50)] # go from 200-2000 in 50 GeV steps
#systematics = [ "jes", "ees", "shape", "norm", "lumi", "eer", "jer", "pu", "ereco", "pdf" ]
systematicsNamesBackground = [ "Trigger", "Reco", "PU", "PDF", "Lumi", "JER", "JEC", "HEEP", "E_scale", "EER", "DYShape", "TTShape" ]
systematicsNamesSignal = [ "Trigger", "Reco", "PU", "PDF", "Lumi", "JER", "JEC", "HEEP", "E_scale", "EER" ]
#FIXME systematics
systematics = []
#XXX FIXME FOR enujj needed
if doEEJJ:
  background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTBarFromDATA", "ZJet_amcatnlo_ptBinned", "WJet_amcatnlo_ptBinned", "DIBOSON","SingleTop"  ]
else:
  background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTbar_powheg", "ZJet_amcatnlo_ptBinned", "WJet_amcatnlo_ptBinned", "DIBOSON","SingleTop"  ]
# background names for systs
if doEEJJ:
  syst_background_names = ['GJets', 'QCDFakes_DATA', 'TTBarFromDATA', 'DY', 'WJets', 'Diboson', 'Singletop']
else:
  syst_background_names = ['GJets', 'QCDFakes_DATA', 'TTbar_powheg', 'DY', 'WJets', 'Diboson', 'Singletop']
# XXX FIXME TEST
#maxLQselectionBkg = 'LQ1500' # max background selection point used
if doEEJJ:
  maxLQselectionBkg = 'LQ1200' # max background selection point used
else:
  maxLQselectionBkg = 'LQ900' # max background selection point used
minLQselectionBkg='LQ200'

# DYnorm for eejj
if doEEJJ:
  zjetsSF = 1.05
  zjetsSFerr = 0.01
  zJetNormDeltaXOverX=zjetsSFerr/zjetsSF
#TODO FIXME:
# Need to add Wjets/TTBar scale factor norms for enujj

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
ttBarNormDeltaXOverX = 0.1
ttbarSampleName='TTBarFromDATA'
ttBarUnscaledRawSampleName='TTBarUnscaledRawFromDATA'
nonTTBarSampleName='NONTTBARBKG_amcatnloPt'

# FIXME update to 2016 analysis numbers
# QCDNorm is 0.40 [40% norm uncertainty for eejj = uncertaintyPerElectron*2]
if doEEJJ:
  qcdNormDeltaXOverX = 0.40
else:
  qcdNormDeltaXOverX = 0.20

n_background = len ( background_names  )
#n_systematics = len ( systematics ) + n_background + 1
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

inputList = os.environ["LQANA"]+'/config/PSKeejj_may21_SEleL_reminiAOD_v236_eoscms/inputListAllCurrent.txt'
sampleListForMerging = os.environ["LQANA"]+'/config/sampleListForMerging_13TeV_eejj.txt'
sampleListForMergingQCD = os.environ["LQANA"]+'/config/sampleListForMerging_13TeV_QCD_dataDriven.txt'
sampleListForMergingTTBar = os.environ["LQANA"]+'/config/sampleListForMerging_13TeV_ttbarBkg_emujj.txt'
xsection = os.environ["LQANA"]+'/config/xsection_13TeV_2015eejj_DYrescale.txt'
intLumi = 35867.0

filePath = os.environ["LQDATA"] + '/2016analysis/eejj_psk_jul4_properEle27wptightOREle115ORPhoton175_eejjOptFinalSels/output_cutTable_lq_eejj/'
qcdFilePath = os.environ["LQDATA"] + '/2016analysis/eejj_QCD_psk_jul2_ele27wptightOREle115ORPhoton175_eejjOptFinalSels/output_cutTable_lq_eejj_QCD/'
ttbarFilePath = os.environ["LQDATA"] + '/2016ttbar/jul4_emujj_properEle27wptightOREle115ORPhoton175_eejjOptFinalSels/output_cutTable_lq_ttbar_emujj_correctTrig/'

# this has the TopPtReweight+updatedSF and the Z+jets St corrections at final selections
#filePath = os.environ["LQDATA"] + '/RunII/eejj_analysis_zJetsStCorrectionFinalSelections_21jul/output_cutTable_lq_eejj/'

dataMC_filepath   = filePath+'analysisClass_lq_eejj_plots.root'
qcd_data_filepath = qcdFilePath+'analysisClass_lq_eejj_QCD_plots.root'
if doEEJJ:
  ttbar_data_filepath = ttbarFilePath+'analysisClass_lq_ttbarEst_plots.root'
else:
  ttbar_data_filepath = ''
systematics_filepaths = {}
for systName in systematicsNamesBackground:
  systematics_filepaths[systName] = '/afs/cern.ch/user/m/mbhat/work/public/Systematics_txtfiles_20_07_2016/'
systematics_filepaths['EER'] = '/afs/cern.ch/user/m/mbhat/work/public/Systematics_textfiles_28_07_2016/'


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
        
        card_file.write ( "bin 1\n\n" )

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
            line = line + "1 " 
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
        print signal_name+str(mass_point), total_signal, total_bkg

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
        for syst in ["DYShape","TTShape"]:
            line = syst + ' lnN - '
            for ibkg,background_name in enumerate(syst_background_names):
                if syst=='DYShape' and not 'DY' in background_name or syst=='TTShape' and not 'TT' in background_name or 'TTBarFromDATA' in background_name:
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
        
        # background norm systs
        foundTTBar = False
        foundZJet = False
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
            elif 'DY' in background_name and not foundZJet:
                line = 'norm_zjet lnN - '
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
            print 'ERROR: could not find one or more of [ttbar,zjet,QCD] background names for normalization syst; check background names'
            exit(-1)

        card_file.write("\n")

        # background stat error part
        for i_background_name ,background_name in enumerate(background_names):
            thisBkgEvts = d_background_rates[background_name][selectionName]
            thisBkgEvtsErr = d_background_rateErrs[background_name][selectionName]
            thisBkgTotalEntries = d_background_unscaledRates[background_name][selectionName]

            if thisBkgEvts != 0.0: 
                lnN_f = 1.0 + 1.0/math.sqrt(thisBkgTotalEntries+1) # Poisson becomes Gaussian, approx by logN with this kappa
                gmN_weight = thisBkgEvts / thisBkgTotalEntries # for small uncertainties, use gamma distribution with alpha=(factor to go to signal region from control/MC)
            else: 
                # for small uncertainties, use gamma distribution with alpha=(factor to go to signal region from control/MC)
                # since we can't compute evts/entries, we use it from the preselection (following LQ2)
                gmN_weight = d_background_rates[background_name]['preselection'] / d_background_unscaledRates[background_name]['preselection']
            
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

            if thisBkgTotalEntries > 10:
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
          # THIS IS BROKEN FIXME
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
columnNames = ['MLQ','signal','Z+jets','ttbar','QCD(data)','Other','Data','Total BG']
## FOR TESTING
#columnNames = ['MLQ']
#for bn in background_names:
#  columnNames.append(bn)
otherBackgrounds = ['PhotonJets_Madgraph','WJet_amcatnlo_ptBinned','DIBOSON','SingleTop']
#background_names =  [ "PhotonJets_Madgraph", "QCDFakes_DATA", "TTbar_Madgraph", "WJet_Madgraph_HT", "ZJet_Madgraph_HT", "DIBOSON","SingleTop"  ]
latexRows = []
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
            thisBkgEvtsErrUp = d_background_rateErrs[background_name][selectionName]
            thisBkgEvtsErrDown = thisBkgEvtsErrUp
            thisBkgTotalEntries = d_background_unscaledRates[background_name][selectionName]
            backgroundEvtsErrIsAsymm[background_name] = False
            #if thisBkgEvts==0.0:
            if thisBkgTotalEntries < 10.0:
                #thisBkgEvtsErr = 1.8 # error is +1.8 from StatComm: twiki.cern.ch/twiki/bin/view/CMS/PoissonErrorBars
                thisBkgEvtsErrUp,thisBkgEvtsErrDown = GetStatErrors(thisBkgTotalEntries)
                rateOverUnscaledRatePresel = d_background_rates[background_name]['preselection'] / d_background_unscaledRates[background_name]['preselection']
                thisBkgEvtsErrUp *= rateOverUnscaledRatePresel
                thisBkgEvtsErrDown *= rateOverUnscaledRatePresel
                backgroundEvtsErrIsAsymm[background_name] = True
                backgroundEvtsErrUp[background_name] = thisBkgEvtsErrUp
                backgroundEvtsErrDown[background_name] = thisBkgEvtsErrDown
                #print background_name,': selection',selectionName,'rateOverUnscaledRatePresel=',rateOverUnscaledRatePresel,'thisBkgEvtsErr=',thisBkgEvtsErr
            thisBkgSyst = GetBackgroundSyst(syst_background_names[i_background_name],selectionName)
            thisBkgSystErr = thisBkgEvts*thisBkgSyst
            totalBackground+=thisBkgEvts
            totalBackgroundErrStatUp+=(thisBkgEvtsErrUp*thisBkgEvtsErrUp)
            totalBackgroundErrStatDown+=(thisBkgEvtsErrDown*thisBkgEvtsErrDown)
            totalBackgroundErrSyst+=(thisBkgSystErr*thisBkgSystErr)
            if selectionName=='preselection':
              print 'background:',background_name,'thisBkgEvents =',thisBkgEvts,'GetBackgroundSyst(syst_background_names['+str(i_background_name)+'],'+selectionName+')=',thisBkgSyst
              print 'thisBkgSystErr=',math.sqrt(thisBkgSystErr)
              print 'updated totalBackgroundErrSyst',math.sqrt(totalBackgroundErrSyst)
              #print 'totalBackgound=',totalBackground
            if background_name in otherBackgrounds:
              otherBackground+=thisBkgEvts
              otherBackgroundErrStatUp+=(thisBkgEvtsErrUp*thisBkgEvtsErrUp)
              otherBackgroundErrStatDown+=(thisBkgEvtsErrDown*thisBkgEvtsErrDown)
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
            GetTableEntryStr(backgroundEvts['ZJet_amcatnlo_ptBinned'],backgroundEvtsErrUp['ZJet_amcatnlo_ptBinned'],backgroundEvtsErrDown['ZJet_amcatnlo_ptBinned']),
            GetTableEntryStr(backgroundEvts['TTBarFromDATA'],backgroundEvtsErrUp['TTBarFromDATA'],backgroundEvtsErrDown['TTBarFromDATA']),
            GetTableEntryStr(backgroundEvts['QCDFakes_DATA'],backgroundEvtsErrUp['QCDFakes_DATA'],backgroundEvtsErrDown['QCDFakes_DATA']),
            GetTableEntryStr(otherBackground,otherBackgroundErrStatUp,otherBackgroundErrStatDown),
            GetTableEntryStr(thisDataEvents),
            GetTableEntryStr(totalBackground,totalBackgroundErrStatUp,totalBackgroundErrStatDown,totalBackgroundErrSyst),
            ]
        t.add_row(row)
        latexRow = [selectionName,
            GetTableEntryStr(thisSigEvts,thisSigEvtsErr,thisSigEvtsErr,latex=True), # assumes we always have > 0 signal events
            GetTableEntryStr(backgroundEvts['ZJet_amcatnlo_ptBinned'],backgroundEvtsErrUp['ZJet_amcatnlo_ptBinned'],backgroundEvtsErrDown['ZJet_amcatnlo_ptBinned'],latex=True),
            GetTableEntryStr(backgroundEvts['TTBarFromDATA'],backgroundEvtsErrUp['TTBarFromDATA'],backgroundEvtsErrDown['TTBarFromDATA'],latex=True),
            GetTableEntryStr(backgroundEvts['QCDFakes_DATA'],backgroundEvtsErrUp['QCDFakes_DATA'],backgroundEvtsErrDown['QCDFakes_DATA'],latex=True),
            GetTableEntryStr(otherBackground,otherBackgroundErrStatUp,otherBackgroundErrStatDown,latex=True),
            GetTableEntryStr(thisDataEvents,latex=True),
            GetTableEntryStr(totalBackground,totalBackgroundErrStatUp,totalBackgroundErrStatDown,totalBackgroundErrSyst,True),
            ]
        latexRow = ['$'+entry+'$' if not 'LQ' in entry else entry for entry in latexRow ]
        for i,rowEntry in enumerate(latexRow):
            if i<len(latexRow)-1:
                #rowEntry+=' & '
                latexRow[i]+=' & '
            else:
                #rowEntry+=' \\\\ '
                latexRow[i]+=' \\\\ '
        latexRows.append(''.join(latexRow))
        if selectionName=='preselection':
          latexRows.append('\\hline')
print t

print
# latex table
for line in latexRows:
  print(line)
print

exit(0)

