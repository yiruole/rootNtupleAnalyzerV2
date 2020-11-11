#define baseClass_cxx
#include "baseClass.h"
#include <boost/lexical_cast.hpp>
#include "TEnv.h"
#include "TLeaf.h"

static_assert(std::numeric_limits<float>::is_iec559, "IEEE 754 required");

template void baseClass::fillArrayVariableWithValue(const string& s, TTreeReaderArray<Float_t>& reader);

baseClass::baseClass(string * inputList, string * cutFile, string * treeName, string * outputFileName, string * cutEfficFile):
  fillSkim_                         ( true ) ,
  fillAllPreviousCuts_              ( true ) ,
  fillAllOtherCuts_                 ( true ) ,
  fillAllSameLevelAndLowerLevelCuts_( true ) ,
  fillAllCuts_                      ( true ) ,
  oldKey_                           ( "" ) 
{
  STDOUT("begins");
  nOptimizerCuts_ = 20; // number of cut points used in optimizer scan over a variable
  inputList_ = inputList;
  cutFile_ = cutFile;
  treeName_= treeName;
  if(outputFileName != NULL)
  {
    outputFileName_ = *outputFileName;
  }
  else
  {
    STDOUT("baseClass::init(): ERROR: outputFileName_ == NULL ");
    exit(-1);
  }
  cutEfficFile_ = cutEfficFile;
  init();
  STDOUT("ends");
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
  output_root_->cd();
  checkOverflow(h_weightSums_,sumAMCNLOWeights_);
  h_weightSums_->SetBinContent(1,sumAMCNLOWeights_);
  checkOverflow(h_weightSums_,sumTopPtWeights_);
  h_weightSums_->SetBinContent(2,sumTopPtWeights_);
  h_weightSums_->Write();
  for(auto& hist : histsToSave_)
    hist->Write();
  output_root_->Close();
  if(produceSkim_)
  {
    skim_file_->cd("savedHists");
    h_weightSums_->Write();
    skim_file_->Close();
  }
  if(produceReducedSkim_)
  {
    reduced_skim_file_->cd("savedHists");
    h_weightSums_->Write();
    reduced_skim_file_->Close();
  }
}

void baseClass::init()
{
  // set up prefetching
  //gEnv->SetValue("TFile.AsyncPrefetching", 1);
  tree_ = NULL;
  readInputList();
  Long64_t ret = tree_->LoadTree(0);
  if(ret < 0) {
    STDOUT("baseClass::init(): Had an error of code " << ret << " when calling LoadTree(); exit");
    exit(1);
  }
  readCutFile();
  if(tree_ == NULL){
    STDOUT("baseClass::init(): ERROR: tree_ = NULL ");
    exit(1);
  }
  readerTools_ = std::shared_ptr<TTreeReaderTools>(new TTreeReaderTools(tree_));


  //directly from string
  std::string filename = outputFileName_;
  filename+=+".root";
  output_root_ = new TFile(filename.c_str(),"RECREATE", "", 207);

  // Skim stuff
  produceSkim_ = false;
  NAfterSkim_ = 0;
  if(int(getSkimPreCutValue("produceSkim"))==1) produceSkim_ = true;
  
  if(produceSkim_) {
    
    skim_file_ = new TFile((outputFileName_ + "_skim.root").c_str(),"RECREATE", "", 207);
    skim_tree_ = tree_->CloneTree(0);
    hCount_ = new TH1F("EventCounter","Event Counter",4,-0.5,3.5);
    hCount_->GetXaxis()->SetBinLabel(1,"all events");
    hCount_->GetXaxis()->SetBinLabel(2,"passed");
    hCount_->GetXaxis()->SetBinLabel(3,"sum of amc@NLO weights");
    hCount_->GetXaxis()->SetBinLabel(4,"sum of TopPt weights");
  }

  // Reduced Skim stuff
  produceReducedSkim_ = false;
  NAfterReducedSkim_ = 0;
  if(int(getSkimPreCutValue("produceReducedSkim"))==1) produceReducedSkim_ = true;

  if(produceReducedSkim_) {

    reduced_skim_file_ = new TFile((outputFileName_ + "_reduced_skim.root").c_str(),"RECREATE", "", 207);
    reduced_skim_tree_= new TTree("tree","Reduced Skim");
    hReducedCount_ = new TH1F("EventCounter","Event Counter",4,-0.5,3.5);
    hReducedCount_->GetXaxis()->SetBinLabel(1,"all events");
    hReducedCount_->GetXaxis()->SetBinLabel(2,"passed");
    hReducedCount_->GetXaxis()->SetBinLabel(3,"sum of amc@NLO weights");
    hReducedCount_->GetXaxis()->SetBinLabel(4,"sum of TopPt weights");
    for (map<string, cut>::iterator cc = cutName_cut_.begin(); cc != cutName_cut_.end(); cc++)
    {
      cut * c = & (cc->second);
      if(c->saveVariableInReducedSkim) {
        if (reduced_skim_tree_->FindBranch(c->variableName.c_str()) != nullptr) {
          STDOUT("ERROR: found branch named: '" << c->variableName << "' already specified in cutfile and saved. Please remove it from the cut file. (This could be a size branch for an array variable: if so, it will be saved automatically.) Exiting here.");
          exit(-5);
        }
        reduced_skim_tree_->Branch(c->variableName.c_str(),&c->value,(c->variableName+"/F").c_str());
      }
      else if(c->saveVariableArrayInReducedSkim) {
        std::stringstream branchFormat;
        branchFormat << c->variableName;
        std::string arraySizeVar = "n" + c->variableName;
        if (reduced_skim_tree_->FindBranch(arraySizeVar.c_str()) != nullptr) {
          STDOUT("ERROR: found branch named: '" << arraySizeVar << "' specified in cutfile and saved. This is a size branch for an array variable, so it will be saved automatically and shouldn't be saved manually. Exiting here.");
          exit(-5);
        }
        reduced_skim_tree_->Branch(arraySizeVar.c_str(),&c->arraySize,(arraySizeVar+"/i").c_str());
          branchFormat << "[" << arraySizeVar << "]";
          reduced_skim_tree_->Branch(c->variableName.c_str(),(void*)nullptr,(branchFormat.str()+"/F").c_str());
      }
    }
  }

  //  for (map<string, cut>::iterator it = cutName_cut_.begin();
  //   it != cutName_cut_.end(); it++) STDOUT("cutName_cut->first = "f<<it->first)
  //  for (vector<string>::iterator it = orderedCutNames_.begin();
  //       it != orderedCutNames_.end(); it++) STDOUT("orderedCutNames_ = "<<*it)
  //STDOUT("ends");

  // setup sum of weights hist
  gDirectory->cd();
  h_weightSums_ = new TH1F("SumOfWeights","Sum of weights over all events",2,-0.5,1.5);
  h_weightSums_->GetXaxis()->SetBinLabel(1,"amc@NLOweightSum");
  h_weightSums_->GetXaxis()->SetBinLabel(2,"topPtWeightSum");

}

