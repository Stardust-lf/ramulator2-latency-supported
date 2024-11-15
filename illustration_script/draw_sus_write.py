import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
data = pd.read_csv('sus_final_results.csv')

# Convert trace column to string for matching dictionary keys
data['trace'] = data['trace'].astype(str)

# Extract frequency and configuration from the 'slow_timing' column
data['frequency'] = data['slow_timing'].str.extract(r'DDR5_(\d+)')[0]
data['configuration'] = data['slow_timing'].str.extract(r'DDR5_\d+(\w+)')[0]

# Calculate write latency for each configuration
data['write_latency'] = data['total_wait_cycles'] / data['total_num_write_requests']

# Calculate write ratio
data['write_ratio'] = (data['total_num_write_requests'] * 100) / (
    data['total_num_write_requests'] + data['total_num_read_requests'])

# Filter 6400 AN data for baseline comparisons
baseline_6400_an = data[(data['frequency'] == '6400') & (data['configuration'] == 'AN')]

# Initialize a dictionary to store baseline latencies for each trace
baseline_latencies = baseline_6400_an.set_index('trace')['write_latency'].to_dict()

# Filter unique frequencies excluding 6400
frequencies = [freq for freq in data['frequency'].unique() if freq != '6400']

# Define consistent order for traces
custom_trace_order = ['623', '603', '602', '605', '607', '621', '628', '654', '619', '620']

# Trace name mapping
trace_names = {
    '600': 'perlbench', '602': 'gcc', '605': 'mcf', '620': 'omnetpp', '623': 'xalancbmk',
    '625': 'x264', '631': 'deepsjeng', '641': 'leela', '648': 'exchange2', '657': 'xz',
    '603': 'bwaves', '607': 'cactuBSSN', '619': 'lbm', '621': 'wrf', '627': 'cam4',
    '628': 'pop2', '638': 'imagick', '644': 'nab', '649': 'fotonik3d', '654': 'roms'
}
mapped_trace_names = [trace_names.get(trace, trace) for trace in custom_trace_order]

# Define x-axis positions
x_positions = np.arange(len(custom_trace_order))
width = 0.25

# Create subplots for two rows and four columns
num_columns = 4
num_rows = 2
fig, axs = plt.subplots(num_rows, num_columns, figsize=(12, 8), dpi=150, sharey=True, sharex=True)
axs = axs.flatten()

# Define colors
bar_color = '#FFCC99'  # For latency impact bars
write_ratio_color = '#1f77b4'  # For write ratio line

# Plot each frequency in a separate subplot
for idx, freq in enumerate(frequencies):
    # Filter data for the current frequency and configuration AN
    data_freq_an = data[(data['frequency'] == freq) & (data['configuration'] == 'AN')]

    # Skip empty datasets
    if data_freq_an.empty:
        continue

    # Plot data in the corresponding subplot
    ax1 = axs[idx]

    # Calculate write latency impact for each trace, set values below 0 to 0
    impact_values = [
        max(
            ((data_freq_an[data_freq_an['trace'] == trace]['write_latency'].values[0] - baseline_latencies[trace]) /
             baseline_latencies[trace]),
            0  # Ensure values below 0 are set to 0
        )
        if trace in baseline_latencies and not data_freq_an[data_freq_an['trace'] == trace].empty else 0
        for trace in custom_trace_order
    ]

    # Plot impact values as bars
    ax1.bar(x_positions, impact_values, width=width, label=f"{freq} AN", color=bar_color)

    # Set y-axis to log scale for write latency impact
    ax1.set_yscale('log')
    ax1.set_ylabel("Write Speed Loss (%)", fontsize=10, color="#ff7f0e")
    ax1.tick_params(axis='y', labelcolor="#ff7f0e")
    ax1.set_title(f"DDR5 {freq} MHz", fontsize=12)

    # Add a secondary y-axis for write ratio
    ax2 = ax1.twinx()
    write_ratio_values = [
        data_freq_an[data_freq_an['trace'] == trace]['write_ratio'].values[0]
        if not data_freq_an[data_freq_an['trace'] == trace].empty else 0
        for trace in custom_trace_order
    ]
    ax2.plot(x_positions, write_ratio_values, color=write_ratio_color, marker='o', linestyle='--', label="Write Ratio (%)")
    #ax2.set_ylabel("Write Ratio (%)", fontsize=10, color=write_ratio_color)
    ax2.tick_params(axis='y', labelcolor=write_ratio_color)

    # Set x-axis ticks and labels
    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(mapped_trace_names, rotation=45, ha="right")

    # Add grid for better readability
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

# Hide unused subplots
for i in range(len(frequencies), len(axs)):
    fig.delaxes(axs[i])

# Adjust layout to prevent overlap
plt.tight_layout()
plt.legend()
plt.savefig('../figures/write_latency_impact_with_write_ratio_log_two_rows_four_columns.png')
plt.show()
