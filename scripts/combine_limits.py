#!/usr/bin/env python

import numpy
from ROOT import TCanvas,TGraph

# July 2016
# combine single-point full frequentist limit calculation output


def readLimitFile(filename,mass):
# limit files have this at the end:
#
#LQ_M_200
#Expected  2.5%: r < 0.001575
#Expected 16.0%: r < 0.0032346
#Expected 50.0%: r < 0.00369221
#Expected 84.0%: r < 0.00568794
#Expected 97.5%: r < 0.00776398
#Observed Limit: r < 0.0047285
    limDict = {}
    with open(filename) as limFile:
        for line in limFile:
            if 'Expected  2.5%:' in line:
                limDict['exp2p5'] = float(line.split()[-1])
            if 'Expected 16.0%:' in line:
                limDict['exp16'] = float(line.split()[-1])
            if 'Expected 50.0%:' in line:
                limDict['exp50'] = float(line.split()[-1])
            if 'Expected 84.0%:' in line:
                limDict['exp84'] = float(line.split()[-1])
            if 'Expected 97.5%:' in line:
                limDict['exp97p5'] = float(line.split()[-1])
            if 'Observed Limit:' in line:
                limDict['obs'] = float(line.split()[-1])
    return limDict


limLogDir = '/afs/cern.ch/user/s/scooper/work/private/cmssw/7416patch2/LQ2015Limits/src/HiggsAnalysis/CombinedLimit/'
limLogDir+='jul29_freqLimit_test/log/'
limLogPrefix = 'jul29_freqLimit_test_'
# the mass point goes in between the prefix and suffix
limLogSuffix = '.log'
massPoints = [i*50 for i in range(4,31)]
mTh = [0.200E+03,0.210E+03,0.220E+03,0.230E+03,0.240E+03,0.250E+03,0.260E+03,0.270E+03,0.290E+03,0.300E+03,0.310E+03,0.320E+03,0.330E+03,0.340E+03,0.350E+03,0.360E+03,0.370E+03,0.380E+03,0.390E+03,0.400E+03,0.410E+03,0.420E+03,0.430E+03,0.440E+03,0.450E+03,0.460E+03,0.470E+03,0.480E+03,0.490E+03,0.500E+03,0.510E+03,0.520E+03,0.530E+03,0.540E+03,0.550E+03,0.560E+03,0.570E+03,0.580E+03,0.590E+03,0.600E+03,0.610E+03,0.620E+03,0.630E+03,0.640E+03,0.650E+03,0.660E+03,0.670E+03,0.680E+03,0.690E+03,0.700E+03,0.710E+03,0.720E+03,0.730E+03,0.740E+03,0.750E+03,0.760E+03,0.770E+03,0.780E+03,0.790E+03,0.800E+03,0.810E+03,0.820E+03,0.830E+03,0.840E+03,0.850E+03,0.860E+03,0.870E+03,0.880E+03,0.890E+03,0.900E+03,0.910E+03,0.920E+03,0.930E+03,0.940E+03,0.950E+03,0.960E+03,0.970E+03,0.980E+03,0.990E+03,0.100E+04,0.101E+04,0.102E+04,0.103E+04,0.104E+04,0.105E+04,0.106E+04,0.107E+04,0.108E+04,0.109E+04,0.110E+04,0.111E+04,0.112E+04,0.113E+04,0.114E+04,0.115E+04,0.116E+04,0.117E+04,0.118E+04,0.119E+04,0.120E+04,0.121E+04,0.122E+04,0.123E+04,0.124E+04,0.125E+04,0.126E+04,0.127E+04,0.128E+04,0.129E+04,0.130E+04,0.131E+04,0.132E+04,0.133E+04,0.134E+04,0.135E+04,0.136E+04,0.137E+04,0.138E+04,0.139E+04,0.140E+04,0.141E+04,0.142E+04,0.143E+04,0.144E+04,0.145E+04,0.146E+04,0.147E+04,0.148E+04,0.149E+04,0.150E+04,0.151E+04,0.152E+04,0.153E+04,0.154E+04,0.155E+04,0.156E+04,0.157E+04,0.158E+04,0.159E+04,0.160E+04,0.161E+04,0.162E+04,0.163E+04,0.164E+04,0.165E+04,0.166E+04,0.167E+04,0.168E+04,0.169E+04,0.170E+04,0.171E+04,0.172E+04,0.173E+04,0.174E+04,0.175E+04,0.176E+04,0.177E+04,0.178E+04,0.179E+04,0.180E+04,0.181E+04,0.182E+04,0.183E+04,0.184E+04,0.185E+04,0.186E+04,0.187E+04,0.188E+04,0.189E+04,0.190E+04,0.191E+04,0.192E+04,0.193E+04,0.194E+04,0.195E+04,0.196E+04,0.197E+04,0.198E+04,0.199E+04,0.200E+04,0.201E+04,0.202E+04,0.203E+04,0.204E+04,0.205E+04,0.206E+04,0.207E+04,0.208E+04,0.209E+04,0.210E+04,0.211E+04,0.212E+04,0.213E+04,0.214E+04,0.215E+04,0.216E+04,0.217E+04,0.218E+04,0.219E+04,0.220E+04,0.221E+04,0.222E+04,0.223E+04,0.224E+04,0.225E+04,0.226E+04,0.227E+04,0.228E+04,0.229E+04,0.230E+04,0.231E+04,0.232E+04,0.233E+04,0.234E+04,0.235E+04,0.236E+04,0.237E+04,0.238E+04,0.239E+04,0.240E+04,0.241E+04,0.242E+04,0.243E+04,0.244E+04,0.245E+04,0.246E+04,0.247E+04,0.248E+04,0.249E+04,0.250E+04,0.251E+04,0.252E+04,0.253E+04,0.254E+04,0.255E+04,0.256E+04,0.257E+04,0.258E+04,0.259E+04,0.260E+04,0.261E+04,0.262E+04,0.263E+04,0.264E+04,0.265E+04,0.266E+04,0.267E+04,0.268E+04,0.269E+04,0.270E+04,0.271E+04,0.272E+04,0.273E+04,0.274E+04,0.275E+04,0.276E+04,0.277E+04,0.278E+04,0.279E+04,0.280E+04,0.281E+04,0.282E+04,0.283E+04,0.284E+04,0.285E+04,0.286E+04,0.287E+04,0.288E+04,0.289E+04,0.290E+04,0.291E+04,0.292E+04,0.293E+04,0.294E+04,0.295E+04,0.296E+04,0.297E+04,0.298E+04,0.299E+04 ]
xsTh = [6.06E+01,4.79E+01,3.82E+01,3.07E+01,2.49E+01,2.03E+01,1.67E+01,1.38E+01,1.15E+01,9.60E+00,8.04E+00,6.80E+00,5.75E+00,4.90E+00,4.18E+00,3.59E+00,3.09E+00,2.66E+00,2.31E+00,2.00E+00,1.74E+00,1.52E+00,1.33E+00,1.17E+00,1.03E+00,9.06E-01,8.00E-01,7.07E-01,6.27E-01,5.58E-01,4.96E-01,4.43E-01,3.95E-01,3.54E-01,3.16E-01,2.84E-01,2.55E-01,2.29E-01,2.07E-01,1.87E-01,1.69E-01,1.53E-01,1.38E-01,1.25E-01,1.14E-01,1.03E-01,9.39E-02,8.54E-02,7.78E-02,7.10E-02,6.48E-02,5.92E-02,5.42E-02,4.97E-02,4.55E-02,4.16E-02,3.82E-02,3.51E-02,3.22E-02,2.97E-02,2.73E-02,2.51E-02,2.31E-02,2.13E-02,1.97E-02,1.82E-02,1.68E-02,1.55E-02,1.44E-02,1.33E-02,1.23E-02,1.14E-02,1.06E-02,9.79E-03,9.09E-03,8.45E-03,7.84E-03,7.28E-03,6.77E-03,6.30E-03,5.86E-03,5.45E-03,5.08E-03,4.73E-03,4.41E-03,4.11E-03,3.83E-03,3.58E-03,3.34E-03,3.12E-03,2.91E-03,2.72E-03,2.54E-03,2.38E-03,2.22E-03,2.08E-03,1.95E-03,1.82E-03,1.71E-03,1.60E-03,1.50E-03,1.41E-03,1.32E-03,1.24E-03,1.16E-03,1.09E-03,1.02E-03,9.59E-04,9.01E-04,8.46E-04,7.95E-04,7.48E-04,7.03E-04,6.61E-04,6.22E-04,5.85E-04,5.50E-04,5.18E-04,4.87E-04,4.59E-04,4.33E-04,4.07E-04,3.84E-04,3.61E-04,3.41E-04,3.21E-04,3.03E-04,2.85E-04,2.69E-04,2.54E-04,2.40E-04,2.26E-04,2.13E-04,2.02E-04,1.90E-04,1.80E-04,1.70E-04,1.60E-04,1.51E-04,1.43E-04,1.35E-04,1.28E-04,1.21E-04,1.14E-04,1.08E-04,1.02E-04,9.66E-05,9.13E-05,8.64E-05,8.18E-05,7.74E-05,7.32E-05,6.93E-05,6.56E-05,6.21E-05,5.88E-05,5.57E-05,5.27E-05,5.00E-05,4.73E-05,4.48E-05,4.25E-05,4.02E-05,3.81E-05,3.61E-05,3.43E-05,3.25E-05,3.08E-05,2.92E-05,2.77E-05,2.62E-05,2.49E-05,2.36E-05,2.24E-05,2.12E-05,2.01E-05,1.91E-05,1.81E-05,1.72E-05,1.63E-05,1.55E-05,1.47E-05,1.39E-05,1.32E-05,1.26E-05,1.19E-05,1.13E-05,1.07E-05,1.02E-05,9.68E-06,9.20E-06,8.73E-06,8.29E-06,7.87E-06,7.47E-06,7.10E-06,6.74E-06,6.41E-06,6.08E-06,5.78E-06,5.49E-06,5.22E-06,4.96E-06,4.71E-06,4.47E-06,4.26E-06,4.04E-06,3.84E-06,3.65E-06,3.46E-06,3.30E-06,3.13E-06,2.97E-06,2.83E-06,2.69E-06,2.55E-06,2.43E-06,2.31E-06,2.19E-06,2.08E-06,1.98E-06,1.88E-06,1.79E-06,1.70E-06,1.62E-06,1.54E-06,1.46E-06,1.39E-06,1.32E-06,1.25E-06,1.19E-06,1.13E-06,1.08E-06,1.03E-06,9.74E-07,9.27E-07,8.81E-07,8.37E-07,7.96E-07,7.57E-07,7.20E-07,6.84E-07,6.50E-07,6.19E-07,5.88E-07,5.60E-07,5.32E-07,5.05E-07,4.80E-07,4.57E-07,4.35E-07,4.13E-07,3.92E-07,3.73E-07,3.55E-07,3.38E-07,3.21E-07,3.05E-07,2.90E-07,2.75E-07,2.62E-07,2.49E-07,2.36E-07,2.25E-07,2.14E-07,2.03E-07,1.93E-07,1.83E-07,1.74E-07,1.66E-07,1.58E-07,1.50E-07,1.42E-07,1.35E-07,1.28E-07,1.22E-07,1.16E-07,1.10E-07,1.05E-07,9.95E-08,9.46E-08 ]

