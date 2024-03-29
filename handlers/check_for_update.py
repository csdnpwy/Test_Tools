#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import shutil
import sys
import time
import zipfile

import requests
import tkinter as tk
from tkinter import messagebox, ttk
from handlers.configReader import ConfigReader
from commons.variables import *
from handlers.log_handler import get_log

"""
获取文件md5值
"""
def calculate_md5(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        # 以二进制方式读取文件内容
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def check_for_update(log_path):
    current_version = version
    hfs = hfs_url
    conf_version = f"{hfs}version.ini"
    profile = os.path.join(project_root, "template", "profile_template.txt")
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    try:
        # 发送HTTP GET请求以获取最新版本信息
        response = requests.get(conf_version)
        # 检查响应状态码
        if response.status_code == 200:
            with open(f'{log_dir}version.ini', 'wb') as local_file:
                local_file.write(response.content)
            conf_reder = ConfigReader(f"{log_dir}version.ini")
            ver = conf_reder.get_value('info', 'version')
            # 配置文件更新
            profile_md5 = conf_reder.get_value('info', 'profileMD5').lower()
            local_md5 = calculate_md5(profile).lower()
            if local_md5 != profile_md5:
                down_url = conf_reder.get_value('info', 'profile_url')
                response = requests.get(down_url)
                if response.status_code == 200:
                    with open(profile, 'wb') as temp_file:
                        temp_file.write(response.content)
                        get_log(log_path).debug(f'配置文件更新成功！\nprofile_md5:{profile_md5}\nlocal_md5:{local_md5}')
            # 软件版本更新
            if int(ver) > int(current_version):
                # 创建确认对话框
                message = f"发现新版本{ver},是否更新？"
                confirmed = messagebox.askyesno("确认", message)
                # 根据用户的选择执行操作
                if confirmed:
                    down_url = conf_reder.get_value('info', 'down_url')
                    response = requests.get(down_url)
                    if response.status_code == 200:
                        update_file_path = f'{log_dir}update_file.zip'
                        with open(update_file_path, 'wb') as temp_file:
                            temp_file.write(response.content)
                        # 移动新版本文件并解压到当前执行路径
                        current_path = os.path.abspath(os.path.join(project_root, os.pardir))
                        install_path = os.path.join(current_path, "latest")
                        if os.path.exists(install_path):
                            shutil.rmtree(install_path)
                        with zipfile.ZipFile(update_file_path, 'r') as zip_ref:
                            zip_ref.extractall(install_path)
                        messagebox.showinfo("确认", f"更新完毕，安装路径{install_path}\n请重新打开最新版本软件！")
                        # 关闭当前运行的程序
                        sys.exit()
                    else:
                        message = f"检测更新失败，是否继续使用？"
                        confirmed = messagebox.askyesno("确认", message)
                        if confirmed:
                            return False
                        else:
                            return True
                else:
                    return False
            else:
                # 最新版本无操作
                pass
        else:
            message = f"检测更新失败，是否继续使用？"
            confirmed = messagebox.askyesno("确认", message)
            if confirmed:
                return False
            else:
                return True
    except Exception as e:
        get_log(log_path).error(f'更新过程发生如下错误：{e}')
        message = f"检测更新失败，是否继续使用？"
        confirmed = messagebox.askyesno("确认", message)
        if confirmed:
            return False
        else:
            return True


# if __name__ == '__main__':
#     log_path = f"{log_dir}check_for_update.txt"
#     check_for_update(log_path)
