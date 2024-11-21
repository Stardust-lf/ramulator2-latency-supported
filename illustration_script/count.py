from numpy.ma.extras import average


def count_reads_between_writes(trace_file, write_threshold=24):
    read_count = 0
    write_count = 0
    total_writes = 0
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
                total_writes += 1

            if write_count == write_threshold:
                results.append(read_count)
                read_count = 0
                write_count = 0
    print(total_writes)
    write_ratio = total_writes / (total_writes + sum(results)) if (total_writes + sum(results)) > 0 else 0
    return results, write_ratio

# Example usage
trace_file = '../wb_short_trace/602.trace'
results, write_ratio = count_reads_between_writes(trace_file, write_threshold=48)
print(f"Read counts between writes: {average(results)}")
print(f"Write ratio: {write_ratio:.8f}")