import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "Times New Roman"
# Trace 名称映射
trace_names = {
    '600': 'perlbench', '602': 'gcc', '605': 'mcf', '620': 'omnetpp', '623': 'xalancbmk',
    '625': 'x264', '631': 'deepsjeng', '641': 'leela', '648': 'exchange2', '657': 'xz',
    '603': 'bwaves', '607': 'cactuBSSN', '619': 'lbm', '621': 'wrf', '627': 'cam4',
    '628': 'pop2', '638': 'imagick', '644': 'nab', '649': 'fotonik3d', '654': 'roms'
}

# 读取 CSV 文件
input_csv_path = "../result_csv/power_stat.csv"
data = pd.read_csv(input_csv_path)

# 删除全为 0 的列
data = data.loc[:, (data != 0).any(axis=0)]

# 格式化 TRACE 列为整数字符串
data['TRACE'] = data['TRACE'].apply(lambda x: str(int(float(x))) if not pd.isnull(x) else x)

# 替换 Trace 名称，如果未找到匹配值，保留原始值
data['TRACE'] = data['TRACE'].map(trace_names).fillna(data['TRACE'])

# 提取不同频率的数据
freqs = [4800, 5200, 5600, 6400]
data['Total'] = data.iloc[:, 2:].sum(axis=1)  # 计算每行所有值的总和

# 定义颜色映射
color_map = {
    "RD_VDD": "tomato",
    "RD_VPP": "salmon",
    "WR_VDD": "red",
    "WR_VPP": "darkred",
    "ACT_VDD": "gold",
    "ACT_VPP": "yellow",
    "ACTSTBY_VDD": "skyblue",
    "ACTSTBY_VPP": "deepskyblue",
    "REF_VDD": "blue",
    "REF_VPP": "navy"
}

# 创建 1 行 4 列的子图
fig, axes = plt.subplots(1, 4, dpi=150, figsize=(12, 6), sharey=True)

# 遍历每个频率绘制子图
for idx, freq in enumerate(freqs):
    freq_data = data[data['FREQ'] == freq]
    traces = freq_data['TRACE']
    component_values = freq_data.iloc[:, 2:-1]  # 除去 FREQ, TRACE, Total 的值

    # 当前子图
    ax = axes[idx]

    # 绘制堆叠柱状图
    bottoms = np.zeros(len(traces))  # 初始化堆叠基底
    x = np.arange(len(traces))  # X 轴的位置

    for column in component_values.columns:
        ax.bar(
            x,
            component_values[column],
            color=color_map.get(column, "grey"),  # 使用颜色映射
            label=column,
            bottom=bottoms
        )
        bottoms += component_values[column]  # 更新堆叠基底

    # 设置子图标题和轴标签
    ax.set_title(f"{freq} MHz")
    ax.set_xlabel("Trace")
    if idx == 0:  # 仅左侧子图显示 Y 轴标签
        ax.set_ylabel("Total Values")
    ax.set_xticks(x)
    ax.set_xticklabels(traces, rotation=45)
    ax.grid()

# 添加全局图例，调整为两行
fig.legend(
    component_values.columns,
    loc="upper center",
    ncol=len(component_values.columns) // 2,  # 设置每行的列数，自动调整为两行
    frameon=False  # 去除图例边框（可选）
)
plt.tight_layout(rect=[0, 0, 1, 0.88])  # 调整布局，避免图例遮挡子图
plt.savefig('../figures/pow_stat.jpg')