void baseClass::readInputList()
{

  std::shared_ptr<TChain> chain = std::shared_ptr<TChain>(new TChain(treeName_->c_str()));
  char pName[500];
  skimWasMade_ = true;
  jsonFileWasUsed_ = false;
  NBeforeSkim_ = 0;
  int NBeforeSkim;
  sumAMCNLOWeights_ = 0;
  sumTopPtWeights_ = 0;
  float tmpSumAMCNLOWeights = 0;
  float tmpSumTopPtWeights = 0;

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
      //STDOUT("Adding file: " << name);
      chain->Add(name.c_str());
      NBeforeSkim = getGlobalInfoNstart(name);
      NBeforeSkim_ = NBeforeSkim_ + NBeforeSkim;
      STDOUT("Initial number of events (current file,runningTotal): NBeforeSkim, NBeforeSkim_ = "<<NBeforeSkim<<", "<<NBeforeSkim_);
      tmpSumAMCNLOWeights = getSumAMCNLOWeights(name);
      sumAMCNLOWeights_ += tmpSumAMCNLOWeights;
      STDOUT("amc@NLO weight sum (current,total): = "<<tmpSumAMCNLOWeights<<", "<<sumAMCNLOWeights_);
      tmpSumTopPtWeights = getSumTopPtWeights(name);
      sumTopPtWeights_ += tmpSumTopPtWeights;
      //STDOUT("TopPt weight sum (current,total): = "<<tmpSumTopPtWeights<<", "<<sumTopPtWeights_);
      saveLHEPdfSumw(name);
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
  treeEntries_ = tree_->GetEntries();

}

bool is_number(const std::string& s) {
  try {
    float number = boost::lexical_cast<float>(s);
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
      if (s[0] == '#' || s.empty()) continue;
      vector<string> v = split(s);
      if ( v.size() == 0 ) continue;

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
        //jsonParser_.printGoodLumis();
        jsonFileWasUsed_ = true;
        continue;
      }

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
        float minval=atof(v[3].c_str());
        float maxval=atof(v[4].c_str());
        Optimize opt(optimize_count,v[0],minval, maxval, greaterthan, level_int, nOptimizerCuts_ );
        optimizeName_cut_[optimize_count]=opt; // order cuts by cut #, rather than name, so that optimization histogram is consistently ordered
        ++optimize_count;
        continue;
      }

      map<string, cut>::iterator cc = cutName_cut_.find(v[0]);
      if( cc != cutName_cut_.end() )
      {
        STDOUT("ERROR: variableName = "<< v[0] << " exists already in cutName_cut_. Returning.");
        exit(-1);
        //return;
      }

      if(v.size() < 6)
      {
        STDOUT("ERROR: This line [" << s << "] is too short! Quitting.");
        exit(-1);
      }
      int level_int = atoi( v[5].c_str() );
      if(level_int == -1)
      {
        map<string, preCut>::iterator cc = preCutName_cut_.find(v[0]);
        if( cc != preCutName_cut_.end() )
        {
          STDOUT("ERROR: variableName = "<< v[0] << " exists already in preCutName_cut_. Returning.");
          exit(-1);
          //return;
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
        exit(-2);
        //return; // FIXME implement exception
      }
      if( (m2=="-" && M2!="-") || (m2!="-" && M2=="-") )
      {
        STDOUT("ERROR: if any of minValue2 and maxValue2 is -, then both have to be -. Returning");
        exit(-2);
        //return; // FIXME implement exception
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
      thisCut.saveVariableArrayInReducedSkim = ( v.size()>9 && v[9]=="SAVEARRAY" ) ? true : false;

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
    STDOUT( "baseClass::readCutFile: Finished reading cutFile: " << *cutFile_ );
  }
  else
  {
    STDOUT("ERROR opening cutFile:" << *cutFile_ );
    exit (-3);
  }
  // make optimizer histogram
  if (optimizeName_cut_.size()>0)
    {
      h_optimizer_=new TH1F("optimizer","Optimization of cut variables",(int)pow(nOptimizerCuts_,optimizeName_cut_.size()),0,
			    pow(nOptimizerCuts_,optimizeName_cut_.size()));
      h_optimizer_entries_ =new TH1I("optimizerEntries","Optimization of cut variables (entries)",(int)pow(nOptimizerCuts_,optimizeName_cut_.size()),0,
			    pow(nOptimizerCuts_,optimizeName_cut_.size()));
    }

  is.close();

  // Create a histogram that will show events passing cuts
  int cutsize=orderedCutNames_.size()+1;
  if (skimWasMade_) ++cutsize;
  gDirectory->cd();
  eventcuts_=new TH1F("EventsPassingCuts","Events Passing Cuts",cutsize,0,cutsize);


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

void baseClass::fillVariableWithValue(const string& s, const float& d, const float& w)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: variableName = "<< s << " not found in cutName_cut_. Exiting.");
      exit(-5);
    }
  else
    {
      cut * c = & (cc->second);
      c->filled = true;
      c->value = d;
      c->weight = w;
    }
  fillOptimizerWithValue(s, d);
  return;
}

