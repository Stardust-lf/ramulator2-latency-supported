import os

class TraceFileProcessorWithIdleCounter:
    def __init__(self, file_paths, output_path):
        """
        初始化 TraceFileProcessorWithIdleCounter
        :param file_paths: 文件路径列表
        :param output_path: 输出文件路径
        """
        self.file_paths = file_paths
        self.output_path = output_path
        self.files = [open(file_path, "r") for file_path in file_paths]
        self.lines = [file.readlines() for file in self.files]  # 预加载文件内容
        self.current_indices = [0] * len(file_paths)  # 每个文件当前行索引
        self.current_counts = [None] * len(file_paths)  # 每个文件的当前计数值
        self.current_file_index = 0  # 当前处理的文件索引
        self.idle_counter = 0  # 空闲计数器
        self.processed_lines = 0  # 已处理的行数

    @staticmethod
    def calculate_mpki(file_lines):
        """
        计算文件的 MPKI
        :param file_lines: 文件内容的行列表
        :return: MPKI 和相关统计数据
        """
        adjusted_total_accesses = 0
        adjusted_total_cycles = 0
        for line in file_lines:
            parts = line.strip().split()
            if len(parts) == 3:
                cycle = int(parts[0])
                adjusted_cycle = min(cycle, 256)  # 调整 cycle 值
                adjusted_total_accesses += 1
                adjusted_total_cycles += adjusted_cycle

        adjusted_mpki = (adjusted_total_accesses / (adjusted_total_cycles / 1000)) if adjusted_total_cycles > 0 else 0
        return {
            "Total Memory Accesses": adjusted_total_accesses,
            "Adjusted Total Cycles": adjusted_total_cycles,
            "Adjusted MPKI": adjusted_mpki
        }

    def print_input_mpki(self):
        """
        打印所有输入文件的 MPKI
        """
        for i, lines in enumerate(self.lines):
            mpki_data = self.calculate_mpki(lines)
            print(f"Input File {self.file_paths[i]} MPKI: {mpki_data}")

    def print_output_mpki(self):
        """
        打印输出文件的 MPKI
        """
        if not os.path.exists(self.output_path):
            print("Output file does not exist.")
            return

        with open(self.output_path, "r") as output_file:
            lines = output_file.readlines()
            mpki_data = self.calculate_mpki(lines)
            print(f"Output File {self.output_path} MPKI: {mpki_data}")

    def process_next(self):
        """
        处理下一个文件的下一行
        """
        with open(self.output_path, "a") as output_file:
            while True:
                current_file_index = self.current_file_index
                current_lines = self.lines[current_file_index]
                current_index = self.current_indices[current_file_index]

                if current_index >= len(current_lines):
                    # 如果当前文件已读完，跳转到下一个文件
                    self.current_indices[current_file_index] = 0  # 重置索引
                    self.current_counts[current_file_index] = None  # 重置计数
                    self.current_file_index = (self.current_file_index + 1) % len(self.files)
                    continue

                # 获取当前行
                line = current_lines[current_index].strip()
                tokens = line.split()
                tokens[0] = min(int(tokens[0]), 256)  # 调整 cycle 值
                count = int(tokens[0])

                if self.current_counts[current_file_index] is None:
                    self.current_counts[current_file_index] = count

                if self.current_counts[current_file_index] == 0:
                    output_file.write(f"{self.idle_counter} " + " ".join(tokens[1:]) + "\n")
                    self.current_indices[current_file_index] += 1
                    self.current_counts[current_file_index] = None
                    self.idle_counter = 0
                    self.processed_lines += 1

                    # 每处理 10,000 行，打印一次进度
                    if self.processed_lines % 10000 == 0:
                        print(f"Processed {self.processed_lines} lines...")
                else:
                    self.current_counts[current_file_index] -= 1
                    self.idle_counter += 1
                    self.current_file_index = (self.current_file_index + 1) % len(self.files)
                break

    def close(self):
        """
        关闭所有文件
        """
        for file in self.files:
            file.close()


# 示例使用
file_paths = ["final_traces/620.trace", "final_traces/628.trace"]
output_path = "multiThread.trace"
processor = TraceFileProcessorWithIdleCounter(file_paths, output_path)

try:
    # 打印输入文件的 MPKI
    processor.print_input_mpki()

    # 处理所有行，直到所有文件内容都处理完成
    while True:
        processor.process_next()
except StopIteration:
    print("All files processed.")
finally:
    # 打印输出文件的 MPKI
    processor.print_output_mpki()
    processor.close()
