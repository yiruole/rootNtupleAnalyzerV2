#include "eventListHelper.h"
#include <fstream>
#include <iostream>
#include <algorithm>
#include <boost/iostreams/filter/gzip.hpp>
#include <boost/iostreams/filtering_stream.hpp>

#include "TFile.h"
#include "TTreeReader.h"
#include "TTreeReaderValue.h"

EventListHelper::EventListHelper(){}
EventListHelper::~EventListHelper(){}


std::vector<std::string> EventListHelper::split(const std::string& s, const std::string& delim, const bool keep_empty = false) {
  std::vector<std::string> result;
    if (delim.empty()) {
        result.push_back(s);
        return result;
    }
    std::string::const_iterator substart = s.begin(), subend;
    while (true) {      
      subend = std::search(substart, s.end(), delim.begin(), delim.end());
      std::string temp(substart, subend);
      if (keep_empty || !temp.empty()) 	result.push_back(temp);
      if (subend == s.end())            break;
      substart = subend + delim.size();
    }
    return result;
}


bool EventListHelper::eventInList(int run, int lumi, int event ){ 
  EventKey key;
  key.run   = run;
  key.lumi  = lumi;
  key.event = event;
  
  //std::map<EventKey, bool>::iterator it     = m_map.find ( key );
  //std::map<EventKey, bool>::iterator it_end = m_map.end();


  //if ( it == it_end ) return false;
  //else return it->second;
  if(m_set.count(key)>0) return true;
  else return false;
  
}

void EventListHelper::addEventToList ( int run, int lumi, int event  ){
  EventKey key;
  key.run   = run;
  key.lumi  = lumi;
  key.event = event;
  //m_map[key] = true;
  m_set.insert(key);
}

void EventListHelper::addFileToList  ( const char * file_name ) { 
  std::string line;
  if(std::string(file_name).find(".gz") != std::string::npos) {
    std::cout << "INFO: Adding gzipped file " << file_name << " to event list...";
    std::ifstream myfile(file_name, std::ios_base::in | std::ios_base::binary);
    try {
      boost::iostreams::filtering_istream in;
      in.push(boost::iostreams::gzip_decompressor());
      in.push(myfile);
      for(std::string str; std::getline(in, str); )
      {
        std::vector<std::string> fields = split ( str, std::string(":") );
        if ( fields.size() != 3 ) continue;
        addEventToList ( atoi ( fields[0].c_str() ),
            atoi ( fields[1].c_str() ),
            atoi ( fields[2].c_str() ) );
      }
    }
    catch(const boost::iostreams::gzip_error& e) {
      std::cout << "ERROR: problem with event list file " << file_name << " Cowardly exiting." << std::endl;
      std::cout << e.what() << '\n';
      exit(-1);
    }
  }
  else if(std::string(file_name).find(".txt") != std::string::npos) {
    std::cout << "INFO: Adding txt file " << file_name << " to event list...";
    std::ifstream myfile (file_name);
    if (myfile.is_open()) {

      while ( myfile.good() ) { 
        getline (myfile,line);
        std::vector<std::string> fields = split ( line, std::string(":") );
        if ( fields.size() != 3 ) continue;
        addEventToList ( atoi ( fields[0].c_str() ),
            atoi ( fields[1].c_str() ),
            atoi ( fields[2].c_str() ) );

      }
      myfile.close();
    }
    else {
      std::cout << "ERROR: could not open event list file " << file_name << " Cowardly exiting." << std::endl;
      exit(-1);
    }
  }
  else {
    std::cout << "ERROR: event list file " << file_name << " does not end with .gz or .txt. We don't know how to handle this.  Cowardly exiting." << std::endl;
    exit(-1);
  }
  if(m_set.size() < 1) {
    std::cout << "ERROR: event list has size < 1.  Did something go wrong when reading it?  Cowardly exiting." << std::endl;
    exit(-1);
  }
  std::cout << "INFO: added " << m_set.size() << " events." << std::endl;
}
  
void EventListHelper::addFileToList  ( const char * file_name, const char * tree_name ) { 
  if(std::string(file_name).find(".root") != std::string::npos) {
    std::cout << "INFO: Adding root file " << file_name << " containing tree named " << tree_name << " to event list...";

    TFile* file = TFile::Open(file_name);
    if(file->IsOpen()) {
      TTreeReader reader(tree_name,file);
      TTreeReaderValue<UInt_t> run(reader,"run"); // aka unsigned int
      TTreeReaderValue<UInt_t> lumi(reader,"lumi"); // aka unsigned int
      TTreeReaderValue<ULong64_t> event(reader,"event"); // aka unsigned long long
      while(reader.Next()) {
        addEventToList (*run, *lumi, *event);
      }
      file->Close();
    }
    else {
      std::cout << "ERROR: could not open event list file " << file_name << " Cowardly exiting." << std::endl;
      exit(-1);
    }
  }
  else {
    std::cout << "ERROR: event list file " << file_name << " does not end with .root. We don't know how to handle this.  Cowardly exiting." << std::endl;
    exit(-1);
  }
  if(m_set.size() < 1) {
    std::cout << "ERROR: event list has size < 1.  Did something go wrong when reading it?  Cowardly exiting." << std::endl;
    exit(-1);
  }
  std::cout << "INFO: added " << m_set.size() << " events." << std::endl;
}

void EventListHelper::printEventList(){
  //std::map<EventKey, bool>::iterator it     = m_map.begin();
  //std::map<EventKey, bool>::iterator it_end = m_map.end();
  
  std::cout << "Events in list: " << std::endl;
  //for (; it != it_end; ++it ){
  //  if (!it -> second) continue;
  //  std::cout << "\t" << it -> first.run << ":" << it -> first.lumi << ":" << it -> first.event << std::endl;
  //}
  for(auto it = m_set.begin(); it != m_set.end(); ++it)
  {
    std::cout << "\t" << it->run << ":" << it->lumi << ":" << it->event << std::endl;
  }
}
