import json
import time
from datetime import datetime
from commons.variables import *
import paho.mqtt.client as mqtt

from handlers.log_handler import get_log
from lib.mqtt.modules import dmgr_checkBind, dmgr_readPIIDS, dmgr_ctrlFIIDS, dmgr_writePIIDS, dmgr_notifyUnBind


class MQTTClient:
    """
    MQTT客户端操作
    """
    def __init__(self, log_path, broker_address, username=None, password=None, client_id="", tool="default", args=None):
        self.args = args
        self.log_path = log_path
        self.client = mqtt.Client(client_id)
        self.broker_address = broker_address
        self.username = username
        self.password = password
        self.messages = {}  # panwy240816新增：存储订阅的主题报文
        self.subscribed_topics = []  # panwy240809新增：存储订阅的主题

        # 设置回调函数
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect  # panwy240809新增：断开连接的回调
        if tool == 't2_led':
            self.client.on_message = self.on_message_t2_led
        elif tool == 'direct_con_dev':
            self.client.on_message = self.on_message_direct_con_dev
        elif tool == 'sensor_link_duration':
            self.client.on_message = self.on_message_sensor_link_duration
        else:
            self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        """
        连接操作
        :param client:
        :param userdata:
        :param flags:
        :param rc:
        """
        if rc == 0:
            get_log(self.log_path).debug(f"{self.username} connected to MQTT Broker -- {self.broker_address}")
            # 重连时重新订阅已订阅的主题
            for topic, qos in self.subscribed_topics:
                client.subscribe(topic, qos)
                get_log(self.log_path).debug(f"Re-subscribed to {topic} with QoS {qos}")
        else:
            get_log(self.log_path).debug(f"Connection failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """
        断开重连操作
        :param client:
        :param userdata:
        :param rc:
        """
        if rc != 0:
            get_log(self.log_path).debug(f"{self.username} unexpected disconnection. Reconnecting...")
            retries = 0
            while rc != 0 and retries < 5:
                retries += 1
                try:
                    get_log(self.log_path).debug(f"Attempting to reconnect, attempt {retries}/5")
                    rc = client.reconnect()
                    if rc == 0:
                        get_log(self.log_path).debug("Reconnected successfully.")
                        break
                except Exception as e:
                    get_log(self.log_path).debug(f"Reconnect attempt {retries} failed: {e}")
                time.sleep(30)
            if retries >= 5:
                get_log(self.log_path).debug("Max retries reached. Could not reconnect.")

    def on_message(self, client, userdata, message):
        """
        默认接收到信息操作
        :param client:
        :param userdata:
        :param message:
        """
        # 数据处理，去掉\t\n
        cleaned_mes = message.payload.decode().replace('\t', '').replace('\n', '')
        get_log(self.log_path).debug(f"Received message '{cleaned_mes}' on topic '{message.topic}'")
        if message.topic in self.messages:
            self.messages[message.topic].append(cleaned_mes)
        else:
            self.messages[message.topic] = [cleaned_mes]

    def on_message_sensor_link_duration(self, client, userdata, message):
        playload = str(message.payload).replace(" ", "")
        if "lliot/fiids_report" and '"fiid":49408,' in message.topic:
            get_log(self.log_path).debug(f"子设备上报状态：{message.topic}: {playload}")
            current_time = datetime.now()
            with open(f'{os.path.dirname(self.log_path)}\\fiids_report.txt', 'a') as file:
                file.write(f'{current_time} -- {message.topic} -- {playload}\n')
        else:
            get_log(self.log_path).debug(f"接收到报文：{message.topic}: {playload}")

    def on_message_t2_led(self, client, userdata, message):
        playload = str(message.payload).replace(" ", "")
        if self.args.场景 == '群组' or self.args.场景 == '手动场景':
            # 33106：执行群组  33031：执行场景  49408：面板开关--兼容集中式场景控制
            if message.topic == f'lliot/receiver/{self.args.Did}' and ('"fiid":33106,' in playload or '"fiid":33031,' in playload or '"fiid":49408,' in playload):
                current_time = datetime.now()
                with open(f'{os.path.dirname(self.log_path)}\\gw_control.txt', 'w') as file:
                    file.write(f'{current_time} -- {message.topic} -- {playload}')
                get_log(self.log_path).debug(f"网关接收群组/手动场景控制报文：{message.topic}: {playload}")
            elif "lliot/fiids_report" in message.topic:
                get_log(self.log_path).debug(f"子设备上报状态：{message.topic}: {playload}")
                current_time = datetime.now()
                with open(f'{os.path.dirname(self.log_path)}\\fiids_report.txt', 'a') as file:
                    file.write(f'{current_time} -- {message.topic} -- {playload}\n')
        else:
            if message.topic == f'lliot/receiver/{self.args.Did}' and '"fiid":49408,' in playload:
                current_time = datetime.now()
                with open(f'{os.path.dirname(self.log_path)}\\gw_control.txt', 'w') as file:
                    file.write(f'{current_time} -- {message.topic} -- {playload}')
                get_log(self.log_path).debug(f"网关接收开关控制报文：{message.topic}: {playload}")
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
        self.publish(rsp_topic, json.dumps(rsp_playload))

    def connect(self):
        """
        连接操作
        """
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.broker_address)
        self.client.loop_start()
        time.sleep(3)

    def publish(self, topic, message, qos=0, retain=False):
        """
        发布主题信息
        :param topic:
        :param message:
        :param qos:
        :param retain:
        """
        get_log(self.log_path).debug(f"Publish message:'{message}' on topic:'{topic}'")
        self.client.publish(topic, message, qos, retain)

    def subscribe(self, topic, qos=0):
        """
        订阅主题
        :param topic:
        :param qos:
        """
        self.subscribed_topics.append((topic, qos))  # 记录订阅的主题及其QoS
        self.client.subscribe(topic, qos)

    def unsubscribe(self, topic):
        """
        取消订阅
        :param topic:
        """
        self.client.unsubscribe(topic)

    def get_message(self):
        """
        获取订阅主题及其消息
        :return:
        """
        return self.messages

    def start_loop(self):
        """
        执行消息获取循环
        """
        self.client.loop_start()

    def stop_loop(self):
        """
        停止消息获取循环
        """
        self.client.loop_stop()

    def disconnect(self):
        """
        断开连接
        """
        self.client.disconnect()


if __name__ == "__main__":
    username = "HA-CE-R31-001:12300001000000000110"
    # password = hashlib.sha256('jhfeq6vsxonjjlfa'.encode('utf-8')).hexdigest()
    password = "a0090d1c49ce52b4bd600077d9abb9d16738f8187f2cb5de212837f2f1c550d5"
    log_path = f"D:\\pwy_log\\Leelen-ATT\\test.txt"

    # 创建MQTT客户端
    mqtt_client = MQTTClient(log_path, "iotpre.leelen.net", username=username, password=password,
                             client_id="12300001000000000110")

    # 连接到MQTT代理
    mqtt_client.connect()
    time.sleep(5)

    # 订阅主题
    mqtt_client.subscribe("lliot/fiids_report/0001201bbc026efffea7b98e/2")
    # time.sleep(600)
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

    # # 断开连接
    # print("断开")
    # mqtt_client.disconnect()
    # time.sleep(20)
    # # 连接到MQTT代理
    # print("重连")
    # mqtt_client.connect()
    # time.sleep(30)

