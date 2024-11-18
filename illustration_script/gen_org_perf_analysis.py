import os
import yaml
import subprocess
import pandas as pd
import re

# Path to the configuration file, trace directory, and output CSV
config_path = "../sus_perf_test.yaml"
trace_dir = "../wb_short_trace/"
output_csv = 'org_perf_results.csv'
# timings = [
#     "DDR5_3200BN", "DDR5_3200AN", "DDR5_3200C",
#     "DDR5_3600BN", "DDR5_3600AN", "DDR5_3600C",
#     "DDR5_4000BN", "DDR5_4000AN", "DDR5_4000C",
#     "DDR5_4400BN", "DDR5_4400AN", "DDR5_4400C",
#     "DDR5_4800BN", "DDR5_4800AN", "DDR5_4800C",
#     "DDR5_5200BN", "DDR5_5200AN", "DDR5_5200C",
#     "DDR5_5600BN", "DDR5_5600AN", "DDR5_5600C",
#     "DDR5_6000BN", "DDR5_6000AN", "DDR5_6000C",
#     "DDR5_6400BN", "DDR5_6400AN", "DDR5_6400C"
# ]
timings = [
    "DDR5_3200AN","DDR5_3200BN","DDR5_3200C",
    "DDR5_6400AN","DDR5_6400BN","DDR5_6400C"
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

# Get a list of all trace files in the directory
trace_files = [f for f in os.listdir(trace_dir) if f.endswith('.trace')]

# Iterate over each trace file and each slow_chip_perf value
for trace_filename in trace_files:
    trace_path = os.path.join(trace_dir, trace_filename)
    config['Frontend']['path'] = trace_path  # Set the current trace file

    for timing in timings:
        for org in ["DDR5_baseline", "DDR5_design", "DDR5_design2"]:
            print(f"Running simulation with trace {trace_filename} and timing = {timing} with org = {org}")

            # Update slow_chip_perf for this iteration
            config['MemorySystem']["slow_timing"] = timing
            config['MemorySystem']['DRAM']['timing']['preset'] = timing
            config['MemorySystem']['DRAM']['org']['preset'] = org
            # Save the updated configuration to a temporary file
            temp_config_path = "../temp/temp_config.yaml"
            with open(temp_config_path, 'w') as temp_config:
                yaml.dump(config, temp_config)

            # Run the simulation and capture the output with a timeout
            result = subprocess.run(['../build/ramulator2', '-f', temp_config_path], capture_output=True, text=True)
            #print(result.stdout)
            # Extract performance data
            extracted_data = extract_info(result.stdout)
            extracted_data['trace'] = trace_filename.split('.')[0]
            extracted_data['timing'] = timing
            extracted_data['organization'] = org

            # Append extracted data to results list
            results.append(extracted_data)

            # except subprocess.TimeoutExpired:
            #     print(f"Simulation for {trace_filename} and slow_chip_perf = {timing} timed out. Skipping this iteration.")

# Convert the results to a pandas DataFrame and handle any NaN values
df = pd.DataFrame(results).fillna('NaN')

# Save the results to CSV
df.to_csv(output_csv, index=False)

print(f"All simulations are complete. Results saved to {output_csv}.")
