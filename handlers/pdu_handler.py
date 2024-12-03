#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

from commons.variables import log_dir
from handlers.log_handler import get_log
from handlers.tcp_handler import TCPClient


def ctl_pdu(ip, port=17722, lock=1, ctl='open', ctl_modul='leelen', tcp_type='udp'):
    """
    控制pdu
    :param ip: pdu ip
    :param port: 端口
    :param lock: 控制座号
    :param ctl: open：打开  close：关闭  one：关闭-打开
    :param ctl_modul: pdu模型  leelen：立林   seewe：讯威
    :param tcp_type: tcp连接类型  tcp、udp
    """
    log_path = f"{log_dir}ctl_pdu.txt"
    if ctl_modul == 'seewe':
        Y0_close = bytes.fromhex('01050000ff008c3a')
        Y0_open = bytes.fromhex('010500000000cdca')
        Y1_close = bytes.fromhex('01050001ff00ddfa')
        Y1_open = bytes.fromhex('0105000100009c0a')
        Y2_close = bytes.fromhex('01050002ff002dfa')
        Y2_open = bytes.fromhex('0105000200006c0a')
        Y3_close = bytes.fromhex('01050003ff007c3a')
        Y3_open = bytes.fromhex('0105000300003dca')
        Y4_close = bytes.fromhex('01050004ff00cdfb')
        Y4_open = bytes.fromhex('0105000400008c0b')
        Y5_close = bytes.fromhex('01050005ff009c3b')
        Y5_open = bytes.fromhex('010500050000ddcb')
        Y6_close = bytes.fromhex('01050006ff006c3b')
        Y6_open = bytes.fromhex('0105000600002dcb')
        Y7_close = bytes.fromhex('01050007ff003dfb')
        Y7_open = bytes.fromhex('0105000700007c0b')
        YAll_close = bytes.fromhex('010f0000000802ffffe530')
        YAll_open = bytes.fromhex('010f00000008020000e480')
        cmd_mapping = {
            'lock_0_close': Y0_open,
            'lock_0_open': Y0_close,
            'lock_1_close': Y1_open,
            'lock_1_open': Y1_close,
            'lock_2_close': Y2_open,
            'lock_2_open': Y2_close,
            'lock_3_close': Y3_open,
            'lock_3_open': Y3_close,
            'lock_4_close': Y4_open,
            'lock_4_open': Y4_close,
            'lock_5_close': Y5_open,
            'lock_5_open': Y5_close,
            'lock_6_close': Y6_open,
            'lock_6_open': Y6_close,
            'lock_7_close': Y7_open,
            'lock_7_open': Y7_close,
            'lock_all_close': YAll_open,
            'lock_all_open': YAll_close
        }
        cmd = cmd_mapping[f"lock_{lock}_{ctl}"]
    else:
        lock_1_one = B"\xd1\xd2\xd5\x04\x03\x09\x01\x05\x21\xe1\x7b\x00\x00\x30\x00\x00\x00\xff\x62\x63\x07\x16\xff\x01\x00\x1a\x02\x01\x01\x01\xff\x62\x63\x07\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xe6"
        lock_1_close = B"\xd1\xd2\xd5\x04\x03\x09\x01\x05\x21\xe1\x7b\x00\x00\x30\x00\x00\x00\xff\x62\x63\x07\x16\xff\x01\x00\x1a\x02\x01\x01\x02\xff\x62\x63\x07\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xe5"
        lock_1_open = B"\xd1\xd2\xd5\x04\x03\x09\x01\xee\x19\x2a\x3a\x00\x00\x30\x00\x00\x00\xff\x62\x63\x07\x16\xff\x01\x00\x1a\x02\x01\x01\x03\xff\x62\x63\x07\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xfb"
        lock_2_one = B"\xd1\xd2\xd5\x04\x03\x09\x01\x05\x21\xe1\x7b\x00\x00\x30\x00\x00\x00\xff\x62\x63\x07\x16\xff\x01\x00\x1a\x02\x03\x01\x01\xff\x62\x63\x07\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xe4"
        lock_2_close = B"\xd1\xd2\xd5\x04\x03\x09\x01\x05\x21\xe1\x7b\x00\x00\x30\x00\x00\x00\xff\x62\x63\x07\x16\xff\x01\x00\x1a\x02\x03\x01\x02\xff\x62\x63\x07\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xe3"
        lock_2_open = B"\xd1\xd2\xd5\x04\x03\x09\x01\xee\x19\x2a\x3a\x00\x00\x30\x00\x00\x00\xff\x62\x63\x07\x16\xff\x01\x00\x1a\x02\x03\x01\x03\xff\x62\x63\x07\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xf9"
        lock_3_one = B"\xd1\xd2\xd5\x04\x03\x09\x01\x05\x21\xe1\x7b\x00\x00\x30\x00\x00\x00\xff\x62\x63\x07\x16\xff\x01\x00\x1a\x02\x05\x01\x01\xff\x62\x63\x07\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xe2"
        lock_3_close = B"\xd1\xd2\xd5\x04\x03\x09\x01\x05\x21\xe1\x7b\x00\x00\x30\x00\x00\x00\xff\x62\x63\x07\x16\xff\x01\x00\x1a\x02\x05\x01\x02\xff\x62\x63\x07\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xe1"
        lock_3_open = B"\xd1\xd2\xd5\x04\x03\x09\x01\xee\x19\x2a\x3a\x00\x00\x30\x00\x00\x00\xff\x62\x63\x07\x16\xff\x01\x00\x1a\x02\x05\x01\x03\xff\x62\x63\x07\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xf7"
        lock_4_one = B"\xd1\xd2\xd5\x04\x03\x09\x01\x05\x21\xe1\x7b\x00\x00\x30\x00\x00\x00\xff\x62\x63\x07\x16\xff\x01\x00\x1a\x02\x07\x01\x01\xff\x62\x63\x07\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xe0"
        lock_4_close = B"\xd1\xd2\xd5\x04\x03\x09\x01\x05\x21\xe1\x7b\x00\x00\x30\x00\x00\x00\xff\x62\x63\x07\x16\xff\x01\x00\x1a\x02\x07\x01\x02\xff\x62\x63\x07\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xdf"
        lock_4_open = B"\xd1\xd2\xd5\x04\x03\x09\x01\xee\x19\x2a\x3a\x00\x00\x30\x00\x00\x00\xff\x62\x63\x07\x16\xff\x01\x00\x1a\x02\x07\x01\x03\xff\x62\x63\x07\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xf5"
        cmd_mapping = {
            'lock_1_one': lock_1_one,
            'lock_1_close': lock_1_close,
            'lock_1_open': lock_1_open,
            'lock_2_one': lock_2_one,
            'lock_2_close': lock_2_close,
            'lock_2_open': lock_2_open,
            'lock_3_one': lock_3_one,
            'lock_3_close': lock_3_close,
            'lock_3_open': lock_3_open,
            'lock_4_one': lock_4_one,
            'lock_4_close': lock_4_close,
            'lock_4_open': lock_4_open,
        }
        cmd = cmd_mapping[f"lock_{lock}_{ctl}"]
    client = TCPClient(log_path, ip, port, type=tcp_type)
    client.connect()
    client.send_data(cmd)
    time.sleep(0.5)
    rec = client.receive_data()
    get_log(log_path).debug(f"Connected PDU: {ip}:{port}  Send: {cmd.hex()}  Rec: {rec.hex()}")
    client.close()


if __name__ == '__main__':
    # 讯威开关
    # ctl_pdu('10.58.104.10', port=502, lock=0, ctl_modul='seewe', tcp_type='tcp')
    # ctl_pdu('10.58.104.10', port=502, lock=0, ctl='close', ctl_modul='seewe', tcp_type='tcp')
    # 立林开关
    ctl_pdu('10.58.51.144', ctl='close')
    ctl_pdu('10.58.51.144')

