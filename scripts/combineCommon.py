#!/usr/bin/env python

#---Import
import sys
import string

def lookupXSection(datasetFromAnalysis,xsectionFile):
  dataset_forXsec = datasetFromAnalysis
  if datasetFromAnalysis.endswith('_reduced_skim'):
    dataset_forXsec = datasetFromAnalysis[0:datasetFromAnalysis.find('_reduced_skim')]

  xsectionDataset = ''
  xsectionVal = -1
  for lin1 in open( xsectionFile ):

    lin1 = string.strip(lin1,"\n")

    (dataset , xsection_val) = string.split(lin1)
    #print dataset + " " + xsection_val

    dataset_mod_1 = dataset[1:].replace('/','__')
    #print dataset_mod_1 + " " + xsection_val

    # TODO: fix this hack!
    if ( dataset_mod_1.startswith(dataset_forXsec+'_Tune') or
        (dataset_forXsec=='DYJetsToLL_Mbin_M-50' and dataset_mod_1.startswith('DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8')) or
        (dataset_forXsec=='TTJets_DiLept_ext1' and dataset_mod_1.startswith('TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8__RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9_ext1-v1'))):
      # TODO: fix this hack
      # special handling of DYJetsToLL_M-50
      # for madgraph; Mbin has _Mbin in it
      if dataset_forXsec=='DYJetsToLL_M-50':
        if not 'madgraph' in dataset:
          continue
      #elif dataset_forXsec=='DYJetsToLL_Mbin_M-50':
      #  if not 'amcatnloFXFX' in dataset:
      #    continue
      #
      if len(xsectionDataset) <= 0:
        xsectionDataset = dataset
        xsectionVal = xsection_val
      elif xsectionVal != xsection_val:
        print 'ERROR: Two datasets in xsection file start with',dataset_forXsec
        print '1)',xsectionDataset,xsectionVal
        print '2)',dataset,xsection_val
        print 'Cannot figure out which is correct; exiting'
        sys.exit()

  xsection_val = xsectionVal
  dataset = xsectionDataset
  if(xsection_val < 0):
    print "ERROR: xsection for dataset " + dataset_forXsec + " not found in " + options.xsection
    print "Expected a line in xsection file to start with "+dataset_forXsec+"_Tune but couldn't find one."
    print "exiting..."
    sys.exit()
  return dataset,xsection_val


