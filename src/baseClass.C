#define baseClass_cxx
#include "baseClass.h"
#include <boost/lexical_cast.hpp>

baseClass::baseClass(string * inputList, string * cutFile, string * treeName, string * outputFileName, string * cutEfficFile):
  PileupWeight_ ( 1.0 ),
  fillSkim_                         ( true ) ,
  fillAllPreviousCuts_              ( true ) ,
  fillAllOtherCuts_                 ( true ) ,
  fillAllSameLevelAndLowerLevelCuts_( true ) ,
  fillAllCuts_                      ( true ) ,
  oldKey_                           ( "" ) 
{
  //STDOUT("begins");
  // nOptimizerCuts_ = 26;
  nOptimizerCuts_ = 20;
  inputList_ = inputList;
  cutFile_ = cutFile;
  treeName_= treeName;
  outputFileName_ = outputFileName;
  cutEfficFile_ = cutEfficFile;
  init();
  //STDOUT("ends");
}

baseClass::~baseClass()
{
  if( !writeCutHistos() )
    {
      STDOUT("ERROR: writeCutHistos did not complete successfully.");
    }
  if( !writeCutEfficFile() )
    {
      STDOUT("ERROR: writeStatFile did not complete successfully.");
    }
  if( !writeUserHistos() )
    {
      STDOUT("ERROR: writeUserHistos did not complete successfully.");
    }
  if( !writeSkimTree() )
    {
      STDOUT("ERROR: writeSkimTree did not complete successfully.");
    }
  if( !writeReducedSkimTree() )
    {
      STDOUT("ERROR: writeReducedSkimTree did not complete successfully.");
    }
  output_root_->Close();
  if(produceSkim_) skim_file_->Close();
  if(produceReducedSkim_) reduced_skim_file_->Close();
}

void baseClass::init()
{
  //STDOUT("begins");
  tree_ = NULL;
  readInputList();
  readCutFile();
  if(tree_ == NULL){
    STDOUT("baseClass::init(): ERROR: tree_ = NULL ");
    exit(-1);
  }
  Init(tree_);

  //char output_root_title[200];
  //sprintf(output_root_title,"%s%s",&std::string(*outputFileName_)[0],".root");
  //output_root_ = new TFile(&output_root_title[0],"RECREATE");

  //directly from string
  output_root_ = new TFile((*outputFileName_ + ".root").c_str(),"RECREATE");

  // Skim stuff
  produceSkim_ = false;
  NAfterSkim_ = 0;
  if(int(getSkimPreCutValue("produceSkim"))==1) produceSkim_ = true;
  
  if(produceSkim_) {
    
    skim_file_ = new TFile((*outputFileName_ + "_skim.root").c_str(),"RECREATE");
    skim_tree_ = fChain->CloneTree(0);
    hCount_ = new TH1I("EventCounter","Event Counter",2,-0.5,1.5);
    hCount_->GetXaxis()->SetBinLabel(1,"all events");
    hCount_->GetXaxis()->SetBinLabel(2,"passed");
  }

  // Reduced Skim stuff
  produceReducedSkim_ = false;
  NAfterReducedSkim_ = 0;
  if(int(getSkimPreCutValue("produceReducedSkim"))==1) produceReducedSkim_ = true;

  if(produceReducedSkim_) {

    reduced_skim_file_ = new TFile((*outputFileName_ + "_reduced_skim.root").c_str(),"RECREATE");
    reduced_skim_tree_= new TTree("tree","Reduced Skim");
    hReducedCount_ = new TH1I("EventCounter","Event Counter",2,-0.5,1.5);
    hReducedCount_->GetXaxis()->SetBinLabel(1,"all events");
    hReducedCount_->GetXaxis()->SetBinLabel(2,"passed");
    for (map<string, cut>::iterator cc = cutName_cut_.begin(); cc != cutName_cut_.end(); cc++)
      {
	cut * c = & (cc->second);
	if(c->saveVariableInReducedSkim)    reduced_skim_tree_->Branch(c->variableName.c_str(),&c->value,(c->variableName+"/D").c_str());
      }
  }

  //  for (map<string, cut>::iterator it = cutName_cut_.begin();
  //   it != cutName_cut_.end(); it++) STDOUT("cutName_cut->first = "f<<it->first)
  //  for (vector<string>::iterator it = orderedCutNames_.begin();
  //       it != orderedCutNames_.end(); it++) STDOUT("orderedCutNames_ = "<<*it)
  //STDOUT("ends");
}

void baseClass::readInputList()
{

  TChain *chain = new TChain(treeName_->c_str());
  char pName[500];
  skimWasMade_ = true;
  jsonFileWasUsed_ = false;
  pileupMCFileWasUsed_ = false;
  pileupDataFileWasUsed_ = false;
  NBeforeSkim_ = 0;
  int NBeforeSkim;

  STDOUT("baseClass::readinputList(): inputList_ =  "<< *inputList_ );

  ifstream is(inputList_->c_str());
  if(is.good())
  {
    STDOUT("baseClass::readInputList: Starting reading list: " << *inputList_ );
    while( is.getline(pName, 500, '\n') )
    {
      if (pName[0] == '#') continue;
      //if (pName[0] == ' ') continue; // do we want to skip lines that start with a space?
      if (pName[0] == '\n') continue;// simple protection against blank lines
      // if it's just /store (e.g., via crab3) add the necessary prefix
      std::string name(pName);
      if(name.find("/store") != std::string::npos && name.find("/store")==0)
        name.insert(0,"root://eoscms//eos/cms");
      STDOUT("Adding file: " << name);
      chain->Add(name.c_str());
      NBeforeSkim = getGlobalInfoNstart(name.c_str());
      NBeforeSkim_ = NBeforeSkim_ + NBeforeSkim;
      STDOUT("Initial number of events: NBeforeSkim, NBeforeSkim_ = "<<NBeforeSkim<<", "<<NBeforeSkim_);
    }
    tree_ = chain;
    STDOUT("baseClass::readInputList: Finished reading list: " << *inputList_ );
  }
  else
  {
    STDOUT("baseClass::readInputList: ERROR opening inputList:" << *inputList_ );
    exit (-1);
  }
  is.close();

}

bool is_number(const std::string& s) {
  try {
    double number = boost::lexical_cast<double>(s);
  } catch(boost::bad_lexical_cast& e) {
    return false;
  }
  return true;
}

