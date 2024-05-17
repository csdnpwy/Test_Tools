from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

class SeleniumWrapper:
    """
    selenium封装
    """
    def __init__(self, driver_path=None, browser='chrome'):
        if browser == 'chrome':
            if driver_path:
                self.service = Service(driver_path)
            self.driver = webdriver.Chrome(service=self.service)
        else:
            raise ValueError(f"Unsupported browser: {browser}")

    def open_url(self, url):
        """
        打开URL
        :param url:
        """
        self.driver.get(url)

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

    def close(self):
        """
        关闭浏览器
        """
        self.driver.quit()
