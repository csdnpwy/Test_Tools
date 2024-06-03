from commons.variables import conf_file_path
from handlers.configReader import ConfigReader


def get_conf_value(section, option):
    """
    获取配置文件值
    :param section: 节点名
    :param option: 键名
    :return: 值
    """
    configreader = ConfigReader(conf_file_path)
    value = configreader.get_value(section, option)
    return value

def get_did(dev_type, did_postfix):
    """
    获取虚拟设备did
    :param did_postfix:
    :param dev_type: 设备类型（T2筒射灯等）
    :return: did
    """
    configreader = ConfigReader(conf_file_path)
    did_prefix = configreader.get_value('did_prefix', dev_type)
    did_postfix = did_postfix
    did = did_prefix + did_postfix
    return did
