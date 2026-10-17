#include "TauSpinner/Particle.h"
#include <cmath>
#include <iostream>
#include <stdexcept>

int main() try {
  using TauSpinner::Particle;
  for(auto frame : {Particle(0,0,4,8,0), Particle(0,0,-4,8,0),
                    Particle(0,0,0,8,0), Particle(1e-12,0,4,8,0),
                    Particle(1,2,3,8,0)}) {
    Particle p(1,2,3,5,15),original=p;
    p.boostToRestFrame(frame);
    if(!std::isfinite(p.px()+p.py()+p.pz()+p.e()))
      throw std::runtime_error("Nonfinite collinear boost");
    double mass2=p.e()*p.e()-p.px()*p.px()-p.py()*p.py()-p.pz()*p.pz();
    if(std::abs(mass2-11)>1e-10) throw std::runtime_error("Mass not preserved");
    p.boostFromRestFrame(frame);
    if(std::abs(p.px()-original.px())+std::abs(p.py()-original.py())+
       std::abs(p.pz()-original.pz())+std::abs(p.e()-original.e())>1e-10)
      throw std::runtime_error("Boost inverse failed");
  }
  std::cout<<"PASS: collinear/rest/generic boosts, mass shell and inverse\n";
  return 0;
} catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
