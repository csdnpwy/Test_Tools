import random
import select
import socket
import ssl
import threading
import time

from handlers.csv_handler import CSVHandler
from handlers.data_encrypt_handler import aes_decrypt
from handlers.global_handler import extract_between, hex_to_custom_decimals, custom_decimals_to_hex
from handlers.log_handler import get_log


class TCPClient:
    def __init__(self, log_path, server_host, server_port, timeout=5, protocol='tcp'):
        self.log_path = log_path
        self.timeout = timeout
        self.ssl_socket = None
        self.protocol = protocol
        self.server_host = server_host
        self.server_port = server_port
        # AF_INET：使用IPv4地址族  SOCK_STREAM：面向连接的TCP协议
        if self.protocol == 'udp':
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
        """
        接收数据
        :param buffer_size:
        :return:
        """
        try:
            data = self.client_socket.recv(buffer_size)
            return data
        except socket.timeout:
            return None

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

    def process_tcp_message(self, message):
        """
        处理TCP消息，供子类重写
        :param message: 接收到的TCP消息
        """
        print(f"接收到TCP信息：{message.hex()}")

    def process_udp_message(self, message):
        """
        处理UDP消息，供子类重写
        :param message: 接收到的UDP消息
        """
        print(f"接收到UDP信息：{message.hex()}")

    def start(self):
        """
        启动客户端并监听消息
        """
        try:
            self.connect()
            print("开始监听消息...")
            while True:
                if isinstance(self.client_socket, ssl.SSLSocket):
                    data = self.receive_ssl_data()
                else:
                    data = self.receive_data()
                if data:
                    if self.protocol == "udp":
                        self.process_udp_message(data)
                    else:
                        self.process_tcp_message(data)
        except Exception as e:
            print(f"Error handling mess : {e}")
        finally:
            try:
                self.close()
            except Exception as e:
                print(f"Error closing client socket : {e}")

    def close(self):
        """
        关闭连接
        """
        self.client_socket.close()
        # print("Connection closed")


