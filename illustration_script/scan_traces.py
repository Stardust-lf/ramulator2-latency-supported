import os


def scan_trace_file_for_low_5_bits(input_file_path):
    with open(input_file_path, 'r') as infile:
        line_number = 0
        invalid_addresses = []

        for line in infile:
            line_number += 1
            parts = line.strip().split()
            if len(parts) == 3:
                address = int(parts[2])  # 将地址转换为整数
                if address & 0x1F != 0:  # 检查低 5 位是否为 0
                    invalid_addresses.append((line_number, parts[2]))

        # 汇报结果
        if invalid_addresses:
            print(f"File: {input_file_path}")
            for line_num, addr in invalid_addresses:
                print(f"Line {line_num}: Address {addr} does not have lower 5 bits set to 0.")
        else:
            print(f"File: {input_file_path} - All addresses have lower 5 bits set to 0.")


def scan_trace_folder(input_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt') or filename.endswith('.trace'):  # 根据你的文件扩展名修改
            input_file_path = os.path.join(input_folder, filename)
            scan_trace_file_for_low_5_bits(input_file_path)


# 输入文件夹路径
input_folder = "../wb_short_trace"  # 替换为你的输入文件夹路径

# 扫描文件夹中的所有 trace 文件
scan_trace_folder(input_folder)
