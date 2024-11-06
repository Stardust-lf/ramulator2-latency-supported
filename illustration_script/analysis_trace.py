file_path = '../final_traces/620.trace'  # 你的文件路径
count_R = 0
count_W = 0

with open(file_path, 'r') as file:
    for line in file:
        # 检查是否包含 'R' 或 'W'
        if ' R ' in line:
            count_R += 1
        elif ' W ' in line:
            count_W += 1

print(f"Total R count: {count_R}")
print(f"Total W count: {count_W}")
print(f"W percentage",count_W/(count_W+count_R))
