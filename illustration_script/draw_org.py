import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
data = pd.read_csv('org_perf_results.csv')
#plt.rcParams["font.family"] = "Times New Roman"

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
    '603': 'bwaves', '607': 'cactuBSSN', '619': 'lbm', '621': 'wrf', '627': 'cam4',
    '628': 'pop2', '638': 'imagick', '644': 'nab', '649': 'fotonik3d', '654': 'roms'
}
data_6400['trace_name'] = data_6400['trace'].map(trace_names)

# Define benchmark order based on provided list
custom_order = ['623', '603', '602', '605', '607', '621', '628', '654', '619', '620']
unique_traces = [trace_names[trace] for trace in custom_order]

# Define x-axis positions
x_positions = np.arange(len(unique_traces))

# Define colors for the three designs
colors = ['#FFCC99', '#FF9966', '#FF6600']  # Lightest to darkest orange

# Calculate write operation ratio for each trace
write_ratio = data_6400.groupby('trace').apply(
    lambda df: df['total_num_write_requests'].sum() /
               (df['total_num_write_requests'].sum() + df['total_num_read_requests'].sum()) * 100
)
write_ratio_sorted = [write_ratio[trace] if trace in write_ratio else 0 for trace in custom_order]

# Create the plot
fig, ax1 = plt.subplots(figsize=(8, 6),dpi=100)

# Plot Baseline, Design1, and Design2 as separate columns
for j, org in enumerate(["DDR5_baseline", "DDR5_design", "DDR5_design2"]):
    org_data = data_6400[data_6400['organization'] == org]

    # Get y-values for each trace in the custom order
    y_values = [org_data[org_data['trace'] == trace]['memory_system_cycles'].values[0]
                if trace in org_data['trace'].values else 0
                for trace in custom_order]

    # Plot bars with an offset for each design
    ax1.bar(x_positions + j * 0.25, y_values, width=0.25, label=org, color=colors[j])

# Customize the left axis
ax1.set_ylabel("Memory System Cycles", fontsize=12, color="#ff7f0e")
ax1.tick_params(axis='y', labelcolor="#ff7f0e")
ax1.set_xticks(x_positions + 0.25)
ax1.set_xticklabels(unique_traces, rotation=45, ha="right")
ax1.grid(axis="y", linestyle="--", alpha=0.7)

# Add a secondary y-axis for write ratio
ax2 = ax1.twinx()
ax2.plot(x_positions + 0.25, write_ratio_sorted, color="#1f77b4", marker='o', linestyle='--', label="Write Ratio (%)")
ax2.set_ylabel("Write Ratio (%)", fontsize=12, color="#1f77b4")
ax2.tick_params(axis='y', labelcolor="#1f77b4")

# Add legends
fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.85), fontsize=10, title="Legend")

# Set plot title
#ax1.set_title("Memory System Cycles and Write Ratio for 6400 MHz by Benchmark", fontsize=16)

# Adjust layout to prevent overlap
plt.tight_layout()
plt.savefig("Org_design")
plt.show()
