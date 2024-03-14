import json
import os
import socket
import ssl
import time
from cryptography.fernet import Fernet

from commons.variables import project_root


class TCPClient:
    def __init__(self, server_host, server_port):
        self.ssl_socket = None
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET：使用IPv4地址族  SOCK_STREAM：面向连接的TCP协议

    def connect(self):
        self.client_socket.connect((self.server_host, self.server_port))
        print(f"Connected to {self.server_host}:{self.server_port}")

    def send_data(self, message):
        self.client_socket.send(message)

    def receive_data(self, buffer_size=1024):
        data = self.client_socket.recv(buffer_size)
        return data.decode('utf-8')

    def send_ssl_data(self, message):
        # 客户端认证：ssl.Purpose.CLIENT_AUTH  服务端认证（默认）：ssl.Purpose.SERVER_AUTH
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        # 禁用证书验证
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        # 客户端验证服务端证书
        # cer_path = os.path.join(project_root, "template", "IOTLeelenCAroot.cer")
        # ssl_context.load_verify_locations(cafile=cer_path)
        self.ssl_socket = ssl_context.wrap_socket(self.client_socket, server_hostname=self.server_host)
        self.ssl_socket.sendall(message)
        print(f"发送字节串 : {message}")

    def receive_ssl_data(self, buffer_size=1024):
        if self.ssl_socket is not None:
            data = self.ssl_socket.recv(buffer_size)
        else:
            data = None
        return data.decode('utf-8')

    def close(self):
        self.client_socket.close()
        print("Connection closed")


if __name__ == '__main__':
    # Example of using the TCPClient class
    server_host = '192.168.1.100'
    server_port = 49853

    # Create and connect the client
    client = TCPClient(server_host, server_port)
    client.connect()

    time.sleep(2)

    # 生成 AES 密钥
    # key = Fernet.generate_key()
    # cipher = Fernet(key)

    # Send and receive data
    # bind_data = {"method": "bind", "seq": 1, "params": {"src": "0001200424140702c4f1", "dst": "0001200424140702c4f7",
    #                                                     "groupId": "1045263038358777856"}}
    # random_data = {"method": "random", "seq": 2,
    #                "params": {"src": "0001200424140702c4f1", "dst": "00012004241407770e3e"}}
    # heartbeat = {"method": "heartbeat", "seq": 37, "params": {"interval": 7}}
    # # bind_data_json = json.dumps(bind_data)
    # # encrypted_data = cipher.encrypt(bind_data_json.encode())
    # encrypted_data = json.dumps(heartbeat).encode()
    data = b'LEEL\x00\x00\x00\x7F\x00\x01\x00{"method":"bind","seq":1,"params":{"src":"0001200424140702c4f1","dst":"0001200424140702c4f7","groupId":"1045263038358777856"}}\x2E'
    # data = b'{"method":"bind","seq":1,"params":{"src":"0001200424140702c4f1","dst":"0001200424140702c4f7","groupId":"1045263038358777856"}}'
    # data = b'LEEL\x00\x00\x00\x44\x00\x01\x00{"method":"heartbeat","seq":37,"params":{"interval":7}}\xD3'
    # data = "4C 45 45 4C 00 00 00 7F 00 01 00 7B 22 6D 65 74 68 6F 64 22 3A 22 62 69 6E 64 22 2C 22 73 65 71 22 3A 31 2C 22 70 61 72 61 6D 73 22 3A 7B 22 73 72 63 22 3A 22 30 30 30 31 32 30 30 34 32 34 31 34 30 37 30 32 63 34 66 31 22 2C 22 64 73 74 22 3A 22 30 30 30 31 32 30 30 34 32 34 31 34 30 37 30 32 63 34 66 37 22 2C 22 67 72 6F 75 70 49 64 22 3A 22 31 30 34 35 32 36 33 30 33 38 33 35 38 37 37 38 35 36 22 7D 7D 2E"
    # data_bytes = bytes.fromhex(data)
    # print(f"预发送16进制码：{data}")
    client.send_ssl_data(data)
    # client.send_data(bind_data)

    # time.sleep(30)
    # data_received = client.receive_data()
    data_received = client.receive_ssl_data()
    print(f"Received data: {data_received}")

    # Close the connection
    client.close()
