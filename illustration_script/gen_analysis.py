import os
import yaml
import subprocess
import re
import pandas as pd

# Directory containing the configuration files
config_dir = "../exp_cfgs/"
trace_files = [600, 602, 605, 625, 631, 657, 641, 648, 620, 623, 603, 607, 619, 621, 628, 638, 644, 649, 654]
tCK_DDR4 = 1250
tCK_DDR5 = 625


def extract_info(output):
    """
    Extracts all numerical information from the simulator output string and returns it as a dictionary.
    :param output: The output string from the simulator.
    :return: A dictionary containing all the extracted information.
    """
    info_dict = {}

    # Regex pattern to match key-value pairs in the output (allowing numbers, underscores, and letters)
    matches = re.findall(r"(\w+):\s*([\d.]+)", output)

    for match in matches:
        key = match[0]
        try:
            value = float(match[1])
        except ValueError:
            value = None
        info_dict[key] = value

    return info_dict


# Initialize lists to store latencies for each config
latency_results = []

# Fetch all YAML configuration files from the directory
config_files = [f for f in os.listdir(config_dir) if f.endswith('.yaml')]

# Loop through all the configuration files and trace files to run the simulation
for config_file in config_files:
    for filename in trace_files:
        print(f'Running simulation for config {config_file} and trace {filename}')
        trace_file = f"../ctraces/{filename}.trace"

        # Load the configuration file
        config_path = os.path.join(config_dir, config_file)
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Update the trace file in the config
        config['Frontend']['traces'] = [trace_file]

        # Save the updated configuration to a temporary file
        temp_config_path = "../temp/temp_config.yaml"
        yaml_config_str = yaml.dump(config)
        with open(temp_config_path, 'w+') as temp_config:
            temp_config.write(yaml_config_str)

        # Run the simulation and capture the output
        result = subprocess.run(['../ramulator2', '-f', temp_config_path], capture_output=True, text=True)

        # Extract relevant data
        extracted_data = extract_info(result.stdout)

        # Append extracted data to the results list
        latency_results.append({"config": config_file, "trace": filename, **extracted_data})

# Convert the latencies to pandas DataFrame and handle NaN values
latency_df = pd.DataFrame(latency_results).fillna('NaN')

# Save the result to CSV
latency_df.to_csv('latency_results.csv', index=False)

print('All simulations are complete, and the results have been saved.')
