import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.ticker as ticker

# 读取数据
df = pd.read_csv("../result_csv/latency_results.csv")
df[['memory_type', 'frequency', 'chip_width']] = df['config'].str.split('_', n=2, expand=True)
df['chip_width'] = df['chip_width'].str.extract(r'(x4|x8|x16)')
plt.rcParams["font.family"] = "Times New Roman"

# 过滤掉 'avg_write_latency_0' 为 0 的数据
df_filtered = df[(df['chip_width'] == 'x4') & (df['avg_write_latency_0'] > 0)]  # 只保留写延迟大于 0 的行
#df_filtered = df
# 计算每个 config 的平均值
df_grouped = df_filtered.groupby(['trace', 'memory_type']).agg({
    'avg_read_latency_0': 'mean',
    'avg_write_latency_0': 'mean',
    'cycles_recorded_core_0': 'mean'
}).reset_index()

# 将 config 平均值的数据分为 DDR4 和 DDR5
df_ddr4 = df_grouped[df_grouped['memory_type'] == 'DDR4'].copy()
df_ddr5 = df_grouped[df_grouped['memory_type'] == 'DDR5'].copy()

# 基准测试的映射字典
trace_names = {
    '600': 'perlbench', '602': 'gcc', '605': 'mcf', '620': 'omnetpp', '623': 'xalancbmk',
    '625': 'x264', '631': 'deepsjeng', '641': 'leela', '648': 'exchange2', '657': 'xz',
    '603': 'bwaves', '607': 'cactuBSSN', '619': 'lbm', '621': 'wrf', '627': 'cam4',
    '628': 'pop2', '638': 'imagick', '644': 'nab', '649': 'fotonik3d', '654': 'roms'
}

# 映射 trace 为对应的名称
df_ddr4.loc[:, 'trace_name'] = df_ddr4['trace'].astype(str).map(trace_names)
df_ddr5.loc[:, 'trace_name'] = df_ddr5['trace'].astype(str).map(trace_names)

# 计算所有 config 平均值的平均
avg_read_ddr4 = df_ddr4['avg_read_latency_0'].mean()
avg_read_ddr5 = df_ddr5['avg_read_latency_0'].mean()
avg_write_ddr4 = df_ddr4['avg_write_latency_0'].mean()
avg_write_ddr5 = df_ddr5['avg_write_latency_0'].mean()
avg_cycles_ddr4 = (1 / df_ddr4['cycles_recorded_core_0']).mean()
avg_cycles_ddr5 = (1 / df_ddr5['cycles_recorded_core_0']).mean()

# 设置柱状图宽度
bar_width = 0.35

# 设置figure和subplot布局
fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(15, 3), dpi=150)

# 构建 x 轴的 index 并添加 'Avg.' 标签的索引和标签
index_combined = np.arange(len(df_ddr4))
xticks = np.concatenate((index_combined, [len(index_combined)]))
xtick_labels = list(df_ddr4['trace_name']) + ['Avg.']

# 定义 y 轴的偏移量，用于标签的上浮和下沉 (正值表示上浮，负值表示下沉)
y_offsets = np.zeros(20)

# 绘制读取延迟图
axes[0].bar(index_combined, df_ddr4['avg_read_latency_0'], bar_width, label='DDR4 Read (config)', color='blue', zorder=2)
axes[0].bar(index_combined + bar_width, df_ddr5['avg_read_latency_0'], bar_width, label='DDR5 Read (config)', color='green', zorder=2)
axes[0].bar([len(index_combined)], avg_read_ddr4, bar_width, label='DDR4 Read (avg)', color='navy', zorder=2)
axes[0].bar([len(index_combined) + bar_width], avg_read_ddr5, bar_width, label='DDR5 Read (avg)', color='darkgreen', zorder=2)
axes[0].set_xticks(xticks + bar_width / 2)
axes[0].set_xticklabels(xtick_labels, rotation=30)
axes[0].set_ylabel('Average Latency (cycles)')
axes[0].set_title('Read Latency')
axes[0].grid(axis='y', zorder=0)

# 绘制写入延迟图 (对数刻度)
axes[1].bar(index_combined, df_ddr4['avg_write_latency_0'], bar_width, label='DDR4 Write (config)', color='blue', zorder=2)
axes[1].bar(index_combined + bar_width, df_ddr5['avg_write_latency_0'], bar_width, label='DDR5 Write (config)', color='green', zorder=2)
axes[1].bar([len(index_combined)], avg_write_ddr4, bar_width, label='DDR4 Write (avg)', color='navy', zorder=2)
axes[1].bar([len(index_combined) + bar_width], avg_write_ddr5, bar_width, label='DDR5 Write (avg)', color='darkgreen', zorder=2)
axes[1].set_xticks(xticks + bar_width / 2)
axes[1].set_xticklabels(xtick_labels, rotation=30)
axes[1].set_yscale('log')
axes[1].set_ylabel('Average Latency (cycles) - Log Scale')
axes[1].set_title('Write Latency (Log Scale)')
axes[1].yaxis.set_major_locator(ticker.LogLocator(base=10.0, numticks=10))
axes[1].grid(axis='y', which='both', zorder=0)

# 绘制性能图
axes[2].bar(index_combined, 1 / df_ddr4['cycles_recorded_core_0'], bar_width, label='DDR4 Performance (config)', color='blue', zorder=2)
axes[2].bar(index_combined + bar_width, 1 / df_ddr5['cycles_recorded_core_0'], bar_width, label='DDR5 Performance (config)', color='green', zorder=2)
axes[2].bar([len(index_combined)], avg_cycles_ddr4, bar_width, label='DDR4 Performance (avg)', color='navy', zorder=2)
axes[2].bar([len(index_combined) + bar_width], avg_cycles_ddr5, bar_width, label='DDR5 Performance (avg)', color='darkgreen', zorder=2)
axes[2].set_xticks(xticks + bar_width / 2)
axes[2].set_xticklabels(xtick_labels, rotation=30)
axes[2].set_yscale('log')
axes[2].set_ylabel('Total Cycles (core 0)')
axes[2].set_title('Performance')
axes[2].yaxis.set_major_locator(ticker.LogLocator(base=10.0, numticks=10))
axes[2].grid(axis='y', which='both', zorder=0)

# 绘制单个配置的 LLC Miss 图
single_exp = df[df['config'] == "DDR4_1600J_x4_cfg.yaml"].set_index('trace')
single_exp = single_exp.reindex(df_ddr4['trace']).reset_index()
axes[3].bar(index_combined, single_exp['llc_read_misses'], bar_width, label='LLC Read Misses', color='blue', zorder=2)
axes[3].bar(index_combined + bar_width, single_exp['llc_write_misses'], bar_width, label='LLC Write Misses', color='green', zorder=2)
axes[3].set_xticks(xticks + bar_width / 2)
axes[3].set_xticklabels(xtick_labels, rotation=30)
axes[3].set_yscale('log')
axes[3].set_ylabel('Total Requests')
axes[3].set_title('Total Requests')
axes[3].grid(axis='y', zorder=0)

# 调整布局
plt.tight_layout()
plt.show()
