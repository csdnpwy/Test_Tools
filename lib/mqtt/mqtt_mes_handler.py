#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mqtt报文组成
因 modules.py 参数局限前端 GUI 的参数命名，所以写此模块替换
"""
import json

from commons.variables import conf_file_path
from handlers.configReader import ConfigReader
from handlers.crc_handler import calc_crc8
from handlers.data_encrypt_handler import aes_encrypt, hmac_encode

version = "V1.0"
businessId = "91910A54-E556-431D-90E8-433E77B36FBE"
configreader = ConfigReader(conf_file_path)
dev_mgmt_module = configreader.get_value('module', '设备管理组件')

# ================================================ 操作子设备相关 ========================================================
def dmgr_subDeviceOnlineStatus(directDid, subDid, seq):
    """
    网关mqtt请求报文--子设备在线状态上报
    :param directDid: 网关did
    :param subDid: 子设备did
    :param seq: seq对应接收到请求的seq
    :return: 请求（上报）报文
    """
    req_payload = {
        "method": "dmgr.subDeviceOnlineStatus",
        "src": f"{directDid}",
        "dst": f"{dev_mgmt_module}",
        "version": f"{version}",
        "params": [{
            "did": f"{subDid}",
            "status": 1
        }],
        "seq": seq
    }
    return json.dumps(req_payload)


def dmgr_reportAddDevice(directDid, subDid, dev_type, seq):
    """
    网关mqtt请求报文--上报添加子设备
    :param directDid: 网关did
    :param subDid: 子设备did
    :param dev_type: 对应配置文件设备类型
    :param seq: seq对应接收到请求的seq
    :return: 请求报文
    """
    config = ConfigReader(conf_file_path)
    subDevInf = config.get_section(dev_type)
    req_payload = {
        "method": "dmgr.reportAddDevice",
        "src": f"{directDid}",
        "dst": f"{dev_mgmt_module}",
        "version": f"{version}",
        "params": {
            "businessId": f"{businessId}",
            "subDevices": [{
                "errCode": "null",
                "fatherDid": f"{directDid}",
                "did": f"{subDid}",
                "profileId": f"{subDevInf.get('profileid', '')}",
                "manufacturer": f"{subDevInf.get('manufacture_name', '')}",
                "lineProductModel": f"{subDevInf.get('product_label', '')}",
                "softModel": f"{subDevInf.get('model_identifier', '')}",
                "softVersion": f"{subDevInf.get('manufacture_version', '')}",
                "productSn": f"{subDevInf.get('product_sn', '')}",
                "softProjectNo": f"{subDevInf.get('soft_pro_no', '')}"
            }]
        },
        "seq": seq
    }
    return json.dumps(req_payload)


def dmgr_reportPIIDS(directDid, subDid, seq):
    """
    网关mqtt请求报文--子设备上报piids
    :param directDid: 网关did
    :param subDid: 子设备did
    :param seq: seq对应接收到请求的seq
    :return: 请求（上报）报文
    """
    req_payload = {
        "method": "dmgr.reportPIIDS",
        "src": f"{directDid}",
        "dst": f"{dev_mgmt_module}",
        "version": f"{version}",
        "params": {
            "did": f"{subDid}",
            "siids": [{
                "siid": 0,
                "piids": [{
                    "piid": 273,
                    "value": 0
                }]
            }]
        },
        "seq": seq
    }
    return json.dumps(req_payload)


# ============================================== 网关局域网通信相关 =======================================================
def format_lenth(hex_str):
    """
    格式化数据长度，eg：174 --> 74010000
    :param hex_str: 数据长度，为十六进制的字符串
    :return: 格式化后十六进制
    """
    if len(hex_str) % 2 == 1:
        hex_str = '0' + hex_str
    byte_str = bytes.fromhex(hex_str)  # Convert hex string to bytes
    byte_str_reversed = byte_str[::-1]  # Reverse byte order
    byte_str_padded = byte_str_reversed.ljust(4, b'\x00')  # Pad to length 8 with 0
    return byte_str_padded.hex()  # Convert bytes back to hex string


def format_req_data(payload, is_encrypt=True, password=None):
    """
    网关局域网通信发送数据格式化
    :param payload: 请求主题
    :param is_encrypt: 是否加密
    :param password: 机密秘钥（若要加密必须带）
    :return: 格式化的请求数据
    """
    if is_encrypt and password is None:
        raise ValueError("要进行数据加密时必须传参password！")
    if isinstance(payload, dict):
        payload = json.dumps(payload, ensure_ascii=False).replace(" ", "")
    if is_encrypt:
        encryption = "01"
        payload = aes_encrypt(payload, password)
    else:
        encryption = "00"
        payload = payload.encode().hex()
    head = 'LEEL'.encode().hex()
    lenth = format(int(len(payload) / 2) + 4, '02x')
    lenth = format_lenth(lenth)
    padding = 8 - len(lenth)
    lenth += '0' * padding
    vs = "0001"
    req_data = f'{head}{lenth}{vs}{encryption}{payload}'
    byte_list = bytes.fromhex(req_data)
    req_data = req_data + calc_crc8(byte_list)
    # print(f"预发送16进制码：{req_data}")
    return req_data


def gw_bind(src_did, dst_did, groupId):
    """
    绑定操作
    :param src_did: 局域网内源did
    :param dst_did: 局域网内目的did
    :param groupId: 住家id
    :return: 格式化的预发送数据
    """
    payload = {
        "method": "bind",
        "seq": 1,
        "params": {
            "src": f"{src_did}",
            "dst": f"{dst_did}",
            "groupId": f"{groupId}"
        }
    }
    req_data = format_req_data(payload, is_encrypt=False)
    return req_data


def gw_random(src_did, dst_did):
    """
    获取随机数
    :param src_did: 局域网内源did
    :param dst_did: 局域网内目的did
    :return: 格式化的预发送数据
    """
    payload = {
        "method": "random",
        "seq": 2,
        "params": {
            "src": f"{src_did}",
            "dst": f"{dst_did}",
        }
    }
    req_data = format_req_data(payload, is_encrypt=False)
    return req_data


def gw_login(src_did, dst_did, groupId, random_code, is_encrypt=True):
    """
    局域网登录
    :param src_did: 局域网内源did
    :param dst_did: 局域网内目的did
    :param groupId: 住家id
    :param random_code: 随机码
    :return: 格式化的预发送数据
    :param is_encrypt: 是否进行payload二次加密（AES加密）
    """
    key_random = '@9jHaGa]' + random_code
    password = hmac_encode("md5", key_random, groupId).upper()
    payload = {
        "method": "login",
        "seq": 3,
        "params": {
            "src": f"{src_did}",
            "dst": f"{dst_did}",
            "username": f"{groupId}",
            "password": f"{password}"
        }
    }
    req_data = format_req_data(payload, is_encrypt=is_encrypt, password=password)
    return req_data, password


def gw_heartbeat(is_encrypt=True, password=None):
    """
    局域网心跳数据上报
    :return: 格式化的预发送数据
    """
    if is_encrypt and password is None:
        raise ValueError("要进行数据加密时必须传参password！")
    payload = {
        "method": "heartbeat",
        "seq": 66,
        "params": {
            "interval": 7
        }
    }
    req_data = format_req_data(payload, is_encrypt=is_encrypt, password=password)
    return req_data


def gw_transparent(payload, is_encrypt=True, password=None):
    """
    网关局域网信息透传之自定义payload
    :param payload: payload
    :return: 格式化的透传信息
    :param password: 通信秘钥
    :param is_encrypt: 是否进行payload二次加密（AES加密）
    """
    req_data = format_req_data(payload, is_encrypt=is_encrypt, password=password)
    return req_data
