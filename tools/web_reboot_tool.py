#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time

from ping3 import ping
from selenium.webdriver.common.by import By

from commons.variables import project_root
from handlers.error_handler import CustomError
from handlers.log_handler import get_log
from handlers.selenium_handler import SeleniumWrapper


def web_reboot_tool(args, log_path):
    """
    主机软重启
    :param args: 前端参数
    :param log_path:  日志保存路径
    """
    get_log(log_path).debug(args)
    # 检测测试环境
    get_log(log_path).info(f'Step 1：检测测试环境...')
    ping_res = ping(f"{args.主机IP}")
    if ping_res is not None:
        get_log(log_path).info(f'    ----    被测主机ip={args.主机IP}连通性正常')
        time.sleep(2)
    else:
        get_log(log_path).error(f'    !!!!    被测主机ip={args.主机IP}无法连通,请检查设备!')
        raise CustomError("环境异常，停止压测！")
    get_log(log_path).info(f'Step 2：环境检测正常，开始执行测试...')
    nums = args.压测次数
    url = f"http://{args.主机IP}/"
    # 指定ChromeDriver路径
    driver_path = os.path.join(project_root, "drivers", "chromedriver.exe")
    user_id = 'username'
    password_id = 'password'
    log_in_class_name = 'input_save'
    save_name = 'save'
    selenium_wrapper = SeleniumWrapper(log_path=log_path, driver_path=driver_path)
    for num in range(0, nums):
        get_log(log_path).info(f'    ----    开始执行第{num + 1}轮测试...')
        # 打开URL
        get_log(log_path).info(f'        ----        打开主机配置页面并登录...')
        selenium_wrapper.open_url(url)
        selenium_wrapper.wait_for_element(By.ID, user_id)
        # 登录
        selenium_wrapper.send_keys(By.ID, user_id, 'admin')
        time.sleep(1)
        selenium_wrapper.send_keys(By.ID, password_id, '123456')
        time.sleep(1)
        selenium_wrapper.click_element(By.CLASS_NAME, log_in_class_name)
        # 划到底部
        selenium_wrapper.scroll_to_bottom()
        time.sleep(2)
        get_log(log_path).info(f'        ----        点击保存配置...')
        # 点击保存
        selenium_wrapper.click_element(By.NAME, save_name)
        time.sleep(1)
        # 处理弹窗
        get_log(log_path).info(f'        ----        点击重启弹窗提示...')
        alert_info = selenium_wrapper.handle_alert(action='get_text')
        get_log(log_path).debug(alert_info)
        if "the device will be restarted" in alert_info:
            selenium_wrapper.handle_alert()
            time.sleep(8)
        else:
            get_log(log_path).error(f'        !!!!        保存异常，未触发重启弹窗提示！')
            raise CustomError("测试异常！")
        for i in range(0, 6):
            ping_res = ping(f"{args.主机IP}")
            if ping_res is not None:
                get_log(log_path).info(f'        ----        被测主机已能正常ping通，{args.间隔时长}秒后将进行下一轮测试...')
                time.sleep(args.间隔时长)
                break
            else:
                if i == 5:
                    get_log(log_path).error(f'        !!!!        30S内被测主机ip仍无法连通，结束测试!')
                    raise CustomError("测试失败，停止压测！")
                else:
                    get_log(log_path).error(f'        !!!!        被测主机ip无法连通,5S后将重新检测!')
                    time.sleep(5)
    get_log(log_path).info(f'Step 3：测试结束，关闭浏览器...')
    selenium_wrapper.close()
