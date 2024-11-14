#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
from datetime import datetime

from commons.variables import log_dir
from handlers.app_handler import app_request
from handlers.configReader import ConfigReader
from handlers.log_handler import get_log


def get_stake_did(accessToken, env, log_path):
    """
    获取监控桩did
    优先从did_pools选举，非连接状态选用
    did_pools都为连接状态则根据时间戳随机生成
    """
    conf_reder = ConfigReader(f"{log_dir}version.ini")
    stake_monitor = conf_reder.get_value('global_config', 'stake_monitor')
    if stake_monitor == "none":
        did_pools = ['12300001000000000111', '12300001000000000222', '12300001000000000333', '12300001000000000444',
                     '12300001000000000555', '12300001000000000666']
        url = f"{env}/rest/app/community/isOnLine"
        seq = 110
        for _ in range(0, 10):  # pwy0816：修订为随机从资源池获取，避免第一个did异常导致每次都异常
            did = random.choice(did_pools)
            seq += 1
            data = {
                "seq": seq,
                "version": "v0.1",
                "params": {
                    "did": f"{did}"
                }
            }
            res = app_request(accessToken, url, data, log_path)
            if '{"isOnline":0}' in res:
                get_log(log_path).debug(f'本次测试推举监控did--{did}')
                return did
        now = datetime.now()
        formatted_time = now.strftime("%m%d%H%M%S")
        did = f"1230000100{formatted_time}"
    else:
        did = stake_monitor
    get_log(log_path).debug(f'本次测试推举监控did--{did}')
    return did


def is_ping_successful(ping_res):
    """
    判断ping结果，兼容多个环境结果
    :param ping_res:
    :return:
    """
    if ping_res is None:
        return False
    if isinstance(ping_res, bool):
        return ping_res
    try:
        ping_value = float(ping_res)
        return ping_value >= 0
    except ValueError:
        return False
