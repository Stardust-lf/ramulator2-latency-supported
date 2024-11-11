import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
data = pd.read_csv('org_perf_results.csv')
plt.rcParams["font.family"] = "Times New Roman"

# Convert trace column to string for matching dictionary keys
data['trace'] = data['trace'].astype(str)

# Extract frequency and configuration from 'slow_timing' column
data['frequency'] = data['timing'].str.extract(r'DDR5_(\d+)')[0].astype(int)
data['configuration'] = data['timing'].str.extract(r'DDR5_\d+(\w+)')[0]

# Add 'org' column assuming rows appear in sets of three (Baseline, Design1, Design2)
# data['org'] = ['Baseline', 'Design1', 'Design2'] * (len(data) // 3)

# Mapping trace names for better readability
trace_names = {
    '600': 'perlbench', '602': 'gcc', '605': 'mcf', '620': 'omnetpp', '623': 'xalancbmk',
    '625': 'x264', '631': 'deepsjeng', '641': 'leela', '648': 'exchange2', '657': 'xz',
    '603': 'bwaves', '607': 'cactuBSSN', '619': 'lbm', '621': 'wrf', '627': 'cam4',
    '628': 'pop2', '638': 'imagick', '644': 'nab', '649': 'fotonik3d', '654': 'roms'
}
data['trace_name'] = data['trace'].map(trace_names)

# Define unique frequency-configuration combinations as x-axis labels
data['freq_config'] = data['frequency'].astype(str) + data['configuration']
unique_freq_configs = sorted(data['freq_config'].unique())

# Define grid layout with 5 columns and 2 rows
num_columns = 5
num_rows = 2
fig, axs = plt.subplots(num_rows, num_columns, figsize=(12, 8), sharey=True)
fig.suptitle("Memory System Cycles by Frequency-Configuration and Design for Each Benchmark", fontsize=16)

# Plot each trace in its own subplot
for i, (trace, trace_data) in enumerate(data.groupby('trace_name')):
    row, col = divmod(i, num_columns)

    # Select the axis for this subplot
    ax = axs[row, col] if num_rows > 1 else axs[col]

    # Plot each design as a set of bars
    for j, org in enumerate(["DDR5_baseline", "DDR5_design", "DDR5_design2"]):
        org_data = trace_data[trace_data['organization'] == org]

        # Set up x-axis with positions for each frequency-configuration combination
        x_positions = np.arange(len(unique_freq_configs))
        y_values = [org_data[org_data['freq_config'] == fc]['memory_system_cycles'].values[0]
                    if fc in org_data['freq_config'].values else 0
                    for fc in unique_freq_configs]

        # Plot the bars with an offset for each design
        ax.bar(x_positions + j * 0.2, y_values, width=0.2, label=org)

    # Customize each subplot
    ax.set_title(trace)
    ax.set_xticks(x_positions + 0.3)
    ax.set_xticklabels(unique_freq_configs, rotation=45, ha="right")
    ax.grid(True)
    ax.legend(loc="upper right", fontsize=8, title="Design")

# Adjust layout to prevent overlap
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
