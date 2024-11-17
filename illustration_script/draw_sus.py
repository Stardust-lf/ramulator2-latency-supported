import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

# Load the data
data = pd.read_csv('sus_partial_results.csv')

# Convert trace column to string for matching dictionary keys
data['trace'] = data['trace'].astype(str)

# Extract frequency and configuration from the 'slow_timing' column
data['frequency'] = data['slow_timing'].str.extract(r'DDR5_(\d+)')[0]
data['configuration'] = data['slow_timing'].str.extract(r'DDR5_\d+(\w+)')[0]

# Find the baseline wait cycles for each trace at 6400 MHz
baseline_wait_cycles = data[data['frequency'] == '6400'].groupby('trace')['total_wait_cycles'].mean()

# Calculate adjusted performance loss based on the new formula
data['adjusted_wait_percentage'] = data.apply(
    lambda row: (
        (row['total_wait_cycles'] - baseline_wait_cycles.get(row['trace'], 0)) * 100 / row['memory_system_cycles']
    ) if row['trace'] in baseline_wait_cycles else 0,
    axis=1
)

# Custom trace order and mapping
custom_trace_order = [
    '600', '602', '605', '620', '623', '625', '631', '641', '648', '657',
    '603', '607', '619', '621', '628', '638', '644', '649', '654',
    'bfs_twi', 'bfs_web', 'bfs_road',
    'bc_twi', 'bc_web', 'bc_road',
    'cc_twi', 'cc_web', 'cc_road',
    'pr_twi', 'pr_web', 'pr_road'
]
trace_names = {
    '600': 'perlbench', '602': 'gcc', '605': 'mcf', '620': 'omnetpp', '623': 'xalancbmk',
    '625': 'x264', '631': 'deepsjeng', '641': 'leela', '648': 'exchange2', '657': 'xz',
    '603': 'bwaves', '607': 'cactuBSSN', '619': 'lbm', '621': 'wrf', '628': 'pop2',
    '638': 'imagick', '644': 'nab', '649': 'fotonik3d', '654': 'roms',
    'bfs_twi': 'bfs twi', 'bfs_web': 'bfs web', 'bfs_road': 'bfs road',
    'bc_twi': 'bc twi', 'bc_web': 'bc web', 'bc_road': 'bc road',
    'cc_twi': 'cc twi', 'cc_web': 'cc web', 'cc_road': 'cc road',
    'pr_twi': 'pr twi', 'pr_web': 'pr web', 'pr_road': 'pr road'
}
mapped_trace_names = [trace_names.get(trace, trace) for trace in custom_trace_order]

# Define x-axis positions and labels
x_positions = np.arange(len(custom_trace_order))
bar_width = 0.1  # Narrower bars for more distinction

# Sort frequencies and create a smooth color gradient
frequencies = sorted([int(freq) for freq in data['frequency'].unique() if freq != '6400'])
cmap = plt.colormaps["OrRd"]
frequency_to_color = {
    str(freq): mcolors.to_hex(cmap(0.2 + (i / (len(frequencies) - 1)) * 0.6))  # Adjust range for smoother colors
    for i, freq in enumerate(frequencies)
}

# Calculate write_ratio if not already present
if 'write_ratio' not in data.columns:
    data['write_ratio'] = (data['total_num_write_requests'] * 100) / (
        data['total_num_write_requests'] + data['total_num_read_requests'])

# Prepare write ratio values
write_ratio_values = [
    data[data['trace'] == trace]['write_ratio'].mean()  # Take mean across all frequencies
    if not data[data['trace'] == trace].empty else 0
    for trace in custom_trace_order
]

# Define breakpoints for the write ratio line
breakpoints = ['657', '654']
break_indices = [custom_trace_order.index(breakpoint) + 1 for breakpoint in breakpoints]

# Plot the chart
fig, ax1 = plt.subplots(figsize=(10, 6), dpi=150)

# Plot write ratio with breaks
ax2 = ax1.twinx()
for start, end in zip([0] + break_indices, break_indices + [len(write_ratio_values)]):
    ax2.plot(x_positions[start:end], write_ratio_values[start:end], color='#1f77b4', marker='*',
             linewidth=1, label="Write Ratio (%)" if start == 0 else None)

ax2.set_ylabel("Write Ratio (%)", fontsize=12, color='#1f77b4')
ax2.tick_params(axis='y', labelcolor='#1f77b4')

# Plot adjusted performance loss for each configuration and frequency
for i, (config, freq) in enumerate(
    [(c, f) for c in data['configuration'].unique() for f in frequencies]
):
    # Filter data for the current configuration and frequency
    data_subset = data[(data['configuration'] == config) & (data['frequency'] == str(freq))]

    if data_subset.empty:
        continue

    # Calculate adjusted performance loss for traces
    adjusted_wait_values = [
        data_subset[data_subset['trace'] == trace]['adjusted_wait_percentage'].mean()
        if not data_subset[data_subset['trace'] == trace].empty else 0
        for trace in custom_trace_order
    ]

    # Plot as thinner bars with offsets and color based on frequency
    offset = (i - len(frequencies) / 2) * bar_width * 2  # Offset for separation
    ax1.bar(
        x_positions + offset,
        adjusted_wait_values,
        width=bar_width*3,
        edgecolor='black',  # Add black border
        linewidth=0.5,  # Thin border
        color=frequency_to_color[str(freq)],  # Color based on frequency
        label=f"{config} - DDR5 {freq} MHz"
    )

# Set x-axis ticks and labels
ax1.set_xticks(x_positions)
ax1.set_xticklabels(mapped_trace_names, rotation=45, ha="right")

# Set axis labels and title
ax1.set_yscale('log')  # Use log scale for adjusted performance loss
ax1.set_ylabel("Adjusted Performance Loss (%)", fontsize=12, color="#ff7f0e")
ax1.set_xlabel("Trace", fontsize=12)
ax1.set_title("Performance Loss and Write Ratio (Write-back LRU Cache)", fontsize=14)
ax1.tick_params(axis='y', labelcolor="#ff7f0e")

# Add legend to the top-left corner
fig.legend(loc='upper left', bbox_to_anchor=(0.08, 0.92))
ax1.grid(alpha=0.7)

# Adjust layout to prevent overlap
fig.tight_layout()
plt.savefig('sus_perf_loss_WT.png')
plt.show()
