import select
import socket
import ssl
import time

from handlers.data_encrypt_handler import aes_decrypt
from handlers.log_handler import get_log


class TCPClient:
    def __init__(self, log_path, server_host, server_port, timeout=5, type='tcp'):
        self.log_path = log_path
        self.timeout = timeout
        self.ssl_socket = None
        self.server_host = server_host
        self.server_port = server_port
        # AF_INET：使用IPv4地址族  SOCK_STREAM：面向连接的TCP协议
        if type == 'udp':
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(self.timeout)

    def connect(self):
        self.client_socket.connect((self.server_host, self.server_port))
        # print(f"Connected to {self.server_host}:{self.server_port}")

    def send_data(self, message):
        self.client_socket.send(message)

    def receive_data(self, buffer_size=1024):
        data = self.client_socket.recv(buffer_size)
        return data

    def clear_buff(self, buffer_size=1024):
        """
        清理缓冲区
        :param buffer_size:
        """
        try:
            self.client_socket.settimeout(self.timeout)
            self.client_socket.setblocking(False)
            while True:
                ready_socket = select.select([self.client_socket], [], [], 0.1)
                if ready_socket and ready_socket[0]:
                    continue_cmd_recv = self.client_socket.recv(buffer_size)
                    # print(f"清理{continue_cmd_recv}")
                    # 执行数据处理，丢弃也好，使用也好，按照业务处理
                else:
                    # print(f"已没有缓存数据需要清理！")
                    break
        except:
            raise
        finally:
            self.client_socket.setblocking(True)
            self.client_socket.settimeout(self.timeout)

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
        get_log(self.log_path).debug(f"发送ssl数据 {message}")
        time.sleep(1)

    def receive_ssl_data(self, buffer_size=1024, max_attempts=5, password=None):
        """
                接收ssl回复数据
                :param password:
                :param max_attempts:
                :param buffer_size:
                :return:
                """
        receive_payload = []
        if self.ssl_socket is not None:
            # 设置套接字为非阻塞模式
            self.ssl_socket.setblocking(False)
            attempts = 0
            while attempts < max_attempts:
                try:
                    data = self.ssl_socket.recv(buffer_size)
                    payload_hex = ''.join(format(byte, '02x') for byte in data)[22:-2]
                    if password is None:
                        payload = bytes.fromhex(payload_hex).decode('utf-8')
                    else:
                        payload = aes_decrypt(payload_hex, password)
                    receive_payload.append(payload)
                    if not data:
                        break
                except ssl.SSLWantReadError:
                    # 捕获 SSLWantReadError 异常，继续循环
                    attempts += 1
                    continue
                except BlockingIOError:
                    break
            # 恢复套接字为阻塞模式
            self.ssl_socket.setblocking(True)
            self.ssl_socket.settimeout(self.timeout)
        else:
            pass
        get_log(self.log_path).debug(f"接收到ssl数据 {receive_payload}")
        return receive_payload

    def clear_ssl_buff(self, buffer_size=1024, max_attempts=5):
        """
        清理ssl连接缓冲区
        :param max_attempts:
        :param buffer_size:
        """
        # 设置套接字为非阻塞模式
        self.ssl_socket.setblocking(False)
        attempts = 0
        while attempts < max_attempts:
            try:
                data = self.ssl_socket.recv(buffer_size)
                if not data:
                    break
            except ssl.SSLWantReadError:
                # 捕获 SSLWantReadError 异常，继续循环
                attempts += 1
                continue
            except BlockingIOError:
                break
        # 恢复套接字为阻塞模式
        self.ssl_socket.setblocking(True)
        self.ssl_socket.settimeout(self.timeout)

    def close(self):
        """
        关闭连接
        """
        self.client_socket.close()
        # print("Connection closed")
