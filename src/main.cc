#include "Pythia8/Pythia.h"
#include "Pythia8Plugins/HepMC3.h"
#include "HepMC3/WriterAsciiHepMC2.h"
#include "TauSpinner/tau_reweight_lib.h"
#include "Tauola/Tauola.h"
#include "LHAPDF/LHAPDF.h"
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <cmath>
#include <sstream>
#include <set>

using TauSpinner::SimpleParticle;
#ifdef SPINNER_PHOTON_API
// Public symbols in the pinned 1.1.9 library, omitted from its installed headers.
namespace TauSpinner {
int initTables(char*, char*, char*);
void ExtraEWparamsSet(double,double,double,double,double,double,double,int);
}
#endif
SimpleParticle simple(const Pythia8::Particle& p) {
  return {p.px(),p.py(),p.pz(),p.e(),p.id()};
}

void check_photon_input(const std::string& path, int requested) {
  std::ifstream file(path);
  if(!file) throw std::runtime_error("Cannot read photon LHE");
  std::string line;
  int events=0;
  while(std::getline(file,line)) {
    if(line.find("<event>")==std::string::npos) continue;
    if(!std::getline(file,line)) throw std::runtime_error("Truncated LHE");
    int nup; std::istringstream header(line);
    if(!(header>>nup)||nup!=4) throw std::runtime_error("Photon input must have four hard particles");
    int photons=0; std::set<int> taus;
    for(int i=0;i<nup;++i) {
      if(!std::getline(file,line)) throw std::runtime_error("Truncated particle record");
      std::istringstream p(line); int id,status,m1,m2,c1,c2; double px,py,pz,e,m,t,spin;
      if(!(p>>id>>status>>m1>>m2>>c1>>c2>>px>>py>>pz>>e>>m>>t>>spin))
        throw std::runtime_error("Malformed particle record");
      if(!std::isfinite(px+py+pz+e+m+t+spin)||e<=0)
        throw std::runtime_error("Nonfinite or nonphysical LHE particle");
      if(status==-1&&id==22) ++photons;
      else if(status==1&&std::abs(id)==15) taus.insert(id);
      else throw std::runtime_error("Not a stable-tau photon input");
    }
    if(photons!=2||taus.size()!=2) throw std::runtime_error("Wrong photon/tau content");
    ++events;
  }
  if(events<requested) throw std::runtime_error("Insufficient LHE events");
}

