import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
data = pd.read_csv('sus_final_results.csv')

# Convert trace column to string for matching dictionary keys
data['trace'] = data['trace'].astype(str)

# Extract frequency and configuration from the 'slow_timing' column
data['frequency'] = data['slow_timing'].str.extract(r'DDR5_(\d+)')[0]
data['configuration'] = data['slow_timing'].str.extract(r'DDR5_\d+(\w+)')[0]

# Calculate wait percentage and write ratio for plotting
data['wait_percentage'] = (data['total_wait_cycles'] * 100) / data['memory_system_cycles']
data['write_ratio'] = (data['total_num_write_requests'] * 100) / (
        data['total_num_write_requests'] + data['total_num_read_requests'])

# Sort data by trace and configuration
data = data.sort_values(by=['trace', 'configuration'])

# Define consistent order for traces
custom_trace_order = ['623', '603', '602', '605', '607', '621', '628', '654', '619', '620']

# Trace name mapping
trace_names = {
    '600': 'perlbench', '602': 'gcc', '605': 'mcf', '620': 'omnetpp', '623': 'xalancbmk',
    '625': 'x264', '631': 'deepsjeng', '641': 'leela', '648': 'exchange2', '657': 'xz',
    '603': 'bwaves', '607': 'cactuBSSN', '619': 'lbm', '621': 'wrf', '627': 'cam4',
    '628': 'pop2', '638': 'imagick', '644': 'nab', '649': 'fotonik3d', '654': 'roms',
    'bfs_twi': 'bfs twi', 'bfs_web': 'bfs web', 'bfs_road': 'bfs road',
    'bc_twi': 'bc twi', 'bc_web': 'bc web', 'bc_road': 'bc road',
    'cc_twi': 'cc twi', 'cc_web': 'cc web', 'cc_road': 'cc road',
    'pr_twi': 'pr twi', 'pr_web': 'pr web', 'pr_road': 'pr road'
}

mapped_trace_names = [trace_names.get(trace, trace) for trace in custom_trace_order]

# Define x-axis positions
x_positions = np.arange(len(custom_trace_order))
width = 0.25

# Define colors
colors = ['#FFCC99']  # Only for AN configuration
write_ratio_color = '#1f77b4'  # For write ratio line

# Filter unique frequencies excluding 6400
frequencies = data['frequency'].unique()
frequencies = [freq for freq in frequencies if freq != '6400']

# Create subplots for two rows and four columns
num_columns = 4
num_rows = 2
fig, axs = plt.subplots(num_rows, num_columns, figsize=(12, 6), dpi=150, sharey=True, sharex=True)
axs = axs.flatten()

# Plot each frequency in a separate subplot
for idx, freq in enumerate(frequencies):
    # Filter data for the current frequency and configuration AN
    data_freq_an = data[(data['frequency'] == freq) & (data['configuration'] == 'AN')]

    # Skip empty datasets
    if data_freq_an.empty:
        continue

    # Plot data in the corresponding subplot
    ax1 = axs[idx]

    # Plot wait percentage as bars for AN configuration only
    y_values = [
        data_freq_an[data_freq_an['trace'] == trace]['wait_percentage'].values[0]
        if not data_freq_an[data_freq_an['trace'] == trace].empty else 1  # Avoid log(0)
        for trace in custom_trace_order
    ]
    ax1.bar(x_positions, y_values, width=width, label='AN', color=colors[0])

    # Set the left axis to log scale
    ax1.set_yscale('log')
    ax1.set_ylabel("Performance Loss (%)", fontsize=10, color="#ff7f0e")
    ax1.tick_params(axis='y', labelcolor="#ff7f0e")

    # Add a secondary y-axis for write ratio
    write_ratio_values = [
        data_freq_an[data_freq_an['trace'] == trace]['write_ratio'].values[0]
        if not data_freq_an[data_freq_an['trace'] == trace].empty else 0
        for trace in custom_trace_order
    ]
    ax2 = ax1.twinx()
    ax2.plot(x_positions, write_ratio_values, color=write_ratio_color, marker='o', linestyle='--',
             label="Write Ratio (%)")
    ax2.set_ylabel("Write Ratio (%)", fontsize=10, color=write_ratio_color)
    ax2.tick_params(axis='y', labelcolor=write_ratio_color)

    # Set x-axis ticks and labels
    ax1.set_title(f"DDR5 {freq} MHz", fontsize=12)
    #ax1.set_xlabel("Trace", fontsize=10)
    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(mapped_trace_names, rotation=45, ha="right")

    # Add grid for better readability
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

# Hide unused subplots
for i in range(len(frequencies), len(axs)):
    fig.delaxes(axs[i])

# Adjust layout to prevent overlap
plt.tight_layout()
plt.savefig('../figures/multi_subplot_two_rows_four_columns.png')
plt.show()
