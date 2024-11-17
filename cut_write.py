import os

def process_file(input_file, output_file, max_lines=10**6):
    """
    Process a file by retaining the first `max_lines` lines and performing mod 2^64 on the address field.

    Args:
        input_file (str): Path to the input file.
        output_file (str): Path to the output file.
        max_lines (int): Maximum number of lines to retain.
    """

    with open(input_file, 'r') as infile, open(output_file, 'w+') as outfile:
        for i, line in enumerate(infile):
            if i >= max_lines:
                break
            parts = line.strip().split()
            parts[0] = min(int(parts[0]),256)
            if len(parts) == 3:  # Ensure line has the correct format
                address = int(parts[2]) % (2**64)  # Perform mod 2^64

                outfile.write('{} {} {}\n'.format(parts[0],parts[1],address))
            else:
                outfile.write(line)  # Write the line as-is if the format is incorrect
    print(f"Processed: {input_file} -> {output_file}")


def process_folder(folder_path, output_folder, max_lines=10**6):
    """
    Process all files in a folder by retaining the first `max_lines` lines and performing mod 2^64 on addresses.

    Args:
        folder_path (str): Path to the folder containing input files.
        output_folder (str): Path to the folder where output files will be saved.
        max_lines (int): Maximum number of lines to retain.
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(folder_path):
        input_file = os.path.join(folder_path, filename)
        if os.path.isfile(input_file):  # Process only files
            output_file = os.path.join(output_folder, filename)
            process_file(input_file, output_file, max_lines)
# Example usage
input_folder = "wb_traces"  # Replace with the path to your input folder
output_folder = "wb_short_trace"  # Replace with the path to your output folder
process_folder(input_folder, output_folder)
