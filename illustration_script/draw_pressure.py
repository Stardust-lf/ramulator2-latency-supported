import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load your data
file_path = 'sus_pressure_results.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# Filter data for only 6400 MHz
data_6400 = data

# Recalculate sorted traces and write ratio if not defined
write_ratio_by_trace_6400 = data_6400.groupby('trace', group_keys=False).apply(
    lambda df: df['total_num_write_requests'].sum() /
               (df['total_num_write_requests'].sum() + df['total_num_read_requests'].sum()) * 100
)
write_ratio_sorted = write_ratio_by_trace_6400.sort_values()  # Sort write ratios
sorted_traces = write_ratio_sorted.index

# Calculate wait cycles to system cycles ratio for each trace
wait_cycle_ratio = data_6400.groupby('trace', group_keys=False).apply(
    lambda df: df['total_wait_cycles'].sum() / df['memory_system_cycles'].sum()
)
wait_cycle_ratio_sorted = wait_cycle_ratio.loc[sorted_traces]

# Remove the last trace from the sorted traces and related data
sorted_traces_trimmed = sorted_traces[:-1]
write_ratio_sorted_trimmed = write_ratio_sorted[:-1]
wait_cycle_ratio_sorted_trimmed = wait_cycle_ratio_sorted[:-1]

# Replace x-axis labels with Random10 ~ Random80
random_labels = [f"Random{i}" for i in range(10, 10 * (len(sorted_traces_trimmed) + 1), 10)]

# Plot the updated results
fig, ax1 = plt.subplots(figsize=(6, 4), dpi=100)

# Plot wait cycle to system cycle ratio as bars with log scale
ax1.bar(random_labels, wait_cycle_ratio_sorted_trimmed, color="#FF9966", edgecolor="black", label="Wait/System Cycles")
ax1.set_yscale('log')  # Set log scale
ax1.set_ylabel("Performance Loss", fontsize=12, color="#ff7f0e")
ax1.tick_params(axis='y', labelcolor="#ff7f0e")

# Add a secondary y-axis for write ratio
ax2 = ax1.twinx()
ax2.plot(random_labels, write_ratio_sorted_trimmed, color="#1f77b4", marker='o', linestyle='--', label="Write Ratio (%)")
ax2.set_ylabel("Write Ratio (%)", fontsize=12, color="#1f77b4")
ax2.tick_params(axis='y', labelcolor="#1f77b4")

# Set x-axis labels
ax1.set_xlabel("Traces (Sorted by Write Ratio)", fontsize=12)
ax1.set_xticks(range(len(random_labels)))
ax1.set_xticklabels(random_labels, rotation=45, ha='right')

# Add legends
fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.85), fontsize=10)

# Add grid for better readability
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# Adjust layout
plt.tight_layout()
plt.savefig("Pressure_test_3200AN.png")
plt.show()
