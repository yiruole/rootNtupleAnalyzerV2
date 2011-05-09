#!/usr/bin/perl

###########################################
## Code to launch the analysis in batch  ##
###########################################

#--------------------------------------------------------------
# Francesco Santanastasio  <francesco.santanastasio@cern.ch>
#--------------------------------------------------------------

print "Starting...\n";

use Time::Local;
use Getopt::Std;

## input info

my $inputList;
my $outputDir;
my $treename;
my $cutfile;

getopts('h:i:o:n:c:j:q:w:');

if(!$opt_i) {help();}
if(!$opt_o) {help();}
if(!$opt_n) {help();}
if(!$opt_c) {help();}
if(!$opt_j) {help();}
if(!$opt_q) {help();}
#if(!$opt_w) {help();}

if($opt_h) {help();}
if($opt_i) {$inputList = $opt_i;}
if($opt_o) {$outputDir = $opt_o;}
if($opt_n) {$treename = $opt_n;}
if($opt_c) {$cutfile = $opt_c;}
if($opt_j) {$njobs = $opt_j;}
if($opt_q) {$queue = $opt_q;}
if($opt_w) {$wait = $opt_w;} else {$wait=0;}

system "mkdir -p $outputDir";
system "cp $cutfile $outputDir/";

open CUTFILE, $cutfile or die $!;

my $found_json = 0;
my $jsonFile = "";

while (<CUTFILE>) {
    my $line = trim ($_);
    my $first_four_characters = substr($line,0,4);
    if (lc($first_four_characters) eq "json" )
    {	
	
	@split_line = split (" ", $line) ;
	$number_of_elements = $#split_line + 1;

	if ( $found_json ) 
	{
	    print "ERROR: Please specify only one JSON file in your cut file!\n";
	    exit 0;
 	}

	if ( $#split_line != 1 ) 
	{
	    print "ERROR: Too many ($number_of_elements) elements in the line.  Line reads:\n";
	    print "  $line\n";
	    print "  Format in cut file should be:\n";
	    print "  JSON <json file full path>\n";
	    exit 0;
	}

	$jsonFile = @split_line[1];

	open (JSONFILE, "<$jsonFile") || die ("ERROR: JSON file $jsonFile specified in $cutfile does not exist");
	close (JSONFILE );
   
	$found_json=1
    }    
} 

close (CUTFILE);

if ( $found_json ) {
    print  "cp $jsonFile $outputDir/\n";
    system "cp $jsonFile $outputDir/";
}

open (INPUTLIST, "<$inputList") || die ("...error reading file $inputList $!");
@inputList = <INPUTLIST>;
#print @inputList;
close(INPUTLIST);

open (FILE, "ls -l src/analysisClass.C |") || die ("...error reading the file src/analysisClass.C $!");
$analysisClassFull = <FILE>;
close(FILE);

## 1st split
my @array = split(/\s+/ , $analysisClassFull );
#print "$analysisClassFull\n";
#print "$array[10]\n";

if ( scalar(@array) != 11 ) 
{die ("...error src/analysisClass.C is not a symbolic link");}

## 2nd split
my @codenameC = split(/\// , $array[10] );
#print "@codenameC\n";
#print "$codenameC[scalar(@codenameC)-1]\n";

## 3rd split
my ($codename,$EXT) = split(/\./ , $codenameC[scalar(@codenameC)-1] );
#print "$codename\n";

for $line(@inputList)
{
    chomp($line);

    my @array1 = split(/\// , $line );
    my ($dataset,$EXT) = split(/\./ , $array1[scalar(@array1)-1] );

#    print "./main $line $cutfile $treename $outputDir/$codename\_\_\_$dataset $outputDir/$codename\_\_\_$dataset \n";
#    system "./main $line $cutfile $treename $outputDir/$codename\_\_\_$dataset $outputDir/$codename\_\_\_$dataset";

    
    print "./scripts/submit_batch.py -i $line -c $cutfile -t $treename -o $outputDir/$codename\_\_\_$dataset -n $njobs -q $queue \n";
    system "./scripts/submit_batch.py -i $line -c $cutfile -t $treename -o $outputDir/$codename\_\_\_$dataset -n $njobs -q $queue";    

    time.sleep($wait);
    
}

#---------------------------------------------------------#

sub help(){
    print "Usage: perl ./script/launchAnalysis.pl -i <inputList> -c <cutfile> -n <treename> -o <outputDir> -j <njobs> -q <queue> [-w <wait> -h <help?>] \n";
    print "Example: perl scripts/launchAnalysis_batch.pl -i HeepStudies_v1/inputListAllCurrent.txt -c HeepStudies_v1/cutFile_HeepElectronStudiesV1.txt -n rootTupleTree/tree -o TestFrancesco -j 2 -q 1nh -w 5 \n";
    print "Options:\n";
    print "-i <inputList>:      choose the file containing all the input lists for the analysis\n";
    print "-n <treename>:       choose the name of the TTree of the .root files you want to analyze\n";
    print "-c <cutfile>:        choose the name of the file with the analysis cuts\n";
    print "-o <outputDir>:      choose the output directory where the .root files will be stored\n";
    print "-j <njobs>:          choose number of jobs for batch submission, limited automatically to number of files in input list\n";
    print "-q <queue>:          choose queue for batch submission (choose among cmst3 8nm 1nh 8nh 1nd 1nw)\n";
    print "-w <wait>:           set a wait time in sec between submission of different datasets\n";
    print "-h <yes> :           to print the help \n";
    die "please, try again...\n";
}

# Perl trim function to remove whitespace from the start and end of the string
sub trim($)
{
	my $string = shift;
	$string =~ s/^\s+//;
	$string =~ s/\s+$//;
	return $string;
}
