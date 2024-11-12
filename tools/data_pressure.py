#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import hashlib
import json
import sys
import time
import pandas as pd
from ping3 import ping

from commons.variables import *
from handlers.app_handler import get_terminal_info, app_request
from handlers.error_handler import CustomError
from handlers.global_handler import get_stake_did, is_ping_successful
from handlers.log_handler import get_log
from handlers.mqtt_handler import MQTTClient
from handlers.mysql_tool import MyPymysqlPool
from handlers.pdu_handler import ctl_pdu


def data_pressure(args, log_path):
    """
    传感器联动链路时长获取
    :param args: 前端参数
    :param log_path: 日志路径
    """
    get_log(log_path).debug(args)
    get_log(log_path).info(f'Step 1：检测测试环境...')
    # 检测测试环境
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
    # 判断用户名密码是否正确
    db_tool = MyPymysqlPool(mysql_info)
    username = f"{args.APP用户名}"
    password = hashlib.sha256(f'{args.APP密码}'.encode('utf-8')).hexdigest()
    user_pw_sql = f"select password from lbl_app_account where username = '{username}'"
    try:
        user_pw_sql_res = db_tool.getAll(user_pw_sql)
        get_log(log_path).info(f'    ----    数据库访问正常')
        time.sleep(2)
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
    except Exception as e:
        get_log(log_path).error(f"    !!!!    数据库连通性异常 {e}")
        sys.exit()
    # 进行压测
    protocol = args.压测协议
    excel_path = args.Path
    nums = args.测试轮询次数
    get_log(log_path).info(f'Step 2：即将进行{protocol}压测...')
    if protocol == "HTTP":
        # 获取接口token
        terminal_info = get_terminal_info(envs[evn]["云端环境_v"], mysql_info, args.APP用户名, args.APP密码, log_path)
        accessToken = json.loads(terminal_info)['params']['accessToken']
        # 设置过期时间
        token_expiry = datetime.now() + timedelta(hours=22)
        # 读取 Excel 文件
        df = pd.read_excel(excel_path, sheet_name="Http")
        for num in range(0, int(nums)):
            # 防止token过期
            if datetime.now() >= token_expiry:
                terminal_info = get_terminal_info(envs[evn]["云端环境_v"], mysql_info, args.APP用户名, args.密码, log_path)
                accessToken = json.loads(terminal_info)['params']['accessToken']
                token_expiry = datetime.now() + timedelta(hours=20)  # 重置计时器
            get_log(log_path).info(f'    ----    进行第{num + 1}轮压测')
            for index, row in df.iterrows():
                if row['是否执行'] == 'T':
                    get_log(log_path).error(f"        ----        执行用例-[{row['用例编号']}-{row['用例名称']}]")
                    if row['用例名称'] == "睡眠":
                        time.sleep(int(row["请求数据"]))
                        continue
                    elif row['用例名称'] == "迅威上电":
                        pdu_ip = row["请求数据"].split(',')[0]
                        check_ip = row["请求数据"].split(',')[-1]
                        pdu_lock = row["请求数据"].split(',')[1]
                        ctl_pdu(pdu_ip, port=502, lock=pdu_lock, ctl_modul='seewe', tcp_type='tcp')
                        for i in range(0, 20):
                            ping_res = ping(check_ip)
                            get_log(log_path).debug(f'        ----        Ping ip: {check_ip} Res: {ping_res}')
                            if is_ping_successful(ping_res):
                                get_log(log_path).info(f'        ----        {check_ip}已上电')
                                break
                            else:
                                get_log(log_path).debug(f'        ----        {(i+1)*5}S内还未上电，继续等待...')
                                ctl_pdu(pdu_ip, port=502, lock=pdu_lock, ctl_modul='seewe', tcp_type='tcp')
                                time.sleep(5)
                                if i == 19:
                                    get_log(log_path).error(f'        !!!!        100S内上电失败')
                                    raise CustomError("测试异常！")
                        continue
                    elif row['用例名称'] == "迅威下电":
                        pdu_ip = row["请求数据"].split(',')[0]
                        check_ip = row["请求数据"].split(',')[-1]
                        pdu_lock = row["请求数据"].split(',')[1]
                        ctl_pdu(pdu_ip, port=502, lock=pdu_lock, ctl='close', ctl_modul='seewe', tcp_type='tcp')
                        for i in range(0, 20):
                            ping_res = ping(check_ip)
                            if not is_ping_successful(ping_res):
                                get_log(log_path).info(f'        ----        {check_ip}已下电')
                                break
                            else:
                                get_log(log_path).debug(f'        ----        {(i + 1) * 5}S内还未下电，继续等待...')
                                ctl_pdu(pdu_ip, port=502, lock=pdu_lock, ctl='close', ctl_modul='seewe', tcp_type='tcp')
                                time.sleep(5)
                                if i == 19:
                                    get_log(log_path).error(f'        !!!!        100S内下电失败')
                                    raise CustomError("测试异常！")
                        continue
                    post_data = json.loads(row["请求数据"])
                    expect_res = row["预期请求结果"]
                    url = f"{envs[evn]['云端环境_v']}{row['请求URL']}"
                    for i in range(0, 3):
                        res = app_request(accessToken, url, post_data, log_path)
                        get_log(log_path).debug(f"{res}")
                        if expect_res in res:
                            get_log(log_path).error(f"        ----        与预期请求结果相符，测试正常")
                            break
                        else:
                            get_log(log_path).error(f"        !!!!        与预期请求结果不符，10S后重新发起请求")
                            time.sleep(10)
                            if i == 2:
                                get_log(log_path).error(f'        !!!!        达到重试限制，测试失败')
                                raise CustomError("测试异常！")
            time.sleep(args.测试间隔时长)
    if protocol == "MQTT":
        # 获取接口token
        terminal_info = get_terminal_info(envs[evn]["云端环境_v"], mysql_info, args.APP用户名, args.APP密码, log_path)
        accessToken = json.loads(terminal_info)['params']['accessToken']
        get_log(log_path).info(f'    ----    启用MQTT客户端')
        environment = envs[evn]["云端环境_v"]
        did = get_stake_did(accessToken, environment, log_path)
        username = "HA-CE-R31-001"
        sql_did = f"select device_secret from iot_device where did = '{did}'"
        device_secret_res = db_tool.getAll(sql_did)
        if not device_secret_res:
            try:
                # 创建MQTT客户端
                password = hashlib.sha256('jhfeq6vsxonjjlfa'.encode('utf-8')).hexdigest()
                mqtt_client = MQTTClient(log_path, f'{envs[evn]["云端MQTT_Host_v"]}', username=username,
                                         password=password, client_id=did, args=args)
                # 连接到MQTT代理
                mqtt_client.connect()
                # 订阅主题
                mqtt_client.subscribe(f"lliot/receiver/{did}")
                # 发布消息
                payload = {
                    "method": "dmgr.reg",
                    "src": f"{did}",
                    "dst": f'{dev_manage_moduleID}',
                    "version": "V1.0",

                    "params": {
                        "did": f"{did}",
                        "softModel": f"{username}",
                        "profileId": 7
                    },
                    "seq": 1
                }
                mqtt_client.publish(f"lliot/receiver/{dev_manage_moduleID}", json.dumps(payload))
                get_log(log_path).info(f'        ----        注册MQTT桩中...')
                time.sleep(3)
                # 启动消息循环
                mqtt_client.start_loop()
                # 停止消息循环
                mqtt_client.stop_loop()
                # 断开连接
                mqtt_client.disconnect()
                device_secret_res = db_tool.getAll(sql_did)
                if device_secret_res:
                    print(f'        ----        桩did={did}注册成功')
                    time.sleep(2)
                else:
                    get_log(log_path).error(f"        ----        桩did={did}注册失败！")
                    sys.exit()
            except Exception as e:
                get_log(log_path).error(f'        !!!!        注册MQTT桩失败：{e}')
                sys.exit()
        else:
            get_log(log_path).info(f'        ----        MQTT桩已存在，无需注册...')
        # 一机一密连接到MQTT代理
        mqtt_client = MQTTClient(log_path, f'{envs[evn]["云端MQTT_Host_v"]}', username=f"{username}:{did}",
                                 password=f"{device_secret_res[0]['device_secret']}", client_id=did, args=args)
        mqtt_client.connect()
        time.sleep(5)
        # 读取 Excel 文件
        df = pd.read_excel(excel_path, sheet_name="Mqtt")
        for num in range(0, int(nums)):
            get_log(log_path).info(f'    ----    进行第{num + 1}轮压测')
            for index, row in df.iterrows():
                if row['是否执行'] == 'T':
                    get_log(log_path).error(f"        ----        执行用例-[{row['用例编号']}-{row['用例名称']}]")
                    if row['用例名称'] == "睡眠":
                        time.sleep(int(row["请求数据"]))
                        continue
                    post_data = json.loads(row["请求数据"])
                    expect_res = row["预期请求结果"]
                    publish_topic = row["发布主题"]
                    subscribe_topic = row["订阅主题"]
                    mqtt_client.subscribe(subscribe_topic)
                    time.sleep(1)
                    mqtt_client.publish(publish_topic, json.dumps(post_data))
                    time.sleep(5)
                    mes = mqtt_client.get_message().get(subscribe_topic, None)
                    for i in range(0, 3):
                        if expect_res in str(mes):
                            get_log(log_path).error(f"        ----        与预期请求结果相符，测试正常")
                            break
                        else:
                            get_log(log_path).error(f"        !!!!        与预期请求结果不符，10S后重新发起请求")
                            time.sleep(10)
                            mqtt_client.publish(topic=publish_topic, message=post_data)
                            mes = mqtt_client.get_message().get(subscribe_topic, None)
                            if i == 2:
                                get_log(log_path).error(f'        !!!!        达到重试限制，测试失败')
                                raise CustomError("测试异常！")
            time.sleep(args.测试间隔时长)
    else:
        get_log(log_path).error(f'    !!!!    暂不支持此协议压测，敬请期待')
        sys.exit()
    get_log(log_path).info("*" * gap_num)
    try:
        # 关闭数据库
        db_tool.dispose()
        # 关闭mqtt连接
        mqtt_client.disconnect()
    except Exception:
        pass
    get_log(log_path).info(f'测试结束，具体压测数据请看日志')
