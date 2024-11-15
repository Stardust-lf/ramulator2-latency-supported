import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the data (update the file path as needed)
file_path = 'sus_final_results.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# Filter data for only 6400 MHz
data_6400 = data[data['slow_timing'].str.contains('6400')]

# Calculate write ratio for 6400 MHz
write_ratio_by_trace_6400 = data_6400.groupby('trace').apply(
    lambda df: (df['total_num_write_requests'].sum() /
                (df['total_num_write_requests'].sum() + df['total_num_read_requests'].sum())) * 100
)

# Group system cycles by configuration and trace
system_cycles_by_config_6400 = data_6400.groupby(['trace', 'slow_timing'])['memory_system_cycles'].sum().unstack()

# Use original order of traces from the data
original_trace_order_6400 = data_6400['trace'].unique()

# Allow user to manually modify the trace order
print("Original trace order:")
print(original_trace_order_6400)

custom_trace_order = ['623', '603', '602', '605', '607', '621', '628', '654', '619', '620',
                      'pr_twi', 'pr_web', 'bfs_web', 'bc_twi', 'cc_web', 'cc_twi', 'bc_web', 'pr_road',
                      'bfs_road', 'bc_road', 'bfs_twi', 'cc_road']

# Reindex data based on the custom order
system_cycles_by_config_custom_6400 = system_cycles_by_config_6400.loc[custom_trace_order]
write_ratio_custom_6400 = write_ratio_by_trace_6400.loc[custom_trace_order]

# Define x-axis positions for the custom order
width = 0.25  # Width of each bar
x_custom_6400 = np.arange(len(custom_trace_order) + 2)  # Add 2 for SPEC and GAP

# Define colors for the three configurations and write ratio
colors = ['#FFCC99', '#FF9966', '#FF6600']  # Lighter to darker shades of orange
write_ratio_color = '#1f77b4'  # Blue for write ratio line

# Dictionary to map trace names
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

# Map trace names and add SPEC and GAP
mapped_trace_names = ['SPEC'] + [trace_names.get(trace, trace) for trace in custom_trace_order] + ['GAP']

# Create the bar plot with dual y-axes for custom trace order
fig, ax1 = plt.subplots(figsize=(10, 6), dpi=100)

# Plot the system cycles for each configuration in the custom order
for i, config in enumerate(system_cycles_by_config_custom_6400.columns):
    # Extract only AN, BN, or C from the config for the label
    if "_" in config:
        label = config.split("_")[-1]  # Extract last segment after "_"
    else:
        label = config  # If no "_", use the whole config

    ax1.bar(
        x_custom_6400[1:-1] + i * width,  # Adjust for SPEC and GAP
        system_cycles_by_config_custom_6400[config],
        width,
        label=label,  # Simplified label
        color=colors[i % len(colors)]  # Cycle through defined colors
    )

# Add a secondary y-axis for write ratio
ax2 = ax1.twinx()
ax2.plot(
    x_custom_6400[1:-1] + width,  # Align with the center of bars
    write_ratio_custom_6400,
    color=write_ratio_color,
    marker='*',
    linestyle='--',
    label="Write Ratio (%)"
)

# Set labels for the axes
ax1.set_ylabel("Execution Cycles", fontsize=12, color="#ff7f0e")
ax1.tick_params(axis='y', labelcolor="#ff7f0e")
ax2.set_ylabel("Write Request Ratio (%)", fontsize=12, color=write_ratio_color)
ax2.tick_params(axis='y', labelcolor=write_ratio_color)

# Set x-axis labels with SPEC and GAP
ax1.set_title("System Cycles and Write Operation Ratio for 6400 MHz", fontsize=16)
ax1.set_xticks(x_custom_6400)
ax1.set_xticklabels(mapped_trace_names, rotation=45, ha='right')

# Add legends for bars and line
fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.85), fontsize=10)

# Add grid for better readability
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# Adjust layout
plt.tight_layout()
plt.savefig('Overall.png')
# plt.show()
