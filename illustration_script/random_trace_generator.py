import random


def generate_ordered_address_trace(num_entries, rw_ratio, min_address, max_address, alignment):
    """
    Generates a trace with a specific RW ratio and orderly pattern.

    Args:
        num_entries (int): Total number of trace entries to generate.
        rw_ratio (tuple): Ratio of reads to writes (e.g., (2, 1) for RRW).
        min_address (int): Minimum address (inclusive) for generated addresses.
        max_address (int): Maximum address (inclusive) for generated addresses.
        alignment (int): Required alignment for the generated addresses.

    Returns:
        list: List of trace strings in the required format.
    """
    read_ratio, write_ratio = rw_ratio
    ratio_sum = read_ratio + write_ratio

    # Adjust num_entries if it is not divisible by the RW ratio sum
    if num_entries % ratio_sum != 0:
        adjusted_entries = (num_entries // ratio_sum) * ratio_sum
        print(f"Adjusted num_entries from {num_entries} to {adjusted_entries} to match the RW ratio.")
        num_entries = adjusted_entries

    trace = []
    total_read = num_entries * read_ratio // ratio_sum
    total_write = num_entries - total_read

    # Generate sequential addresses for reads and writes
    read_addresses = [
        addr * alignment for addr in range(
            (min_address + alignment - 1) // alignment,
            (min_address + alignment - 1) // alignment + total_read,
        )
    ]
    write_addresses = [
        addr * alignment for addr in range(
            (min_address + alignment - 1) // alignment + total_read,
            (min_address + alignment - 1) // alignment + total_read + total_write,
        )
    ]

    # Interleave addresses based on the RW ratio
    read_count, write_count = 0, 0
    pattern_length = ratio_sum
    for _ in range(num_entries // pattern_length):
        trace.extend(
            [f"0 R {read_addresses[read_count + i]}" for i in range(read_ratio)]
        )
        read_count += read_ratio
        trace.extend(
            [f"0 W {write_addresses[write_count + i]}" for i in range(write_ratio)]
        )
        write_count += write_ratio

    return trace


if __name__ == "__main__":
    # Parameters
    num_entries = 100000  # Total number of trace entries to generate
    min_address = 0x10000000  # Minimum address
    max_address = 0xFFFFFFFF  # Maximum address
    alignment = 64  # Addresses must be aligned to 64 bytes

    # Iterate through RW ratios from 9:1 to 1:9
    for read_ratio in [10,0,5]:
        write_ratio = 10 - read_ratio
        rw_ratio = (read_ratio, write_ratio)
        print(f"Generating trace for R:W = {read_ratio}:{write_ratio}")

        # Generate the trace
        ordered_trace = generate_ordered_address_trace(num_entries, rw_ratio, min_address, max_address, alignment)

        # Save to a file
        output_file = f"../ordered_traces/RW{read_ratio}_{write_ratio}.trace"
        with open(output_file, "w") as f:
            f.write("\n".join(ordered_trace))

        print(f"Ordered trace for R:W = {read_ratio}:{write_ratio} saved to {output_file}!")
