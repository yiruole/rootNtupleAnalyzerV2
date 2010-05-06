#define baseClass_cxx
#include "baseClass.h"

baseClass::baseClass(string * inputList, string * cutFile, string * treeName, string * outputFileName, string * cutEfficFile)
{
  std::cout << "baseClass::baseClass(): begins " << std::endl;
  inputList_ = inputList;
  cutFile_ = cutFile;
  treeName_= treeName;
  outputFileName_ = outputFileName;
  cutEfficFile_ = cutEfficFile;
  init();
  std::cout << "baseClass::baseClass(): ends " << std::endl;
}

baseClass::~baseClass()
{
  std::cout << "baseClass::~baseClass(): begin " << std::endl;
  if( !writeCutHistos() )
    {
      STDOUT("ERROR: writeCutHistos did not complete successfully.");
    }
  if( !writeCutEfficFile() )
    {
      STDOUT("ERROR: writeStatFile did not complete successfully.");
    }
  output_root_->Close();
  std::cout << "baseClass::~baseClass(): end " << std::endl;
}

void baseClass::init()
{
  STDOUT("begin");
    //std::cout << "baseClass::init(): begin " << std::endl;

  tree_ = NULL;
  readInputList();
  readCutFile();
  if(tree_ == NULL){
    std::cout << "baseClass::init(): ERROR: tree_ = NULL " << std::endl;
    return;
  }
  Init(tree_);

  //char output_root_title[200];
  //sprintf(output_root_title,"%s%s",&std::string(*outputFileName_)[0],".root");
  //output_root_ = new TFile(&output_root_title[0],"RECREATE");

  //directly from string
  output_root_ = new TFile((*outputFileName_ + ".root").c_str(),"RECREATE");
  
  //  for (map<string, cut>::iterator it = cutName_cut_.begin(); 
  //   it != cutName_cut_.end(); it++) STDOUT("cutName_cut->first = "<<it->first)
  //  for (vector<string>::iterator it = orderedCutNames_.begin(); 
  //       it != orderedCutNames_.end(); it++) STDOUT("orderedCutNames_ = "<<*it)
  STDOUT("end");
}

void baseClass::readInputList()
{

  TChain *chain = new TChain(treeName_->c_str());
  char pName[500];
  skimWasMade_ = true;
  NBeforeSkim_ = 0;
  int NBeforeSkim;

  std::cout << "baseClass::readinputList(): inputList_ =  "<< *inputList_ << std::endl;

  ifstream is(inputList_->c_str());
  if(is.good())
    {
      cout << "baseClass::readInputList: Reading list: " << *inputList_ << " ......." << endl;
      while( is.getline(pName, 500, '\n') )
        {
          if (pName[0] == '#') continue;
	  //if (pName[0] == ' ') continue; // do we want to skip lines that start with a space?
	  if (pName[0] == '\n') continue;// simple protection against blank lines
          STDOUT("Adding file: " << pName);
          chain->Add(pName);
	  NBeforeSkim = getGlobalInfoNstart(pName);
	  NBeforeSkim_ = NBeforeSkim_ + NBeforeSkim;
	  STDOUT("Initial number of events: NBeforeSkim, NBeforeSkim_ = "<<NBeforeSkim<<", "<<NBeforeSkim_);
        }
      tree_ = chain;
      cout << "baseClass::readInputList: Finished reading list: " << *inputList_ << endl;
    }
  else
    {
      cout << "baseClass::readInputList: ERROR opening inputList:" << *inputList_ << endl;
      exit (1);
    }
  is.close();

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
	      Optimize opt(optimize_count,v[0],minval, maxval, greaterthan, level_int);
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
	      thisPreCut.value1  = decodeCutValue( v[1] );
	      thisPreCut.value2  = decodeCutValue( v[2] );
	      thisPreCut.value3  = decodeCutValue( v[3] );
	      thisPreCut.value4  = decodeCutValue( v[4] );
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
	  thisCut.passed = false;
	  thisCut.nEvtInput=0;
	  thisCut.nEvtPassed=0;

	  orderedCutNames_.push_back(thisCut.variableName);
	  cutName_cut_[thisCut.variableName]=thisCut;

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
      h_optimizer_=new TH1F("optimizer","Optimization of cut variables",(int)pow(10,optimizeName_cut_.size()),0,
			    pow(10,optimizeName_cut_.size()));
    }

  // Create a histogram that will show events passing cuts
  int cutsize=orderedCutNames_.size()+1;
  if (skimWasMade_) ++cutsize;
  gDirectory->cd();
  eventcuts_=new TH1F("EventsPassingCuts","Events Passing Cuts",cutsize,0,cutsize);

  is.close();

}