fileNames = [limLogDir+limLogPrefix+str(mp)+limLogSuffix for mp in massPoints]
limitDictByMass = {} # this will be like limitDict[200]['obs'] to get obs limit

# read all the files
for i,mp in enumerate(massPoints):
    limitDictByMass[mp] = readLimitFile(fileNames[i],mp)
    if len(limitDictByMass[mp]) < 6:
        print 'ERROR: did not get 6 limit values for LQ=',mp
        print limitDictByMass[mp]
        exit(-1)

#for item in limitDictByMass.keys():
#  print item
#  print limitDictByMass[item]
#  print limitDictByMass[item].keys()
#  print limitDictByMass[item]['exp2p5']
#exit(0)

exp2p5lims = [limitDictByMass[item]['exp2p5'] for item in sorted(limitDictByMass.keys())]
exp16lims = [limitDictByMass[item]['exp16'] for item in sorted(limitDictByMass.keys())]
exp50lims = [limitDictByMass[item]['exp50'] for item in sorted(limitDictByMass.keys())]
exp84lims = [limitDictByMass[item]['exp84'] for item in sorted(limitDictByMass.keys())]
exp97p5lims = [limitDictByMass[item]['exp97p5'] for item in sorted(limitDictByMass.keys())]
obslims = [limitDictByMass[item]['obs'] for item in sorted(limitDictByMass.keys())]
masses = [item for item in sorted(limitDictByMass.keys())]

