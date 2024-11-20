import os

def modify_trace(input_trace_path, output_trace_path):
    """
    Modify a trace file by keeping all 'R' instructions and adding a corresponding 'R'
    instruction before each 'W' instruction with the same address.
    Calculate original and modified write percentages.

    Args:
        input_trace_path (str): Path to the input trace file.
        output_trace_path (str): Path to save the modified trace file.

    Returns:
        tuple: Original write percentage, modified write percentage.
    """
    original_writes = 0
    original_total = 0
    modified_writes = 0
    modified_total = 0
    modified_lines = []

    with open(input_trace_path, "r") as infile:
        for line in infile:
            parts = line.split()
            if len(parts) < 3:
                continue  # Skip malformed lines

            # Identify operation type and address
            operation = parts[1]
            address = parts[2]

            original_total += 1
            if operation == "W":
                original_writes += 1
                # Add an 'R' instruction with the same address before 'W'
                r_line = f"{parts[0]} R {address}\n"
                modified_lines.append(r_line)
                modified_lines.append(line)
                modified_writes += 1  # 'W' is still counted as a write
                modified_total += 2  # Both the new 'R' and original 'W'
            elif operation == "R":
                modified_lines.append(line)
                modified_total += 1

    # Write modified lines to the output file
    with open(output_trace_path, "w") as outfile:
        outfile.writelines(modified_lines)

    original_write_percentage = (original_writes / original_total) * 100 if original_total > 0 else 0
    modified_write_percentage = (modified_writes / modified_total) * 100 if modified_total > 0 else 0

    return original_write_percentage, modified_write_percentage


def modify_all_traces(input_folder, output_folder):
    """
    Modify all trace files in the input folder and save the modified files to the output folder.
    Print original and modified write percentages for each file.

    Args:
        input_folder (str): Path to the input folder containing .trace files.
        output_folder (str): Path to the output folder to save modified .trace files.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".trace"):
            input_trace_path = os.path.join(input_folder, filename)
            output_trace_path = os.path.join(output_folder, filename)

            original_write_percentage, modified_write_percentage = modify_trace(input_trace_path, output_trace_path)

            print(f"File: {filename}")
            print(f"Original Write Percentage: {original_write_percentage:.2f}%")
            print(f"Modified Write Percentage: {modified_write_percentage:.2f}%")
            print("-" * 40)


if __name__ == "__main__":
    # Input and output folder paths
    input_folder = "../wt_short_trace"  # Replace with the first folder's path
    output_folder = "../wt_loadstore_trace"  # Replace with the second folder's path

    # Modify all traces in the input folder
    modify_all_traces(input_folder, output_folder)
    print(f"All traces in {input_folder} have been modified and saved to {output_folder}.")
