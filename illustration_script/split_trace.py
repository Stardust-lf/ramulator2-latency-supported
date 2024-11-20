import os


def split_trace_folder(input_folder, output_folder_r, output_folder_w):
    """
    Splits all trace files in a folder into two separate folders based on operation type (R or W).
    Additionally, sets the first number of 'W' lines to 0.

    Args:
        input_folder (str): Path to the folder containing input trace files.
        output_folder_r (str): Path to the folder to save files with 'R' lines.
        output_folder_w (str): Path to the folder to save files with 'W' lines.
    """
    # Ensure output directories exist
    os.makedirs(output_folder_r, exist_ok=True)
    os.makedirs(output_folder_w, exist_ok=True)

    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        input_file_path = os.path.join(input_folder, filename)

        # Skip non-files
        if not os.path.isfile(input_file_path):
            continue

        # Define output file paths
        output_file_r = os.path.join(output_folder_r, filename)
        output_file_w = os.path.join(output_folder_w, filename)

        # Process the file
        with open(input_file_path, "r") as infile, \
                open(output_file_r, "w") as outfile_r, \
                open(output_file_w, "w") as outfile_w:

            for line in infile:
                parts = line.split()
                if len(parts) < 2:
                    continue  # Skip malformed lines

                operation = parts[1]
                if operation == "R":
                    outfile_r.write(line)
                elif operation == "W":
                    # Set the first number to 0
                    parts[0] = "0"
                    outfile_w.write(" ".join(parts) + "\n")

        print(f"Processed file: {filename}")


if __name__ == "__main__":
    # Input and output folder paths
    input_folder = "../wb_short_trace"  # Folder containing your input trace files
    output_folder_r = "../wb_traces_R"  # Folder to store 'R' lines
    output_folder_w = "../wb_traces_W"  # Folder to store 'W' lines

    # Split all trace files
    split_trace_folder(input_folder, output_folder_r, output_folder_w)

    print(f"Trace splitting completed!")
    print(f"Files with 'R' lines saved to: {output_folder_r}")
    print(f"Files with 'W' lines saved to: {output_folder_w}")
