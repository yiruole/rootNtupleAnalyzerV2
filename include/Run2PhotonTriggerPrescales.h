#include <vector>
#include <unordered_map>
#include <string>
#include <iostream>

// class for the average prescale values over an entire year
// based on brilcalc numbers (Nov. 2019)
class Run2PhotonTriggerPrescales {
  public:
    Run2PhotonTriggerPrescales()
    {
    }
    float LookupPrescale(const int year, const std::string& triggerName)
    {
      if(year==2016) return prescales2016.at(triggerName);
      else if(year==2017) return prescales2017.at(triggerName);
      else if(year==2018) return prescales2018.at(triggerName);
      else
      {
        std::cout << "ERROR: cannot lookup prescale for trigger: " << triggerName << " for year: " << year << endl;
        return -1;
      }
    }
  private:
    std::unordered_map<std::string,float> prescales2016
    { {"Photon22" ,22488.67},
      {"Photon30" ,5435.99},
      {"Photon36" ,2735.88},
      {"Photon50" ,1157.41},
      {"Photon75" ,266.94},
      {"Photon90" ,136.029},
      {"Photon120",66.89},
      {"Photon175",1}
    };
    std::unordered_map<std::string,float> prescales2017
    { {"Photon25" ,31004.77},
      {"Photon33" ,2911.54},
      {"Photon50" ,1871.62},
      {"Photon75" ,409.41},
      {"Photon90" ,339.88},
      {"Photon120",84.70},
      {"Photon150",60.20},
      {"Photon175",33.33},
      {"Photon200",1}
    };
    std::unordered_map<std::string,float> prescales2018
    { {"Photon25" ,32556166.32},
      {"Photon33" ,25463.58},
      {"Photon50" ,4614.91},
      {"Photon75" ,507.28},
      {"Photon90" ,508.68},
      {"Photon120",127.07},
      {"Photon150",125.08},
      {"Photon175",62.79},
      {"Photon200",1}
    };

};
