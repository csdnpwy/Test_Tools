import time

from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser
import socket


class MDNSManager:
    def __init__(self, service_type, service_name, port, properties=None):
        self.service_type = service_type
        self.service_name = service_name
        self.port = port
        self.properties = properties or {}
        self.service_info = None
        self.zeroconf = Zeroconf()

    def register_service(self):
        self.service_info = ServiceInfo(
            self.service_type,
            self.service_name,
            addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
            # addresses=[socket.inet_aton("192.168.1.100")],
            port=self.port,
            properties=self.properties,
        )
        print(f"本机IP：{socket.gethostbyname(socket.gethostname())}")
        self.zeroconf.register_service(self.service_info)

    def unregister_service(self):
        if self.service_info:
            self.zeroconf.unregister_service(self.service_info)
            self.zeroconf.close()

    def discover_services(self, listener):
        browser = ServiceBrowser(self.zeroconf, self.service_type, listener)


if __name__ == "__main__":
    # 定义服务类型、服务名、端口和属性
    service_type = "_iot-gateway._tcp.local."
    service_name = "0001200424140702c4f1._iot-gateway._tcp.local."
    port = 49853
    properties = {
        "fb": "LV20",
        "bd": "EC2E0AD2305CC056FC6975664896CFE8",
        "mac": "24140702c4f1",
        "md": "HAZB-CE-R15-112",
        "smd": "HAZB-CE-R15-112",
        "mf": "LEELEN",
        "sn": "031525E019000073",
        "role": "standby",
        "ver": "2.41",
        "autoSiid": "3",
        "wt": "-10.000000"
    }

    # 创建MDNSManager实例
    mdns_manager = MDNSManager(service_type, service_name, port, properties)

    try:
        # 注册服务
        mdns_manager.register_service()

        time.sleep(5)


        # 发现服务的监听器
        class MyListener:
            def __init__(self, local_name):
                self.local_name = local_name

            def remove_service(self, zeroconf, type, name):
                print(f"Service {name} removed")

            def add_service(self, zeroconf, type, name):
                info = zeroconf.get_service_info(type, name)
                IP = info.parsed_addresses()[0]
                if name == self.local_name:
                    # print(f"Local Service: {name} , service info: {info}")
                    print(f"Local Service: {name} IP: {IP} Port: {port}, service info: {info}")
                else:
                    # print(f"Other Service: {name} , service info: {info}")
                    print(f"Other Service: {name} IP: {IP} Port: {port}, service info: {info}")

            def update_service(self, zeroconf, type, name):
                pass
                # info = zeroconf.get_service_info(type, name)
                # print(f"发现服务：{name}, 服务信息：{info}")


        listener = MyListener(service_name)

        # 发现服务
        mdns_manager.discover_services(listener)

        time.sleep(10)

        # input("Press enter to unregister...\n\n")
    finally:
        # 注销服务
        mdns_manager.unregister_service()