void baseClass::readCutFile()
{
  string s;
  STDOUT("Reading cutFile_ = "<< *cutFile_)

  ifstream is(cutFile_->c_str());
  if(is.good())
    {
      //      STDOUT("Reading file: " << *cutFile_ );
      int id=0;
      int optimize_count=0;
      while( getline(is,s) )
        {
          STDOUT("read line: " << s);
          if (s[0] == '#' || s.empty()) continue;
	  vector<string> v = split(s);
	  if ( v.size() == 0 ) continue;

	  STDOUT("starting JSON code");
	  
	  if ( v[0] == "JSON" ){ 

	    if ( jsonFileWasUsed_ ){
	      STDOUT("ERROR: Please specify only one JSON file in your cut file!");
	      return;
	    }
	    
	    if ( v.size() != 2 ){
	      STDOUT("ERROR: In your cutfile, JSON file line must have the syntax: \"JSON <full json file path>\"");
	    }
	    jsonFileName_ = v[1];
	    STDOUT("Getting JSON file: " << v[1]);
	    jsonParser_.parseJSONFile ( & v[1] ) ;
	    jsonParser_.printGoodLumis();
	    jsonFileWasUsed_ = true;
	    continue;
	  }

	  STDOUT ("starting pileup reweighting code 1");
	  
	  if ( v[0] == "PILEUP_DATA_ROOT_FILE" ){ 
	    if ( pileupDataFileWasUsed_ ) { 
	      STDOUT("ERROR: Please specify only one PILEUP_DATA_ROOT_FILE in your cut file!");
	      return;
	    }

	    if ( v.size() != 2 ){
	      STDOUT("ERROR: In your cutfile, PILEUP_DATA_ROOT_FILE line must have the syntax: \"PILEUP_DATA_ROOT_FILE <full pileup data file path>\"");
	    }
	    
	    pileupDataFileName_ = v[1];
	    STDOUT("Getting PILEUP_DATA_ROOT_FILE:" << v[1]);
	    pileupReweighter_.readPileupDataFile ( & v[1] ) ;
	    pileupDataFileWasUsed_ = true;
	    continue;
	  }

	  STDOUT ("starting pileup reweighting code 2");

	  if ( v[0] == "PILEUP_MC_TXT_FILE" ){ 
	    if ( pileupMCFileWasUsed_ ) { 
	      STDOUT("ERROR: Please specify only one PILEUP_MC_TXT_FILE in your cut file!");
	      return;
	    }

	    if ( v.size() != 2 ){
	      STDOUT("ERROR: In your cutfile, PILEUP_MC_TXT_FILE line must have the syntax: \"PILEUP_MC_TXT_FILE <full pileup MC file path>\"");
	    }
	    
	    pileupMCFileName_ = v[1];
	    STDOUT("Getting PILEUP_MC_TXT_FILE:" << v[1]);
	    pileupReweighter_.readPileupMCFile ( & v[1] ) ;
	    pileupMCFileWasUsed_ = true;
	    continue;
	  }

          STDOUT("starting OPT code");
	  if (v[1]=="OPT") // add code for grabbing optimizer objects
	    {
	      if (optimizeName_cut_.size()>=6)
		{
		  STDOUT("WARNING:  Optimizer can only accept up to 6 variables.\nVariable "<<v[0]<<" is not being included.");
		  continue;
		}
	      bool found=false;
	      for (int i=0;i<optimizeName_cut_.size();++i)
		{
		  if (optimizeName_cut_[i].variableName==v[0])
		    {
		      STDOUT("ERROR:  variableName = "<<v[0]<<" is already being optimized in optimizedName_cut_.  Skipping.");
		      found=true;
		      break;
		    }
		}
	      if (found) continue;

	      int level_int = atoi(v[5].c_str());
	      bool greaterthan=true;
	      if (v[2]=="<") greaterthan=false;
	      double minval=atof(v[3].c_str());
	      double maxval=atof(v[4].c_str());
	      Optimize opt(optimize_count,v[0],minval, maxval, greaterthan, level_int, nOptimizerCuts_ );
	      optimizeName_cut_[optimize_count]=opt; // order cuts by cut #, rather than name, so that optimization histogram is consistently ordered
	      ++optimize_count;
	      continue;
	    }

	  map<string, cut>::iterator cc = cutName_cut_.find(v[0]);
	  if( cc != cutName_cut_.end() )
	    {
	      STDOUT("ERROR: variableName = "<< v[0] << " exists already in cutName_cut_. Returning.");
	      return;
	    }

	  int level_int = atoi( v[5].c_str() );
	  if(level_int == -1)
	    {
	      map<string, preCut>::iterator cc = preCutName_cut_.find(v[0]);
	      if( cc != preCutName_cut_.end() )
		{
		  STDOUT("ERROR: variableName = "<< v[0] << " exists already in preCutName_cut_. Returning.");
		  return;
		}
	      preCutInfo_ << "### Preliminary cut values: " << s <<endl;
	      preCut thisPreCut;
	      thisPreCut.variableName =     v[0];
	      if ( is_number ( v[1] ) ) thisPreCut.value1  = decodeCutValue( v[1] );
	      else                      thisPreCut.string1 = v[1];
	      if ( is_number ( v[2] ) ) thisPreCut.value2  = decodeCutValue( v[2] );
	      else                      thisPreCut.string2 = v[2];
	      if ( is_number ( v[3] ) ) thisPreCut.value1  = decodeCutValue( v[3] );
	      else                      thisPreCut.string3 = v[3];
	      if ( is_number ( v[4] ) ) thisPreCut.value2  = decodeCutValue( v[4] );
	      else                      thisPreCut.string4 = v[4];
	      preCutName_cut_[thisPreCut.variableName]=thisPreCut;
	      continue;
	    }
	  cut thisCut;
	  thisCut.variableName =     v[0];
	  string m1=v[1];
	  string M1=v[2];
	  string m2=v[3];
	  string M2=v[4];
	  if( m1=="-" || M1=="-" )
	    {
	      STDOUT("ERROR: minValue1 and maxValue2 have to be provided. Returning.");
	      return; // FIXME implement exception
	    }
	  if( (m2=="-" && M2!="-") || (m2!="-" && M2=="-") )
	    {
	      STDOUT("ERROR: if any of minValue2 and maxValue2 is -, then both have to be -. Returning");
	      return; // FIXME implement exception
	    }
	  if( m2=="-") m2="+inf";
	  if( M2=="-") M2="-inf";
	  thisCut.minValue1  = decodeCutValue( m1 );
	  thisCut.maxValue1  = decodeCutValue( M1 );
	  thisCut.minValue2  = decodeCutValue( m2 );
	  thisCut.maxValue2  = decodeCutValue( M2 );
	  thisCut.level_int  = level_int;
	  thisCut.level_str  =       v[5];
	  thisCut.histoNBins = atoi( v[6].c_str() );
	  thisCut.histoMin   = atof( v[7].c_str() );
	  thisCut.histoMax   = atof( v[8].c_str() );
	  thisCut.saveVariableInReducedSkim = ( v.size()==10 && v[9]=="SAVE" ) ? true : false;

	  // Not filled from file
	  thisCut.id=++id;
	  string s1;
	  if(skimWasMade_)
	    {
	      s1 = "cutHisto_skim___________________" + thisCut.variableName;
	    }
	  else
	    {
	      s1 = "cutHisto_noCuts_________________" + thisCut.variableName;
	    }
	  string s2 = "cutHisto_allPreviousCuts________" + thisCut.variableName;
	  string s3 = "cutHisto_allOthrSmAndLwrLvlCuts_" + thisCut.variableName;
	  string s4 = "cutHisto_allOtherCuts___________" + thisCut.variableName;
	  string s5 = "cutHisto_allCuts________________" + thisCut.variableName;
	  thisCut.histo1 = TH1F (s1.c_str(),"", thisCut.histoNBins, thisCut.histoMin, thisCut.histoMax);
	  thisCut.histo2 = TH1F (s2.c_str(),"", thisCut.histoNBins, thisCut.histoMin, thisCut.histoMax);
	  thisCut.histo3 = TH1F (s3.c_str(),"", thisCut.histoNBins, thisCut.histoMin, thisCut.histoMax);
	  thisCut.histo4 = TH1F (s4.c_str(),"", thisCut.histoNBins, thisCut.histoMin, thisCut.histoMax);
	  thisCut.histo5 = TH1F (s5.c_str(),"", thisCut.histoNBins, thisCut.histoMin, thisCut.histoMax);
	  thisCut.histo1.Sumw2();
	  thisCut.histo2.Sumw2();
	  thisCut.histo3.Sumw2();
	  thisCut.histo4.Sumw2();
	  thisCut.histo5.Sumw2();
	  // Filled event by event
	  thisCut.filled = false;
	  thisCut.value = 0;
	  thisCut.weight = 1;
	  thisCut.passed = false;
	  thisCut.nEvtPassedBeforeWeight=0;
	  thisCut.nEvtPassed=0;
	  thisCut.nEvtPassedErr2=0;
	  thisCut.nEvtPassedBeforeWeight_alreadyFilled = false;

	  orderedCutNames_.push_back(thisCut.variableName);
	  cutName_cut_[thisCut.variableName]=thisCut;

	}
      if ( pileupMCFileWasUsed_ && pileupDataFileWasUsed_ ) {
	pileupReweighter_.calculatePileupWeights();
	pileupReweighter_.printPileupWeights();
      }
      else if ( (!pileupMCFileWasUsed_) && pileupDataFileWasUsed_  ||
		pileupMCFileWasUsed_  && (!pileupDataFileWasUsed_) ) { 
	STDOUT("ERROR: You must specify TWO pileup files in your cutfile:");
	if ( pileupMCFileWasUsed_   ) STDOUT("   You have only specified PILEUP_MC_TXT_FILE " ) ;
	if ( pileupDataFileWasUsed_ ) STDOUT("   You have only specified PILEUP_DATA_ROOT_FILE " ) ;
	exit(1);
      }
      STDOUT( "baseClass::readCutFile: Finished reading cutFile: " << *cutFile_ );
    }
  else
    {
      STDOUT("ERROR opening cutFile:" << *cutFile_ );
      exit (1);
    }
  // make optimizer histogram
  if (optimizeName_cut_.size()>0)
    {
      h_optimizer_=new TH1F("optimizer","Optimization of cut variables",(int)pow(nOptimizerCuts_,optimizeName_cut_.size()),0,
			    pow(nOptimizerCuts_,optimizeName_cut_.size()));
    }

  // Create a histogram that will show events passing cuts
  int cutsize=orderedCutNames_.size()+1;
  if (skimWasMade_) ++cutsize;
  gDirectory->cd();
  eventcuts_=new TH1F("EventsPassingCuts","Events Passing Cuts",cutsize,0,cutsize);

  is.close();

}

