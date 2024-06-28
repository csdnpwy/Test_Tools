import json
import time

from selenium.common import UnexpectedAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from handlers.log_handler import get_log


class SeleniumWrapper:
    """
    selenium封装
    """

    def __init__(self, log_path, driver_path=None, browser='chrome'):
        if browser == 'chrome':
            if browser == 'chrome':
                chrome_options = Options()
                chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
                self.service = Service(driver_path) if driver_path else None
                self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
                self.driver.execute_cdp_cmd('Network.enable', {})
        else:
            raise ValueError(f"Unsupported browser: {browser}")
        self.log_path = log_path

    def open_url(self, url):
        """
        打开URL
        :param url:
        """
        try:
            self.driver.get(url)
        except UnexpectedAlertPresentException:
            # self.handle_alert()
            self.driver.execute_script("window.stop();")  # 停止当前页面加载
            self.driver.get(url)  # 重新打开 URL

    def find_element(self, by, value):
        """
        查找元素
        :param by:
        :param value:
        :return:
        """
        return self.driver.find_element(by, value)

    def click_element(self, by, value):
        """
        点击某元素
        :param by:
        :param value:
        """
        element = self.find_element(by, value)
        element.click()

    def send_keys(self, by, value, keys):
        """
        输入值
        :param by:
        :param value:
        :param keys:
        """
        element = self.find_element(by, value)
        element.send_keys(keys)

    def wait_for_element(self, by, value, timeout=10):
        """
        等待某元素出现
        :param by:
        :param value:
        :param timeout:
        """
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))

    def scroll_to_bottom(self):
        """
        使用 JavaScript 将滚动条滑动到页面底部
        """
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def refresh(self):
        """
        刷新页面
        """
        self.driver.refresh()

    def get_value(self, by, value):
        """
        获取值
        """
        element = self.find_element(by, value)
        res = element.get_attribute('value')
        return res

    def has_target_request(self, target_url):
        """
        检查目标请求是否已存在
        :param target_url:
        :return:
        """
        response = {"status": 0}
        logs = self.driver.get_log('performance')
        for entry in logs:
            log = json.loads(entry['message'])['message']
            if log['method'] == 'Network.responseReceived':
                response = log['params']['response']
                # print(response)
                if target_url in response['url']:
                    # print(f"==============")
                    get_log(self.log_path).debug(f'接收到{target_url}应答：\n{response}')
                    return True, response['status']
        return False, response['status']

    def check_response_status(self, by, value, target_url):
        """
        点击按钮并检查请求的返回状态码
        :param by:
        :param value:
        """
        status = 0
        self.click_element(by, value)
        # 等待一段时间以确保请求完成（这里可以根据具体情况调整等待时间）
        for i in range(0, 10):
            res, status = self.has_target_request(target_url)
            if res:
                break
            time.sleep(1)
        return status

    def handle_alert(self, action='accept', text=None):
        """
        处理弹窗
        :param action: 'accept' 接受弹窗, 'dismiss' 拒绝弹窗, 'get_text' 获取弹窗文本, 'send_keys' 输入文本到弹窗
        :param text: 在 action 为 'send_keys' 时，需要输入的文本
        """
        alert = self.driver.switch_to.alert
        if action == 'accept':
            alert.accept()
        elif action == 'dismiss':
            alert.dismiss()
        elif action == 'get_text':
            return alert.text
        elif action == 'send_keys' and text is not None:
            alert.send_keys(text)
            alert.accept()
        else:
            raise ValueError(f"Unsupported action: {action}")

    def close(self):
        """
        关闭浏览器
        """
        self.driver.quit()
