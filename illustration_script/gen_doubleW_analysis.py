import os
import yaml
import subprocess
import pandas as pd
import re

# Path to the configuration file, trace directories, and output CSV
config_path = "../sus_perf_test.yaml"
trace_base_dir = "../wb_doubleR_traces_traces"
dw_trace_dir = '../wb_doubleW_trace'
output_csv = 'doubleW_analysis_with_probability.csv'

# Supported timings
timings = [
    "DDR5_6400AN",
]

def extract_info(output):
    """
    Extracts all numerical information from the simulator output string and returns it as a dictionary.
    :param output: The output string from the simulator.
    :return: A dictionary containing all the extracted information.
    """
    info_dict = {}
    matches = re.findall(r"(\w+):\s*([\d.]+)", output)
    for match in matches:
        key, value = match
        try:
            info_dict[key] = float(value)
        except ValueError:
            info_dict[key] = None
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
            extracted_data['dw_tag'] = 0
            extracted_data['probability'] = probability
            results.append(extracted_data)

        # Process the double write trace
        trace_path = os.path.join(dw_trace_dir, trace_filename)
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
            extracted_data['dw_tag'] = 1
            extracted_data['timing'] = timing
            extracted_data['probability'] = probability
            results.append(extracted_data)

# Convert the results to a pandas DataFrame and handle any NaN values
df = pd.DataFrame(results).fillna('NaN')

# Save the results to CSV
df.to_csv(output_csv, index=False)

print(f"All simulations are complete. Results saved to {output_csv}.")
