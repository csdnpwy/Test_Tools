#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from handlers.crc_handler import calculate_crc
from handlers.log_handler import get_log
from handlers.tcp_handler import TCPClient


def usr_tcp232_t2_tool(log_path, dev_ip, send_data=None, data_type='zcl', timeout=5):
    """
    插针式以太网模块USR-TCP232-T2数据收发方法，用于跟虚拟子设备盒子通信；
    :param log_path:
    :param dev_ip:
    :param send_data:发送数据
    :param data_type:数据类型（ZCL=ZCL指令、access=入网请求、status=状态查询、restore=设备恢复出厂设置、str=写属性字符串）
    :param timeout:超时时长，默认5S
    :return:接收数据
    """
    try:
        host = dev_ip
        port = 20108
        client = TCPClient(host, port, timeout=timeout)
        client.connect()
        # ZCL数据传输
        if data_type == 'zcl':
            data_list = send_data.split()
            date_len = hex(len(data_list))[2:].zfill(2)
            data_list.insert(0, date_len)
            send_data = "".join(data_list)
            send_data = "55000100" + send_data
            crc16 = calculate_crc(send_data.replace(" ", ""), crc_type='crc16-modbus')
            send_data = send_data + crc16
        # 控制入网
        elif data_type == 'access':
            send_data = "550003010102DDCB"  # 集中式入网
        # 状态查询
        elif data_type == 'status':
            send_data = "5500030200D96C"
        # 恢复出厂设置
        elif data_type == 'restore':
            send_data = "5500030300D8FC"
        # 其他（写属性）
        elif data_type == 'str':
            send_data = send_data
        client.clear_buff()
        if data_type == 'str':
            client.send_data(send_data.encode())
        else:
            client.send_data(bytes.fromhex(send_data))
        get_log(log_path).debug(f"向{dev_ip}发送数据：{send_data}")
        recv_data = client.receive_data().hex().upper()
        recv_data = ' '.join(recv_data[i:i + 2] for i in range(0, len(recv_data), 2))  # 每两位插入空格
        get_log(log_path).debug(f"{dev_ip}回复数据：{recv_data}")
        client.close()
        return recv_data
    except Exception as e:
        get_log(log_path).debug(f"与虚拟设备通信异常：{e}")


def usr_tcp232_t2_tool_clear_buff(log_path, dev_ip, timeout=5):
    """
    插针式以太网模块USR-TCP232-T2数据清空接收缓冲区，用于家居子设备模拟自动化
    :param log_path:
    :param dev_ip:
    :param timeout:超时时长，默认5S
    """
    try:
        host = dev_ip
        port = 20108
        client = TCPClient(host, port, timeout=timeout)
        client.connect()
        client.clear_buff()
        client.close()
    except Exception as e:
        get_log(log_path).debug(f"与虚拟设备通信异常：{e}")


def usr_tcp232_t2_tool_recv(log_path, dev_ip, timeout=5):
    """
    插针式以太网模块USR-TCP232-T2数据接受方法，用于家居子设备模拟自动化
    :param log_path:
    :param dev_ip:
    :param timeout:超时时长，默认5S
    :return:接收数据
    """
    try:
        host = dev_ip
        port = 20108
        client = TCPClient(host, port, timeout=timeout)
        client.connect()
        recv_data = client.receive_data().hex().upper()
        recv_data = ' '.join(recv_data[i:i + 2] for i in range(0, len(recv_data), 2))  # 每两位插入空格
        get_log(log_path).debug(f"接收数据：{recv_data}")
        client.close()
        return recv_data
    except Exception as e:
        get_log(log_path).debug(f"与虚拟设备通信异常：{e}")
