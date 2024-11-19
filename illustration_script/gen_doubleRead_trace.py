import os
import random


def process_trace_with_probability(trace_path, output_path, probability):
    """
    按给定概率复制读指令，将复制的指令插入到当前指令的后第9行，并翻转第12位。
    同时在插入前后打印读请求数量和总指令数量。
    :param trace_path: trace 文件路径
    :param output_path: 输出文件路径
    :param probability: 复制读指令的概率
    """
    with open(trace_path, 'r') as trace_file:
        lines = trace_file.readlines()

    # 统计插入前的读请求数量和总数量
    initial_read_requests = sum(1 for line in lines if len(line.strip().split()) >= 3 and line.strip().split()[1] == 'R')
    initial_total_requests = len(lines)

    print(f"文件 {trace_path} 插入前：")
    print(f"  读请求数量: {initial_read_requests}")
    print(f"  总请求数量: {initial_total_requests}")

    new_lines = lines[:]
    offset = 0  # 用于调整插入行号
    inserted_count = 0  # 统计插入行数

    for i, line in enumerate(lines):
        parts = line.strip().split()
        if len(parts) >= 3 and parts[1] == 'R':  # 读指令
            if random.random() < probability:  # 按概率决定是否复制
                address = int(parts[2])  # 提取地址
                flipped_address = address ^ (1 << 12)  # 翻转第12位
                new_line = f"0 R {flipped_address}\n"  # 新的指令格式
                insert_index = i + 9 + offset  # 插入到当前行的后第9行
                if insert_index < len(new_lines):  # 确保不越界
                    new_lines.insert(insert_index, new_line)
                else:
                    new_lines.append(new_line)  # 如果超出范围，则追加到文件末尾
                offset += 1  # 每插入一行，后续行号需加1
                inserted_count += 1

    # 统计插入后的读请求数量和总数量
    final_read_requests = sum(1 for line in new_lines if len(line.strip().split()) >= 3 and line.strip().split()[1] == 'R')
    final_total_requests = len(new_lines)

    print(f"文件 {trace_path} 插入后：")
    print(f"  读请求数量: {final_read_requests}")
    print(f"  总请求数量: {final_total_requests}")

    # 写入到输出文件
    with open(output_path, 'w') as output_file:
        output_file.writelines(new_lines)

    # 打印结果
    print(f"  总共插入了 {inserted_count} 行.")
    print(f"  处理后的文件已保存到: {output_path}")


def main():
    # 输入目录路径
    input_dir = "../wb_short_trace"
    output_base_dir = "../processed_traces"

    # 生成的概率列表，从 10^-5 到 10^-1
    probabilities = [0]

    # 确保输出基目录存在
    os.makedirs(output_base_dir, exist_ok=True)

    for prob in probabilities:
        output_dir = os.path.join(output_base_dir, f"prob_{prob:.0e}")  # 使用科学计数法命名子目录
        os.makedirs(output_dir, exist_ok=True)

        for trace in os.listdir(input_dir):
            trace_path = os.path.join(input_dir, trace)
            output_path = os.path.join(output_dir, trace)

            try:
                # 处理 trace 文件并插入地址
                process_trace_with_probability(trace_path, output_path, prob)
            except FileNotFoundError:
                print(f"文件未找到: {trace_path}")
            except Exception as e:
                print(f"处理文件 {trace_path} 时发生错误: {e}")


if __name__ == "__main__":
    main()
