import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
data = pd.read_csv('../result_csv/sus_perf_results.csv')
plt.rcParams["font.family"] = "Times New Roman"
# Convert trace column to string for matching dictionary keys
data['trace'] = data['trace'].astype(str)

# Extract frequency and configuration from the 'slow_timing' column
data['frequency'] = data['slow_timing'].str.extract(r'DDR5_(\d+)')[0]
data['configuration'] = data['slow_timing'].str.extract(r'DDR5_\d+(\w+)')[0]

# Calculate the new percentage metric for plotting
data['wait_percentage'] = (data['total_wait_cycles'] * 100) / data['memory_system_cycles']

# Sort data by frequency and configuration for plot alignment
data = data.sort_values(by=['trace', 'frequency', 'configuration'])

# Trace name dictionary
trace_names = {
    '600': 'perlbench', '602': 'gcc', '605': 'mcf', '620': 'omnetpp', '623': 'xalancbmk',
    '625': 'x264', '631': 'deepsjeng', '641': 'leela', '648': 'exchange2', '657': 'xz',
    '603': 'bwaves', '607': 'cactuBSSN', '619': 'lbm', '621': 'wrf', '627': 'cam4',
    '628': 'pop2', '638': 'imagick', '644': 'nab', '649': 'fotonik3d', '654': 'roms'
}

# Define the consistent order of configurations
desired_configs = ["AN", "BN", "C"]
unique_frequencies = sorted(data['frequency'].unique())

# Set up grid layout
num_columns = 5
num_rows = (len(data['trace'].unique()) + num_columns - 1) // num_columns
fig, axs = plt.subplots(num_rows, num_columns, figsize=(16, num_rows * 3), sharex=True, dpi=100)
fig.suptitle("Wait Times as Percentage of Memory System Cycles for Each Trace", fontsize=16)

# Plot each trace with separate lines for AN, BN, and C configurations
for i, trace in enumerate(data['trace'].unique()):
    row, col = divmod(i, num_columns)
    trace_data = data[data['trace'] == trace]

    # Plot each configuration line separately
    for config in desired_configs:
        config_data = trace_data[trace_data['configuration'] == config]
        x_positions = [unique_frequencies.index(freq) for freq in config_data['frequency']]
        y_values = config_data['wait_percentage']

        # Plot each configuration line with a label
        axs[row, col].plot(x_positions, y_values, marker='o', linestyle='-', label=config)

    axs[row, col].set_title(trace_names.get(trace, f'Trace {trace}'))
    axs[row, col].grid(True)

    # Set x-axis lower labels for frequencies
    axs[row, col].set_xticks(range(len(unique_frequencies)))
    axs[row, col].set_xticklabels(unique_frequencies, rotation=45, ha='right')
    #axs[row, col].set_xlabel("Frequency (MHz)")
    axs[row, col].legend(title="Type", loc="upper right", fontsize=8)

# Hide any unused subplots
for j in range(i + 1, num_rows * num_columns):
    fig.delaxes(axs[j // num_columns, j % num_columns])

# Adjust layout to prevent overlap
plt.tight_layout(h_pad=0,w_pad=-0.1)
plt.show()
