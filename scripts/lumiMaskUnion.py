#!/usr/bin/env python2

from optparse import OptionParser
import os, sys, errno, time, copy

try:
    from FWCore.PythonUtilities.LumiList import LumiList
except ImportError:
    print
    print( "ERROR: Could not load LumiList.  Please execute this script in a cmssw environment.")
    exit(-1)

# --------------------------------------------------------------------------------
#  Parse options
# --------------------------------------------------------------------------------
#
# usage = "usage: %prog [options] \nExample: python ./scripts/lumiMaskOps.py <options>"
#
# parser = OptionParser(usage=usage)
#
# parser.add_option("-i", "--inputlist", dest="inputlist",
#                  help="list of all lumi mask jsons to be used",
#                  metavar="LIST")
#
# parser.add_option("-o", "--output", dest="outputDir",
#                  help="the directory OUTDIR contains the output of the program",
#                  metavar="OUTDIR")
#
# parser.add_option("-n", "--treeName", dest="treeName",
#                  help="name of the root tree; defaults to rootTupleTree/tree",
#                  metavar="TREENAME")
#
# parser.add_option("-c", "--cutfile", dest="cutfile",
#                  help="name of the cut file",
#                  metavar="CUTFILE")
#
#
# (options, args) = parser.parse_args()


# Union
originalLumiList1 = LumiList(
    filename="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt"
    #filename="certified_UL2016preVFP.json"
)
originalLumiList2 = LumiList(
    filename="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt"
    #filename="certified_UL2016postVFP.json"
)
#unionLumiList = originalLumiList1 | originalLumiList2
originalLumiList3 = LumiList(
    filename="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"
)
unionLumiList = originalLumiList1 | originalLumiList2 | originalLumiList3
unionLumiList.writeJSON("my_lumi_union.json")

## Difference
##originalLumiList1 = LumiList(filename='my_lumi_mask.json')
## 2.11/fb
# goldenJsonLumiList = LumiList(filename='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON.txt')
# nov17LumiList = goldenJsonLumiList - unionLumiList
# nov17LumiList.writeJSON('newLumisNov17_lumi_mask.json')

## new Nov17 lumis
# originalLumiList4 = LumiList(filename='runData2015D_newNov13Lumis_singleElectron/v1-4-0_2015Nov17_105129/crab_SingleElectron__Run2015D-PromptReco-v4/results/lumiSummary.json')
# unionLumiList = originalLumiList1 | originalLumiList2 | originalLumiList3 | originalLumiList4
# unionLumiList.writeJSON('newestLumisProcessed.json')

