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

# Calculate write latencies and write queue lengths for 3200 and 6400 configurations
write_latency_3200 = data_3200.groupby('trace')['avg_write_latency_0'].mean()
write_latency_6400 = data_6400.groupby('trace')['avg_write_latency_0'].mean()
write_queue_3200 = data_3200.groupby('trace')['write_queue_len_0'].mean()
write_queue_6400 = data_6400.groupby('trace')['write_queue_len_0'].mean()

# Sort traces by their alignment
sorted_traces = sorted(aligned_traces)
sorted_write_latency_3200 = write_latency_3200.reindex(sorted_traces)
sorted_write_latency_6400 = write_latency_6400.reindex(sorted_traces)
sorted_write_queue_3200 = write_queue_3200.reindex(sorted_traces)
sorted_write_queue_6400 = write_queue_6400.reindex(sorted_traces)

# Prepare labels
random_labels = [f"Random{i}" for i in range(10, 10 * (len(sorted_traces) + 1), 10)]

# Plot the results
fig, ax1 = plt.subplots(figsize=(8, 6), dpi=120)

# Plot write latencies on the left y-axis
ax1.plot(random_labels, sorted_write_latency_3200.values, color="red", marker='o', label="Design queue latency")
ax1.plot(random_labels, sorted_write_latency_6400.values, color="blue", marker='s', label="Baseline queue latency")
ax1.set_ylabel("Write Latency (cycles)", fontsize=12)
ax1.set_xlabel("Traces", fontsize=12)
ax1.set_xticks(range(len(random_labels)))
ax1.set_xticklabels(random_labels, rotation=45, ha="right")
ax1.tick_params(axis='y', labelcolor="black")
ax1.grid(axis='y')

# Set y-axis limits for the first axis
ax1.set_ylim(0, max(sorted_write_latency_3200.max(), sorted_write_latency_6400.max()) * 1.2)

# Add a secondary y-axis for write queue length
ax2 = ax1.twinx()
ax2.plot(random_labels, sorted_write_queue_3200.values, color="green", marker='^', linestyle='--', label="Design queue length")
ax2.plot(random_labels, sorted_write_queue_6400.values, color="purple", marker='v', linestyle='--', label="Baseline queue length")
ax2.set_ylabel("Write Queue Length", fontsize=12)
ax2.tick_params(axis='y', labelcolor="black")

# Set y-axis limits for the second axis
ax2.set_ylim(0, max(sorted_write_queue_3200.max(), sorted_write_queue_6400.max()) * 1.2)

# Add legends for both axes
ax1.legend(loc='upper left', fontsize=10)
ax2.legend(loc='upper right', fontsize=10)

# Adjust layout and save the plot
plt.tight_layout()
plt.savefig("latency_and_queue_length_zero_based.png")
plt.show()