class KNXIpClient(TCPClient):
    """
    knx ip模块客户端
    """

    def __init__(self, log_path, server_host, server_port=3671, timeout=5, protocol='udp', args=None):
        super().__init__(log_path, server_host, server_port=server_port, timeout=timeout, protocol=protocol)
        self.stauts_req = None
        self.channel_no = None
        self.sid = -1
        self.args = args
        self.csv_handler = CSVHandler(self.args.Path)
        self.report_threads = []  # 存储所有定时上报的线程

    def get_sid(self):
        """
        回复报文获取sid
        """
        if self.sid == 255:
            self.sid = 0
        else:
            self.sid += 1
        res = hex(self.sid)[2:].zfill(2).upper()
        return res

    def schedule_device_status_report(self):
        """
        根据 CSV 配置文件定时上报非控制类设备的状态
        """
        devices = self.csv_handler.read_all()
        for device in devices:
            rate = device.get("Rate", "")
            if rate.isdigit():
                interval = int(rate)
                thread = threading.Thread(target=self._report_status, args=(device, interval), daemon=True)
                thread.start()
                self.report_threads.append(thread)

    def _report_status(self, device, interval):
        """
        按间隔定时上报设备状态
        :param device: 设备信息字典
        :param interval: 上报间隔（秒）
        """
        address = device.get("Address", "")
        group_name = device.get("Group name", "")
        while True:
            if 'ENV_环境检测仪_STA_TP' in group_name:
                random_number = random.randint(0, 255)
                hex_number = f"{random_number:02X}"
                status = f'0300800C{hex_number}'  # 温度
                sta_len = '17'
            elif 'ENV_环境检测仪_STA_AH' in group_name:
                random_number = random.randint(0, 255)
                hex_number = f"{random_number:02X}"
                status = f'03008014{hex_number}'  # 湿度
                sta_len = '17'
            elif 'ENV_环境检测仪_STA_PM25' in group_name:
                random_number = random.randint(0, 255)
                hex_number = f"{random_number:02X}"
                status = f'03008000{hex_number}'  # PM2.5
                sta_len = '17'
            elif 'MS_移动照度_STA_SW' in group_name:
                random_number = random.randint(0, 1)
                status = f'01008{random_number}'  # 有无人
                sta_len = '15'
            elif 'MS_移动照度_STA_LUX' in group_name:
                random_number = random.randint(0, 255)
                hex_number = f"{random_number:02X}"
                status = f'03008007{hex_number}'  # 光照度
                sta_len = '17'
            else:
                status = None
                sta_len = None
            try:
                seq = self.get_sid()
                destination = custom_decimals_to_hex(address)
                status_message = f"0610042000{sta_len}04{self.channel_no}{seq}001100BCE00000{destination}{status}"  # 状态报文
                self.send_data(bytes.fromhex(status_message))
                get_log(self.log_path).info(f"非控制类设备状态上报: Group={group_name}, Address={address}, Message={status_message}")
            except Exception as e:
                get_log(self.log_path).error(f"设非控制类设备状态上报出错: Group={group_name}, Error={e}")
            time.sleep(interval)

    def process_udp_message(self, message):
        """
        重写对udp信息的处理函数
        :param message:
        """
        message = message.hex().upper()
        get_log(self.log_path).info(f"接收到UDP消息：{message}")
        if message.startswith("061002060014"):  # 连接knxip设备服务器响应
            self.channel_no = extract_between(message, "061002060014", length=2)[-1].strip()
            self.stauts_req = f"061002070010{self.channel_no}000801000000000000".upper()
            self.send_data(bytes.fromhex(self.stauts_req))
            get_log(self.log_path).info(f"发送连接状态请求：{self.stauts_req}")
        elif message.startswith("0610042000"):  # 总线报文格式
            sid = message[16:18]
            default_rsp = f"06100421000a04{self.channel_no}{sid}00"
            self.send_data(bytes.fromhex(default_rsp))
            get_log(self.log_path).info(f"   ---   默认回复：{default_rsp}")
            servercode = message[20:22]
            if servercode == '29':  # server端透传总线上报文
                # 状态回复
                address = hex_to_custom_decimals(message[32:36])  # 目标地址解析
                csv_row = self.csv_handler.find_by_column('Address', address)
                if csv_row:
                    group_name = csv_row['Group name']
                    if "_SC_" in group_name:  # 场景控制
                        sc_id = message[-1]
                        subaddr_list = csv_row['SCSubAddr'].split('-')
                        if sc_id == '0':  # 对应210_SC_卧室睡眠_CTL_1，关灯操作
                            end = "80"
                        else:  # 对应211_SC_卧室起床_CTL_2，开灯灯操作
                            end = "81"
                        for subassr in subaddr_list:
                            destination = custom_decimals_to_hex(subassr)
                            seq = self.get_sid()
                            status_rsp = message[:16] + seq + "001100BCE00000" + destination + f"0100{end}"
                            self.send_data(bytes.fromhex(status_rsp))
                            get_log(self.log_path).info(f"   ---   场景子设备状态回复：{status_rsp}")
                    else:  # 单控
                        status_row = self.csv_handler.find_by_column('Group name', group_name.replace('CTL', 'STA'))
                        if status_row:
                            seq = self.get_sid()
                            status_address = status_row['Address']
                            destination = custom_decimals_to_hex(status_address)
                            status_rsp = message[:16] + seq + "001100BCE00000" + destination + message[36:]
                            self.send_data(bytes.fromhex(status_rsp))
                            get_log(self.log_path).info(f"   ---   状态回复：{status_rsp}")
        elif message.startswith("0610020900"):  # 断开连接
            get_log(self.log_path).error(f"   !!!!!!   连接已被KNXIP主动断开   !!!!!!")
            exit()
        else:
            pass

    def connect_knxip_server(self):
        """
        发起连接请求
        """
        req_0205 = "06100205001a0801000000000000080100000000000004040200".upper()
        self.send_data(bytes.fromhex(req_0205))
        get_log(self.log_path).info(f"发送连接请求：{req_0205}")

    def connection_status_request(self):
        """
        定时发送状态请求
        """
        while True:
            self.send_data(bytes.fromhex(self.stauts_req))
            get_log(self.log_path).info(f"发送心跳数据：{self.stauts_req}")
            time.sleep(60)