void baseClass::resetCuts()
{
  for (map<string, cut>::iterator cc = cutName_cut_.begin(); cc != cutName_cut_.end(); cc++) 
    {
      cut * c = & (cc->second);
      c->filled = false;
      c->value = 0;
      c->passed = false;
    }
  combCutName_passed_.clear();
  return;
}

void baseClass::fillVariableWithValue(const string& s, const double& d)
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
  for (int i=0;i<pow(10,thesize);++i) counterbins.push_back(true); // assume true
  
  // lowest-numbered cut appears first in cut ordering
  // That is, for cut:  ABCDEF
  //  A is the index of cut0, B is cut 1, etc.
  for (int cc=0;cc<thesize;++cc) // loop over all cuts, starting at cut 0
    {
      --mysize;
      for (int i=0;i<10;++i) // loop over 10 cuts for each
	{
	  if (!optimizeName_cut_[cc].Compare(i)) // cut failed; set all values associated with cut to false
	    {
	      // loop over  all cut values starting with current cut
	      for (unsigned int j=(int)(i*pow(10,mysize));j<int(pow(10,thesize));++j)
		{
		  // if relevant digit of the cut value matches the current (failed) cut, set this cut to false 
		  if ((j/int(pow(10,mysize)))%10==i)
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
	h_optimizer_->Fill(i,1);
      
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
  if(c->value1 == -9999999) STDOUT("ERROR: value1 of preliminary cut "<<s<<" was not provided.");
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
  if(c->value2 == -9999999) STDOUT("ERROR: value2 of preliminary cut "<<s<<" was not provided.");
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
  if(c->value3 == -9999999) STDOUT("ERROR: value3 of preliminary cut "<<s<<" was not provided.");
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
  if(c->value4 == -9999999) STDOUT("ERROR: value4 of preliminary cut "<<s<<" was not provided.");
  return (c->value4);
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
	  c->histo1.Fill( c->value );
	  if( passedAllPreviousCuts(c->variableName) )                c->histo2.Fill( c->value );
	  if( passedAllOtherSameAndLowerLevelCuts(c->variableName) )  c->histo3.Fill( c->value );
	  if( passedAllOtherCuts(c->variableName) )                   c->histo4.Fill( c->value );
	  if( passedCut("all") )                                      c->histo5.Fill( c->value );
	}
    }
  return ret;
}

bool baseClass::writeCutHistos()
{ 
  bool ret = true;
  for (vector<string>::iterator it = orderedCutNames_.begin(); 
       it != orderedCutNames_.end(); it++) 
    {
      cut * c = & (cutName_cut_.find(*it)->second);
      c->histo1.Write();
      c->histo2.Write();
      c->histo3.Write();
      c->histo4.Write();
      c->histo5.Write();
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
	  c->nEvtInput++;
	  if( passedCut(c->variableName) )              c->nEvtPassed++;
	}
    }
  return ret;
}


