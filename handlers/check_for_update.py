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
    """
    软件版本更新
    :param log_path:
    :return:
    """
    current_version = version
    hfs = hfs_url
    conf_version = f"{hfs}version.ini"
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
            description = conf_reder.get_value('info', 'description')
            # 软件版本更新
            if int(ver) > int(current_version):
                # 创建确认对话框
                message = f"发现新版本{ver},是否更新？\n\n更新内容：\n{description}"
                confirmed = messagebox.askyesno("确认", message)
                # 根据用户的选择执行操作
                if confirmed:
                    # 显示正在更新提示框
                    updating_message = tk.Toplevel(root)
                    updating_message.title("正在更新")
                    updating_message.geometry("300x80")
                    tk.Label(updating_message, text="正在更新，请稍等...", font=18).pack(pady=20)

                    # 使窗口居中显示
                    root.update_idletasks()
                    x = (root.winfo_screenwidth() // 2) - (updating_message.winfo_reqwidth() // 2)
                    y = (root.winfo_screenheight() // 2) - (updating_message.winfo_reqheight() // 2)
                    updating_message.geometry(f"+{x}+{y}")
                    updating_message.update()

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
                        # 关闭“正在更新”提示框
                        updating_message.destroy()
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

def profile_check_for_update(log_path):
    """
    配置生成器 - 配置文件检查更新
    :param log_path: 日志存储路径
    """
    conf_reder = ConfigReader(f"{log_dir}version.ini")
    profile = os.path.join(project_root, "template", "profile_template.txt")
    profile_md5 = conf_reder.get_value('info', 'profileMD5').lower()
    local_md5 = "test"
    # 如果目录不存在则创建
    profile_dir = os.path.dirname(profile)
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
        get_log(log_path).debug(f'创建目录: {profile_dir}')
    elif not os.path.exists(profile):
        pass
    else:
        local_md5 = calculate_md5(profile).lower()
    if local_md5 != profile_md5:
        down_url = conf_reder.get_value('info', 'profile_url')
        response = requests.get(down_url)
        if response.status_code == 200:
            with open(profile, 'wb') as temp_file:
                temp_file.write(response.content)
                get_log(log_path).debug(f'配置文件更新成功！\nprofile_md5:{profile_md5}\nlocal_md5:{local_md5}')
        else:
            get_log(log_path).info(f'配置文件更新失败！请求内容{response.status_code}-{response.text}')
            sys.exit()
    else:
        get_log(log_path).debug(f'已是最新配置文件模板！')

def profile_rf7_check_for_update(log_path):
    """
    配置生成器 - 配置文件检查更新（新框架RF7.0配置文件）
    :param log_path: 日志存储路径
    """
    conf_reder = ConfigReader(f"{log_dir}version.ini")
    profile = os.path.join(project_root, "template", "profile_template_rf7.txt")
    profile_md5 = conf_reder.get_value('info', 'profileMD5_rf7').lower()
    local_md5 = "test"
    # 如果目录不存在则创建
    profile_dir = os.path.dirname(profile)
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
        get_log(log_path).debug(f'创建目录: {profile_dir}')
    elif not os.path.exists(profile):
        pass
    else:
        local_md5 = calculate_md5(profile).lower()
    if local_md5 != profile_md5:
        down_url = conf_reder.get_value('info', 'profile_url_rf7')
        response = requests.get(down_url)
        if response.status_code == 200:
            with open(profile, 'wb') as temp_file:
                temp_file.write(response.content)
                get_log(log_path).debug(f'配置文件更新成功！\nprofile_md5_rf7:{profile_md5}\nlocal_md5_rf7:{local_md5}')
        else:
            get_log(log_path).info(f'配置文件更新失败！请求内容{response.status_code}-{response.text}')
            sys.exit()
    else:
        get_log(log_path).debug(f'已是最新配置文件模板！')

def config_check_for_update(log_path):
    """
    链路时长监控 - config配置文件检查更新
    :param log_path: 日志存储路径
    """
    conf_reder = ConfigReader(f"{log_dir}version.ini")
    config = os.path.join(project_root, "configs", "config.cnf")
    config_md5 = conf_reder.get_value('info', 'configMD5').lower()
    local_md5 = "test"
    # 如果目录不存在则创建
    config_dir = os.path.dirname(config)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        get_log(log_path).debug(f'创建目录: {config_dir}')
    elif not os.path.exists(config):
        pass
    else:
        local_md5 = calculate_md5(config).lower()
    if local_md5 != config_md5:
        down_url = conf_reder.get_value('info', 'config_url')
        response = requests.get(down_url)
        if response.status_code == 200:
            with open(config, 'wb') as temp_file:
                temp_file.write(response.content)
                get_log(log_path).debug(f'config配置文件更新成功！\nconfig_md5:{config_md5}\nlocal_md5:{local_md5}')
        else:
            get_log(log_path).info(f'配置文件更新失败！请求内容{response.status_code}-{response.text}')
            sys.exit()
    else:
        get_log(log_path).debug(f'已是最新config配置文件！')


def driver_check_for_update(log_path):
    """
    web-OTA中断电压测 & web-reboot - 浏览器驱动文件检查更新
    :param log_path: 日志存储路径
    """
    conf_reder = ConfigReader(f"{log_dir}version.ini")
    driver = os.path.join(project_root, "drivers", "chromedriver.exe")
    driver_md5 = conf_reder.get_value('info', 'chromedriverMD5').lower()
    local_md5 = "test"
    # 如果目录不存在则创建
    driver_dir = os.path.dirname(driver)
    if not os.path.exists(driver_dir):
        os.makedirs(driver_dir)
        get_log(log_path).debug(f'创建目录: {driver_dir}')
    # 如果文件不存在则创建一个空文件
    elif not os.path.exists(driver):
        pass
    else:
        local_md5 = calculate_md5(driver).lower()
    if local_md5 != driver_md5:
        down_url = conf_reder.get_value('info', 'chromedriver_url')
        response = requests.get(down_url)
        if response.status_code == 200:
            with open(driver, 'wb') as temp_file:
                temp_file.write(response.content)
                get_log(log_path).debug(f'浏览器驱动文件更新成功！\ndirver_md5:{driver_md5}\nlocal_md5:{local_md5}')
        else:
            get_log(log_path).info(f'浏览器驱动文件更新失败！请求内容{response.status_code}-{response.text}')
            sys.exit()
    else:
        get_log(log_path).debug(f'已是最新浏览器驱动文件！')

def audio_check_for_update(log_path):
    """
    真实设备链路监控之小立管家场景 - 音频文件检查更新
    :param log_path: 日志存储路径
    """
    conf_reder = ConfigReader(f"{log_dir}version.ini")
    audio_info = {
        "open_light_audio": os.path.join(project_root, "audio", "小立管家", "小立管家开灯.wav"),
        "close_light_audio": os.path.join(project_root, "audio", "小立管家", "小立管家关灯.wav")
    }
    audio_md5 = {
        "open_light_audio_md5": conf_reder.get_value('info', 'open_light_audioMD5').lower(),
        "close_light_audio_md5": conf_reder.get_value('info', 'close_light_audioMD5').lower()
    }
    local_md5 = "test"
    for (audio_name, audio_path), (audio_name_md5, value) in zip(audio_info.items(), audio_md5.items()):
        # 如果目录不存在则创建
        audio_dir = os.path.dirname(audio_path)
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
            get_log(log_path).debug(f'创建目录: {audio_dir}')
        # 如果文件不存在则创建一个空文件
        elif not os.path.exists(audio_path):
            pass
        else:
            local_md5 = calculate_md5(audio_path).lower()
        if local_md5 != value:
            down_url = conf_reder.get_value('info', f"{audio_name}_url")
            response = requests.get(down_url)
            if response.status_code == 200:
                with open(audio_path, 'wb') as temp_file:
                    temp_file.write(response.content)
                    get_log(log_path).debug(f'音频文件文件更新成功！\nremote_md5:{value}\nlocal_md5:{local_md5}')
            else:
                get_log(log_path).info(f'音频文件更新失败！请求内容{response.status_code}-{response.text}')
                sys.exit()
        else:
            get_log(log_path).debug(f'已是最新音频文件！')


# if __name__ == '__main__':
#     log_path = f"{log_dir}check_for_update.txt"
#     check_for_update(log_path)
