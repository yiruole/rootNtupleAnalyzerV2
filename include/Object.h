#ifndef OBJECT_H
#define OBJECT_H

#include <ostream> 
#include <iostream>
#include "IDTypes.h"
#include "Collection.h"

#include <TLeaf.h>

class Object {
 public:
  Object();
  Object( const Object & );
  Object( Collection& collection, short raw_index, const char* name);

  Object( Collection& collection, short raw_index,  short trigObj_index, const char* name);
  ~Object();
  
  const std::string Name() const { return m_name; }
  virtual short GetRawIndex() const { return m_raw_index; }
  
  float Pt()  const { return m_pt;  }
  float Eta() const { return m_eta; }
  float Phi() const { return m_phi; }
  float PtOrignal() const { return m_originalPt; }

  void SetPt(float pt) { m_pt = pt; }
  void SetEta(float eta) { m_eta = eta; }
  void SetPhi(float phi) { m_phi = phi; }

  virtual double EnergyResScaleFactor() { return 1.0; }
  virtual double EnergyResScaleFactorFromCorrection(const correction::Correction* correction, const std::string& variation) { return -1.0; }
  virtual double EnergyRes           () { return -1.0; }
  virtual double EnergyResFromCorrection(const correction::Correction* correction) { return -1.0; }
  virtual double EnergyScaleFactor   () { return 1.0; } 
  virtual double EnergyResScaleError () { return 0.0; }
  
  virtual bool   PassUserID ( ID id, bool verbose ) = 0;
    
  float DeltaR     ( Object * other_object );
  float DeltaPhi   ( Object * other_object );
  float DeltaPt    ( Object * other_object );
  template <typename T> constexpr T reduceRange(T x);

  bool IsGenEBFiducial() ;
  bool IsGenEEFiducial() ;
  bool IsGenElectronFiducial() ;
  bool IsMuonFiducial() ;

  bool IsNULL() ;

  template <class AnotherObject>
    bool MatchByDR ( CollectionPtr c, AnotherObject & best_match, float max_dr ) { 
      unsigned short size = c -> GetSize();
      float min_dr = 9999.;
      bool match = false;
      for (unsigned short i = 0; i < size ; ++i){
        AnotherObject constituent = c -> GetConstituent<AnotherObject> ( i );
        float dr = DeltaR ( & constituent );
        if ( dr < max_dr ) { 
          if ( dr < min_dr ) { 
            match = true;
            min_dr = dr;
            best_match = constituent;
          }
        }
      }
      return match;
    }

  template<class AnotherObject>
    bool MatchByDRAndDPt ( CollectionPtr c, AnotherObject & best_match, float max_dr, float max_dpt ) { 
      unsigned short size = c -> GetSize();
      double min_dR = 9999.;
      bool match = false;
      for (unsigned short i = 0; i < size ; ++i){
        AnotherObject constituent = c -> GetConstituent<AnotherObject> ( i );
        float dr = DeltaR ( & constituent );

        if (dr < max_dr) {
          if (dr < min_dR) {
            double dPt = fabs(DeltaPt( & constituent ));
            if (dPt > max_dpt)
              continue;

            match = true;
            min_dR = dr;
            best_match = constituent;
          }
        }
      }

      return match;
    }

  bool operator==(const Object& rhs) const { return this->m_raw_index == rhs.m_raw_index; }

 protected:

  Collection * m_collection;
  short m_raw_index;
  short m_trigObj_index;
  std::string m_name;

 private:
  void initP4();

  float m_pt, m_eta, m_phi;
  float m_originalPt;
};



#endif 
