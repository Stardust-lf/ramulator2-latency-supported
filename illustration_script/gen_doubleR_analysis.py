import os
import yaml
import subprocess
import pandas as pd
import re

# Path to the configuration file, trace directories, and output CSV
config_path = "../sus_perf_test.yaml"
trace_base_dir = "../wb_doubleR_traces"
output_csv = 'sus_doubleR_wb_results.csv'

# Supported timings
timings = [
    "DDR5_6400AN",
]

import re


def extract_info(output):
    """
    从模拟器输出中提取所有数值信息，并解决键重复的问题。
    :param output: 模拟器的输出字符串。
    :return: 包含提取信息的字典。
    """
    info_dict = {}
    key_counter = {}  # 用于记录每个键出现的次数

    for line in output.splitlines():
        # 匹配键值对
        kv_match = re.match(r"^\s*(\w+):\s*([\d.]+|nan)", line)
        if kv_match:
            key, value = kv_match.groups()
            try:
                value = float(value) if value != "nan" else float("nan")
            except ValueError:
                pass  # 如果无法转换为浮点数，保持原始值

            # 检查键是否重复
            if key in info_dict or key in key_counter:
                # 如果重复，为键添加递增的数字后缀
                key_counter[key] = key_counter.get(key, 0) + 1
                key = f"{key}_{key_counter[key]}"
            else:
                key_counter[key] = 0

            # 保存键值对
            info_dict[key] = value

    return info_dict

# Initialize list to store results
results = []

# Load the initial configuration file
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Iterate over each probability directory
for prob_dir in os.listdir(trace_base_dir):
    prob_path = os.path.join(trace_base_dir, prob_dir)
    if not os.path.isdir(prob_path) or not prob_dir.startswith("prob_"):
        continue

    # Extract probability value from directory name
    probability = float(prob_dir.split("_")[1])

    # Get a list of all trace files in the current probability directory
    trace_files = [f for f in os.listdir(prob_path) if f.endswith('.trace')]

    # Iterate over each trace file and each timing
    for trace_filename in trace_files:
        trace_path = os.path.join(prob_path, trace_filename)

        config['Frontend']['path'] = trace_path  # Set the current trace file
        for timing in timings:
            print(f"Running simulation with trace {trace_filename}, timing = {timing}, probability = {probability}")
            config['MemorySystem']["slow_timing"] = timing
            config['MemorySystem']['DRAM']['timing']['preset'] = timing
            temp_config_path = "../temp/temp_config.yaml"
            with open(temp_config_path, 'w') as temp_config:
                yaml.dump(config, temp_config)
            result = subprocess.run(['../build/ramulator2', '-f', temp_config_path], capture_output=True, text=True)
            extracted_data = extract_info(result.stdout)
            extracted_data['trace'] = trace_filename.split('.')[0]
            extracted_data['timing'] = timing
            extracted_data['probability'] = probability
            results.append(extracted_data)


# Convert the results to a pandas DataFrame and handle any NaN values
df = pd.DataFrame(results).fillna('NaN')

# Save the results to CSV
df.to_csv(output_csv, index=False)

print(f"All simulations are complete. Results saved to {output_csv}.")
