#include "Object.h"
#include <cmath>

Object::~Object(){}

Object::Object():
  m_name ("NO_NAME"),
  m_collection(0),
  m_raw_index ( -1 ),
  m_trigObj_index (-1)
{}

Object::Object(const Object & o):
  m_name(o.m_name),
  m_collection(o.m_collection),
  m_raw_index(o.m_raw_index),
  m_trigObj_index ( o.m_trigObj_index )
{}

Object::Object(Collection & collection, short raw_index, Long64_t current_entry):
  m_name ("NO_NAME"),
  m_collection ( & collection ),
  m_raw_index (raw_index),
  m_trigObj_index (-1)
{}

Object::Object(Collection & collection, short raw_index, short trigObj_index, Long64_t current_entry):
  m_name ("NO_NAME"),
  m_collection ( & collection ),
  m_raw_index (raw_index),
  m_trigObj_index (trigObj_index)
{}

Object::Object(Collection & collection, short raw_index, const char* name, Long64_t current_entry):
  m_name (name),
  m_collection ( & collection ),
  m_raw_index (raw_index),
  m_trigObj_index (-1)
{}

Object::Object(Collection & collection, short raw_index, short trigObj_index, const char* name, Long64_t current_entry):
  m_name (name),
  m_collection ( & collection ),
  m_raw_index (raw_index),
  m_trigObj_index (trigObj_index)
{}

float Object::DeltaR( Object * other_object ) { 
  float deta = Eta() - other_object -> Eta();
  float dphi = DeltaPhi ( other_object );
  float dr = sqrt ( deta * deta + dphi * dphi );
  return dr;
}

float Object::DeltaPhi( Object * other_object ) { 
  return reduceRange(Phi() - other_object -> Phi() );
}

float Object::DeltaPt( Object * other_object ) {
  return Pt() - other_object -> Pt();
}

//float Object::Phi_mpi_pi ( float x ) {
//  float PI = 3.14159265359;
//  while ( x >=  PI ) x -= ( 2*PI );
//  while ( x <  -PI ) x += ( 2*PI );
//  return x;
//}

bool Object::IsGenEBFiducial       () { return bool ( fabs(Eta()) < 1.4442 ); }
bool Object::IsGenEEFiducial       () { return bool ( ( fabs(Eta()) > 1.566 ) && ( fabs(Eta()) < 2.50 ) ); }
bool Object::IsGenElectronFiducial () { return ( IsGenEBFiducial() || IsGenEEFiducial() ); }
bool Object::IsMuonFiducial     () { return bool (fabs(Eta()) < 2.1); }
bool Object::IsNULL             () { return bool ( m_raw_index < 0 ); }

// reduce to [-pi,pi]
template <typename T>
constexpr T Object::reduceRange(T x) {
  constexpr T o2pi = 1. / (2. * M_PI);
  if (std::abs(x) <= T(M_PI))
    return x;
  T n = std::round(x * o2pi);
  return x - n * T(2. * M_PI);
}

//constexpr double deltaPhi(double phi1, double phi2) { return reduceRange(phi1 - phi2); }

//namespace angle_units {
//
//  constexpr long double piRadians(M_PIl);              // M_PIl is long double version of pi
//  constexpr long double degPerRad = 180. / piRadians;  // Degrees per radian
//
//  namespace operators {
//
//    // Angle
//    constexpr long double operator"" _pi(long double x) { return x * piRadians; }
//    constexpr long double operator"" _pi(unsigned long long int x) { return x * piRadians; }
//    constexpr long double operator"" _deg(long double deg) { return deg / degPerRad; }
//    constexpr long double operator"" _deg(unsigned long long int deg) { return deg / degPerRad; }
//    constexpr long double operator"" _rad(long double rad) { return rad * 1.; }
//
//    template <class NumType>
//    inline constexpr NumType convertRadToDeg(NumType radians)  // Radians -> degrees
//    {
//      return (radians * degPerRad);
//    }
//
//    template <class NumType>
//    inline constexpr long double convertDegToRad(NumType degrees)  // Degrees -> radians
//    {
//      return (degrees / degPerRad);
//    }
//  }  // namespace operators
//}  // namespace angle_units
//
//namespace angle0to2pi {
//
//  using angle_units::operators::operator""_pi;
//
//  // make0To2pi constrains an angle to be >= 0 and < 2pi.
//  // This function is a faster version of reco::reduceRange.
//  // In timing tests, it is almost always faster than reco::reduceRange.
//  // It also protects against floating-point value drift over repeated calculations.
//  // This implementation uses multiplication instead of division and avoids
//  // calling fmod to improve performance.
//
//  template <class valType>
//  inline constexpr valType make0To2pi(valType angle) {
//    constexpr valType twoPi = 2._pi;
//    constexpr valType oneOverTwoPi = 1. / twoPi;
//    constexpr valType epsilon = 1.e-13;
//
//    if ((std::abs(angle) <= epsilon) || (std::abs(twoPi - std::abs(angle)) <= epsilon))
//      return (0.);
//    if (std::abs(angle) > twoPi) {
//      valType nFac = trunc(angle * oneOverTwoPi);
//      angle -= (nFac * twoPi);
//      if (std::abs(angle) <= epsilon)
//        return (0.);
//    }
//    if (angle < 0.)
//      angle += twoPi;
//    return (angle);
//  }
//}  // namespace angle0to2pi
//
