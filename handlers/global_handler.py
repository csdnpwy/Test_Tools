#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import re
from datetime import datetime

from commons.variables import log_dir
from handlers.app_handler import app_request
from handlers.configReader import ConfigReader
from handlers.log_handler import get_log


def get_stake_did(accessToken, env, log_path):
    """
    获取监控桩did
    优先从did_pools选举，非连接状态选用
    did_pools都为连接状态则根据时间戳随机生成
    """
    conf_reder = ConfigReader(f"{log_dir}version.ini")
    stake_monitor = conf_reder.get_value('global_config', 'stake_monitor')
    if stake_monitor == "none":
        did_pools = ['12300001000000000111', '12300001000000000222', '12300001000000000333', '12300001000000000444',
                     '12300001000000000555', '12300001000000000666']
        url = f"{env}/rest/app/community/isOnLine"
        seq = 110
        for _ in range(0, 10):  # pwy0816：修订为随机从资源池获取，避免第一个did异常导致每次都异常
            did = random.choice(did_pools)
            seq += 1
            data = {
                "seq": seq,
                "version": "v0.1",
                "params": {
                    "did": f"{did}"
                }
            }
            res = app_request(accessToken, url, data, log_path)
            if '{"isOnline":0}' in res:
                get_log(log_path).debug(f'本次测试推举监控did--{did}')
                return did
        now = datetime.now()
        formatted_time = now.strftime("%m%d%H%M%S")
        did = f"1230000100{formatted_time}"
    else:
        did = stake_monitor
    get_log(log_path).debug(f'本次测试推举监控did--{did}')
    return did


def is_ping_successful(ping_res):
    """
    判断ping结果，兼容多个环境结果
    :param ping_res:
    :return:
    """
    if ping_res is None:
        return False
    if isinstance(ping_res, bool):
        return ping_res
    try:
        ping_value = float(ping_res)
        return ping_value >= 0
    except ValueError:
        return False


def extract_between(text, start, end=None, length=None):
    """
    截取字符串字符
    :param text: 欲截取的字符串文本
    :param start: 开始字段（支持正则）
    :param end: 结束字段（支持正则）
    :param length: 当 end 为 None 时，截取 start 后 length 长度的字段
    :return: 截取的字段列表
    """
    if end:
        # 当 end 不为空时，匹配 start 和 end 之间的内容，start 和 end 都支持正则表达式
        pattern = start + r'(.*?)' + end
        matches = re.findall(pattern, text)
        return list(dict.fromkeys(matches)) if matches else []  # 去重保留顺序，无匹配时返回空列表
    elif length:
        # 当 end 为空且 length 不为空时，找到所有 start 匹配的位置，并截取 length 长度的字符串
        matches = re.finditer(start, text)
        results = []
        for match in matches:
            start_index = match.end()  # 从匹配到的 start 之后开始
            end_index = start_index + int(length)
            # 边界检查，避免超出字符串长度
            results.append(text[start_index:end_index] if end_index <= len(text) else text[start_index:])
        return list(dict.fromkeys(results)) if results else []
    else:
        # 如果没有提供 end 或 length，则返回空列表
        return []


def hex_to_custom_decimals(hex_num, bit_sizes=None):
    """
    将十六进制数转换为按指定bit分割后的十进制列表。
    KNX设备模拟器适用
    :param hex_num: 输入的十六进制字符串
    :param bit_sizes: 分割的 bit 长度列表，如 [5, 3, 8]
    :return: 转换后的十进制列表
    """
    # Step 1: 转为二进制字符串并补零到足够长度
    if bit_sizes is None:
        bit_sizes = [5, 3, 8]
    binary_str = bin(int(hex_num, 16))[2:]  # 去掉 '0b' 前缀
    total_bits = sum(bit_sizes)  # 计算总位数
    binary_str = binary_str.zfill(total_bits)

    # Step 2: 按 bit_sizes 分割
    result = []
    start = 0
    for size in bit_sizes:
        segment = binary_str[start:start + size]
        result.append(int(segment, 2))  # 将二进制段转为十进制
        start += size
    return '/'.join(map(str, result))


def custom_decimals_to_hex(decimal_str, bit_sizes=None):
    """
    将分割后的十进制字符串转换为十六进制数。
    KNX设备模拟器适用
    :param decimal_str: 用 '/' 分割的十进制字符串
    :param bit_sizes: 对应的 bit 长度列表
    :return: 转换后的十六进制字符串
    """
    # Step 1: 将输入字符串转换为整数列表
    if bit_sizes is None:
        bit_sizes = [5, 3, 8]
    decimal_list = list(map(int, decimal_str.split('/')))

    # Step 2: 将每个整数转为指定 bit 长度的二进制字符串并拼接
    binary_str = ""
    for value, size in zip(decimal_list, bit_sizes):
        binary_segment = bin(value)[2:].zfill(size)  # 转为二进制并补零
        binary_str += binary_segment

    # Step 3: 将拼接后的二进制字符串转为十六进制
    hex_result = hex(int(binary_str, 2))[2:].upper()  # 去掉 '0x' 并转为大写
    return hex_result

def parse_input(input_str):
    """
    输入字符串格式 lliot/fiids_report/0001202ce8a788ba36b4001/204...206
    输出列表['lliot/fiids_report/0001202ce8a788ba36b4001/204','lliot/fiids_report/0001202ce8a788ba36b4001/205','lliot/fiids_report/0001202ce8a788ba36b4001/206']
    输入格式 lliot/fiids_report/0001202ce8a788ba36b4001/204:lliot/fiids_report/0001202ce8a788ba36b4001/207
    输出列表['lliot/fiids_report/0001202ce8a788ba36b4001/204','lliot/fiids_report/0001202ce8a788ba36b4001/207']
    :param input_str: 输入字符
    :return: 处理后列表
    """
    result = []
    if "..." in input_str:
        # 处理范围格式
        prefix, range_part = input_str.rsplit("/", 1)
        start, end = map(int, range_part.split("..."))
        result = [f"{prefix}/{i}" for i in range(start, end + 1)]
    elif ":" in input_str:
        # 处理冒号格式
        parts = input_str.split(":")
        result = list(parts)
    return result
