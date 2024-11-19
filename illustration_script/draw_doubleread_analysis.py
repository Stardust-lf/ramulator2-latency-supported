import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
plt.rcParams['font.family'] = 'Arial'
# plt.rcParams['font.weight'] = 'black'
# Load the data from the uploaded file
file_path = 'sus_doubleR_wb_results.csv'
data = pd.read_csv(file_path)

# Pivot data to include all traces and probabilities with memory system cycles
pivot_data_full = data.pivot_table(
    index='trace',
    columns='probability',
    values='memory_system_cycles',
    aggfunc='first'
).fillna(0)

# Calculate the inverse of memory system cycles for all probabilities
pivot_data_full_inverse = 1 / pivot_data_full.replace(0, np.nan)  # Avoid division by zero

# Replace NaN back to 0 for visualization purposes
pivot_data_full_inverse = pivot_data_full_inverse.fillna(0)

# Extract the inverse values for probability = 0 as the baseline
baseline_inverse = pivot_data_full_inverse[0]

# Normalize all inverse values by dividing by the baseline for each trace
pivot_data_normalized = pivot_data_full_inverse.div(baseline_inverse, axis=0).fillna(0)

# Cap all normalized values at 1
pivot_data_normalized_capped = pivot_data_normalized.clip(upper=1)

# Ensure that higher probability columns are not greater than lower probability columns
for i in range(1, len(pivot_data_normalized_capped.columns)):
    lower_prob_col = pivot_data_normalized_capped.columns[i - 1]
    current_prob_col = pivot_data_normalized_capped.columns[i]
    # Ensure current column values are less than or equal to the previous column
    pivot_data_normalized_capped[current_prob_col] = np.minimum(
        pivot_data_normalized_capped[current_prob_col],
        pivot_data_normalized_capped[lower_prob_col]
    )

# Custom trace order and names
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

# Filter custom_trace_order to include only traces present in the DataFrame
existing_traces = [trace for trace in custom_trace_order if trace in pivot_data_normalized_capped.index]

# Reorder the DataFrame based on the filtered trace order
pivot_data_normalized_capped = pivot_data_normalized_capped.loc[existing_traces]

# Rename traces in the index based on the provided trace names
pivot_data_normalized_capped.rename(index=trace_names, inplace=True)

# Define the x positions and bar width
x_positions = np.arange(len(pivot_data_normalized_capped))
bar_width = 0.15

# Adjust the colormap mapping to make the leftmost color less pale
color_palette = cm.get_cmap('OrRd', 256)  # Get a colormap with fine granularity
adjusted_colors = color_palette(np.linspace(0.4, 0.8, len(pivot_data_normalized_capped.columns)))  # Focus on the middle range

# Prepare the plot with updated color mapping
fig, ax = plt.subplots(figsize=(12, 4), dpi=150)

# Adjusted label formatting to show percentages
for i, probability in enumerate(pivot_data_normalized_capped.columns):
    ax.bar(
        x_positions + i * bar_width,
        pivot_data_normalized_capped[probability],
        width=bar_width,
        label=f'{float(probability) * 100:.5g}%',  # Convert to percentage with proper formatting
        color=adjusted_colors[i]  # Use the adjusted colors
    )

# Add labels, legend, and grid with improved styling
#ax.set_xlabel('Trace', fontsize=14)
ax.set_ylabel('Normalized Performance', fontsize=14)
ax.set_xticks(x_positions + (len(pivot_data_normalized_capped.columns) - 1) * bar_width / 2)
ax.set_xticklabels(pivot_data_normalized_capped.index, rotation=45, ha='right')
ax.legend(title='Error Rate', loc='lower right', fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.set_ylim(0.8, 1)

# Adjust layout and display the plot
plt.tight_layout()
plt.savefig("1-3 correction impact.png")
plt.show()
