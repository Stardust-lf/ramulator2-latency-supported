import os

def count_write_addresses_and_process(trace_path):
    """
    统计写地址总数量、原始写地址种类、清零后写地址种类并处理 trace 文件。
    :param trace_path: trace 文件路径
    :return: 写地址的总数量, 原始写地址种类, 清零后写地址种类, 处理后的数据
    """
    total_write_count = 0
    original_addresses = set()
    processed_blocks = {}  # 存储清零后的唯一地址和其最后写指令行号
    lines = []

    with open(trace_path, 'r') as trace_file:
        lines = trace_file.readlines()
        for i, line in enumerate(lines):
            parts = line.strip().split()
            if len(parts) >= 3 and parts[1] == 'W':  # 写操作
                total_write_count += 1  # 总写地址计数
                address = int(parts[2])  # 提取写地址
                original_addresses.add(address)  # 原始地址集合
                processed_address = address & ~0b111111  # 清零后6位
                processed_blocks[processed_address] = i  # 更新为最新的写指令行号

    return total_write_count, len(original_addresses), len(processed_blocks), processed_blocks, lines


def process_trace_and_bitflip_addresses(trace_path, output_path):
    """
    对清零后的地址进行 bit-flip 处理，并插入到原始写地址对应的最后一条指令后面。
    :param trace_path: trace 文件路径
    :param output_path: 输出文件路径
    """
    # 统计写地址并获取处理所需数据
    total_write_count, original_count, processed_count, processed_blocks, lines = count_write_addresses_and_process(trace_path)

    # 创建插入后的新文件内容
    new_lines = lines[:]
    offset = 0  # 用于调整插入行号
    inserted_count = 0  # 统计插入行数

    for processed_address, last_write_index in sorted(processed_blocks.items(), key=lambda x: x[1]):
        # 计算 bit-flip 地址（翻转第12位）
        bitflip_address = processed_address ^ (1 << 12)
        # 新行格式
        new_line = f"0 W {bitflip_address}\n"
        # 插入到目标行号的下一行
        insert_index = last_write_index + 1 + offset
        new_lines.insert(insert_index, new_line)
        offset += 1  # 每插入一行，后续行号需加1
        inserted_count += 1

    # 写入到输出文件
    with open(output_path, 'w') as output_file:
        output_file.writelines(new_lines)

    # 打印统计结果和插入结果
    print(f"文件 {trace_path}：")
    print(f"  写地址的总数量: {total_write_count}")
    print(f"  原始写地址种类数量: {original_count}")
    print(f"  清零后写地址种类数量: {processed_count}")
    print(f"  总共插入了 {inserted_count} 行.")
    print(f"  处理后的文件已保存到: {output_path}")


def main():
    # 输入目录路径
    input_dir = "../wb_short_trace"
    output_dir = "../wb_doubleW_trace"

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    for trace in os.listdir(input_dir):
        trace_path = os.path.join(input_dir, trace)
        output_path = os.path.join(output_dir, trace)

        try:
            # 处理 trace 文件并插入地址
            process_trace_and_bitflip_addresses(trace_path, output_path)
        except FileNotFoundError:
            print(f"文件未找到: {trace_path}")
        except Exception as e:
            print(f"处理文件 {trace_path} 时发生错误: {e}")

if __name__ == "__main__":
    main()
