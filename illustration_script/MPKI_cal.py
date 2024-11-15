import os
trace_dir = "../short_traces"

trace_files = [filename for filename in os.listdir(trace_dir)]
for trace_name in trace_files:
    adjusted_total_accesses = 0
    adjusted_total_cycles = 0
    with open(f"../short_traces/{trace_name}", 'r') as file:
        for line in file:
            # Split each line into its components
            parts = line.strip().split()
            if len(parts) == 3:
                cycle = int(parts[0])
                operation = parts[1]
                address = parts[2]

                # Adjust cycle count if it exceeds 256
                adjusted_cycle = min(cycle, 256)

                # Count total accesses and track adjusted total cycles
                adjusted_total_accesses += 1
                adjusted_total_cycles += adjusted_cycle

    # Calculate MPKI with adjusted cycles
    adjusted_mpki = adjusted_total_accesses / (adjusted_total_cycles / 1000)

    # Prepare the adjusted results
    adjusted_mpki_results = {
        "Total Memory Accesses": adjusted_total_accesses,
        "Adjusted Total Cycles": adjusted_total_cycles,
        "Adjusted MPKI": adjusted_mpki
    }
    print(adjusted_mpki_results)
