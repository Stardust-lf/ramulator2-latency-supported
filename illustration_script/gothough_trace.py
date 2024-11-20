import pandas as pd
import numpy as np
import os
def count_reads_between_writes(trace_file, write_threshold=24):
    """
    Counts the number of 'R' operations between every 'write_threshold' (e.g., 24) 'W' operations.

    Args:
        trace_file (str): Path to the input trace file.
        write_threshold (int): Number of 'W' operations to trigger a read count record.

    Returns:
        list: Counts of 'R' operations between every 'write_threshold' 'W' operations.
    """
    read_count = 0
    write_count = 0
    results = []

    with open(trace_file, "r") as infile:
        for line in infile:
            parts = line.split()
            if len(parts) < 2:
                continue  # Skip malformed lines

            operation = parts[1]
            if operation == "R":
                read_count += 1
            elif operation == "W":
                write_count += 1

            # Every time we reach the write_threshold, record the read count and reset
            if write_count == write_threshold:
                results.append(read_count)
                read_count = 0  # Reset read count
                write_count = 0  # Reset write count

    return results

def calculate_cost(data, trace_name, timing, request_type):
    """
    Calculate the average cost for a given trace, timing, and request type.

    Args:
        data (pd.DataFrame): DataFrame containing the performance data.
        trace_name (str): The name of the trace to filter.
        timing (str): The timing configuration to filter (e.g., DDR5_6400AN).
        request_type (str): Request type ('read' or 'write').

    Returns:
        int: The average cost as an integer, or None if no data is found.
    """
    column_requests = f"total_num_read_requests"  # Assuming this column applies to both read and write
    filtered_data = data[(data['slow_timing'] == timing) & (data['trace'] == trace_name)]

    if not filtered_data.empty:
        # Compute average cost and convert to int
        average_cost = (filtered_data["memory_system_cycles"] / filtered_data[column_requests]).sum()
        return int(average_cost)
    return None

def get_total_system_cycles(data, trace_name, timing):
    """
    Get the total system cycles for a given trace and timing.

    Args:
        data (pd.DataFrame): DataFrame containing the performance data.
        trace_name (str): The name of the trace to filter.
        timing (str): The timing configuration to filter (e.g., DDR5_6400AN).

    Returns:
        int: Total system cycles, or None if no data is found.
    """
    filtered_data = data[(data['slow_timing'] == timing) & (data['trace'] == trace_name)]
    if not filtered_data.empty:
        return filtered_data["memory_system_cycles"].sum()
    return None

if __name__ == "__main__":
    write_threshold = 2
    # Define paths
    trace_folder = "../memory_intensive_traces"  # Folder containing trace files
    read_speed_data = pd.read_csv('sus_Rtrace_results.csv')
    write_speed_data = pd.read_csv('sus_Wtrace_results.csv')

    # Iterate through all .trace files in the folder
    for trace_file in os.listdir(trace_folder):
        if not trace_file.endswith(".trace"):
            continue

        trace_path = os.path.join(trace_folder, trace_file)
        trace_name = trace_file.split('.')[0]

        # Calculate costs
        fast_read_cost = calculate_cost(read_speed_data, trace_name, "DDR5_6400AN", "read")
        slow_read_cost = calculate_cost(read_speed_data, trace_name, "DDR5_1600AN", "read")
        fast_write_cost = calculate_cost(write_speed_data, trace_name, "DDR5_6400AN", "write")
        slow_write_cost = calculate_cost(write_speed_data, trace_name, "DDR5_1600AN", "write")

        # Get total system cycles for DDR5_6400AN
        total_system_cycles_6400 = get_total_system_cycles(write_speed_data, trace_name, "DDR5_6400AN")

        # Print results
        print(f"Trace Name: {trace_name}")
        print(f"Fast Read Cost: {fast_read_cost if fast_read_cost is not None else 'No data found'}")
        print(f"Slow Read Cost: {slow_read_cost if slow_read_cost is not None else 'No data found'}")
        print(f"Fast Write Cost: {fast_write_cost if fast_write_cost is not None else 'No data found'}")
        print(f"Slow Write Cost: {slow_write_cost if slow_write_cost is not None else 'No data found'}")

        if fast_read_cost is not None and fast_write_cost is not None and slow_write_cost is not None:
            r_count = count_reads_between_writes(trace_path,write_threshold)
            #print(r_count)
            cost_sum = np.sum([
                max(write_threshold * (slow_write_cost - fast_write_cost) - i * fast_read_cost, 0) for i in r_count
            ])

            if total_system_cycles_6400:
                normalized_cost = cost_sum / total_system_cycles_6400
                print(f"Normalized Cost for {trace_name}: {normalized_cost:.6f}")
            else:
                print(f"Total system cycles for DDR5_6400AN not found for {trace_name}.")
        else:
            print(f"Insufficient data to calculate cost for {trace_name}.")

        print("-" * 40)  # Separator for better readability