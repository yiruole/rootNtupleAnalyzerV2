#define baseClass_cxx
#include "baseClass.h"

#include <boost/lexical_cast.hpp>

#include <boost/regex.hpp>

#include "TEnv.h"
#include "TLeaf.h"
#include "TMap.h"
#include "TObjString.h"
#include "TGraphAsymmErrors.h"

using namespace std;

static_assert(std::numeric_limits<float>::is_iec559, "IEEE 754 required");

template void baseClass::fillArrayVariableWithValue(const string& s, TTreeReaderArray<Float_t>& reader);

baseClass::baseClass(string * inputList, string * cutFile, string * treeName, string * outputFileName, string * cutEfficFile):
  fillAllPreviousCuts_              ( !true ) ,
  fillAllOtherCuts_                 ( !true ) ,
  fillAllSameLevelAndLowerLevelCuts_( !true ) ,
  fillAllCuts_                      ( !true ) ,
  fillAllSameLevelCuts_             ( !true ) ,
  oldKey_                           ( "" ) 
{
  STDOUT("begins");
  //nOptimizerCuts_ = 20; // number of cut points used in optimizer scan over a variable
  nOptimizerCuts_ = 10000; // number of cut points used in optimizer scan over a variable
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
  checkOverflow(h_weightSums_,sumGenWeights_);
  h_weightSums_->SetBinContent(1,sumGenWeights_);
  h_weightSums_->SetBinError(1,sqrt(sumGenWeightSqrs_));
  checkOverflow(h_weightSums_,sumTopPtWeights_);
  h_weightSums_->SetBinContent(2,sumTopPtWeights_);
  h_weightSums_->Write();
  for(auto& hist : histsToSave_) {
    hist->Write();
    // make hist of ratio proj/nominal
    if(std::string(hist->GetName())=="systematics") {
      unique_ptr<TH2D> systDiffs(new TH2D("systematicsDiffs", "systematicsDiffs", hist->GetNbinsX(), 0, hist->GetXaxis()->GetXmax(), hist->GetNbinsY(), 0, hist->GetYaxis()->GetXmax()));
      hist->GetXaxis()->Copy(*systDiffs->GetXaxis());
      hist->GetYaxis()->Copy(*systDiffs->GetYaxis());
      systDiffs->Sumw2();
      systDiffs->SetDirectory(0);
      auto hist2D = dynamic_pointer_cast<TH2D>(hist);
      unique_ptr<TH1D> nominal(hist2D->ProjectionX("nominal", 1, 1, "e"));
      nominal->LabelsDeflate();
      nominal->SetDirectory(0);
      //cout << "nominal x bins: " << nominal->GetNbinsX() << endl;
      for(auto yBin = 1; yBin <= hist->GetNbinsY(); ++yBin) {
        unique_ptr<TH1D> proj(hist2D->ProjectionX("proj", yBin, yBin, "e"));
        proj->LabelsDeflate(); // otherwise we get 2x number of bins
        proj->SetDirectory(0);
        //cout << "proj x bins: " << proj->GetNbinsX() << endl;
        unique_ptr<TGraphAsymmErrors> quotient(new TGraphAsymmErrors());
        // suppress warning messages for divide; this can happen for zero content bins, for example
        int prevLevel = gErrorIgnoreLevel;
        gErrorIgnoreLevel = kError;
        quotient->Divide(proj.get(), nominal.get(), "pois cp");
        gErrorIgnoreLevel = prevLevel;
        for(auto iPoint = 0; iPoint < quotient->GetN(); ++iPoint) {
          double x = quotient->GetPointX(iPoint);
          double y = quotient->GetPointY(iPoint);
          double err = quotient->GetErrorY(iPoint);
          int binNum = systDiffs->FindBin(x, yBin-0.5);
          systDiffs->SetBinContent(binNum, y);
          systDiffs->SetBinError(binNum, err);
        }
      }
      systDiffs->Write();
      // here we make the TMap of systematicName-->branchNames
      unique_ptr<TMap> systNameToBranchTitlesMap(new TMap());
      systNameToBranchTitlesMap->SetName("systematicNameToBranchesMap");
      systNameToBranchTitlesMap->SetOwner(true); // clean up for us, please
      for(auto const& syst : systematics_) {
        TObjString* systName = new TObjString(syst.name.c_str());
        TList* branchTitleList = new TList();
        branchTitleList->SetOwner(true);
        if(syst.formula) {
          int nBranches = syst.formula->GetNcodes();
          for(int iBranch = 0; iBranch < nBranches; ++iBranch) {
            TObjString* branchTitle = new TObjString(syst.formula->GetLeaf(iBranch)->GetBranch()->GetTitle());
            branchTitleList->Add(branchTitle);
          }
        }
        else {
          // regex cases
          for(auto const& pair : syst.cutNamesToBranchNames) {
            if(pair.second.empty())
              continue; // here is a case where there is no branch in the tree and we manually fill the systVar in the analysis class code, so skip this
            branchTitleList->Add(new TObjString(pair.second.c_str()));
          }
        }
        systNameToBranchTitlesMap->Add(systName, branchTitleList);
      }
      systNameToBranchTitlesMap->Write(systNameToBranchTitlesMap->GetName(), TObject::kSingleKey);
    }
  }
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

std::vector<std::string> split(const std::string &s, char delim) {
  std::stringstream ss(s);
  std::string item;
  std::vector<std::string> elems;
  while (std::getline(ss, item, delim))
    elems.push_back(std::move(item));
  return elems;
}

void baseClass::updateBranchList() {
  if(!hasPreCut("BranchSelection"))
    return;
  string branchSelFile = getPreCutString1("BranchSelection");
  std::ifstream f(branchSelFile);
  std::string line;
  if (f.is_open()) {
    while (f.good()) {
      getline (f,line);
      if(line.empty() || line[0] == '#')
        continue;
      vector<string> splitLine = ::split(line, ' ');
      if(splitLine.size() != 2) {
        std::cout << "ERROR: Branch selection line '" << line << "' in file " << branchSelFile << " does not have the proper format: " 
          << " Should be (keep|keepmatch|drop|dropmatch) <branch_pattern>" << std::endl;
        exit(-2);
      }
      string op = splitLine[0];
      string branch = splitLine[1];
      if(op == "keep")
        skim_tree_->SetBranchStatus(branch.c_str(), 1);
      else if(op == "drop")
        skim_tree_->SetBranchStatus(branch.c_str(), 0);
      else if(op == "keepmatch" || op == "dropmatch") {
        //boost::regex regExp("(:?"+branch+")$");
        boost::regex regExp(branch);
        for(unsigned int i=0; i<tree_->GetListOfBranches()->GetEntries(); ++i) {
          TBranch* branch = static_cast<TBranch*>(tree_->GetListOfBranches()->At(i));
          string branchName = branch->GetName();
          if(boost::regex_search(branchName, regExp)) {
            if(op == "keepmatch")
              skim_tree_->SetBranchStatus(branchName.c_str(), 1);
            else
              skim_tree_->SetBranchStatus(branchName.c_str(), 0);
          }
        }
      }
      else {
        std::cout << "ERROR: Branch selection line '" << line << "' in file " << branchSelFile << " does not have the proper format: " 
          << " Should be (keep|keepmatch|drop|dropmatch) <branch_pattern>" << std::endl;
        exit(-2);
      }

    }
    f.close();
  }
  else { 
    std::cout << "ERROR: Branch selection file " << branchSelFile << " does not exist." << std::endl;
    exit(-1);
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
  if(tree_ == NULL){
    STDOUT("baseClass::init(): ERROR: tree_ = NULL ");
    exit(1);
  }
  readerTools_ = std::shared_ptr<TTreeReaderTools>(new TTreeReaderTools(tree_));
  readCutFile();
  if(haveSystematics()) {
    for(auto& syst: systematics_) {
      if(syst.formula)
        systFormulas_.Add(syst.formula.get());
    }
    tree_->SetNotify(&systFormulas_); // updates formulas in collection when needed
    // see: https://root-forum.cern.ch/t/ttreeformula-and-tchain/15155/
    // and: https://github.com/root-project/root/commit/5a918e25f8c5df4e51ad837e66d8fd23133dec38
  }


  //directly from string
  std::string filename = outputFileName_;
  filename+=+".root";
  output_root_ = new TFile(filename.c_str(),"RECREATE", "", 207);

  // Skim stuff
  if(produceSkim_) {
    
    skim_file_ = new TFile((outputFileName_ + "_skim.root").c_str(),"RECREATE", "", 207);
    skim_file_->cd();
    skim_file_->mkdir("rootTupleTree");
    skim_file_->cd("rootTupleTree");
    skim_tree_ = tree_->CloneTree(0);
    updateBranchList();
    hCount_ = new TH1D("EventCounter","Event Counter",4,-0.5,3.5);
    hCount_->GetXaxis()->SetBinLabel(1,"all events");
    hCount_->GetXaxis()->SetBinLabel(2,"passed");
    hCount_->GetXaxis()->SetBinLabel(3,"sum of amc@NLO weights");
    hCount_->GetXaxis()->SetBinLabel(4,"sum of TopPt weights");
  }

  // Reduced Skim stuff
  if(produceReducedSkim_) {

    reduced_skim_file_ = new TFile((outputFileName_ + "_reduced_skim.root").c_str(),"RECREATE", "", 207);
    reduced_skim_file_->cd();
    reduced_skim_file_->mkdir("rootTupleTree");
    reduced_skim_file_->cd("rootTupleTree");
    reduced_skim_tree_= new TTree("tree","Reduced Skim");
    hReducedCount_ = new TH1D("EventCounter","Event Counter",4,-0.5,3.5);
    hReducedCount_->GetXaxis()->SetBinLabel(1,"all events");
    hReducedCount_->GetXaxis()->SetBinLabel(2,"passed");
    hReducedCount_->GetXaxis()->SetBinLabel(3,"sum of amc@NLO weights");
    hReducedCount_->GetXaxis()->SetBinLabel(4,"sum of TopPt weights");
    for (auto& cutName : orderedCutNames_) {
      auto c = cutName_cut_.find(cutName)->second;
      //cut * c = & (cc->second);
      if(c->saveVariableInReducedSkim) {
        if (reduced_skim_tree_->FindBranch(c->variableName.c_str()) != nullptr) {
          STDOUT("ERROR: found branch named: '" << c->variableName << "' already specified in cutfile and saved. Please remove it from the cut file. (This could be a size branch for an array variable: if so, it will be saved automatically.) Exiting here.");
          exit(-5);
        }
        reduced_skim_tree_->Branch(c->variableName.c_str(),&c->value,(c->variableName+"/"+c->branchType).c_str());
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
        TBranch* branch = reduced_skim_tree_->Branch(c->variableName.c_str(),(void*)nullptr,(branchFormat.str()+"/"+c->branchType).c_str());
        branch->SetTitle("");
      }
    }
  }

  // setup sum of weights hist
  gDirectory->cd();
  h_weightSums_ = new TH1D("SumOfWeights","Sum of weights over all events",2,-0.5,1.5);
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
  sumGenWeights_ = 0;
  sumGenWeightSqrs_ = 0;
  sumTopPtWeights_ = 0;
  double tmpSumGenWeights = 0;
  double tmpSumGenWeightSqrs = 0;
  double tmpSumTopPtWeights = 0;

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
      tmpSumGenWeights = getSumGenWeights(name);
      sumGenWeights_ += tmpSumGenWeights;
      tmpSumGenWeightSqrs += getSumGenWeightSqrs(name);
      sumGenWeightSqrs_ += tmpSumGenWeightSqrs;
      STDOUT("gen weight sum (current,total): = "<<tmpSumGenWeights<<"+/-"<<sqrt(tmpSumGenWeightSqrs)<<", "<<sumGenWeights_<<"+/-"<<sqrt(sumGenWeightSqrs_));
      tmpSumTopPtWeights = getSumTopPtWeights(name);
      sumTopPtWeights_ += tmpSumTopPtWeights;
      //STDOUT("TopPt weight sum (current,total): = "<<tmpSumTopPtWeights<<", "<<sumTopPtWeights_);
      saveLHEPdfSumw(name);
      saveEventsPassingCuts(name);
    }
    tree_ = chain;
    STDOUT("baseClass::readInputList: Finished reading list: " << *inputList_ );
  }
  else
    throw runtime_error("baseClass::readInputList: ERROR opening inputList: " + *inputList_ );
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

  vector<string> systLines;
  ifstream is(cutFile_->c_str());
  if(is.good())
  {
    int id=0;
    int optimize_count=0;
    while( getline(is,s) )
    {
      if (s[0] == '#' || s.empty()) continue;
      vector<string> v = split(s);
      if ( v.size() == 0 ) continue;

      if ( v[0] == "SYST" ) {
        if ( v.size() < 2 || v.size() > 4 ){
          STDOUT("ERROR: In your cutfile, SYST line must have the syntax: \"SYST name [[regex=]/branchName/formula/value] [cutVariable(s)]\"");
          exit(-6);
        }
        else {
          systLines.push_back(s);
          continue;
        }
      }
      else if ( v[0] == "JSON" ) {
        if ( jsonFileWasUsed_ ) {
          STDOUT("ERROR: Please specify only one JSON file in your cut file!");
          return;
        }
        if ( v.size() != 2 ) {
          STDOUT("ERROR: In your cutfile, JSON file line must have the syntax: \"JSON <full json file path>\"");
        }
        jsonFileName_ = v[1];
        STDOUT("Getting JSON file: " << v[1]);
        jsonParser_.parseJSONFile ( & v[1] ) ;
        //jsonParser_.printGoodLumis();
        jsonFileWasUsed_ = true;
        continue;
      }
      else if (v[1]=="OPT") // add code for grabbing optimizer objects
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

      auto&& cc = cutName_cut_.find(v[0]);
      if( cc != cutName_cut_.end() )
      {
        STDOUT("ERROR: variableName = "<< v[0] << " exists already in cutName_cut_. Returning.");
        exit(-1);
      }

      if(v.size() < 6)
      {
        STDOUT("ERROR: This line [" << s << "] is too short! Quitting.");
        exit(-1);
      }
      int level_int = atoi( v[5].c_str() );
      if(level_int == -1)
      {
        const auto&  cc = preCutName_cut_.find(v[0]);
        if( cc != preCutName_cut_.end() )
        {
          STDOUT("ERROR: variableName = "<< v[0] << " exists already in preCutName_cut_. Returning.");
          exit(-1);
        }
        preCutInfo_ << "### Preliminary cut values: " << s <<endl;
        unique_ptr<preCut> thisPreCut = make_unique<preCut>();
        thisPreCut->variableName =     v[0];
        if ( is_number ( v[1] ) ) thisPreCut->value1  = decodeCutValue( v[1] );
        else                      thisPreCut->string1 = v[1];
        if ( is_number ( v[2] ) ) thisPreCut->value2  = decodeCutValue( v[2] );
        else                      thisPreCut->string2 = v[2];
        if ( is_number ( v[3] ) ) thisPreCut->value1  = decodeCutValue( v[3] );
        else                      thisPreCut->string3 = v[3];
        if ( is_number ( v[4] ) ) thisPreCut->value2  = decodeCutValue( v[4] );
        else                      thisPreCut->string4 = v[4];
        preCutName_cut_[thisPreCut->variableName] = move(thisPreCut);
        continue;
      }
      std::string variableName = v[0];
      string m1=v[1];
      string M1=v[2];
      string m2=v[3];
      string M2=v[4];
      if( m1=="-" || M1=="-" )
      {
        STDOUT("ERROR: minValue1 and maxValue2 have to be provided. Returning.");
        exit(-2);
      }
      if( (m2=="-" && M2!="-") || (m2!="-" && M2=="-") )
      {
        std::cout << "ERROR reading line '" << s << "'" << endl;
        STDOUT("ERROR: if any of minValue2 and maxValue2 is -, then both have to be -. Returning");
        exit(-2);
      }
      if( m2=="-") m2="+inf";
      if( M2=="-") M2="-inf";
      shared_ptr<cut> thisCut = make_shared<cut>();
      bool isTMVACut = false;
      map<string, float> staticParametersMap;
      if(v.size() > 9) { // check for optional flags
        string flag(v[9]);
        string flagOrig(flag);
        transform(flag.begin(), flag.end(), flag.begin(),
            [](unsigned char c){ return tolower(c); });
        thisCut->saveVariableArrayInReducedSkim = (flag.find("savearray") != string::npos );
        if(!thisCut->saveVariableArrayInReducedSkim)
          thisCut->saveVariableInReducedSkim = (flag.find("save") != string::npos );
        if(thisCut->saveVariableArrayInReducedSkim || thisCut->saveVariableInReducedSkim) {
          thisCut->branchType = 'F';
          // see if branch type was explicitly specified
          if(flagOrig.find("/") != string::npos) {
            std::string type = flagOrig.substr(flagOrig.find("/")+1, 1);
            thisCut->branchType = type[0];
          }
          if(thisCut->branchType == 'F') {
            thisCut->value = float(0.0);
          }
          else if(thisCut->branchType == 'I')
            thisCut->value = int(0);
          else if(thisCut->branchType == 'l')
            thisCut->value = static_cast<unsigned long long int>(0);
          else if(thisCut->branchType == 'i')
            thisCut->value = static_cast<unsigned int>(0);
          else if(thisCut->branchType == 'b')
            thisCut->value = static_cast<unsigned char>(0);
          else if(thisCut->branchType == 'O')
            thisCut->value = static_cast<bool>(false);
          else {
            STDOUT("ERROR: BranchType '" << thisCut->branchType << "' for saved variable named '" << variableName << "' is not one of F,I,l,i,b,O. Must add support for additional branch types.");
            exit(-2);
          }
          //std::string varTypeName = std::visit( [](auto&&x)->decltype(auto){ return typeid(x).name(); }, thisCut->value );
          //STDOUT("INFO: saving variable " << variableName << " using branchType=" << thisCut->branchType << "; its value _now_ has type " << varTypeName);
        }
        // TMVA cuts
        // format: TMVACut:ModelName,preCutWeightFileName[,staticVar=value,staticVar2=value,...]
        else if(flag.find("tmvacut:") != string::npos ) {
          string tmvaCutParams = flagOrig.substr(flag.find("tmvacut:")+8);
          vector<string> splitByCommas = ::split(tmvaCutParams, ',');
          if(splitByCommas.size() < 2) {
            STDOUT("ERROR: TMVACut specifier must look like 'TMVACut:modelName,preCutNameForWeightFile[,stativVar=value,...]'. What was found looks like '" << flag << "' instead.");
            exit(-2);
          }
          string modelName = splitByCommas[0];
          string weightFile = getPreCutString1(splitByCommas[1]);
          thisCut.reset(new TMVACut(modelName, weightFile));
          isTMVACut = true;
          if(splitByCommas.size() > 2) {
            for(int index = 2; index < splitByCommas.size(); ++index) {
              string param = splitByCommas[2];
              vector<string> splitByEquals = ::split(param, '=');
              if(splitByEquals.size() != 2) {
                STDOUT("ERROR: Didn't understand TMVACut parameter '" << param << "'. TMVACut specifier must look like 'TMVACut:modelName,preCutNameForWeightFile[,stativVar=value,...]'. What was found looks like '" << flag << "' instead.");
                exit(-2);
              }
              staticParametersMap[splitByEquals[0]] = stof(splitByEquals[1]);
            }
          }
          // TMVA input variables (defined in XML) have to be specified in the cut file as cuts already
          vector<shared_ptr<cut>> tmvaCuts;
          tmvaCuts.reserve(thisCut->getInputVariableNames().size());
          for(const auto& varName : thisCut->getInputVariableNames()) {
            auto&& cc = cutName_cut_.find(varName);
            if( cc == cutName_cut_.end() ) {
              shared_ptr staticCutPtr  = make_shared<cut>();
              staticCutPtr->variableName = varName;
              staticCutPtr->value = staticParametersMap.find(varName)->second;
              staticCutPtr->passed = true;
              staticCutPtr->filled = true;
              tmvaCuts.push_back(staticCutPtr);
            }
            else
              tmvaCuts.push_back(cc->second);
          }
          thisCut->setupReader(tmvaCuts);
        }
        else if(flag.find("systs") != string::npos)
          thisCut->computeSysts = true;
      }
      thisCut->variableName = variableName;
      thisCut->minValue1  = decodeCutValue( m1 );
      thisCut->maxValue1  = decodeCutValue( M1 );
      thisCut->minValue2  = decodeCutValue( m2 );
      thisCut->maxValue2  = decodeCutValue( M2 );
      thisCut->level_int  = level_int;
      if(level_int >= SYST_LEVEL)
        thisCut->computeSysts = true;
      thisCut->level_str  =       v[5];
      thisCut->histoNBins = atoi( v[6].c_str() );
      thisCut->histoMin   = atof( v[7].c_str() );
      thisCut->histoMax   = atof( v[8].c_str() );

      // Not filled from file
      thisCut->id=++id;
      string s1;
      if(skimWasMade_)
      {
        s1 = "cutHisto_skim___________________" + thisCut->variableName;
      }
      else
      {
        s1 = "cutHisto_noCuts_________________" + thisCut->variableName;
      }
      string s2 = "cutHisto_allPreviousCuts________" + thisCut->variableName;
      string s3 = "cutHisto_allOthrSmAndLwrLvlCuts_" + thisCut->variableName;
      string s4 = "cutHisto_allOtherCuts___________" + thisCut->variableName;
      string s5 = "cutHisto_allCuts________________" + thisCut->variableName;
      string s6 = "cutHisto_allOtherSameLevelCuts__" + thisCut->variableName;
      thisCut->histo1 = TH1D (s1.c_str(),"", thisCut->histoNBins, thisCut->histoMin, thisCut->histoMax);
      thisCut->histo2 = TH1D (s2.c_str(),"", thisCut->histoNBins, thisCut->histoMin, thisCut->histoMax);
      thisCut->histo3 = TH1D (s3.c_str(),"", thisCut->histoNBins, thisCut->histoMin, thisCut->histoMax);
      thisCut->histo4 = TH1D (s4.c_str(),"", thisCut->histoNBins, thisCut->histoMin, thisCut->histoMax);
      thisCut->histo5 = TH1D (s5.c_str(),"", thisCut->histoNBins, thisCut->histoMin, thisCut->histoMax);
      thisCut->histo6 = TH1D (s6.c_str(),"", thisCut->histoNBins, thisCut->histoMin, thisCut->histoMax);
      thisCut->histo1.Sumw2();
      thisCut->histo2.Sumw2();
      thisCut->histo3.Sumw2();
      thisCut->histo4.Sumw2();
      thisCut->histo5.Sumw2();
      thisCut->histo6.Sumw2();
      // Filled event by event
      thisCut->filled = false;
      thisCut->weight = 1;
      thisCut->passed = false;
      thisCut->nEvtPassedBeforeWeight=0;
      thisCut->nEvtPassed=0;
      thisCut->nEvtPassedErr2=0;
      thisCut->nEvtPassedBeforeWeight_alreadyFilled = false;

      orderedCutNames_.push_back(thisCut->variableName);
      if(isTMVACut) {
        systCutName_cut_[thisCut->variableName] = make_shared<TMVACut>(*dynamic_cast<TMVACut*>(thisCut.get()));
        vector<shared_ptr<cut>> tmvaCuts;
        tmvaCuts.reserve(thisCut->getInputVariableNames().size());
        for(const auto& varName : thisCut->getInputVariableNames()) {
          auto&& cc = systCutName_cut_.find(varName);
          if( cc == systCutName_cut_.end() ) {
            shared_ptr staticCutPtr  = make_shared<cut>();
            staticCutPtr->variableName = varName;
            staticCutPtr->value = staticParametersMap.find(varName)->second;
            staticCutPtr->passed = true;
            staticCutPtr->filled = true;
            tmvaCuts.push_back(staticCutPtr);
          }
          else {
            tmvaCuts.push_back(cc->second);
          }
        }
        systCutName_cut_[thisCut->variableName]->setupReader(tmvaCuts);
      }
      else
        systCutName_cut_[thisCut->variableName] = make_shared<cut>(*thisCut);
      string varName = thisCut->variableName;
      cutName_cut_[thisCut->variableName] = move(thisCut);
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
    h_optimizer_=new TH1D("optimizer","Optimization of cut variables",(int)pow(nOptimizerCuts_,optimizeName_cut_.size()),0,
        pow(nOptimizerCuts_,optimizeName_cut_.size()));
    h_optimizer_->Sumw2();
    h_optimizer_entries_ =new TH1I("optimizerEntries","Optimization of cut variables (entries)",(int)pow(nOptimizerCuts_,optimizeName_cut_.size()),0,
        pow(nOptimizerCuts_,optimizeName_cut_.size()));
    h_optimizer_entries_->Sumw2();
  }

  is.close();

  produceSkim_ = false;
  NAfterSkim_ = 0;
  if(int(getSkimPreCutValue("produceSkim"))==1)
    produceSkim_ = true;
  produceReducedSkim_ = false;
  NAfterReducedSkim_ = 0;
  if(int(getSkimPreCutValue("produceReducedSkim"))==1) {
    STDOUT("Producing reduced skim!");
    produceReducedSkim_ = true;
  }

  
  // Create a histogram that will show events passing cuts
  int cutsize=orderedCutNames_.size()+1;
  int skimCutSize = getCutsAtLevel(SKIM_LEVEL).size()+1;
  if (skimWasMade_) 
  {
    ++cutsize;
    ++skimCutSize;
  }
  gDirectory->cd();
  auto eventsPassingCutsProf = dynamic_pointer_cast<TProfile>(findSavedHist("EventsPassingSkimCuts"));
  int nSkimCuts = 2;
  nPreviousSkimCuts_ = 0;
  if(!eventsPassingCutsProf)
  {
    STDOUT("INFO: no pre-existing EventsPassingSkimCuts profile.");
    // this should be the case when there was no previous skim (besides in nano processing) --> no hist in input root file(s)
    if(produceReducedSkim_ || produceSkim_)
    {
      STDOUT("INFO: doing skim -- creating new EventsPassingSkimCuts profile.");
      gDirectory->cd();
      auto newProf = makeNewEventsPassingSkimCutsProfile();
      newProf->SetNameTitle("EventsPassingSkimCuts", "Events Passing Skim Cuts");
      histsToSave_.push_back(newProf);
    }
    else
      STDOUT("INFO: not doing skim -- produceReducedSkim_=" << produceReducedSkim_ << " and produceSkim_=" << produceSkim_ << "; not creating new EventsPassingSkimCuts profile.");
  }
  else
  {
    STDOUT("INFO: found pre-existing EventsPassingSkimCuts profile.");
    // we have a previous skim profile available
    nPreviousSkimCuts_ = eventsPassingCutsProf->GetNbinsX();
    if(produceReducedSkim_ || produceSkim_)
    {
      STDOUT("INFO: doing skim -- updating pre-existing EventsPassingSkimCuts profile.");
      auto newProf = makeNewEventsPassingSkimCutsProfile(eventsPassingCutsProf);
      histsToSave_.erase(find(histsToSave_.begin(), histsToSave_.end(), eventsPassingCutsProf));
      newProf->SetNameTitle("EventsPassingSkimCuts", "Events Passing Skim Cuts");
      histsToSave_.push_back(newProf);
    }
    nSkimCuts = eventsPassingCutsProf->GetNbinsX();
  }
  auto savedEventsPassingCuts = dynamic_pointer_cast<TProfile>(findSavedHist("EventsPassingSkimCuts"));
  if(!savedEventsPassingCuts) {
    STDOUT("ERROR: did not find an EventsPassingSkimCuts profile, though we should have by this point!  exiting");
    exit(-5);
  }
  eventCuts_ = std::shared_ptr<TProfile>(new TProfile("EventsPassingCuts","Events Passing Cuts",cutsize,0,cutsize));
  eventCuts_->Sumw2();
  eventCutsHist_ = std::shared_ptr<TH1D>(new TH1D("EventsPassingCutsAllHist","Events Passing Cuts",cutsize+nSkimCuts,0,cutsize+nSkimCuts));
  eventCutsHist_->Sumw2();
  eventCutsEfficHist_ = std::shared_ptr<TH1D>(new TH1D("EfficiencyPassingCutsAllHist","Abs. Efficiency of Passing Cuts",cutsize+nSkimCuts,0,cutsize+nSkimCuts));
  eventCutsEfficHist_->Sumw2();
  if(eventsPassingCutsProf) {
    double noCuts = eventsPassingCutsProf->GetBinEntries(1);
    for(int iBin=1; iBin <= nSkimCuts; iBin++) {
      double sumw = eventsPassingCutsProf->GetBinContent(iBin)*eventsPassingCutsProf->GetBinEntries(iBin);
      double sqrtSumw2 = sqrt(eventsPassingCutsProf->GetSumw2()->At(iBin));
      eventCutsHist_->GetXaxis()->SetBinLabel(iBin, eventsPassingCutsProf->GetXaxis()->GetBinLabel(iBin));
      checkOverflow(eventCutsHist_.get(), sumw);
      eventCutsHist_->SetBinContent(iBin, sumw);
      eventCutsHist_->SetBinError(iBin, sqrtSumw2);
      eventCutsEfficHist_->GetXaxis()->SetBinLabel(iBin, eventsPassingCutsProf->GetXaxis()->GetBinLabel(iBin));
      double N = noCuts;
      double p = sumw / N;
      eventCutsEfficHist_->SetBinContent(iBin, p);
      double q = 1-p;
      double w = sumw / eventsPassingCutsProf->GetBinEntries(iBin);
      double effAbsErr = sqrt(p*q/N)*w;
      eventCutsEfficHist_->SetBinError(iBin, effAbsErr);
    }
  }
  else {
    Long64_t nEntTot = (skimWasMade_ ? NBeforeSkim_ : GetTreeEntries() );
    eventCutsHist_->GetXaxis()->SetBinLabel(1, "NoCuts");
    checkOverflow(eventCutsHist_.get(), nEntTot);
    eventCutsHist_->SetBinContent(1, nEntTot);
    eventCutsHist_->SetBinError(1, sqrt(nEntTot));
    eventCutsEfficHist_->GetXaxis()->SetBinLabel(1, "NoCuts");
    eventCutsEfficHist_->SetBinContent(1, 1.0);
    eventCutsEfficHist_->SetBinError(1, 0.0);
    eventCutsEfficHist_->GetXaxis()->SetBinLabel(2, "Skim");
    checkOverflow(eventCutsHist_.get(),GetTreeEntries());
    eventCutsHist_->SetBinContent(2, GetTreeEntries());
    eventCutsHist_->SetBinError(2, sqrt(GetTreeEntries()));
    eventCutsEfficHist_->GetXaxis()->SetBinLabel(2, "Skim");
    double N = nEntTot;
    double p = GetTreeEntries() / N;
    eventCutsEfficHist_->SetBinContent(2, p);
    double q = 1-p;
    double effAbsErr = sqrt(p*q/N);
    eventCutsEfficHist_->SetBinError(2, effAbsErr);
  }

  for(auto& systLine : systLines) {
    vector<string> v = split(systLine);
    Systematic syst(v[1]);
    if(v.size() > 2) {
      // regexp to match with branch pattern
      if (v[2].find("regex=")==0) {
        size_t firstQuote = v[2].find_first_of("\"")+1;
        size_t lastQuote = v[2].find_last_of("\"");
        syst.regex = v[2].substr(firstQuote, lastQuote-firstQuote);
        syst.length = 1;
      }
      // tformula-compatible string
      else {
        syst.formula.reset(new TTreeFormula(syst.name.c_str(), v[2].c_str(), readerTools_->GetTree().get()));
        if(!syst.formula->GetNdim()) {
          STDOUT("ERROR: syst named '" << syst.name << "' has invalid formula: '" << v[2] << "', Check syntax (TFormula) and make sure that any branches used exist in the tree.");
          exit(-6);
        }
        syst.length = syst.formula->GetNdata();
      }
    }
    STDOUT("for syst named: " << syst.name << "; syst.length = " << syst.length);
    // parse cut variables affected by syst
    if(v.size() > 3) {
      istringstream iss(v[3]);
      string cutVar;
      string branchName;
      // loop over list of cutVars
      while (getline(iss, cutVar, ',')) {
        boost::regex regExp(syst.regex);
        // try to find the regex-matching branch for this cutVar
        string matchingBranch;
        bool foundMatchingBranch = false;
        for(unsigned int i=0; i<tree_->GetListOfBranches()->GetEntries(); ++i) {
          TBranch* branch = static_cast<TBranch*>(tree_->GetListOfBranches()->At(i));
          branchName = branch->GetName();
          if(branchName.find(cutVar)!=string::npos) {
            if(boost::regex_search(branchName, regExp)) {
              if(foundMatchingBranch) {
                STDOUT("ERROR: Already found matching branch for syst name="+v[1]+" with "+v[2]+": "+matchingBranch+" but found another matching branch: "+branchName+". Can't handle this.");
                exit(-6);
              }
              matchingBranch = branchName;
              foundMatchingBranch = true;
            }
          }
        }
        // in case there is no matching branch, we still put an entry in the map: cutVar-->""
        bool handledCutVar = false;
        for(auto& cutName : orderedCutNames_) {
          if(cutName.find(cutVar) != string::npos) {
            syst.cutNamesToBranchNames[cutName] = matchingBranch;
            //STDOUT("syst=" << syst.name << "--> Added matchingBranch=" << matchingBranch << " for cutName=" << cutName);
            handledCutVar = true;
          }
        }
        if(!handledCutVar) {
          STDOUT("ERROR: did not find any cuts in the cut file that contain the cutVar '" << cutVar << "'. Can't handle this systematic: '" << syst.name << "'. Quitting here.");
          exit(-6);
        }
      }
    }
    systematics_.push_back(move(syst));
  }


  // make syst hist
  if(haveSystematics()) {
    // add hardcoded nominal
    Systematic nominalSyst("nominal");
    nominalSyst.formula.reset(new TTreeFormula("nominal","1", readerTools_->GetTree().get()));
    systematics_.emplace(systematics_.begin(), move(nominalSyst));
    // special PDF oand scale weight bins
    vector<string> pdfCombBins = {"LHEPdfWeightMC_UpComb", "LHEPdfWeightMC_DownComb", "LHEPdfWeightHessian_NominalComb", "LHEPdf_UpComb", "LHEPdf_DownComb"};
    vector<string> scaleCombBins = {"LHEScaleWeight_maxComb", "LHEScale_UpComb", "LHEScale_DownComb"};

    int nSysts = 0;
    for(auto& syst : systematics_) {
      unsigned int length = syst.length;
      // always use 103 PDF weights and 9 scale weights
      if(syst.name=="LHEPdfWeight") {
        length = NUMPDFWEIGHTS;
        length+=pdfCombBins.size();
      }
      else if(syst.name=="LHEScaleWeight") {
        length = NUMSCALEWEIGHTS;
        length+=scaleCombBins.size();
      }
      nSysts+=length;
    }
    for (int i=0;i<orderedCutNames_.size();++i) {
      auto&& cc = cutName_cut_.find(orderedCutNames_[i]);
      if(cc->second->computeSysts)
      orderedSystCutNames_.push_back(cc->first);
    }
    int nCutsForSysts = orderedSystCutNames_.size();
    STDOUT("Making systematics 2D hist with " << nCutsForSysts << " x bins");
    histsToSave_.push_back(std::shared_ptr<TH2D>(new TH2D("systematics", "systematics", nCutsForSysts, 0, nCutsForSysts, nSysts, 0, nSysts)));
    currentSystematicsHist_.reset(new TH2D("currentSystematics", "current systematics", nCutsForSysts, 0, nCutsForSysts, nSysts, 0, nSysts));
    auto systHist = dynamic_pointer_cast<TH2D>(histsToSave_.back());
    histsToSave_.push_back(std::shared_ptr<TH2D>(new TH2D("systematicsUnweighted", "systematics (no weight)", nCutsForSysts, 0, nCutsForSysts, nSysts, 0, nSysts)));
    auto systHistUnweighted = dynamic_pointer_cast<TH2D>(histsToSave_.back());
    systHist->Sumw2();
    systHist->SetDirectory(0);
    systHistUnweighted->Sumw2();
    systHistUnweighted->SetDirectory(0);
    int idx = 1;
    for (auto& cutName : orderedSystCutNames_) {
      systHist->GetXaxis()->SetBinLabel(idx, cutName.c_str());
      systHistUnweighted->GetXaxis()->SetBinLabel(idx, cutName.c_str());
      ++idx;
    }
    idx = 1;
    for(auto& syst : systematics_) {
      if(syst.length==1) {
        systHist->GetYaxis()->SetBinLabel(idx, syst.name.c_str());
        systHistUnweighted->GetYaxis()->SetBinLabel(idx, syst.name.c_str());
        ++idx;
      }
      else {
        unsigned int length = syst.length;
        // always use 103 PDF weights and 9 scale weights
        if(syst.name=="LHEPdfWeight")
          length = NUMPDFWEIGHTS;
        else if(syst.name=="LHEScaleWeight")
          length = NUMSCALEWEIGHTS;
        for(int arrIdx = 0; arrIdx < length; ++arrIdx) {
          string systName = syst.name + "_" + to_string(arrIdx);
          systHist->GetYaxis()->SetBinLabel(idx, systName.c_str());
          systHistUnweighted->GetYaxis()->SetBinLabel(idx, systName.c_str());
          ++idx;
        }
        if(syst.name=="LHEPdfWeight") {
          for(const auto& binName : pdfCombBins) {
            systHist->GetYaxis()->SetBinLabel(idx, binName.c_str());
            systHistUnweighted->GetYaxis()->SetBinLabel(idx, binName.c_str());
            ++idx;
          }
        }
        else if(syst.name=="LHEScaleWeight") {
          for(const auto& binName : scaleCombBins) {
            systHist->GetYaxis()->SetBinLabel(idx, binName.c_str());
            systHistUnweighted->GetYaxis()->SetBinLabel(idx, binName.c_str());
            ++idx;
          }
        }
      }
    }
    systHist->GetYaxis()->Copy(*currentSystematicsHist_->GetYaxis());
  }
}

void baseClass::resetCuts(const string& s)
{
  for (auto& cc : cutName_cut_)
    {
      auto& c = cc.second;
      if(c->isStatic)
        continue;
      c->filled = false;
      //c->value = decltype(c->value)();
      c->resetValue();
      c->weight = 1;
      c->passed = false;
      c->evaluatedPreviousCuts = false;
      c->passedPreviousCuts = false;
      if(haveSystematics()) {
        systCutName_cut_[cc.first]->filled = false;
        systCutName_cut_[cc.first]->value = decltype(systCutName_cut_[cc.first]->value)();
        systCutName_cut_[cc.first]->weight = 1;
        systCutName_cut_[cc.first]->passed = false;
        systCutName_cut_[cc.first]->evaluatedPreviousCuts = false;
        systCutName_cut_[cc.first]->passedPreviousCuts = false;
        for(auto& syst : systematics_) {
          for(auto& mapItem : syst.cutNamesToSystValues) {
            syst.cutNamesToSystValues[mapItem.first] = 0;
            syst.cutNamesToSystFilled[mapItem.first] = false;
          }
        }
      }
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

void baseClass::fillSystVariableWithValue(const string& s, const string& cutVar, const float& d) {
  if(!haveSystematics())
    return;
  bool systFound = false;
  for(auto& syst : systematics_) {
    if(syst.name==s) {
      syst.cutNamesToSystValues[cutVar] = d;
      syst.cutNamesToSystFilled[cutVar] = true;
      systFound = true;
      break;
    }
  }
}

void baseClass::fillSystVariableWithValue(const string& s, const float& d) {
  if(!haveSystematics())
    return;
  bool systFound = false;
  for(auto& syst : systematics_) {
    if(syst.name==s) {
      syst.value = d;
      syst.filled = true;
      systFound = true;
      break;
    }
  }
}

template <typename T> void baseClass::fillArrayVariableWithValue(const string& s, TTreeReaderArray<T>& reader)
{
  auto&& cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
  {
    STDOUT("ERROR: variableName = "<< s << " not found in cutName_cut_. Exiting.");
    exit(-5);
  }
  else
  {
    auto& c = cc->second;
    c->filled = true;
    c->value = T();
    c->weight = 1.;
    if(reader.GetSize() > cut::MAX_ARRAY_SIZE)
    {
      STDOUT("WARNING: truncated array size from" << reader.GetSize() << " to MAX_ARRAY_SIZE=" << cut::MAX_ARRAY_SIZE << " in this event.");
      c->arraySize = cut::MAX_ARRAY_SIZE;
    }
    else
      c->arraySize = reader.GetSize();
    // set the branch title for arrays; this includes useful information from NanoAOD
    TBranch* arrayBranch = reduced_skim_tree_->FindBranch(s.c_str());
    if(std::string(arrayBranch->GetTitle()).empty()) {
      std::string readerBranchName(reader.GetBranchName());
      std::string title(readerTools_->GetTree()->FindBranch(readerBranchName.c_str())->GetTitle());
      //STDOUT("INFO: setting branch '" << s << "' title to '" << title << "'");
      arrayBranch->SetTitle(title.c_str());
    }
    else {
      // check to make sure the title hasn't changed (could happen when running over different datasets in one job)
      std::string readerBranchName(reader.GetBranchName());
      std::string title(readerTools_->GetTree()->FindBranch(readerBranchName.c_str())->GetTitle());
      if(title != std::string(arrayBranch->GetTitle())) {
        STDOUT("ERROR: inconsistent array branch content for branch named: " << s << "; branch title had been '" << arrayBranch->GetTitle() <<
            "', and has now changed to '" << title <<
            "' inside file: " << readerTools_->GetTree()->GetCurrentFile()->GetName());
        exit(-5);
      }
    }
    arrayBranch->SetAddress(const_cast<void*>(reader.GetAddress()));
  }
  return;
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

template<typename T> void baseClass::evaluateCuts(map<string, T>& cutNameToCut, map<string, bool>& combNameToPassFail, vector<string>& orderedCutNames, bool verbose)
{
  combNameToPassFail.clear();
  for (vector<string>::iterator it = orderedCutNames.begin(); it != orderedCutNames.end(); it++)
  {
    auto&& cc = cutNameToCut.find(*it);
    auto& c = cc->second;
    std::string cName = c->variableName;
    c->evaluatedPreviousCuts = false; // if redoing individual cuts, have to redo previous cut checking as well
    bool passed = c->evaluateCut();

    if( !passed )
    {
      c->passed = false;
      combNameToPassFail[c->level_str.c_str()] = false;
      combNameToPassFail["all"] = false;
      if(verbose) std::cout << "FAILED cut: " << c->variableName << "; value is: " << c->getStringValue() << std::endl;
    }
    else
    {
      c->passed = true;
      map<string,bool>::iterator cp = combNameToPassFail.find( c->level_str.c_str() );
      combNameToPassFail[c->level_str.c_str()] = (cp==combNameToPassFail.end()?true:cp->second);
      map<string,bool>::iterator ap = combNameToPassFail.find( "all" );
      combNameToPassFail["all"] = (ap==combNameToPassFail.end()?true:ap->second);
      if(verbose) std::cout << "PASSED cut: " << c->variableName << "; value is: " << c->getStringValue() << std::endl;
    }
  }
}

void baseClass::evaluateCuts(bool verbose)
{
  evaluateCuts(cutName_cut_, combCutName_passed_, orderedCutNames_);

  runOptimizer();

  if(haveSystematics())
    runSystematics();

  if( !fillCutHistos() )
  {
    STDOUT("ERROR: fillCutHistos did not complete successfully.");
  }

  if( !updateCutEffic() )
  {
    STDOUT("ERROR: updateCutEffic did not complete successfully.");
  }

  if(passedAllCutsAtLevel(SKIM_LEVEL))
  {
    if(produceReducedSkim_)
      fillReducedSkimTree();
    if(produceSkim_)
      fillSkimTree();
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
      h_optimizer_->Fill(i,cutName_cut_[orderedCutNames_.at(orderedCutNames_.size()-1)]->weight); // take the event weight from the last cut in the cut file
      h_optimizer_entries_->Fill(i);
    }

  }

  return;
} //runOptimizer

void baseClass::runSystematics()
{
  shared_ptr<TH2D> systHist = dynamic_pointer_cast<TH2D>(findSavedHist("systematics"));
  if(systHist == nullptr) {
    cout << "ERROR: could not find systematics histogram. This shouldn't happen. Exiting" << endl;
    exit(-6);
  }
  shared_ptr<TH2D> systHistUnweighted = dynamic_pointer_cast<TH2D>(findSavedHist("systematicsUnweighted"));
  if(systHistUnweighted == nullptr) {
    cout << "ERROR: could not find systematics unweighted histogram. This shouldn't happen. Exiting" << endl;
    exit(-6);
  }
  currentSystematicsHist_->Reset();
  // copy cut decisions/filled
  for(auto& cutName : orderedCutNames_) {
    systCutName_cut_[cutName]->passed = cutName_cut_[cutName]->passed;
    systCutName_cut_[cutName]->filled = cutName_cut_[cutName]->filled;
    systCutName_cut_[cutName]->weight = cutName_cut_[cutName]->weight;
    systCutName_cut_[cutName]->value = cutName_cut_[cutName]->value;
    systCutName_cut_[cutName]->passedPreviousCuts = cutName_cut_[cutName]->passedPreviousCuts;
    systCutName_cut_[cutName]->evaluatedPreviousCuts = cutName_cut_[cutName]->evaluatedPreviousCuts;
  }
  for(auto& syst : systematics_) {
    int currentLength = syst.formula ? syst.formula->GetNdata() : syst.length;
    if(syst.length!=currentLength) {
      string msg = "For systematic named: " + syst.name + ", length in event " + to_string(GetCurrentEntry()) + " is: " + to_string(currentLength) +
        " != initial length of: " + to_string(syst.length) + "." +
        " Cannot handle this situation! Bailing out.";
      cout << msg << endl;
      exit(-6);
    }
    map<string, bool> combCutNameToPassFail;
    bool shiftValue = !syst.cutNamesToBranchNames.empty();
    for(int i=0; i < currentLength; ++i) {
      float systVal = syst.value;
      if(shiftValue) {
        for(auto& cutNameBranch : syst.cutNamesToBranchNames) {
          auto cutName = cutNameBranch.first;
          auto& systCut = systCutName_cut_[cutName];
          systCut->filled = false;
          if(syst.cutNamesToBranchNames[cutName].size()) {
            //cout << "[DEBUG] syst " << syst.name << " affects cut named: " << cutName << "; replace orig val of: " << systCut->getValue<float>() << 
            //  " with the value of the branch: " << syst.cutNamesToBranchNames[cutName];
            //cout << " which is: " << readerTools_->ReadValueBranch<Float_t>(syst.cutNamesToBranchNames[cutName]) << endl;
            //STDOUT("\tDEBUG: [pre-value overwrite] systCut " << cutName << " has value = " << systCut->getValue<float>() << " and address: " << systCut->getValueAddress<float>());
            systCut->value = readerTools_->ReadValueBranch<Float_t>(syst.cutNamesToBranchNames[cutName]);
            systCut->filled = true;
          }
          else {
            systVal = syst.cutNamesToSystValues[cutName];
            //cout << "\t[DEBUG] syst affects cut named: " << cutNameCut.first << "; replace orig val of: " << cutNameCut.second.value << 
            //  " with the syst value: " << systVal << "; filled? " << syst.cutNamesToSystFilled[cutNameCut.first] << endl;
            if(syst.cutNamesToSystFilled[cutName]) {
              systCut->value = systVal;
              systCut->filled = true;
            }
            else {
              STDOUT("ERROR: syst value for cut named: " << cutName << " was not filled for systematic " << syst.name <<
                  "! No regex matching branches specified in cutfile for this cut, so must be filled manually with fillSystVariableWithValue()." <<
                  " Can't compute systematic for this cut. Quitting.");
              exit(-6);
            }
          }
        }
        // reevaluate since cuts were updated
        evaluateCuts(systCutName_cut_, combCutNameToPassFail, orderedSystCutNames_);
      }
      else {
        if(syst.formula)
          systVal = syst.formula->EvalInstance(i);
        else if(!syst.filled) {
          STDOUT("ERROR: For systematic " << syst.name << ", no formula was given and no filled value was found either! Did you forget to call fillSystVariableWithValue()?" <<
              " Can't compute systematic for this cut. Quitting.");
          exit(-6);
        }
      }
      float xbinCoord = 0.5;
      std::string systNameBinLookup = currentLength==1 ? syst.name : syst.name+"_"+to_string(i);
      float ybinCoord = systHist->GetYaxis()->GetBinCenter(systHist->GetYaxis()->FindFixBin(systNameBinLookup.c_str()));
      for(auto& cutName : orderedSystCutNames_) {
        //if(syst.name == "nominal" || syst.name=="JERUp") {
        //  STDOUT("[DEBUG] passedCut() for cut: " << cutName << "? " << passedCut(cutName, systCutName_cut_, combCutNameToPassFail) << ", value=" << systCutName_cut_[cutName]->getValue<float>() << ", for syst: " << syst.name);
        //  STDOUT("[DEBUG] calling passedSelection() for selection: " << cutName << " for syst: " << syst.name);
        //}
        //TODO: perhaps remove the list of cut names; always have to use the full list!
        if(passedSelection(cutName, systCutName_cut_, combCutNameToPassFail, orderedCutNames_)) {
          //if(syst.name == "nominal" || syst.name=="JERUp") {
          //  cout << "[DEBUG]: passed selection " << cutName << " with value="<< systCutName_cut_[cutName]->getValue<float>() << "; fill syst hist; syst="<<syst.name<<",  xbin: " << xbinCoord << ", ybin: " << ybinCoord <<
          //    ", origWeight=" << systCutName_cut_[cutName]->weight << "; systVal=" << systVal << "; new weight= " << systCutName_cut_[cutName]->weight*systVal <<
          //    " passedPreviousCuts? " << systCutName_cut_[cutName]->passedPreviousCuts << " evaluatedPreviousCuts? " << systCutName_cut_[cutName]->evaluatedPreviousCuts << endl;
          //  cout << "\t[DEBUG]: NOMINAL selection " << cutName << " with value="<< cutName_cut_[cutName]->getValue<float>()
          //    << " passedSelection? " << passedSelection(cutName, cutName_cut_, combCutNameToPassFail, orderedCutNames_) <<
          //    " passedPreviousCuts? " << cutName_cut_[cutName]->passedPreviousCuts << " evaluatedPreviousCuts? " << cutName_cut_[cutName]->evaluatedPreviousCuts << endl;
          //}
          if(shiftValue) {
            systHist->Fill(xbinCoord, ybinCoord, systCutName_cut_[cutName]->weight);
            systHistUnweighted->Fill(xbinCoord, ybinCoord);
            currentSystematicsHist_->Fill(xbinCoord, ybinCoord, 1);
            //int bin = currentSystematicsHist_->FindFixBin(xbinCoord, ybinCoord);
            //if(syst.name=="JERUp")
            //  STDOUT("INFO: runSystematics(): 1. fill hist for syst="<<syst.name<<", systCutName=" << cutName //<<", binX=" << currentSystematicsHist_->GetXaxis()->FindFixBin(xbinCoord) << ", binY=" << currentSystematicsHist_->GetYaxis()->FindFixBin(ybinCoord)
            //      << ", nom. weight="<<systCutName_cut_[cutName]->weight << "; binContent=" << systHist->GetBinContent(bin));
          }
          else {
            systHist->Fill(xbinCoord, ybinCoord, systCutName_cut_[cutName]->weight*systVal);
            systHistUnweighted->Fill(xbinCoord, ybinCoord, systVal);
            currentSystematicsHist_->Fill(xbinCoord, ybinCoord, systVal);
            //int bin = currentSystematicsHist_->FindFixBin(xbinCoord, ybinCoord);
            //if(syst.name == "nominal")
            //  STDOUT("DEBUG: runSystematics() passed selection " << cutName << ": 2. fill hist for syst="<<syst.name<<", systCutName=" << cutName //<<", binX=" << currentSystematicsHist_->GetXaxis()->FindFixBin(xbinCoord) << ", binY=" << currentSystematicsHist_->GetYaxis()->FindFixBin(ybinCoord)
            //      << ", syst. weight=weight*systVal="<<systCutName_cut_[cutName]->weight << "*"
            //      << systVal << "=" << systCutName_cut_[cutName]->weight*systVal << "; binContent=" << systHist->GetBinContent(bin));
          }
        }
        xbinCoord+=1;
      }
      if(shiftValue) {
        // if value was shifted, reset all the cuts to nominal before moving to next syst
        for(auto& cutName : orderedCutNames_) {
          systCutName_cut_[cutName]->passed = cutName_cut_[cutName]->passed;
          systCutName_cut_[cutName]->filled = cutName_cut_[cutName]->filled;
          systCutName_cut_[cutName]->weight = cutName_cut_[cutName]->weight;
          systCutName_cut_[cutName]->value = cutName_cut_[cutName]->value;
          systCutName_cut_[cutName]->passedPreviousCuts = cutName_cut_[cutName]->passedPreviousCuts;
          systCutName_cut_[cutName]->evaluatedPreviousCuts = cutName_cut_[cutName]->evaluatedPreviousCuts;
        }
      }
    }
  }
}

float baseClass::getPreCutValue1(const string& s)
{
  float ret;
  const auto& cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Bailing.");
    STDOUT("precut names:");
    for( auto& pair : preCutName_cut_)
      std::cout << pair.first << std::endl;
    exit(-5);
  }
  if(cc->second->value1 == -999) STDOUT("ERROR: value1 of preliminary cut "<<s<<" was not provided.");
  return (cc->second->value1);
}

float baseClass::getPreCutValue2(const string& s)
{
  float ret;
  const auto& cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Bailing.");
    exit(-5);
  }
  if(cc->second->value2 == -999) STDOUT("ERROR: value2 of preliminary cut "<<s<<" was not provided.");
  return (cc->second->value2);
}

float baseClass::getPreCutValue3(const string& s)
{
  float ret;
  const auto& cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Bailing.");
    exit(-5);
  }
  if(cc->second->value3 == -999) STDOUT("ERROR: value3 of preliminary cut "<<s<<" was not provided.");
  return (cc->second->value3);
}