# make 2016UL pre/postVFP JSONs
#lumiListFullUL2016 = LumiList(
#        filename="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt"
#)
#runs2016Bver1 = [272760, 272761, 272762, 272774, 272775, 272776, 272782, 272783, 272784, 272785, 272786, 272798, 272811, 272812, 272814, 272815, 272816, 272818, 272827, 272828, 272930, 272936, 273013, 273017, ]
#runs2016Bver2 = [273150, 273158, 273290, 273291, 273292, 273294, 273295, 273299, 273301, 273302, 273402, 273403, 273404, 273405, 273406, 273407, 273408, 273409, 273410, 273411, 273425, 273426, 273445, 273446, 273447, 273448, 273449, 273450, 273492, 273493, 273494, 273502, 273503, 273523, 273526, 273537, 273554, 273555, 273589, 273590, 273592, 273725, 273728, 273730, 274094, 274102, 274103, 274104, 274105, 274106, 274107, 274108, 274142, 274146, 274157, 274159, 274160, 274161, 274172, 274198, 274199, 274200, 274240, 274241, 274243, 274244, 274250, 274251, 274282, 274283, 274284, 274285, 274286, 274314, 274315, 274316, 274317, 274318, 274319, 274335, 274336, 274337, 274338, 274339, 274344, 274345, 274382, 274387, 274388, 274420, 274421, 274422, 274440, 274441, 274442, 274443, 274954, 274955, 274957, 274958, 274959, 274967, 274968, 274969, 274970, 274971, 274998, 274999, 275000, 275001, 275059, 275062, 275063, 275064, 275066, 275067, 275068, 275073, 275074, 275124, 275125, 275282, 275283, 275284, 275285, 275286, 275289, 275290, 275291, 275292, 275293, 275309, 275310, 275311, 275319, 275337, 275338, 275344, 275345, 275370, 275371, 275375, 275376, ]
#runs2016C = [275656, 275657, 275658, 275659, 275757, 275758, 275759, 275761, 275763, 275764, 275766, 275767, 275768, 275772, 275773, 275774, 275776, 275777, 275778, 275781, 275782, 275828, 275829, 275831, 275832, 275833, 275834, 275835, 275836, 275837, 275841, 275846, 275847, 275886, 275887, 275890, 275911, 275912, 275913, 275918, 275920, 275921, 275922, 275923, 275931, 275963, 276062, 276063, 276064, 276092, 276095, 276097, 276242, 276243, 276244, 276282, 276283]
#runs2016D = [276315, 276317, 276318, 276327, 276352, 276355, 276357, 276361, 276363, 276384, 276437, 276453, 276454, 276458, 276495, 276501, 276502, 276525, 276527, 276528, 276542, 276543, 276544, 276545, 276581, 276582, 276583, 276584, 276585, 276586, 276587, 276653, 276655, 276659, 276775, 276776, 276794, 276807, 276808, 276810, 276811]
#runs2016E = [276824, 276830, 276831, 276832, 276834, 276836, 276837, 276870, 276886, 276922, 276923, 276935, 276940, 276941, 276942, 276944, 276945, 276946, 276947, 276948, 276950, 277069, 277070, 277071, 277072, 277073, 277075, 277076, 277081, 277086, 277087, 277093, 277094, 277096, 277112, 277125, 277126, 277127, 277148, 277166, 277168, 277180, 277194, 277202, 277216, 277217, 277218, 277219, 277220, 277277, 277278, 277279, 277305, 277420]
#runs2016F = [277932, 277934, 277981, 277991, 277992, 278017, 278018, 278167, 278175, 278193, 278239, 278240, 278273, 278274, 278288, 278289, 278290, 278308, 278309, 278310, 278315, 278345, 278346, 278349, 278366, 278406, 278509, 278761, 278770, 278806, 278807]
#runList = runs2016Bver1+runs2016Bver2+runs2016C+runs2016D+runs2016E+runs2016F
#lumiListUL2016preVFP = copy.deepcopy(lumiListFullUL2016)
#lumiListUL2016preVFP.selectRuns(runList)
#print("Writing 2016preVFP JSON...",)
#lumiListUL2016preVFP.writeJSON("certified_UL2016preVFP.json")
#print("Done")
#
#runs2016F_noHIPM = [278769, 278801, 278802, 278803, 278804, 278805, 278808]
#runs2016G = [278820, 278821, 278822, 278873, 278874, 278875, 278923, 278957, 278962, 278963, 278969, 278975, 278976, 278986, 279024, 279029, 279071, 279080, 279115, 279116, 279479, 279480, 279488, 279489, 279588, 279653, 279654, 279656, 279658, 279667, 279681, 279682, 279683, 279684, 279685, 279691, 279694, 279715, 279716, 279760, 279766, 279767, 279794, 279823, 279841, 279844, 279887, 279931, 279966, 279975, 279993, 279994, 279995, 280002, 280006, 280007, 280013, 280014, 280015, 280016, 280017, 280018, 280019, 280020, 280021, 280022, 280023, 280024, 280187, 280188, 280190, 280191, 280192, 280194, 280242, 280249, 280251, 280327, 280330, 280349, 280361, 280363, 280364, 280383, 280384, 280385]
#runs2016H = [281613, 281616, 281638, 281639, 281641, 281663, 281674, 281680, 281686, 281689, 281691, 281693, 281707, 281726, 281727, 281797, 281974, 281975, 281976, 282033, 282034, 282035, 282037, 282092, 282663, 282707, 282708, 282710, 282711, 282712, 282730, 282731, 282732, 282733, 282734, 282735, 282800, 282807, 282814, 282842, 282917, 282918, 282919, 282922, 282923, 282924, 283042, 283043, 283049, 283050, 283052, 283059, 283270, 283283, 283305, 283306, 283307, 283308, 283353, 283358, 283359, 283407, 283408, 283413, 283415, 283416, 283453, 283469, 283478, 283548, 283672, 283675, 283676, 283680, 283681, 283682, 283685, 283820, 283830, 283834, 283835, 283863, 283865, 283876, 283877, 283884, 283885, 283933, 283934, 283946, 283964, 284006, 284014, 284025, 284029, 284035, 284036, 284037, 284038, 284039, 284040, 284041, 284042, 284043, 284044]
#runList = runs2016F_noHIPM+runs2016G+runs2016H
#lumiListUL2016postVFP = copy.deepcopy(lumiListFullUL2016)
#lumiListUL2016postVFP.selectRuns(runList)
#print("Writing 2016postVFP JSON...",)
#lumiListUL2016postVFP.writeJSON("certified_UL2016postVFP.json")
#print("Done")
