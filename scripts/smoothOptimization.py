#!/usr/bin/env python

import numpy
from prettytable import PrettyTable
from tabulate import tabulate
from ROOT import gROOT, gDirectory, gPad, gStyle, TFile, TGraph, TMultiGraph, TCanvas, TLegend


def makePaperTableLine(cutList, title):
    # lineCuts = [str(st)+' & ' for st in cutList]
    # lineCuts = [(i, st) if lq_masses[i] <= maxMassPointToUse else '' for i, st in enumerate(cutList)]
    lineCuts = [
        str((i, st)[1]) + " & " if lq_masses[i] <= maxMassPointToUse else ""
        for i, st in enumerate(cutList)
    ]
    lineSt = title + " & " + "".join(lineCuts)
    k = lineSt.rfind("& ")
    lineSt = lineSt[:k] + "\\\\" + lineSt[k + 1:]
    return lineSt


gROOT.SetBatch(True)

# XXX must modify this by hand
isEEJJ = True
if isEEJJ:
    maxMassPointToUse = 1400  # 2016 eejj, last point where nS > 5
    # maxMassPointToUse = 1100  # 2017 eejj, last point where nB > 1
    # maxMassPointToUse = 1150  # 2018 eejj, last point where nB > 1
    optimizationFileName = (
        # "$LQANA/versionsOfOptimization/2016/eejj_10jul2020/optimization.root"
        # "$LQANA/versionsOfOptimization/2017/eejj_10jul/optimization.root"
        # "$LQANA/versionsOfOptimization/2018/eejj_10jul2020/optimization.root"
        # nanoV7
        # "$LQANA/versionsOfOptimization/nanoV7/2016/eejj_14sep/optimization.root"
        # "$LQANA/versionsOfOptimization/nanoV7/2017/eejj_14sep/optimization.root"
        # "$LQANA/versionsOfOptimization/nanoV7/2018/eejj_14sep/optimization.root"
        # LQToDEle
        # "$LQANA/versionsOfOptimization/nanoV7/2016/eejj_16oct/optimization.root"
        # "$LQANA/versionsOfOptimization/nanoV7/2017/eejj_22oct/optimization.root"
        # "$LQANA/versionsOfOptimization/nanoV7/2016/eejj_11aug_loosenMee_addMasym/punzi2/optimization.root"
        # "$LQANA/versionsOfOptimization/nanoV7/2016/eejj_11aug_loosenMee/punzi/optimization.root"
        "$LQANA/versionsOfOptimization/nanoV7/2016/eejj_17jan_egmLooseID/optimization.root"
    )
else:
    # maxMassPointToUse = 900 # enujj
    # maxMassPointToUse = 1200 # last point where we have nB > 1
    maxMassPointToUse = 1200  # last point where we have nB > 1
    # optimizationFileName = '$LQANA/versionsOfAnalysis_enujj/jun2/opt/cutOffFitRange/optimization.root'
    # optimizationFileName = '$LQANA/versionsOfAnalysis_enujj/aug9/opt_fromJun2processing/powhegTTBar/optimization.root'
    # optimizationFileName = '$LQANA/versionsOfAnalysis_enujj/oct6_oldOptUpdateRescale/optimization.root'
    # optimizationFileName = '$LQANA/versionsOfAnalysis_enujj/oct6_finerTrigEff/opt/optimization.root'
    optimizationFileName = (
        "$LQANA/versionsOfAnalysis_enujj/jan17/opt_jan19/optimization.root"
    )

print "INFO: Opening file: {}".format(optimizationFileName)
optimizationTFile = TFile.Open(optimizationFileName)
optimizationTFile.cd()

