#include <filesystem>
#include <iostream>
#include <cmath>
#include <iomanip>

namespace TauSpinner {
int initTables(char*,char*,char*);
int CheckinitTables();
double Amz(int);
double Gamz(int);
double sin2W(int);
}

int main(int argc,char** argv) try {
  if(argc!=2) throw std::runtime_error("Usage: check-tables TABLE_DIRECTORY");
  auto root=std::filesystem::path(argv[1]);
  std::string mu=(root/"table.mu").string(),down=(root/"table.down").string(),up=(root/"table.up").string();
  for(auto name:{mu,down,up})
    if(!std::filesystem::is_regular_file(name)||std::filesystem::file_size(name)==0)
      throw std::runtime_error("Missing/empty official table: "+name);
  if(TauSpinner::initTables(mu.data(),down.data(),up.data())!=1 || !TauSpinner::CheckinitTables())
    throw std::runtime_error("TauSpinner rejected the tables");
  // Inspect all three flavour headers, not just the table-loaded flag.
  // EWtables.cxx uses category indices (0=mu, 1=down, 2=up), not PDG IDs.
  for(int flavour:{0,1,2}) {
    double mass=TauSpinner::Amz(flavour),width=TauSpinner::Gamz(flavour),sw=TauSpinner::sin2W(flavour);
    if(!std::isfinite(mass)||!std::isfinite(width)||!std::isfinite(sw)||
        mass<=0||width<=0||sw<=0||sw>=1)
      throw std::runtime_error("Invalid EW header parameters");
    std::cout<<std::setprecision(17)<<"flavour="<<flavour<<" MZ="<<mass
             <<" GammaZ="<<width<<" sin2thetaW="<<sw<<'\n';
  }
  std::cout<<"TABLE_LOADING_PASS (not a photon-physics qualification)\n";
  return 0;
} catch(const std::exception& e) { std::cerr<<e.what()<<'\n'; return 1; }
