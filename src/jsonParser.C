#include <iostream>
#include <getopt.h>
#include <vector>
#include <string>
#include <sstream>
#include <fstream>
#include <algorithm>
#include <iterator>
#include <memory>

#include "jsonParser.h"

JSONParser::JSONParser(){}
JSONParser::~JSONParser(){}

std::vector<std::string> JSONParser::split(const std::string& s, const std::string& delim, const bool keep_empty = false) {
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

std::string JSONParser::getFileContent ( const char * file_name ) {
  typedef std::auto_ptr<char> char_ptr;
  
  char_ptr buffer;
  std::string line;
  std::string retval;
  std::ifstream f(file_name);
  if (f.is_open())
  {
    while ( f.good() )
    {
      getline (f,line);
      retval += line ;
    }
    f.close();
  }
  
  else { 
    std::cout << "ERROR: JSON file " << file_name << " does not exist.  Code will crash." << std::endl;
  }

  return retval;
}

int JSONParser::getRunNumber ( std::string & run_number_string ) { 

    int i = 0;
    int length = (int) run_number_string.length();
    bool clean = false;
    
    while ( i < length && !clean){
      if ( run_number_string.compare(0,1,"," ) == 0 ||
	   run_number_string.compare(0,1," " ) == 0 ||
	   run_number_string.compare(0,1,"{" ) == 0 ||
	   run_number_string.compare(0,1,"'" ) == 0 ||
	   run_number_string.compare(0,1,"\"") == 0 ) run_number_string.erase(0,1);
      else clean = true;
      i++;
    }

    i = 0;
    length = (int) run_number_string.length();
    clean = false;

    while ( i < length && !clean){
      
      int pos = run_number_string.length() - 1;

      if ( run_number_string.compare(pos,1,"," ) == 0 ||
	   run_number_string.compare(pos,1," " ) == 0 ||
	   run_number_string.compare(pos,1,"{" ) == 0 ||
	   run_number_string.compare(pos,1,"'" ) == 0 ||
	   run_number_string.compare(pos,1,"\"") == 0 ) run_number_string.erase(pos,1);
      else clean = true;
      i++;
    }

    int run_number = atoi ( run_number_string.c_str());

    return run_number;

}

std::vector < std::pair<int,int> > JSONParser::getLumiRanges ( std::string lumi_ranges_string ) {
  
  std::vector< std::pair <int, int > > lumi_ranges;

  std::vector <std::string> split_lumi_ranges_string = split ( lumi_ranges_string, "]" );

  for (int i = 0 ; i < (int) split_lumi_ranges_string.size() ; ++ i ) {

    std::string lumi_range_string = split_lumi_ranges_string[i];

    int j = 0; 
    int length = (int) lumi_range_string.length();
    bool clean = false;
    
    while ( i < length && !clean){
      if ( lumi_range_string.compare(0,1,"[" ) == 0 ||
	   lumi_range_string.compare(0,1," " ) == 0 ||
	   lumi_range_string.compare(0,1,"," ) == 0 ) lumi_range_string.erase(0,1);
      else clean = true;
      j++;
    }

    std::vector<std::string> v_lumi_range_string = split ( lumi_range_string, "," ) ;

    int range_min = atoi ( v_lumi_range_string[0].c_str() );
    int range_max = atoi ( v_lumi_range_string[1].c_str() );

    lumi_ranges.push_back ( std::pair <int,int>(range_min, range_max ) );

  }

  return lumi_ranges;

}

void JSONParser::addToMap ( int run_number , const std::vector<std::pair<int,int> > & lumi_ranges ) { 

  GoodLumiMapIterator map_entry     = m_good_lumi_map.find ( run_number ) ;
  GoodLumiMapIterator map_entry_end = m_good_lumi_map.end();
  
  if ( map_entry == map_entry_end ) 
    m_good_lumi_map . insert ( GoodLumiMapEntry ( run_number , lumi_ranges ) ) ;
  
  else { 
    std::vector < std::pair <int, int > > * current_lumi_ranges = & (*map_entry).second;
    current_lumi_ranges -> insert ( current_lumi_ranges -> end(), lumi_ranges.begin() , lumi_ranges.end() );
  }
  
}

bool JSONParser::isAGoodLumi ( int run_number, int lumi ) {

  bool decision = false;

  GoodLumiMapIterator map_entry     = m_good_lumi_map.find ( run_number ) ;
  GoodLumiMapIterator map_entry_end = m_good_lumi_map.end();

  if ( map_entry == map_entry_end ) return false;
  
  else { 
    std::vector < std::pair < int, int > > * lumi_ranges = & map_entry -> second;
    std::vector < std::pair < int, int > >::iterator lumi_range     = lumi_ranges -> begin();
    std::vector < std::pair < int, int > >::iterator lumi_range_end = lumi_ranges -> end();
    
    for (; lumi_range != lumi_range_end; ++lumi_range) 
      if ( lumi >= lumi_range -> first && lumi <= lumi_range -> second ) return true;

  }
  
  return decision;

}

void JSONParser::printGoodLumis () { 
  
  
  GoodLumiMapIterator map_entry     = m_good_lumi_map.begin();
  GoodLumiMapIterator map_entry_end = m_good_lumi_map.end();
  
  std::cout << "For JSON file: " << *m_file_name << std::endl;
  std::cout << "Good run/lumi ranges are: " << std::endl;

  for (; map_entry != map_entry_end; ++map_entry ) {
    
    int run_number = map_entry -> first;
    std::vector < std::pair < int, int > > * lumi_ranges = & map_entry -> second;
    std::vector < std::pair < int, int > >::iterator lumi_range     = lumi_ranges -> begin();
    std::vector < std::pair < int, int > >::iterator lumi_range_end = lumi_ranges -> end();
    
    std::cout << run_number << " : ";

    int n_ranges = (int) lumi_ranges -> size();
    int i_range  = 0;

    for (; lumi_range != lumi_range_end; ++lumi_range) {
      int lumi_range_min = lumi_range -> first;
      int lumi_range_max = lumi_range -> second;
      std::cout << "[ " << lumi_range_min << ", " << lumi_range_max << " ]";
      if ( i_range < n_ranges - 1 ) std::cout << ", ";
      i_range ++;
    }

    std::cout << std::endl;
  }

}

void JSONParser::parseJSONFile( std::string * file_name ) {

  m_file_name = file_name;

  std::string file_content = getFileContent ( file_name -> c_str() ) ;

  std::vector <std::string> split_file_content  = split ( file_content, "]]" ) ;
  
  for ( int i = 0 ; i < (int) split_file_content.size() ; ++i ) {
    std::string run_info = split_file_content[i];
    std::vector < std::string > split_run_info = split ( run_info, ":" );

    if ( split_run_info.size() < 2 ) continue;

    std::string run_number_string  = split_run_info[0];
    std::string lumi_ranges_string = split_run_info[1];

    int run_number                                   = getRunNumber  ( run_number_string  ) ;
    std::vector<std::pair < int, int > > lumi_ranges = getLumiRanges ( lumi_ranges_string ) ;

    addToMap ( run_number , lumi_ranges ) ;
    
  }

}
