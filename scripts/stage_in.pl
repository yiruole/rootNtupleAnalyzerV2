#!/usr/bin/perl -w
use strict;

my $castorHome = $ENV{CASTOR_HOME};

## MC

# my $inputdir = "/castor/cern.ch/user/b/barfuss/LQ/RootNtuple/RootNtuple-V00-01-04-SpringMC_Zjet_20101209_121708";
# my $inputdir = "/castor/cern.ch/user/b/barfuss/LQ/RootNtuple/RootNtuple-V00-01-04-SpringMC_Wjet_20101208_164254";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-04-MC-enujj_preselection_skim";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-BJets_TuneD6T_7TeV-madgraph-Fall10-START38_V12-v1_20101224_193503";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-GJets_TuneD6T_7TeV-madgraph-Fall10-START38_V12-v1_20110106_010744";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-QCD_TuneD6T_7TeV-madgraph_Fall10-START38_V12-v1_20110106_013229";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-TTbar_SingleTop-madgraph_Spring10-START3X_V26_S09-v1_20110105_221542";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-WW_WZ_ZZ_Spring10-START3X_V26_S09-v1_20110105_222352";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-enujj_preselection_skim";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-LQToUE_7TeV-pythia6_Spring10-START3X_V26-v1_20110106_053202";
my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-06-MC-LQToUE_ENuJJFilter_7TeV-pythia6_Spring10-START3X_V26-v1_20110106_050514";

## Data

# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-EG-Run2010A-Nov4ReReco_v1_136035-144114_20101209_043341";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-Electron-Run2010B-Nov4ReReco_v1_146428-149294_20101209_182617";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-enujj_preselection_skim";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-SC_Skim-EG-Run2010A-Nov4ReReco_v1_136035-144114_20101209_054303";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-SC_Skim-Photon-Run2010B-Nov4ReReco_v1_146428-149294_20101209_195542";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-QCD-enujj_preselection_skim";

## 2011 Data

# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-09-DATA-SingleElectron_Run2011A-PromptReco-v1_160431-161312_20110329_182031";


### Old ntuples

## MC

# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-TTbar_SingleTop_VV_20100519_011910";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-Z_plus_Jets_20100520_171604";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-W_plus_Jets_20100521_141022";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-WW_ZZ_WZ_20100612_133148";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-W_plus_Jets_20100521_141022";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-enujj_preselection_skim";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-eejj_low_mass_20100604_213652";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-eejj_20100518_231412";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-enujj_low_mass_20100608_175052";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-enujj_20100519_011206";

## Data

# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-02-DATA-enujj_preselection_skim";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-02-DATA-QCD-enujj_preselection_skim";

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
        }
        if($x=~/STAGEIN/)
        {
            $isStagin=1;
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
