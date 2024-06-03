#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from handlers.app_handler import *
from commons.variables import *

ver = "V1.0"
businessId = "91910A54-E556-431D-90E8-433E77B36FBE"

def getMyAllHomeInfo(args, log_path):
    """
    获取住家信息
    适配条件：GUI需包含【测试环境、用户名、密码】
    :param args: GUI填写信息
    :param log_path: 日志记录路径
    :return: 住家信息
    """
    env = args.测试环境
    mysql_info = {'host': f'{envs[env]["云端DB_Host_v"]}', 'port': f'{envs[env]["云端DB_Port_v"]}',
                  'user': f'{envs[env]["云端DB_用户名_v"]}',
                  'password': f'{envs[env]["云端DB_密码_v"]}', 'db_name': f'{envs[env]["云端DB_库名_v"]}',
                  'charset': 'utf8'}
    url = f"{envs[env]['云端环境_v']}/rest/app/community/smartHome/getMyAllHomeInfo"
    data = {
        "seq": 888,
        "version": f"{ver}"
    }
    terminal_info = get_terminal_info(envs[env]['云端环境_v'], mysql_info, args.用户名, args.密码, log_path)
    accessToken = json.loads(terminal_info)['params']['accessToken']
    res = app_request(accessToken, url, data, log_path)
    return res


def bindDevice(args, log_path):
    """
    APP绑定设备
    适配条件：GUI需包含【测试环境、Did、用户名、密码、住家名称、房间、产品_软件模型_profileId】
    :param args: GUI填写信息
    :param log_path: 日志记录路径
    :return:
    """
    env = args.测试环境
    mysql_info = {'host': f'{envs[env]["云端DB_Host_v"]}', 'port': f'{envs[env]["云端DB_Port_v"]}',
                  'user': f'{envs[env]["云端DB_用户名_v"]}',
                  'password': f'{envs[env]["云端DB_密码_v"]}', 'db_name': f'{envs[env]["云端DB_库名_v"]}',
                  'charset': 'utf8'}
    db_tool = MyPymysqlPool(mysql_info)
    # 获取app_code
    app_code_sql = f"select app_code from lbl_app_account where username = '{args.用户名}'"
    app_code_res = db_tool.getAll(app_code_sql)
    app_code = app_code_res[0]['app_code']
    # 获取住家信息
    home_info = getMyAllHomeInfo(args, log_path)
    groupId = None
    subGroupId = None
    for home in json.loads(home_info)['params']:
        if home['groupName'] == args.住家名称:
            groupId = home['groupId']
            for room in home['subObjs']:
                if room['subGroupName'] == args.房间:
                    subGroupId = room['subGroupId']
    # 获取profileId
    profileId = args.产品_软件模型_profileId.split(':')[2]
    url = f"{envs[env]['云端环境_v']}/rest/app/community/smartHome/bindDevice"
    data = {
        "seq": 121,
        "version": "v0.1",
        "params": {
            "did": f"{args.Did}",
            "bindInfo": {
                "groupId": f"{groupId}",
                "subGroupId": f"{subGroupId}",
                "profileId": f"{profileId}",
                "userName": f"{args.用户名}",
                "appCode": app_code,
                "location": "(null),(null)"
            }
        }
    }
    terminal_info = get_terminal_info(envs[env]['云端环境_v'], mysql_info, args.用户名, args.密码, log_path)
    accessToken = json.loads(terminal_info)['params']['accessToken']
    res = app_request(accessToken, url, data, log_path)
    db_tool.dispose(1)
    return res


def encryptV1CtrlFIIDS(args, log_path, terminal_info, directDid=None, fiid=33024, dev_type="gw"):
    """
    子设备邀请或子设备取消邀请
    :param dev_type: 区分网关gw或终端网关mini
    :param log_path:
    :param directDid:
    :param args:
    :param fiid: 33024=子设备邀请（默认）、33025=子设备取消邀请
    :return: response
    """
    env = args.测试环境
    uri = f"{envs[env]['云端环境_v']}/rest/app/community/encryptV1CtrlFIIDS"
    if dev_type == "mini":
        siid = 3
    else:
        siid = 2
    if fiid == 33024:
        fiids = [{"value": {"mode": 0, "timeOutSeconds": 60}, "fiid": 33024}]
    elif fiid == 33025:
        fiids = [{"fiid": 33025}]
    else:
        fiids = None
    if directDid is None:
        directDid = args.Did
    else:
        directDid = directDid
    req_data = {
        "seq": 100,
        "version": f"{ver}",
        "params": {
            "did": f"{directDid}",
            "directDid": f"{directDid}",
            "siid": siid,
            "fiids": fiids,
            "ext": {
                "phone": f"{args.APP用户名}",
                "clientId": "1",
                "expireTime": "60",
                "appClientId": f"{json.loads(terminal_info)['params']['clientId']}"
            },
            "businessId": f"{businessId}"
        }
    }
    accessToken = json.loads(terminal_info)['params']['accessToken']
    res = app_request(accessToken, uri, req_data, log_path)
    return res


def getPhysicsDeviceList(args, log_path, terminal_info, groupId):
    """
    获取住家下的设备列表
    :param log_path:
    :param args:
    :param groupId: 住家ID
    :return: response
    """
    env = args.测试环境
    uri = f"{envs[env]['云端环境_v']}/rest/app/community/smartHome/getPhysicsDeviceList"
    req_data = {
        "seq": 102,
        "version": f"{version}",
        "params": {
            "groupId": groupId
        }
    }
    accessToken = json.loads(terminal_info)['params']['accessToken']
    res = app_request(accessToken, uri, req_data, log_path)
    return res

def delSubDevices(args, log_path, terminal_info, directDid, *dids):
    """
    删除子设备
    :param directDid:
    :param log_path:
    :param args:
    :param terminal_info: 终端信息（accessToken、clientId），默认每个请求都发起，建议传入，避免多次请求
    :param dids: 预删除子设备did：did1,did2...didn
    :return: response
    """
    env = args.测试环境
    uri = f"{envs[env]['云端环境_v']}/rest/app/community/delSubDevices"
    dids = list(dids)
    req_data = {
        "seq": 101,
        "version": f"{version}",
        "params": {
            "directDid": f"{directDid}",
            "dids": dids,
            "ext": {
                "expireTime": "10",
                "appClientId": f"{json.loads(terminal_info)['params']['clientId']}"
            },
            "businessId": f"{businessId}"
        }
    }
    accessToken = json.loads(terminal_info)['params']['accessToken']
    res = app_request(accessToken, uri, req_data, log_path)
    return res

# if __name__ == '__main__':
#     log_path = f"{log_dir}debug.txt"
#     envs = {
#         'iotpre': iotpre,
#         'iottest': iottest,
#         '56': iot56,
#         '58': iot58,
#     }
#     evn = 'iottest'
#     env = envs[evn]["云端环境_v"]
#     mysql_info = {'host': f'{envs[evn]["云端DB_Host_v"]}', 'port': f'{envs[evn]["云端DB_Port_v"]}',
#                   'user': f'{envs[evn]["云端DB_用户名_v"]}',
#                   'password': f'{envs[evn]["云端DB_密码_v"]}', 'db_name': f'{envs[evn]["云端DB_库名_v"]}',
#                   'charset': 'utf8'}
#     user = '15606075512'
#     pw = 'Admin123'
#     print(env)
#     print(mysql_info)
#     res = getMyAllHomeInfo(env, mysql_info, user, pw, log_path)
#     print(res)
#     subObjs = json.loads(res)['params']
#     print(len(subObjs))
