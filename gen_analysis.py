import os
import yaml
import subprocess
import re
import matplotlib.pyplot as plt

tCK_DDR4 = 1250
tCK_DDR5 = 625
def extract_info(output):
    """
    从输出字符串中提取所有信息并返回为字典
    :param output: 模拟器的输出字符串
    :return: 包含所有信息的字典
    """
    info_dict = {}

    # 匹配输出中的键值对，允许带有数字、下划线、字母的键和值
    matches = re.findall(r"(\w+):\s*([\d.]+)", output)

    for match in matches:
        key = match[0]
        try:
            value = float(match[1])
        except Exception:
            continue
        info_dict[key] = value

    return info_dict



# 初始化
DDR4_config_file = "./DDR4_CPU_cache_cfg.yaml"
DDR5_config_file = "./DDR5_CPU_cache_cfg.yaml"
fixed_nRCD = 15  # 固定的 nRCD 值

# 存储延迟结果
ddr4_latencies = []
ddr5_latencies = []

# 加载配置文件
with open(DDR4_config_file, 'r') as f:
    DDR4_config = yaml.safe_load(f)

with open(DDR5_config_file, 'r') as f:
    DDR5_config = yaml.safe_load(f)


# 生成 trace 文件并运行模拟器
trace_files = [600,602,605,625,631,657,641,648,620,623]
#trace_files = [600,602,603,605,607,619,620,623,625,631,641,648]
#trace_files = ['600']
for filename in trace_files:
    print('Trace: ', filename)
    trace_file = "/home/fan/projects/ramulator2/ctraces/{}.trace".format(filename)

    # 更新配置文件中的 trace 路径
    DDR4_config['Frontend']['traces'] = [trace_file]
    DDR5_config['Frontend']['traces'] = [trace_file]

    print('Simulating on DDR4')
    # 运行并捕获 DDR4 配置的模拟器输出
    yaml_config_str = yaml.dump(DDR4_config)
    with open("./temp/temp_DDR4_config.yaml", 'w+') as temp_config:
        temp_config.write(yaml_config_str)
    result = subprocess.run(['./ramulator2', '-f', './temp/temp_DDR4_config.yaml'], capture_output=True, text=True)
    print(result)
    ddr4_latencies.append(extract_info(result.stdout))

    print('Simulating on DDR5')
    # 运行并捕获 DDR5 配置的模拟器输出
    yaml_config_str = yaml.dump(DDR5_config)
    with open("./temp/temp_DDR5_config.yaml", 'w+') as temp_config:
        temp_config.write(yaml_config_str)
    result = subprocess.run(['./ramulator2', '-f', './temp/temp_DDR5_config.yaml'], capture_output=True, text=True)
    ddr5_latencies.append(extract_info(result.stdout))

print(ddr4_latencies)
print(ddr5_latencies)
import pickle
with open('int_latency_comp','wb+') as f:
    pickle.dump([trace_files,ddr4_latencies,ddr5_latencies],f)
    print('Saving Complete')

