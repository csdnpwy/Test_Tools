from bleak import BleakScanner, BleakClient

from handlers.data_encrypt_handler import hex_checksum
from handlers.log_handler import get_log


class BleDevice:
    def __init__(self, address):
        self.address = address
        self.client = BleakClient(address)

    async def connect(self):
        await self.client.connect()

    async def disconnect(self):
        await self.client.disconnect()

    async def get_services_and_characteristics(self):
        if self.client:
            return self.client.services
        else:
            print("Not connected to any device")

    async def read_characteristic(self, service_uuid, characteristic_uuid):
        value = await self.client.read_gatt_char(characteristic_uuid)
        return value

    async def write_to_characteristic(self, service_uuid, characteristic_uuid, data):
        await self.client.write_gatt_char(characteristic_uuid, data)

    async def subscribe_to_notifications(self, service_uuid, characteristic_uuid, callback):
        async def handle_notification(sender, data):
            callback(sender, data)

        await self.client.start_notify(characteristic_uuid, handle_notification)

    async def scan_devices(self):
        devices = await BleakScanner.discover()
        return devices

# 灯带蓝牙连接
async def light_strip_bluetooth_connection(args, token, log_path):
    # 扫描设备
    device_address = None
    devices = await BleakScanner.discover()
    for device in devices:
        if device.name == args.SN:
            get_log(log_path).info(f" --- 发现欲连接设备蓝牙：{device}")
            device_address = device.address
            break
    # 连接设备
    if device_address:
        device = BleDevice(device_address)
        get_log(log_path).info(f" --- 连接设备蓝牙")
        await device.connect()
        # 获取蓝牙服务id和特性id
        services = await device.get_services_and_characteristics()
        for service in services:
            get_log(log_path).debug(f"Service UUID:{service.uuid}")
            for char in service.characteristics:
                get_log(log_path).debug(f"  Characteristic UUID:{char.uuid}")
        # 读取特性值
        service_uuid = "0000f000-123c-9510-5895-1e818d1d8ee9"
        characteristic_uuid = "0000f001-123c-9510-5895-1e818d1d8ee9"
        # value = await device.read_characteristic(service_uuid, characteristic_uuid)
        # print("Characteristic value:", value)
        # 写入数据
        hex_data_begin = "fe"
        hex_data_protocol_info = "00"
        hex_data_seq = "07"
        hex_data_func = "02"
        hex_data_cont = f'{{"ssid":"{args.wifi名称}","passwd":"{args.wifi密码}","token":"{token}","encryption":0}}'.encode().hex()
        data_len = hex(int(len(bytes.fromhex(hex_data_cont).decode('utf-8'))) + 7)[2:].zfill(4)
        hex_data = f"{hex_data_begin}{hex_data_protocol_info}{data_len}{hex_data_seq}{hex_data_func}{hex_data_cont}"
        sum_data = hex_checksum(hex_data)
        data_to_write = hex_data + str(sum_data)
        # print(bytes.fromhex(data_to_write))
        get_log(log_path).info(f" --- 发送配网请求")
        await device.write_to_characteristic(service_uuid, characteristic_uuid, bytes.fromhex(data_to_write))
        # # 订阅通知
        # async def handle_notification(sender, data):
        #     print(f"Notification from {sender}: {data}")
        #
        # await device.subscribe_to_notifications(service_uuid, characteristic_uuid, handle_notification)
        #
        # 断开连接
        await device.disconnect()

    else:
        get_log(log_path).error(f" !!! 未发现欲连接设备蓝牙")


if __name__ == '__main__':
    pass

