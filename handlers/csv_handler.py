import csv
import re

class CSVHandler:
    """
    csv文件操作器
    """
    def __init__(self, file_path, encoding='utf-8'):
        self.file_path = file_path
        self.encoding = encoding

    def read_all(self):
        """读取整个CSV文件，返回为列表字典"""
        with open(self.file_path, encoding=self.encoding) as file:
            return list(csv.DictReader(file))

    def write_all(self, data, fieldnames):
        """将数据写入CSV文件，覆盖原有文件"""
        with open(self.file_path, mode='w', encoding=self.encoding, newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def append_row(self, row):
        """向CSV文件追加一行数据"""
        with open(self.file_path, mode='a', encoding=self.encoding, newline='') as file:
            writer = csv.DictWriter(file, fieldnames=row.keys())
            if file.tell() == 0:  # 文件为空时写入头
                writer.writeheader()
            writer.writerow(row)

    def find_by_column(self, column_name, value, fuzzy=False):
        """
        根据指定列的值查找匹配的行
        :param column_name: 列名
        :param value: 要查找的值
        :param fuzzy: 是否进行模糊匹配
        :return: 第一个匹配项（字典），找不到返回 None
        """
        with open(self.file_path, encoding=self.encoding) as file:
            reader = csv.DictReader(file)
            for row in reader:
                if fuzzy:
                    if re.search(value, row[column_name]):  # 模糊匹配
                        return row
                else:
                    if row[column_name] == value:  # 精确匹配
                        return row
        return None

    def update_row(self, column_name, value, update_data):
        """根据指定列的值更新匹配的行"""
        rows = self.read_all()
        updated = False
        for row in rows:
            if row[column_name] == value:
                row.update(update_data)
                updated = True
        if updated:
            fieldnames = rows[0].keys() if rows else update_data.keys()
            self.write_all(rows, fieldnames)
        return updated
