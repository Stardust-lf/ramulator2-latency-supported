import pandas as pd
import matplotlib.pyplot as plt

# Load the uploaded CSV file
file_path = 'sus_doubleW_wb_results.csv'
data = pd.read_csv(file_path)

# Filter data for the two folders: doubleW and wbshorttrace
doubleW_data = data[data['folder'] == 'modified_doubleW_traces']
wbshorttrace_data = data[data['folder'] == 'wb_short_trace']

# Merge the datasets on 'trace' and 'slow_timing' to align the corresponding traces and frequencies
merged_data = pd.merge(doubleW_data, wbshorttrace_data, on=['trace', 'slow_timing'], suffixes=('_doubleW', '_wbshorttrace'))

# Calculate write ratios
merged_data['write_ratio_doubleW'] = (
    merged_data['total_num_write_requests_doubleW'] /
    (merged_data['total_num_write_requests_doubleW'] + merged_data['total_num_read_requests_doubleW'])
)
merged_data['write_ratio_wbshorttrace'] = (
    merged_data['total_num_write_requests_wbshorttrace'] /
    (merged_data['total_num_write_requests_wbshorttrace'] + merged_data['total_num_read_requests_wbshorttrace'])
)

# Calculate average write ratio
merged_data['avg_write_ratio'] = (merged_data['write_ratio_doubleW'] + merged_data['write_ratio_wbshorttrace']) / 2

# Pivot data for plotting
doubleW_system_cycles = merged_data.pivot(index='trace', columns='slow_timing', values='memory_system_cycles_doubleW')
wbshort_system_cycles = merged_data.pivot(index='trace', columns='slow_timing', values='memory_system_cycles_wbshorttrace')
write_ratios = merged_data.pivot(index='trace', columns='slow_timing', values='avg_write_ratio')

# Calculate the updated metric
updated_ratios = (doubleW_system_cycles - wbshort_system_cycles) / wbshort_system_cycles

# Plot the updated metric and write ratios
fig, ax1 = plt.subplots(figsize=(10, 6),dpi=150)

# Define bar width and x positions
width = 0.35
x = range(len(updated_ratios.index))

# Bar plot for the updated metric for both frequencies
ax1.bar(
    [i - width / 2 for i in x],
    updated_ratios.iloc[:, 0],
    width,
    label=updated_ratios.columns[0],
    color='skyblue'
)
ax1.bar(
    [i + width / 2 for i in x],
    updated_ratios.iloc[:, 1],
    width,
    label=updated_ratios.columns[1],
    color='lightcoral'
)

# Configure primary y-axis (Updated Metric)
ax1.set_ylabel('Performance Loss', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.set_xlabel('Trace')
ax1.set_xticks(x)
ax1.set_xticklabels(updated_ratios.index, rotation=45, ha='right')

# Add a secondary y-axis for write ratios
ax2 = ax1.twinx()
ax2.plot(write_ratios.index, write_ratios.iloc[:, 0], color='orange', marker='o', label='Write Ratio - Low Frequency')
ax2.plot(write_ratios.index, write_ratios.iloc[:, 1], color='green', marker='x', label='Write Ratio - High Frequency')
ax2.set_ylabel('Write Operation Ratio', color='orange')
ax2.tick_params(axis='y', labelcolor='orange')

# Add legends and title
fig.suptitle('Performance influence for more W operation')
ax1.legend(loc='upper left', bbox_to_anchor=(0, 1))
ax2.legend(loc='upper right', bbox_to_anchor=(1, 1))
ax1.grid()
# Adjust layout and show the plot
plt.savefig('reduce w merits.png')
plt.tight_layout()
plt.show()
