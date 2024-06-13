import time

import serial
import threading

from handlers.log_handler import get_log


class SerialComm:
    """
    串口通信处理方法
    """
    def __init__(self, log_path, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.receive_thread = None
        self.running = False
        self.log_path = log_path

    def open(self):
        """
        打开串口
        """
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_data)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            get_log(self.log_path).debug(f"Opened serial port {self.port} at {self.baudrate} baud")
        except serial.SerialException as e:
            get_log(self.log_path).debug(f"Error opening serial port: {e}")

    def close(self):
        """
        关闭串口
        """
        self.running = False
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join()
        if self.ser:
            self.ser.close()
            get_log(self.log_path).debug(f"Closed serial port {self.port}")

    def send_data(self, data):
        """
        发送数据
        :param data:
        """
        if self.ser and self.ser.is_open:
            self.ser.write(data)
            get_log(self.log_path).debug(f"Data sent: {data}")
        else:
            get_log(self.log_path).debug("Serial port is not open")

    def _receive_data(self):
        while self.running:
            if self.ser and self.ser.in_waiting > 0:
                data = self.ser.readline().hex()
                if data:
                    self.handle_received_data(data)

    def handle_received_data(self, data):
        """
        数据处理
        :param data:
        """
        """Override this method to handle received data"""
        print(time.time())
        get_log(self.log_path).info(f"Data received: {data}")


if __name__ == '__main__':
    log_path = "D:\\pwy_log\\Leelen-ATT\\test.txt"
    open_data = "550001000a010406184A0A00001801D05C"
    down_data = "550001000a010406184B0A00001800104D"
    status_data = "5500030200D96C"
    serial1 = SerialComm(log_path, 'COM7')
    serial2 = SerialComm(log_path, 'COM3')
    serial1.open()
    serial2.open()
    time.sleep(2)
    for i in range(0, 6):
        get_log(log_path).info(f"第{i+1}次触发有人状态")
        serial1.send_data(bytes.fromhex(open_data))
        time.sleep(10)
        get_log(log_path).info(f"第{i + 1}次触发无人状态")
        serial1.send_data(bytes.fromhex(down_data))
        time.sleep(10)
    serial1.close()
    serial2.close()
