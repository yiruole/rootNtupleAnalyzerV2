import os
from ROOT import gROOT, gMinuit, gStyle, gPad, TFile, TF1, TCanvas, TLegend, kSpring, kAzure, kRed, kOrange

gROOT.SetBatch(True)

outputFileName = "fitResults.root"
pdf_folder = "pdf"

# fitFunctions = [TF1("pol0", "pol0"), TF1("pol1", "pol1"), TF1("pol2", "pol2")]
funcTypes = ["pol0", "pol1", "pol2", "pol3"]
fitColors = [kSpring-1, kRed+1, kAzure+1, kOrange+8]
fitStyles = [1, 2]

# years = [2016, 2017, 2018]
years = [2016]

fileNames = {}
fileNames[2016] = "$LQANA/versionsOfFakeRate/2016/may25/plots.root"
fileNames[2017] = "$LQANA/versionsOfFakeRate/2017/apr17/plots.root"
fileNames[2018] = "$LQANA/versionsOfFakeRate/2018/jun4/plots.root"

regionsDict = {}
regionsDict[2016] = ["Bar_2Jet", "End1_2Jet", "End2_2Jet"]
regionsDict[2017] = regionsDict[2016]
regionsDict[2018] = ["Bar_pre319077_2Jet", "End1_pre319077_2Jet", "End2_pre319077_2Jet"]
regionsDict[2018].extend(["Bar_noHEM_post319077_2Jet", "End1_noHEM_post319077_2Jet", "End2_noHEM_post319077_2Jet"])
regionsDict[2018].extend(["Bar_HEMonly_post319077_2Jet", "End1_HEMonly_post319077_2Jet", "End2_HEMonly_post319077_2Jet"])

fitRanges = {}
fitRanges[2016] = {}
fitRanges[2016]["Bar_2Jet"] = [[0, 200], [150, 1000]]
fitRanges[2016]["End1_2Jet"] = [[0, 175], [150, 1000]]
fitRanges[2016]["End2_2Jet"] = [[0, 175], [150, 1000]]
fitRanges[2017] = fitRanges[2016]
fitRanges[2018] = {}
fitRanges[2018]["Bar_pre319077_2Jet"] = [[0, 200], [150, 1000]]
fitRanges[2018]["End1_pre319077_2Jet"] = [[0, 225], [175, 1000]]
fitRanges[2018]["End2_pre319077_2Jet"] = [[0, 175], [150, 1000]]
fitRanges[2018]["Bar_noHEM_post319077_2Jet"] = [[0, 175], [150, 1000]]
fitRanges[2018]["End1_noHEM_post319077_2Jet"] = [[0, 175], [150, 1000]]
fitRanges[2018]["End2_noHEM_post319077_2Jet"] = [[0, 175], [150, 1000]]
fitRanges[2018]["Bar_HEMonly_post319077_2Jet"] = [[0, 225], [150, 1000]]
fitRanges[2018]["End1_HEMonly_post319077_2Jet"] = [[0, 175], [150, 1000]]
fitRanges[2018]["End2_HEMonly_post319077_2Jet"] = [[0, 175], [150, 1000]]

# use this after we've determined the function selection to write the combined function to the file
# number of functions has to match number of specified fit ranges/regions
# list: [functionType1, functionType2, splitPoint, functionType2, functionType3, splitPoint, etc.]
selectedFits = {}
selectedFits[2016] = {}
for year in years:
    for reg in regionsDict[year]:
        selectedFits[year][reg] = {}
selectedFits[2016]["Bar_2Jet"]["funcs"] = ["pol2", "pol1", 150]
selectedFits[2016]["End1_2Jet"]["funcs"] = ["pol2", "pol2", 140]
selectedFits[2016]["End2_2Jet"]["funcs"] = ["pol2", "pol2", 160]
selectedFits[2016]["Bar_2Jet"]["splits"] = [150]
selectedFits[2016]["End1_2Jet"]["splits"] = [140]
selectedFits[2016]["End2_2Jet"]["splits"] = [160]
if len(selectedFits) > 0:
    writeFitResults = True
else:
    writeFitResults = False

graphName = "fr{}_template"

tfiles = {}
for year in years:
    tfiles[year] = TFile.Open(fileNames[year])

canvases = []
legends = []
functions = []
fitResults = {}

