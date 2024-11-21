import pandas as pd
import numpy as np
import os

def count_reads_between_writes(trace_file, write_threshold=24):
    read_count = 0
    write_count = 0
    results = []

    with open(trace_file, "r") as infile:
        for line in infile:
            parts = line.split()
            if len(parts) < 2:
                continue

            operation = parts[1]
            if operation == "R":
                read_count += 1
            elif operation == "W":
                write_count += 1

            if write_count == write_threshold:
                results.append(read_count)
                read_count = 0
                write_count = 0

    return results

def calculate_cost(data, trace_name, timing, request_type):
    column_requests = f"total_num_read_requests"
    filtered_data = data[(data['slow_timing'] == timing) & (data['trace'] == trace_name)]

    if not filtered_data.empty:
        average_cost = (filtered_data["memory_system_cycles"] / filtered_data[column_requests]).sum()
        return int(average_cost)
    return None

def get_total_system_cycles(data, trace_name, timing):
    filtered_data = data[(data['slow_timing'] == timing) & (data['trace'] == trace_name)]
    if not filtered_data.empty:
        return filtered_data["memory_system_cycles"].sum()
    return None

def calculate_write_proportion(trace_file):
    total_operations = 0
    write_operations = 0

    with open(trace_file, "r") as infile:
        for line in infile:
            parts = line.split()
            if len(parts) < 2:
                continue

            total_operations += 1
            if parts[1] == "W":
                write_operations += 1

    if total_operations > 0:
        return write_operations / total_operations
    return 0.0

# Initialize results storage for different write thresholds
all_results = []

# Configuration
write_thresholds = [6, 12, 24, 48]
trace_folder = "../wb_short_trace"
read_speed_data = pd.read_csv('sus_Rtrace_results.csv')
write_speed_data = pd.read_csv('sus_Wtrace_results.csv')
slow_chips = ["DDR5_1600AN", "DDR5_3200AN", "DDR5_6400AN"]

# Process traces for each threshold
for write_threshold in write_thresholds:
    for slow_chip in slow_chips:
        for trace_file in os.listdir(trace_folder):
            if not trace_file.endswith(".trace"):
                continue

            trace_path = os.path.join(trace_folder, trace_file)
            trace_name = trace_file.split('.')[0]

            # Calculate costs
            fast_read_cost = calculate_cost(read_speed_data, trace_name, "DDR5_6400AN", "read")
            fast_write_cost = calculate_cost(write_speed_data, trace_name, "DDR5_6400AN", "read")
            slow_write_cost = calculate_cost(write_speed_data, trace_name, slow_chip, "read")
            total_system_cycles_6400 = get_total_system_cycles(write_speed_data, trace_name, "DDR5_6400AN")
            write_proportion = calculate_write_proportion(trace_path)

            # Analyze costs
            if fast_read_cost is not None and fast_write_cost is not None and slow_write_cost is not None:
                r_count = count_reads_between_writes(trace_path, write_threshold)
                cost_sum = np.sum([
                    max(write_threshold * (slow_write_cost - fast_write_cost) - i * fast_read_cost, 0) for i in r_count
                ])
                normalized_cost = cost_sum / total_system_cycles_6400 if total_system_cycles_6400 else None
            else:
                normalized_cost = None
            # Collect results
            all_results.append({
                "Write Threshold": write_threshold,
                "Trace Name": trace_name,
                "Slow Chip": slow_chip,
                "Fast Read Cost": fast_read_cost,
                "Fast Write Cost": fast_write_cost,
                "Slow Write Cost": slow_write_cost,
                "Write Proportion": write_proportion,
                "Average Read Block Size": np.average(r_count) if len(r_count) != 0 else 0,
                "Normalized Cost (%)": 100 * normalized_cost if normalized_cost is not None else None
            })

# Save results to CSV
all_results_df = pd.DataFrame(all_results)
output_file = "avg_latency_results_multiple_thresholds.csv"
all_results_df.to_csv(output_file, index=False)