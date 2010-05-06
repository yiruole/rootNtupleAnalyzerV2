#!/usr/local/bin/perl

###################################
## Code to create the input list ##
###################################

#--------------------------------------------------------------
# Francesco Santanastasio  <francesco.santanastasio@cern.ch>
#--------------------------------------------------------------

print "Starting...\n";

use Time::Local;
use Getopt::Std;

## input info

my $inputDir;
my $outputDir;
my $MATCH;
my $IsCASTOR=0;

getopts('h:d:o:m:c');

if(!$opt_d) {help();}
if(!$opt_o) {help();}
if(!$opt_m) {help();}

if($opt_h) {help();}
if($opt_d) {$inputDir = $opt_d;}
if($opt_o) {$outputDir = $opt_o;}
if($opt_m) {$MATCH = $opt_m;}
if($opt_c) {$IsCASTOR = $opt_c;}

system "mkdir -p $outputDir";

my @inputList;

if($IsCASTOR) #FILES ON CASTOR (CERN.CH)
{
    open (INPUTLIST, "rfdir $inputDir | awk \'\{print \$ 9\}\' | grep $MATCH | ") || die ("...error reading file $inputDir $!");
    @inputList = <INPUTLIST>;
    #print @inputList;
    close(INPUTLIST);
}
else                   #FILES ON REGULAR DISK
{
    open (INPUTLIST, "ls $inputDir | grep $MATCH |") || die ("...error reading file $inputDir $!");
    @inputList = <INPUTLIST>;
    #print @inputList;
    close(INPUTLIST);
}

my @AllLists;
my $AllListsFilename="$outputDir/inputListAllCurrent.txt";
system "rm -f $AllListsFilename";

#first loop to remove the old files
for $file(@inputList)
{

    ## split each line
    my ($foo) = ""; ($foo) = grep(/\_\d+\_\d+\.root/, $file);
    my ($dataset) = "";
    if ($foo ne "") {($dataset) = split( /\_\d+\_\d+\.root/ , $file );}
    else {($dataset) = split( /\_\d+\.root/ , $file );}
    #print "$dataset\n";

    $listfilename="$dataset.txt";
    #print "$listfilename\n";

    system "rm -f $outputDir/$listfilename";

}


#second loop to create the new files
for $file(@inputList)
{
    chomp($file);
    #print "$file\n";

    ## split each line
    my ($foo) = ""; ($foo) = grep(/\_\d+\_\d+\.root/, $file);
    my ($dataset) = "";
    if ($foo ne "") {($dataset) = split( /\_\d+\_\d+\.root/ , $file );}
    else {($dataset) = split( /\_\d+\.root/ , $file );}
    #print "$dataset\n";

    $listfilename="$outputDir/$dataset.txt";
    #print "$listfilename\n";

    system "touch $listfilename";

    my $IsPresent=0;
    for $line(@AllLists)
    {
	if($IsPresent==0)
	{
	    if($listfilename eq $line)
	    {
		$IsPresent=1;
	    }
	}
    }

    if($IsPresent==0)
    {
	print "$listfilename\n";
	push @AllLists, $listfilename;
    }

    if($IsCASTOR) #FILES ON CASTOR (CERN.CH)
    {
	open(LISTFILENAME,">>$listfilename");
	print LISTFILENAME "rfio:$inputDir/$file\n";
	close(LISTFILENAME);
    }
    else
    {
	open(LISTFILENAME,">>$listfilename");
	print LISTFILENAME "$inputDir/$file\n";
	close(LISTFILENAME);
    }

}


open(LISTALLFILENAME,">$AllListsFilename");
for $txtfile(@AllLists)
{
    chomp($txtfile);
    print LISTALLFILENAME "$txtfile\n";
}
close(LISTALLFILENAME);

print "List created: $AllListsFilename\n";

#print "@AllLists\n";

#---------------------------------------------------------#

sub help(){
    print "Usage: ./createList.pl -d <inputDir> -m <match> -o <outputDir> -c yes [optional]  [-h <help?>] \n";
    print "Example: ./createList.pl -d /home/santanas/Data/Leptoquarks/RootNtuples/V00-00-06_2008121_163513/output -m root -o /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config \n";
    print "Example for a CASTOR directory: ./createList.pl -d /castor/cern.ch/user/s/santanas/LQ/RootNtuple/RootNtuple-V00-00-03-DATA-GR_R_35X_V7A_SD_EG-v2-132440-133511_20100505_233733 -m root -o /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config -c yes \n";
    print "Options:\n";
    print "-d <inputDir>:       choose the input directory containing the files (FULL PATH REQUIRED + NO SLASH AT THE END)\n";
    print "-m <match>:          choose the parameter MATCH, will be used to select only the files whose filename matches with the string MATCH\n";
    print "-o <outputDir>:      choose the output directory where the .txt list files will be stored (FULL PATH REQUIRED NO SLASH AT THE END)\n";
    print "-c <yes> [optional]: set to yes if the input files are in a CASTOR directory \n";
    print "-h <yes> :           to print the help \n";
    die "please, try again...\n";
}
