import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv("latency_results.csv")
df[['memory_type', 'frequency', 'chip_width']] = df['config'].str.split('_', n=2, expand=True)
df['chip_width'] = df['chip_width'].str.extract(r'(x4|x8|x16)')
plt.rcParams["font.family"] = "Times New Roman"


df_filtered = df[(df['chip_width'] == 'x4') & (df['frequency'].isin(['3200AN', '3200W']))]

df_ddr4 = df_filtered[(df_filtered['memory_type'] == 'DDR4') & (df_filtered['avg_write_latency_0'] > 0) & (df_filtered['avg_read_latency_0'] > 0)]
df_ddr5 = df_filtered[(df_filtered['memory_type'] == 'DDR5') & (df_filtered['avg_write_latency_0'] > 0) & (df_filtered['avg_read_latency_0'] > 0)]


int_traces = ['600', '602', '605', '620', '623', '625', '631', '641', '648', '657']
float_traces = ['603', '607', '619', '621', '627', '628', '638', '644', '649', '654']


trace_names = {
    '600': 'perlbench', '602': 'gcc', '605': 'mcf', '620': 'omnetpp', '623': 'xalancbmk',
    '625': 'x264', '631': 'deepsjeng', '641': 'leela', '648': 'exchange2', '657': 'xz',
    '603': 'bwaves', '607': 'cactuBSSN', '619': 'lbm', '621': 'wrf', '627': 'cam4',
    '628': 'pop2', '638': 'imagick', '644': 'nab', '649': 'fotonik3d', '654': 'roms'
}

df_ddr4_int = df_ddr4[df_ddr4['trace'].astype(str).isin(int_traces)]
df_ddr4_float = df_ddr4[df_ddr4['trace'].astype(str).isin(float_traces)]
df_ddr5_int = df_ddr5[df_ddr5['trace'].astype(str).isin(int_traces)]
df_ddr5_float = df_ddr5[df_ddr5['trace'].astype(str).isin(float_traces)]

trace_labels = [trace_names[str(trace)] for trace in df_ddr4_int['trace']] + [trace_names[str(trace)] for trace in df_ddr4_float['trace']] + ['Avg.']

# 计算平均值
avg_read_ddr4 = df_ddr4['avg_read_latency_0'].mean()
avg_read_ddr5 = df_ddr5['avg_read_latency_0'].mean()
avg_write_ddr4 = df_ddr4['avg_write_latency_0'].mean()
avg_write_ddr5 = df_ddr5['avg_write_latency_0'].mean()

bar_width = 0.35

# 设置figure和subplot布局
fig, axes = plt.subplots(ncols=2, figsize=(8, 3), dpi=200)

# 构建 x 轴的 index
index_int = np.arange(len(df_ddr4_int))
index_float = np.arange(len(df_ddr4_float)) + len(df_ddr4_int)  # float 部分的 index 要排在 int 部分后面
index_avg = len(df_ddr4_int) + len(df_ddr4_float)  # avg 部分的 index 放在最后
index_combined = np.concatenate((index_int, index_float, [index_avg]))

axes[0].bar(index_int, df_ddr4_int['avg_read_latency_0'], bar_width, label='DDR4 3200 Read (int)', color='blue')
axes[0].bar(index_float, df_ddr4_float['avg_read_latency_0'], bar_width, label='DDR4 3200 Read (float)', color='cyan')
axes[0].bar([index_avg], avg_read_ddr4, bar_width, label='DDR4 3200 Read (avg)', color='navy')

axes[0].bar(index_int + bar_width, df_ddr5_int['avg_read_latency_0'], bar_width, label='DDR5 3200 Read (int)', color='green')
axes[0].bar(index_float + bar_width, df_ddr5_float['avg_read_latency_0'], bar_width, label='DDR5 3200 Read (float)', color='lightgreen')
axes[0].bar([index_avg + bar_width], avg_read_ddr5, bar_width, label='DDR5 3200 Read (avg)', color='darkgreen')


axes[0].set_xlabel('Benchmark')
axes[0].set_ylabel('Average Latency (cycles)')
axes[0].set_title('Read Latency')
axes[0].set_xticks(index_combined + bar_width / 2)
axes[0].set_xticklabels(trace_labels, rotation=45)
#axes[0].legend()
axes[0].grid()

axes[1].bar(index_int, df_ddr4_int['avg_write_latency_0'], bar_width, label='DDR4 3200 Write (int)', color='blue')
axes[1].bar(index_float, df_ddr4_float['avg_write_latency_0'], bar_width, label='DDR4 3200 Write (float)', color='cyan')
axes[1].bar([index_avg], avg_write_ddr4, bar_width, label='DDR4 3200 Write (avg)', color='navy')

axes[1].bar(index_int + bar_width, df_ddr5_int['avg_write_latency_0'], bar_width, label='DDR5 3200 Write (int)', color='green')
axes[1].bar(index_float + bar_width, df_ddr5_float['avg_write_latency_0'], bar_width, label='DDR5 3200 Write (float)', color='lightgreen')
axes[1].bar([index_avg + bar_width], avg_write_ddr5, bar_width, label='DDR5 3200 Write (avg)', color='darkgreen')

axes[1].set_xlabel('Benchmark')
axes[1].set_ylabel('Average Latency (cycles)')
axes[1].set_title('Write Latency')
axes[1].set_xticks(index_combined + bar_width / 2)
axes[1].set_xticklabels(trace_labels, rotation=45)
#axes[1].legend()
axes[1].grid()

plt.tight_layout()
plt.show()