void baseClass::fillVariableWithValue(const string& s, TTreeReaderValue<float>& reader, const float& w)
{
  fillVariableWithValue(s, *reader, w);
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

template <typename T> void baseClass::fillArrayVariableWithValue(const string& s, TTreeReaderArray<T>& reader)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: variableName = "<< s << " not found in cutName_cut_. Exiting.");
      exit(-5);
    }
  else
    {
      cut * c = & (cc->second);
      c->filled = true;
      c->value = 0.;
      c->weight = 1.;
      if(reader.GetSize() > cut::MAX_ARRAY_SIZE)
      {
        STDOUT("WARNING: truncated array size from" << reader.GetSize() << " to MAX_ARRAY_SIZE=" << cut::MAX_ARRAY_SIZE << " in this event.");
        c->arraySize = cut::MAX_ARRAY_SIZE;
      }
      else
        c->arraySize = reader.GetSize();
      reduced_skim_tree_->FindBranch(s.c_str())->SetAddress(const_cast<void*>(reader.GetAddress()));
    }
  return;
}

float baseClass::getVariableValue(const string& s)
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

void baseClass::fillOptimizerWithValue(const string& s, const float& d)
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

void baseClass::evaluateCuts(bool verbose)
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
      if(verbose) std::cout << "FAILED cut: " << c->variableName << "; value is: " << c->value << std::endl;
    }
    else
    {
      c->passed = true;
      map<string,bool>::iterator cp = combCutName_passed_.find( c->level_str.c_str() );
      combCutName_passed_[c->level_str.c_str()] = (cp==combCutName_passed_.end()?true:cp->second);
      map<string,bool>::iterator ap = combCutName_passed_.find( "all" );
      combCutName_passed_["all"] = (ap==combCutName_passed_.end()?true:ap->second);
      if(verbose) std::cout << "PASSED cut: " << c->variableName << "; value is: " << c->value << std::endl;
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
    if (passedCut(*it) == false) {
      //std::cout << "SIC DEBUG: examining cut: " << *it << "; passed? " << passedCut(*it) << "; don't run optimizer" << std::endl;
      return;
    }
  }

  /*
  if (combCutName_passed_["all"] == false)
    return;
  */

  // loop over up to 6 cuts
  int counter=0;
  int thesize=optimizeName_cut_.size();
  int mysize=thesize;
  std::vector<bool> counterbins(pow(nOptimizerCuts_,thesize),true);

  // lowest-numbered cut appears first in cut ordering
  // That is, for cut:  ABCDEF
  //  A is the index of cut0, B is cut 1, etc.
  for (int cc=0;cc<thesize;++cc) // loop over all cuts, starting at cut 0
  {
    --mysize;
    for (int i=0;i<nOptimizerCuts_;++i) // loop over cuts for each
    {
      if (!optimizeName_cut_[cc].Compare(i)) // cut failed; set all values associated with cut to false
      {
        int power = pow(nOptimizerCuts_,mysize);
        int power1 = pow(nOptimizerCuts_,mysize+1);
        for(int x=0; x<pow(nOptimizerCuts_,thesize-1);++x)
        {
          int idx = (x/power)*power1+(x%power)+i*power;
          counterbins[idx]=false;
        }
      } // if (cut comparison failed)
    } // for (int i=0;i<10;++i)
  }
  // now fill histograms
  for (int i=0;i<counterbins.size();++i)
  {
    if (counterbins[i]==true)
    {
      //if(i==0)
      //  std::cout << "\tSIC DEBUG FIll opt hist bin " << i+1 << " with " << cutName_cut_[orderedCutNames_.at(orderedCutNames_.size()-1)].weight <<std::endl;
      h_optimizer_->Fill(i,cutName_cut_[orderedCutNames_.at(orderedCutNames_.size()-1)].weight); // take the event weight from the last cut in the cut file
      h_optimizer_entries_->Fill(i);
    }

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

bool baseClass::hasCut(const string& s)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc != cutName_cut_.end() )
    return true;
  // check the comb map for completeness
  map<string, bool>::iterator cp = combCutName_passed_.find(s);
  if( cp != combCutName_passed_.end() )
    return true;
  return false;
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
      if( ! (c->filled && c->passed) )
        return false;
    }
  }
  STDOUT("ERROR. It should never pass from here.");
  return false;
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