# can make graphs to check that all points convereged properly
graphs = []

graphExp2p5 = TGraph(len(masses),numpy.array(masses,dtype='f'),numpy.array(exp2p5lims,dtype='f'))
graphs.append(graphExp2p5)

graphExp16 = TGraph(len(masses),numpy.array(masses,dtype=float),numpy.array(exp16lims,dtype=float))
graphs.append(graphExp16)

graphExp50 = TGraph(len(masses),numpy.array(masses,dtype=float),numpy.array(exp16lims,dtype=float))
graphs.append(graphExp50)

graphExp84 = TGraph(len(masses),numpy.array(masses,dtype=float),numpy.array(exp16lims,dtype=float))
graphs.append(graphExp84)

graphExp97p5 = TGraph(len(masses),numpy.array(masses,dtype=float),numpy.array(exp16lims,dtype=float))
graphs.append(graphExp97p5)

graphObslims = TGraph(len(masses),numpy.array(masses,dtype=float),numpy.array(exp16lims,dtype=float))
graphs.append(graphObslims)

for g in graphs:
    canvas = TCanvas()
    canvas.cd()
    g.Draw('ap')


# print out the arrays for the plot macro
# copied from RunBasicStatsCLS script
print "*"*40 + '\n BETA ONE CLS RESULTS\n\n' +"*"*40

