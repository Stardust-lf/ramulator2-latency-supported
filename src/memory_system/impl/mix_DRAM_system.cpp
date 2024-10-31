#include "memory_system/memory_system.h"
#include "translation/translation.h"
#include "dram_controller/controller.h"
#include "addr_mapper/addr_mapper.h"
#include "dram/dram.h"
namespace Ramulator {

class DualChannelDRAMSystem final : public IMemorySystem, public Implementation {
  RAMULATOR_REGISTER_IMPLEMENTATION(IMemorySystem, DualChannelDRAMSystem, "DualChannelDRAM", "A dual-channel DRAM-based memory system.");

protected:
  Clk_t m_clk = 0;
  IDRAM* m_dram;
  IDRAM* m_slow_dram;
  IAddrMapper* m_pri_mapper;
  IAddrMapper* m_sec_mapper;
  std::vector<IDRAMController*> m_controllers;

public:
  int s_num_read_requests = 0;
  int s_num_write_requests = 0;
  int s_num_other_requests = 0;
  int s_num_wait_cycles = 0;
  IDRAMController* primary_controller;
  IDRAMController* secondary_controller;

public:
  void init() override { 
    m_dram = create_child_ifce<IDRAM>();
    m_pri_mapper = create_child_ifce<IAddrMapper>();
    m_config["DRAM"]["impl"] = YAML::Node("DDR4");
    m_config["DRAM"]["org"]["preset"] = YAML::Node("DDR4_16Gb_x4");
    m_config["DRAM"]["timing"]["preset"] = YAML::Node("DDR4_1600J");
    m_sec_mapper = create_child_ifce<IAddrMapper>();
    // m_config["DRAM"]["org"]["channel"] = YAML::Node("2");
    std::cout << m_config << std::endl;
    m_slow_dram = create_child_ifce<IDRAM>();
    
    int num_channels = m_dram->get_level_size("channel");
    

    primary_controller = create_child_ifce<IDRAMController>();
    primary_controller->m_impl->set_id(fmt::format("Primary Channel {}", 0));
    primary_controller->m_channel_id = 0;

    
    secondary_controller = create_child_ifce<IDRAMController>();
    secondary_controller->m_impl->set_id(fmt::format("Secondary Channel {}", 1));
    secondary_controller->m_channel_id = 0; 


    primary_controller->m_dram = m_dram;
    secondary_controller->m_dram = m_slow_dram;
    

    m_clock_ratio = param<uint>("clock_ratio").required();

    register_stat(m_clk).name("memory_system_cycles");
    register_stat(s_num_read_requests).name("total_num_read_requests");
    register_stat(s_num_write_requests).name("total_num_write_requests");
    register_stat(s_num_other_requests).name("total_num_other_requests");
    register_stat(s_num_wait_cycles).name("total_wait_cycles");

  };

private:
  bool m_prev_read = true;

  void setup(IFrontEnd* frontend, IMemorySystem* memory_system) override { }

  bool send(Request req) override {
    Request req_cp = req;
    m_pri_mapper->apply(req);
    m_sec_mapper->apply(req_cp);
    // req.addr_vec[0] = 0;
    // req_cp.addr_vec[0] = 0;
    bool is_success = primary_controller->send(req);
    bool is_success_sec = true;
    if(req.type_id == Request::Type::Write){
      is_success_sec = secondary_controller->send(req_cp);
    }

    if (is_success && is_success_sec) {
      switch (req.type_id) {
        case Request::Type::Read: {
          s_num_read_requests++;
          break;
        }
        case Request::Type::Write: {
          s_num_write_requests++;
          break;
        }
        default: {
          s_num_other_requests++;
          break;
        }
      }
    }

    return is_success && is_success_sec;
  };

  void tick() override {
    m_clk++;
    m_dram->tick();
    int speed_times = 2;
    if(m_clk % speed_times == 0){
      m_slow_dram->tick();
    }
    if(secondary_controller->m_write_buffer.size()){
      if(!m_prev_read || primary_controller->m_curr_cmd->type_id == Request::Type::Read || 
      primary_controller->m_curr_cmd->addr == secondary_controller->m_curr_cmd->addr){
        primary_controller->tick();
        m_prev_read = primary_controller->m_curr_cmd->type_id == Request::Type::Read;
        secondary_controller->tick();
       }else{
        s_num_wait_cycles ++;
        secondary_controller->tick();
       }
      }else{
        primary_controller->tick();
        secondary_controller->tick();
      }
    
  };

  float get_tCK() override {
    return m_dram->m_timing_vals("tCK_ps") / 1000.0f;
  }

  // const SpecDef& get_supported_requests() override {
  //   return m_dram->m_requests;
  // };
};

} // namespace 
