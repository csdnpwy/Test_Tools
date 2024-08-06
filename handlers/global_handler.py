#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from commons.variables import log_dir
from handlers.configReader import ConfigReader


def get_stake_did():
    """
    获取监控桩did
    """
    conf_reder = ConfigReader(f"{log_dir}version.ini")
    stake_monitor = conf_reder.get_value('global_config', 'stake_monitor')
    if stake_monitor == "none":
        now = datetime.now()
        formatted_time = now.strftime("%d%m%H%M%S")
        did = f"1230000100{formatted_time}"
    else:
        did = stake_monitor
    return did


if __name__ == '__main__':
    res = get_stake_did()
    print(res)
