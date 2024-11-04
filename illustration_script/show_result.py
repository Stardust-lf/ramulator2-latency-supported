import pandas as pd
import matplotlib.pyplot as plt

# Load the data from CSV
data = pd.read_csv('sus_perf_results.csv')
plt.rcParams["font.family"] = "Times New Roman"

# Dictionary of trace names for legend
trace_names = {
    '600': 'perlbench', '602': 'gcc', '605': 'mcf', '620': 'omnetpp', '623': 'xalancbmk',
    '625': 'x264', '631': 'deepsjeng', '641': 'leela', '648': 'exchange2', '657': 'xz',
    '603': 'bwaves', '607': 'cactuBSSN', '619': 'lbm', '621': 'wrf', '627': 'cam4',
    '628': 'pop2', '638': 'imagick', '644': 'nab', '649': 'fotonik3d', '654': 'roms'
}

# Convert avg_write_latency_0 to time in seconds using tCK_ps = 625 ps
tCK_ps = 625e-12  # 625 ps in seconds
print(data.keys())
# Filter out rows with NaN in relevant columns if necessary
data = data[data['avg_write_latency_0'] != 'NaN']
data['avg_write_latency_0'] = pd.to_numeric(data['avg_write_latency_0'])
data['cycles_recorded_core_0'] = pd.to_numeric(data['memory_system_cycles'], errors='coerce')
data['total_num_write_requests'] = pd.to_numeric(data['total_num_write_requests'], errors='coerce')
data['total_num_read_requests'] = pd.to_numeric(data['total_num_read_requests'], errors='coerce')

# Convert avg_write_latency_0 (cycles) to latency in seconds
data['latency_seconds'] = data['avg_write_latency_0'] * tCK_ps

# Calculate write performance in Instructions per Millisecond (IMs)
data['write_performance_ms'] = 1 / (data['latency_seconds'] * 1e3)  # Write instructions per millisecond

# Calculate total request rate as total instructions per millisecond
data['total_request_rate_ms'] = (data['total_num_write_requests'] + data['total_num_read_requests']) / (data['cycles_recorded_core_0'] * tCK_ps * 1e3)

# Remove traces with NaN values
traces_without_nan = data.groupby('trace').filter(lambda x: not x['write_performance_ms'].isna().any() and not x['total_request_rate_ms'].isna().any())

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# First plot: Write Instructions per Millisecond vs Slow Chip Perf
for trace, group in traces_without_nan.groupby('trace'):
    if trace == '602.trace':  # Skip the trace with code '602'
        continue
    trace_label = trace_names.get(str(trace), trace)  # Use descriptive name or default to trace code
    ax1.plot(group['slow_chip_perf'], group['write_performance_ms'])
    ax1.scatter(group['slow_chip_perf'], group['write_performance_ms'], s=9, label=trace_label)

# Customize the first plot
ax1.set_ylabel('Write Instructions per Millisecond (IMs)')
ax1.legend(title='SPEC 2017', bbox_to_anchor=(1.05, 1), loc='upper left')
ax1.set_xlabel('Slow Chip Perf')
ax1.grid(True)

# Second plot: Total Instructions per Millisecond vs Slow Chip Perf
for trace, group in traces_without_nan.groupby('trace'):
    if trace == '602.trace':  # Skip the trace with code '602'
        continue
    trace_label = trace_names.get(str(trace), trace)
    ax2.plot(group['slow_chip_perf'], group['total_request_rate_ms'])
    ax2.scatter(group['slow_chip_perf'], group['total_request_rate_ms'], s=9, label=trace_label)

# Customize the second plot
ax2.set_xlabel('Slow Chip Perf')
ax2.set_ylabel('Total Instructions per Millisecond (IMs)')
ax2.grid(True)

# Invert the x-axis on both subplots
ax1.invert_xaxis()
ax2.invert_xaxis()

# Adjust layout and show the plot
plt.tight_layout()
plt.savefig('susLatency')
plt.show()
