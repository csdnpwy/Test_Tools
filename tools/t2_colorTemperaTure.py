#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import json
import sys
import time
import pyautogui
from datetime import datetime

from PIL import ImageGrab

from handlers.app_handler import get_terminal_info, app_request
from handlers.log_handler import get_log
from commons.variables import *
from handlers.mysql_tool import MyPymysqlPool


def t2_colorTemperaTure(args, log_path):
    global db_tool, devices_did, app
    mysql_info = {}
    env_info = {}
    get_log(log_path).debug(args)
    # 环境环境获取
    get_log(log_path).info(f'检测测试环境中...')
    get_log(log_path).info("*" * gap_num)
    envs = {
        'iotpre': iotpre,
        'iottest': iottest,
        '56': iot56,
        '58': iot58,
    }
    evn = args.测试环境
    if evn in envs:
        mysql_info = {'host': f'{envs[evn]["云端DB_Host_v"]}', 'port': f'{envs[evn]["云端DB_Port_v"]}',
                      'user': f'{envs[evn]["云端DB_用户名_v"]}',
                      'password': f'{envs[evn]["云端DB_密码_v"]}', 'db_name': f'{envs[evn]["云端DB_库名_v"]}',
                      'charset': 'utf8'}
        env_info.update(mysql_info)
    else:
        get_log(log_path).error(f'未找到{evn}环境下的任何配置，请联系管理员处理！')
        sys.exit()
    # APP信息获取
    try:
        # 判断用户名密码是否正确
        db_tool = MyPymysqlPool(mysql_info)
        username = f"{args.用户名}"
        password = hashlib.sha256(f'{args.密码}'.encode('utf-8')).hexdigest()
        user_pw_sql = f"select password from lbl_app_account where username = '{username}'"
        user_pw_sql_res = db_tool.getAll(user_pw_sql)
        if not user_pw_sql_res:
            get_log(log_path).error(f'    !!!!    APP用户名不存在')
            sys.exit()
        else:
            if password == user_pw_sql_res[0]['password']:
                get_log(log_path).info(f'    ----    APP用户名、密码正确')
                time.sleep(2)
            else:
                get_log(log_path).error(f'    !!!!    APP密码错误')
                sys.exit()
        # 获取网关绑定的住家和房间
        sql_group_id = f"select group_id from newiot_device_group ndg  where biz_id = (select id from iot_dc_logic_device idld  where did = '{args.Did}' and siid = '2')"
        group_id = db_tool.getAll(sql_group_id)
        sql = f"select id, parent_id, name  from newiot_group ng  where id = '{group_id[0]['group_id']}'"
        res = db_tool.getAll(sql)
        homeId = res[0]['parent_id']
        room = res[0]['name']
        roomID = res[0]['id']
        app = {
            'username': f'{args.用户名}',
            'pw': f'{args.密码}',
            'homeID': f'{homeId}',
            f'{room}id': f'{roomID}'
        }
        env_info.update(app)
        get_log(log_path).info(f'    ----    数据库连通性正常')
        time.sleep(2)
        get_log(log_path).info(f'    ----    APP获取网关绑定住家及房间正常')
        time.sleep(2)
        # 获取网关下挂设备
        sql_devices = f"select did from account.iot_device aadi where direct_did = '{args.Did}' and model = '{args.测试模型}'"
        devices_did = db_tool.getAll(sql_devices)
        if not devices_did or len(devices_did) != 1:
            get_log(log_path).error(f'    !!!!    网关未下挂任何预测试设备或下挂多个同模型设备')
            sys.exit()
    except Exception as e:
        get_log(log_path).error(f"APP信息处理发生错误: {e}\n1、请确保所选环境与APP一致\n2、确保测试住家下只绑定一个预测试网关\n3、确保网关did填写正确")
        sys.exit()
    get_log(log_path).info("*" * gap_num)
    get_log(log_path).info(f'开始执行测试...')
    nums = args.测试轮询次数
    terminal_info = get_terminal_info(envs[evn]["云端环境_v"], mysql_info, args.用户名, args.密码, log_path)
    accessToken = json.loads(terminal_info)['params']['accessToken']
    url = f"{envs[evn]['云端环境_v']}/rest/app/community/encryptV1CtrlFIIDS"
    x, y = 50, 50
    pic_dir = f"{log_dir}t2_colorTemperaTure\\pic\\"
    os.makedirs(os.path.dirname(pic_dir), exist_ok=True)
    low_data = {
        "seq": 999,
        "version": "v0.1",
        "params": {
            "did": f"{devices_did[0]['did']}",
            "directDid": f"{args.Did}",
            "siid": 2,
            "fiids": [
                {
                    "value": {
                        "colorTemperaTure": 2700
                    },
                    "fiid": 49229
                }
            ]
        }
    }
    high_data = {
        "seq": 999,
        "version": "v0.1",
        "params": {
            "did": f"{devices_did[0]['did']}",
            "directDid": f"{args.Did}",
            "siid": 2,
            "fiids": [
                {
                    "value": {
                        "colorTemperaTure": 6500
                    },
                    "fiid": 49229
                }
            ]
        }
    }
    for num in range(0, nums):
        get_log(log_path).info(f'第 {num + 1} 次控制筒射灯色温为最高...')
        res = app_request(accessToken, url, high_data, log_path)
        get_log(log_path).debug(f"{res}")
        get_log(log_path).info(f"app下发成功，等待截屏...")
        time.sleep(10)
        # 点击屏幕规避浏览器自动退出
        pyautogui.click(x, y)
        screenshot = ImageGrab.grab()
        img_time = datetime.now().strftime('%Y%m%d%H%M%S')
        screenshot.save(f"{pic_dir}{img_time}.png")
        get_log(log_path).info(f"截屏完成，已保存至{pic_dir}{img_time}.png")
        get_log(log_path).info(f'第 {num + 1} 次控制筒射灯色温为最低...')
        res = app_request(accessToken, url, low_data, log_path)
        get_log(log_path).debug(f"{res}")
        get_log(log_path).info(f"app下发成功，等待截屏...")
        time.sleep(10)
        # 点击屏幕规避浏览器自动退出
        pyautogui.click(x, y)
        screenshot = ImageGrab.grab()
        img_time = datetime.now().strftime('%Y%m%d%H%M%S')
        screenshot.save(f"{pic_dir}{img_time}.png")
        get_log(log_path).info(f"截屏完成，已保存至{pic_dir}{img_time}.png")


