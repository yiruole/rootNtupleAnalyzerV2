#ifndef JSONPARSER_H
#define JSONPARSER_H

#include <string>
#include <vector>
#include <map>

class JSONParser {

 public:
  JSONParser();
  ~JSONParser();
  
  void parseJSONFile( std::string * file_name );
  bool isAGoodLumi ( int run_number, int lumi );
  void printGoodLumis();

 private:

  typedef std::map < int , std::vector<std::pair < int, int > > > GoodLumiMap;
  typedef std::map < int , std::vector<std::pair < int, int > > >::iterator GoodLumiMapIterator;
  typedef std::pair < int, std::vector < std::pair < int , int > > > GoodLumiMapEntry;

  GoodLumiMap m_good_lumi_map ;
  std::string * m_file_name;
  
  std::vector<std::string> split(const std::string& s, const std::string& delim, const bool keep_empty);
  std::string getFileContent ( const char * file_name );
  int getRunNumber ( std::string & run_number_string ) ;
  std::vector < std::pair<int,int> > getLumiRanges ( std::string lumi_ranges_string ) ;
  void addToMap ( int run_number , const std::vector<std::pair<int,int> > & lumi_ranges ) ;

};

#endif
