import pandas as pd

df = pd.read_csv("latency_results.csv")
print(df.columns)
print(df['config'])
print(df['total_num_write_requests'])
print(df['avg_write_latency_0'])