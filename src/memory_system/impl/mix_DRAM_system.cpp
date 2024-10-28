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
  IAddrMapper* m_addr_mapper;
  std::vector<IDRAMController*> m_primary_controllers; // 主控制器
  std::vector<IDRAMController*> m_secondary_controllers; // 辅助控制器

public:
  int s_num_read_requests = 0;
  int s_num_write_requests = 0;
  int s_num_other_requests = 0;

public:
  void init() override { 
    m_dram = create_child_ifce<IDRAM>();
    m_addr_mapper = create_child_ifce<IAddrMapper>();
    int num_channels = m_dram->get_level_size("channel");   

    // 为主通道和辅助通道创建内存控制器
    for (int i = 0; i < num_channels; i++) {
      IDRAMController* primary_controller = create_child_ifce<IDRAMController>();
      primary_controller->m_impl->set_id(fmt::format("Primary Channel {}", i));
      primary_controller->m_channel_id = i;
      m_primary_controllers.push_back(primary_controller);
      
      IDRAMController* secondary_controller = create_child_ifce<IDRAMController>();
      secondary_controller->m_impl->set_id(fmt::format("Secondary Channel {}", i));
      secondary_controller->m_channel_id = num_channels + i; // 分配一个唯一的 ID
      m_secondary_controllers.push_back(secondary_controller);
    }

    m_clock_ratio = param<uint>("clock_ratio").required();

    register_stat(m_clk).name("memory_system_cycles");
    register_stat(s_num_read_requests).name("total_num_read_requests");
    register_stat(s_num_write_requests).name("total_num_write_requests");
    register_stat(s_num_other_requests).name("total_num_other_requests");
  };

  void setup(IFrontEnd* frontend, IMemorySystem* memory_system) override { }

  bool send(Request req) override {
    m_addr_mapper->apply(req);
    int channel_id = req.addr_vec[0];
    
    // 根据通道 ID 确定使用主控制器还是辅助控制器
    IDRAMController* controller;
    if (channel_id < m_primary_controllers.size()) {
      controller = m_primary_controllers[channel_id];
    } else {
      controller = m_secondary_controllers[channel_id - m_primary_controllers.size()];
    }

    bool is_success = controller->send(req);

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
    for (auto controller : m_primary_controllers) {
      controller->tick();
    }
    for (auto controller : m_secondary_controllers) {
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
