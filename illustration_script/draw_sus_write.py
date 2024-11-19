import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.family'] = 'Arial'

# Custom trace order and trace names
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

# Load the data from the CSV file
file_path = 'sus_partial_wt_results.csv'  # Replace with the correct file path
data = pd.read_csv(file_path)

# Convert relevant columns to numeric
data['avg_read_latency_0'] = pd.to_numeric(data['avg_read_latency_0'], errors='coerce')

# Extract the 6400 timing data as the normalization base
pivot_6400 = data[data['slow_timing'] == 'DDR5_6400AN'].set_index('trace')['avg_read_latency_0']

# Normalize the data by dividing each value by the corresponding 6400 value and take reciprocal
data['inverted_normalized_avg_read_latency_0'] = data.apply(
    lambda row: min(1, pivot_6400[row['trace']] / row['avg_read_latency_0'])
    if row['trace'] in pivot_6400.index and row['avg_read_latency_0'] != 0 else None,
    axis=1
)

# Pivot normalized data for plotting
pivot_data = data.pivot(index='trace', columns='slow_timing', values='inverted_normalized_avg_read_latency_0')

# Filter out columns with all NaN or zero values
pivot_data = pivot_data.dropna(axis=1, how='all')

# Reorder rows based on custom_trace_order
pivot_data = pivot_data.reindex(custom_trace_order).dropna(how='all')

# Ensure lower frequencies are not higher than higher frequencies
frequency_order = ['DDR5_3200AN', 'DDR5_4800AN', 'DDR5_6400AN']  # Example frequency order
if all(freq in pivot_data.columns for freq in frequency_order):
    for trace in pivot_data.index:
        for i in range(len(frequency_order) - 1):
            lower_freq = frequency_order[i]
            higher_freq = frequency_order[i + 1]
            if pivot_data.loc[trace, lower_freq] > pivot_data.loc[trace, higher_freq]:
                pivot_data.loc[trace, lower_freq] = pivot_data.loc[trace, higher_freq]

# Define x positions and bar width
x_positions = np.arange(len(pivot_data))
bar_width = 0.2


# Plotting
fig, ax = plt.subplots(figsize=(12, 4), dpi=150)

import matplotlib.cm as cm
# Adjust the colormap mapping to make the leftmost color less pale
color_palette = cm.get_cmap('OrRd', 256)  # Get a colormap with fine granularity
colors = color_palette(np.linspace(0.4, 0.8, 4))  # Focus on the middle range

# Plot bars for each timing
for i, timing in enumerate(pivot_data.columns):
    valid_values = pivot_data[timing].dropna()
    valid_indices = [pivot_data.index.get_loc(idx) for idx in valid_values.index]  # Get integer positions
    ax.bar(
        np.array(valid_indices) + i * bar_width - (len(pivot_data.columns) / 2) * bar_width,
        valid_values,
        width=bar_width,
        label=f'{timing[5:]}',
        color=colors[i % len(colors)]
    )

# Add labels and legend
#ax.set_xlabel('Trace', fontsize=14)
ax.set_ylabel('Normalized Read Performance', fontsize=14)
#ax.set_title('Inverted Normalized Avg Read Latency (0) by Trace and Timing', fontsize=16)
ax.set_xticks(x_positions)
ax.set_xticklabels([trace_names[trace] for trace in pivot_data.index], rotation=45, ha='right')
ax.legend(title='Timing', loc='lower right')
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.set_ylim(0,1)
# Adjust layout and save the plot
plt.tight_layout()
plt.savefig("2-5 performance influence_WT.png")
plt.show()
