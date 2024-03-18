#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import hashlib
import json
import sys
import time

from handlers.app_handler import get_terminal_info, app_request
from handlers.bluetooth_handler import light_strip_bluetooth_connection
from handlers.log_handler import get_log
from commons.variables import *
from handlers.mysql_tool import MyPymysqlPool


def gw_bind_unbind_pressure(args, log_path):
    global db_tool, app
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
    else:
        get_log(log_path).error(f'未找到{evn}环境下的任何配置，请联系管理员处理！')
        sys.exit()
    # APP信息获取
    try:
        # 判断用户名密码是否正确
        db_tool = MyPymysqlPool(mysql_info)
        username = f"{args.用户名}"
        password = hashlib.sha256(f'{args.密码}'.encode('utf-8')).hexdigest()
        user_pw_sql = f"select password, app_code from lbl_app_account where username = '{username}'"
        user_pw_sql_res = db_tool.getAll(user_pw_sql)
        app_code = user_pw_sql_res[0]['app_code']
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
        roomID = res[0]['id']
        sql_profileId = f"select profile_id from iot_dc_logic_device idld  where did = '{args.Did}' and siid = '2'"
        res_profileId = db_tool.getAll(sql_profileId)
        profileId = res_profileId[0]['profile_id']
        get_log(log_path).info(f'    ----    数据库连通性正常')
        time.sleep(2)
        get_log(log_path).info(f'    ----    APP获取设备绑定住家及房间正常')
        time.sleep(2)
    except Exception as e:
        get_log(log_path).error(f"APP信息处理发生错误: {e}\n1、请确保所选环境与APP一致\n2、确保设备did填写正确")
        sys.exit()
    get_log(log_path).info("*" * gap_num)
    get_log(log_path).info(f'开始执行测试...')
    nums = args.测试轮询次数
    terminal_info = get_terminal_info(envs[evn]["云端环境_v"], mysql_info, args.用户名, args.密码, log_path)
    accessToken = json.loads(terminal_info)['params']['accessToken']
    unbind_url = f"{envs[evn]['云端环境_v']}/rest/app/community/smartHome/unbindDevice"
    bind_url = f"{envs[evn]['云端环境_v']}/rest/app/community/smartHome/bindDevice"
    getDevicePermission_url = f"{envs[evn]['云端环境_v']}/rest/app/community/mergeHomes/getDevicePermission"
    getDevices_url = f"{envs[evn]['云端环境_v']}/rest/app/community/smartHome/getDevices"
    getConnectNetworkToken_url = f"{envs[evn]['云端环境_v']}/rest/app/community/getConnectNetworkToken"
    unbind_data = {
        "seq": 999,
        "version": "v0.1",
        "params": {
            "did": f"{args.Did}",
            "directDid": f"{args.Did}"
        }
    }
    bind_data = {
        "seq": 999,
        "version": "v0.1",
        "params": {
            "did": f"{args.Did}",
            "bindInfo": {
                "groupId": f"{homeId}",
                "subGroupId": f"{roomID}",
                "profileId": f"{profileId}",
                "userName": f"{username}",
                "appCode": app_code,
                "location": "(null),(null)"
            }
        }
    }
    getDevicePermission_data = {
        "params": {
            "siid": 0,
            "groupId": homeId,
            "directDid": f"{args.Did}",
            "isShared": 0,
            "did": f"{args.Did}"
        },
        "seq": 666,
        "version": "V1.0"
    }
    getDevices_data = {
        "params": {
            "did": f"{args.Did}",
            "directDid": f"{args.Did}"
        },
        "seq": 888,
        "version": "V1.0"
    }
    getConnectNetworkToken_data = {
        "params": {
            "clientId": "1",
            "expireTime": 180,
            "phone": "18650041613"
        },
        "seq": 111,
        "version": "V1.0"
    }
    for num in range(0, nums):
        try:
            get_log(log_path).info(f'第 {num + 1} 次解绑操作...')
            res = app_request(accessToken, unbind_url, unbind_data, log_path)
            if json.loads(res)["result"] == 1:
                get_log(log_path).info(f" --- APP发送解绑请求成功")
                time.sleep(3)
                group_id = db_tool.getAll(sql_group_id)
                if group_id:
                    get_log(log_path).error(f" !!! 设备解绑失败")
                else:
                    get_log(log_path).info(f" --- 设备解绑成功")
            else:
                get_log(log_path).error(f" !!! APP发送解绑请求失败")
            time.sleep(args.测试间隔时长)
            get_log(log_path).info(f'第 {num + 1} 次绑定操作...')
            if args.设备类型 == '网关':
                res = app_request(accessToken, bind_url, bind_data, log_path)
                if json.loads(res)["result"] == 1:
                    get_log(log_path).info(f" --- APP发送绑定请求成功")
                    time.sleep(3)
                    group_id = db_tool.getAll(sql_group_id)
                    if group_id:
                        get_log(log_path).error(f" --- 设备绑定成功")
                    else:
                        get_log(log_path).info(f" !!! 设备绑定失败")
                else:
                    get_log(log_path).error(f" !!! APP发送绑定请求失败")
            elif args.设备类型 == 'wifi灯带':
                res = app_request(accessToken, getConnectNetworkToken_url, getConnectNetworkToken_data, log_path)
                token = json.loads(res)["params"]["token"]
                asyncio.run(light_strip_bluetooth_connection(args, token, log_path))
                get_log(log_path).info(f" --- 等待设备配网中")
                time.sleep(30)
                res = app_request(accessToken, bind_url, bind_data, log_path)
                if json.loads(res)["result"] == 1:
                    get_log(log_path).info(f" --- APP发送绑定请求成功")
                    res = app_request(accessToken, getDevicePermission_url, getDevicePermission_data, log_path)
                    if json.loads(res)["result"] == 1:
                        app_request(accessToken, getDevices_url, getDevices_data, log_path)
                        time.sleep(3)
                        group_id = db_tool.getAll(sql_group_id)
                        if group_id:
                            get_log(log_path).error(f" --- 设备绑定成功")
                        else:
                            get_log(log_path).info(f" !!! 30S内设备绑定失败")
                else:
                    get_log(log_path).error(f" !!! APP发送绑定请求失败")
            else:
                get_log(log_path).error(f" !!! 不支持此设备类型的绑定操作")
            time.sleep(args.测试间隔时长)
        except Exception as e:
            get_log(log_path).error(f" !!! 发生不可预知错误，将直接跳过本次轮询：{e}")
            time.sleep(2)
