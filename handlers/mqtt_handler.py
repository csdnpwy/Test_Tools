import hashlib
import json
import os
import random
import time
from datetime import datetime
from commons.variables import *
import paho.mqtt.client as mqtt

from handlers.log_handler import get_log
from lib.mqtt.modules import dmgr_checkBind, dmgr_readPIIDS, dmgr_ctrlFIIDS, dmgr_writePIIDS, dmgr_notifyUnBind


class MQTTClient:
    def __init__(self, log_path, broker_address, username=None, password=None, client_id="", tool="default", args=None):
        self.args = args
        self.log_path = log_path
        self.client = mqtt.Client(client_id)
        self.broker_address = broker_address
        self.username = username
        self.password = password

        # 设置回调函数
        self.client.on_connect = self.on_connect
        if tool == 't2_led':
            self.client.on_message = self.on_message_t2_led
        elif tool == 'direct_con_dev':
            self.client.on_message = self.on_message_direct_con_dev
        else:
            self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            get_log(self.log_path).debug("Connected to MQTT Broker")
        else:
            get_log(self.log_path).debug(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, message):
        get_log(self.log_path).debug(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

    def on_message_t2_led(self, client, userdata, message):
        playload = str(message.payload).replace(" ", "")
        if self.args.场景 == '分布式-群组':
            if message.topic == f'lliot/receiver/{self.args.Did}' and '"fiid":33106,' in playload:
                current_time = datetime.now()
                with open(f'{os.path.dirname(self.log_path)}\\gw_control.txt', 'w') as file:
                    file.write(f'{current_time} -- {message.topic} -- {playload}')
                get_log(self.log_path).debug(f"网关接收群组控制报文：{message.topic}: {playload}")
            elif "lliot/fiids_report" in message.topic:
                get_log(self.log_path).debug(f"子设备上报状态：{message.topic}: {playload}")
                current_time = datetime.now()
                with open(f'{os.path.dirname(self.log_path)}\\fiids_report.txt', 'a') as file:
                    file.write(f'{current_time} -- {message.topic} -- {playload}\n')
        elif self.args.场景 == '集中式-联动' or self.args.场景 == '单控':
            if message.topic == f'lliot/receiver/{self.args.Did}' and '"fiid":49408,' in playload:
                current_time = datetime.now()
                with open(f'{os.path.dirname(self.log_path)}\\gw_control.txt', 'w') as file:
                    file.write(f'{current_time} -- {message.topic} -- {playload}')
                get_log(self.log_path).debug(f"网关接收群组控制报文：{message.topic}: {playload}")
            elif "lliot/fiids_report" in message.topic:
                get_log(self.log_path).debug(f"子设备上报状态：{message.topic}: {playload}")
                current_time = datetime.now()
                with open(f'{os.path.dirname(self.log_path)}\\fiids_report.txt', 'a') as file:
                    file.write(f'{current_time} -- {message.topic} -- {playload}\n')

    def on_message_direct_con_dev(self, client, userdata, message):
        get_log(self.log_path).debug(f"Received message:'{message.payload.decode()}' on topic:'{message.topic}'")
        method = json.loads(message.payload)['method']
        seq = json.loads(message.payload)['seq']
        module = json.loads(message.payload)['src']
        rsp_topic = f"lliot/receiver/{module}"
        if method == 'dmgr.notifyUnBind':
            rsp_playload = dmgr_notifyUnBind(self.args, module=module, seq=seq)['rsp']
        elif method == 'dmgr.checkBind':
            rsp_playload = dmgr_checkBind(self.args, module=module, seq=seq)['rsp']
        elif method == 'dmgr.readPIIDS':
            rsp_playload = dmgr_readPIIDS(self.args, module=module, seq=seq)['rsp']
        elif method == 'dmgr.ctrlFIIDS':
            rsp_playload = dmgr_ctrlFIIDS(self.args, module=module, seq=seq)['rsp']
        elif method == 'dmgr.writePIIDS':
            rsp_playload = dmgr_writePIIDS(self.args, module=module, seq=seq)['rsp']
        else:
            return
        self.publish(rsp_topic, str(rsp_playload))

    def connect(self):
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.broker_address)
        self.client.loop_start()

    def publish(self, topic, message, qos=0, retain=False):
        get_log(self.log_path).debug(f"Publish message:'{message}' on topic:'{topic}'")
        self.client.publish(topic, message, qos, retain)

    def subscribe(self, topic, qos=0):
        self.client.subscribe(topic, qos)

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)

    def start_loop(self):
        self.client.loop_start()

    def stop_loop(self):
        self.client.loop_stop()

    def disconnect(self):
        self.client.disconnect()


if __name__ == "__main__":
    username = "HA-CE-R31-001"
    password = hashlib.sha256('jhfeq6vsxonjjlfa'.encode('utf-8')).hexdigest()
    log_path = f"D:\\pwy_log\\Leelen-ATT\\conf_builder_test.txt"

    # 创建MQTT客户端
    mqtt_client = MQTTClient(log_path, "iottest.leelen.net", username=username, password=password,
                             client_id="12300001000000000001")

    # 连接到MQTT代理
    mqtt_client.connect()
    time.sleep(5)
    #
    # # 订阅主题
    # mqtt_client.subscribe("lliot/receiver/12300001000000000006")
    #
    # # 发布消息
    # payload = {
    #     "method": "dmgr.reg",
    #     "src": "12300001000000000008",
    #     "dst": "00000001000000000000",
    #     "version": "V1.0",
    #
    #     "params": {
    #         "did": "12300001000000000008",
    #         "softModel": "HA-CE-R31-001",
    #         "profileId": 7
    #     },
    #     "seq": 1
    #
    # }
    # mqtt_client.publish("lliot/receiver/00000001000000000000", str(payload))
    #
    # # 启动消息循环
    # mqtt_client.start_loop()
    #
    # # 等待一段时间以接收消息
    # input("Press Enter to exit...")
    #
    # # 停止消息循环
    # mqtt_client.stop_loop()

    # 断开连接
    # mqtt_client.disconnect()
