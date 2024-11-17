import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the CSV file
file_path = 'sus_pressure_results.csv'  # Replace with your actual file path
data = pd.read_csv(file_path)

# Filter data for 3200 and 6400 configurations
data_3200 = data[data['slow_timing'] == 'DDR5_3200AN']
data_6400 = data[data['slow_timing'] == 'DDR5_6400AN']

# Ensure traces are aligned between 3200 and 6400 configurations
aligned_traces = set(data_3200['trace']).intersection(set(data_6400['trace']))
data_3200 = data_3200[data_3200['trace'].isin(aligned_traces)]
data_6400 = data_6400[data_6400['trace'].isin(aligned_traces)]

# Calculate the performance difference ratio for each trace
performance_diff_ratio = (
    data_3200.groupby('trace')['memory_system_cycles'].sum()
    - data_6400.groupby('trace')['memory_system_cycles'].sum()
) * 100 / data_6400.groupby('trace')['memory_system_cycles'].sum()

# Calculate write ratios for 3200 and 6400 configurations
write_ratio_3200 = data_3200.groupby('trace').apply(
    lambda x: x['total_num_write_requests'].sum() * 100 /
              (x['total_num_write_requests'].sum() + x['total_num_read_requests'].sum())
)
write_ratio_6400 = data_6400.groupby('trace').apply(
    lambda x: x['total_num_write_requests'].sum() * 100 /
              (x['total_num_write_requests'].sum() + x['total_num_read_requests'].sum())
)

# Average write ratio across 3200 and 6400 configurations
average_write_ratio = (write_ratio_3200 + write_ratio_6400) / 2

# Sort traces by average write ratio (low to high)
sorted_traces = average_write_ratio.sort_values().index
sorted_performance_diff_ratio = performance_diff_ratio.reindex(sorted_traces)
sorted_write_ratio = average_write_ratio.reindex(sorted_traces)

# Prepare labels
random_labels = [f"Random{i}" for i in range(10, 10 * (len(sorted_traces) + 1), 10)]

# Plot the results
fig, ax1 = plt.subplots(figsize=(6, 4), dpi=100)

# Bar plot of the performance difference ratio (left y-axis)
ax1.set_title("Pressure exp for 3200AN on 6400AN")
ax1.bar(random_labels, sorted_performance_diff_ratio.values, color="#FF9966", label="Performance Difference Ratio")
ax1.set_ylabel("Performance Loss(%)")
#ax1.set_xlabel("Traces", fontsize=12)
ax1.set_xticks(range(len(random_labels)))
ax1.set_xticklabels([])
ax1.set_yscale('log')  # Set y-axis to logarithmic scale
ax1.grid()

# Add a secondary y-axis for write ratio
ax2 = ax1.twinx()
ax2.plot(random_labels, sorted_write_ratio.values, color="blue", marker='o', label="Write Ratio (%)")
ax2.set_ylabel("Write Ratio (%)", fontsize=10, color='blue')
ax2.tick_params(axis='y', labelcolor='blue')

# Add legends
ax1.legend(loc='upper left', fontsize=10)
ax2.legend(loc='upper right', fontsize=10)

# Adjust layout and save the plot
plt.tight_layout()
plt.savefig("2-2 write pressure.png")
plt.show()
