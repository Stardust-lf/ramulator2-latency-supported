from collections import OrderedDict

CACHE_SIZE = 2 * 1024 * 1024  # 2 MB cache size in bytes
CACHE_LINE_SIZE = 64  # Cache line size in bytes
CACHE_LINES = CACHE_SIZE // CACHE_LINE_SIZE  # Total cache lines in cache

class LRUCache:
    def __init__(self, capacity, fout):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.fout = fout

    def get(self, address):
        if address in self.cache:
            self.cache.move_to_end(address)
            return self.cache[address][0]  # 返回dirty状态
        return None

    def put(self, address, is_dirty, original_address, op_type, instr_count):
        if address in self.cache:
            # 更新dirty位为True（若当前操作是写操作）
            if is_dirty:
                self.cache[address] = (True, original_address, op_type)
            self.cache.move_to_end(address)
        else:
            # 如果缓存满了，移除最近最少使用的缓存行
            if len(self.cache) >= self.capacity:
                evict_address, (evict_dirty, evict_original_address, evict_op_type) = self.cache.popitem(last=False)
                # 若被驱逐的缓存行是脏的，写回文件
                if evict_dirty:
                    self.fout.write(f'{instr_count} {evict_op_type} {evict_original_address}\n')
                    return evict_op_type  # 返回写回文件的操作类型
            # 将新地址加入缓存并设置脏位状态
            self.cache[address] = (is_dirty, original_address, op_type)
            return op_type  # 返回新写入的操作类型

# 初始化缓存和处理trace文件
#traces = [603, 607, 619, 621, 628, 638, 644, 649, 654]
# traces = [600, 602, 605, 620, 623, 631, 641, 648, 657]
# traces = ["bc_twi","bc_web","cc_twi","cc_web","pr_twi","pr_web"]
traces = ["bfs_twi","bfs_web","bfs_road","bc_road","cc_road","pr_road"]
for trace in traces:

    file_writes, w, r, lc ,lr = 0, 0, 0, 0, 0
    instr_count = 0  # 初始化CPU指令计数
    with open(f'/home/fan/projects/ramulator2/ctraces/{trace}.trace', 'w+') as fout:
        cache = LRUCache(CACHE_LINES, fout)
        with open(f'/home/fan/projects/ramulator2/ori_trace/{trace}.trace') as f:
            for line in f:
                lr += 1
                if lr<50000000:
                    continue
                if lr%1000000 == 0:
                    print("Proceeding on line {}".format(lr))
                if lc % 100000 == 0 and lc > 0:
                    print(f"Trace {trace}, written lines {lc}, w percentage {w / (w + r + 1)}, cache usage: {len(cache.cache)}/{CACHE_LINES}")

                if lc >= 2_000_000:
                    break

                try:
                    sp = line.split(' ')

                    cpu_instr_count = min(int(sp[0]),128)  # 从 sp[0] 获取 CPU 指令数量
                    address = int(sp[2][:-1], 16)  # 转换地址为整数
                    address %= 2147483648
                    aligned_address = (address // CACHE_LINE_SIZE) * CACHE_LINE_SIZE  # 对齐缓存行

                    # 累加 CPU 指令数量
                    instr_count += cpu_instr_count

                    if sp[1] == 'W':
                        is_dirty = True
                    elif sp[1] == 'R':
                        is_dirty = False
                    else:
                        continue

                    # 检查缓存并决定是否写入操作
                    cached_value = cache.get(aligned_address)
                    if cached_value is None:
                        # 缓存未命中，添加到缓存并写入文件
                        operation_type = cache.put(aligned_address, is_dirty, address, sp[1], instr_count)
                        fout.write(f'{instr_count} {sp[1]} {address}\n')
                        instr_count = 0  # 写入后重置指令计数
                        if operation_type == 'W':
                            w += 1
                        else:
                            r += 1
                        lc += 1
                    elif cached_value is False and is_dirty:
                        # 缓存命中但dirty位溢出，更新dirty位并写入文件
                        operation_type = cache.put(aligned_address, is_dirty, address, sp[1], instr_count)
                        fout.write(f'{instr_count} {sp[1]} {address}\n')
                        instr_count = 0  # 写入后重置指令计数
                        w += 1
                        lc += 1

                except Exception as e:
                    #print(f"Error processing line {lc} in trace {trace}: {e}")
                    continue

    print(f"Trace {trace} completed: Write count {w}, Read count {r}, Total lines written to file {lc}")