# FIXME: this still doesn't work for descending cut values; M_asym doesn't work here
optVarsToCutValues = {}
optVarsToTitles = {"sT_eejj_opt": "S_{T} cut [GeV]", "M_e1e2_opt": "M(ee) cut [GeV]", "Mej_min_opt": "M_{min}(ej) cut [GeV]"}  # , "Mej_asym_opt": "M_{asym}(ej) cut"}
optVarsToDirections = {"sT_eejj_opt": "inc", "M_e1e2_opt": "inc", "Mej_min_opt": "inc"}  # , "Mej_asym_opt": "dec"}
optVarsToTypes = {"sT_eejj_opt": int, "M_e1e2_opt": int, "Mej_min_opt": int}  # , "Mej_asym_opt": float}
optVarsToCodeNames = {"sT_eejj_opt": "sT_eejj_LQ", "M_e1e2_opt": "M_e1e2_LQ", "Mej_min_opt": "min_M_ej_LQ"}  # , "Mej_asym_opt": "asym_M_ej_LQ"}
optVarsToPaperNames = {"sT_eejj_opt": "\st~[\GeV]", "M_e1e2_opt": "\mee~[\GeV]", "Mej_min_opt": "\mejmin~[\GeV]"}  # , "Mej_asym_opt": "M_{asym}(ej) cut [GeV]"}
# add later if needed
# elif "MT" in graph.GetName():
#     "Opt. M_{T}(e,#nu) cut [GeV]"
# elif "MET" in graph.GetName():
#     "Opt. MET cut [GeV]"
lq_masses = []

for key in gDirectory.GetListOfKeys():
    print "INFO: Key found:", key.GetName(), "with class:", key.GetClassName()
    if "TGraph" in key.GetClassName():
        # look only at func2 --> pol2
        if "func2" not in key.GetName():
            continue
        print "INFO: looking at TGraph named", key.GetName()
        graph = optimizationTFile.Get(key.GetName())
        varName = graph.GetName().replace("graph_", "").replace("_func2", "")
        for func in graph.GetListOfFunctions():
            if "func2" not in func.GetName():
                continue
            # print 'func=',func.GetName()
            fitFunction = graph.GetFunction(func.GetName())  # using pol2
            # print 'got fitFunction:',fitFunction.Print()
            pars = fitFunction.GetParameters()
            # print list(pars)
            xValues = graph.GetX()
            yValues = graph.GetY()
            if optVarsToTypes[varName] == int:
                # round to nearest 5 GeV
                funcYvalues = [
                    5 * round(float(fitFunction.Eval(x)) / 5)
                    if x <= maxMassPointToUse
                    else 5 * round(float(fitFunction.Eval(maxMassPointToUse)) / 5)
                    for x in xValues
                ]
                graphYvalues = [5 * round(y / 5) for y in yValues]
            else:
                lastYVal = -1
                funcYvalues = []
                for idx, xVal in enumerate(xValues):
                    if xVal > maxMassPointToUse:
                        funcYvalues.append(lastYVal)
                    else:
                        funcYvalues.append(yValues[idx])
                        lastYVal = yValues[idx]
                graphYvalues = [y for y in yValues]
                funcYvalues = yValues
                graphYvalues = yValues
            print "funcYvalues=", [y for y in funcYvalues]
            print "funcOrigValues=", [fitFunction.Eval(x) for x in xValues]
            print "xValues=", [x for x in xValues]
            t = PrettyTable([str(xVal) for xVal in xValues])
            t.float_format = "4.3"
            # t.align['VarName'] = 'l'
            t.align = "l"
            t.add_row([str(y) for y in funcYvalues])
            print t
            print
            # make sure no y values come out less than any raw cut threshold
            yMin = min(graphYvalues)
            # make sure y values are monotonically increasing
            # FIXME: implement descending cut values
            # -- so don't do this for floats for now
            if optVarsToTypes[varName] != float:
                for idx, yVal in enumerate(funcYvalues):
                    if yVal < yMin:
                        print "INFO: adjusting yVal=", yVal, " at", xValues[idx], "from", funcYvalues[
                            idx
                        ], "to", yMin
                        funcYvalues[idx] = yMin
                    if idx == 0:
                        continue
                    if yVal < funcYvalues[idx - 1]:
                        print "INFO: adjusting yVal at", xValues[idx], "from", funcYvalues[
                            idx
                        ], "to", funcYvalues[idx - 1]
                        funcYvalues[idx] = funcYvalues[idx - 1]
            # done
            graphFunc = TGraph(
                len(funcYvalues), numpy.array(xValues), numpy.array(funcYvalues)
            )
            graphFunc.SetMarkerStyle(20)
            # nominal graph style
            graph.SetMarkerStyle(24)
            canvas = TCanvas("canvas", "", 1000, 500)
            canvas.cd()
            gStyle.SetOptFit(0)
            gStyle.SetOptStat(0)
            # graph.GetListOfFunctions().FindObject("stats").Delete()
            mg = TMultiGraph()
            mg.Add(graph)
            mg.Add(graphFunc)
            mg.Draw("a")
            mg.GetXaxis().SetTitle("LQ mass [GeV]")
            mg.GetXaxis().SetTitleSize(0.04)
            mg.GetXaxis().SetTitleOffset(1.1)
            mg.GetXaxis().SetNdivisions(220)
            mg.GetXaxis().SetRangeUser(150, 2050)
            mg.GetXaxis().SetLabelSize(0.03)
            mg.GetYaxis().SetLabelSize(0.03)
            mg.GetYaxis().SetTitle("Opt. "+optVarsToTitles[varName])
            mg.GetYaxis().SetTitleSize(0.04)
            mg.GetYaxis().SetTitleOffset(1.0)
            mg.Draw("ap")
            # leg = TLegend(0.5,0.2,0.85,0.3)
            leg = TLegend(0.17, 0.78, 0.42, 0.88)
            leg.SetBorderSize(1)
            leg.AddEntry(graph, '"Raw result" of optimization', "p")
            leg.AddEntry(fitFunction, 'Fit (pol2) of "raw result"', "l")
            leg.AddEntry(graphFunc, "Evaluation of fit", "p")
            leg.Draw()
            canvas.Modified()
            gPad.Modified()
            gPad.Update()
            canvas.SaveAs(graph.GetName().replace("graph", "smoothed") + ".png")
            canvas.SaveAs(graph.GetName().replace("graph", "smoothed") + ".pdf")

            ### wait for input to keep the GUI (which lives on a ROOT event dispatcher) alive
            # if __name__ == '__main__':
            #   rep = ''
            #   while not rep in [ 'c', 'C' ]:
            #      rep = raw_input( 'enter "c" to continue: ' )
            #      if 1 < len(rep):
            #         rep = rep[0]
            # for tables
            if len(lq_masses) <= 0:
                lq_masses = list(xValues)
            optVarsToCutValues[varName] = list(funcYvalues)
            break

