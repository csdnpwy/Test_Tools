import time

from ping3 import ping

from handlers.dingding_handler import dingding
from handlers.error_handler import CustomError
from handlers.global_handler import is_ping_successful
from handlers.log_handler import get_log
from handlers.mqtt_handler import MQTTClient
from handlers.pdu_handler import ctl_pdu
from handlers.serial_handler import SerialComm

log_path = "D:\\pwy_log\\Leelen-ATT\\幻彩灯带压测\\log.txt"
username = "HA-CE-R31-001"
did = "12300001000000000100"
password = "56ca0ac2c3b30091cc95b7d122b97f86a2f5c0be93eab3fe397825e3c6633b79"
subscribe_topic = "lliot/fiids_report/0001201becda3b136490/2"
expect_open = '{"fiid":49408,"value":{"onOff":1}}'
expect_down = '{"fiid":49408,"value":{"onOff":0}}'
check_ip = "10.58.2.11"
# 一机一密连接到MQTT代理
mqtt_client = MQTTClient(log_path, 'iottest.leelen.net', username=f"{username}:{did}", password=password, client_id=did)
mqtt_client.connect()
time.sleep(5)
mqtt_client.subscribe(subscribe_topic)
time.sleep(1)
# 两线网关串口执行reboot
serial1 = SerialComm(log_path, 'COM11', baudrate=115200)
serial1.open()
time.sleep(2)
for i in range(0, 5000):
    num = i + 1
    # 按键自定义控制开
    mqtt_client.clean_message()
    get_log(log_path).info(f"   ---   第{num}次进行控制按键自定义开")
    ctl_pdu('10.58.51.144', ctl='close')
    ctl_pdu('10.58.51.144')
    # mqtt监听是否收到控制报文
    time.sleep(5)
    mes = mqtt_client.get_message().get(subscribe_topic, None)
    get_log(log_path).debug(f"{mes}")
    if expect_open in str(mes):
        get_log(log_path).info(f"      ---      监听幻彩灯带mqtt上报开状态报文正常")
    else:
        get_log(log_path).error(f"      !!!      监听幻彩灯带mqtt上报开状态报文异常")
        err_info = f"第{num}次进行控制按键自定义开幻彩灯带失败！"
        dingding("error", err_info)
        raise CustomError("测试异常！")
    # 网关reboot
    get_log(log_path).info(f"   ---   网关reboot")
    serial1.send_data('reboot\n'.encode('utf-8'))
    time.sleep(2)
    for t in range(0, 12):
        ping_res = ping(check_ip)
        get_log(log_path).debug(f'      ---      Ping ip: {check_ip} Res: {ping_res}')
        if is_ping_successful(ping_res):
            get_log(log_path).info(f'      ---      {check_ip}已上电')
            time.sleep(25)
            break
        else:
            get_log(log_path).debug(f'      ---      {(t + 1) * 5}S内还未上电，继续等待...')
            time.sleep(5)
            if i == 11:
                get_log(log_path).error(f'      !!!       60S内上电失败')
                err_info = f"60S内网关无法ping通"
                dingding("error", err_info)
                raise CustomError("测试异常！")
    # 按键自定义控制关
    mqtt_client.clean_message()
    get_log(log_path).info(f"   ---   第{num}次进行控制按键自定义关")
    ctl_pdu('10.58.51.144', ctl='close')
    ctl_pdu('10.58.51.144')
    # mqtt监听是否收到控制报文
    time.sleep(5)
    mes = mqtt_client.get_message().get(subscribe_topic, None)
    get_log(log_path).debug(f"{mes}")
    if expect_down in str(mes):
        get_log(log_path).info(f"      ---      监听幻彩灯带mqtt上报关状态报文正常")
    else:
        get_log(log_path).error(f"      !!!      监听幻彩灯带mqtt上报关状态报文异常")
        err_info = f"第{num}次进行控制按键自定义关幻彩灯带失败！"
        dingding("error", err_info)
        raise CustomError("测试异常！")
    # 网关reboot
    get_log(log_path).info(f"   ---   网关reboot")
    serial1.send_data('reboot\n'.encode('utf-8'))
    time.sleep(2)
    for t in range(0, 12):
        ping_res = ping(check_ip)
        get_log(log_path).debug(f'      ---      Ping ip: {check_ip} Res: {ping_res}')
        if is_ping_successful(ping_res):
            get_log(log_path).info(f'      ---      {check_ip}已上电')
            time.sleep(25)
            break
        else:
            get_log(log_path).debug(f'      ---      {(t + 1) * 5}S内还未上电，继续等待...')
            time.sleep(5)
            if i == 11:
                get_log(log_path).error(f'      !!!       60S内上电失败')
                err_info = f"60S内网关无法ping通"
                dingding("error", err_info)
                raise CustomError("测试异常！")
    # 进度汇报
    if num == 1:
        dingding("info", f"幻彩灯带压测开始")
    if num % 100 == 0:
        dingding("info", f"幻彩灯带压测已经执行{num}次")
mqtt_client.disconnect()
