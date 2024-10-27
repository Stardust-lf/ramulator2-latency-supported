import os
import yaml
import subprocess
import pandas as pd
import re

# Path to the configuration file, trace directory, and output CSV
config_path = "../sus_exp_cfgs/DDR5_3200AN_x4_cfg.yaml"
trace_dir = "../ctraces/"
output_csv = 'sus_perf_results.csv'
slow_chip_perf_values = [round(0.5 + i * 0.05, 2) for i in range(11)]  # 0.5 to 1.0 with step size of 0.05

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
    config['Frontend']['traces'] = [trace_path]  # Set the current trace file

    for slow_chip_perf in slow_chip_perf_values:
        print(f"Running simulation with trace {trace_filename} and slow_chip_perf = {slow_chip_perf}")

        # Update slow_chip_perf for this iteration
        config['MemorySystem']['Controller']['slow_chip_perf'] = slow_chip_perf

        # Save the updated configuration to a temporary file
        temp_config_path = "../temp/temp_config.yaml"
        with open(temp_config_path, 'w') as temp_config:
            yaml.dump(config, temp_config)

        # Run the simulation and capture the output
        result = subprocess.run(['../ramulator2', '-f', temp_config_path], capture_output=True, text=True)

        # Extract performance data
        extracted_data = extract_info(result.stdout)
        extracted_data['trace'] = trace_filename
        extracted_data['slow_chip_perf'] = slow_chip_perf

        # Append extracted data to results list
        results.append(extracted_data)

# Convert the results to a pandas DataFrame and handle any NaN values
df = pd.DataFrame(results).fillna('NaN')

# Save the results to CSV
df.to_csv(output_csv, index=False)

print(f"All simulations are complete. Results saved to {output_csv}.")
