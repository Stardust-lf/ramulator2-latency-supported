import random
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity, fout):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.fout = fout

    def get(self, address):
        if address in self.cache:
            self.cache.move_to_end(address)
            return self.cache[address][0]  # 返回 dirty 状态
        return None

    def put(self, address, is_dirty, original_address, op_type, instr_count):
        if address in self.cache:
            # 更新 dirty 位为 True（若当前操作是写操作）
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


def generate_unique_address_trace(num_entries, write_ratio, min_address, max_address, alignment):
    """
    Generates a trace where every address is unique, ensuring all accesses are cache misses.

    Args:
        num_entries (int): Total number of trace entries to generate.
        write_ratio (float): Ratio of write (W) operations to total operations (0 to 1).
        min_address (int): Minimum address (inclusive) for generated addresses.
        max_address (int): Maximum address (inclusive) for generated addresses.
        alignment (int): Required alignment for the generated addresses.

    Returns:
        list: List of trace strings in the required format.
    """
    trace = []
    unique_addresses = set()
    address_space = range(
        (min_address + alignment - 1) // alignment, max_address // alignment
    )

    if len(address_space) < num_entries:
        raise ValueError("Not enough unique addresses in the specified range for the given number of entries.")

    for _ in range(num_entries):
        # Randomly select operation type based on the write ratio
        operation = "W" if random.random() < write_ratio else "R"

        # Generate a unique aligned address
        while True:
            address = random.choice(address_space) * alignment
            if address not in unique_addresses:
                unique_addresses.add(address)
                break

        # Generate a random prefix (e.g., 1024 or 5 for W)
        prefix = random.randint(1, 20)

        # Append the trace entry
        trace.append(f"0 {operation} {address}")

    return trace


if __name__ == "__main__":
    # Parameters
    num_entries = 1000000  # Total number of trace entries to generate
    write_ratio = 0.4  # 40% of operations will be writes
    min_address = 0x10000000  # Minimum address
    max_address = 0xFFFFFFFF  # Maximum address
    alignment = 64  # Addresses must be aligned to 64 bytes

    for write_ratio in range(1, 10):
        # Generate the trace
        random_trace = generate_unique_address_trace(num_entries, write_ratio / 10, min_address, max_address, alignment)

        # Save to a file or print
        output_file = f"../random_traces/random_W0{write_ratio}.trace"
        with open(output_file, "w") as f:
            f.write("\n".join(random_trace))

        print(f"Random trace with {num_entries} entries generated and saved to {output_file}!")
