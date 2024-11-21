import os
from hyperparams import trace_names


def process_trace_file(input_file_path, output_file_path):
    input_line_count = 0
    output_line_count = 0

    with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
        last_address = None
        last_operation = None
        for line in infile:
            input_line_count += 1
            parts = line.strip().split()
            if len(parts) == 3:
                address_str = parts[2]

                # Detect hexadecimal addresses starting with "0x"
                if address_str.startswith("0x"):
                    address = int(address_str, 16)  # Convert address from hex to integer
                else:
                    address = int(address_str)  # Convert address from decimal to integer

                address = address & ~0x7F  # Set the lower 7 bits to 0

                # Check if the operation and address are the same as the last one
                current_operation = parts[1]
                if last_operation == current_operation and last_address == address:
                    continue  # Skip consecutive identical operations
                else:
                    last_address = address
                    last_operation = current_operation

                # Write the processed line
                outfile.write(f"{parts[0]} {current_operation} {hex(address)}\n")
                output_line_count += 1
                if output_line_count >= 1000000:
                    break

    # Print input and output line counts
    print(f"File: {input_file_path}")
    print(f"Input Lines: {input_line_count}, Output Lines: {output_line_count}")


def process_trace_folder(input_folder, output_folder):
    # Check if output folder exists, if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process each trace file in the folder
    for filename in trace_names:
        if filename.endswith('.txt') or filename.endswith('.trace'):  # Modify based on your file extension
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)
            process_trace_file(input_file_path, output_file_path)
            print(f"Processed {filename} and saved to {output_folder}\n")


# Input folder and output folder paths
input_folder = "../offest_base_traces"  # Replace with your input folder path
output_folder = "../offest_128_traces"  # Replace with your output folder path

# Process the folder
process_trace_folder(input_folder, output_folder)
