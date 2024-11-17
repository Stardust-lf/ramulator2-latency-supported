def extract_write_addresses(trace_path):
    """
    从 trace 文件中提取所有写操作的地址。
    :param trace_path: trace 文件路径
    :return: 写操作地址的列表
    """
    write_addresses = []
    with open(trace_path, 'r') as trace_file:
        for line in trace_file:
            parts = line.strip().split()
            if len(parts) >= 3 and parts[1] == 'W':  # 检查操作类型是否为写操作
                address = int(parts[2])  # 地址为第 3 列，转换为整数
                write_addresses.append(address)
    return write_addresses

def calculate_unique_8B_blocks(addresses):
    """
    计算写操作涉及的唯一 8B 内存块数量。
    :param addresses: 写操作地址的列表
    :return: 唯一的 8B 内存块数量
    """
    unique_blocks = {addr // 8 for addr in addresses}  # 计算每个地址对应的 8B 块编号
    return len(unique_blocks)

def main():
    # 输入 trace 文件路径
    trace_path = "../final_traces/602.trace"

    try:
        # 提取写操作地址
        write_addresses = extract_write_addresses(trace_path)

        # 计算唯一的 8B 内存块数量
        unique_blocks_count = calculate_unique_8B_blocks(write_addresses)

        # 输出结果
        print(f"写操作的总地址数: {len(write_addresses)}")
        print(f"写操作涉及的唯一 8B 内存块数: {unique_blocks_count}")
    except FileNotFoundError:
        print(f"文件未找到: {trace_path}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