float baseClass::getPreCutValue1(const string& s)
{
  float ret;
  map<string, preCut>::iterator cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Bailing.");
    exit(-5);
  }
  preCut * c = & (cc->second);
  if(c->value1 == -99999999999) STDOUT("ERROR: value1 of preliminary cut "<<s<<" was not provided.");
  return (c->value1);
}

float baseClass::getPreCutValue2(const string& s)
{
  float ret;
  map<string, preCut>::iterator cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Bailing.");
    exit(-5);
  }
  preCut * c = & (cc->second);
  if(c->value2 == -99999999999) STDOUT("ERROR: value2 of preliminary cut "<<s<<" was not provided.");
  return (c->value2);
}

float baseClass::getPreCutValue3(const string& s)
{
  float ret;
  map<string, preCut>::iterator cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Bailing.");
    exit(-5);
  }
  preCut * c = & (cc->second);
  if(c->value3 == -99999999999) STDOUT("ERROR: value3 of preliminary cut "<<s<<" was not provided.");
  return (c->value3);
}

float baseClass::getPreCutValue4(const string& s)
{
  float ret;
  map<string, preCut>::iterator cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Bailing.");
    exit(-5);
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
    STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Bailing.");
    exit(-5);
  }
  preCut * c = & (cc->second);
  return (c->string1);
}


float baseClass::getCutMinValue1(const string& s)
{
  float ret;
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning");
  }
  cut * c = & (cc->second);
  return (c->minValue1);
}

float baseClass::getCutMaxValue1(const string& s)
{
  float ret;
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning");
  }
  cut * c = & (cc->second);
  return (c->maxValue1);
}

float baseClass::getCutMinValue2(const string& s)
{
  float ret;
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning");
  }
  cut * c = & (cc->second);
  return (c->minValue2);
}

float baseClass::getCutMaxValue2(const string& s)
{
  float ret;
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

float baseClass::getHistoMin(const string& s)
{
  map<string, cut>::iterator cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }
  cut * c = & (cutName_cut_.find(s)->second);
  return (c->histoMin);
}

