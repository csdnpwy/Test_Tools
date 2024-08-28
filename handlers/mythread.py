#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
* @description: 多进程相关操作
* @copyright: Copyright (c) 2020 厦门立林科技有限公司
* @author: 潘伟阳
* @date: 2024/05/10 10:30
* @version: 1.0
* @fileName:
* @history:
"""
import threading
import time

from lib.mqtt.mqtt_mes_handler import gw_heartbeat


class HeartbeatThread(threading.Thread):
    """
    网关局域网通信心跳上报
    """
    def __init__(self, tcp_client, password):
        super().__init__()
        self.tcp_client = tcp_client
        self.password = password
        self._stop_event = threading.Event()

    def run(self):
        """
        重写run方法，心跳上报
        """
        while not self._stop_event.is_set():
            # print(f"Heartbeat操作...")
            try:
                data = gw_heartbeat(password=self.password)
                self.tcp_client.send_ssl_data(bytes.fromhex(data))
                # self.tcp_client.receive_ssl_data(password=self.password)
                # print(f"接收到数据{data_received}")
                time.sleep(7)  # 7S上报一次
            except Exception:
                pass

    def stop(self):
        """
        线程停止
        """
        self._stop_event.set()

    def stopped(self):
        """
        线程状态查询
        :return:
        """
        return self._stop_event.is_set()