void baseClass::resetCuts(const string& s)
{
  for (map<string, cut>::iterator cc = cutName_cut_.begin(); cc != cutName_cut_.end(); cc++)
    {
      cut * c = & (cc->second);
      c->filled = false;
      c->value = 0;
      c->weight = 1;
      c->passed = false;
      if(s == "newEvent")
	{
	  c->nEvtPassedBeforeWeight_alreadyFilled = false;
	}
      else if(s != "sameEvent")
	{
	  STDOUT("ERROR: unrecognized option. Only allowed options are 'sameEvent' and 'newEvent'; no option = 'newEvent'.");
	}
    }
  combCutName_passed_.clear();
  return;
}

void baseClass::fillVariableWithValue(const string& s, const double& d, const double& w)
{

  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: variableName = "<< s << " not found in cutName_cut_. Returning");
      return;
    }
  else
    {
      cut * c = & (cc->second);
      c->filled = true;
      c->value = d;
      c->weight = w;
      
// if ( pileupReweighter_.pileupWeightsCalculated() ) 
// 	c ->weight *= PileupWeight_;
    }
  fillOptimizerWithValue(s, d);
  return;
}

bool baseClass::variableIsFilled(const string& s)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning");
    }
  cut * c = & (cc->second);
  return (c->filled);
}

double baseClass::getVariableValue(const string& s)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_.");
    }
  cut * c = & (cc->second);
  if( !variableIsFilled(s) )
    {
      STDOUT("ERROR: requesting value of not filled variable "<<s);
    }
  return (c->value);
}

void baseClass::fillOptimizerWithValue(const string& s, const double& d)
{
  for (int i=0;i<optimizeName_cut_.size();++i)
    {
      if (optimizeName_cut_[i].variableName==s)
	{
	  optimizeName_cut_[i].value=d;
	  return;
	}
    }
  return;
}

void baseClass::evaluateCuts()
{
  //  resetCuts();
  combCutName_passed_.clear();
  for (vector<string>::iterator it = orderedCutNames_.begin();
       it != orderedCutNames_.end(); it++)
    {
      cut * c = & (cutName_cut_.find(*it)->second);
      if( ! ( c->filled && (c->minValue1 < c->value && c->value <= c->maxValue1 || c->minValue2 < c->value && c->value <= c->maxValue2 ) ) )
	{
          c->passed = false;
          combCutName_passed_[c->level_str.c_str()] = false;
          combCutName_passed_["all"] = false;
	}
      else
	{
	  c->passed = true;
	  map<string,bool>::iterator cp = combCutName_passed_.find( c->level_str.c_str() );
	  combCutName_passed_[c->level_str.c_str()] = (cp==combCutName_passed_.end()?true:cp->second);
	  map<string,bool>::iterator ap = combCutName_passed_.find( "all" );
	  combCutName_passed_["all"] = (ap==combCutName_passed_.end()?true:ap->second);
	}
    }

  // reset optimization cut values
  //for (int i=0;i<optimizeName_cut_.size();++i)
  //  optimizeName_cut_[i].value=0;
  runOptimizer();

  if( !fillCutHistos() )
    {
      STDOUT("ERROR: fillCutHistos did not complete successfully.");
    }

  if( !updateCutEffic() )
    {
      STDOUT("ERROR: updateCutEffic did not complete successfully.");
    }

  return ;
}

