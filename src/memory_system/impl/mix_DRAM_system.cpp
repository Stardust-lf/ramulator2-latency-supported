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
  std::string m_slow_timing;
  std::string m_slow_impl;
public:
  int s_num_read_requests = 0;
  int s_num_write_requests = 0;
  int s_num_other_requests = 0;
  int s_num_wait_cycles = 0;
  IDRAMController* primary_controller;
  IDRAMController* secondary_controller;

public:
  void init() override { 
    m_clock_ratio = param<uint>("clock_ratio").required();
    m_slow_impl = param<std::string>("slow_impl").required();
    m_slow_timing = param<std::string>("slow_timing").required();
    

    m_dram = create_child_ifce<IDRAM>();
    m_pri_mapper = create_child_ifce<IAddrMapper>();
    m_config["DRAM"]["impl"] = YAML::Node(m_slow_impl);
    m_config["DRAM"]["timing"]["preset"] = YAML::Node(m_slow_timing);
    
    m_sec_mapper = create_child_ifce<IAddrMapper>();
    m_slow_dram = create_child_ifce<IDRAM>();
    
    int num_channels = m_dram->get_level_size("channel");
    

    primary_controller = create_child_ifce<IDRAMController>();
    primary_controller->m_impl->set_id(fmt::format("Primary Channel {}", 0));
    primary_controller->m_channel_id = 0;

    
    secondary_controller = create_child_ifce<IDRAMController>();
    secondary_controller->m_impl->set_id(fmt::format("Secondary Channel {}", 1));
    secondary_controller->m_channel_id = 0; 
    secondary_controller->m_is_spc_dram = true;

    primary_controller->m_dram = m_dram;
    secondary_controller->m_dram = m_slow_dram;
    

    

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
    if(req.type_id == Request::Type::Write){
      if(primary_controller->m_write_buffer.size() == 32 || secondary_controller->m_write_buffer.size() == 32){
        return false;
      }
    }
    bool is_success = primary_controller->send(req);
    
    if(is_success && req.type_id == Request::Type::Write){
      secondary_controller->send(req_cp);
    }

    if (is_success) {
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

    return is_success;
  };

  
  void tick() override {
    m_clk++;
    m_dram->tick();
    // int speed_times = 2;
    // if(m_clk % speed_times == 0){
    //   m_slow_dram->tick();
    // }
    m_slow_dram->tick();
    ReqBuffer::iterator pri_req_it;
    ReqBuffer* pri_buffer = nullptr;
    ReqBuffer::iterator sec_req_it;
    ReqBuffer* sec_buffer = nullptr;
    
    bool request_found_pri = primary_controller->schedule_request(pri_req_it, pri_buffer);
    if(primary_controller->m_is_write_mode && request_found_pri){
      secondary_controller->m_is_write_mode = true;
    }
    bool request_found_sec = secondary_controller->schedule_request(sec_req_it, sec_buffer);
    if(secondary_controller->m_is_write_mode && primary_controller->m_is_write_mode){
      if(request_found_pri && !request_found_sec && m_prev_read){
        primary_controller->empty_tick();
        s_num_wait_cycles ++;
      }else{
        primary_controller->tick();
        m_prev_read = pri_req_it->type_id == Request::Type::Read;
      }
    }else{
      primary_controller->tick();
      m_prev_read = pri_req_it->type_id == Request::Type::Read;
    }
    secondary_controller->tick();
    
  };

  bool is_finished() override{

    return bool(primary_controller->m_write_buffer.size() 
    + primary_controller->m_read_buffer.size() 
    + primary_controller->pending.size()
    + secondary_controller->pending.size()
    + secondary_controller->m_write_buffer.size());
  }

  float get_tCK() override {
    return m_dram->m_timing_vals("tCK_ps") / 1000.0f;
  }

  // const SpecDef& get_supported_requests() override {
  //   return m_dram->m_requests;
  // };
};

} // namespace 
