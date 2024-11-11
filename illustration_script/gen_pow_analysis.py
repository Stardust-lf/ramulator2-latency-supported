import xlwings as xw
import csv
from chip_pow_config import config_4800, config_5200, config_5600, config_6400

# 配置和频率
configs = [config_4800, config_5200, config_5600, config_6400]
freqs = [4800, 5200, 5600, 6400]

# Excel 文件路径和输出 CSV 文件路径
modified_file_path = "../result_csv/ddr4_power_calc.xlsm"
output_csv_path = "../result_csv/power_stat.csv"

# 定义 CSV 表头
headers = [
    "FREQ", "TRACE", "ACT_VDD", "ACT_VPP", "RD_VDD", "RD_VPP",
    "WR_VDD", "WR_VPP", "REIO_VDD", "REIO_VPP", "WRODT_VDD", "WRODT_VPP",
    "ACTSTBY_VDD", "ACTSTBY_VPP", "REF_VDD", "REF_VPP"
]

# 创建并写入表头到 CSV 文件
with open(output_csv_path, mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=headers)
    writer.writeheader()

# 打开 Excel 文件
app = xw.App(visible=False)  # 不显示 Excel 窗口
workbook = app.books.open(modified_file_path)

# 访问相关的工作表
config_sheet = workbook.sheets['DDR4 Config']
system_sheet = workbook.sheets['System Config']
benchmark_sheet = workbook.sheets['Trace']
output_sheet = workbook.sheets['Summary']

# 遍历配置并采集数据
for i in range(len(configs)):
    print(f"-----------------------------Calculating {freqs[i]}-----------------------------")
    for key, val in configs[i].items():
        config_sheet[key].value = val
    system_sheet['N9'].value = freqs[i] // 2
    system_sheet['N8'].value = 1.8
    system_sheet['N7'].value = 1.1

    for j in range(10):
        curr_line = 4 * j + i + 2
        curr_bc = benchmark_sheet.range(f'A{curr_line}').value
        print(f"Testing on line {curr_line}, benchmark {curr_bc}")
        system_sheet['N20'].value = benchmark_sheet[f'E{curr_line}'].value
        system_sheet['N21'].value = benchmark_sheet[f'C{curr_line}'].value
        system_sheet['N23'].value = benchmark_sheet[f'D{curr_line}'].value

        # 创建样本
        sample = {
            "FREQ": freqs[i],
            "TRACE": curr_bc,
            "ACT_VDD": output_sheet['E10'].value,
            "ACT_VPP": output_sheet['F10'].value,
            "RD_VDD": output_sheet['E12'].value,
            "RD_VPP": output_sheet['F12'].value,
            "WR_VDD": output_sheet['E13'].value,
            "WR_VPP": output_sheet['F13'].value,
            "REIO_VDD": output_sheet['E14'].value,
            "REIO_VPP": output_sheet['F14'].value,
            "WRODT_VDD": output_sheet['E15'].value,
            "WRODT_VPP": output_sheet['F15'].value,
            "ACTSTBY_VDD": output_sheet['E17'].value,
            "ACTSTBY_VPP": output_sheet['F17'].value,
            "REF_VDD": output_sheet['E21'].value,
            "REF_VPP": output_sheet['F21'].value,
        }

        # 写入样本到 CSV 文件
        with open(output_csv_path, mode='a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writerow(sample)

# 关闭工作簿和 Excel 应用
workbook.close()
app.quit()

print(f"Data successfully exported to {output_csv_path}")
