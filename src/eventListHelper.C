#include "eventListHelper.h"
#include <fstream>
#include <iostream>
#include <algorithm>

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
  
  std::map<EventKey, bool>::iterator it     = m_map.find ( key );
  std::map<EventKey, bool>::iterator it_end = m_map.end();

  if ( it == it_end ) return false;
  else return it->second;
  
}

void EventListHelper::addEventToList ( int run, int lumi, int event  ){
  EventKey key;
  key.run   = run;
  key.lumi  = lumi;
  key.event = event;
  m_map[key] = true;
}

void EventListHelper::addFileToList  ( const char * file_name ) { 
  
  std::string line;
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

  else std::cout << "ERROR: event list file " << file_name << " does not exist.  Code will crash." << std::endl;

  
}
  
void EventListHelper::printEventList(){
  std::map<EventKey, bool>::iterator it     = m_map.begin();
  std::map<EventKey, bool>::iterator it_end = m_map.end();
  
  std::cout << "Events in list: " << std::endl;
  for (; it != it_end; ++it ){
    if (!it -> second) continue;
    std::cout << "\t" << it -> first.run << ":" << it -> first.lumi << ":" << it -> first.event << std::endl;
  }
}
