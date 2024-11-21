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
                address = int(parts[2])  # 将地址转换为整数
                address = address & ~0x7F  # 将低 7 位比特置 0

                # 检查是否与上一个操作和地址相同
                current_operation = parts[1]
                if last_operation == current_operation and last_address == address:
                    continue  # 跳过连续的相同操作
                else:
                    last_address = address
                    last_operation = current_operation

                # 写入处理后的行
                outfile.write(f"{parts[0]} {current_operation} {address}\n")
                output_line_count += 1


    # 打印输入和输出的行数
    print(f"File: {input_file_path}")
    print(f"Input Lines: {input_line_count}, Output Lines: {output_line_count}")


def process_trace_folder(input_folder, output_folder):
    # 检查输出文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 处理文件夹中的每个 trace 文件
    for filename in trace_names:
        if filename.endswith('.txt') or filename.endswith('.trace'):  # 根据你的文件扩展名修改
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)
            process_trace_file(input_file_path, output_file_path)
            print(f"Processed {filename} and saved to {output_folder}\n")


# 输入文件夹和输出文件夹路径
input_folder = "../offest_base_traces"  # 替换为你的输入文件夹路径
output_folder = "../offest_128_traces"  # 替换为你的输出文件夹路径

# 处理文件夹
process_trace_folder(input_folder, output_folder)
