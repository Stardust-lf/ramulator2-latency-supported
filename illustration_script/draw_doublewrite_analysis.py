from pydoc import locate

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.family'] = 'Arial'

# Load the data from the first CSV file
file_path = 'doubleW_analysis.csv'  # Replace with the correct file path
data = pd.read_csv(file_path)

# Load the data from the second CSV file
file_path_2 = 'sus_partial_wb_results.csv'  # Replace with the correct file path
data_3200 = pd.read_csv(file_path_2)

# Filter the 3200 system_cycles data
data_3200_filtered = data_3200[data_3200['slow_timing'] == 'DDR5_3200AN'][['trace', 'memory_system_cycles', 'total_wait_cycles']].rename(
    columns={'memory_system_cycles': 'system_cycles_3200', 'total_wait_cycles': 'wait_cycles_3200'}
)

# Merge the two datasets on trace
merged_data = pd.merge(data, data_3200_filtered, on='trace')

# Calculate the normalization base: wb_tag=0 system_cycles for each trace
base_cycles = merged_data[merged_data['dw_tag'] == 0].set_index('trace')['memory_system_cycles']

# Add normalized columns for wb_tag=0, wb_tag=1, and 3200 (inverted)
merged_data['inverted_wb_tag_0'] = merged_data.apply(
    lambda row: base_cycles[row['trace']] / base_cycles[row['trace']]
    if row['trace'] in base_cycles else None,
    axis=1
)
merged_data['inverted_wb_tag_1'] = merged_data.apply(
    lambda row: base_cycles[row['trace']] / row['memory_system_cycles']
    if row['trace'] in base_cycles and row['dw_tag'] == 1 else None,
    axis=1
)
merged_data['inverted_3200'] = merged_data.apply(
    lambda row: base_cycles[row['trace']] / (base_cycles[row['trace']] + row['wait_cycles_3200'])
    if row['trace'] in base_cycles and not pd.isna(row['wait_cycles_3200']) else None,
    axis=1
)

# Pivot the data for plotting
pivot_data = pd.DataFrame({
    'wb_tag_0': merged_data.groupby('trace')['inverted_wb_tag_0'].first(),
    'wb_tag_1': merged_data.groupby('trace')['inverted_wb_tag_1'].first(),
    'adjusted_3200': merged_data.groupby('trace')['inverted_3200'].first()
})

# Define the x positions and bar width
x_positions = np.arange(len(pivot_data))
bar_width = 0.25

# Plotting
fig, ax = plt.subplots(figsize=(12, 4), dpi=150)
import matplotlib.cm as cm
color_palette = cm.get_cmap('OrRd', 256)  # Get a colormap with fine granularity
colors = color_palette(np.linspace(0.4, 0.8, 3))  # Focus on the middle range

# Bar for wb_tag=1
ax.bar(
    x_positions - bar_width,
    pivot_data['wb_tag_1']/ pivot_data['wb_tag_1'],
    width=bar_width,
    label='Baseline',
    color=colors[1]
)

# Bar for wb_tag=0
ax.bar(
    x_positions,
    pivot_data['wb_tag_0'] / pivot_data['wb_tag_1'],
    width=bar_width,
    label='Ideal',
    color=colors[0]
)



# Bar for 3200 system_cycles
ax.bar(
    x_positions + bar_width,
    pivot_data['adjusted_3200']/ pivot_data['wb_tag_1'],
    width=bar_width,
    label='Our design',
    color=colors[2]
)

# Add labels and legend
#ax.set_xlabel('Trace', fontsize=14)
ax.set_ylabel('Normalized Performance', fontsize=14)
#ax.set_title('Inverted Normalized System Cycles by Trace with Adjusted 3200 Timing', fontsize=16)
ax.set_xticks(x_positions)
ax.set_xticklabels(pivot_data.index, rotation=45, ha='right')
ax.legend(loc = "lower right")
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Set Y-axis limit
ax.set_ylim(0.5, None)

# Adjust layout and display the plot
plt.tight_layout()
plt.savefig("2-4 reduce w merits-WB.png")
plt.show()
