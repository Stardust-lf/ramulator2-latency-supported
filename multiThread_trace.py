class TraceFileIterator:
    def __init__(self, file_paths):
        """
        初始化 TraceFileIterator
        :param file_paths: 一个包含多个文件路径的列表
        """
        self.file_paths = file_paths
        self.files = [open(file_path, "r") for file_path in file_paths]
        self.current_file_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        """
        返回当前文件的下一行，如果到达最后一个文件，跳回第一个文件。
        :return: 当前文件的下一行
        """
        while True:
            current_file = self.files[self.current_file_index]
            line = current_file.readline()
            if line:  # 如果当前文件还有内容
                return line.strip()  # 去掉首尾空白字符后返回
            else:  # 当前文件读完，跳到下一个文件
                self.current_file_index = (self.current_file_index + 1) % len(self.files)
                # 如果循环回到原点且没有内容，所有文件为空
                if self.current_file_index == 0 and not any(f.tell() < f.seek(0, 2) for f in self.files):
                    raise StopIteration  # 所有文件均已读取完毕
                # 重置文件指针到开头
                current_file.seek(0)

    def close(self):
        """
        关闭所有打开的文件
        """
        for f in self.files:
            f.close()


# 示例使用
file_paths = ["trace1.txt", "trace2.txt"]
iterator = TraceFileIterator(file_paths)

try:
    for _ in range(10):  # 示例迭代 10 次
        print(next(iterator))
finally:
    iterator.close()  # 确保关闭文件