void baseClass::runOptimizer()
{

  // don't run optimizer if no optimized cuts specified
  if (optimizeName_cut_.size()==0)
    return;

  // first, check that all cuts (except those to be optimized) have been passed

  for (vector<string>::iterator it = orderedCutNames_.begin();
       it != orderedCutNames_.end(); it++)
    {
      bool ignorecut=false;
      for (unsigned int i=0; i < optimizeName_cut_.size();++i)
	{
	  const string str = (const string)(*it);
	  if (optimizeName_cut_[i].variableName.compare(str)==0)
	    {
	      ignorecut=true;
	      break;
	    }
	}
      if (ignorecut) continue;
      if (passedCut(*it) == false)
	return;
    }

  /*
  if (combCutName_passed_["all"] == false)
    return;
  */

  // loop over up to 6 cuts
  int counter=0;
  int thesize=optimizeName_cut_.size();
  int mysize=thesize;
  std::vector<bool> counterbins;
  for (int i=0;i<pow(nOptimizerCuts_,thesize);++i) counterbins.push_back(true); // assume true

  // lowest-numbered cut appears first in cut ordering
  // That is, for cut:  ABCDEF
  //  A is the index of cut0, B is cut 1, etc.
  for (int cc=0;cc<thesize;++cc) // loop over all cuts, starting at cut 0
    {
      --mysize;
      for (int i=0;i<nOptimizerCuts_;++i) // loop over 10 cuts for each
	{
	  if (!optimizeName_cut_[cc].Compare(i)) // cut failed; set all values associated with cut to false
	    {
	      // loop over  all cut values starting with current cut
	      for (unsigned int j=(int)(i*pow(nOptimizerCuts_,mysize));j<int(pow(nOptimizerCuts_,thesize));++j)
		{
		  // if relevant digit of the cut value matches the current (failed) cut, set this cut to false
		  if ((j/int(pow(nOptimizerCuts_,mysize)))%nOptimizerCuts_==i)
		    counterbins[j]=false;
		  if (j>counterbins.size())
		    continue; // shouldn't ever happen
		}
	    } // if (cut comparison failed)
	} // for (int i=0;i<10;++i)
    }
  // now fill histograms
  for (int i=0;i<counterbins.size();++i)
    {
      if (counterbins[i]==true)
	h_optimizer_->Fill(i,cutName_cut_[orderedCutNames_.at(orderedCutNames_.size()-1)].weight); // take the event weight from the last cut in the cut file

    }

  return;
} //runOptimizer

bool baseClass::passedCut(const string& s)
{
  bool ret = false;
  //  map<string, bool>::iterator vp = cutName_passed_.find(s);
  //  if( vp != cutName_passed_.end() ) return ret = vp->second;
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc != cutName_cut_.end() )
    {
      cut * c = & (cutName_cut_.find(s)->second);
      return (c->filled && c->passed);
    }
  map<string, bool>::iterator cp = combCutName_passed_.find(s);
  if( cp != combCutName_passed_.end() )
    {
      return ret = cp->second;
    }
  STDOUT("ERROR: did not find variableName = "<<s<<" neither in cutName_cut_ nor combCutName_passed_. Returning false.");
  return (ret=false);
}

bool baseClass::passedAllPreviousCuts(const string& s)
{
  //STDOUT("Examining variableName = "<<s);

  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
      return false;
    }

  for (vector<string>::iterator it = orderedCutNames_.begin();
       it != orderedCutNames_.end(); it++)
    {
      cut * c = & (cutName_cut_.find(*it)->second);
      if( c->variableName == s )
	{
	  return true;
	}
      else
	{
	  if( ! (c->filled && c->passed) ) return false;
	}
    }
  STDOUT("ERROR. It should never pass from here.");
}

bool baseClass::passedAllOtherCuts(const string& s)
{
  //STDOUT("Examining variableName = "<<s);
  bool ret = true;

  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
      return false;
    }

  for (map<string, cut>::iterator cc = cutName_cut_.begin(); cc != cutName_cut_.end(); cc++)
    {
      cut * c = & (cc->second);
      if( c->variableName == s )
	{
	  continue;
	}
      else
	{
	  if( ! (c->filled && c->passed) ) return false;
	}
    }
  return ret;
}

bool baseClass::passedAllOtherSameAndLowerLevelCuts(const string& s)
{
  //STDOUT("Examining variableName = "<<s);
  bool ret = true;
  int cutLevel;
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
      return false;
    }
  else
    {
      cutLevel = cc->second.level_int;
    }

  for (map<string, cut>::iterator cc = cutName_cut_.begin(); cc != cutName_cut_.end(); cc++)
    {
      cut * c = & (cc->second);
      if( c->level_int > cutLevel || c->variableName == s )
	{
	  continue;
	}
      else
	{
	  if( ! (c->filled && c->passed) ) return false;
	}
    }
  return ret;
}

double baseClass::getPreCutValue1(const string& s)
{
  double ret;
  map<string, preCut>::iterator cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Returning");
    }
  preCut * c = & (cc->second);
  if(c->value1 == -99999999999) STDOUT("ERROR: value1 of preliminary cut "<<s<<" was not provided.");
  return (c->value1);
}

double baseClass::getPreCutValue2(const string& s)
{
  double ret;
  map<string, preCut>::iterator cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Returning");
    }
  preCut * c = & (cc->second);
  if(c->value2 == -99999999999) STDOUT("ERROR: value2 of preliminary cut "<<s<<" was not provided.");
  return (c->value2);
}

double baseClass::getPreCutValue3(const string& s)
{
  double ret;
  map<string, preCut>::iterator cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Returning");
    }
  preCut * c = & (cc->second);
  if(c->value3 == -99999999999) STDOUT("ERROR: value3 of preliminary cut "<<s<<" was not provided.");
  return (c->value3);
}

double baseClass::getPreCutValue4(const string& s)
{
  double ret;
  map<string, preCut>::iterator cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Returning");
    }
  preCut * c = & (cc->second);
  if(c->value4 == -99999999999) STDOUT("ERROR: value4 of preliminary cut "<<s<<" was not provided.");
  return (c->value4);
}






string baseClass::getPreCutString1(const string& s)
{
  string ret;
  map<string, preCut>::iterator cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Returning");
    }
  preCut * c = & (cc->second);
  return (c->string1);
}


















double baseClass::getCutMinValue1(const string& s)
{
  double ret;
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning");
    }
  cut * c = & (cc->second);
  return (c->minValue1);
}

double baseClass::getCutMaxValue1(const string& s)
{
  double ret;
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning");
    }
  cut * c = & (cc->second);
  return (c->maxValue1);
}

double baseClass::getCutMinValue2(const string& s)
{
  double ret;
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning");
    }
  cut * c = & (cc->second);
  return (c->minValue2);
}

double baseClass::getCutMaxValue2(const string& s)
{
  double ret;
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning");
    }
  cut * c = & (cc->second);
  return (c->maxValue2);
}

const TH1F& baseClass::getHisto_noCuts_or_skim(const string& s)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }

  cut * c = & (cutName_cut_.find(s)->second);
  return (c->histo1);
}

const TH1F& baseClass::getHisto_allPreviousCuts(const string& s)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }

  cut * c = & (cutName_cut_.find(s)->second);
  return (c->histo2);
}

const TH1F& baseClass::getHisto_allOthrSmAndLwrLvlCuts(const string& s)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }

  cut * c = & (cutName_cut_.find(s)->second);
  return (c->histo3);
}

const TH1F& baseClass::getHisto_allOtherCuts(const string& s)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }

  cut * c = & (cutName_cut_.find(s)->second);
  return (c->histo4);
}

const TH1F& baseClass::getHisto_allCuts(const string& s)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }

  cut * c = & (cutName_cut_.find(s)->second);
  return (c->histo5);
}

int baseClass::getHistoNBins(const string& s)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }
  cut * c = & (cutName_cut_.find(s)->second);
  return (c->histoNBins);
}

double baseClass::getHistoMin(const string& s)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }
  cut * c = & (cutName_cut_.find(s)->second);
  return (c->histoMin);
}

double baseClass::getHistoMax(const string& s)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }
  cut * c = & (cutName_cut_.find(s)->second);
  return (c->histoMax);
}


