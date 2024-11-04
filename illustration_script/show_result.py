import pandas as pd
import matplotlib.pyplot as plt

# Load the data from CSV
data = pd.read_csv('sus_perf_results.csv')
plt.rcParams["font.family"] = "Times New Roman"

# Dictionary of trace names for labeling the plots
trace_names = {
    '600': 'perlbench', '602': 'gcc', '605': 'mcf', '620': 'omnetpp', '623': 'xalancbmk',
    '625': 'x264', '631': 'deepsjeng', '641': 'leela', '648': 'exchange2', '657': 'xz',
    '603': 'bwaves', '607': 'cactuBSSN', '619': 'lbm', '621': 'wrf', '627': 'cam4',
    '628': 'pop2', '638': 'imagick', '644': 'nab', '649': 'fotonik3d', '654': 'roms'
}

# Convert trace column to string for easier matching with the dictionary keys
data['trace'] = data['trace'].astype(str)

# Set up grid layout with 3 columns and sufficient rows based on the number of traces
num_columns = 3
num_rows = (len(data['trace'].unique()) + num_columns - 1) // num_columns

fig, axs = plt.subplots(num_rows, num_columns, figsize=(15, num_rows * 3), sharex=True)
fig.suptitle("Wait Times Across Frequency Configurations for Each Trace", fontsize=16)

# Plot each trace in a grid
for i, trace in enumerate(data['trace'].unique()):
    row, col = divmod(i, num_columns)
    trace_data = data[data['trace'] == trace]
    axs[row, col].plot(trace_data['slow_timing'], trace_data['total_wait_cycles'], marker='o')
    axs[row, col].set_title(trace_names.get(trace, f'Trace {trace}'))
    axs[row, col].set_ylabel('Total Wait Cycles')
    axs[row, col].grid(True)

# Hide any unused subplots
for j in range(i + 1, num_rows * num_columns):
    fig.delaxes(axs[j // num_columns, j % num_columns])

# Set a common x-label for all plots
fig.text(0.5, 0.04, 'Frequency Configuration', ha='center')

# Adjust layout to prevent overlap
plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.show()
