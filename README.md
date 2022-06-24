### Introduction
This package provides a small facility to analyze one or a chain of root ntuples. It is independent of CMSSW. `baseClass` provides the methods that are common to all analysis, such as the method to read a list of root files and form a chain. It also provides a method to read a list of selection cuts.

The class `analysisClass` (`include/analysisClass.h` and `src/analysisClass.C`) inherits from `baseClass`.

The user's code should be placed in the method `Loop()` of `analysisClass`.

The main program (`src/main.C`) receives the configuration parameters (such as the input chain of root files and a file to provide a cut list) and executes the `analysisClass` code.

### Instructions
   1. Environment setup:
`source /cvmfs/sft.cern.ch/lcg/views/LCG_102rc1/x86_64-centos7-gcc11-opt/setup.sh`

   2. Check out the code (in a directory outside of any CMSSW areas):
`git clone git@github.com:CMSLQ/rootNtupleAnalyzerV2 Leptoquarks/rootNtupleAnalyzerV2`
You will also want the macros package:
`git clone git@github.com:CMSLQ/rootNtupleMacrosV2 Leptoquarks/rootNtupleMacrosV2`


   3. Copy the analysis template file into your own file:
`cp -i src/analysisClass_template.C src/analysisClass_myCode.C`
and make a symbolic link `analysisClass.C`:
`ln -s analysisClass_myCode.C src/analysisClass.C`
NOTE: There are many analysis classes already available in the macros repo.

   4. Compile:
Clean up any old builds if needed with `cmake --build build --target clean`.  
Then:  
`cmake -B build -S .`  
`cmake --build build -j4`

   5. If you are writing a new analysis class, add your analysis code to the method `Loop()` of analysisClass_myCode.C

   6. Compile as in step 4.

   7.  Run:
`build/main`
This will not work, as you need to specify input arguments.

Note1:
one can have several analyses in a directory, such as
`src/analysisClass_myCode1.C`
`src/analysisClass_myCode2.C`
`src/analysisClass_myCode3.C`
and move the symbolic link to the one to be used:
`ln -sf analysisClass_myCode2.C src/analysisClass.C`
and compile/run as above.

Note2:
The analysis macro area
https://github.com/CMSLQ/rootNtupleMacrosV2
allows separate development of the rootNtupleAnalyzerV2 package from the development of the analysis macros.

In order to compile and run an analysis macro
`/...fullPath.../rootNtupleMacros/src/analysisClass_XXX.C`
do:
`ln -sf /...fullPath.../rootNtupleMacrosV2/src/analysisClass_XXX.C src/analysisClass.C`
and compile/run as above.

### More details:

#### Example code:

The src/analysisClass_template.C comes with simple example code. The example code is enclosed by:
```
#ifdef USE_EXAMPLE
... code ...
#endif //end of USE_EXAMPLE
```
The code is NOT compiled by default. In order to compile it, uncomment the line
`#add_compile_options(-DUSE_EXAMPLE)` in `CMakeLists.txt`.

#### Providing cuts via file

A list of cut variable names and cut limits can be provided through a file (see config/cutFileExample.txt). The variable names in such a file have to be filled with a value calculated by the user analysisClass code; a function `fillVariableWithValue()` is provided - see example code.

Once all the cut variables have been filled, the cuts can be evaluated by calling `evaluateCuts()` - see example code. Do not forget to reset the cuts by calling `resetCuts()` at each event before filling the variables - see example code.

The function `evaluateCuts()` determines whether the cuts are satisfied or not, stores the pass/failed result of each cut, calculates cut efficiencies and fills histograms for each cut variable (binning provided by the cut file, see `config/cutFileExample.txt`).

The user has access to the cut results via a set of functions (see `include/baseClass.h`):
```
bool baseClass::passedCut(const string& s);
bool baseClass::passedAllPreviousCuts(const string& s);
bool baseClass::passedAllOtherCuts(const string& s);
```
where the string to be passed is the cut variable name.

The cuts are evaluated following the order of their appearance in the cut file (`config/cutFileExample.txt`).

One can simply change the sequence of lines in the cut file to have the cuts applied in a different order and to do cut efficiency studies.

Also, the user can assign to each cut a level (0,1,2,3,4 ... n) and use the function `bool baseClass::passedAllOtherSameLevelCuts(const string& s);` to have the pass/failed info on all other cuts with the same level.

There are also "pre" cuts with level=-1. These cuts are not actually evaluated; the corresponding lines in the cut file (`config/cutFileExample.txt`) are used to pass values to the user code (such as fiducial region limits). The user can access these values by using these functions:
```
float getPreCutValue1(const std::string& s);
float getPreCutValue2(const std::string& s);
float getPreCutValue3(const std::string& s);
float getPreCutValue4(const std::string& s);
std::string getPreCutString1(const std::string& s);
std::string getPreCutString2(const std::string& s);
std::string getPreCutString3(const std::string& s);
std::string getPreCutString4(const std::string& s);
```
Float values are string values are supported, as can be seen from the functions above.

