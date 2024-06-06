# -*- coding: utf-8 -*-
import hashlib
import time
from commons.variables import *
from ping3 import ping
from handlers.log_handler import get_log
from handlers.mqtt_handler import MQTTClient
from handlers.mysql_tool import MyPymysqlPool
from handlers.profile_handler import replace_and_save
  
def conf_builder(args, log_path):
    global db_tool
    mysql_info = {}
    get_log(log_path).debug(args)
    input_file = os.path.join(project_root, "template", "profile_template.txt")
    # input_file = os.path.join(sys._MEIPASS, "template", "profile_template.txt")
    output_dir = args.Path
    replacements = {}
    # 环境判断
    get_log(log_path).info(f'即将根据您所填写的信息生成自动化配置...')
    get_log(log_path).info("*" * gap_num)
    get_log(log_path).info(f'Step 1：开始配置和检测环境信息和APP信息...')
    envs = {
        'iotpre': iotpre,
        'iottest': iottest,
        '56': iot56,
        '58': iot58,
    }
    evn = args.测试环境
    if evn in envs:
        replacements.update(envs[evn])
        mysql_info = {'host': f'{envs[evn]["云端DB_Host_v"]}', 'port': f'{envs[evn]["云端DB_Port_v"]}',
                      'user': f'{envs[evn]["云端DB_用户名_v"]}',
                      'password': f'{envs[evn]["云端DB_密码_v"]}', 'db_name': f'{envs[evn]["云端DB_库名_v"]}',
                      'charset': 'utf8'}
    else:
        get_log(log_path).error(f'未找到{evn}环境下的任何配置，请确认环境是否正确或让管理员添加对应数据！')
        time.sleep(2)
    # APP判断
    try:
        # 判断用户名密码是否正确
        db_tool = MyPymysqlPool(mysql_info)
        username = f"{args.用户名}"
        password = hashlib.sha256(f'{args.密码}'.encode('utf-8')).hexdigest()
        user_pw_sql = f"select password from lbl_app_account where username = '{username}'"
        user_pw_sql_res = db_tool.getAll(user_pw_sql)
        if not user_pw_sql_res:
            get_log(log_path).info(f'    !!!!    用户名不存在，请更正')
            time.sleep(2)
        else:
            get_log(log_path).info(f'    ----    用户名存在')
            time.sleep(2)
            if password == user_pw_sql_res[0]['password']:
                get_log(log_path).info(f'    ----    密码正确')
                time.sleep(2)
            else:
                get_log(log_path).info(f'    !!!!    密码错误，请更正')
                time.sleep(2)
        # 获取网关绑定的住家和房间
        sql_group_id = f"select group_id from newiot_device_group ndg  where biz_id = (select id from iot_dc_logic_device idld  where did = '{args.Did}' and siid = '2')"
        group_id = db_tool.getAll(sql_group_id)
        sql = f"select id, parent_id, name  from newiot_group ng  where id = '{group_id[0]['group_id']}'"
        res = db_tool.getAll(sql)
        homeId = res[0]['parent_id']
        room = res[0]['name']
        roomID = res[0]['id']
        sql_room_2nd = f"select id, name  from newiot_group ng  where parent_id = '{homeId}' and id != '{roomID}' limit 1"
        res = db_tool.getAll(sql_room_2nd)
        # room_2nd = res[0]['name']
        room_2nd_id = res[0]['id']
        app = {
            '乐比邻账号_v': f'{args.用户名}',
            '乐比邻密码_v': f'{args.密码}',
            '设备所在住家ID_v': f'{homeId}',
            '房间id': f'{room}id',
            '房间_id_v': f'{roomID}',
            # '房间2id': f'{room_2nd}id',
            '房间2_id_v': f'{room_2nd_id}'
        }
        replacements.update(app)
        get_log(log_path).info(f'    ----    数据库连通性正常')
        time.sleep(2)
        get_log(log_path).info(f'    ----    APP获取网关绑定住家及房间正常')
        time.sleep(2)
    except Exception as e:
        get_log(log_path).error(f"APP信息处理发生错误: {e}\n1、请确保所选环境与APP一致\n2、确保网关did填写正确")
        time.sleep(2)
    # 网关
    gateway = {
        '网关did_v': f'{args.Did}'
    }
    replacements.update(gateway)
    # 子设备&子设备did后缀
    get_log(log_path).info(f'Step 2：开始配置和检测子设备信息...')
    vdevs = {
        '虚拟设备1（204|208|209）': vDev204,
        '虚拟设备2（206|207|213）': vDev206,
        '虚拟设备3（210|211|212）': vDev210,
        '虚拟设备4（214|215|217）': vDev214,
        '虚拟设备5（216|218|219）': vDev216
    }
    vdev = args.虚拟设备
    if vdev in vdevs:
        replacements.update(vdevs[vdev])
        ips = list(vdevs[vdev].values())[:3]
        for ip in ips:
            ping_res = ping(f"{ip}")
            if ping_res is not None:
                get_log(log_path).info(f'    ----    虚拟设备ip={ip}连通性正常')
                time.sleep(2)
            else:
                get_log(log_path).info(f'    !!!!    虚拟设备ip={ip}无法连通,请检查设备')
                time.sleep(2)
    else:
        get_log(log_path).error(f'未找到{vdev}的任何配置，请确认虚拟子设备是否正确或让管理员添加对应数据！')
        time.sleep(2)
    # 云端桩did
    get_log(log_path).info(f'Step 3：开始配置和检测云端桩信息...')
    stake = {
        '设备did_v': f'{args.Did1}',
        '设备did2_v': f'{args.Did2}',
        '桩外设备did1_v': f'{args.桩外设备did}',
        '设备did100_v': f'{args.Did100}'
    }
    for did in stake.values():
        sql = f"select device_secret from iot_device where did = '{did}'"
        res = db_tool.getAll(sql)
        if not res:
            get_log(log_path).info(f'    !!!!    桩did={did}未注册')
            time.sleep(2)
            try:
                username = "HA-CE-R31-001"
                password = hashlib.sha256('jhfeq6vsxonjjlfa'.encode('utf-8')).hexdigest()
                # 创建MQTT客户端
                mqtt_client = MQTTClient(log_path, f'{envs[evn]["云端MQTT_Host_v"]}', username=username, password=password, client_id=did)
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
                get_log(log_path).info(f'    ----    注册{did}中...')
                time.sleep(3)
                # 停止消息循环
                mqtt_client.stop_loop()
                # 断开连接
                mqtt_client.disconnect()
                query_res = db_tool.getAll(sql)
                if query_res:
                    get_log(log_path).info(f'        ----        桩did={did}注册成功')
                else:
                    get_log(log_path).info(f'        !!!!        桩did={did}注册失败')
                time.sleep(2)
            except Exception as e:
                get_log(log_path).error(f"f'        ----        桩did={did}注册失败，报错{e}'")
                time.sleep(2)
        else:
            get_log(log_path).info(f'    ----    桩did={did}已在该测试环境注册')
            time.sleep(2)
    replacements.update(stake)
    # 关闭数据库
    db_tool.dispose()
    # 创建配置文件
    get_log(log_path).info("*" * gap_num)
    replace_and_save(input_file, output_dir, replacements, log_path)
