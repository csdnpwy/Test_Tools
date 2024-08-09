#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
        did_pools = ['12300001000000000004', '12300001000000000005', '12300001000000000006', '12300001000000000110',
                     '12300001000000000111', '12300001000000000666']
        url = f"{env}/rest/app/community/isOnLine"
        for did in did_pools:
            data = {
                "seq": 66,
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
        formatted_time = now.strftime("%d%m%H%M%S")
        did = f"1230000100{formatted_time}"
    else:
        did = stake_monitor
    get_log(log_path).debug(f'本次测试推举监控did--{did}')
    return did


# if __name__ == '__main__':
#     res = get_stake_did()
#     print(res)