#### Automatic histograms for cuts

The following histograms are generated for each cut variable with level >= 0:
- no cuts applied
- passedAllPreviousCuts
- passedAllOtherSameLevelCuts
- passedAllOtherCuts
- passedAllCut

and by default only the following subset
- no cuts applied
- passedAllPreviousCuts
- passedAllOtherCuts

is saved to the output root file. All histograms can be saved to the output root file by uncommenting the following line in `CMakeLists.txt`:
`#add_compile_options(-DSAVE_ALL_HISTOGRAMS)`

#### Automatic cut efficiency
The absolute and relative efficiency is calculated for each cut and stored in an output file (named `data/output/cutEfficiencyFile.dat` if the code is executed following the examples).

#### Good Run/LuminosityBlock JSON
The user has the option to implement a good run list using a JSON file. This requires two edits to the cut file and one edit to the `analysisClass.C` file.  A line must be inserted at the beginning of the cut file with the word "JSON" first, and then the full path of the desired JSON file. For example:

`JSON /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions11/7TeV/Prompt/Cert_160404-163369_7TeV_PromptReco_Collisions11_JSON.txt`

In addition, the user must define the JSON file selection in the cut file. This is done in the usual way:
```
#VariableName minValue1(<) maxValue1(>=) minValue2(<) maxValue2(>=) level histoNbinsMinMax

#------------ ------------ ------------- ------------ ------------- ----- ----------------

PassJSON 0 1 - - 0 2 -0.5 1.5
```
In the `analysisClass.C` file, the user must add the following line within the analysis loop:
`fillVariableWithValue ( "PassJSON", passJSON (run, ls, isData));`

Note that the use of a JSON file (good run list) is optional. If the user does not list a JSON file in the cut file, no selection will be made.

This tool was validated on May 18, 2011. The results of the validation study are here:
https://twiki.cern.ch/twiki/pub/CMS/ExoticaLeptoquarkAnalyzerRootNtupleMakerV2/json_validation.pdf

Additional scripts for running on several datasets:

---------------------------------------------------

See .`/doc/howToMakeAnalysisWithRootTuples.txt`

### Using the Optimizer (Jeff Temple):
The input cut file can also specify variables to be used in optimization studies.  To do so, add a line in the file for each variable to optimize. The first field of a line must be the name of the variable, second field must be "OPT", third field either ">" or "<". (The ">" sign will pass values greater than the applied threshold, and "<" will pass those less than the threshold.) 4th and 5th fields should be the minimum and maximum thresholds you wish to apply when scanning for optimal cuts. An example of the optimization syntax is:
```
#VariableName must be OPT > or < RangeMin RangeMax unused

#------------ ----------- ------ ------------ ------------- ------

muonPt OPT > 10 55 5
```
This optimizer will scan 10 different values, evenly distributed over the inclusive range [`RangeMin`, `RangeMax`]. At the moment, the 6th value is not used and does not need to be specified. The optimization cuts are always run after all the other cuts in the file, and are only run when all other cuts are passed. The above line will make 10 different cuts on `muonPt`, at [10, 15, 20, 25, ..., 55]. (`5` in the 6th field is meaningless here.)

The output of the optimization will be a 10-bin histogram, showing the number of events passing each of the 10 thresholds. Multiple optimization cuts may be applied in the same file. In the case where N optimization cuts are applied, a histogram of 10^N bins will be produced, with each bin corresponding to a unique cut combination.

No more than 6 variables may be optimized at one time (limitation in the number of bins for a TH1F ~ 10^6).
A file (optimizationCuts.txt in the working directory) that lists the cut values applied for each bin is produced and is needed for processing the optimization results later.

### Producing an ntuple skim (Dinko Ferencek):
The class `baseClass` provides the ability to produce a skimmed version of the input ntuples. In order to produce a skim, the following preliminary cut line has to be added to the cut file
```
#VariableName value1 value2 value3 value4 level

#------------ ------------ ------------- ------------ ------------- -----

produceSkim 1 - - - -1
```
and call the `fillSkimTree()` method for those events that meet the skimming criteria. One possible example is

if( passedCut("all") ) fillSkimTree();

If the above preliminary cut line is not present in the cut file, is commented out or its value1 is set to 0,

the skim creation will be turned off and calling the fillSkimTree() method will have no effect.

### JSON parser (Edmund Berry)
See https://hypernews.cern.ch/HyperNews/CMS/get/exotica-lq/266.html

### PU reweighting
~This is done in the NanoAOD postprocessing step.~~

### Reduced skims
Producing a new ntuple with a subset of cutFile variables and a subset of events (Paolo, Francesco, Edmund).

The class `baseClass` provides the ability to produce a new ntuple with a subset of the variables defined in the cutFile, and with a subset of events.

