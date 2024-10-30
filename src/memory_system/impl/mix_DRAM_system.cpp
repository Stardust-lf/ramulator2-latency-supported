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
  IAddrMapper* m_addr_mapper;
  std::vector<IDRAMController*> m_controllers;

public:
  int s_num_read_requests = 0;
  int s_num_write_requests = 0;
  int s_num_other_requests = 0;

public:
  void init() override { 
    m_dram = create_child_ifce<IDRAM>();
    m_config["DRAM"]["impl"] = YAML::Node("DDR4");
    m_config["DRAM"]["org"]["preset"] = YAML::Node("DDR4_16Gb_x4");
    m_config["DRAM"]["timing"]["preset"] = YAML::Node("DDR4_2133N");
    std::cout << m_config << std::endl;
    m_slow_dram = create_child_ifce<IDRAM>();
    m_addr_mapper = create_child_ifce<IAddrMapper>();
    int num_channels = m_dram->get_level_size("channel");
    

    IDRAMController* primary_controller = create_child_ifce<IDRAMController>();
    primary_controller->m_impl->set_id(fmt::format("Primary Channel {}", 0));
    primary_controller->m_channel_id = 0;
    m_controllers.push_back(primary_controller);
    
    IDRAMController* secondary_controller = create_child_ifce<IDRAMController>();
    secondary_controller->m_is_slow = true;
    secondary_controller->m_impl->set_id(fmt::format("Secondary Channel {}", 1));
    secondary_controller->m_channel_id = 1; 
    m_controllers.push_back(secondary_controller);
    
    

    m_clock_ratio = param<uint>("clock_ratio").required();

    register_stat(m_clk).name("memory_system_cycles");
    register_stat(s_num_read_requests).name("total_num_read_requests");
    register_stat(s_num_write_requests).name("total_num_write_requests");
    register_stat(s_num_other_requests).name("total_num_other_requests");
  };

  void setup(IFrontEnd* frontend, IMemorySystem* memory_system) override { }

  bool send(Request req) override {
    m_controllers[0]->m_dram = m_dram;
    m_controllers[1]->m_dram = m_slow_dram;
    m_addr_mapper->apply(req);
    Request req_cp = req;
    req.addr_vec[0] = 0;
    req_cp.addr_vec[0] = 1;
    bool is_success = m_controllers[0]->send(req);
    bool is_success_sec = m_controllers[1]->send(req_cp);


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
    m_slow_dram->tick();
    for (auto controller : m_controllers) {
      controller->tick();
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
