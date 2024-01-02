#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import json
from datetime import datetime
import requests

from handlers.log_handler import get_log
from handlers.mysql_tool import MyPymysqlPool


def get_uuid(env):
    # 发送HTTP POST请求
    url = f'{env}/rest/app/community/safe/getUuid'
    # 定义自定义请求头
    custom_headers = {
        'Content-Type': 'application/json'  # 替换为适合您的Content-Type
    }
    # POST请求的数据，可以是字典或JSON字符串，根据需要修改
    post_data = {
        'seq': '666',
        'version': 'V1.0'
    }
    # 发送HTTP POST请求，包括自定义请求头和数据
    response = requests.post(url, headers=custom_headers, json=post_data)
    # 检查是否成功收到响应
    if response.status_code == 200:
        # 打印响应内容
        uuid = json.loads(response.text)['params']['uuid']
    else:
        uuid = 0
    return uuid

def get_terminal_info(env, mysql_info, username, password, log_path):
    password = hashlib.sha256(f"{password}".encode('utf-8')).hexdigest()
    url = f'{env}/rest/app/community/user/login'
    custom_headers = {
        'Content-Type': 'application/json',
        'Connection': 'close'
    }
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    query_sql = f"select app_terminal_id, app_terminal_name, app_terminal_model from lbl_app_terminal_auth where account_id = (select id from lbl_app_account where phone = '{username}')"
    db_tool = MyPymysqlPool(mysql_info)
    res = db_tool.getAll(query_sql)
    db_tool.dispose(1)
    # print(res)
    if res:
        post_data = {
            "params": {
                "accountType": 1,
                "intlPhoneCode": 86,
                "osType": 1,
                "osVersion": "5.1.1",
                "password": f"{password}",
                "terminalId": f"{res[0]['app_terminal_id']}",
                "terminalModel": f"{res[0]['app_terminal_model']}",
                "terminalName": f"{res[0]['app_terminal_name']}",
                "username": f"{username}",
                "timestamp": f"{ts}",
                "uniqueCode": f"{get_uuid(env)}"
            },
            "seq": 888,
            "version": "V1.0"
        }
        # post_data = json.dumps(post_data)
        # print(post_data)
        response = requests.post(url, headers=custom_headers, json=post_data)
        if response.status_code == 200:
            # 返回响应内容
            return response.text
        else:
            get_log(log_path).error(f'请求失败，状态码：{response.status_code}')
    else:
        get_log(log_path).error(f"此终端无效，请确认用户名是否存在！")


def app_request(accesstoken, url, data, log_path):
    custom_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'{accesstoken}'
    }
    response = requests.post(url, headers=custom_headers, json=data)
    if response.status_code == 200:
        # 返回响应内容
        return response.text
    else:
        get_log(log_path).error(f'请求失败，状态码：{response.status_code}')