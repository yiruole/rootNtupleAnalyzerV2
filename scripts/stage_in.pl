#!/usr/bin/perl -w
use strict;

my $castorHome = $ENV{CASTOR_HOME};

# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-02-DATA-Electron-Run2010B-PromptReco-v2_147757-148058_20101025_012008/";
# my $inputdir = "/castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-01-01-DATA-EG-Run2010A-Sep17ReReco_v2-132440-144114_20101006_194357/";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-02-DATA-enujj_preselection_skim/";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-02-DATA-QCD-enujj_preselection_skim/";

# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-EG-Run2010A-Nov4ReReco_v1_136035-144114_20101209_043341/";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-Electron-Run2010B-Nov4ReReco_v1_146428-149294_20101209_182617/";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-SC_Skim-EG-Run2010A-Nov4ReReco_v1_136035-144114_20101209_054303/";
my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-01-05-DATA-SC_Skim-Photon-Run2010B-Nov4ReReco_v1_146428-149294_20101209_195542/";

# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-TTbar_SingleTop_VV_20100519_011910/";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-W_plus_Jets_20100521_141022/";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-enujj_preselection_skim/";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-eejj_low_mass_20100604_213652";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-eejj_20100518_231412";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-enujj_low_mass_20100608_175052";
# my $inputdir = "/castor/cern.ch/user/f/ferencek/LQ/RootNtuple/RootNtuple-V00-00-08-MC-LQ-enujj_20100519_011206";


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
