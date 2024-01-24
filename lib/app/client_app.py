#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from handlers.app_handler import *
from commons.variables import *


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
        "version": "V1.0"
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