bool baseClass::fillCutHistos()
{
  bool ret = true;
  for (vector<string>::iterator it = orderedCutNames_.begin();
       it != orderedCutNames_.end(); it++)
    {
      cut * c = & (cutName_cut_.find(*it)->second);
      if( c->filled )
	{
	  if ( fillSkim_ ) 
	    c->histo1.Fill( c->value, c->weight );
	  if ( fillAllPreviousCuts_ ) 
	    if( passedAllPreviousCuts(c->variableName) )                c->histo2.Fill( c->value, c->weight );
	  if( fillAllSameLevelAndLowerLevelCuts_) 
	    if( passedAllOtherSameAndLowerLevelCuts(c->variableName) )  c->histo3.Fill( c->value, c->weight );
	  if( fillAllOtherCuts_ ) 
	    if( passedAllOtherCuts(c->variableName) )                   c->histo4.Fill( c->value, c->weight );
	  if( fillAllCuts_ ) 
	    if( passedCut("all") )                                      c->histo5.Fill( c->value, c->weight );
	}
    }
  return ret;
}

bool baseClass::writeCutHistos()
{
  bool ret = true;
  output_root_->cd();
  for (vector<string>::iterator it = orderedCutNames_.begin();
       it != orderedCutNames_.end(); it++)
    {
      cut * c = & (cutName_cut_.find(*it)->second);
      if ( fillSkim_                          ) c->histo1.Write();
      if ( fillAllPreviousCuts_               ) c->histo2.Write();
      if ( fillAllOtherCuts_                  ) c->histo4.Write();
#ifdef SAVE_ALL_HISTOGRAMS 
      if ( fillAllSameLevelAndLowerLevelCuts_ ) c->histo3.Write();
      if ( fillAllCuts_                       ) c->histo5.Write();
#endif // SAVE_ALL_HISTOGRAMS
    }

  // Any failure mode to implement?
  return ret;
}

bool baseClass::updateCutEffic()
{
  bool ret = true;
  for (vector<string>::iterator it = orderedCutNames_.begin();
       it != orderedCutNames_.end(); it++)
    {
      cut * c = & (cutName_cut_.find(*it)->second);
      if( passedAllPreviousCuts(c->variableName) )
	{
	  if( passedCut(c->variableName) )
	    {
	      if ( c->nEvtPassedBeforeWeight_alreadyFilled == false)
		{
		  c->nEvtPassedBeforeWeight += 1;
		  c->nEvtPassedBeforeWeight_alreadyFilled = true;
		}
	      c->nEvtPassed+=c->weight;
	      c->nEvtPassedErr2 += (c->weight)*(c->weight);
	    }
	}
    }
  return ret;
}