for year in years:
    thisFile = tfiles[year]
    fitResults[year] = {}
    for region in regionsDict[year]:
        fitResults[year][region] = {}
        graph = thisFile.Get(graphName.format(region))
        canName = "y"+str(year)+"_"+region
        canvas = TCanvas(canName, canName)
        canvas.cd()
        leg = TLegend(0.38, 0.71, 0.63, 0.88)
        leg.SetBorderSize(0)
        gPad.cd()
        graph.Draw("ap0")
        graph.GetYaxis().SetRangeUser(0, 0.1)
        if year != 2018:
            graph.SetTitle(str(year)+" FR, "+graph.GetTitle())
        gStyle.SetOptFit(0)
        for frIndex, fitRange in enumerate(fitRanges[year][region]):
            thisFitRangeMinChi2OverNdf = 1000
            # print "Fit range:", fitRange
            fitRangeStr = "to".join(str(fr) for fr in fitRange)
            fitResults[year][region][fitRangeStr] = {}
            for funcIndex, funcType in enumerate(funcTypes):
                func = TF1(canName+"_"+fitRangeStr+"_"+funcType, funcType)
                func.SetLineColor(fitColors[funcIndex])
                func.SetRange(float(fitRange[0]), float(fitRange[1]))
                func.SetLineStyle(fitStyles[frIndex])
                print "Fit for year={} region={} fitRange={} funcType={}".format(year, region, fitRange, funcType)
                graph.Fit(func, "WQRN", "", float(fitRange[0]), float(fitRange[1]))
                result = graph.Fit(func, "SFRM", "", float(fitRange[0]), float(fitRange[1]))
                # print "Func name: {} Chi2={} NDF={}; chi2/ndf={}".format(
                #         func.GetName(), func.GetChisquare(), func.GetNDF(), func.GetChisquare()/func.GetNDF())
                thisChi2OverNdf = result.Chi2()/result.Ndf()
                if "CONVERGED" in gMinuit.fCstatu or "OK" in gMinuit.fCstatu:
                    # print "func: {} fit converged!".format(func.GetName())
                    if thisChi2OverNdf < thisFitRangeMinChi2OverNdf:
                        thisFitRangeMinChi2OverNdf = thisChi2OverNdf
                        # thisFitRangeBestFitResult = result
                        thisFitRangeBestFunc = func
                    # print "Func name: {} Chi2={} NDF={}; chi2/ndf={}".format(
                    #         func.GetName(), result.Chi2(), result.Ndf(), thisChi2OverNdf)
                    # print
                    fitResults[year][region][fitRangeStr][func] = [result]
                else:
                    print "ERROR: Fit for function:", func.GetName(), "did not converge; skipping"
                    fitResults[year][region][fitRangeStr][func] = [None]
                    continue
                canvas.cd()
                gPad.cd()
                func.Draw("same")
                functions.append(func)
            for func in fitResults[year][region][fitRangeStr].keys():
                if func == thisFitRangeBestFunc:
                    fitResults[year][region][fitRangeStr][func].append(True)
                else:
                    fitResults[year][region][fitRangeStr][func].append(False)
        for func in sorted(fitResults[year][region].values()[0].keys(), key=lambda x: len(x.GetExpFormula().Data())):
            leg.AddEntry(func, func.GetExpFormula().Data(), "l")
        leg.Draw()
        canvas.Modified()
        canvas.Update()
        canvases.append(canvas)
        legends.append(leg)

    print
    print "SUMMARY"
    print
    for region in regionsDict[year]:
        for fitRange in fitResults[year][region].keys():
            print "Year={}, region={}, Fit range: {}".format(year, region, fitRange)
            for func in fitResults[year][region][fitRange].keys():
                thisFitResult = fitResults[year][region][fitRange][func][0]
                if thisFitResult is not None:
                    print "--> func name: {} Chi2={} NDF={}; chi2/ndf={}".format(
                            func.GetName(), thisFitResult.Chi2(), thisFitResult.Ndf(),
                            thisFitResult.Chi2()/thisFitResult.Ndf()),
                    if fitResults[year][region][fitRange][func][1]:
                        print "[BEST]"
                    else:
                        print
                else:
                    print "--> func name: {} fit did not converge.".format(func.GetName())

outputTFile = TFile(outputFileName, "recreate")
outputTFile.cd()
if not os.path.isdir(pdf_folder) and pdf_folder != "":
    "Making directory", pdf_folder
    os.mkdir(pdf_folder)
for can in canvases:
    can.Draw()
    can.Write()
    can.Print(pdf_folder + "/" + can.GetName() + "_fit.pdf")
for func in functions:
    func.Write()

# write manually-selected full functions
if writeFitResults:
    for year in years:
        for region in regionsDict[year]:
            selectedFitList = selectedFits[year][region]["funcs"]
            selectedFitSplitList = selectedFits[year][region]["splits"]
            canName = "y"+str(year)+"_"+region
            selectedFitFuncs = []
            selectedFuncTypes = []
            for frIndex, fitRange in enumerate(fitRanges[year][region]):
                funcType = selectedFitList[frIndex]
                fitRangeStr = "to".join(str(fr) for fr in fitRange)
                funcName = canName+"_"+fitRangeStr+"_"+funcType
                for func in functions:
                    if funcName == func.GetName():
                        break
                selectedFitFuncs.append(func)
                selectedFuncTypes.append(funcType)
            paramIndex = 0
            params = []
            formula = ""
            for i, func in enumerate(selectedFitFuncs):
                formula += selectedFuncTypes[i]+"("+str(paramIndex)+")"
                if i < len(selectedFitFuncs)-1:
                    splitPoint = str(selectedFitSplitList[i])
                    formula += "*(x<"+str(splitPoint)+")+(x>="+str(splitPoint)+")*"
                paramIndex += func.GetNpar()
                params.extend([func.GetParameter(j) for j in range(0, func.GetNpar())])
            # nParams = sum([func.GetNpar() for func in selectedFitFuncs])
            print "Create TF1 with combined formula: '{}'".format(formula)
            combinedFitFunc = TF1(canName+"_combinedFit", formula)
            combinedFitFunc.SetRange(0, 5000)
            for i, param in enumerate(params):
                combinedFitFunc.SetParameter(i, param)
            combinedFitFunc.Write()


outputTFile.Close()

for f in tfiles.values():
    f.Close()