float baseClass::getHistoMax(const string& s)
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

  Long64_t nEntTot = (skimWasMade_ ? NBeforeSkim_ : GetTreeEntries() );
  string cutEfficFile = *cutEfficFile_ + ".dat";
  ofstream os(cutEfficFile.c_str());

  if ( jsonFileWasUsed_ ) {
    os << "################################## JSON file used at runtime    ###################################################################\n"
       << "### " << jsonFileName_ << "\n";
  } else { 
    os << "################################## NO JSON file used at runtime ###################################################################\n";
  }

  os << "################################## Preliminary Cut Values ###################################################################\n"
     << "########################### variableName                        value1          value2          value3          value4          level\n"
     << preCutInfo_.str();

  int cutIdPed=0;
  float minForFixed = 0.1;
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

  float effRel;
  float effRelErr;
  float effAbs;
  float effAbsErr;

  checkOverflow(eventcuts_,nEntTot);
  eventcuts_->SetBinContent(bincounter,nEntTot);
  if (optimizeName_cut_.size())
  {
    checkOverflow(h_optimizer_,nEntTot);
    h_optimizer_->SetBinContent(0, nEntTot);
    checkOverflow(h_optimizer_entries_,nEntTot);
    h_optimizer_entries_->SetBinContent(0, nEntTot);
  }

  float nEvtPassedBeforeWeight_previousCut = nEntTot;
  float nEvtPassed_previousCut = nEntTot;

  if(skimWasMade_)
    {
      ++bincounter;
      checkOverflow(eventcuts_,GetTreeEntries());
      eventcuts_->SetBinContent(bincounter, GetTreeEntries() );
      effRel = (float) GetTreeEntries() / (float) NBeforeSkim_;
      effRelErr = sqrt( (float) effRel * (1.0 - (float) effRel) / (float) NBeforeSkim_ );
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
	 << setw(mainFieldWidth) << GetTreeEntries()
	 << setw(mainFieldWidth) << ( (effRel                 < minForFixed) ? (scientific) : (fixed) ) << effRel
	 << setw(mainFieldWidth) << ( (effRelErr              < minForFixed) ? (scientific) : (fixed) ) << effRelErr
	 << setw(mainFieldWidth) << ( (effAbs                 < minForFixed) ? (scientific) : (fixed) ) << effAbs
	 << setw(mainFieldWidth) << ( (effAbsErr              < minForFixed) ? (scientific) : (fixed) ) << effAbsErr
	 << fixed << endl;
      nEvtPassedBeforeWeight_previousCut = GetTreeEntries();
      nEvtPassed_previousCut = GetTreeEntries();
    }
  for (vector<string>::iterator it = orderedCutNames_.begin();
       it != orderedCutNames_.end(); it++)
    {
      cut * c = & (cutName_cut_.find(*it)->second);
      ++bincounter;
      checkOverflow(eventcuts_,c->nEvtPassed);
      eventcuts_->SetBinContent(bincounter, c->nEvtPassed);
      effRel = (float) c->nEvtPassed / nEvtPassed_previousCut;
      float N = nEvtPassedBeforeWeight_previousCut;
      float Np = c->nEvtPassedBeforeWeight;
      float p = Np / N;
      float q = 1-p;
      float w = c->nEvtPassed / c->nEvtPassedBeforeWeight;
      effRelErr = sqrt(p*q/N)*w;
      effAbs = (float) c->nEvtPassed / (float) nEntTot;
      N = nEntTot;
      p = Np / N;
      q = 1-p;
      effAbsErr = sqrt(p*q/N)*w;

      std::stringstream ssm1, ssM1, ssm2,ssM2;
      ssm1 << fixed << setprecision(4) << c->minValue1;
      ssM1 << fixed << setprecision(4) << c->maxValue1;
      if(c->minValue2 == std::numeric_limits<float>::lowest())
	{
	  ssm2 << "-inf";
	}
      else
	{
	  ssm2 << fixed << setprecision(4) << c->minValue2;
	}
      if(c->maxValue2 == std::numeric_limits<float>::max())
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
	 << setw(mainFieldWidth) << ( ( c->minValue1 == std::numeric_limits<float>::lowest() ) ? "-inf" : ssm1.str() )
	 << setw(mainFieldWidth) << ( ( c->maxValue1 == std::numeric_limits<float>::max() ) ? "+inf" : ssM1.str() )
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
      // now, you call this function explicitly, as in the makeOptCutFile main cc
//#ifdef CREATE_OPT_CUT_FILE
//      STDOUT("write opt cut file");
//      createOptCutFile();
//#endif // CREATE_OPT_CUT_FILE


      gDirectory->mkdir("Optimizer");
      gDirectory->cd("Optimizer");
      h_optimizer_->Write();
      h_optimizer_entries_->Write();
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

float baseClass::decodeCutValue(const string& s)
{
  //STDOUT("s = "<<s);
  float ret;
  if( s == "inf" || s == "+inf" )
    {
       ret = std::numeric_limits<float>::max();
    }
  else if ( s == "-inf" || s == "-" )
    {
       ret = std::numeric_limits<float>::lowest();
    }
  else
    {
       ret = atof( s.c_str() );
    }
  return ret;
}

double baseClass::getInfoFromHist(const std::string& fileName, const std::string& histName, int bin)
{
  double NBeforeSkim = 0;

  auto f = std::unique_ptr<TFile>(TFile::Open(fileName.c_str()));
  if(!f)
  {
    STDOUT("File pointer for "<< fileName << " came back null. Quitting");
    exit(-1);
  }
  if(!f->IsOpen())
  {
    STDOUT("File didn't open! Quitting");
    exit(-1);
  }

  if(histName=="EventCounter")
  {
    string s1 = "LJFilter/EventCount/EventCounter";
    string s2 = "savedHists/EventCounter";
    string s3 = "EventCounter";
    auto hCount1 = f->Get<TH1F>(s1.c_str());
    auto hCount2 = f->Get<TH1F>(s2.c_str());
    auto hCount3 = f->Get<TH1F>(s3.c_str());
    if(!hCount1 && !hCount2 && !hCount3)
    {
      STDOUT("Skim filter histogram(s) not found. Will assume skim was not made for ALL files.");
      skimWasMade_ = false;
      return NBeforeSkim;
    }
    if (hCount1) NBeforeSkim = hCount1->GetBinContent(bin);
    else if (hCount2) NBeforeSkim = hCount2->GetBinContent(bin);
    else NBeforeSkim = hCount3->GetBinContent(bin);
  }
  else
  {
    auto hCount = f->Get<TH1F>(histName.c_str());
    if(!hCount)
    {
      STDOUT("ERROR: Did not find specified hist named: '" << histName << "'. Cannot extract info. Quitting");
      exit(-1);
    }
    NBeforeSkim = hCount->GetBinContent(bin);
  }

  return NBeforeSkim;
}

double baseClass::getGlobalInfoNstart(const std::string& fileName)
{
  STDOUT(fileName);
  return getInfoFromHist(fileName, "EventCounter", 1);
}

double baseClass::getSumAMCNLOWeights(const std::string& fileName)
{
  return getInfoFromHist(fileName, "EventCounter", 3);
}

double baseClass::getSumTopPtWeights(const std::string& fileName)
{
  return getInfoFromHist(fileName, "EventCounter", 4);
}

double baseClass::getSumWeightFromRunsTree(const std::string& fName, const std::string& weightName, int index)
{
  if(index < 0)
    return getSumArrayFromRunsTree(fName, weightName, false)[0];
  else
    return getSumArrayFromRunsTree(fName, weightName, true)[index];
}

std::vector<double> baseClass::getSumArrayFromRunsTree(const std::string& fName, const std::string& weightName, bool isArrayBranch)
{
  std::vector<double> sumWeightArray(1);

  auto chain = std::shared_ptr<TChain>(new TChain("Runs"));
  int retVal = chain->AddFile(fName.c_str(), -1);
  if(!retVal)
  {
    STDOUT("ERROR: Something went wrong. Could not find TTree 'Runs' in the inputfile '" << fName << "'. Quit here.");
    exit(-2);
  }

  auto readerTools = std::unique_ptr<TTreeReaderTools>(new TTreeReaderTools(chain));
  if(readerTools->GetTree()->GetBranch(weightName.c_str())) // data may not have the branch we want
  {
    for(Long64_t entry = 0; entry < chain->GetEntries(); ++entry)
    {
      readerTools->LoadEntry(entry);
      if(isArrayBranch)
      {
        unsigned int arraySize = readerTools->ReadArrayBranch<Double_t>(weightName).GetSize();
        if(arraySize > 0 && arraySize != sumWeightArray.size())
        {
          if(entry == 0)
            sumWeightArray.resize(arraySize);
          else
          {
            STDOUT("ERROR: array '" << weightName << "' changed size between runs. The indices of the array are inconsistent. Refusing to proceed.");
            exit(-2);
          }
        }
        for(unsigned int index = 0; index < arraySize; ++index) {
          double toAdd = readerTools->ReadArrayBranch<Double_t>(weightName, index);
          if(weightName == "LHEPdfSumw")
            toAdd*=readerTools->ReadValueBranch<Double_t>("genEventSumw");
          sumWeightArray[index]+=toAdd;
        }
      }
      else
        sumWeightArray[0]+=readerTools->ReadValueBranch<Double_t>(weightName);
    }
  }

  return sumWeightArray;
}

void baseClass::saveLHEPdfSumw(const std::string& fileName)
{
  STDOUT("saveLHEPdfSumw");
  std::vector<double> lhePdfSumwArr;
  auto f = std::unique_ptr<TFile>(TFile::Open(fileName.c_str()));
  if(!f)
  {
    STDOUT("File pointer for "<< fileName << " came back null. Quitting");
    exit(-1);
  }
  if(!f->IsOpen())
  {
    STDOUT("File didn't open! Quitting");
    exit(-1);
  }
  // we have to have the histogram or the Runs tree available
  auto histFromFile = f->Get<TH1D>("savedHists/LHEPdfSumw");
  if(histFromFile)
  {
    lhePdfSumwArr.resize(histFromFile->GetNbinsX());
    for(unsigned int bin = 1; bin < histFromFile->GetNbinsX(); ++bin)
      lhePdfSumwArr[bin-1] = histFromFile->GetBinContent(bin);
  }
  else
    lhePdfSumwArr = getSumArrayFromRunsTree(fileName, "LHEPdfSumw", true);

  std::shared_ptr<TH1D> lhePdfSumwHist = nullptr;
  for(auto& hist : histsToSave_)
  {
    if(std::string(hist->GetName()) == "LHEPdfSumw")
      lhePdfSumwHist = dynamic_pointer_cast<TH1D>(hist);
  }
  if(!lhePdfSumwHist)
  {
    gDirectory->cd();
    histsToSave_.push_back(std::shared_ptr<TH1D>(new TH1D("LHEPdfSumw", "LHEPdfSumw", lhePdfSumwArr.size(), 0, lhePdfSumwArr.size())));
    lhePdfSumwHist = dynamic_pointer_cast<TH1D>(histsToSave_.back());
    lhePdfSumwHist->SetDirectory(0); // very important
  }
  for(unsigned int index = 0; index < lhePdfSumwArr.size(); ++index) {
    double totalToFill = lhePdfSumwArr[index]+lhePdfSumwHist->GetBinContent(index+1);
    checkOverflow(lhePdfSumwHist.get(), totalToFill);
    lhePdfSumwHist->SetBinContent(index+1, totalToFill);
  }
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
void baseClass::FillUserTH1D(const char* nameAndTitle, TTreeReaderValue<double>& reader, Double_t weight)
{
  FillUserTH1D(nameAndTitle, *reader, weight);
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
void baseClass::FillUserTH2D(const char* nameAndTitle, TTreeReaderValue<double>& xReader, TTreeReaderValue<double>& yReader, Double_t weight)
{
  FillUserTH2D(nameAndTitle, *xReader, *yReader, weight);
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
	
	float x_min  = x_axis -> GetBinLowEdge( i_bin_x );
	float x_max  = x_axis -> GetBinUpEdge ( i_bin_x );
	float x_mean = x_axis -> GetBinCenter ( i_bin_x );

	if ( value_x <= x_min ) continue;
	
	for ( int i_bin_y = 1; i_bin_y <= n_bins_y; ++i_bin_y ){
	  
	  float y_min  = y_axis -> GetBinLowEdge( i_bin_y );
	  float y_mean = y_axis -> GetBinCenter ( i_bin_y );
	  
	  if ( value_y <= y_min ) continue;
	  
	  hist -> Fill (x_mean,y_mean, weight);
	  
	}
      }
    }
}


void baseClass::CreateAndFillUserTH3D(const char* nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup, Int_t nbinsz, Double_t zlow, Double_t zup,  Double_t value_x,  Double_t value_y, Double_t z, Double_t weight)
{
  map<std::string , TH3D*>::iterator nh_h = userTH3Ds_.find(std::string(nameAndTitle));
  TH3D * h;
  if( nh_h == userTH3Ds_.end() )
    {
      h = new TH3D(nameAndTitle, nameAndTitle, nbinsx, xlow, xup, nbinsy, ylow, yup, nbinsz, zlow, zup);
      h->Sumw2();
      userTH3Ds_[std::string(nameAndTitle)] = h;
      h->Fill(value_x, value_y, weight);
    }
  else
    {
      nh_h->second->Fill(value_x, value_y, weight);
    }
}

void baseClass::CreateUserTH3D(const char* nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup, Int_t nbinsz, Double_t zlow, Double_t zup)
{
  map<std::string , TH3D*>::iterator nh_h = userTH3Ds_.find(std::string(nameAndTitle));
  TH3D * h;
  if( nh_h == userTH3Ds_.end() )
    {
      h = new TH3D(nameAndTitle, nameAndTitle, nbinsx, xlow, xup, nbinsy, ylow, yup, nbinsz, zlow, zup);
      h->Sumw2();
      userTH3Ds_[std::string(nameAndTitle)] = h;
    }
  else
    {
      STDOUT("ERROR: trying to define already existing histogram "<<nameAndTitle);
    }
}


void baseClass::CreateUserTH3D(const char* nameAndTitle, Int_t nbinsx, Double_t * x, Int_t nbinsy, Double_t * y, Int_t nbinsz, Double_t * z)
{
  map<std::string , TH3D*>::iterator nh_h = userTH3Ds_.find(std::string(nameAndTitle));
  TH3D * h;
  if( nh_h == userTH3Ds_.end() )
    {
      h = new TH3D(nameAndTitle, nameAndTitle, nbinsx, x, nbinsy, y, nbinsz, z );
      h->Sumw2();
      userTH3Ds_[std::string(nameAndTitle)] = h;
    }
  else
    {
      STDOUT("ERROR: trying to define already existing histogram "<<nameAndTitle);
    }
}

void baseClass::FillUserTH3D(const char* nameAndTitle, Double_t value_x,  Double_t value_y, Double_t value_z, Double_t weight)
{
  map<std::string , TH3D*>::iterator nh_h = userTH3Ds_.find(std::string(nameAndTitle));
  TH3D * h;
  if( nh_h == userTH3Ds_.end() )
    {
      STDOUT("ERROR: trying to fill histogram "<<nameAndTitle<<" that was not defined.");
    }
  else
    {
      nh_h->second->Fill(value_x, value_y, value_z, weight);
    }
}
void baseClass::FillUserTH3D(const char* nameAndTitle, TTreeReaderValue<double>& xReader, TTreeReaderValue<double>& yReader, TTreeReaderValue<double>& zReader, Double_t weight)
{
  FillUserTH3D(nameAndTitle, *xReader, *yReader, *zReader, weight);
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
  for (map<std::string, TH3D*>::iterator uh_h = userTH3Ds_.begin(); uh_h != userTH3Ds_.end(); uh_h++)
    {
      output_root_->cd();
      uh_h->second->Write();
    }
  // Any failure mode to implement?
  return ret;
}

float baseClass::getSkimPreCutValue(const string& s)
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

  tree_->GetEntry(readerTools_->GetCurrentEntry());
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
  TDirectory *dir1 = skim_file_->mkdir("savedHists");
  skim_file_->cd("savedHists");
  Long64_t nEntTot = (skimWasMade_ ? NBeforeSkim_ : GetTreeEntries() );
  //FIXME topPtWeight
  checkOverflow(hCount_,nEntTot);
  checkOverflow(hCount_,NAfterSkim_);
  checkOverflow(hCount_,sumAMCNLOWeights_);
  checkOverflow(hCount_,sumTopPtWeights_);
  hCount_->SetBinContent(1,nEntTot);
  hCount_->SetBinContent(2,NAfterSkim_);
  hCount_->SetBinContent(3,sumAMCNLOWeights_);
  hCount_->SetBinContent(4,sumTopPtWeights_);
  hCount_->Write();
  for(auto& hist : histsToSave_)
    hist->Write();

  if ( GetTreeEntries() == 0 ){
    skim_file_->cd();
    skim_file_->mkdir("rootTupleTree");
    skim_file_->cd("rootTupleTree");
    tree_ -> CloneTree(0) -> Write("tree");
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
  TDirectory *dir1 = reduced_skim_file_->mkdir("savedHists");
  reduced_skim_file_->cd("savedHists");
  Long64_t nEntTot = (skimWasMade_ ? NBeforeSkim_ : GetTreeEntries() );
  //FIXME topPtWeight
  checkOverflow(hReducedCount_,nEntTot);
  checkOverflow(hReducedCount_,NAfterReducedSkim_);
  checkOverflow(hReducedCount_,sumAMCNLOWeights_);
  checkOverflow(hReducedCount_,sumTopPtWeights_);
  hReducedCount_->SetBinContent(1,nEntTot);
  hReducedCount_->SetBinContent(2,NAfterReducedSkim_);
  hReducedCount_->SetBinContent(3,sumAMCNLOWeights_);
  hReducedCount_->SetBinContent(4,sumTopPtWeights_);
  hReducedCount_->Write();
  for(auto& hist : histsToSave_)
    hist->Write();

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

void baseClass::getTriggers(Long64_t entry) {
  triggerDecisionMap_.clear();
  //FIXME deal with prescale map
  //triggerPrescaleMap_.clear();
  for(unsigned int i=0; i<tree_->GetListOfBranches()->GetEntries(); ++i) {
    TBranch* branch = static_cast<TBranch*>(tree_->GetListOfBranches()->At(i));
    std::string branchName = branch->GetName();
    if(branchName.find("HLT_")!=std::string::npos) {
      triggerDecisionMap_[branchName] = readerTools_->ReadValueBranch<Bool_t>(branchName.c_str());
    }
  }
}

void baseClass::printTriggers(){
  std::map<std::string, bool>::iterator i     = triggerDecisionMap_.begin();
  std::map<std::string, bool>::iterator i_end = triggerDecisionMap_.end();
  STDOUT( "Triggers: ")
    for (; i != i_end; ++i)
      std::cout << "\tfired? " << i -> second <<"\t\"" << i -> first << "\"" << std::endl;
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

bool baseClass::triggerExists ( const char* name ) {
  std::map<std::string, bool>::iterator i = triggerDecisionMap_.find ( name ) ;
  if ( i == triggerDecisionMap_.end())
  {
    // try to look by prefix of given path name
    auto itr = triggerDecisionMap_.lower_bound( name );
    while(itr!=triggerDecisionMap_.end() && itr->first.find(name)==0) // check to make sure key actually starts with name
    {
      //STDOUT("Found matching trigger: " << itr->first << " with result: " << itr->second);
      return true;
      ++itr;
    }
    return false;
  }
  else
  {
    return true;
  }
}

bool baseClass::triggerFired ( const char* name ) {
  std::map<std::string, bool>::iterator i = triggerDecisionMap_.find ( name ) ;
  if ( i == triggerDecisionMap_.end())
  {
    // try to look by prefix of given path name
    auto itr = triggerDecisionMap_.lower_bound( name );
    while(itr!=triggerDecisionMap_.end() && itr->first.find(name)==0) // check to make sure key actually starts with name
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
    while(itr!=triggerPrescaleMap_.end() && itr->first.find(name)==0) // check to make sure key actually starts with name
    {
      //STDOUT("Found matching trigger: " << itr->first << " with prescale=" << itr->second);
      return itr->second;
      ++itr;
    }
    //printTriggers();
    //STDOUT("ERROR: could not find trigger " << name << " in triggerPrescaleMap_ after attempting to match by prefix!");
    //exit(-1);
    //FIXME
    return 1;
  }
  else {
    //STDOUT("INFO: Found matching trigger: " << i->first << " with prescale: " << i->second);
    return i->second;
  }
}

void baseClass::fillTriggerVariable ( const char * hlt_path, const char* variable_name, int extraPrescale ) { 
  int prescale = triggerPrescale(hlt_path);
  prescale*=extraPrescale;
  if ( triggerFired (hlt_path) ) {
    //STDOUT("INFO: triggerFired! fillVariableWithValue("<<variable_name<<","<<prescale<<") for hlt_path="<<hlt_path);
    fillVariableWithValue(variable_name, prescale      ) ; 
  }
  else {
    //STDOUT("INFO: fillVariableWithValue("<<variable_name<<","<<-1*prescale<<") for hlt_path="<<hlt_path);
    fillVariableWithValue(variable_name, prescale * -1 ) ;
  }
}

void baseClass::createOptCutFile() {
  STDOUT("creating optimization cut file");
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
}

bool baseClass::isData() {
  // if tree has isData branch, we know the answer
  if(tree_->GetBranch("isData")) {
    if(readerTools_->ReadValueBranch<Float_t>("isData") < 1)
      return false;
    else
      return true;
  }
  // if no isData branch (like in nanoAOD output), check for Weight or genWeight branches
  else if(tree_->GetBranch("Weight") || tree_->GetBranch("genWeight"))
    return false;
  return true;
}

template <typename T> void baseClass::checkOverflow(const TH1* hist, const T binContent) {
  std::ostringstream stringStream;
  if(std::string(hist->ClassName()).find("TH1F") != std::string::npos) {
    float limit = std::numeric_limits<float>::max();
    if(binContent>limit) {
      stringStream << "ERROR: binContent=" << binContent << " will overflow this TH1F bin in histo: " << hist->GetName() << "! Quitting.";
      STDOUT(stringStream.str());
      exit(-3);
    }
  }
  else if(std::string(hist->ClassName()).find("TH1I") != std::string::npos) {
    float limit = std::numeric_limits<int>::max();
    if(binContent>limit) {
      stringStream << "ERROR: binContent=" << binContent << " will overflow this TH1I bin in histo: " << hist->GetName() << "! Quitting.";
      STDOUT(stringStream.str());
      exit(-3);
    }
  }
  else if(std::string(hist->ClassName()).find("TH1D") != std::string::npos) {
    double limit = std::numeric_limits<double>::max();
    if(binContent>limit) {
      stringStream << "ERROR: binContent=" << binContent << " will overflow this TH1D bin in histo: " << hist->GetName() << "! Quitting.";
      STDOUT(stringStream.str());
      exit(-3);
    }
  }
  else {
    stringStream << "WARNING: Could not check bin content of hist:" << hist->GetName()
      << " for overflow as it is not a TH1F, TH1I, or TH1D. Please implement this check.";
    STDOUT(stringStream.str());
  }
}
