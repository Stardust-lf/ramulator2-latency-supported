import pandas as pd

df = pd.read_csv("sus_perf_results.csv")
print(df.keys())
print(df["avg_write_latency_0"])

import matplotlib.pyplot as plt

plt.plot(df["avg_write_latency_0"])
plt.show()