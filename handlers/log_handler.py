import logging
import os
import sys


# 生成日志记录器
# 参数：日志存储路径
# 返回：日志记录器
def get_log(log_path):
    # 创建日志目录
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    # 创建日志记录器
    logger = logging.getLogger("execute_log")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        # 创建日志处理器，一个输出到桌面，一个输出到文件
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setLevel(logging.INFO)
        file_handler = logging.FileHandler(filename=log_path, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        # 设置日志格式
        formatter = logging.Formatter("[%(levelname)s] %(asctime)s [%(filename)s:%(lineno)d, %(funcName)s] %(message)s")
        # 为处理器设置格式
        # screen_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        # 添加日志处理器到日志记录器
        logger.addHandler(screen_handler)
        logger.addHandler(file_handler)
    return logger
