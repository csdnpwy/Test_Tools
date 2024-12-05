import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def get_log(log_path):
    """
    生成日志记录器，输出执行日志到前端并记录到本地文件。
    :param log_path: 日志存储路径
    :return: 日志记录器
    """
    # 创建日志目录
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    # 创建日志记录器
    logger = logging.getLogger("execute_log")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        # 创建日志处理器，一个输出到桌面，一个输出到文件
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setLevel(logging.INFO)
        # 使用 RotatingFileHandler 进行日志轮换
        file_handler = RotatingFileHandler(filename=log_path, maxBytes=400 * 1024 * 1024, backupCount=10, encoding='utf-8')
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
