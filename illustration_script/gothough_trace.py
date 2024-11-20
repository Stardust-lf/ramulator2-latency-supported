import pandas as pd

def calculate_cost(data, trace_name, timing, request_type):
    """
    Calculate the average cost for a given trace, timing, and request type.

    Args:
        data (pd.DataFrame): DataFrame containing the performance data.
        trace_name (str): The name of the trace to filter.
        timing (str): The timing configuration to filter (e.g., DDR5_6400AN).
        request_type (str): Request type ('read' or 'write').

    Returns:
        float: The average cost, or None if no data is found.
    """
    column_requests = f"total_num_read_requests"
    filtered_data = data[(data['slow_timing'] == timing) & (data['trace'] == trace_name)]

    if not filtered_data.empty:
        return filtered_data["memory_system_cycles"].sum() / filtered_data[column_requests].sum()
    return None


if __name__ == "__main__":
    # Input trace file
    trace_file = "../wb_short_trace/603.trace"
    trace_name = trace_file.split("/")[-1].split('.')[0]

    # Load data
    read_speed_data = pd.read_csv('sus_Rtrace_results.csv')
    write_speed_data = pd.read_csv('sus_Wtrace_results.csv')

    # Calculate costs
    fast_read_cost = calculate_cost(read_speed_data, trace_name, "DDR5_6400AN", "read")
    slow_read_cost = calculate_cost(read_speed_data, trace_name, "DDR5_3200AN", "read")
    fast_write_cost = calculate_cost(write_speed_data, trace_name, "DDR5_6400AN", "write")
    slow_write_cost = calculate_cost(write_speed_data, trace_name, "DDR5_3200AN", "write")

    # Print results
    print(f"Trace Name: {trace_name}")
    print(f"Fast Read Cost: {fast_read_cost if fast_read_cost is not None else 'No data found'}")
    print(f"Slow Read Cost: {slow_read_cost if slow_read_cost is not None else 'No data found'}")
    print(f"Fast Write Cost: {fast_write_cost if fast_write_cost is not None else 'No data found'}")
    print(f"Slow Write Cost: {slow_write_cost if slow_write_cost is not None else 'No data found'}")
