#!/usr/local/bin/perl -w
use strict;

my $castorHome = $ENV{CASTOR_HOME};




################ 2011 #####################


###################
### ParticleFlow ##
###################
#my $inputdir = "/castor/cern.ch/user/b/benedet/CMSSW_420pre8";
#my $inputdir = "/castor/cern.ch/user/s/santanas/ParticleFlow/Display_QCDForPF_420pre8_10042011";

####################
### ElectronSkim ###
####################

## 2011 PROMPT RECO + May10 RERECO
my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-02-02-DATA-SingleElectron-Run2011A-May10ReReco-v1-160329-163869_20110601_174652";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-02-02-DATA-SingleElectron-Run2011A-PromptReco-v4-165088-165969_20110601_180608";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-02-02-DATA-ElectronHad-Run2011A-PromptReco-v4-165970-166021_20110601_182553";

## MC (V00-02-0X)  
#my $inputdir = "/castor/cern.ch/user/e/eberry/LQ/RootNtupleSpring11/RootNtuple-V00-02-01-Spring11MC-SingleTopMadGraph_20110528_083757";
#my $inputdir = "/castor/cern.ch/user/e/eberry/LQ/RootNtupleSpring11/RootNtuple-V00-02-01-Spring11MC-TTBarMadGraph_20110528_083554";
#my $inputdir = "/castor/cern.ch/user/d/darinb/LQ/RootNtuple_Spring2011MC/RootNtuple-V00-02-01-Spring11MC_ZJets_ALPGEN_20110525_203142";

################ 2010 #####################


####################
### ElectronSkim ###
####################

##NOV 4 RERECO
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-Electron-Run2010B-Nov4ReReco_v1_146428-149294_20101209_182617";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-EG-Run2010A-Nov4ReReco_v1_136035-144114_20101209_043341";

## PROMPT RECO
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-01-DATA-Electron-Run2010B-PromptReco-v2_146511-146513_147115-147454_20101018_051044";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-01-DATA-Electron-Run2010B-PromptReco-v2-146428-146644_20101006_162408";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-01-DATA-Electron-Run2010B-PromptReco-v2-146804-147114_20101009_001302";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-02-DATA-Electron-Run2010B-PromptReco-v2_147757-148058_20101025_012008";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-02-DATA-Electron-Run2010B-PromptReco-v2_147754-148031_148822-148864_20101101_014243";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-02-DATA-Electron-Run2010B-PromptReco-v2_148952-149294_20101106_003153";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-01-DATA-EG-Run2010A-Sep17ReReco_v2-132440-144114_20101006_194357";

### MC (V00-01-XX) 
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-LQToUE_7TeV-pythia6_Spring10-START3X_V26-v1_20110106_053202";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-LQToUE_ENuJJFilter_7TeV-pythia6_Spring10-START3X_V26-v1_20110106_050514";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-06-MC-LQ_ENuJJFilter_7TeV_TuneD6T_ISR_FSR_Spring10Like_20110218_125243";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-TTbar_SingleTop-madgraph_Spring10-START3X_V26_S09-v1_20110105_221542";
#my $inputdir = "/castor/cern.ch/user/b/barfuss/LQ/RootNtuple/RootNtuple-V00-01-04-SpringMC_Zjet_20101209_121708";
#my $inputdir = "/castor/cern.ch/user/b/barfuss/LQ/RootNtuple/RootNtuple-V00-01-04-SpringMC_Wjet_20101208_164254";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-WW_WZ_ZZ_Spring10-START3X_V26_S09-v1_20110105_222352";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-GJets_TuneD6T_7TeV-madgraph-Fall10-START38_V12-v1_20110106_010744";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-QCD_TuneD6T_7TeV-madgraph_Fall10-START38_V12-v1_20110106_013229";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-BJets_TuneD6T_7TeV-madgraph-Fall10-START38_V12-v1_20101224_193503";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-LQToUE_ENuJJFilter_7TeV-pythia6_Fall10-START38_V12-v1_20110128_005328";


##--> Studies on W+jets
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-06-MC-WJetsToLNu_TuneD6T_7TeV-madgraph-tauola_Fall10-START38_V12-v1_20110125_005330";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-06-MC-WJets_TuneD6T_scaledown_7TeV-madgraph-tauola_Fall10-START38_V12-v1_20110126_024147";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-06-MC-WJets_TuneD6T_scaleup_7TeV-madgraph-tauola_Fall10-START38_V12-v1_20110126_094535";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-06-MC-WJets_TuneD6T_matchingup_7TeV-madgraph-tauola_Fall10-START38_V12-v1_20110126_225940";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-06-MC-WJets_TuneD6T_matchingdown_7TeV-madgraph-tauola_Fall10-START38_V12-v1_20110127_225653";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-06-MC-WJetsToLNu_TuneZ2_7TeV-madgraph-tauola_Fall10-E7TeV_ProbDist_2010Data_BX156_START38_V12-v1_20110216_112909";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-06-MC-WJetsToLNu_TuneZ2_7TeV-madgraph-tauola_Fall10-START38_V12-v1_20110215_142129";

