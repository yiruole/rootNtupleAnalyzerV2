#include <vector>
#include <unordered_map>
#include <string>
#include <iostream>

// class for the average prescale values over an entire year
// based on brilcalc numbers (June 2023)
class Run2PhotonTriggerPrescales {
  public:
    Run2PhotonTriggerPrescales()
    {
    }
    double LookupPrescale(const std::string year, const std::string& triggerName)
    {
      if(year=="2016preVFP") return prescales2016preVFP.at(triggerName);
      else if(year=="2016postVFP") return prescales2016postVFP.at(triggerName);
      else if(year=="2017") return prescales2017.at(triggerName);
      else if(year=="2018") return prescales2018.at(triggerName);
      else
      {
        std::cout << "ERROR: cannot lookup prescale for trigger: " << triggerName << " for year: " << year << std::endl;
        return -1;
      }
    }
  private:
    std::unordered_map<std::string,double> prescales2016preVFP
    { {"Photon22" , 18817.110413595063},
      {"Photon30" , 4361.903982918845},
      {"Photon36" , 2204.4498446894813},
      {"Photon50" , 1041.5481979037547},
      {"Photon75" , 235.09159636337623},
      {"Photon90" , 119.3997345135344},
      {"Photon120", 57.67833471869751},
      {"Photon175", 1.0}
    };
    std::unordered_map<std::string,double> prescales2016postVFP
    { {"Photon22" , 29092.45531046727},
      {"Photon30" , 7614.771636816898},
      {"Photon36" , 2204.4498446894813},
      {"Photon50" , 3800.435902809001},
      {"Photon75" , 316.8895860489016},
      {"Photon90" , 162.33283231274035},
      {"Photon120", 82.17482260061728},
      {"Photon175", 1.0}
    };
    std::unordered_map<std::string,double> prescales2017
    { {"Photon25" , 30968.042890472476},
      {"Photon33" , 2896.7084694667606},
      {"Photon50" , 1869.88656260226},
      {"Photon75" , 409.0433851046414},
      {"Photon90" , 339.6345236550635},
      {"Photon120", 84.62955045585228},
      {"Photon150", 60.12748639942892},
      {"Photon175", 33.30622307595083},
      {"Photon200", 1.0}
    };
    std::unordered_map<std::string,double> prescales2018
    { {"Photon33" , 25462.774388295096},
      {"Photon50" , 4616.669094598204},
      {"Photon75" , 507.28475874050457},
      {"Photon90" , 508.6821570150963},
      {"Photon120", 127.06961017784332},
      {"Photon150", 125.08480188090338},
      {"Photon175", 62.790153493012376},
      {"Photon200", 1.0}
    };

};
