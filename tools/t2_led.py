# -*- coding: utf-8 -*-
import sys
from datetime import datetime
import hashlib
import json
import time

from commons.variables import *
from handlers.app_handler import get_terminal_info, app_request
from handlers.log_handler import get_log
from handlers.mqtt_handler import MQTTClient
from handlers.mysql_tool import MyPymysqlPool


# 测试环境信息
def t2_led(args, log_path):
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
        if args.场景 == "分布式-群组":
            sql_devices = f"select did, logic_name, siid, service_type, is_display from iot_dc_logic_device where direct_did = '{args.Did}' and mactch_category = '1'"
        elif args.场景 == "集中式-联动":
            sql_devices = f"select did, logic_name from iot_dc_logic_device where mactch_category = '1' and did = '{args.联动条件did}' and siid = '2'"
            devices_condition = db_tool.getAll(sql_devices)
            if not devices_condition:
                get_log(log_path).error(f'    !!!!    网关未下挂联动条件设备 {args.联动条件did}')
                sys.exit()
            sql_devices = f"select did, logic_name, siid, service_type, is_display from (select * from iot_dc_logic_device where direct_did = '{args.Did}' and mactch_category = '1') as subset where not (did = '{args.联动条件did}' and siid = '2')"
        elif args.场景 == "单控":
            if args.单控did != 'All':
                sql_devices = f"select did, logic_name, siid from iot_dc_logic_device where direct_did = '{args.Did}' and did = '{args.单控did}' and siid = '2'"
            else:
                sql_devices = f"select did, logic_name, siid from iot_dc_logic_device where direct_did = '{args.Did}' and mactch_category = '1' and siid = '2'"
        else:
            return
        devices_did = db_tool.getAll(sql_devices)
        if not devices_did or len(devices_did) == 0:
            get_log(log_path).error(f'    !!!!    网关未下挂任何预测试设备')
            sys.exit()
        else:
            get_log(log_path).debug(f'{devices_did}')
            get_log(log_path).info(f'    ----    共计下挂 {len(devices_did)} 个预测试设备（逻辑设备）')
    except Exception as e:
        get_log(log_path).error(f"APP信息处理发生错误: {e}\n1、请确保所选环境与APP一致\n2、确保网关did填写正确")
        sys.exit()
    get_log(log_path).info("*" * gap_num)
    # 环境初始化
    get_log(log_path).info(f'测试环境初始化...')
    terminal_info = get_terminal_info(envs[evn]["云端环境_v"], mysql_info, args.用户名, args.密码, log_path)
    accessToken = json.loads(terminal_info)['params']['accessToken']
    # 注册监听用户
    time.sleep(2)
    get_log(log_path).info(f'    ----    启用监听mqtt客户端')
    did = "12300001000000000666"
    username = "HA-CE-R31-001"
    password = hashlib.sha256('jhfeq6vsxonjjlfa'.encode('utf-8')).hexdigest()
    mqtt_client = MQTTClient(log_path, f'{envs[evn]["云端MQTT_Host_v"]}', username=username,
                             password=password, client_id=did, tool="t2_led", args=args)
    sql_did = f"select device_secret from iot_device where did = '{did}'"
    res = db_tool.getAll(sql_did)
    if not res:
        try:
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
            mqtt_client.publish(f"lliot/receiver/{dev_manage_moduleID}", str(payload))
            get_log(log_path).info(f'        ----        注册mqtt监听用户中...')
            time.sleep(3)
            # 启动消息循环
            mqtt_client.start_loop()
            # 停止消息循环
            mqtt_client.stop_loop()
        except Exception as e:
            get_log(log_path).error(f'        !!!!        注册mqtt监听用户失败：{e}')
    else:
        get_log(log_path).info(f'        ----        mqtt监听用户已存在，无需注册...')
    time.sleep(2)
    get_log(log_path).info(f'        ----        订阅所有相关主题...')
    # 连接到MQTT代理
    mqtt_client.connect()
    # 订阅所有设备功能反馈主题
    dev_list = []
    for device in devices_did:
        topic = f"lliot/fiids_report/{device['did']}/{device['siid']}"
        dev_list.append(f"{device['did']}/{device['siid']}")
        mqtt_client.subscribe(topic)
    # 订阅网关接收主题
    topic = f"lliot/receiver/{args.Did}"
    mqtt_client.subscribe(topic)
    # 分布式-群组
    if args.场景 == '分布式-群组':
        get_log(log_path).info(f'    ----    创建测试群组')
        url = f"{envs[args.测试环境]['云端环境_v']}/rest/app/community/smartHome/classify/addOrModify"
        deviceList = []
        for device in devices_did:
            devices = {'did': device['did'], 'directDid': args.Did, 'siid': device['siid'], 'logicName': device['logic_name'],
                       'serviceType': device['service_type'], 'isDisplay': device['is_display']}
            deviceList.append(devices)
        data = {
            "seq": 999,
            "version": "v0.1",
            "params": {
                "groupId": rf"{app['homeID']}",
                "icon": f"http://{envs[evn]['云端MQTT_Host_v']}:9001/home/data/nas/3/record/111/202207/14/20220714141800423194.png",
                "classifyType": 5,
                "classifyName": "灯光群组",
                "subGroupId": rf"{app[f'{room}id']}",
                "deviceList": deviceList
            }
        }
        res = app_request(accessToken, url, data, log_path)
        if not res:
            get_log(log_path).error(f'        !!!!        群组创建失败')
            sys.exit()
        time.sleep(30)
        get_log(log_path).info("*" * gap_num)
        get_log(log_path).info(f'开始执行测试...')
        classifyId = json.loads(res)['params']['classifyId']
        nums = args.测试轮询次数
        url = f"{envs[evn]['云端环境_v']}/rest/app/community/smartHome/classify/control"
        open_data = {
            "seq": 999,
            "version": "v0.1",
            "params": {
                "groupId": rf"{app['homeID']}",
                "classifyId": f"{classifyId}",
                "fiids": [
                    {
                        "value": "{\"onOff\":1}",
                        "fiid": 49408
                    }
                ]
            }
        }
        down_data = {
            "seq": 999,
            "version": "v0.1",
            "params": {
                "groupId": rf"{app['homeID']}",
                "classifyId": f"{classifyId}",
                "fiids": [
                    {
                        "value": "{\"onOff\":0}",
                        "fiid": 49408
                    }
                ]
            }
        }
        # 执行循环测试
        for num in range(0, nums):
            report_list = []
            if os.path.exists(f'{os.path.dirname(log_path)}\\fiids_report.txt'):
                os.remove(f'{os.path.dirname(log_path)}\\fiids_report.txt')
            get_log(log_path).info(f'第 {num + 1} 次控制群组开...')
            begin_time = datetime.now()
            res = app_request(accessToken, url, open_data, log_path)
            get_log(log_path).debug(f"{res}")
            time.sleep(args.测试间隔时长)
            try:
                with open(f'{os.path.dirname(log_path)}\\gw_control.txt', 'r', encoding='utf-8') as f:
                    content = f.read().split('--')[0].strip()
                    control_time = datetime.strptime(content, '%Y-%m-%d %H:%M:%S.%f')
                with open(f'{os.path.dirname(log_path)}\\fiids_report.txt', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        report_list.append(line.split('--')[1].strip().split('/', maxsplit=2)[2])
                    last_line = lines[-1]
                    content = last_line.split('--')[0].strip()
                    end_time = datetime.strptime(content, '%Y-%m-%d %H:%M:%S.%f')
                unique_list_open = [d for d in dev_list if d not in list(set(report_list))]
                if not unique_list_open:
                    get_log(log_path).info(f'超时时长{args.测试间隔时长}内接收到所有测试设备的开状态上报主题')
                else:
                    get_log(log_path).info(
                        f'超时时长{args.测试间隔时长}内未接收到{unique_list_open}测试设备的开状态上报主题--失败率{len(unique_list_open) / len(dev_list) * 100}%')
                get_log(log_path).debug(
                    f'app接口下发开操作时间为：{begin_time}\n网关接收到开操作主题时间：{control_time}\n最后一台子设备上报开状态时间：{end_time}')
                get_log(log_path).info(
                    f'app下发 --> 网关接收到开操作主题用时：{"{:.3f}".format((control_time - begin_time).total_seconds())} S')
                get_log(log_path).info(
                    f'网关接收到开操作主题 --> 最后一台子设备上报开状态用时：{"{:.3f}".format((end_time - control_time).total_seconds())} S')
            except FileNotFoundError as e:
                get_log(log_path).error(f'发生如下错误：{e}')
                get_log(log_path).error(f'    !!!!    mqtt监听客户端未接收到任何测试设备上报报文')
            except Exception as e:
                get_log(log_path).error(f'发生如下错误：{e}')
            # 关操作
            report_list = []
            if os.path.exists(f'{os.path.dirname(log_path)}\\fiids_report.txt'):
                os.remove(f'{os.path.dirname(log_path)}\\fiids_report.txt')
            get_log(log_path).info(f'第 {num + 1} 次控制群组关...')
            begin_time = datetime.now()
            res = app_request(accessToken, url, down_data, log_path)
            get_log(log_path).debug(f"{res}")
            time.sleep(args.测试间隔时长)
            try:
                with open(f'{os.path.dirname(log_path)}\\gw_control.txt', 'r', encoding='utf-8') as f:
                    content = f.read().split('--')[0].strip()
                    control_time = datetime.strptime(content, '%Y-%m-%d %H:%M:%S.%f')
                with open(f'{os.path.dirname(log_path)}\\fiids_report.txt', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        report_list.append(line.split('--')[1].strip().split('/', maxsplit=2)[2])
                    last_line = lines[-1]
                    content = last_line.split('--')[0].strip()
                    end_time = datetime.strptime(content, '%Y-%m-%d %H:%M:%S.%f')
                unique_list_down = [d for d in dev_list if d not in list(set(report_list))]
                if not unique_list_down:
                    get_log(log_path).info(f'超时时长{args.测试间隔时长}内接收到所有测试设备的关状态上报主题')
                else:
                    get_log(log_path).info(
                        f'超时时长{args.测试间隔时长}内未接收到{unique_list_down}测试设备的关状态上报主题--失败率{len(unique_list_down) / len(dev_list) * 100}%')
                get_log(log_path).debug(
                    f'app接口下发关操作时间为：{begin_time}\n网关接收到关操作主题时间：{control_time}\n最后一台子设备上报关状态时间：{end_time}')
                get_log(log_path).info(
                    f'app下发 --> 网关接收到关操作主题用时：{"{:.3f}".format((control_time - begin_time).total_seconds())} S')
                get_log(log_path).info(
                    f'网关接收到关操作主题 --> 最后一台子设备上报关状态用时：{"{:.3f}".format((end_time - control_time).total_seconds())} S')
            except FileNotFoundError as e:
                get_log(log_path).error(f'发生如下错误：{e}')
                get_log(log_path).error(f'    !!!!    mqtt监听客户端未接收到任何测试设备上报报文')
            except Exception as e:
                get_log(log_path).error(f'发生如下错误：{e}')
        get_log(log_path).info("*" * gap_num)
    elif args.场景 == '集中式-联动':
        get_log(log_path).info(f'    ----    创建联动场景')
        url = f"{envs[args.测试环境]['云端环境_v']}/rest/app/community/linkage/addOrModify"
        ctrlList = []
        conditionList = []
        ctrlId = 0
        sort = 1
        isDefaultValue = "false"
        for device in devices_did:
            devices = {
                "extInfo": r'{\"type\":1,\"value\":\"开关:开启\"}',
                "isDefaultValue": isDefaultValue,
                "ctrlType": 0,
                "directDid": f"{args.Did}",
                "defaultName": f"{device['logic_name']}",
                "siid": f"{device['siid']}",
                "roomName": f"{room}",
                "ctrlId": ctrlId,
                "floorId": "(null)",
                "isUpdate": 1,
                "did": f"{device['did']}",
                "serviceType": f"{device['service_type']}",
                "roomId": f"{roomID}",
                "fiids": [
                    {
                        "value": {
                            "onOff": 1
                        },
                        "fiid": 49408
                    }
                ],
                "name": f"{device['logic_name']}",
                "sort": sort
            }
            ctrlList.append(devices)
            ctrlId += 1
            sort += 1
        for device in devices_condition:
            condition = {
                "fiid": 49408,
                "name": f"{device['logic_name']}",
                "did": f"{device['did']}",
                "compareConditionList": [
                    {
                        "compareValue": "1",
                        "fiidCompareField": "onOff",
                        "compareValueType": "1",
                        "compareType": "2"
                    }
                ],
                "roomName": f"{room}",
                "isUpdate": 1,
                "directDid": f"{args.Did}",
                "extInfo": r'{\"type\":1,\"value\":\"开关控制:开启\"}',
                "siid": 2,
                "fiidType": 2
            }
            conditionList.append(condition)
        open_data = {
            "seq": 666,
            "version": "v0.1",
            "params": {
                "linkName": "Open",
                "enabled": 1,
                "subGroupId": f"{roomID}",
                "linkAppType": 0,
                "conditionRelation": 1,
                "effectTime": "00:00",
                "expireTime": "00:00",
                "timerType": 1,
                "groupId": rf"{homeId}",
                "conditionList": conditionList,
                "ctrlList": ctrlList
            }
        }
        res = app_request(accessToken, url, open_data, log_path)
        if not res:
            get_log(log_path).error(f'        !!!!        开联动场景创建失败')
            sys.exit()
        else:
            get_log(log_path).error(f'        ----        创建开联动场景中，请耐心等待...')
        time.sleep(30)
        ctrlList = []
        conditionList = []
        ctrlId = 0
        sort = 1
        isDefaultValue = False
        for device in devices_did:
            devices = {
                "extInfo": r'{\"type\":1,\"value\":\"开关:关闭\"}',
                "isDefaultValue": isDefaultValue,
                "ctrlType": 0,
                "directDid": f"{args.Did}",
                "defaultName": f"{device['logic_name']}",
                "siid": f"{device['siid']}",
                "roomName": f"{room}",
                "ctrlId": ctrlId,
                "floorId": "(null)",
                "isUpdate": 1,
                "did": f"{device['did']}",
                "serviceType": f"{device['service_type']}",
                "roomId": f"{roomID}",
                "fiids": [
                    {
                        "value": {
                            "onOff": 0
                        },
                        "fiid": 49408
                    }
                ],
                "name": f"{device['logic_name']}",
                "sort": sort
            }
            ctrlList.append(devices)
            ctrlId += 1
            sort += 1
        for device in devices_condition:
            condition = {
                "fiid": 49408,
                "name": f"{device['logic_name']}",
                "did": f"{device['did']}",
                "compareConditionList": [
                    {
                        "compareValue": "0",
                        "fiidCompareField": "onOff",
                        "compareValueType": "1",
                        "compareType": "2"
                    }
                ],
                "roomName": f"{room}",
                "isUpdate": 1,
                "directDid": f"{args.Did}",
                "extInfo": r'{\"type\":1,\"value\":\"开关控制:关闭\"}',
                "siid": 2,
                "fiidType": 2
            }
            conditionList.append(condition)
        down_data = {
            "seq": 666,
            "version": "v0.1",
            "params": {
                "linkName": "Down",
                "enabled": 1,
                "subGroupId": f"{roomID}",
                "linkAppType": 0,
                "conditionRelation": 1,
                "effectTime": "00:00",
                "expireTime": "00:00",
                "timerType": 1,
                "groupId": rf"{homeId}",
                "conditionList": conditionList,
                "ctrlList": ctrlList
            }
        }
        res = app_request(accessToken, url, down_data, log_path)
        if not res:
            get_log(log_path).error(f'        !!!!        关联动场景创建失败')
            sys.exit()
        else:
            get_log(log_path).error(f'        ----        创建关联动场景中，请耐心等待...')
        time.sleep(30)
        get_log(log_path).info("*" * gap_num)
        get_log(log_path).info(f'开始执行测试...')
        nums = args.测试轮询次数
        url = f"{envs[evn]['云端环境_v']}/rest/app/community/encryptV1CtrlFIIDS"
        open_data = {
            "seq": 888,
            "version": "v0.1",
            "params": {
                "did": f"{devices_condition[0]['did']}",
                "directDid": f"{args.Did}",
                "siid": 2,
                "fiids": [
                    {
                        "value": {
                            "onOff": 1
                        },
                        "fiid": 49408
                    }
                ]
            }
        }
        down_data = {
            "seq": 888,
            "version": "v0.1",
            "params": {
                "did": f"{devices_condition[0]['did']}",
                "directDid": f"{args.Did}",
                "siid": 2,
                "fiids": [
                    {
                        "value": {
                            "onOff": 0
                        },
                        "fiid": 49408
                    }
                ]
            }
        }
        # 执行循环测试
        for num in range(0, nums):
            report_list = []
            if os.path.exists(f'{os.path.dirname(log_path)}\\fiids_report.txt'):
                os.remove(f'{os.path.dirname(log_path)}\\fiids_report.txt')
            get_log(log_path).info(f'第 {num + 1} 次控制联动开...')
            begin_time = datetime.now()
            res = app_request(accessToken, url, open_data, log_path)
            get_log(log_path).debug(f"{res}")
            time.sleep(args.测试间隔时长)
            try:
                with open(f'{os.path.dirname(log_path)}\\gw_control.txt', 'r', encoding='utf-8') as f:
                    content = f.read().split('--')[0].strip()
                    control_time = datetime.strptime(content, '%Y-%m-%d %H:%M:%S.%f')
                with open(f'{os.path.dirname(log_path)}\\fiids_report.txt', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        report_list.append(line.split('--')[1].strip().split('/', maxsplit=2)[2])
                    last_line = lines[-1]
                    content = last_line.split('--')[0].strip()
                    end_time = datetime.strptime(content, '%Y-%m-%d %H:%M:%S.%f')
                unique_list_open = [d for d in dev_list if d not in list(set(report_list))]
                if not unique_list_open:
                    get_log(log_path).info(f'超时时长{args.测试间隔时长}内接收到所有测试设备的开状态上报主题')
                else:
                    get_log(log_path).info(
                        f'超时时长{args.测试间隔时长}内未接收到{unique_list_open}测试设备的开状态上报主题--失败率{len(unique_list_open) / len(dev_list) * 100}%')
                get_log(log_path).debug(
                    f'app接口下发开操作时间为：{begin_time}\n网关接收到开操作主题时间：{control_time}\n最后一台子设备上报开状态时间：{end_time}')
                get_log(log_path).info(
                    f'app下发 --> 网关接收到开操作主题用时：{"{:.3f}".format((control_time - begin_time).total_seconds())} S')
                get_log(log_path).info(
                    f'网关接收到开操作主题 --> 最后一台子设备上报开状态用时：{"{:.3f}".format((end_time - control_time).total_seconds())} S')
            except FileNotFoundError as e:
                get_log(log_path).error(f'发生如下错误：{e}')
                get_log(log_path).error(f'    !!!!    mqtt监听客户端未接收到任何测试设备上报报文')
            except Exception as e:
                get_log(log_path).error(f'发生如下错误：{e}')
            # 关操作
            report_list = []
            if os.path.exists(f'{os.path.dirname(log_path)}\\fiids_report.txt'):
                os.remove(f'{os.path.dirname(log_path)}\\fiids_report.txt')
            get_log(log_path).info(f'第 {num + 1} 次控制联动关...')
            begin_time = datetime.now()
            res = app_request(accessToken, url, down_data, log_path)
            get_log(log_path).debug(f"{res}")
            time.sleep(args.测试间隔时长)
            try:
                with open(f'{os.path.dirname(log_path)}\\gw_control.txt', 'r', encoding='utf-8') as f:
                    content = f.read().split('--')[0].strip()
                    control_time = datetime.strptime(content, '%Y-%m-%d %H:%M:%S.%f')
                with open(f'{os.path.dirname(log_path)}\\fiids_report.txt', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        report_list.append(line.split('--')[1].strip().split('/', maxsplit=2)[2])
                    last_line = lines[-1]
                    content = last_line.split('--')[0].strip()
                    end_time = datetime.strptime(content, '%Y-%m-%d %H:%M:%S.%f')
                unique_list_down = [d for d in dev_list if d not in list(set(report_list))]
                if not unique_list_down:
                    get_log(log_path).info(f'超时时长{args.测试间隔时长}内接收到所有测试设备的关状态上报主题')
                else:
                    get_log(log_path).info(
                        f'超时时长{args.测试间隔时长}内未接收到{unique_list_down}测试设备的关状态上报主题--失败率{len(unique_list_down) / len(dev_list) * 100}%')
                get_log(log_path).debug(
                    f'app接口下发关操作时间为：{begin_time}\n网关接收到关操作主题时间：{control_time}\n最后一台子设备上报关状态时间：{end_time}')
                get_log(log_path).info(
                    f'app下发 --> 网关接收到关操作主题用时：{"{:.3f}".format((control_time - begin_time).total_seconds())} S')
                get_log(log_path).info(
                    f'网关接收到关操作主题 --> 最后一台子设备上报关状态用时：{"{:.3f}".format((end_time - control_time).total_seconds())} S')
            except FileNotFoundError as e:
                get_log(log_path).error(f'发生如下错误：{e}')
                get_log(log_path).error(f'    !!!!    mqtt监听客户端未接收到任何测试设备上报报文')
            except Exception as e:
                get_log(log_path).error(f'发生如下错误：{e}')
        get_log(log_path).info("*" * gap_num)
    elif args.场景 == '单控':
        get_log(log_path).info(f'开始执行测试...')
        nums = args.测试轮询次数
        url = f"{envs[evn]['云端环境_v']}/rest/app/community/encryptV1CtrlFIIDS"
        # 执行循环测试
        for num in range(0, nums):
            for device in devices_did:
                open_data = {
                    "seq": 999,
                    "version": "v0.1",
                    "params": {
                        "did": rf"{device['did']}",
                        "directDid": f"{args.Did}",
                        "siid": 2,
                        "fiids": [
                            {
                                "value": {
                                    "onOff": 1
                                },
                                "fiid": 49408
                            }
                        ]
                    }
                }
                report_list = []
                if os.path.exists(f'{os.path.dirname(log_path)}\\fiids_report.txt'):
                    os.remove(f'{os.path.dirname(log_path)}\\fiids_report.txt')
                if os.path.exists(f'{os.path.dirname(log_path)}\\gw_control.txt'):
                    os.remove(f'{os.path.dirname(log_path)}\\gw_control.txt')
                time.sleep(3)
                get_log(log_path).info(f'第 {num + 1} 次单控设备 {device["did"]} 开...')
                begin_time = datetime.now()
                res = app_request(accessToken, url, open_data, log_path)
                get_log(log_path).debug(f"{res}")
                time.sleep(args.测试间隔时长)
                try:
                    with open(f'{os.path.dirname(log_path)}\\gw_control.txt', 'r', encoding='utf-8') as f:
                        content = f.read().split('--')[0].strip()
                        control_time = datetime.strptime(content, '%Y-%m-%d %H:%M:%S.%f')
                    with open(f'{os.path.dirname(log_path)}\\fiids_report.txt', 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines:
                            report_list.append(line.split('--')[1].strip().split('/', maxsplit=2)[2])
                        last_line = lines[-1]
                        content = last_line.split('--')[0].strip()
                        end_time = datetime.strptime(content, '%Y-%m-%d %H:%M:%S.%f')
                    dev_list = [f"{device['did']}/{device['siid']}"]
                    unique_list_open = [d for d in dev_list if d not in list(set(report_list))]
                    if unique_list_open:
                        get_log(log_path).info(f"超时时长{args.测试间隔时长}内未接收到{unique_list_open}测试设备的开状态上报主题")
                    else:
                        get_log(log_path).debug(
                            f'app接口下发开操作时间为：{begin_time}\n网关接收到开操作主题时间：{control_time}\n子设备上报开状态时间：{end_time}')
                        get_log(log_path).info(
                            f'app下发 --> 网关接收到开操作主题用时：{"{:.3f}".format((control_time - begin_time).total_seconds())} S')
                        get_log(log_path).info(
                            f'网关接收到开操作主题 --> 子设备上报开状态用时：{"{:.3f}".format((end_time - control_time).total_seconds())} S')
                except FileNotFoundError as e:
                    get_log(log_path).error(f'发生如下错误：{e}')
                    get_log(log_path).error(f'    !!!!    mqtt监听客户端未接收到网关操作主题或测试设备上报报文')
                except Exception as e:
                    get_log(log_path).error(f'发生如下错误：{e}')
                # 关操作
                down_data = {
                    "seq": 999,
                    "version": "v0.1",
                    "params": {
                        "did": rf"{device['did']}",
                        "directDid": f"{args.Did}",
                        "siid": 2,
                        "fiids": [
                            {
                                "value": {
                                    "onOff": 0
                                },
                                "fiid": 49408
                            }
                        ]
                    }
                }
                report_list = []
                if os.path.exists(f'{os.path.dirname(log_path)}\\fiids_report.txt'):
                    os.remove(f'{os.path.dirname(log_path)}\\fiids_report.txt')
                if os.path.exists(f'{os.path.dirname(log_path)}\\gw_control.txt'):
                    os.remove(f'{os.path.dirname(log_path)}\\gw_control.txt')
                time.sleep(3)
                get_log(log_path).info(f'第 {num + 1} 次单控设备 {device["did"]} 关...')
                begin_time = datetime.now()
                res = app_request(accessToken, url, down_data, log_path)
                get_log(log_path).debug(f"{res}")
                time.sleep(args.测试间隔时长)
                try:
                    with open(f'{os.path.dirname(log_path)}\\gw_control.txt', 'r', encoding='utf-8') as f:
                        content = f.read().split('--')[0].strip()
                        control_time = datetime.strptime(content, '%Y-%m-%d %H:%M:%S.%f')
                    with open(f'{os.path.dirname(log_path)}\\fiids_report.txt', 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines:
                            report_list.append(line.split('--')[1].strip().split('/', maxsplit=2)[2])
                        last_line = lines[-1]
                        content = last_line.split('--')[0].strip()
                        end_time = datetime.strptime(content, '%Y-%m-%d %H:%M:%S.%f')
                    unique_list_open = [d for d in dev_list if d not in list(set(report_list))]
                    if unique_list_open:
                        get_log(log_path).info(f"超时时长{args.测试间隔时长}内未接收到{unique_list_open}测试设备的关状态上报主题")
                    else:
                        get_log(log_path).debug(
                            f'app接口下发关操作时间为：{begin_time}\n网关接收到关操作主题时间：{control_time}\n子设备上报关状态时间：{end_time}')
                        get_log(log_path).info(
                            f'app下发 --> 网关接收到关操作主题用时：{"{:.3f}".format((control_time - begin_time).total_seconds())} S')
                        get_log(log_path).info(
                            f'网关接收到关操作主题 --> 子设备上报关状态用时：{"{:.3f}".format((end_time - control_time).total_seconds())} S')
                except FileNotFoundError as e:
                    get_log(log_path).error(f'发生如下错误：{e}')
                    get_log(log_path).error(f'    !!!!    mqtt监听客户端未接收到任何测试设备上报报文')
                except Exception as e:
                    get_log(log_path).error(f'发生如下错误：{e}')
            get_log(log_path).info("*" * gap_num)
    # 关闭数据库
    db_tool.dispose(1)
    # 断开mqtt连接
    mqtt_client.disconnect()