bool baseClass::writeCutEfficFile()
{
  bool ret = true;
  output_root_->cd();

  // Set bin labels for event counter histogram
  int bincounter=1;

  eventcuts_->GetXaxis()->SetBinLabel(bincounter,"NoCuts");
  ++bincounter;

  if (skimWasMade_)
    {
      eventcuts_->GetXaxis()->SetBinLabel(bincounter,"Skim");
      ++bincounter;
    }
  for (int i=0;i<orderedCutNames_.size();++i)
    {
      eventcuts_->GetXaxis()->SetBinLabel(bincounter,orderedCutNames_[i].c_str());
      ++bincounter;
    }

  bincounter=1;

  int nEntRoottuple = fChain->GetEntriesFast();
  int nEntTot = (skimWasMade_ ? NBeforeSkim_ : nEntRoottuple );
  string cutEfficFile = *cutEfficFile_ + ".dat";
  ofstream os(cutEfficFile.c_str());

  if ( jsonFileWasUsed_ ) {
    os << "################################## JSON file used at runtime    ###################################################################\n"
       << "### " << jsonFileName_ << "\n";
  } else { 
    os << "################################## NO JSON file used at runtime ###################################################################\n";
  }

  if ( pileupMCFileWasUsed_ && pileupDataFileWasUsed_ ){
    os << "################################## PILEUP files used at runtime    ###################################################################\n"
       << "### " << pileupMCFileName_ << "\n" 
       << "### " << pileupDataFileName_ << "\n";
  } else { 
    os << "################################## NO PILEUP files used at runtime ###################################################################\n";
  }

  os << "################################## Preliminary Cut Values ###################################################################\n"
     << "########################### variableName                        value1          value2          value3          value4          level\n"
     << preCutInfo_.str();

  int cutIdPed=0;
  double minForFixed = 0.1;
  int precision = 4;
  int mainFieldWidth=20;
  os.precision(precision);
  os << "################################## Cuts #########################################################################################################################################################################################################################\n"
     <<"#id                       variableName                min1                max1                min2                max2               level                   N               Npass              EffRel           errEffRel              EffAbs           errEffAbs"<<endl
     << fixed
     << setw(3) << cutIdPed
     << setw(35) << "nocut"
     << setprecision(4)
     << setw(mainFieldWidth) << "-" //min1
     << setw(mainFieldWidth) << "-" //max1
     << setw(mainFieldWidth) << "-" //min2
     << setw(mainFieldWidth) << "-" //max2
     << setw(mainFieldWidth) << "-" //level
     << setw(mainFieldWidth) << nEntTot //N
     << setw(mainFieldWidth) << nEntTot //Npass
    //     << setprecision(11)
     << setw(mainFieldWidth) << 1. //EffRell
     << setw(mainFieldWidth) << 0. //errEffRel
     << setw(mainFieldWidth) << 1. //EffAbs
     << setw(mainFieldWidth) << 0. //errEffAbs
     << endl;

  double effRel;
  double effRelErr;
  double effAbs;
  double effAbsErr;

  eventcuts_->SetBinContent(bincounter,nEntTot);
  if (optimizeName_cut_.size())
    h_optimizer_->SetBinContent(0, nEntTot);

  double nEvtPassedBeforeWeight_previousCut = nEntTot;
  double nEvtPassed_previousCut = nEntTot;

  if(skimWasMade_)
    {
      ++bincounter;
      eventcuts_->SetBinContent(bincounter, nEntRoottuple);
      effRel = (double) nEntRoottuple / (double) NBeforeSkim_;
      effRelErr = sqrt( (double) effRel * (1.0 - (double) effRel) / (double) NBeforeSkim_ );
      effAbs = effRel;
      effAbsErr = effRelErr;
      os << fixed
	 << setw(3) << ++cutIdPed
	 << setw(35) << "skim"
	 << setprecision(4)
	 << setw(mainFieldWidth) << "-"
	 << setw(mainFieldWidth) << "-"
	 << setw(mainFieldWidth) << "-"
	 << setw(mainFieldWidth) << "-"
	 << setw(mainFieldWidth) << "-"
	 << setw(mainFieldWidth) << NBeforeSkim_
	 << setw(mainFieldWidth) << nEntRoottuple
	 << setw(mainFieldWidth) << ( (effRel                 < minForFixed) ? (scientific) : (fixed) ) << effRel
	 << setw(mainFieldWidth) << ( (effRelErr              < minForFixed) ? (scientific) : (fixed) ) << effRelErr
	 << setw(mainFieldWidth) << ( (effAbs                 < minForFixed) ? (scientific) : (fixed) ) << effAbs
	 << setw(mainFieldWidth) << ( (effAbsErr              < minForFixed) ? (scientific) : (fixed) ) << effAbsErr
	 << fixed << endl;
      nEvtPassedBeforeWeight_previousCut = nEntRoottuple;
      nEvtPassed_previousCut = nEntRoottuple;
    }
  for (vector<string>::iterator it = orderedCutNames_.begin();
       it != orderedCutNames_.end(); it++)
    {
      cut * c = & (cutName_cut_.find(*it)->second);
      ++bincounter;
      eventcuts_->SetBinContent(bincounter, c->nEvtPassed);
      effRel = (double) c->nEvtPassed / nEvtPassed_previousCut;
      double N = nEvtPassedBeforeWeight_previousCut;
      double Np = c->nEvtPassedBeforeWeight;
      double p = Np / N;
      double q = 1-p;
      double w = c->nEvtPassed / c->nEvtPassedBeforeWeight;
      effRelErr = sqrt(p*q/N)*w;
      effAbs = (double) c->nEvtPassed / (double) nEntTot;
      N = nEntTot;
      p = Np / N;
      q = 1-p;
      effAbsErr = sqrt(p*q/N)*w;

      std::stringstream ssm1, ssM1, ssm2,ssM2;
      ssm1 << fixed << setprecision(4) << c->minValue1;
      ssM1 << fixed << setprecision(4) << c->maxValue1;
      if(c->minValue2 == -99999999999)
	{
	  ssm2 << "-inf";
	}
      else
	{
	  ssm2 << fixed << setprecision(4) << c->minValue2;
	}
      if(c->maxValue2 ==  99999999999)
	{
	  ssM2 << "+inf";
	}
      else
	{
	  ssM2 << fixed << setprecision(4) << c->maxValue2;
	}
      os << setw(3) << cutIdPed+c->id
	 << setw(35) << c->variableName
	 << setprecision(precision)
	 << fixed
	 << setw(mainFieldWidth) << ( ( c->minValue1 == -99999999999.0 ) ? "-inf" : ssm1.str() )
	 << setw(mainFieldWidth) << ( ( c->maxValue1 ==  99999999999.0 ) ? "+inf" : ssM1.str() )
	 << setw(mainFieldWidth) << ( ( c->minValue2 > c->maxValue2 ) ? "-" : ssm2.str() )
	 << setw(mainFieldWidth) << ( ( c->minValue2 > c->maxValue2 ) ? "-" : ssM2.str() )
	 << setw(mainFieldWidth) << c->level_int
	 << setw(mainFieldWidth) << ( (nEvtPassed_previousCut < minForFixed) ? (scientific) : (fixed) ) << nEvtPassed_previousCut
	 << setw(mainFieldWidth) << ( (c->nEvtPassed          < minForFixed) ? (scientific) : (fixed) ) << c->nEvtPassed
	 << setw(mainFieldWidth) << ( (effRel                 < minForFixed) ? (scientific) : (fixed) ) << effRel
	 << setw(mainFieldWidth) << ( (effRelErr              < minForFixed) ? (scientific) : (fixed) ) << effRelErr
	 << setw(mainFieldWidth) << ( (effAbs                 < minForFixed) ? (scientific) : (fixed) ) << effAbs
	 << setw(mainFieldWidth) << ( (effAbsErr              < minForFixed) ? (scientific) : (fixed) ) << effAbsErr
	 << fixed << endl;
      nEvtPassedBeforeWeight_previousCut = c->nEvtPassedBeforeWeight;
      nEvtPassed_previousCut = c->nEvtPassed;
    }

  // Write optimization histograms
  if (optimizeName_cut_.size())
    {
#ifdef CREATE_OPT_CUT_FILE
      //std::string optFileName = *outputFileName_+"_optimization.txt";
      std::string optFileName = "optimizationCuts.txt";
      std::ofstream optFile( optFileName.c_str() );
      if ( !optFile.good() )
	{
	  STDOUT("ERROR: cannot open file "<< optFileName.c_str() ) ;
	}

      // Add code for printing histogram output
      int Nbins=h_optimizer_->GetNbinsX();
      for (int i=0;i<Nbins;++i)
	{
	  std::vector<int> cutindex;
	  // cutindex will store histogram bin as a series of integers
	  // 12345 = {1,2,3,4,5}, etc.

	  optFile <<"Bin = "<<i;
	  for (int j=Nbins/nOptimizerCuts_;j>=1;j/=nOptimizerCuts_)
	    {
	      cutindex.push_back((i/j)%nOptimizerCuts_);
	    }  // for (int j=(int)log10(Nbins);...)

	  for (unsigned int j=0;j<cutindex.size();++j)
	    {
	      optFile <<"\t"<< optimizeName_cut_[j].variableName <<" ";
	      if (optimizeName_cut_[j].testgreater==true)
		optFile <<"> "<<optimizeName_cut_[j].minvalue+optimizeName_cut_[j].increment*cutindex[j];
	      //I'm not sure this is how I implemented the < cut; need to check.
	      else
		optFile <<"< "<<optimizeName_cut_[j].maxvalue-optimizeName_cut_[j].increment*cutindex[j];
	    } //for (unsigned int j=0;...)
	  optFile <<endl;
	  //optFile <<"\t Entries = "<<h_optimizer_->GetBinContent(i+1)<<endl;

	} // for (int i=0;...)
#endif // CREATE_OPT_CUT_FILE

      gDirectory->mkdir("Optimizer");
      gDirectory->cd("Optimizer");
      h_optimizer_->Write();
      for (int i=0;i<optimizeName_cut_.size();++i)
	{
	  stringstream x;
	  x<<"Cut"<<i<<"_"<<optimizeName_cut_[i].variableName;
	  if (optimizeName_cut_[i].testgreater==true)
	    x<<"_gt_";
	  else
	    x<<"_lt_";
	  x<<optimizeName_cut_[i].minvalue<<"_to_"<<optimizeName_cut_[i].maxvalue;
	  TObjString test(x.str().c_str());
	  test.Write();
	}
      gDirectory->cd("..");
    }

  eventcuts_->Write(); // write here, since WriteCutHistos is called before WriteCutEfficFile
  // Any failure mode to implement?
  return ret;
} // writeCutEffFile


bool baseClass::sortCuts(const cut& X, const cut& Y)
{
  return X.id < Y.id;
}


vector<string> baseClass::split(const string& s)
{
  vector<string> ret;
  string::size_type i =0;
  while (i != s.size()){
    while (i != s.size() && isspace(s[i]))
      ++i;
    string::size_type j = i;
    while (j != s.size() && !isspace(s[j]))
      ++j;
    if (i != j){
      ret.push_back(s.substr(i, j -i));
      i = j;
    }
  }
  return ret;
}

double baseClass::decodeCutValue(const string& s)
{
  //STDOUT("s = "<<s);
  double ret;
  if( s == "inf" || s == "+inf" )
    {
       ret = 99999999999;
    }
  else if ( s == "-inf" || s == "-" )
    {
       ret = -99999999999;
    }
  else
    {
       ret = atof( s.c_str() );
    }
  return ret;
}

