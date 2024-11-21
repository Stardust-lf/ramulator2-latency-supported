import os


def calculate_adjusted_mpki(trace_file_path):
    adjusted_total_accesses = 0
    adjusted_total_cycles = 0

    with open(trace_file_path, 'r') as file:
        for line in file:
            # Split each line into its components
            parts = line.strip().split()
            if len(parts) == 3:
                cycle = int(parts[0])
                operation = parts[1]
                address = parts[2]

                # Adjust cycle count if it is negative or exceeds 256
                if cycle < 0 or cycle > 64:
                    adjusted_cycle = 64
                else:
                    adjusted_cycle = cycle

                # Count total accesses and track adjusted total cycles
                adjusted_total_accesses += 1
                adjusted_total_cycles += adjusted_cycle

    # Calculate MPKI with adjusted cycles
    if adjusted_total_cycles == 0:
        return None  # Avoid division by zero
    adjusted_mpki = adjusted_total_accesses / (adjusted_total_cycles / 1000)

    return adjusted_mpki


def main():
    # 输入目录路径
    input_dir = "wb_short_trace"
    mpki_results = []

    # 遍历目录下的所有 trace 文件并计算 MPKI
    for trace in os.listdir(input_dir):
        trace_path = os.path.join(input_dir, trace)
        if os.path.isfile(trace_path):
            try:
                mpki = calculate_adjusted_mpki(trace_path)
                if mpki is not None:
                    mpki_results.append((trace, mpki))
            except Exception as e:
                print(f"处理文件 {trace_path} 时发生错误: {e}")

    # 按照 MPKI 进行排序
    sorted_results = sorted(mpki_results, key=lambda x: x[1])

    # 打印排序后的 trace 文件名和 MPKI
    print("按 MPKI 排序的 trace 文件列表：")
    for trace, mpki in sorted_results:
        print(f"{trace}: MPKI = {mpki:.2f}")


if __name__ == "__main__":
    main()