# -*- coding: utf-8 -*-
import datetime
import hashlib
import re
import sys
import time
import pandas as pd
from commons.variables import *
from handlers.error_handler import CustomError
from handlers.log_handler import get_log
from handlers.mqtt_handler import MQTTClient
from handlers.mysql_tool import MyPymysqlPool
from handlers.mythread import HeartbeatThread
from handlers.tcp_handler import TCPClient
from lib.app.client_app import getMyAllHomeInfo, json, bindDevice
from lib.mqtt.modules import dmgr_reg
from lib.mqtt.mqtt_mes_handler import dmgr_subDeviceOnlineStatus, dmgr_reportPIIDS, dmgr_reportAddDevice, gw_bind, \
    gw_random, gw_login, gw_transparent


class MyListener:
    """
    mdns监听器
    """
    def __init__(self, local_name):
        self.local_name = local_name

    def remove_service(self, zeroconf, type, name):
        print(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        IP = info.parsed_addresses()[0]
        current_time = datetime.datetime.now()
        if name == self.local_name:
            print(f"{current_time} -- Local Service: {name} IP: {IP} service info: {info}")
        else:
            print(f"{current_time} -- Other Service: {name} IP: {IP} service info: {info}")

    def update_service(self, zeroconf, type, name):
        pass
        # info = zeroconf.get_service_info(type, name)
        # print(f"发现服务：{name}, 服务信息：{info}")

def gw_simulator(args, log_path):
    """
    网关模拟器
    :param args: 前端信息
    :param log_path: 日志路径
    """
    global db_tool
    get_log(log_path).debug(args)
    # 环境检测
    get_log(log_path).info(f'Step 1：检测预注册环境信息...')
    env = args.测试环境
    if env in envs:
        mysql_info = {'host': f'{envs[env]["云端DB_Host_v"]}', 'port': f'{envs[env]["云端DB_Port_v"]}',
                      'user': f'{envs[env]["云端DB_用户名_v"]}',
                      'password': f'{envs[env]["云端DB_密码_v"]}', 'db_name': f'{envs[env]["云端DB_库名_v"]}',
                      'charset': 'utf8'}
    else:
        get_log(log_path).error(f'未找到{env}环境下的任何配置，请确认环境是否正确或让管理员添加对应数据！')
        sys.exit()
    time.sleep(2)
    # APP检测
    # 判断用户名密码是否正确
    get_log(log_path).info(f'Step 2：检测预绑定APP信息...')
    db_tool = MyPymysqlPool(mysql_info)
    username = f"{args.用户名}"
    password = hashlib.sha256(f'{args.密码}'.encode('utf-8')).hexdigest()
    user_pw_sql = f"select password from lbl_app_account where username = '{username}'"
    user_pw_sql_res = db_tool.getAll(user_pw_sql)
    if not user_pw_sql_res:
        get_log(log_path).error(f'    !!!!    APP用户名不存在，请更正')
        sys.exit()
    elif password != user_pw_sql_res[0]['password']:
        get_log(log_path).error(f'    !!!!    APP密码错误，请更正')
        sys.exit()
    home_info = getMyAllHomeInfo(args, log_path)
    groupId = None
    subGroupId = None
    for home in json.loads(home_info)['params']:
        if home['groupName'] == args.住家名称:
            groupId = home['groupId']
            for room in home['subObjs']:
                if room['subGroupName'] == args.房间:
                    subGroupId = room['subGroupId']
    if groupId is None or subGroupId is None:
        get_log(log_path).error(f'    !!!!    未找到住家 {args.住家名称} 或房间 {args.房间}')
        sys.exit()
    time.sleep(2)
    get_log(log_path).info("*" * gap_num)
    get_log(log_path).info(f'Step 1：开始注册虚拟网关...')
    device_secret_sql = f"select device_secret from iot_device where did = '{args.Did}'"
    device_secret_res = db_tool.getAll(device_secret_sql)
    soft_name = args.产品_软件模型_profileId.split(':')[0]
    soft_model = args.产品_软件模型_profileId.split(':')[1]
    if not device_secret_res:
        # 通过一型一密注册
        soft_model_secret_sql = f"select soft_model_secret from op_soft_model osm where soft_name = '{soft_name}' and soft_model = '{soft_model}'"
        res = db_tool.getAll(soft_model_secret_sql)
        password = hashlib.sha256(f'{res[0]["soft_model_secret"]}'.encode('utf-8')).hexdigest()
        # 创建MQTT客户端
        mqtt_client = MQTTClient(log_path, f'{envs[env]["云端MQTT_Host_v"]}', username=soft_model, password=password,
                                 client_id=args.Did)
        # 连接到MQTT代理
        mqtt_client.connect()
        # 订阅主题
        mqtt_client.subscribe(f"lliot/receiver/{args.Did}")
        # 发布消息
        payload = dmgr_reg(args)['rsp']
        mqtt_client.publish(f"lliot/receiver/{dev_manage_moduleID}", json.dumps(payload))
        get_log(log_path).info(f'    ----    注册{args.Did}中...')
        time.sleep(5)
        # 停止消息循环
        mqtt_client.stop_loop()
        # 断开连接
        mqtt_client.disconnect()
        device_secret_res = db_tool.getAll(device_secret_sql)
        if device_secret_res:
            get_log(log_path).info(f'        ----        虚拟网关did={args.Did}注册成功')
            time.sleep(2)
        else:
            get_log(log_path).error(f'        !!!!        虚拟网关did={args.Did}注册失败')
            sys.exit()
    else:
        get_log(log_path).info(f'    ----    虚拟网关did={args.Did}已在该测试环境注册')
        time.sleep(2)
    get_log(log_path).info(f'Step 2：开始执行虚拟网关MQTT登录并启动主题监听...')
    # 通过一机一密登录
    username = f"{soft_model}:{args.Did}"
    # 创建MQTT客户端
    mqtt_client = MQTTClient(log_path, f'{envs[env]["云端MQTT_Host_v"]}', username=username,
                             password=device_secret_res[0]['device_secret'],
                             client_id=args.Did, tool='direct_con_dev', args=args)
    # 连接到MQTT代理
    mqtt_client.connect()
    # 订阅主题
    mqtt_client.subscribe(f"lliot/receiver/{args.Did}")
    time.sleep(2)
    # 绑定设备
    get_log(log_path).info(f'Step 3：开始执行虚拟网关绑定APP...')
    dev_bind_sql = f"select count(*), group_id from newiot_device_bind_ext where did = '{args.Did}'"
    bind_res = db_tool.getAll(dev_bind_sql)
    time.sleep(5)
    if bind_res[0]['count(*)'] != 0:
        get_log(log_path).info(f'    ----    虚拟网关已被住家{bind_res[0]["group_id"]}绑定')
    else:
        res = bindDevice(args, log_path)
        waitTime = int(json.loads(res)['waitTime']) / 1000
        for i in range(0, int(waitTime)):
            get_log(log_path).info(f'    ----    等待倒计时{int(waitTime) - i}S...')
            bind_res = db_tool.getAll(dev_bind_sql)
            if bind_res[0]['count(*)'] == 1:
                get_log(log_path).info(f'    ----    虚拟网关绑定APP成功')
                break
            elif i == int(waitTime) - 1:
                get_log(log_path).error(f'    !!!!    虚拟网关绑定APP失败')
                sys.exit()
            time.sleep(1)
    time.sleep(2)
    # 绑定子设备
    get_log(log_path).info(f'Step 4：开始执行虚拟网关绑定虚拟子设备...')
    # 读取 Excel 文件
    excel_path = args.Path
    df = pd.read_excel(excel_path, sheet_name="subDev")
    directDid = args.Did
    topic = f"lliot/receiver/{dev_manage_moduleID}"
    req_data = []
    for index, row in df.iterrows():
        if row['是否执行'] == 'T':
            subDid = row['did']
            dev_type = row['产品名称']
            req_mes = json.loads(row["请求信息"])
            req_data += req_mes
            subDev_sql = f"select direct_did from iot_device where did = '{subDid}'"
            subDev_res = db_tool.getAll(subDev_sql)
            if not subDev_res:
                get_log(log_path).info(f'    ----    绑定子设备{dev_type}-{subDid}中')
                messages = [dmgr_subDeviceOnlineStatus(directDid, subDid, 500),
                            dmgr_reportAddDevice(directDid, subDid, dev_type, 501),
                            dmgr_reportPIIDS(directDid, subDid, 502)]
                for message in messages:
                    mqtt_client.publish(topic, message)
                    time.sleep(2)
                subDev_sql = f"select * from iot_device where did = '{subDid}' and direct_did = '{args.Did}'"
                subDev_res = db_tool.getAll(subDev_sql)
                if subDev_res:
                    get_log(log_path).info(f'       ----       虚拟子设备绑定成功')
                else:
                    get_log(log_path).error(f'       !!!!       虚拟子设备绑定失败')
            else:
                get_log(log_path).info(f'    ----    虚拟子设备已被设备{subDev_res[0]["direct_did"]}绑定')
        time.sleep(5)
    # 释放资源
    get_log(log_path).info(f'Step 5：停止MQTT，执行局域网操作...')
    # 停止消息循环
    mqtt_client.stop_loop()
    # 断开连接
    mqtt_client.disconnect()
    # 关闭数据库
    db_tool.dispose()
    time.sleep(1)
    nums = args.测试次数
    get_log(log_path).info(f'       ----       登录主网关')
    ip = args.主网关IP
    client = TCPClient(log_path, ip, 49853)
    client.connect()
    src_did = args.Did
    dst_did = args.主网关Did
    # bind
    data = gw_bind(src_did, dst_did, str(groupId))
    client.send_ssl_data(bytes.fromhex(data))
    client.receive_ssl_data()
    # random
    data = gw_random(src_did, dst_did)
    client.send_ssl_data(bytes.fromhex(data))
    data_received = client.receive_ssl_data()
    # 提取random
    random_str = ' '.join(data_received)
    random_match = re.search('"random":"([^"]+)"', random_str)
    if random_match:
        random = random_match.group(1)
        if random != "":
            # login
            data, password = gw_login(src_did, dst_did, str(groupId), random)
            client.send_ssl_data(bytes.fromhex(data))
            client.receive_ssl_data(password=password)
            time.sleep(5)
            # heartbeat
            heartbeat_thread = HeartbeatThread(client, password)
            heartbeat_thread.daemon = True  # 设置为守护线程，使其在主线程结束时自动关闭
            heartbeat_thread.start()
        else:
            raise CustomError(f'       !!!!       局域网获取随机码失败')
    else:
        raise CustomError(f'       !!!!       局域网登录失败')
    for num in range(0, int(nums)):
        get_log(log_path).info(f'       ----       进行第{num + 1}次数据请求')
        data_num = 0
        for data in req_data:
            data_num += 1
            get_log(log_path).info(f'          ----          发送第{data_num}条数据...')
            data = gw_transparent(data, password=password)
            client.clear_ssl_buff()
            client.send_ssl_data(bytes.fromhex(data))
            data_received = client.receive_ssl_data(password=password)
            get_log(log_path).debug(f'发送SSL数据{data}\n接收到回复{data_received}')
            time.sleep(args.间隔时长)
        time.sleep(args.间隔时长)
    get_log(log_path).info(f'Step 6：停止TCP连接，结束测试...')
    try:
        client.close()
    except Exception:
        pass
