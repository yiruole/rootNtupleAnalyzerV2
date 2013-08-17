#ifndef EVENT_LIST_HELPER
#define EVENT_LIST_HELPER

#include <map>
#include <string>
#include <vector>

class EventListHelper {
  
 public:
  EventListHelper();
  ~EventListHelper();
  
  void addFileToList  ( const char * file_name );
  void addEventToList ( int run, int lumi, int event );
  bool eventInList(int run, int lumi, int event );
  void printEventList();

 private:

  std::vector<std::string> split(const std::string& s, const std::string& delim, const bool keep_empty);
  
  struct EventKey { 
    int run  ;
    int lumi ;
    int event;
    bool operator<(EventKey const& right) const {
      if (run  < right.run ) { return true ; }
      if (run  > right.run ) { return false; }
      if (lumi < right.lumi) { return true ; }
      if (lumi > right.lumi) { return false; }
      return event < right.event;
    };
  };
  
  std::map<EventKey, bool> m_map;
  
};


#endif 