int baseClass::getGlobalInfoNstart(const char *pName)
{
  int NBeforeSkim = 0;
  STDOUT(pName<<"  "<< NBeforeSkim)
  TFile *f = TFile::Open(pName);
  string s1 = "LJFilter/EventCount/EventCounter";
  string s2 = "LJFilterPAT/EventCount/EventCounter";
  TH1I* hCount1 = (TH1I*)f->Get(s1.c_str());
  TH1I* hCount2 = (TH1I*)f->Get(s2.c_str());
  if( !hCount1 && !hCount2 )
    {
      STDOUT("Skim filter histogram(s) not found. Will assume skim was not made for ALL files.");
      skimWasMade_ = false;
      return NBeforeSkim;
    }

  if (hCount1) NBeforeSkim = (int)hCount1->GetBinContent(1);
  else NBeforeSkim = (int)hCount2->GetBinContent(1);

//   STDOUT(pName<<"  "<< NBeforeSkim)
  f->Close();

  return NBeforeSkim;
}

void baseClass::CreateAndFillUserTH1D(const char* nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Double_t value, Double_t weight)
{
  map<std::string , TH1D*>::iterator nh_h = userTH1Ds_.find(std::string(nameAndTitle));
  TH1D * h;
  if( nh_h == userTH1Ds_.end() )
    {
      h = new TH1D(nameAndTitle, nameAndTitle, nbinsx, xlow, xup);
      h->Sumw2();
      userTH1Ds_[std::string(nameAndTitle)] = h;
      h->Fill(value);
    }
  else
    {
      nh_h->second->Fill(value, weight);
    }
}
void baseClass::CreateUserTH1D(const char* nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup)
{
  map<std::string , TH1D*>::iterator nh_h = userTH1Ds_.find(nameAndTitle);
  TH1D * h;
  if( nh_h == userTH1Ds_.end() )
    {
      h = new TH1D(nameAndTitle, nameAndTitle, nbinsx, xlow, xup);
      h->Sumw2();
      userTH1Ds_[std::string(nameAndTitle)] = h;
    }
  else
    {
      STDOUT("ERROR: trying to define already existing histogram "<<nameAndTitle);
    }
}
void baseClass::FillUserTH1D(const char* nameAndTitle, Double_t value, Double_t weight)
{
  map<std::string , TH1D*>::iterator nh_h = userTH1Ds_.find(std::string(nameAndTitle));
  TH1D * h;
  if( nh_h == userTH1Ds_.end() )
    {
      STDOUT("ERROR: trying to fill histogram "<<nameAndTitle<<" that was not defined.");
    }
  else
    {
      nh_h->second->Fill(value, weight);
    }
}

void baseClass::CreateAndFillUserTH2D(const char* nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup,  Double_t value_x,  Double_t value_y, Double_t weight)
{
  map<std::string , TH2D*>::iterator nh_h = userTH2Ds_.find(std::string(nameAndTitle));
  TH2D * h;
  if( nh_h == userTH2Ds_.end() )
    {
      h = new TH2D(nameAndTitle, nameAndTitle, nbinsx, xlow, xup, nbinsy, ylow, yup);
      h->Sumw2();
      userTH2Ds_[std::string(nameAndTitle)] = h;
      h->Fill(value_x, value_y, weight);
    }
  else
    {
      nh_h->second->Fill(value_x, value_y, weight);
    }
}

void baseClass::CreateUserTH2D(const char* nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup)
{
  map<std::string , TH2D*>::iterator nh_h = userTH2Ds_.find(std::string(nameAndTitle));
  TH2D * h;
  if( nh_h == userTH2Ds_.end() )
    {
      h = new TH2D(nameAndTitle, nameAndTitle, nbinsx, xlow, xup, nbinsy, ylow, yup);
      h->Sumw2();
      userTH2Ds_[std::string(nameAndTitle)] = h;
    }
  else
    {
      STDOUT("ERROR: trying to define already existing histogram "<<nameAndTitle);
    }
}


void baseClass::CreateUserTH2D(const char* nameAndTitle, Int_t nbinsx, Double_t * x, Int_t nbinsy, Double_t * y )
{
  map<std::string , TH2D*>::iterator nh_h = userTH2Ds_.find(std::string(nameAndTitle));
  TH2D * h;
  if( nh_h == userTH2Ds_.end() )
    {
      h = new TH2D(nameAndTitle, nameAndTitle, nbinsx, x, nbinsy, y );
      h->Sumw2();
      userTH2Ds_[std::string(nameAndTitle)] = h;
    }
  else
    {
      STDOUT("ERROR: trying to define already existing histogram "<<nameAndTitle);
    }
}

void baseClass::FillUserTH2D(const char* nameAndTitle, Double_t value_x,  Double_t value_y, Double_t weight)
{
  map<std::string , TH2D*>::iterator nh_h = userTH2Ds_.find(std::string(nameAndTitle));
  TH2D * h;
  if( nh_h == userTH2Ds_.end() )
    {
      STDOUT("ERROR: trying to fill histogram "<<nameAndTitle<<" that was not defined.");
    }
  else
    {
      nh_h->second->Fill(value_x, value_y, weight);
    }
}


void baseClass::FillUserTH2DLower(const char* nameAndTitle, Double_t value_x,  Double_t value_y, Double_t weight)
{
  map<std::string , TH2D*>::iterator nh_h = userTH2Ds_.find(std::string(nameAndTitle));
  // TH2D * h;
  if( nh_h == userTH2Ds_.end() )
    {
      STDOUT("ERROR: trying to fill histogram "<<nameAndTitle<<" that was not defined.");
    }
  else
    {
      TH2D * hist = nh_h->second;
      TAxis * x_axis   = hist -> GetXaxis();
      TAxis * y_axis   = hist -> GetYaxis();
      int     n_bins_x = hist -> GetNbinsX();
      int     n_bins_y = hist -> GetNbinsY();
      
      for ( int i_bin_x = 1; i_bin_x <= n_bins_x; ++i_bin_x ){
	
	double x_min  = x_axis -> GetBinLowEdge( i_bin_x );
	double x_max  = x_axis -> GetBinUpEdge ( i_bin_x );
	double x_mean = x_axis -> GetBinCenter ( i_bin_x );

	if ( value_x <= x_min ) continue;
	
	for ( int i_bin_y = 1; i_bin_y <= n_bins_y; ++i_bin_y ){
	  
	  double y_min  = y_axis -> GetBinLowEdge( i_bin_y );
	  double y_mean = y_axis -> GetBinCenter ( i_bin_y );
	  
	  if ( value_y <= y_min ) continue;
	  
	  hist -> Fill (x_mean,y_mean, weight);
	  
	}
      }
    }
}


bool baseClass::writeUserHistos()
{

  bool ret = true;
  output_root_->cd();

  for (map<std::string, TH1D*>::iterator uh_h = userTH1Ds_.begin(); uh_h != userTH1Ds_.end(); uh_h++)
    {
      output_root_->cd();
      uh_h->second->Write();
    }
  for (map<std::string, TH2D*>::iterator uh_h = userTH2Ds_.begin(); uh_h != userTH2Ds_.end(); uh_h++)
    {
      //      STDOUT("uh_h = "<< uh_h->first<<" "<< uh_h->second );
      output_root_->cd();
      uh_h->second->Write();
    }
  // Any failure mode to implement?
  return ret;
}

