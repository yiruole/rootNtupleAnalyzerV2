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
  Object( Collection& collection, short raw_index, Long64_t current_entry = -1);
  Object( Collection& collection, short raw_index, const char* name, Long64_t current_entry = -1);

  Object( Collection& collection, short raw_index,  short trigObj_index, Long64_t current_entry = -1);
  Object( Collection& collection, short raw_index,  short trigObj_index, const char* name, Long64_t current_entry = -1);
  ~Object();
  
  const char* Name() const { return m_name; }
  virtual short GetRawIndex() { return m_raw_index; }
  
  virtual float & Pt()  = 0;
  virtual float & Phi() = 0;
  virtual float & Eta() = 0;

  virtual float EnergyResScaleFactor() { return 1.0; }
  virtual float EnergyRes           () { return -1.0; }
  virtual float EnergyScaleFactor   () { return 1.0; } 
  virtual float EnergyResScaleError () { return 0.0; }
  
  virtual bool   PassUserID ( ID id, bool verbose ) = 0;
    
  float DeltaR     ( Object * other_object );
  float DeltaPhi   ( Object * other_object );
  float DeltaPt    ( Object * other_object );
  float Phi_mpi_pi ( float x ); 

  bool IsGenEBFiducial() ;
  bool IsGenEEFiducial() ;
  bool IsGenElectronFiducial() ;
  bool IsMuonFiducial() ;

  bool IsNULL() ;

  template <class AnotherObject>
    bool MatchByDR ( CollectionPtr c, AnotherObject & best_match, float max_dr ) { 
      short size = c -> GetSize();
      float min_dr = 9999.;
      bool match = false;
      for (short i = 0; i < size ; ++i){
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
      short size = c -> GetSize();
      double min_dR = 9999.;
      bool match = false;
      for (short i = 0; i < size ; ++i){
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

 protected:

  Collection * m_collection;
  short m_raw_index;
  short m_trigObj_index;
  const char * m_name;

};



#endif 