bool baseClass::writeCutEfficFile()
{

  bool ret = true;
  
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

  os << "################################## Preliminary Cut Values ###################################################################\n"
     << "########################### variableName                        value1          value2          value3          value4          level\n"
     << preCutInfo_.str();

  int cutIdPed=0;
  os.precision(4); 
  os << "################################## Cuts #####################################################################################\n" 
     <<"#id             variableName           min1           max1           min2           max2          level              N          Npass         EffRel      errEffRel         EffAbs      errEffAbs"<<endl
     << fixed
     << setw(3) << cutIdPed 
     << setw(25) << "nocut" 
     << setprecision(4) 
     << setw(15) << "-"
     << setw(15) << "-"
     << setw(15) << "-"
     << setw(15) << "-"
     << setw(15) << "-"
     << setw(15) << nEntTot
     << setw(15) << nEntTot
     << setprecision(11) 
     << setw(15) << "1.00000000000"
     << setw(15) << "0.00000000000"
     << setw(15) << "1.00000000000"
     << setw(15) << "0.00000000000"
     << endl;

  double effRel;
  double effRelErr;
  double effAbs;
  double effAbsErr;

  eventcuts_->SetBinContent(bincounter,nEntTot);
  if (optimizeName_cut_.size())
    h_optimizer_->SetBinContent(0, nEntTot);

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
	 << setw(25) << "skim" 
	 << setprecision(4) 
	 << setw(15) << "-"
	 << setw(15) << "-"
	 << setw(15) << "-"
	 << setw(15) << "-"
	 << setw(15) << "-"
	 << setw(15) << NBeforeSkim_
	 << setw(15) << nEntRoottuple
	 << setprecision(11) 
	 << setw(15) << effRel
	 << setw(15) << effRelErr
	 << setw(15) << effAbs
	 << setw(15) << effAbsErr
	 << endl;
    }
  for (vector<string>::iterator it = orderedCutNames_.begin(); 
       it != orderedCutNames_.end(); it++) 
    {
      cut * c = & (cutName_cut_.find(*it)->second);
      ++bincounter;
      eventcuts_->SetBinContent(bincounter, c->nEvtPassed);
      effRel = (double) c->nEvtPassed / (double) c->nEvtInput;
      effRelErr = sqrt( (double) effRel * (1.0 - (double) effRel) / (double) c->nEvtInput );
      effAbs = (double) c->nEvtPassed / (double) nEntTot;
      effAbsErr = sqrt( (double) effAbs * (1.0 - (double) effAbs) / (double) nEntTot );

      std::stringstream ssm1, ssM1, ssm2,ssM2;
      ssm1 << fixed << setprecision(4) << c->minValue1;
      ssM1 << fixed << setprecision(4) << c->maxValue1;
      if(c->minValue2 == -9999999) 
	{
	  ssm2 << "-inf";
	}
      else
	{
	  ssm2 << fixed << setprecision(4) << c->minValue2;
	}
      if(c->maxValue2 ==  9999999) 
	{
	  ssM2 << "+inf";
	}
      else
	{
	  ssM2 << fixed << setprecision(4) << c->maxValue2;
	}
      os << setw(3) << cutIdPed+c->id 
	 << setw(25) << c->variableName 
	 << setprecision(4)
	 << fixed 
	 << setw(15) << ( ( c->minValue1 == -9999999.0 ) ? "-inf" : ssm1.str() )
	 << setw(15) << ( ( c->maxValue1 ==  9999999.0 ) ? "+inf" : ssM1.str() )
	 << setw(15) << ( ( c->minValue2 > c->maxValue2 ) ? "-" : ssm2.str() )
	 << setw(15) << ( ( c->minValue2 > c->maxValue2 ) ? "-" : ssM2.str() )
	 << setw(15) << c->level_int
	 << setw(15) << c->nEvtInput
	 << setw(15) << c->nEvtPassed
	 << setprecision(11) 
	 << setw(15) << effRel
	 << setw(15) << effRelErr
	 << setw(15) << effAbs
	 << setw(15) << effAbsErr
	 << endl;
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
	  for (int j=Nbins/10;j>=1;j/=10)
	    {
	      cutindex.push_back((i/j)%10);
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
       ret = 9999999;
    }
  else if ( s == "-inf" || s == "-" )
    {
       ret = -9999999;
    }
  else
    {
       ret = atof( s.c_str() );
    }
  return ret;
}

int baseClass::getGlobalInfoNstart(char *pName)
{
  int NBeforeSkim = 0;
  STDOUT(pName<<"  "<< NBeforeSkim)
  TFile *f = new TFile(pName);
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
