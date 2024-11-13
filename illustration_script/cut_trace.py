import os


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

            # Write the processed trace to the output file
            with open(output_path, 'w') as outfile:
                outfile.write("".join(trace_lines[:1000000]))

# Define input and output directories
input_directory = "../final_traces"  # Replace with the path to your trace folder
output_directory = "../short_traces"  # Replace with the desired output folder

# Process all trace files
process_all_trace_files(input_directory, output_directory)

print(f"All .trace files processed and saved in '{output_directory}'!")
