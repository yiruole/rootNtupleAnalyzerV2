#ifndef EVENT_LIST_HELPER
#define EVENT_LIST_HELPER

//#include <map>
#include <string>
#include <vector>
#include <unordered_set>

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
    bool operator==(const EventKey &other) const
    {
      return (run == other.run
          && lumi == other.lumi
          && event == other.event);
    }
  };

  struct EventKeyHasher
  {
    std::size_t operator()(const EventKey& k) const
    {
      using std::size_t;
      using std::hash;

      return ((hash<int>()(k.run)
            ^ (hash<int>()(k.lumi) << 1)) >> 1)
            ^ (hash<int>()(k.event) << 1);
    }
  };
  
  //std::map<EventKey, bool> m_map;
  std::unordered_set<EventKey,EventKeyHasher> m_set;
  
};


#endif 