float baseClass::getPreCutValue4(const string& s)
{
  float ret;
  const auto& cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Bailing.");
    exit(-5);
  }
  if(cc->second->value4 == -999) STDOUT("ERROR: value4 of preliminary cut "<<s<<" was not provided.");
  return (cc->second->value4);
}

bool baseClass::hasPreCut(const string& s) {
  return preCutName_cut_.find(s) != preCutName_cut_.end();
}

string baseClass::getPreCutString1(const string& s)
{
  string ret;
  const auto& cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in preCutName_cut_. Bailing.");
    exit(-5);
  }
  return (cc->second->string1);
}

float baseClass::getCutMinValue1(const string& s)
{
  float ret;
  auto&& cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning");
  }
  return cc->second->minValue1;
}

float baseClass::getCutMaxValue1(const string& s)
{
  float ret;
  auto&& cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning");
  }
  return cc->second->maxValue1;
}

float baseClass::getCutMinValue2(const string& s)
{
  float ret;
  auto&& cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning");
  }
  return cc->second->minValue2;
}

float baseClass::getCutMaxValue2(const string& s)
{
  float ret;
  auto&& cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
  {
    STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning");
  }
  return cc->second->maxValue2;
}


const TH1D& baseClass::getHisto_noCuts_or_skim(const string& s)
{
  auto&& cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }
  return (cc->second->histo1);
}

