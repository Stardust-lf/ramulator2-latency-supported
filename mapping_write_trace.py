import os


def extract_write_addresses(trace_path):
    """
    从 trace 文件中提取所有写操作的地址及其行号。
    :param trace_path: trace 文件路径
    :return: 写操作地址的列表及其行号
    """
    write_addresses = []
    with open(trace_path, 'r') as trace_file:
        for line_number, line in enumerate(trace_file):
            parts = line.strip().split()
            if len(parts) >= 3 and parts[1] == 'W':  # 检查操作类型是否为写操作
                address = int(parts[2])  # 地址为第 3 列，转换为整数
                write_addresses.append((address, line_number))  # 保存地址及其行号
    return write_addresses


def calculate_unique_8B_blocks(addresses):
    """
    计算写操作涉及的唯一 8B 内存块数量，并定位每个内存块的最靠前地址。
    :param addresses: 写操作地址的列表
    :return: 每个唯一内存块及其最靠前地址和行号
    """
    block_to_first_address = {}
    for address, line_number in addresses:
        block_number = address // 8
        # 只保存最靠前的地址
        if block_number not in block_to_first_address or line_number < block_to_first_address[block_number][1]:
            block_to_first_address[block_number] = (address, line_number)
    return block_to_first_address


def insert_write_requests(trace_path, output_path, block_to_addresses):
    """
    将生成的写入请求插入到对应的最靠前写操作后面。
    :param trace_path: 原始 trace 文件路径
    :param output_path: 修改后的 trace 文件输出路径
    :param block_to_addresses: 内存块到最靠前地址的映射
    :return: 插入前后的写操作数量
    """
    with open(trace_path, 'r') as trace_file:
        lines = trace_file.readlines()

    # 原始写操作数量
    original_write_count = sum(1 for line in lines if line.split()[1] == 'W')

    # 遍历内存块，生成写入请求并插入到最靠前写操作后面
    for block_number, (address, line_number) in block_to_addresses.items():
        write_request = f"0 W {address}\n"
        lines.insert(line_number + 1, write_request)  # 插入到最靠前写操作的下一行

    # 插入后的写操作数量
    modified_write_count = sum(1 for line in lines if line.split()[1] == 'W')

    # 将修改后的内容写入新文件
    with open(output_path, 'w') as output_file:
        output_file.writelines(lines)

    return original_write_count, modified_write_count


def main():
    input_dir = 'wb_short_trace'
    output_dir = 'modified_traces'
    os.makedirs(output_dir, exist_ok=True)

    for trace_filename in os.listdir(input_dir):
        trace_path = os.path.join(input_dir, trace_filename)
        output_path = os.path.join(output_dir, trace_filename)

        try:
            # 提取写操作地址
            write_addresses = extract_write_addresses(trace_path)

            # 计算唯一 8B 内存块及其最靠前地址
            block_to_addresses = calculate_unique_8B_blocks(write_addresses)

            # 输出原始统计结果
            print(f"文件: {trace_filename}")
            print(f"写操作的总地址数: {len(write_addresses)}")
            print(f"写操作涉及的唯一 8B 内存块数: {len(block_to_addresses)}")

            # 插入写入请求并生成新文件
            original_count, modified_count = insert_write_requests(trace_path, output_path, block_to_addresses)
            print(f"插入前写操作数量: {original_count}")
            print(f"插入后写操作数量: {modified_count}")
            print(f"已生成修改后的 trace 文件: {output_path}\n")

        except FileNotFoundError:
            print(f"文件未找到: {trace_filename}")
        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == "__main__":
    main()
