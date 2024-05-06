#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd
from handlers.log_handler import get_log
import warnings

def excel_tool(args, log_path):
    """
    excel处理器
    :param args: 前端参数
    :param log_path: 日志路径
    """
    # 禁用 openpyxl 的警告信息
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl.styles")

    # 输入文件夹路径和输出文件名
    input_folder = f'{args.Excel文件夹}'
    output_file = f'{input_folder}/pwy_合并.xlsx'

    # 如果输出文件已存在，则删除
    if os.path.exists(output_file):
        os.remove(output_file)
        get_log(log_path).info(f'已删除已存在的文件{output_file}')

    # 指定要抓取的列的名称
    columns_to_extract = args.保留列名.split()

    # 创建一个空的 DataFrame 用于存储合并后的数据
    merged_data = pd.DataFrame()

    # 循环遍历文件夹中的每个 Excel 文件
    num = 1
    for filename in os.listdir(input_folder):
        if filename.endswith('.xlsx'):  # 只处理.xlsx文件，如果有其他格式的文件，可以相应地修改条件
            get_log(log_path).info(f'处理第{num}个文件{filename}中...')
            file_path = os.path.join(input_folder, filename)
            df = pd.read_excel(file_path)  # 读取 Excel 文件
            if columns_to_extract[0] != 'All':
                df = df[columns_to_extract]  # 仅保留指定的列
            merged_data = pd.concat([merged_data, df], ignore_index=True)  # 合并数据
            num += 1

    # 将合并后的数据保存到新的 Excel 文件中
    merged_data.to_excel(output_file, index=False)
    get_log(log_path).info(f'处理完成，生成合并文件{output_file}')