double baseClass::getSkimPreCutValue(const string& s)
{
  map<string, preCut>::iterator cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
    {
      return 0;
    }
  preCut * c = & (cc->second);
  if(c->value1 == -99999999999) STDOUT("ERROR: value1 of preliminary cut "<<s<<" was not provided.");
  return (c->value1);
}

void baseClass::fillSkimTree()
{
  if(!produceSkim_) return;

  skim_tree_->Fill();
  NAfterSkim_++;

  return;
}

void baseClass::fillReducedSkimTree()
{
  if(!produceReducedSkim_) return;

  reduced_skim_tree_->Fill();
  NAfterReducedSkim_++;

  return;
}

bool baseClass::writeSkimTree()
{
  bool ret = true;

  if(!produceSkim_) return ret;
  
  skim_file_->cd();
  TDirectory *dir1 = skim_file_->mkdir("LJFilter");
  TDirectory *dir2 = dir1->mkdir("EventCount");
  skim_file_->cd("LJFilter/EventCount");
  int nEntRoottuple = fChain->GetEntriesFast();
  int nEntTot = (skimWasMade_ ? NBeforeSkim_ : nEntRoottuple );
  hCount_->SetBinContent(1,nEntTot);
  hCount_->SetBinContent(2,NAfterSkim_);
  hCount_->Write();

  if ( fChain -> GetEntries() == 0 ){
    skim_file_->cd();
    skim_file_->mkdir("rootTupleTree");
    skim_file_->cd("rootTupleTree");
    fChain -> CloneTree(0) -> Write("tree");
  }
  
  else { 
    skim_file_->cd();
    skim_file_->mkdir("rootTupleTree");
    skim_file_->cd("rootTupleTree");
    skim_tree_ -> Write("tree");
  }

  // Any failure mode to implement?
  return ret;
}

bool baseClass::writeReducedSkimTree()
{
  bool ret = true;

  if(!produceReducedSkim_) return ret;

  reduced_skim_file_->cd();
  reduced_skim_file_->mkdir("rootTupleTree");
  reduced_skim_file_->cd("rootTupleTree");
  reduced_skim_tree_->Write();

  reduced_skim_file_->cd();
  TDirectory *dir1 = reduced_skim_file_->mkdir("LJFilter");
  TDirectory *dir2 = dir1->mkdir("EventCount");
  reduced_skim_file_->cd("LJFilter/EventCount");
  int nEntRoottuple = fChain->GetEntriesFast();
  int nEntTot = (skimWasMade_ ? NBeforeSkim_ : nEntRoottuple );
  hReducedCount_->SetBinContent(1,nEntTot);
  hReducedCount_->SetBinContent(2,NAfterReducedSkim_);
  hReducedCount_->Write();

  // Any failure mode to implement?
  return ret;
}

int baseClass::passJSON (int this_run, int this_lumi, bool this_is_data ) {
  
  if ( !this_is_data     ) return 1;
  if ( !jsonFileWasUsed_ ) {
    STDOUT( "ERROR: baseClass::passJSON invoked when running on data, but no JSON file was specified!" );
    exit(-1);
  }
  
  return jsonParser_.isAGoodLumi ( this_run, this_lumi );
  
}

double baseClass::getPileupWeight ( int npileup, bool this_is_data ) { 
  
  PileupWeight_ = 1.0;

  if ( this_is_data )                                     return PileupWeight_;
  if ( ! pileupReweighter_.pileupWeightsCalculated() )    return PileupWeight_;
  if ( npileup == -1 )                                    return PileupWeight_;

  PileupWeight_ = pileupReweighter_.getPileupWeight ( npileup ) ;
  
  return PileupWeight_;
}

void baseClass::getTriggers(std::string * HLTKey ,  
			    std::vector<std::string> * names, 
			    std::vector<bool>        * decisions,
			    std::vector<int>         * prescales ){
  triggerDecisionMap_.clear();
  triggerPrescaleMap_.clear();
    
  int ntriggers = names -> size();
  
  for (int i = 0; i < ntriggers; ++i){
    triggerDecisionMap_[ (*names)[i].c_str() ] = (*decisions)[i];
    triggerPrescaleMap_[ (*names)[i].c_str() ] = (*prescales)[i];
    //STDOUT("INFO: Filled trigger prescale map: name=" << (*names)[i] << " prescale=" << (*prescales)[i]);
  }
}

void baseClass::printTriggers(){
  std::map<std::string, int>::iterator i     = triggerPrescaleMap_.begin();
  std::map<std::string, int>::iterator i_end = triggerPrescaleMap_.end();
  STDOUT( "Triggers include: ")
    for (; i != i_end; ++i) STDOUT( "\t" << i -> second << "\t\"" << i -> first << "\"" );
}

void baseClass::printFiredTriggers()
{
  std::map<std::string, bool>::iterator i     = triggerDecisionMap_.begin();
  std::map<std::string, bool>::iterator i_end = triggerDecisionMap_.end();
  STDOUT( "Fired triggers: ");
  for (; i != i_end; ++i)
  {
    if(i->second)
      STDOUT("\t\"" << i -> first << "\"" );
  }
}

bool baseClass::triggerFired ( const char* name ) {
  std::map<std::string, bool>::iterator i = triggerDecisionMap_.find ( name ) ;
  if ( i == triggerDecisionMap_.end())
  {
    // try to look by prefix of given path name
    auto itr = triggerDecisionMap_.lower_bound( name );
    while(itr->first.find(name)==0) // check to make sure key actually starts with name
    {
      //STDOUT("Found matching trigger: " << itr->first << " with result: " << itr->second);
      return itr->second;
      ++itr;
    }
    printTriggers();
    STDOUT("ERROR: could not find trigger " << name << " in triggerDecisionMap_!");
    exit(-1);
  }
  else
  {
    //STDOUT("INFO: Found matching trigger: " << i->first << " with result: " << i->second);
    return i -> second;
  }
}

int baseClass::triggerPrescale ( const char* name ) { 
  std::map<std::string, int>::iterator i = triggerPrescaleMap_.find ( name ) ;
  if ( i == triggerPrescaleMap_.end() )
  {
    // try to look by prefix of given path name
    auto itr = triggerPrescaleMap_.lower_bound( name );
    while(itr->first.find(name)==0) // check to make sure key actually starts with name
    {
      //STDOUT("Found matching trigger: " << itr->first << " with prescale=" << itr->second);
      return itr->second;
      ++itr;
    }
    printTriggers();
    STDOUT("ERROR: could not find trigger " << name << " in triggerPrescaleMap_ after attempting to match by prefix!");
    exit(-1);
  }
  else {
    //STDOUT("INFO: Found matching trigger: " << i->first << " with prescale: " << i->second);
    return i->second;
  }
}

void baseClass::fillTriggerVariable ( const char * hlt_path, const char* variable_name ) { 
  int prescale = triggerPrescale(hlt_path);
  if ( triggerFired (hlt_path) ) {
    //STDOUT("INFO: triggerFired! fillVariableWithValue("<<variable_name<<","<<prescale<<") for hlt_path="<<hlt_path);
    fillVariableWithValue(variable_name, prescale      ) ; 
  }
  else {
    //STDOUT("INFO: fillVariableWithValue("<<variable_name<<","<<-1*prescale<<") for hlt_path="<<hlt_path);
    fillVariableWithValue(variable_name, prescale * -1 ) ;
  }
}

