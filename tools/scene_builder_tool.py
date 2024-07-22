# -*- coding: utf-8 -*-
import hashlib
import json
import re
import sys
import time

from commons.variables import *
from handlers.app_handler import app_request, get_terminal_info
from handlers.log_handler import get_log
from handlers.mysql_tool import MyPymysqlPool


def scene_builder_tool(args, log_path):
    """
    场景生成器
    :param args:
    :param log_path:
    """
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
        sql_devices = f"select did, logic_name, siid, service_type, is_display from iot_dc_logic_device where direct_did = '{args.Did}' and mactch_category = '1' and did != '{args.Did}'"
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
    get_log(log_path).info(f'开始创建/删除{args.预生成场景}...')
    terminal_info = get_terminal_info(envs[evn]["云端环境_v"], mysql_info, args.用户名, args.密码, log_path)
    accessToken = json.loads(terminal_info)['params']['accessToken']
    nums = args.生成总数
    interval = args.生成间隔时长
    if int(nums) == 0:  # 删除场景
        if args.预生成场景 == "群组":
            get_log(log_path).info(f'    ----    查询群组列表并获取群组ID')
            # 查询逻辑设备列表获取群组did
            url = f"{envs[args.测试环境]['云端环境_v']}/rest/app/community/smartHome/v2/getGroupLogicDevices"
            data = {
                "seq": 666,
                "version": "V1.1",
                "params": {
                    "groupId": rf"{app['homeID']}",
                    "deviceLabel": [1, 2],
                    "iconVersion": "2.0",
                    "type": 0
                }
            }
            res = app_request(accessToken, url, data, log_path)
            if not res:
                get_log(log_path).error(f'        !!!!        获取逻辑设备列表失败')
                sys.exit()
            else:
                classifydids = []
                res = json.loads(res)
                classifyList = res.get('params', {}).get('classifyList', [])
                regex = re.compile("群组")
                for item in classifyList:
                    if regex.search(item.get('classifyName', '')):
                        classifydids.append(item.get('did'))
                if classifydids:
                    url = f"{envs[args.测试环境]['云端环境_v']}/rest/app/community/smartHome/classify/del"
                    for classifyId in classifydids:
                        data = {
                            "seq": 666,
                            "version": "V1.1",
                            "params": {
                                "groupId": rf"{app['homeID']}",
                                "classifyId": f"{classifyId}"
                            }
                        }
                        res = app_request(accessToken, url, data, log_path)
                        if not res:
                            get_log(log_path).error(f'        !!!!        删除群组{classifyId}失败')
                        else:
                            get_log(log_path).info(f'    ----    删除群组-{classifyId}成功')
                        time.sleep(1)
                else:
                    get_log(log_path).error(f'        !!!!        该环境下不存在群组')
                    sys.exit()
        else:
            get_log(log_path).info(f'        ----        APP支持场景批量删除，请您移动到APP操作')
            sys.exit()
    else:  # 创建场景
        for num in range(0, int(nums)):
            get_log(log_path).info(f'    ----    创建第 {num + 1} 个{args.预生成场景}')
            if args.预生成场景 == "群组":
                url = f"{envs[args.测试环境]['云端环境_v']}/rest/app/community/smartHome/classify/addOrModify"
                deviceList = []
                for device in devices_did:
                    devices = {'did': device['did'], 'directDid': args.Did, 'siid': device['siid'],
                               'logicName': device['logic_name'],
                               'serviceType': device['service_type'], 'isDisplay': device['is_display']}
                    deviceList.append(devices)
                data = {
                    "seq": 999,
                    "version": "V1.1",
                    "params": {
                        "groupId": rf"{app['homeID']}",
                        "icon": f"http://{envs[evn]['云端MQTT_Host_v']}:9001/home/data/nas/3/record/111/202207/14/20220714141800423194.png",
                        "classifyType": 5,
                        "classifyName": f"群组{num + 1}",
                        "subGroupId": rf"{app[f'{room}id']}",
                        "deviceList": deviceList
                    }
                }
                res = app_request(accessToken, url, data, log_path)
                if not res:
                    get_log(log_path).error(f'        !!!!        创建群组{num + 1}失败')
            elif args.预生成场景 == "手动场景":
                url = f"{envs[args.测试环境]['云端环境_v']}/rest/app/community/scene/addOrModify"
                ctrlList = []
                ctrlId = 0
                sort = 1
                for device in devices_did:
                    devices = {
                        "extInfo": "{\"type\":1,\"value\":\"开关控制:开启\"}",
                        "ctrlType": 0,
                        "directDid": f"{args.Did}",
                        "defaultName": f"{device['logic_name']}",
                        "siid": f"{device['siid']}",
                        "roomName": f"{room}",
                        "ctrlId": ctrlId,
                        "roomId": f"{roomID}",
                        "isUpdate": 1,
                        "did": f"{device['did']}",
                        "fiids": [
                            {
                                "value": {
                                    "onOff": 1
                                },
                                "fiid": 49408
                            }
                        ],
                        "sort": sort,
                        "name": f"{device['logic_name']}"
                    }
                    ctrlList.append(devices)
                    ctrlId += 1
                    sort += 1
                data = {
                    "seq": 666,
                    "version": "v0.1",
                    "params": {
                        "uniqueIdentify": "1",
                        "ctrlList": ctrlList,
                        "subGroupId": f"{roomID}",
                        "sceneName": f"手动场景{num + 1}",
                        "groupId": rf"{homeId}",
                        "baseIconId": "46",
                        "icon": f"https://{envs[evn]['云端MQTT_Host_v']}/authpic?p=http://{envs[evn]['云端MQTT_Host_v']}:9001/home/data/nas/3/record/111/202403/13/20240313095149640524.png"
                    }
                }
                res = app_request(accessToken, url, data, log_path)
                if not res:
                    get_log(log_path).error(f'        !!!!        创建手动场景{num + 1}失败')
            else:
                get_log(log_path).error(f'    !!!!    暂不支持此场景的创建，敬请期待')
                sys.exit()
            time.sleep(interval)
