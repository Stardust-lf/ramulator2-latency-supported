import os

def process_trace_flip_sixth_bit(trace_lines):
    processed_lines = []
    for line in trace_lines:
        parts = line.split()
        if len(parts) < 3:
            continue  # Skip invalid lines

        prefix = parts[0]
        instruction = parts[1]
        address = int(parts[2])

        if instruction == "W":
            processed_lines.append(line)  # Keep the original line

            # Perform the bit flip on the 6th hexadecimal position (20-23 bits)
            bit_flip_mask = 0x000F0000
            flipped_address = address ^ bit_flip_mask

            # Add the new line with prefix set to 5
            new_prefix = "0"
            flipped_line = f"{new_prefix} {instruction} {flipped_address}\n"
            processed_lines.append(flipped_line)
        else:
            processed_lines.append(line)
    return processed_lines

def process_all_trace_files(input_dir, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Iterate through all files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".trace"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            # Read the input file
            with open(input_path, 'r') as infile:
                trace_lines = infile.readlines()
                print(len(trace_lines))
            # Process the trace
            processed_lines = process_trace_flip_sixth_bit(trace_lines)

            # Write the processed trace to the output file
            with open(output_path, 'w') as outfile:
                outfile.write("".join(processed_lines))

# Define input and output directories
input_directory = "short_traces"  # Replace with the path to your trace folder
output_directory = "processed_traces"  # Replace with the desired output folder

# Process all trace files
process_all_trace_files(input_directory, output_directory)

print(f"All .trace files processed and saved in '{output_directory}'!")
