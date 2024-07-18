import time

import pandas as pd
from commons.variables import *
from handlers.mqtt_handler import MQTTClient
from lib.httprunner.hrun_global import get_hrun_conf

excel_path = r"C:\Users\panwy\Desktop\接口测试.xlsx"

# 读取配置
config = get_hrun_conf(excel_path)
print(config)

# 读取 Excel 文件
df = pd.read_excel(excel_path, sheet_name="Mqtt")
for index, row in df.iterrows():
    if row['是否执行'] == 'T':
        print(row["请求数据"])

# 创建MQTT客户端
log_path = f"{log_dir}test-interface.txt"
host = "iotpre.leelen.net"
user = "HA-CE-R31-001:12300001000000000001"
pwd = "beb71324864c35c4b2bfc95de61f01149324013baf51201a83412e84d183483a"
client_id = "12300001000000000001"
mqtt_client = MQTTClient(log_path, host, username=user, password=pwd, client_id=client_id)
# 连接到MQTT代理
mqtt_client.connect()
time.sleep(5)
print("test over")
