import json
import time

from commons.variables import *
from handlers.configReader import ConfigReader
from handlers.error_handler import CustomError
from lib.app.client_app import encryptV1CtrlFIIDS, getPhysicsDeviceList, delSubDevices
from lib.globalRes import get_did
from lib.tcpRes import usr_tcp232_t2_tool


def add_subDevices(args, log_path, dev_type, groupId, terminal_info, directDid=None, dev=0, direct_dev_type="gw"):
    """
    添加子设备，失败报错
    :param direct_dev_type: 直连设备类型，gw：网关 mini：终端
    :param dev:
    :param terminal_info:
    :param args: GUI信息
    :param groupId: 住家ID
    :param directDid: 网关
    :param log_path: 日志存储路径
    :param dev_type: 设备类型
    :return:
    """
    vdevs = {
        '虚拟设备1（204|208|209）': vDev204,
        '虚拟设备2（206|207|213）': vDev206,
        '虚拟设备3（210|211|212）': vDev210,
        '虚拟设备4（214|215|217）': vDev214,
        '虚拟设备5（216|218|219）': vDev216
    }
    vdev = args.虚拟设备
    ips = list(vdevs[vdev].values())[:3]
    did_postfixs = list(vdevs[vdev].values())[3:6]
    did_postfix = did_postfixs[dev]
    dev_ip = ips[dev]
    # 子设备信息
    configreader = ConfigReader(conf_file_path)
    subDevInf = configreader.get_section(dev_type)
    did = get_did(dev_type, did_postfix)
    info_list = [
        {"dt": subDevInf.get('device_type', '')},
        {"sn": subDevInf.get('soft_no', '')},
        {"mn": subDevInf.get('manufacture_name', '')},
        {"mid": subDevInf.get('manufacture_code', '')},
        {"mv": subDevInf.get('manufacture_version', '')},
        {"pl": subDevInf.get('product_label', '')},
        {"mi": subDevInf.get('model_identifier', '')},
        {"ps": subDevInf.get('product_sn', '')},
        {"hv": subDevInf.get('hardware_ver', '')},
        {"spn": subDevInf.get('soft_pro_no', '')},
        {"di": subDevInf.get('device_id', '')},
        {"ep_num": subDevInf.get('ep_num', '')},
        {"tv": subDevInf.get('third_version', '')},
        {"app_v": subDevInf.get('application_version', '')},
        {"dc": subDevInf.get('device_capacity', '')},
        {"zt": subDevInf.get('zone_type', '')}
    ]
    subDevInf = json.dumps({"info": info_list})
    # 删除子设备
    del_subDevice(args, log_path, terminal_info, groupId, directDid, did)
    # 子设备恢复出厂设置
    for _ in range(3):
        res = usr_tcp232_t2_tool(log_path, dev_ip, data_type='restore')
        if res == "55 01 83 03 61 19":
            break
    else:
        raise CustomError(f"子设备3次恢复出厂设置失败，停止添加子设备！")
    time.sleep(3)
    # 子设备写入属性
    usr_tcp232_t2_tool(log_path, dev_ip, send_data=subDevInf, data_type='str')
    time.sleep(3)
    # 子设备配置入网
    res = usr_tcp232_t2_tool(log_path, dev_ip, data_type='access')
    if res == "55 01 83 01 E0 D8":
        time.sleep(3)
        # app触发子设备邀请
        res = encryptV1CtrlFIIDS(args, log_path, terminal_info, directDid=directDid, direct_dev_type=direct_dev_type)
        if '"result":1,' in res:
            for i in range(0, 12):
                dev_list = getPhysicsDeviceList(args, log_path, terminal_info, groupId)
                if did in dev_list:
                    # 取消子设备邀请
                    encryptV1CtrlFIIDS(args, log_path, terminal_info, directDid=directDid, fiid=33025, direct_dev_type=direct_dev_type)
                    break
                else:
                    time.sleep(5)
            else:
                # 取消子设备邀请
                encryptV1CtrlFIIDS(args, log_path, terminal_info, directDid=directDid, fiid=33025, direct_dev_type=direct_dev_type)
                raise CustomError(f"{dev_type}添加失败！")
        else:
            raise CustomError(f"app触发子设备邀请失败！")
    else:
        raise CustomError(f"虚拟设备ip={dev_ip}请求入网失败！")


def del_subDevice(args, log_path, terminal_info, groupId, directDid, did):
    """
    删除子设备
    :param did:
    :param directDid:
    :param groupId:
    :param terminal_info:
    :param log_path:
    :param args:
    """
    res = delSubDevices(args, log_path, terminal_info, directDid, did)
    if '"result":1,' in res:
        for _ in range(3):
            dev_list = getPhysicsDeviceList(args, log_path, terminal_info, groupId)
            if did not in dev_list:
                break
            else:
                time.sleep(5)
        else:
            raise CustomError(f"子设备{did}删除失败！")
    else:
        raise CustomError(f"发送子设备{did}删除请求失败！")