##--> Studies on ttbar
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-07-MC-TTbar_7TeV_Fall10-START38_V12_20110624_072949";

### MC (V00-00-XX)
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-eejj_low_mass_20100604_213652";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-eejj_20100518_231412";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-enujj_low_mass_20100608_175052";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-enujj_20100519_011206";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-TTbar_SingleTop_VV_20100519_011910";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-Z_plus_Jets_20100520_171604";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-W_plus_Jets_20100521_141022";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-WW_ZZ_WZ_20100612_133148";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-TTbar_ZeeJet_Pythia6_20100707_214138";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-ZJet-madgraph_20100828_021017";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-PhotonJet_20100824_215127/";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-00-08-MC-QCDmadgraph_20100519_233358";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-BJets_TuneD6T_7TeV-madgraph-Fall10-START38_V12-v1_20101224_193503";


##################
### PhotonSkim ###
##################

## NOV 4 RERECO
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-SC_Skim-Photon-Run2010B-Nov4ReReco_v1_146428-149294_20101209_195542";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-SC_Skim-EG-Run2010A-Nov4ReReco_v1_136035-144114_20101209_054303";

## PROMPT RECO
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-01-DATA-SC_Skim-EG-Run2010A-Sep17ReReco_v2-132440-144114_20101007_124915";
#my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-01-DATA-SC_Skim-Photon-Run2010B-PromptReco-v2-146428-146644_20101007_144045";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-02-DATA-Photon-Run2010B-PromptReco-v2_146804-148058_20101025_014657";
##my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-02-DATA-Photon-Run2010B-PromptReco-v2_147754-148031_148822-148864_20101101_015743";
##my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-02-DATA-Photon-Run2010B-PromptReco-v2_148952-149294_20101106_003521";

##################
### enujj skim ###
##################

## NOV 4RERECO (+ V00-01-XX MC ntuples)
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-LQToUE_7TeV-pythia6_Spring10-START3X_V26-v1_20110106_053202";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-LQToUE_ENuJJFilter_7TeV-pythia6_Spring10-START3X_V26-v1_20110106_050514";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-04-MC-enujj_preselection_skim";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-enujj_preselection_skim";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-enujj_preselection_skim";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-QCD-enujj_preselection_skim";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-07-MC-enujj_preselection_skim";

## NOV 4RERECO (+ V00-00-XX MC ntuples)
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-enujj_preselection_skim/";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-enujj_preselection_skim";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-QCD-enujj_preselection_skim";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-eejj_low_mass_20100604_213652";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-eejj_20100518_231412";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-enujj_low_mass_20100608_175052";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-enujj_20100519_011206";

## PROMPT RECO (+ V00-00-XX MC ntuples)
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-enujj_preselection_skim/";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-02-DATA-enujj_preselection_skim";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-02-DATA-QCD-enujj_preselection_skim";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-eejj_low_mass_20100604_213652";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-eejj_20100518_231412";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-enujj_low_mass_20100608_175052";
#my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-enujj_20100519_011206";


my $listStagedFiles = "stagedFiles.txt";

my $tmpOutputFile = "out.txt";
system("rm -f $tmpOutputFile");

open(LISTSTAGEDFILES,">$listStagedFiles");
print LISTSTAGEDFILES "replace PoolSource.fileNames = {\n";

open(CASTORFILE, "rfdir $inputdir |");
while(<CASTORFILE>)
{
    my $line = $_; chomp $line;
    my @array = split(/\s+/, $line);
    my $currentfile="$inputdir/$array[8]";
    system("stager_qry -M $currentfile \> $tmpOutputFile \n");

    my $isStaged=0;
    my $isStagin=0;
    my $NeedStageget=0;

    open(FILE,"<$tmpOutputFile");
    while(<FILE>)
    {
	my $x=$_; 
	chomp $x;
	#print("$x\n");
	

	if($x=~/STAGED/)
	{
	    $isStaged=1;
	    system("stager_get -M $currentfile");	    
	}
	if($x=~/STAGEIN/)
	{
	    $isStagin=1;
	    system("stager_get -M $currentfile");	    
	}
	if($x=~/Error/)
	{
	    $NeedStageget=1;
	    print "### stager_qry output ###\n";
	    print "$x\n";
	    print "#########################\n";

            ## stager_get
	    print("stager_get -M $currentfile \n");
	    system("stager_get -M $currentfile");
	    print ("\n");
	}
	
    }
    close(FILE);

    if($isStagin==1)
    {
	print ("$currentfile is still STAGEIN\n");
    }
    
    if($isStaged==1)
    {
	print ("$currentfile is STAGED\n");
	print LISTSTAGEDFILES "\'file:rfio:$currentfile\' \,\n";
    }

 }
close (CASTORFILE);

system("rm -f $tmpOutputFile");

print LISTSTAGEDFILES "}\n";
close (LISTSTAGEDFILES);

print ("\n");
print ("$listStagedFiles  created\n");
print ("ATTENTION - REMOVE THE \, FROM THE LAST LINE OF $listStagedFiles \n");
