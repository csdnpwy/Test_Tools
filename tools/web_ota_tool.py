import os
import time

from ping3 import ping

from commons.variables import project_root
from handlers.error_handler import CustomError
from handlers.global_handler import is_ping_successful
from handlers.log_handler import get_log
from handlers.pdu_handler import ctl_pdu
from handlers.selenium_handler import SeleniumWrapper
from selenium.webdriver.common.by import By

def web_ota_tool(args, log_path):
    """
    门禁海外web上下电压测
    :param args:
    :param log_path:
    """
    get_log(log_path).debug(args)
    # 检测测试环境
    get_log(log_path).info(f'Step 1：检测测试环境...')
    ping_res = ping(f"{args.主机IP}")
    get_log(log_path).debug(f'{args.主机IP}连通测试结果：{ping_res}')
    if is_ping_successful(ping_res):
        get_log(log_path).info(f'    ----    被测主机ip={args.主机IP}连通性正常')
        time.sleep(2)
    else:
        get_log(log_path).error(f'    !!!!    被测主机ip={args.主机IP}无法连通,请检查设备!')
        raise CustomError("环境异常，停止压测！")
    ping_res = ping(f"{args.PDU_IP}")
    get_log(log_path).debug(f'{args.PDU_IP}连通测试结果：{ping_res}')
    if is_ping_successful(ping_res):
        get_log(log_path).info(f'    ----    PDU_ip={args.PDU_IP}连通性正常')
        time.sleep(2)
    else:
        get_log(log_path).error(f'    !!!!    PDU_ip={args.PDU_IP}无法连通,请检查设备!')
        raise CustomError("环境异常，停止压测！")
    get_log(log_path).info(f'Step 2：环境检测正常，开始执行测试...')
    nums = args.压测次数
    url = f"http://{args.主机IP}/"
    # 指定ChromeDriver路径
    driver_path = os.path.join(project_root, "drivers", "chromedriver.exe")
    user_id = 'username'
    password_id = 'password'
    log_in_class_name = 'input_save'
    upgrade_class_name = "card_submit"
    file_id = 'file'
    soft_ver_id = 'software'
    time_min = args.下电区间.split('-')[0]
    time_max = args.下电区间.split('-')[1]
    pdu_ip = args.PDU_IP
    lock = args.PDU插座号
    selenium_wrapper = SeleniumWrapper(log_path=log_path, driver_path=driver_path)
    for num in range(0, nums):
        get_log(log_path).info(f'    ----    开始执行第{num+1}轮测试...')
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
        time.sleep(1)
        # 核对软件信息
        soft_ver = selenium_wrapper.get_value(By.ID, soft_ver_id)
        if soft_ver == args.软件版本:
            get_log(log_path).info(f'        ----        当前软件版本{soft_ver}与输入版本{args.软件版本}比对正常...')
        else:
            get_log(log_path).error(f'        !!!!        当前软件版本{soft_ver}与输入版本{args.软件版本}比对异常，停止测试!')
            raise CustomError("测试异常！")
        # 软件升级
        get_log(log_path).info(f'        ----        选择升级包并进行升级...')
        selenium_wrapper.wait_for_element(By.ID, file_id)
        selenium_wrapper.send_keys(By.ID, file_id, args.升级包路径)
        time.sleep(1)
        status = selenium_wrapper.check_response_status(By.CLASS_NAME, upgrade_class_name, f'/cgi-bin/upload.cgi')
        # 理论上0不能算成功，但发现成功的机子抓不到/cgi-bin/upload.cgi，所以暂时放过，即认定失败是抓得到且状态码非200
        if status == 200 or status == 0:
            get_log(log_path).info(f'        ----        成功触发升级...')
        else:
            get_log(log_path).error(f'        !!!!        触发升级失败，返回状态码{status}...')
            raise CustomError("测试异常！")
        if int(time_min) == 0 and int(time_max) == 0:
            pass
        else:
            time_interval = int(time_min) + (num % (int(time_max) - int(time_min) + 1))
            get_log(log_path).info(f'        ----        {time_interval}S后进行断电操作...')
            time.sleep(time_interval)
            ctl_pdu(pdu_ip, lock=lock, ctl='close')
            time.sleep(2)
            for i in range(0, 3):
                ping_res = ping(f"{args.主机IP}")
                get_log(log_path).debug(f'{args.主机IP}连通测试结果：{ping_res}')
                if is_ping_successful(ping_res):
                    get_log(log_path).error(f'        !!!!        被测主机ip={args.主机IP}还能ping通，无正常下电，重试发送下电操作!')
                    ctl_pdu(pdu_ip, lock=lock, ctl='close')
                    time.sleep(2)
                    if i == 2:
                        get_log(log_path).error(f'        !!!!        被测主机ip={args.主机IP}无正常下电，重试3次均异常，停止测试!')
                        raise CustomError("测试异常！")
                else:
                    get_log(log_path).info(f'        ----        被测主机ip={args.主机IP}已正常下电')
                    time.sleep(2)
                    break
            get_log(log_path).info(f'        ----        进行上电操作...')
            ctl_pdu(pdu_ip, lock=lock)
        get_log(log_path).info(f'        ----        {args.间隔时长}后进行机器连通检测并进入下一轮测试...')
        time.sleep(args.间隔时长)
        for i in range(0, 3):
            ping_res = ping(f"{args.主机IP}")
            get_log(log_path).debug(f'{args.主机IP}连通测试结果：{ping_res}')
            if is_ping_successful(ping_res):
                get_log(log_path).info(f'        ----        被测主机ip={args.主机IP}已正常上电...')
                time.sleep(2)
                break
            else:
                get_log(log_path).error(f'        !!!!        被测主机ip={args.主机IP}未能ping通，无正常上电，重试发送上电操作!')
                ctl_pdu(pdu_ip, lock=lock)
                time.sleep(args.间隔时长)
                if i == 2:
                    get_log(log_path).error(f'        !!!!        被测主机ip={args.主机IP}无正常上电，重试3次均异常，停止测试!')
                    raise CustomError("测试异常！")
    # 关闭浏览器
    get_log(log_path).info(f'Step 3：测试结束，关闭浏览器...')
    selenium_wrapper.close()

