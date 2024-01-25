# -*- coding: utf-8 -*-
import hashlib
import sys
import time
from commons.variables import *
from handlers.log_handler import get_log
from handlers.mqtt_handler import MQTTClient
from handlers.mysql_tool import MyPymysqlPool
from lib.app.client_app import getMyAllHomeInfo, json, bindDevice
from lib.mqtt.modules import dmgr_reg


def direct_con_dev(args, log_path):
    global db_tool
    mysql_info = {}
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
    get_log(log_path).info(f'Step 1：开始执行直连桩注册...')
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
        mqtt_client.publish(f"lliot/receiver/{dev_manage_moduleID}", str(payload))
        get_log(log_path).info(f'    ----    注册{args.Did}中...')
        time.sleep(3)
        # 停止消息循环
        mqtt_client.stop_loop()
        # 断开连接
        mqtt_client.disconnect()
        device_secret_res = db_tool.getAll(device_secret_sql)
        if device_secret_res:
            get_log(log_path).info(f'        ----        直连桩did={args.Did}注册成功')
            time.sleep(2)
        else:
            get_log(log_path).error(f'        !!!!        直连桩did={args.Did}注册失败')
            sys.exit()
    else:
        get_log(log_path).info(f'    ----    直连桩did={args.Did}已在该测试环境注册')
        time.sleep(2)
    get_log(log_path).info(f'Step 2：开始执行直连桩登录并启动主题监听...')
    # 通过一机一密登录
    username = f"{soft_name}:{args.Did}"
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
    get_log(log_path).info(f'Step 3：开始执行直连桩绑定...')
    res = bindDevice(args, log_path)
    time.sleep(5)
    if res:
        get_log(log_path).info(f'    ----    直连桩绑定APP成功')
    else:
        get_log(log_path).error(f'    !!!!    直连桩绑定APP失败')
        sys.exit()
    get_log(log_path).info(f'Step 4：停止主题监听，释放资源...')
    # 停止消息循环
    mqtt_client.stop_loop()
    # 断开连接
    mqtt_client.disconnect()
    # 关闭数据库
    db_tool.dispose()
    time.sleep(1)
