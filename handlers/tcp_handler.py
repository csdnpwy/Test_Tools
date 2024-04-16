import json
import re
import socket
import ssl
import time

from handlers.crc_handler import calc_crc8
from handlers.data_encrypt_handler import hmac_encode


class TCPClient:
    def __init__(self, server_host, server_port):
        self.ssl_socket = None
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET,
                                           socket.SOCK_STREAM)  # AF_INET：使用IPv4地址族  SOCK_STREAM：面向连接的TCP协议

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
        if self.ssl_socket is None:
            self.ssl_socket = ssl_context.wrap_socket(self.client_socket, server_hostname=self.server_host)
        self.ssl_socket.sendall(message)
        print(f"发送字节串 : {message}")

    def receive_ssl_data(self, buffer_size=1024):
        if self.ssl_socket is not None:
            data = self.ssl_socket.recv(buffer_size)
        else:
            data = None
        return data

    def close(self):
        self.client_socket.close()
        print("Connection closed")


if __name__ == '__main__':
    random = None
    # Example of using the TCPClient class
    server_host = '192.168.1.100'
    server_port = 49853

    # Create and connect the client
    client = TCPClient(server_host, server_port)
    client.connect()

    # time.sleep(2)

    # 生成 AES 密钥
    # key = Fernet.generate_key()
    # cipher = Fernet(key)

    # bind
    head = 'LEEL'.encode().hex()
    payload = '{"method":"bind","seq":1,"params":{"src":"0001200424140702c4f1","dst":"0001200424140702c4f7","groupId":"1059608211919732902"}}'.encode().hex()
    lenth = format(int(len(bytes.fromhex(payload).decode('utf-8'))) + 4, '02x')
    padding = 8 - len(lenth)
    lenth = lenth + '0' * padding
    version = "0001"
    encryption = "00"
    data = f'{head}{lenth}{version}{encryption}{payload}'
    byte_list = bytes.fromhex(data)
    data = data + calc_crc8(byte_list)
    print(f"预发送16进制码：{data}")
    client.send_ssl_data(bytes.fromhex(data))
    data_received = client.receive_ssl_data()
    print(f"Received data: {data_received}")
    # random
    head = 'LEEL'.encode().hex()
    payload = '{"method":"random","seq":2,"params":{"src":"0001200424140702c4f1","dst":"0001200424140702c4f7"}}'.encode().hex()
    lenth = format(int(len(bytes.fromhex(payload).decode('utf-8'))) + 4, '02x')
    padding = 8 - len(lenth)
    lenth = lenth + '0' * padding
    version = "0001"
    encryption = "00"
    data = f'{head}{lenth}{version}{encryption}{payload}'
    byte_list = bytes.fromhex(data)
    data = data + calc_crc8(byte_list)
    print(f"预发送16进制码：{data}")
    print(type(data))
    client.send_ssl_data(bytes.fromhex(data))
    data_received = client.receive_ssl_data()
    print(f"Received data: {data_received}")
    # 提取random
    json_data_match = re.search(b'\{.*\}', data_received)
    if json_data_match:
        json_data = json.loads(json_data_match.group(0).decode('utf-8'))
        random = json_data['params']['random']
    # login
    head = 'LEEL'.encode().hex()
    key_random = '@9jHaGa]' + random
    groupId = "1059608211919732902"
    password = hmac_encode("md5", key_random, groupId).upper()
    payload = f'{{"method":"login","seq":3,"params":{{"src":"0001200424140702c4f1","dst":"0001200424140702c4f7","username":"{groupId}","password":"{password}"}}}}'.encode().hex()
    lenth = format(int(len(bytes.fromhex(payload).decode('utf-8'))) + 4, '02x')
    padding = 8 - len(lenth)
    lenth = lenth + '0' * padding
    version = "0001"
    encryption = "00"
    data = f'{head}{lenth}{version}{encryption}{payload}'
    byte_list = bytes.fromhex(data)
    data = data + calc_crc8(byte_list)
    print(f"预发送16进制码：{data}")
    client.send_ssl_data(bytes.fromhex(data))
    data_received = client.receive_ssl_data()
    print(f"Received data: {data_received}")
    # heartbeat
    for i in range(1, 11):
        head = 'LEEL'.encode().hex()
        payload = '{"method":"heartbeat","seq":37,"params":{"interval":7}}'.encode().hex()
        lenth = format(int(len(bytes.fromhex(payload).decode('utf-8'))) + 4, '02x')
        padding = 8 - len(lenth)
        lenth = lenth + '0' * padding
        version = "0001"
        encryption = "00"
        data = f'{head}{lenth}{version}{encryption}{payload}'
        byte_list = bytes.fromhex(data)
        data = data + calc_crc8(byte_list)
        print(f"预发送16进制码：{data}")
        client.send_ssl_data(bytes.fromhex(data))
        data_received = client.receive_ssl_data()
        print(f"Received data: {data_received}")
        time.sleep(7)

    # Close the connection
    client.close()