int main(int argc, char** argv) try {
  if (argc != 6) throw std::runtime_error(
      "Usage: tau-spin CHANNEL(gg|dy) INPUT_LHE(or - for internal DY) OUTPUT_DIR EVENTS SEED");
  std::string channel=argv[1], input=argv[2];
  if (channel!="gg" && channel!="dy") throw std::runtime_error("Unknown channel");
#ifndef SPINNER_PHOTON_API
  if(channel=="gg") throw std::runtime_error("This TauSpinner has no photon API; build with env.sh");
#else
  const char* tables=std::getenv("TAUSPIN_EW_TABLES");
  if(!tables) throw std::runtime_error("Set TAUSPIN_EW_TABLES to the official table.mu/table.down/table.up directory; no fallback weights allowed");
  for(auto name: {"table.mu","table.down","table.up"})
    if(!std::filesystem::is_regular_file(std::filesystem::path(tables)/name))
      throw std::runtime_error(std::string("Missing official EW table: ")+name);
#endif
  int count=std::stoi(argv[4]), seed=std::stoi(argv[5]);
  if (count<1 || seed<1 || seed>=900000000) throw std::runtime_error("Invalid count/seed");
  if(channel=="gg") check_photon_input(input,count);
  std::filesystem::path output(argv[3]);
  if (!std::filesystem::create_directories(output)) throw std::runtime_error("Output already exists");
  Pythia8::Pythia py;
  auto set=[&](std::string s) { if(!py.readString(s)) throw std::runtime_error("Invalid Pythia setting: "+s); };
  set("Random:setSeed = on"); set("Random:seed = "+std::to_string(seed));
  if(input!="-") {
    set("Beams:frameType = 4"); set("Beams:LHEF = "+input);
    // Photon LHE contains no coloured remnants; use resonance decays only.
    set("PartonLevel:all = off");
  } else {
    if(channel!="dy") throw std::runtime_error("gg requires a GAMMA-UPC LHE");
    set("Beams:eCM = 13600."); set("WeakSingleBoson:ffbar2gmZ = on");
    set("23:onMode = off"); set("23:onIfAny = 15");
    set("PhaseSpace:mHatMin = 50.");
    set("PartonLevel:ISR = off"); set("PartonLevel:FSR = off");
    set("PartonLevel:MPI = off");
  }
  set("HadronLevel:Hadronize = off");
  set("TimeShower:QEDshowerByL = off");
  set("TimeShower:QEDshowerByOther = off");
  set("TauDecays:mode = 3"); set("TauDecays:tauPolarization = 0");
  set("15:onMode = off"); set("15:onIfMatch = 16 -211");
  set("211:mayDecay = off");
  set("Next:numberShowEvent = 0"); set("Next:numberShowInfo = 0"); set("Next:numberShowProcess = 0");
  if(!py.init()) throw std::runtime_error("Pythia initialization failed");
  Tauolapp::Tauola::initialize();
  LHAPDF::initPDFSetByName("NNPDF23_lo_as_0130_qed");
  TauSpinner::initialize_spinner(true,0,
#ifdef SPINNER_PHOTON_API
      1,
#else
      0,
#endif
      0,13600.);
#ifdef SPINNER_PHOTON_API
  std::string mu=(std::filesystem::path(tables)/"table.mu").string();
  std::string down=(std::filesystem::path(tables)/"table.down").string();
  std::string up=(std::filesystem::path(tables)/"table.up").string();
  if(TauSpinner::initTables(mu.data(),down.data(),up.data())!=1)
    throw std::runtime_error("Official EW table initialization failed");
  TauSpinner::ExtraEWparamsSet(91.1887,2.4952,0.23152,128.86674175,0.,0.,0.00001166389,1);
  // This pinned release uses the ten-argument GSW API (no iqed argument).
  TauSpinner::initialize_GSW(0,1,0.,0.,0.,0.,0.,0.,0.,0.);
  auto photon_fraction=[&](double f) {
    TauSpinner::initialize_gamagama(f,f,0.,0.,0.,0.);
  };
  photon_fraction(channel=="gg" ? 1e6 : 0.);
#endif
  auto run=std::make_shared<HepMC3::GenRunInfo>();
  run->set_weight_names({"unpolarized","spin_sm"});
  HepMC3::WriterAsciiHepMC2 writer((output/"events.hepmc").string());
  HepMC3::Pythia8ToHepMC3 converter;
  std::ofstream csv(output/"weights.csv");
  csv << std::setprecision(17)
      << "event_id,base_weight,spin_weight,spin_weight_photon_limit,m_tautau,z_minus,z_plus,visible_mass\n";
  double sum=0,sum2=0,max_fraction_diff=0;
  for(int n=0;n<count;++n) {
    if(!py.next()) throw std::runtime_error("Event generation/decay failed; no silent event skipping");
    // Decay the central hard system only. The elastic LHE does not supply the
    // outgoing protons, so retaining undecayed pp beam entries would give an
    // incomplete pp event. Use the actual incoming photons as HepMC beams.
    if(input!="-") {
      std::vector<Pythia8::Particle> incoming, outgoing;
      for(int i=1;i<py.process.size();++i) {
        const auto& p=py.process[i];
        if(p.status()==-21 && p.id()==22) incoming.push_back(p);
        if(p.isFinal() && std::abs(p.id())==15) outgoing.push_back(p);
      }
      if(channel!="gg" || incoming.size()!=2 || outgoing.size()!=2)
        throw std::runtime_error("External LHE adapter supports only gamma gamma -> tau tau");
      auto hard=incoming[0].p()+incoming[1].p();
      auto delta=hard-outgoing[0].p()-outgoing[1].p();
      if(std::abs(delta.e())+delta.pAbs()>1e-6*std::max(1.,hard.e()))
        throw std::runtime_error("Hard-process four-momentum mismatch");
      py.event.reset();
      py.event[0].p(hard); py.event[0].m(hard.mCalc());
      for(auto p:incoming) {
        p.status(-12); p.mothers(0,0); p.daughters(3,4);
        py.event.append(p);
      }
      for(auto p:outgoing) {
        p.status(23); p.mothers(1,2); p.daughters(0,0);
        py.event.append(p);
      }
      if(!py.forceHadronLevel())
        throw std::runtime_error("Standalone LHE decay stage failed");
    }
    int tm=-1,tp=-1;
    for(int i=0;i<py.event.size();++i) {
      if(py.event[i].id()==15 && py.event[i].daughter1()>0
          && py.event[py.event[i].daughter1()].id()!=15) tm=i;
      if(py.event[i].id()==-15 && py.event[i].daughter1()>0
          && py.event[py.event[i].daughter1()].id()!=-15) tp=i;
    }
    if(tm<0||tp<0) throw std::runtime_error("Missing decayed tau pair");
    auto daughters=[&](int t) {
      std::vector<SimpleParticle> d;
      for(int i:py.event[t].daughterList()) d.push_back(simple(py.event[i]));
      if(d.size()!=2) throw std::runtime_error("Only pi nu decays supported");
      bool pion=false,nu=false;
      Pythia8::Vec4 total;
      for(int i:py.event[t].daughterList()) {
        pion |= std::abs(py.event[i].id())==211;
        nu |= std::abs(py.event[i].id())==16;
        total+=py.event[i].p();
      }
      auto residual=total-py.event[t].p();
      if(!pion||!nu||std::abs(residual.e())+residual.pAbs()>1e-6)
        throw std::runtime_error("Invalid tau daughter content or momentum closure");
      return d;
    };
    auto a=simple(py.event[tm]), b=simple(py.event[tp]);
    auto da=daughters(tm),db=daughters(tp);
    auto pair=py.event[tm].p()+py.event[tp].p();
    // ID 23 selects the neutral-current TauSpinner entry point. It is NOT
    // inserted as a fake Z mother into the photon HepMC event record.
    SimpleParticle x(pair.px(),pair.py(),pair.pz(),pair.e(),23);
    double w=TauSpinner::calculateWeightFromParticlesH(x,a,b,da,db);
#ifdef SPINNER_PHOTON_API
    if(!std::isfinite(TauSpinner::getWtNonSM()) || std::abs(TauSpinner::getWtNonSM()-1.)>1e-6)
      throw std::runtime_error("Unexpected non-unit SM-to-SM production weight");
#endif
    double wlimit=w;
    if(channel=="gg") {
#ifdef SPINNER_PHOTON_API
      photon_fraction(1e9);
      wlimit=TauSpinner::calculateWeightFromParticlesH(x,a,b,da,db);
      photon_fraction(1e6);
#endif
    }
    if(!std::isfinite(w)||!std::isfinite(wlimit)||w<0||w>4.00001)
      throw std::runtime_error("Invalid spin weight");
    max_fraction_diff=std::max(max_fraction_diff,std::abs(w-wlimit));
    auto pion=[&](int t) { for(int i:py.event[t].daughterList())
      if(std::abs(py.event[i].id())==211) return py.event[i].p();
      throw std::runtime_error("Missing pion"); };
    auto pm=pion(tm),pp=pion(tp);
    double base=py.info.weight();
    csv<<n<<','<<base<<','<<w<<','<<wlimit<<','<<pair.mCalc()<<','
       <<pm.e()/py.event[tm].e()<<','<<pp.e()/py.event[tp].e()<<','<<(pm+pp).mCalc()<<'\n';
    HepMC3::GenEvent event;
    if(!converter.fill_next_event(py,&event,n)) throw std::runtime_error("HepMC conversion failed");
    event.set_run_info(run); event.weights()={base,base*w};
    writer.write_event(event);
    if(writer.failed()) throw std::runtime_error("HepMC write failed");
    sum+=w; sum2+=w*w;
  }
  writer.close(); csv.close();
  double mean=sum/count, error=count>1?std::sqrt(std::max(0.,sum2-count*mean*mean)/(count*(count-1))):0;
  std::ofstream report(output/"run.json");
  report<<std::setprecision(17)<<"{\n\"events\": "<<count<<", \"seed\": "<<seed
        <<", \"channel\": \""<<channel<<"\",\n\"spin_weight_mean\": "<<mean
        <<", \"spin_weight_mean_error\": "<<error
        <<", \"photon_fraction_limit_max_difference\": "<<max_fraction_diff
        <<",\n\"decay_mode\": \"pi_nu_forced_both_taus\",\n"
        <<"\"input_spin\": \"uncorrelated_unpolarized\",\n"
        <<"\"event_record\": \""<<(channel=="gg"?"central_photon_hard_system_no_outgoing_protons":"dy_control")<<"\",\n"
        <<"\"photon_form_factor_configuration\": \""<<(channel=="gg"?"A0=B0=A=B=0; release_source_iqed=0":"not_applicable")<<"\",\n"
        <<"\"normalization\": \"shape_weights_only_no_branching_fractions_applied\",\n"
        <<"\"physics_qualified\": false, \"shower\": false, \"kt_smearing\": false\n}\n";
  py.stat();
  return 0;
} catch(const std::exception& e) { std::cerr<<"ERROR: "<<e.what()<<'\n'; return 1; }
