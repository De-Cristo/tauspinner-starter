#include "HepMC3/ReaderAsciiHepMC2.h"
#include "HepMC3/GenEvent.h"
#include "HepMC3/GenParticle.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <cmath>

int main(int argc,char** argv) try {
  if(argc!=3) throw std::runtime_error("Usage: readcheck events.hepmc weights.csv");
  HepMC3::ReaderAsciiHepMC2 reader(argv[1]);
  std::ifstream csv(argv[2]);
  if(!csv) throw std::runtime_error("Cannot open CSV");
  std::string line; std::getline(csv,line);
  int n=0;
  while(std::getline(csv,line)) {
    HepMC3::GenEvent event; reader.read_event(event);
    if(reader.failed()) throw std::runtime_error("HepMC ended early");
    for(char& c:line) if(c==',') c=' ';
    std::istringstream row(line); int id; double base,spin;
    if(!(row>>id>>base>>spin)) throw std::runtime_error("Malformed CSV");
    if(id!=n||event.event_number()!=n||event.weights().size()!=2)
      throw std::runtime_error("Event/weight count mismatch");
    if(!event.run_info() || event.run_info()->weight_names()!=
        std::vector<std::string>{"unpolarized","spin_sm"})
      throw std::runtime_error("Named weight definitions lost");
    if(std::abs(event.weights()[0]-base)>1e-10*std::max(1.,std::abs(base))||
       std::abs(event.weights()[1]-base*spin)>1e-10*std::max(1.,std::abs(base*spin)))
      throw std::runtime_error("Serialized weight mismatch");
    int pions=0,taus=0,neutrinos=0;
    for(auto p:event.particles()) if(p->status()==1) {
      pions+=std::abs(p->pid())==211;
      taus+=std::abs(p->pid())==15;
      neutrinos+=std::abs(p->pid())==16;
    }
    if(pions!=2||taus!=0||neutrinos!=2)
      throw std::runtime_error("Wrong stable decay products");
    const auto beams=event.beams();
    if(beams.size()==2 && beams[0]->pid()==22 && beams[1]->pid()==22) {
      auto total=beams[0]->momentum()+beams[1]->momentum();
      auto remaining=total;
      for(auto p:event.particles()) {
        if(p->status()==1) remaining-=p->momentum();
        if(p->pid()==23||p->pid()==2212)
          throw std::runtime_error("Unexpected Z/proton in central photon record");
      }
      if(std::abs(remaining.e())+std::abs(remaining.px())+
          std::abs(remaining.py())+std::abs(remaining.pz())>1e-6*std::max(1.,total.e()))
        throw std::runtime_error("Photon hard-system momentum not conserved");
    }
    ++n;
  }
  HepMC3::GenEvent extra; reader.read_event(extra);
  if(!reader.failed()) throw std::runtime_error("Extra HepMC event");
  std::cout<<"PASS: "<<n<<" events, weights and stable pi nu pairs round trip\n";
  return 0;
} catch(const std::exception& e) {std::cerr<<e.what()<<'\n'; return 1;}
