# HttpRunner公共函数

import pandas as pd


def get_hrun_conf(path, sheet_name="Config"):
    """
    获取HttpRunner excel配置文件
    :param path:
    :param sheet_name:
    :return:
    """
    config_df = pd.read_excel(path, sheet_name=sheet_name)
    config = dict(zip(config_df['Setting'], config_df['Value']))
    return config
