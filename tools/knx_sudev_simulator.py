#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import time

from ping3 import ping
from handlers.global_handler import is_ping_successful
from handlers.log_handler import get_log
from handlers.tcp_handler import KNXIpClient


def knx_dev_simulator(args, log_path):
    """
    KNX子设备模拟器
    :param args:
    :param log_path:
    """
    ip = args.IP
    ping_res = ping(ip)
    if is_ping_successful(ping_res):
        knx_client = KNXIpClient(log_path, ip, args=args)
        client_thread = threading.Thread(target=knx_client.start)
        # client_thread.daemon = True
        client_thread.start()
        time.sleep(2)
        knx_client.connect_knxip_server()
        time.sleep(5)
        client_status_thread = threading.Thread(target=knx_client.connection_status_request)
        # client_status_thread.daemon = True
        client_status_thread.start()
        # 非控制类设备状态上报
        time.sleep(3)
        schedule_device_thread = threading.Thread(target=knx_client.schedule_device_status_report)
        # schedule_device_thread.daemon = True
        schedule_device_thread.start()
    else:
        get_log(log_path).error(f"   !!!   KNXIP模块--{ip} 与PC不在同一个局域网")