In order to do so, the following preliminary cut line has to be added to the cut file
```
#VariableName value1 value2 value3 value4 level

#------------ ------------ ------------- ------------ ------------- -----

produceReducedSkim 1 - - - -1
```
If the above preliminary cut line is not present in the cut file, is commented out or its value1 is set to 0, the skim creation will be turned off.
Then each variable that needs to be included in the new tree has to be flagged with `SAVE` in the cutFile at the end of the line where the variable is defined, as for `pT1stEle` and `pT2ndEle` below:
```
#VariableName minValue1(<) maxValue1(>=) minValue2(<) maxValue2(>=) level histoNbinsMinMax OptionalFlag

#------------ ------------ ------------- ------------ ------------- ----- ---------------- ------------

nEleFinal 1 +inf - - 0 11 -0.5 10.5

pT1stEle 85 +inf - - 1 100 0 1000 SAVE

pT2ndEle 30 +inf - - 1 100 0 1000 SAVE

invMass_ee 0 80 100 +inf 1 120 0 1200

LHEPdfWeight -inf +inf - - 1 16 -0.5 15.5 SAVEARRAY
```
Do not put anything for those variables that do not need to be saved, such as for `nEleFinal` and `invMass_ee`.

Finally, the variables that are cut on as part of the skim, in this case `nEleFinal`, need have level 0.

The new ntuple will be created in a file named as the std output root file with `_reduced_skim` appended before `.root` and the tree name will be as in the input root file.

#### Quick guide to skimming code:
1) Log into lxplus

2) Check out the rootNtupleAnalyzerV2 and rootNtupleMacrosV2 packages:
`git clone git@github.com:CMSLQ/rootNtupleAnalyzerV2 Leptoquarks/rootNtupleAnalyzerV2`
`git clone git@github.com:CMSLQ/rootNtupleMacrosV2 Leptoquarks/rootNtupleMacrosV2`
3) Set environment variables:
`export LQANA=$PWD/rootNtupleAnalyzerV2`
`export LQMACRO=$PWD/rootNtupleMacrosV2`
`export LQDATA="some path where you can store a lot of output.` Probably a subdirectory of your afs "work" area.

4) Navigate to the working directory:
`cd $LQANA`

5) Remember that to run the LQ analysis code, you need three pieces:

   1.  An analysisClass file, which is ready for you: `$LQMACRO/src2016/analysisClass_lq1_skim.C`

   2. A cut file, which is ready for you: `$LQMACRO/config2016/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt`

   3. An input list, which you must make for yourself using a script (see step 6)

6) Make the inputlist for the files you want to run on:
`python createList.py -i /eos/cms/store/group/phys_exotica/leptonsPlusJets/RootNtuple/scooper/RootNtuple-V00-03-11-Summer12MC_DY2JetsToLL_ScaleSysts_MG_20131008_124216/ -o config/FullNtupleDatasets_Summer12MC_DY2JetsToLL_ScaleSysts_MG
-m root`
The input list you want will be here:
`$LQANA/config/FullNtupleDatasets_Summer12MC_DY2JetsToLL_ScaleSysts_MGi/inputListAllCurrent.txt`
The `createList.py` script can be found in the submitJobsWithCrabV2 repository here: https://github.com/CMSLQ/submitJobsWithCrabV2

7) Link and then compile the analysis class you need:
`unlink src/analysisClass.C`
`ln -s $LQMACRO/src2012/analysisClass_lq1_skim.C src/analysisClass.C`
`cmake -B build -S .`
`cmake --build build -j4`
8) Test the code:
`./main config/FullNtupleDatasets_Summer12MC_DY2JetsToLL_ScaleSysts_MGi/DY2JetsToLL_M-50_scaledown_8TeV-madgraph__Summer12-START53_V7C-v1__AODSIM.txt $LQMACRO/config2012/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt rootTupleTree/tree test test`

9) You can run skim jobs on crab3 (recommended) by using: `scripts/launchAnalysis_crab3.py`

10) You can check the status of the jobs by using:
`scripts/multicrab.py`

9') For running locally, like for analysis on preselection skims, prepare a list of commands by editing some lines within scripts like the following:
`scripts/writeCommandsToRunOnMoreCutFiles_ForSkimToEOS_MakeSingleEleReducedSkim.sh`

You will need to edit:
`SUBDIR`: Output summary files will be stored in "$LQDATA/$SUBDIR". Name it whatever you want.
`FULLEOSDIR`: The actual miniskims will be stored in this EOS path. Name it whatever you want.
`INPUTLIST`: This should be a path to the inputlist you make in Step 6.

Everything else you should be able to leave unchanged.

Execute the script:
`./writeCommandsToRunOnMoreCutFiles_ForSkimToEOS_MakeSingleEleReducedSkim.sh`

10') Examine the commands you have created.
The script will produce a text file called something like:
`commandsToRunOnMoreCutFiles_MakeSingleEleReducedSkim_lxplus.txt`

Look at the contents of the text file. There should be two commands in it. The first command launches the jobs. The second command should only be executed when all jobs are finished -- it checks to make sure all jobs are complete.

11') Launch the jobs by executing the first command in the text file.

12') When the jobs are done, execute the second command in the text file and follow the instructions. If the second command prints out "All jobs successful" : you're done!