const TH1D& baseClass::getHisto_allPreviousCuts(const string& s)
{
  auto&& cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }
  return (cc->second->histo2);
}

const TH1D& baseClass::getHisto_allOthrSmAndLwrLvlCuts(const string& s)
{
  auto&& cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }
  return (cc->second->histo3);
}

const TH1D& baseClass::getHisto_allOtherCuts(const string& s)
{
  auto&& cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }
  return (cc->second->histo4);
}

const TH1D& baseClass::getHisto_allCuts(const string& s)
{
  auto&& cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }
  return (cc->second->histo5);
}

int baseClass::getHistoNBins(const string& s)
{
  auto&& cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }
  return (cc->second->histoNBins);
}

float baseClass::getHistoMin(const string& s)
{
  auto&& cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }
  return (cc->second->histoMin);
}

float baseClass::getHistoMax(const string& s)
{
  auto&& cc = cutName_cut_.find(s);
  if( cc == cutName_cut_.end() )
    {
      STDOUT("ERROR: did not find variableName = "<<s<<" in cutName_cut_. Returning false.");
    }
  return (cc->second->histoMax);
}


bool baseClass::fillCutHistos()
{
  bool ret = true;
  for (vector<string>::iterator it = orderedCutNames_.begin();
      it != orderedCutNames_.end(); it++)
  {
    auto&& cc = cutName_cut_.find(*it);
    auto& c = cc->second;
    // only fill histos for float vars at the moment
    //XXX SIC FIXME
    if( c->filled && std::holds_alternative<float>(c->value)) {
      auto valPtr = std::get_if<float>(&c->value);
      auto val = *valPtr;
      if ( produceSkim_ || produceReducedSkim_ ) 
        c->histo1.Fill( val, c->weight );
      if ( fillAllPreviousCuts_ ) 
        if( passedAllPreviousCuts(c->variableName) )                c->histo2.Fill( val, c->weight );
      if( fillAllSameLevelAndLowerLevelCuts_) 
        if( passedAllOtherSameAndLowerLevelCuts(c->variableName) )  c->histo3.Fill( val, c->weight );
      if( fillAllOtherCuts_ ) 
        if( passedAllOtherCuts(c->variableName) )                   c->histo4.Fill( val, c->weight );
      if( fillAllCuts_ ) 
        if( passedCut("all") )                                      c->histo5.Fill( val, c->weight );
      if(fillAllSameLevelCuts_)
        if( passedAllOtherCutsAtSameLevel(c->variableName) )        c->histo6.Fill( val, c->weight );
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
      auto&& c = cutName_cut_.find(*it)->second;
      if ( produceSkim_ || produceReducedSkim_ ) c->histo1.Write();
      if ( fillAllPreviousCuts_                ) c->histo2.Write();
      if ( fillAllOtherCuts_                   ) c->histo4.Write();
#ifdef SAVE_ALL_HISTOGRAMS 
      if ( fillAllSameLevelAndLowerLevelCuts_  ) c->histo3.Write();
      if ( fillAllCuts_                        ) c->histo5.Write();
      if ( fillAllSameLevelCuts_               ) c->histo6.Write();
#endif // SAVE_ALL_HISTOGRAMS
    }

  // Any failure mode to implement?
  return ret;
}

bool baseClass::updateCutEffic()
{
  bool ret = true;
  for(const auto& cName : orderedCutNames_)
  {
    auto& c = cutName_cut_.at(cName);
    if( passedAllPreviousCuts(cName) )
    {
      if( passedCut(cName) )
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
  auto savedEventsPassingCuts = dynamic_pointer_cast<TProfile>(findSavedHist("EventsPassingSkimCuts"));
  if(!savedEventsPassingCuts) {
    STDOUT("ERROR: something very bad happened. The EventsPassingSkimCuts hist was not found in savedHists. Exiting.");
    exit(-5);
  }
  int allBinCounter = nPreviousSkimCuts_+1;

  eventCuts_->GetXaxis()->SetBinLabel(bincounter, "NoCuts");
  if(nPreviousSkimCuts_ < 1) {
    eventCutsHist_->GetXaxis()->SetBinLabel(bincounter, "NoCuts");
    eventCutsEfficHist_->GetXaxis()->SetBinLabel(bincounter, "NoCuts");
  }
  ++bincounter;

  if (skimWasMade_)
  {
    eventCuts_->GetXaxis()->SetBinLabel(bincounter, "Skim");
    if(nPreviousSkimCuts_ < 1) {
      eventCutsHist_->GetXaxis()->SetBinLabel(bincounter, "Skim");
      eventCutsEfficHist_->GetXaxis()->SetBinLabel(bincounter, "Skim");
      allBinCounter = bincounter+1;
    }
    ++bincounter;
  }
  for (int i=0;i<orderedCutNames_.size();++i)
  {
    eventCuts_->GetXaxis()->SetBinLabel(bincounter,orderedCutNames_[i].c_str());
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
  if (haveSystematics()) {
    os << "################################## systematics used at runtime    ###################################################################\n"
    << "##########systName                       source/formula                cutVariables" << endl;
    for(auto& syst : systematics_) {
      os << syst.name << setw(40) << (syst.formula ? syst.formula->GetTitle() : "N/A") << setw(40);
      string cutVars;
      for(auto& cutVarToBranchName: syst.cutNamesToBranchNames) {
        cutVars+=cutVarToBranchName.first+",";
      }
      if(cutVars.length())
        cutVars.pop_back();
      os << cutVars << endl;
    }
  } else { 
    os << "################################## NO systematics used at runtime ###################################################################\n";
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
     ;
  if(nPreviousSkimCuts_ < 1)
    os << fixed
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

  double effRel = 0;
  double effRelErr = 0;
  double effAbs = 0;
  double effAbsErr = 0;

  checkOverflow(eventCuts_.get(),nEntTot);
  eventCuts_->SetBinContent(bincounter,nEntTot);
  eventCuts_->SetBinError(bincounter,sqrt(nEntTot));
  eventCuts_->SetBinEntries(bincounter,nEntTot);
  if(nPreviousSkimCuts_ < 1) {
    checkOverflow(eventCutsHist_.get(), nEntTot);
    eventCutsHist_->SetBinContent(bincounter, nEntTot);
    eventCutsHist_->SetBinError(bincounter, sqrt(nEntTot));
    eventCutsEfficHist_->SetBinContent(bincounter, 1.0);
    eventCutsEfficHist_->SetBinError(bincounter, 0.0);
    checkOverflow(savedEventsPassingCuts.get(),nEntTot);
    savedEventsPassingCuts->SetBinContent(bincounter, nEntTot);
    savedEventsPassingCuts->SetBinError(bincounter, sqrt(nEntTot));
    savedEventsPassingCuts->SetBinEntries(bincounter, nEntTot);
  }
  if (optimizeName_cut_.size())
  {
    checkOverflow(h_optimizer_,nEntTot);
    h_optimizer_->SetBinContent(0, nEntTot);
    checkOverflow(h_optimizer_entries_,nEntTot);
    h_optimizer_entries_->SetBinContent(0, nEntTot);
  }

  double nEvtPassedBeforeWeight_previousCut = nEntTot;
  double nEvtPassed_previousCut = nEntTot;

  if(skimWasMade_)
  {
    ++bincounter;
    checkOverflow(eventCuts_.get(),GetTreeEntries());
    eventCuts_->SetBinContent(bincounter, GetTreeEntries() );
    eventCuts_->SetBinError(bincounter, sqrt(GetTreeEntries()) );
    eventCuts_->SetBinEntries(bincounter, GetTreeEntries() );
    if(nPreviousSkimCuts_ < 1) {
      checkOverflow(eventCutsHist_.get(),GetTreeEntries());
      eventCutsHist_->SetBinContent(bincounter, GetTreeEntries() );
      eventCutsHist_->SetBinError(bincounter, sqrt(GetTreeEntries()) );
      checkOverflow(savedEventsPassingCuts.get(), GetTreeEntries());
      savedEventsPassingCuts->SetBinContent(bincounter, GetTreeEntries());
      savedEventsPassingCuts->SetBinError(bincounter, sqrt(GetTreeEntries()));
      savedEventsPassingCuts->SetBinEntries(bincounter, GetTreeEntries());
      effRel = (double) GetTreeEntries() / (double) NBeforeSkim_;
      effRelErr = sqrt( (double) effRel * (1.0 - (double) effRel) / (double) NBeforeSkim_ );
      effAbs = effRel;
      effAbsErr = effRelErr;
      eventCutsEfficHist_->SetBinContent(bincounter, effAbs);
      eventCutsEfficHist_->SetBinError(bincounter, effAbsErr);
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
  }
  // put previous skim cuts in table/plots
  for(int iBin=1; iBin <= nPreviousSkimCuts_; ++iBin) {
    double n = savedEventsPassingCuts->GetBinEntries(iBin);
    double sumw = savedEventsPassingCuts->GetBinContent(iBin)*n;
    double sqrtSumw2 = sqrt(savedEventsPassingCuts->GetSumw2()->At(iBin));
    effRel = sumw / nEvtPassed_previousCut;
    double N = nEvtPassedBeforeWeight_previousCut;
    double Np = n;
    double p = Np / N;
    double q = 1-p;
    double w = sumw / n;
    effRelErr = sqrt(p*q/N)*w;
    effAbs = sumw / nEntTot;
    N = nEntTot;
    p = Np / N;
    q = 1-p;
    effAbsErr = sqrt(p*q/N)*w;
    os << fixed
      << setw(3) << ++cutIdPed
      << setw(35) << savedEventsPassingCuts->GetXaxis()->GetBinLabel(iBin)
      << setprecision(4)
      << setw(mainFieldWidth) << "-"
      << setw(mainFieldWidth) << "-"
      << setw(mainFieldWidth) << "-"
      << setw(mainFieldWidth) << "-"
      << setw(mainFieldWidth) << "-1"
      << setw(mainFieldWidth) << ( (nEvtPassed_previousCut < minForFixed) ? (scientific) : (fixed) ) << nEvtPassed_previousCut
      << setw(mainFieldWidth) << ( (sumw          < minForFixed) ? (scientific) : (fixed) ) << sumw
      << setw(mainFieldWidth) << ( (effRel                 < minForFixed) ? (scientific) : (fixed) ) << effRel
      << setw(mainFieldWidth) << ( (effRelErr              < minForFixed) ? (scientific) : (fixed) ) << effRelErr
      << setw(mainFieldWidth) << ( (effAbs                 < minForFixed) ? (scientific) : (fixed) ) << effAbs
      << setw(mainFieldWidth) << ( (effAbsErr              < minForFixed) ? (scientific) : (fixed) ) << effAbsErr
      << fixed << endl;
    nEvtPassedBeforeWeight_previousCut = n;
    nEvtPassed_previousCut = sumw;
    checkOverflow(eventCutsHist_.get(), sumw);
    eventCutsHist_->SetBinContent(iBin, sumw);
    eventCutsHist_->SetBinError(iBin, sqrtSumw2);
    eventCutsEfficHist_->SetBinContent(iBin, effAbs);
    if(!std::isnan(effAbsErr))
      eventCutsEfficHist_->SetBinError(iBin, effAbsErr);
    else
      eventCutsEfficHist_->SetBinError(iBin, 0.0);
  }
  allBinCounter = nPreviousSkimCuts_ > 0 ? nPreviousSkimCuts_+1 : bincounter+1;
  int skimBinCounter = allBinCounter;
  for (vector<string>::iterator it = orderedCutNames_.begin();
      it != orderedCutNames_.end(); it++)
  {
    auto&& c = cutName_cut_.find(*it)->second;
    ++bincounter;
    checkOverflow(eventCuts_.get(),c->nEvtPassed);
    eventCuts_->SetBinContent(bincounter, c->nEvtPassed);
    eventCuts_->SetBinError(bincounter, sqrt(c->nEvtPassedErr2));
    eventCuts_->SetBinEntries(bincounter, c->nEvtPassedBeforeWeight);
    checkOverflow(eventCutsHist_.get(),c->nEvtPassed);
    eventCutsHist_->SetBinContent(allBinCounter, c->nEvtPassed);
    eventCutsHist_->SetBinError(allBinCounter, sqrt(c->nEvtPassedErr2));
    eventCutsHist_->GetXaxis()->SetBinLabel(allBinCounter, (*it).c_str());
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
    eventCutsEfficHist_->SetBinContent(allBinCounter, effAbs);
    if(!std::isnan(effAbsErr))
      eventCutsEfficHist_->SetBinError(allBinCounter, effAbsErr);
    else
      eventCutsEfficHist_->SetBinError(allBinCounter, 0.0);
    eventCutsEfficHist_->GetXaxis()->SetBinLabel(allBinCounter,(*it).c_str());
    if(isSkimCut(*c))
    {
      checkOverflow(savedEventsPassingCuts.get(),c->nEvtPassed);
      savedEventsPassingCuts->SetBinContent(skimBinCounter, c->nEvtPassed);
      savedEventsPassingCuts->SetBinError(skimBinCounter, sqrt(c->nEvtPassedErr2));
      savedEventsPassingCuts->SetBinEntries(skimBinCounter, c->nEvtPassedBeforeWeight);
      ++skimBinCounter;
    }

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
    ++allBinCounter;
  }

  // Write optimization histograms
  if (optimizeName_cut_.size())
  {
    // now, you call this function explicitly, as in the makeOptCutFile main cc
    //#ifdef CREATE_OPT_CUT_FILE
    //      STDOUT("write opt cut file");
    createOptCutFile();
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

  eventCuts_->Write(); // write here, since WriteCutHistos is called before WriteCutEfficFile
  eventCutsHist_->Write();
  eventCutsEfficHist_->Write();
  // Any failure mode to implement?
  return ret;
} // writeCutEffFile


bool baseClass::sortCuts(const cut& X, const cut& Y)
{
  return X.id < Y.id;
}


vector<string> baseClass::split(const string& s)
{
  istringstream iss(s);
  vector<string> ret( ( std::istream_iterator<string>( iss ) ), std::istream_iterator<string>() );

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

double baseClass::getInfoFromHist(const std::string& fileName, const std::string& histName, int bin, bool getError)
{
  double NBeforeSkim = -999;

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
    auto hCount1 = f->Get<TH1D>(s3.c_str());
    auto hCount2 = f->Get<TH1F>(s3.c_str());
    if(!hCount1 && !hCount2) {
      hCount1 = f->Get<TH1D>(s2.c_str());
      hCount2 = f->Get<TH1F>(s2.c_str());
    }
    if(!hCount1 && !hCount2) {
      hCount1 = f->Get<TH1D>(s1.c_str());
      hCount2 = f->Get<TH1F>(s1.c_str());
    }
    if(!hCount1 && !hCount2) {
      STDOUT("Skim filter histogram not found. Will assume skim was not made for ALL files.");
      skimWasMade_ = false;
      return NBeforeSkim;
    }
    else if(hCount1)
      NBeforeSkim =  getError ? hCount1->GetBinError(bin) : hCount1->GetBinContent(bin);
    else
      NBeforeSkim = getError ? hCount2->GetBinError(bin) : hCount2->GetBinContent(bin);
  }
  else
  {
    auto hCount = f->Get<TH1D>(histName.c_str());
    if(!hCount)
    {
      STDOUT("ERROR: Did not find specified hist named: '" << histName << "'. Cannot extract info. Quitting");
      exit(-1);
    }
    NBeforeSkim = getError ? hCount->GetBinError(bin) : hCount->GetBinContent(bin);
  }

  return NBeforeSkim;
}

double baseClass::getGlobalInfoNstart(const std::string& fileName)
{
  STDOUT(fileName);
  double initialEvents = getInfoFromHist(fileName, "EventCounter", 1);
  if(!skimWasMade_)
    initialEvents = getTreeEntries(fileName);
  return initialEvents;
}

double baseClass::getSumGenWeights(const std::string& fileName)
{
  double sumGenWeights = getInfoFromHist(fileName, "EventCounter", 3);
  if(!skimWasMade_)
    sumGenWeights = getSumWeightFromRunsTree(fileName, "genEventSumw");
  return sumGenWeights;
}

double baseClass::getSumGenWeightSqrs(const std::string& fileName)
{
  double sumGenWeightSqrs = pow(getInfoFromHist(fileName, "EventCounter", 3, true), 2); // need sum(w^2)
  if(!skimWasMade_)
    sumGenWeightSqrs = getSumWeightFromRunsTree(fileName, "genEventSumw2");
  return sumGenWeightSqrs;
}

double baseClass::getSumTopPtWeights(const std::string& fileName)
{
  return getInfoFromHist(fileName, "EventCounter", 4);
}

double baseClass::getTreeEntries(const std::string& fName)
{
  auto chain = std::unique_ptr<TChain>(new TChain("Events"));
  int retVal = chain->AddFile(fName.c_str(), -1);
  if(!retVal)
  {
    STDOUT("ERROR: Something went wrong. Could not find TTree 'Events' in the inputfile '" << fName << "'. Quit here.");
    exit(-2);
  }
  return chain->GetEntries();
}

double baseClass::getSumWeightFromRunsTree(const std::string& fName, const std::string& weightName, int index)
{
  if(index < 0)
    return getSumArrayFromRunsTree(fName, weightName, false)[0];
  else
    return getSumArrayFromRunsTree(fName, weightName, true)[index];
}

template <typename T> std::shared_ptr<T> baseClass::getSavedObjectFromFile(const std::string& fileName, const std::string& histName)
{
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
  auto hist = f->Get<T>(("savedHists/"+histName).c_str());
  if(hist)
    hist->SetDirectory(0);
  return std::shared_ptr<T>(hist);
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
  // we have to have the histogram or the Runs tree available
  auto histFromFile = getSavedObjectFromFile<TH1>(fileName, "LHEPdfSumw");
  if(histFromFile)
  {
    lhePdfSumwArr.resize(histFromFile->GetNbinsX());
    for(unsigned int bin = 1; bin < histFromFile->GetNbinsX(); ++bin)
      lhePdfSumwArr[bin-1] = histFromFile->GetBinContent(bin);
  }
  else
    lhePdfSumwArr = getSumArrayFromRunsTree(fileName, "LHEPdfSumw", true);

  std::shared_ptr<TH1D> lhePdfSumwHist = dynamic_pointer_cast<TH1D>(findSavedHist("LHEPdfSumw"));
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

void baseClass::saveEventsPassingCuts(const std::string& fileName)
{
  STDOUT("saveEventsPassingCuts");
  // if there's no hist in the file, that's not a problem, necessarily. could be a postProc nano file.
  //  but other files should have them
  // if no hist in file, then fine, we can make the profile later (like in readCutFile where it was originally made)
  //  if there is a hist in the file, then it should be added to any existing eventsPassingCuts hist in savedHists
  //    the first hist read can become the saved hist (or a clone of it)
  auto histFromFile = getSavedObjectFromFile<TProfile>(fileName, "EventsPassingSkimCuts");
  if(histFromFile)
  {
    auto eventsPassingCutsProf = dynamic_pointer_cast<TProfile>(findSavedHist("EventsPassingSkimCuts"));
    if(!eventsPassingCutsProf)
    {
      gDirectory->cd();
      histsToSave_.push_back(std::shared_ptr<TProfile>(new TProfile()));
      eventsPassingCutsProf = dynamic_pointer_cast<TProfile>(histsToSave_.back());
      eventsPassingCutsProf->SetDirectory(0); // very important
      eventsPassingCutsProf->Sumw2();
      eventsPassingCutsProf->SetNameTitle(histFromFile->GetName(), histFromFile->GetTitle());
      eventsPassingCutsProf->SetBins(histFromFile->GetNbinsX(), histFromFile->GetXaxis()->GetXmin(), histFromFile->GetXaxis()->GetXmax());
      histFromFile->GetXaxis()->Copy(*eventsPassingCutsProf->GetXaxis());
    }
    eventsPassingCutsProf->Add(histFromFile.get());
  }
}

void baseClass::FillUserHist(const std::string& nameAndTitle, Double_t value, Double_t weight, std::string selection)
{
  if(selection!="" && haveSystematics()) {
    map<std::string , std::unique_ptr<TH2> >::iterator nh_h = user1DHistsWithSysts_.find(std::string(nameAndTitle));
    if( nh_h == user1DHistsWithSysts_.end() ) {
      STDOUT("ERROR: trying to fill histogram wth systs "<<nameAndTitle<<" that was not defined.");
      exit(-4);
    }
    else {
      // systematics
      const auto selectionItr = std::find(orderedSystCutNames_.begin(), orderedSystCutNames_.end(), selection);
      if(selectionItr==orderedSystCutNames_.end()) {
        STDOUT("ERROR: failed to find selection=" << selection << " in orderedSystCutNames=");
        for(auto& cutName : orderedSystCutNames_)
          cout << cutName << ", ";
        cout << endl;
        STDOUT("Cannot fill hist. Exiting.");
        exit(-9);
      }
      float selectionBinCoord = 0.5+int(selectionItr-orderedSystCutNames_.begin());
      unsigned int selectionBin = currentSystematicsHist_->GetXaxis()->FindFixBin(selectionBinCoord);
      for(unsigned int yBin = 1; yBin <= currentSystematicsHist_->GetNbinsY(); ++yBin) {
        float systWeight = currentSystematicsHist_->GetBinContent(selectionBin, yBin);
        float yBinCoord = currentSystematicsHist_->GetYaxis()->GetBinCenter(yBin);
        if(systWeight != 0)
          nh_h->second->Fill(value, yBinCoord, systWeight*weight);
      }
    }
  }
  else {
    map<std::string , std::unique_ptr<TH1> >::iterator nh_h = userTH1s_.find(std::string(nameAndTitle));
    if( nh_h == userTH1s_.end() ) {
      map<std::string , std::unique_ptr<TH2> >::iterator nh_h = user1DHistsWithSysts_.find(std::string(nameAndTitle));
      if( nh_h != user1DHistsWithSysts_.end() ) {
        STDOUT("ERROR: trying to fill histogram which has systs "<<nameAndTitle<<" without passing the cut corresponding to the selection to FillUserTH1D().");
        exit(-4);
      }
      else {
        STDOUT("ERROR: trying to fill histogram "<<nameAndTitle<<" that was not defined.");
        exit(-4);
      }
    }
    else {
      nh_h->second->Fill(value, weight);
    }
  }
}
void baseClass::FillUserHist(const std::string& nameAndTitle, TTreeReaderValue<double>& reader, Double_t weight, std::string selection)
{
  FillUserHist(nameAndTitle, *reader, weight);
}

void baseClass::CreateAndFillUserTH2D(const std::string& nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup,  Double_t value_x,  Double_t value_y, Double_t weight)
{
  map<std::string , std::unique_ptr<TH2> >::iterator nh_h = userTH2s_.find(std::string(nameAndTitle));
  if( nh_h == userTH2s_.end() )
    {
      std::unique_ptr<TH2D> h(new TH2D(nameAndTitle.c_str(), nameAndTitle.c_str(), nbinsx, xlow, xup, nbinsy, ylow, yup));
      h->Sumw2();
      h->SetDirectory(0);
      userTH2s_[std::string(nameAndTitle)] = std::move(h);
      h->Fill(value_x, value_y, weight);
    }
  else
    {
      nh_h->second->Fill(value_x, value_y, weight);
    }
}

void baseClass::CreateUserTH2D(const std::string& nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup)
{
  map<std::string , std::unique_ptr<TH2> >::iterator nh_h = userTH2s_.find(std::string(nameAndTitle));
  if( nh_h == userTH2s_.end() )
    {
      std::unique_ptr<TH2D> h(new TH2D(nameAndTitle.c_str(), nameAndTitle.c_str(), nbinsx, xlow, xup, nbinsy, ylow, yup));
      h->Sumw2();
      h->SetDirectory(0);
      userTH2s_[std::string(nameAndTitle)] = std::move(h);
    }
  else
    {
      STDOUT("ERROR: trying to define already existing histogram "<<nameAndTitle);
    }
}

void baseClass::CreateUserTH2D(const std::string& nameAndTitle, Int_t nbinsx, Double_t * x, Int_t nbinsy, Double_t * y )
{
  map<std::string , std::unique_ptr<TH2> >::iterator nh_h = userTH2s_.find(std::string(nameAndTitle));
  if( nh_h == userTH2s_.end() )
    {
      std::unique_ptr<TH2D> h(new TH2D(nameAndTitle.c_str(), nameAndTitle.c_str(), nbinsx, x, nbinsy, y ));
      h->Sumw2();
      h->SetDirectory(0);
      userTH2s_[std::string(nameAndTitle)] = std::move(h);
    }
  else
    {
      STDOUT("ERROR: trying to define already existing histogram "<<nameAndTitle);
    }
}

void baseClass::FillUserTH2D(const std::string& nameAndTitle, Double_t value_x,  Double_t value_y, Double_t weight)
{
  map<std::string , std::unique_ptr<TH2> >::iterator nh_h = userTH2s_.find(std::string(nameAndTitle));
  if( nh_h == userTH2s_.end() )
    {
      STDOUT("ERROR: trying to fill histogram "<<nameAndTitle<<" that was not defined.");
      exit(-4);
    }
  else
    {
      nh_h->second->Fill(value_x, value_y, weight);
    }
}
void baseClass::FillUserTH2D(const std::string& nameAndTitle, TTreeReaderValue<double>& xReader, TTreeReaderValue<double>& yReader, Double_t weight)
{
  FillUserTH2D(nameAndTitle, *xReader, *yReader, weight);
}


void baseClass::FillUserTH2DLower(const std::string& nameAndTitle, Double_t value_x,  Double_t value_y, Double_t weight)
{
  map<std::string , std::unique_ptr<TH2> >::iterator nh_h = userTH2s_.find(std::string(nameAndTitle));
  if( nh_h == userTH2s_.end() )
    {
      STDOUT("ERROR: trying to fill histogram "<<nameAndTitle<<" that was not defined.");
      exit(-4);
    }
  else
  {
    TH2 * hist = nh_h->second.get();
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


void baseClass::CreateAndFillUserTH3D(const std::string& nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup, Int_t nbinsz, Double_t zlow, Double_t zup,  Double_t value_x,  Double_t value_y, Double_t z, Double_t weight)
{
  map<std::string , std::unique_ptr<TH3> >::iterator nh_h = userTH3s_.find(std::string(nameAndTitle));
  if( nh_h == userTH3s_.end() )
    {
      std::unique_ptr<TH3D> h(new TH3D(nameAndTitle.c_str(), nameAndTitle.c_str(), nbinsx, xlow, xup, nbinsy, ylow, yup, nbinsz, zlow, zup));
      h->Sumw2();
      h->SetDirectory(0);
      h->Fill(value_x, value_y, weight);
      userTH3s_[std::string(nameAndTitle)] = std::move(h);
    }
  else
    {
      nh_h->second->Fill(value_x, value_y, weight);
    }
}

void baseClass::CreateUserTH3D(const std::string& nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup, Int_t nbinsy, Double_t ylow, Double_t yup, Int_t nbinsz, Double_t zlow, Double_t zup)
{
  map<std::string , std::unique_ptr<TH3> >::iterator nh_h = userTH3s_.find(std::string(nameAndTitle));
  if( nh_h == userTH3s_.end() )
    {
      std::unique_ptr<TH3D> h(new TH3D(nameAndTitle.c_str(), nameAndTitle.c_str(), nbinsx, xlow, xup, nbinsy, ylow, yup, nbinsz, zlow, zup));
      h->Sumw2();
      h->SetDirectory(0);
      userTH3s_[std::string(nameAndTitle)] = std::move(h);
    }
  else
    {
      STDOUT("ERROR: trying to define already existing histogram "<<nameAndTitle);
    }
}
void baseClass::CreateUserTH3D(const std::string& nameAndTitle, Int_t nbinsx, Double_t * x, Int_t nbinsy, Double_t * y, Int_t nbinsz, Double_t * z)
{
  map<std::string , std::unique_ptr<TH3> >::iterator nh_h = userTH3s_.find(std::string(nameAndTitle));
  if( nh_h == userTH3s_.end() )
    {
      std::unique_ptr<TH3D> h(new TH3D(nameAndTitle.c_str(), nameAndTitle.c_str(), nbinsx, x, nbinsy, y, nbinsz, z ));
      h->Sumw2();
      h->SetDirectory(0);
      userTH3s_[std::string(nameAndTitle)] = std::move(h);
    }
  else
    {
      STDOUT("ERROR: trying to define already existing histogram "<<nameAndTitle);
    }
}

void baseClass::FillUserTH3D(const std::string& nameAndTitle, Double_t value_x,  Double_t value_y, Double_t value_z, Double_t weight)
{
  map<std::string , std::unique_ptr<TH3> >::iterator nh_h = userTH3s_.find(std::string(nameAndTitle));
  if( nh_h == userTH3s_.end() )
    {
      STDOUT("ERROR: trying to fill histogram "<<nameAndTitle<<" that was not defined.");
      exit(-4);
    }
  else
    {
      nh_h->second->Fill(value_x, value_y, value_z, weight);
    }
}
void baseClass::FillUserTH3D(const std::string& nameAndTitle, TTreeReaderValue<double>& xReader, TTreeReaderValue<double>& yReader, TTreeReaderValue<double>& zReader, Double_t weight)
{
  FillUserTH3D(nameAndTitle, *xReader, *yReader, *zReader, weight);
}

void baseClass::CreateUserTProfile(const std::string& nameAndTitle, Int_t nbinsx, Double_t xlow, Double_t xup)
{
  map<std::string , std::unique_ptr<TProfile> >::iterator nh_h = userTProfiles_.find(nameAndTitle);
  if( nh_h == userTProfiles_.end() )
    {
      std::unique_ptr<TProfile> h(new TProfile(nameAndTitle.c_str(), nameAndTitle.c_str(), nbinsx, xlow, xup));
      h->Sumw2();
      h->SetDirectory(0);
      userTProfiles_[std::string(nameAndTitle)] = std::move(h);
    }
  else
    {
      STDOUT("ERROR: trying to define already existing histogram "<<nameAndTitle);
    }
}
void baseClass::FillUserTProfile(const std::string& nameAndTitle, Double_t x, Double_t y, Double_t weight)
{
  map<std::string , std::unique_ptr<TProfile> >::iterator nh_h = userTProfiles_.find(nameAndTitle);
  if( nh_h == userTProfiles_.end() )
    {
      STDOUT("ERROR: trying to fill histogram "<<nameAndTitle<<" that was not defined.");
      exit(-4);
    }
  else
    {
      nh_h->second->Fill(x, y, weight);
    }
}


bool baseClass::writeUserHistos()
{

  bool ret = true;
  output_root_->cd();

  for (map<std::string, std::unique_ptr<TH1> >::iterator uh_h = userTH1s_.begin(); uh_h != userTH1s_.end(); uh_h++)
    {
      output_root_->cd();
      uh_h->second->Write();
    }
  for (map<std::string, std::unique_ptr<TH2> >::iterator uh_h = userTH2s_.begin(); uh_h != userTH2s_.end(); uh_h++)
    {
      //      STDOUT("uh_h = "<< uh_h->first<<" "<< uh_h->second );
      output_root_->cd();
      uh_h->second->Write();
    }
  for (map<std::string, std::unique_ptr<TH2> >::iterator uh_h = user1DHistsWithSysts_.begin(); uh_h != user1DHistsWithSysts_.end(); uh_h++)
    {
      //      STDOUT("uh_h = "<< uh_h->first<<" "<< uh_h->second );
      output_root_->cd();
      uh_h->second->Write();
    }
  for (map<std::string, std::unique_ptr<TH3> >::iterator uh_h = userTH3s_.begin(); uh_h != userTH3s_.end(); uh_h++)
    {
      output_root_->cd();
      uh_h->second->Write();
    }
  for (map<std::string, std::unique_ptr<TProfile> >::iterator uh_h = userTProfiles_.begin(); uh_h != userTProfiles_.end(); uh_h++)
    {
      output_root_->cd();
      uh_h->second->Write();
    }
  // Any failure mode to implement?
  return ret;
}

float baseClass::getSkimPreCutValue(const string& s)
{
  const auto& cc = preCutName_cut_.find(s);
  if( cc == preCutName_cut_.end() )
  {
    STDOUT("getSkimPreCutValue: (" << s << "): INFO -- did not find the precut string in the map!");
    return 0;
  }
  const auto& c = cc->second;
  if(c->value1 == -999) STDOUT("ERROR: value1 of preliminary cut "<<s<<" was not provided.");
  STDOUT("getSkimPreCutValue: (" << s << "): INFO -- found the precut string in the map with value: " << c->value1);
  return (c->value1);
  return getPreCutValue1(s);
}

void baseClass::fillSkimTree()
{
  tree_->GetEntry(readerTools_->GetCurrentEntry());
  skim_tree_->Fill();
  NAfterSkim_++;

  return;
}

void baseClass::fillReducedSkimTree()
{
  tree_->GetEntry(readerTools_->GetCurrentEntry());
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
  checkOverflow(hCount_,sumGenWeights_);
  checkOverflow(hCount_,sumTopPtWeights_);
  hCount_->SetBinContent(1,nEntTot);
  hCount_->SetBinContent(2,NAfterSkim_);
  hCount_->SetBinContent(3,sumGenWeights_);
  hCount_->SetBinError(3,sqrt(sumGenWeightSqrs_));
  hCount_->SetBinContent(4,sumTopPtWeights_);
  hCount_->Write();
  for(auto& hist : histsToSave_)
    hist->Write();

  skim_file_->cd();
  skim_file_->cd("rootTupleTree");
  if ( GetTreeEntries() == 0 )
    tree_ -> CloneTree(0) -> Write("tree");
  else
    skim_tree_ -> Write("tree", TObject::kOverwrite);

  // Any failure mode to implement?
  return ret;
}

bool baseClass::writeReducedSkimTree()
{
  bool ret = true;

  if(!produceReducedSkim_) return ret;

  reduced_skim_file_->cd();
  reduced_skim_file_->cd("rootTupleTree");
  reduced_skim_tree_->Write("", TObject::kOverwrite);

  reduced_skim_file_->cd();
  TDirectory *dir1 = reduced_skim_file_->mkdir("savedHists");
  reduced_skim_file_->cd("savedHists");
  Long64_t nEntTot = (skimWasMade_ ? NBeforeSkim_ : GetTreeEntries() );
  //FIXME topPtWeight
  checkOverflow(hReducedCount_,nEntTot);
  checkOverflow(hReducedCount_,NAfterReducedSkim_);
  checkOverflow(hReducedCount_,sumGenWeights_);
  checkOverflow(hReducedCount_,sumTopPtWeights_);
  hReducedCount_->SetBinContent(1,nEntTot);
  hReducedCount_->SetBinContent(2,NAfterReducedSkim_);
  hReducedCount_->SetBinContent(3,sumGenWeights_);
  hReducedCount_->SetBinError(3,sqrt(sumGenWeightSqrs_));
  hReducedCount_->SetBinContent(4,sumTopPtWeights_);
  hReducedCount_->Write();
  for(auto& hist : histsToSave_)
    hist->Write();

  // Any failure mode to implement?
  return ret;
}

bool baseClass::passJSON (int this_run, int this_lumi, bool this_is_data ) {
  
  if ( !this_is_data     ) return 1;
  if ( !jsonFileWasUsed_ ) {
    STDOUT( "ERROR: baseClass::passJSON invoked when running on data, but no JSON file was specified!" );
    exit(-1);
  }
  
  return jsonParser_.isAGoodLumi ( this_run, this_lumi );
  
}

void baseClass::getTriggers(Long64_t entry) {
  //FIXME deal with prescale map
  //triggerPrescaleMap_.clear();
  if(triggerNames_.empty()) {
    for(unsigned int i=0; i<tree_->GetListOfBranches()->GetEntries(); ++i) {
      TBranch* branch = static_cast<TBranch*>(tree_->GetListOfBranches()->At(i));
      std::string branchName = branch->GetName();
      if(branchName.find("HLT_")!=std::string::npos) {
        triggerNames_.insert(branchName);
      }
    }
  }
}

void baseClass::printTriggers(){
  std::unordered_set<std::string>::iterator i     = triggerNames_.begin();
  std::unordered_set<std::string>::iterator i_end = triggerNames_.end();
  STDOUT( "Triggers: ")
    for (; i != i_end; ++i) {
      bool decision = readerTools_->ReadValueBranch<Bool_t>(i->c_str());
      std::cout << "\tfired? " << decision <<"\t\"" << *i << "\"" << std::endl;
    }
}

void baseClass::printFiredTriggers()
{
  std::unordered_set<std::string>::iterator i     = triggerNames_.begin();
  std::unordered_set<std::string>::iterator i_end = triggerNames_.end();
  STDOUT( "Fired triggers: ");
  for (; i != i_end; ++i)
  {
    if(readerTools_->ReadValueBranch<Bool_t>(i->c_str()))
      STDOUT("\t\"" << *i << "\"" );
  }
}

bool baseClass::triggerExists ( const char* name ) {
  std::unordered_set<std::string>::iterator i = triggerNames_.find ( name ) ;
  if ( i == triggerNames_.end())
    return false;
  return true;
}

bool baseClass::triggerFired ( const char* name ) {
  //if (!triggerExists(name))
  //{
  //  printTriggers();
  //  STDOUT("ERROR: could not find trigger " << name << " in triggerNames_!");
  //  exit(-1);
  //}
  return readerTools_->ReadValueBranch<Bool_t>(name);
}

int baseClass::triggerPrescale ( const char* name ) { 
  std::map<std::string, int>::iterator i = triggerPrescaleMap_.find ( name ) ;
  if ( i == triggerPrescaleMap_.end() )
  {
    //printTriggers();
    //STDOUT("ERROR: could not find trigger " << name << " in triggerPrescaleMap_ after attempting to match by prefix!");
    //exit(-1);
    //FIXME
    return 1;
  }
  return i->second;
}

void baseClass::fillTriggerVariable ( const char * hlt_path, const char* variable_name, int extraPrescale ) { 
  //int prescale = triggerPrescale(hlt_path);
  //prescale*=extraPrescale;
  float prescale = 1;
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

  optFile << "\t";
  for (int i=0;i<optimizeName_cut_.size();++i)
  {
    optFile << optimizeName_cut_[i].variableName;
    if(optimizeName_cut_[i].testgreater)
      optFile << " > \t";
    else
      optFile << " < \t";
  }
  optFile << endl;

  // Add code for printing histogram output
  int Nbins=h_optimizer_->GetNbinsX();
  for (int i=0;i<Nbins;++i)
  {
    std::vector<int> cutindex;
    // cutindex will store histogram bin as a series of integers
    // 12345 = {1,2,3,4,5}, etc.

    optFile << i;
    for (int j=Nbins/nOptimizerCuts_;j>=1;j/=nOptimizerCuts_)
    {
      cutindex.push_back((i/j)%nOptimizerCuts_);
    }  // for (int j=(int)log10(Nbins);...)

    for (unsigned int j=0;j<cutindex.size();++j)
    {
      if (optimizeName_cut_[j].testgreater==true)
        optFile <<"\t"<<optimizeName_cut_[j].minvalue+optimizeName_cut_[j].increment*cutindex[j];
      //I'm not sure this is how I implemented the < cut; need to check.
      else
        optFile <<"\t"<<optimizeName_cut_[j].maxvalue-optimizeName_cut_[j].increment*cutindex[j];
    } //for (unsigned int j=0;...)
    optFile << endl;
    //optFile <<"\t Entries = "<<h_optimizer_->GetBinContent(i+1)<<endl;

  } // for (int i=0;...)
}

bool baseClass::isData() {
  if(GetCurrentEntry() > 0)
    return isData_;

  isData_ = true;
  if(tree_->GetBranch("isData")) {
    if(readerTools_->ReadValueBranch<Bool_t>("isData") < 1)
      isData_ = false;
  }
  // if no isData branch (like in nanoAOD output), check for Weight or genWeight branches
  else if(tree_->GetBranch("Weight") || tree_->GetBranch("genWeight"))
    isData_ = false;
  return isData_;
}

void baseClass::resetSkimTreeBranchAddress(const std::string& branchName, void* addr) {
  TBranch* branch = skim_tree_->FindBranch(branchName.c_str());
  branch->SetAddress(addr);
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
    int limit = std::numeric_limits<int>::max();
    if(binContent>limit) {
      stringStream << "ERROR: binContent=" << binContent << " will overflow this TH1I bin in histo: " << hist->GetName() << "! Quitting.";
      STDOUT(stringStream.str());
      exit(-3);
    }
  }
  else if(hist->InheritsFrom("TH1D")) {
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

shared_ptr<TH1> baseClass::findSavedHist(string histName)
{
  for(auto& hist : histsToSave_)
  {
    if(std::string(hist->GetName()) == histName)
      return hist;
  }
  return nullptr;
}

shared_ptr<TProfile> baseClass::makeNewEventsPassingSkimCutsProfile(const shared_ptr<TProfile> prevProfFromFile) {
  vector<string> skimCutNames;
  for(auto& cutName : orderedCutNames_) {
    if(isSkimCut(*cutName_cut_.find(cutName)->second))
      skimCutNames.push_back(cutName);
  }
  int nBinsInherited = 1;
  if(skimWasMade_)
    nBinsInherited++;
  if(prevProfFromFile)
    nBinsInherited = prevProfFromFile->GetNbinsX();
  int skimCutSize = skimCutNames.size();
  auto profToRet = std::shared_ptr<TProfile>(new TProfile("TMPEventsPassingCuts","Events Passing Skim Cuts",skimCutSize+nBinsInherited,0,skimCutSize+nBinsInherited));
  profToRet->SetDirectory(0); // very important
  profToRet->Sumw2();
  if(prevProfFromFile) {
    for(int i=1; i<=nBinsInherited; ++i) {
      profToRet->GetXaxis()->SetBinLabel(i, prevProfFromFile->GetXaxis()->GetBinLabel(i));
      profToRet->SetBinContent(i,           prevProfFromFile->GetBinContent(i)*prevProfFromFile->GetBinEntries(i));
      profToRet->SetBinError(i,             sqrt(prevProfFromFile->GetBinSumw2()->At(i)));
      profToRet->SetBinEntries(i,           prevProfFromFile->GetBinEntries(i));
    }
  }
  else {
    profToRet->GetXaxis()->SetBinLabel(1, "NoCuts");
    if(skimWasMade_)
      profToRet->GetXaxis()->SetBinLabel(2, "Skim");
  }
  // label the rest of the bins with just the current skim cuts
  int skimBinCounter = nBinsInherited+1;
  for(auto& cutName : skimCutNames) {
    int i = skimBinCounter;
    profToRet->GetXaxis()->SetBinLabel(skimBinCounter,cutName.c_str());
    ++skimBinCounter;
  }
  return profToRet;
}
