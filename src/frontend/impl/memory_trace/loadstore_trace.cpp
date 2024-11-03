#include <filesystem>
#include <iostream>
#include <fstream>

#include "frontend/frontend.h"
#include "base/exception.h"

namespace Ramulator {

namespace fs = std::filesystem;

class LoadStoreTrace : public IFrontEnd, public Implementation {
  RAMULATOR_REGISTER_IMPLEMENTATION(IFrontEnd, LoadStoreTrace, "LoadStoreTrace", "Load/Store memory address trace.")

  private:
    struct Trace {
      int bubble_count;
      Addr_t addr;
      bool is_write;
    };
    std::vector<Trace> m_trace;
    size_t test_insts = 100000;
    size_t m_trace_length = 0;
    size_t m_curr_trace_idx = 0;

    size_t m_trace_count = 0;

    Logger_t m_logger;

  public:
    void init() override {
      std::string trace_path_str = param<std::string>("path").desc("Path to the load store trace file.").required();
      m_clock_ratio = param<uint>("clock_ratio").required();

      m_logger = Logging::create_logger("LoadStoreTrace");
      m_logger->info("Loading trace file {} ...", trace_path_str);
      init_trace(trace_path_str);
      m_logger->info("Loaded {} lines.", m_trace.size());
    };


    void tick() override {
      if(m_trace_count >= test_insts){
        return;
      }
      Trace& t = m_trace[m_curr_trace_idx];
      while(t.bubble_count >= 0){
        t.bubble_count --;
        return;
      }
      bool request_sent = m_memory_system->send({t.addr, t.is_write ? Request::Type::Write : Request::Type::Read});
      if (request_sent) {
        m_curr_trace_idx = (m_curr_trace_idx + 1) % m_trace_length;
        m_trace_count++;
      }    
    };


  private:
    void init_trace(const std::string& file_path_str) {
      fs::path trace_path(file_path_str);
      if (!fs::exists(trace_path)) {
        throw ConfigurationError("Trace {} does not exist!", file_path_str);
      }

      std::ifstream trace_file(trace_path);
      if (!trace_file.is_open()) {
        throw ConfigurationError("Trace {} cannot be opened!", file_path_str);
      }

      std::string line;
      size_t num_line_insts = 0;
      while (std::getline(trace_file, line) && num_line_insts<test_insts) {
        std::vector<std::string> tokens;
        tokenize(tokens, line, " ");

        int num_tokens = tokens.size();
        if (num_tokens != 2 & num_tokens != 3) {
          throw ConfigurationError("Trace {} format invalid!", file_path_str);
        }
        int bubble_count = std::stoi(tokens[0]);
        bool is_write = tokens[1] == "W";
        Addr_t addr = std::stoll(tokens[2], nullptr, 16);


        m_trace.push_back({bubble_count, addr, is_write});

    num_line_insts++;
  }

      trace_file.close();

      m_trace_length = m_trace.size();
    };

    // TODO: FIXME
    bool is_finished() override {
      bool finish = false;
      if(m_trace_count >= test_insts && m_memory_system->is_finished()){
        finish = true;
      }
      return finish;
    };
};

}        // namespace Ramulator