optimizationTFile.Close()

# print tables
lq_masses = [int(mass) for mass in lq_masses]
print
table = []
for var, cutVals in optVarsToCutValues.items():
    cutValsReduced = cutVals[:lq_masses.index(maxMassPointToUse)+1]
    cutValsReduced = [round(optVarsToTypes[var](val), 4) for val in cutValsReduced]
    table.append([var]+cutValsReduced)
    print makePaperTableLine(cutValsReduced, r"%\multicolumn{1}{c}{"+optVarsToPaperNames[var]+"}")
print


columnNames = [str(mass) for mass in lq_masses if mass <= maxMassPointToUse]
columnNames[-1] = ">=" + columnNames[-1]
columnNames.insert(0, "Var/LQMass")
print tabulate(table, headers=columnNames, tablefmt="github")
print tabulate(table, headers=columnNames, tablefmt="latex")

# for cut file
for i, mass in enumerate(lq_masses):
    print "#"+114*"-"
    print "# LQ M", mass, "optimization"
    print "#"+114*"-"
    for var, cutVals in optVarsToCutValues.items():
        cutVal = optVarsToTypes[var](cutVals[i])
        if optVarsToTypes[var] == float:
            # assume range 0-1
            cutVal = round(cutVal, 4)
        elif var not in optVarsToTypes:
            print "ERROR: variable {} not found in optVarsToTypes dict; please add it. exiting here.".format(var)
            exit(-1)
        cutVar = optVarsToCodeNames[var]+str(mass)
        if optVarsToDirections[var] == "inc":
            line = "{0:20} {1:>20} {2:>20}".format(cutVar, cutVal, "+inf")
        elif optVarsToDirections[var] == "dec":
            line = "{0:20} {1:>20} {2:>20}".format(cutVar, "-inf", cutVal)
        elif var in optVarsToDirections:
            print "ERROR: not sure how to handle direction {} for variable {}; exiting here.".format(optVarsToDirections[var], var)
            exit(-1)
        else:
            print "ERROR: variable {} not found in optVarsToDirections dict; please add it. exiting here.".format(var)
            exit(-1)
        if optVarsToTypes[var] == int:
            line += " 		-		-	2	200 0 2000"
        elif optVarsToTypes[var] == float:
            # assume range 0-1
            line += "		-		-	2	20 0 1"
        elif var in optVarsToTypes:
            print "ERROR: not sure how to handle variable type {} for variable {}; exiting here.".format(optVarsToTypes[var], var)
            exit(-1)
        else:
            print "ERROR: variable {} not found in optVarsToTypes dict; please add it. exiting here.".format(var)
            exit(-1)
        print line
