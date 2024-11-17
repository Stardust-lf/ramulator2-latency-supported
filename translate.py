import os
from collections import OrderedDict

CACHE_SIZE = 2 * 1024  # 2 MB cache size in bytes
CACHE_LINE_SIZE = 64  # Cache line size in bytes
CACHE_LINES = CACHE_SIZE // CACHE_LINE_SIZE  # Total cache lines in cache

class LRUCache:
    def __init__(self, capacity, fout):
        self.cache = OrderedDict()
        self.capacity = capacity  # 缓存容量（行数）
        self.fout = fout  # 输出文件句柄

    def align_to_cacheline(self, address):
        """对地址进行 Cacheline 对齐"""
        return (address // CACHE_LINE_SIZE) * CACHE_LINE_SIZE

    def update(self, address, is_dirty, original_address, op_type, instr_count):
        """
        更新缓存逻辑：
        - 命中：更新脏位。
        - 未命中：加入缓存，必要时驱逐。
        - 写回逻辑统一在此完成。
        """
        address = self.align_to_cacheline(address)

        if address in self.cache:
            # Cache Hit
            if is_dirty:
                # 更新脏位为 True
                self.cache[address] = (True, original_address, op_type)
            self.cache.move_to_end(address)  # 更新 LRU 顺序
        else:
            # Cache Miss
            if len(self.cache) >= self.capacity:
                # 驱逐最近最少使用的缓存行
                evict_address, (evict_dirty, evict_original_address, evict_op_type) = self.cache.popitem(last=False)
                if evict_dirty:
                    # 若被驱逐的缓存行是脏的，写回文件
                    self.fout.write(f'{instr_count} W {evict_original_address}\n')

            # 添加新缓存行
            self.cache[address] = (is_dirty, original_address, op_type)

            # 写当前操作到文件
            self.fout.write(f'{instr_count} R {original_address}\n')


trace_files = [f for f in os.listdir("/home/fan/projects/ramulator2/ori_trace") if f.endswith('.trace')]

for trace in trace_files:
    file_writes, w, r, lc, lr = 0, 0, 0, 0, 0
    instr_count = 0  # 初始化CPU指令计数

    with open(f'/home/fan/projects/ramulator2/wb_traces/{trace}', 'w+') as fout:
        cache = LRUCache(CACHE_LINES, fout)

        with open(f'/home/fan/projects/ramulator2/ori_trace/{trace}') as f:
            print(f"Proceeding on tracefile {trace}")
            for line in f:
                lr += 1
                if lr % 10000000 == 0:
                    print(f"Processing line {lr}")

                if lc >= 10_000_000:  # 限制写入文件的总行数
                    break

                try:
                    sp = line.split(' ')
                    cpu_instr_count = min(int(sp[0]), 128)  # 从 sp[0] 获取 CPU 指令数量
                    address = int(sp[2][:-1], 16)  # 转换地址为整数
                    # address %= 2147483648  # 地址模数化，限制范围

                    # 判断操作类型
                    is_dirty = sp[1] == 'W'

                    # 更新缓存并写回文件（逻辑已经在缓存内部完成）
                    cache.update(address, is_dirty, address, sp[1], cpu_instr_count)

                    if sp[1] == 'W':
                        w += 1
                    else:
                        r += 1
                    lc += 1

                except Exception as e:
                    #print(f"Error processing line {line} in trace {trace}: {e}")
                    continue

    print(f"Trace {trace} completed: Writes {w}, Reads {r}, Total lines written {lc}")
