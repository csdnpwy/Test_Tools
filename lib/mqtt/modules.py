#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件mqtt报文解析
主体为GUI的Did，即：
req_payload为向Did请求（收到）的报文
rsp_payload为Did回复（发出）报文
"""
import json
import random

from commons.variables import *


def dmgr_reg(args, module=dev_manage_moduleID, seq=666):
    """
    生成设备注册mqtt报文和回复报文
    适配条件：GUI需包含【测试环境、Did、产品_软件模型_profileId】
    :param module:
    :param seq:
    :param args:
    :return: 设备注册mqtt报文、回复报文
    """
    profileId = int(args.产品_软件模型_profileId.split(':')[2])
    softModel = args.产品_软件模型_profileId.split(':')[1]
    req_payload = None
    rsp_payload = {
        "method": "dmgr.reg",
        "src": f"{args.Did}",
        "dst": f"{module}",
        "version": "V1.0",
        "params": {
            "lineProductModel": f"{softModel}",
            "did": f"{args.Did}",
            "softModel": f"{softModel}",
            "profileId": profileId
        },
        "seq": seq
    }
    res = {"req": req_payload, "rsp": rsp_payload}
    return res


def dmgr_reg_sensor_link_duration(stake_did, softModel, profileId, module=dev_manage_moduleID, seq=666):
    """
    sensor_link_duration工具生成设备注册mqtt报文和回复报文
    适配条件：GUI需包含【测试环境、Did、产品_软件模型_profileId】
    :param softModel:
    :param profileId:
    :param module:
    :param seq:
    :param stake_did:
    :return: 设备注册mqtt报文、回复报文
    """
    req_payload = None
    rsp_payload = {
        "method": "dmgr.reg",
        "src": f"{stake_did}",
        "dst": f"{module}",
        "version": "V1.0",
        "params": {
            "did": f"{stake_did}",
            "softModel": f"{softModel}",
            "profileId": profileId
        },
        "seq": seq
    }
    res = {"req": req_payload, "rsp": rsp_payload}
    return res


def dmgr_checkBind(args, module=dev_manage_moduleID, seq=666):
    """
    生成设备绑定mqtt报文和回复报文
    适配条件：GUI需包含【测试环境、Did、产品_软件模型_profileId】
    :param module:
    :param seq:
    :param args:
    :return: 设备注册mqtt报文、回复报文
    """
    req_payload = "bindDevice"  # 可从app函数bindDevice发起请求
    rsp_payload = {
        "result": 1,
        "method": "dmgr.checkBind",
        "dst": f"{module}",
        "seq": seq,
        "params": {
            "isBind": 1
        },
        "src": f"{args.Did}",
        "version": "V1.0"
    }
    res = {"req": req_payload, "rsp": rsp_payload}
    return res


def dmgr_notifyUnBind(args, module=dev_manage_moduleID, seq=666):
    """
    生成设备解绑mqtt报文和回复报文
    适配条件：GUI需包含【测试环境、Did、产品_软件模型_profileId】
    :param module:
    :param seq:
    :param args:
    :return: 设备解绑mqtt报文、回复报文
    """
    req_payload = None
    rsp_payload = {
        "method": "dmgr.notifyUnBind",
        "src": f"{args.Did}",
        "dst": f"{module}",
        "result": 1,
        "seq": seq,
        "version": "V1.0"
    }
    res = {"req": req_payload, "rsp": rsp_payload}
    return res


def dmgr_readPIIDS(args, module=dev_manage_moduleID, seq=666):
    """
    读取属性mqtt报文和回复报文
    适配条件：GUI需包含【测试环境、Did、产品_软件模型_profileId】
    :param module:
    :param seq:
    :param args:
    :return: 属性mqtt报文和回复报文
    """
    soft_model = args.产品_软件模型_profileId.split(':')[1]
    mac = args.Did[-12:]
    mac_format = ":".join([mac[i:i + 2] for i in range(0, len(mac), 2)])
    sn_random_num = random.randint(10, 99)
    req_payload = None
    if soft_model == 'HAZB-CE-R15-112':
        rsp_payload = {
            "result": 1,
            "method": "dmgr.readPIIDS",
            "dst": f"{module}",
            "params": {
                "did": f"{args.Did}",
                "directDid": f"{args.Did}",
                "siids": [
                    {
                        "siid": 0,
                        "piids": [
                            {
                                "piid": 3,
                                "value": "MAIN-SSD201:2.39,NCP-EFR32:1.02"
                            },
                            {
                                "piid": 4,
                                "value": "LEELEN"
                            },
                            {
                                "piid": 5,
                                "value": f"{mac_format}"
                            },
                            {
                                "piid": 6,
                                "value": f"{soft_model}"
                            },
                            {
                                "piid": 7,
                                "value": "116.159034,40.360058"
                            },
                            {
                                "piid": 18,
                                "value": f"{soft_model}"
                            },
                            {
                                "piid": 19,
                                "value": "HA-2117-03"
                            },
                            {
                                "piid": 20,
                                "value": "panwy"
                            },
                            {
                                "piid": 10,
                                "value": f"031525E0190000{sn_random_num}"
                            },
                            {
                                "piid": 88,
                                "value": "192.168.1.250"
                            },
                            {
                                "piid": 239,
                                "value": f"{soft_model}"
                            },
                            {
                                "piid": 330,
                                "value": "SSD201"
                            }
                        ]
                    }
                ]
            },
            "src": f"{args.Did}",
            "version": "V1.0",
            "seq": seq
        }
    elif soft_model == 'HA-CE-R31-001':
        rsp_payload = {
            "result": 1,
            "method": "dmgr.readPIIDS",
            "dst": f"{module}",
            "params": {
                "did": f"{args.Did}",
                "directDid": f"{args.Did}",
                "siids": [
                    {
                        "siid": 0,
                        "piids": [
                            {
                                "piid": 3,
                                "value": "MAIN-SSD201:1.14"
                            },
                            {
                                "piid": 4,
                                "value": "LEELEN"
                            },
                            {
                                "piid": 5,
                                "value": f"{mac_format}"
                            },
                            {
                                "piid": 6,
                                "value": "Z3GW-E"
                            },
                            {
                                "piid": 7,
                                "value": "116.159034,40.360058"
                            },
                            {
                                "piid": 18,
                                "value": f"{soft_model}"
                            },
                            {
                                "piid": 19,
                                "value": "HA-2005"
                            },
                            {
                                "piid": 20,
                                "value": "panwy"
                            },
                            {
                                "piid": 10,
                                "value": f"031525E0190000{sn_random_num}"
                            },
                            {
                                "piid": 88,
                                "value": f"192.168.1.250"
                            },
                            {
                                "piid": 239,
                                "value": f"{soft_model}"
                            },
                            {
                                "piid": 330,
                                "value": "SSD201"
                            }
                        ]
                    }
                ]
            },
            "src": f"{args.Did}",
            "version": "V1.0",
            "seq": seq
        }
    else:
        rsp_payload = None
    res = {"req": req_payload, "rsp": rsp_payload}
    return res


def dmgr_ctrlFIIDS(args, module=dev_manage_moduleID, seq=666):
    """
    控制设备功能mqtt报文和回复报文
    适配条件：GUI需包含【测试环境、Did、产品_软件模型_profileId】
    :param module:
    :param seq:
    :param args:
    :return: 控制设备功能mqtt报文、回复报文
    """
    req_payload = None
    rsp_payload = {
        "method": "dmgr.ctrlFIIDS",
        "src": f"{args.Did}",
        "dst": f"{module}",
        "result": 1,
        "seq": seq
    }
    res = {"req": req_payload, "rsp": rsp_payload}
    return res


def dmgr_writePIIDS(args, module=dev_manage_moduleID, seq=666):
    """
    写入设备功能mqtt报文和回复报文
    适配条件：GUI需包含【测试环境、Did、产品_软件模型_profileId】
    :param module:
    :param seq:
    :param args:
    :return: 写入设备功能mqtt报文、回复报文
    """
    req_payload = None
    rsp_payload = {
        "method": "dmgr.writePIIDS",
        "src": f"{args.Did}",
        "dst": f"{module}",
        "result": 1,
        "seq": seq
    }
    res = {"req": req_payload, "rsp": rsp_payload}
    return res


# ================================================子设备操作==============================================================

def dmgr_subDeviceOnlineStatus(args, module=dev_manage_moduleID, seq=666):
    """
    子设备在线状态上报mqtt报文和回复报文
    适配条件：GUI需包含【测试环境、Did、subDevDid】
    :param module:
    :param seq:
    :param args:
    :return: 子设备在线状态上报mqtt报文、回复报文
    """
    req_payload = {
        "dst": f"{args.Did}",
        "message": "正确应答",
        "method": "dmgr.subDeviceOnlineStatus",
        "result": 1,
        "seq": seq,
        "src": f"{module}"
    }
    rsp_payload = {
        "method": "dmgr.subDeviceOnlineStatus",
        "src": f"{args.Did}",
        "dst": f"{module}",
        "version": "V1.0",
        "params": [{
            "did": f"{args.subDevDid}",
            "status": 1
        }],
        "seq": seq
    }
    res = {"req": req_payload, "rsp": rsp_payload}
    return res


def dmgr_reportAddDevice(args, module=dev_manage_moduleID, seq=666):
    """
    添加子设备mqtt报文和回复报文
    适配条件：GUI需包含【测试环境、Did、subDevDid】
    :param module:
    :param seq:
    :param args:
    :return: 添加子设备mqtt报文、回复报文
    """
    req_payload = {
        "dst": f"{args.Did}",
        "message": "正确应答",
        "method": "dmgr.reportAddDevice",
        "result": 1,
        "seq": seq,
        "src": f"{module}"
    }
    rsp_payload = {
        "method": "dmgr.reportAddDevice",
        "src": f"{args.Did}",
        "dst": f"{module}",
        "version": "V1.0",
        "params": {
            "businessId": "FA2F64CC-2C62-462F-B116-54929539231D",
            "subDevices": [{
                "errCode": "null",
                "fatherDid": f"{args.Did}",
                "did": f"{args.subDevDid}",
                "profileId": 319,
                "manufacturer": "LEELEN",
                "lineProductModel": "HAZB-PS-R84-001",
                "softModel": "HAZB-AD-R82-001",
                "softVersion": "MAIN-EFR32MG21:1.30",
                "productSn": "032609E01K000271",
                "softProjectNo": "HA-2206"
            }]
        },
        "seq": seq
    }
    res = {"req": req_payload, "rsp": rsp_payload}
    return res


def dmgr_reportPIIDS(args, module=dev_manage_moduleID, seq=666):
    """
    上报网络短地址属性和回复报文
    适配条件：GUI需包含【测试环境、Did、subDevDid】
    :param module:
    :param seq:
    :param args:
    :return: 子上报网络短地址属性和回复报文
    """
    req_payload = {
        "dst": f"{args.Did}",
        "message": "正确应答",
        "method": "dmgr.reportPIIDS",
        "result": 1,
        "seq": seq,
        "src": f"{module}"
    }
    rsp_payload = {
        "method": "dmgr.reportPIIDS",
        "src": f"{args.Did}",
        "dst": f"{module}",
        "version": "V1.0",
        "params": {
            "did": f"{args.subDevDid}",
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
    res = {"req": req_payload, "rsp": rsp_payload}
    return res

def dmgr_subDeviceOnlineStatus_rtczSensor(args, module=dev_manage_moduleID, seq=666):
    """
    子设备在线状态上报mqtt报文和回复报文
    适配条件：GUI需包含【测试环境、Did、subDevDid】
    :param module:
    :param seq:
    :param args:
    :return: 子设备在线状态上报mqtt报文、回复报文
    """
    req_payload = {
        "dst": f"{args.传感器所在网关}",
        "message": "正确应答",
        "method": "dmgr.subDeviceOnlineStatus",
        "result": 1,
        "seq": seq,
        "src": f"{module}"
    }
    rsp_payload = {
        "method": "dmgr.subDeviceOnlineStatus",
        "src": f"{args.传感器所在网关}",
        "dst": f"{module}",
        "version": "V1.0",
        "params": [{
            "did": "000b20128cf681fffea5cpwy",
            "status": 1
        }],
        "seq": seq
    }
    res = {"req": req_payload, "rsp": rsp_payload}
    return res


def dmgr_reportAddDevice_rtczSensor(args, module=dev_manage_moduleID, seq=667):
    """
    添加子设备mqtt报文和回复报文
    适配条件：GUI需包含【测试环境、Did、subDevDid】
    :param module:
    :param seq:
    :param args:
    :return: 添加子设备mqtt报文、回复报文
    """
    req_payload = {
        "dst": f"{args.传感器所在网关}",
        "message": "正确应答",
        "method": "dmgr.reportAddDevice",
        "result": 1,
        "seq": seq,
        "src": f"{module}"
    }
    rsp_payload = {
        "method": "dmgr.reportAddDevice",
        "src": f"{args.传感器所在网关}",
        "dst": f"{module}",
        "version": "V1.0",
        "params": {
            "businessId": "FA2F64CC-2C62-462F-B116-54929539231D",
            "subDevices": [{
                "errCode": "null",
                "fatherDid": f"{args.传感器所在网关}",
                "did": f"000b20128cf681fffea5cpwy",
                "profileId": 282,
                "manufacturer": "MULTIR",
                "productModel": "HAZB-SD-R71-001",
                "softModel": "HAZB-SD-R71-001",
                "softVersion": "MAIN:0.2",
                "productSn": "",
                "softProjectNo": "HA-2020"
            }]
        },
        "seq": seq
    }
    res = {"req": req_payload, "rsp": rsp_payload}
    return res


def dmgr_reportPIIDS_rtczSensor(args, module=dev_manage_moduleID, seq=668):
    """
    上报网络短地址属性和回复报文
    适配条件：GUI需包含【测试环境、Did、subDevDid】
    :param module:
    :param seq:
    :param args:
    :return: 子上报网络短地址属性和回复报文
    """
    req_payload = {
        "dst": f"{args.传感器所在网关}",
        "message": "正确应答",
        "method": "dmgr.reportPIIDS",
        "result": 1,
        "seq": seq,
        "src": f"{module}"
    }
    rsp_payload = {
        "method": "dmgr.reportPIIDS",
        "src": f"{args.传感器所在网关}",
        "dst": f"{module}",
        "version": "V1.0",
        "params": {
            "did": f"000b20128cf681fffea5cpwy",
            "siids": [{
                "siid": 2,
                "piids": [{
                    "piid": 236,
                    "value": 0
                }]
            }]
        },
        "seq": seq
    }
    res = {"req": req_payload, "rsp": rsp_payload}
    return res