band1sigma = 'Double_t y_1sigma['+str(int(len(masses)*2))+']={'
band2sigma = 'Double_t y_2sigma['+str(int(len(masses)*2))+']={'
excurve = 'Double_t xsUp_expected['+str(int(len(masses)))+'] = {' 
obcurve = 'Double_t xsUp_observed['+str(int(len(masses)))+'] = {'  
mcurve = 'Double_t mData['+str(int(len(masses)))+'] = {'  
scurve = 'Double_t x_shademasses['+str(int(len(masses)*2))+'] = {'  
  
ob = obslims
down2 = exp2p5lims
up2 = exp97p5lims
down1 = exp16lims
up1 = exp84lims
med = exp50lims

fac = 1.0
sigma = []
for x in range(len(mTh)):
  if (mTh[x]) in masses: 
    sigma.append(xsTh[x]*fac)
for x in range(len(masses)):
  excurve += str(float(med[x])*float(sigma[x])) + ' , ' 
  obcurve += str(float(ob[x])*float(sigma[x])) + ' , ' 
  band1sigma += str(float(down1[x])*float(sigma[x])) + ' , ' 
  band2sigma += str(float(down2[x])*float(sigma[x])) + ' , ' 
  mcurve += str(float(masses[x])) + ' , '
  scurve += str(float(masses[x])) + ' , '

for x in range(len(masses)):
  band1sigma += str(float(up1[-(x+1)])*float(sigma[-(x+1)])) + ' , ' 
  band2sigma += str(float(up2[-(x+1)])*float(sigma[-(x+1)])) + ' , ' 
  scurve += str(float(masses[-x-1])) + ' , '
excurve += '}'
obcurve += '}'
mcurve += '}'
scurve += '}'
band1sigma += '}'
band2sigma += '}'
excurve = excurve.replace(' , }',' }; ' )
obcurve = obcurve.replace(' , }',' }; ' )
mcurve = mcurve.replace(' , }',' }; ' )
scurve = scurve.replace(' , }',' }; ' )

band1sigma = band1sigma.replace(' , }',' }; ' )
band2sigma = band2sigma.replace(' , }',' }; ' )

print '\n'
print mcurve
print scurve
print excurve
print obcurve
print band1sigma
print band2sigma
print '\n'

