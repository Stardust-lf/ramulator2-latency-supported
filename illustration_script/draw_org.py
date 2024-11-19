import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.family'] = 'Arial'

# Load the data
data = pd.read_csv('org_perf_results.csv')

# Convert trace column to string for matching dictionary keys
data['trace'] = data['trace'].astype(str)

# Extract frequency and configuration from 'timing' column
data['frequency'] = data['timing'].str.extract(r'DDR5_(\d+)')[0].astype(int)
data['configuration'] = data['timing'].str.extract(r'DDR5_\d+(\w+)')[0]

# Filter for 6400 MHz data only
data_6400 = data[data['frequency'] == 6400]

# Mapping trace names for better readability
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
data_6400['trace_name'] = data_6400['trace'].map(trace_names)

# Define benchmark order based on provided list
custom_order = [
    '600', '602', '605', '620', '623', '625', '631', '641', '648', '657',
    '603', '607', '619', '621', '628', '638', '644', '649', '654',
    'bfs_twi', 'bfs_web', 'bfs_road',
    'bc_twi', 'bc_web', 'bc_road',
    'cc_twi', 'cc_web', 'cc_road',
    'pr_twi', 'pr_web', 'pr_road'
]

# Get ideal_cycles and ideal_wait_cycles for each trace
ideal_data = data_6400[data_6400['organization'] == "DDR5_ideal"]
ideal_cycles = ideal_data.set_index('trace')['memory_system_cycles']
ideal_wait_cycles = ideal_data.set_index('trace')['total_wait_cycles']

# Calculate normalized values: (system_cycles - wait_cycles) / (ideal_cycles - ideal_wait_cycles)
data_6400['normalized_cycles'] = data_6400.apply(
    lambda row: (row['memory_system_cycles'] - row['total_wait_cycles']) /
                (ideal_cycles.get(row['trace'], 1) - ideal_wait_cycles.get(row['trace'], 0)),
    axis=1
)

# Calculate the reciprocal of the normalized values
data_6400['reciprocal_cycles'] = 1 / data_6400['normalized_cycles']

# Filter out zero-height bars and ensure consistent positions for all designs
filtered_positions = []
filtered_traces = []
filtered_values = {org: [] for org in ["DDR5_ideal", "DDR5_baseline1", "DDR5_baseline2", "DDR5_design1", "DDR5_design2"]}

x_counter = 0
for trace in custom_order:
    has_nonzero = False
    for org in filtered_values.keys():
        org_data = data_6400[data_6400['organization'] == org]
        trace_value = org_data[org_data['trace'] == trace]['reciprocal_cycles']
        if not trace_value.empty and trace_value.values[0] > 0:
            filtered_values[org].append(trace_value.values[0])
            has_nonzero = True
        else:
            filtered_values[org].append(0)
    if has_nonzero:
        filtered_positions.append(x_counter)
        filtered_traces.append(trace_names[trace])
        x_counter += 1.5  # Spacing for non-zero bars
    else:
        for org in filtered_values.keys():
            filtered_values[org].pop()  # Remove last appended zero for this trace

# Define improved colors
import matplotlib.cm as cm
color_palette = cm.get_cmap('OrRd', 256)  # Get a colormap with fine granularity
colors = color_palette(np.linspace(0.4, 0.8, 5))  # Focus on the middle range
# Create the plot
fig, ax1 = plt.subplots(figsize=(12, 4), dpi=150)

# Plot Baseline, Design1, and Design2 as separate columns
bar_width = 0.25  # Reduce bar width
for j, org in enumerate(filtered_values.keys()):
    ax1.bar(
        np.array(filtered_positions) + j * bar_width,
        filtered_values[org],
        width=bar_width,
        label=org[5:],
        color=colors[j]
    )

# Customize the left axis
ax1.set_ylabel("Performance", fontsize=14, color="#333333")
ax1.tick_params(axis='y', labelcolor="#333333", labelsize=12)
ax1.set_xticks(np.array(filtered_positions) + 0.5)  # Center the tick labels
ax1.set_xticklabels(filtered_traces, rotation=45, ha="right", fontsize=12)
ax1.grid(axis="y", linestyle="--", alpha=0.7)

# Add legends
ax1.legend(title="Organization",loc='lower right')

# Adjust layout to prevent overlap
plt.tight_layout()
plt.savefig("2-3 lifespan perf.png")
plt.show()
