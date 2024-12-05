import time
from datetime import datetime

import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab

from handlers.app_handler import app_request
from handlers.log_handler import get_log
from handlers.serial_handler import SerialComm

accesstoken = "4888bb1dea33f0730598bffe4e76d80070b049925d4c96c8de49b5d8ab0356f9"
url = "https://oapi.dingtalk.com/robot/send?access_token=4888bb1dea33f0730598bffe4e76d80070b049925d4c96c8de49b5d8ab0356f9"
log_path = "D:\\pwy_log\\Leelen-ATT\\hotel\\log.txt"
press01 = "01050000FF008C3A"
press02 = "010500000000CDCA"
modul1_status = '0102000000187800'
modul1_open_status = "0102033f8c01ed42"
modul1_down_status = "010203000000784e"
modul2_status = '01020000000F380E'
modul2_open_status = "0102020f00bc48"
modul2_down_status = "0102020000b9b8"
# 模块1串口
serial1 = SerialComm(log_path, 'COM4')
serial1.open()
time.sleep(2)
for i in range(0, 10000):
    scene_res = True
    get_log(log_path).info(f"第{i+1}次触发场景")
    serial1.send_data(bytes.fromhex(press01))
    time.sleep(0.3)
    serial1.send_data(bytes.fromhex(press02))
    time.sleep(2)
    # 判断开场景还是关场景
    serial1.send_data(bytes.fromhex(modul1_status))
    time.sleep(2)
    res = serial1.get_received_data()[-1]
    scene = res[10:12]
    if scene == "01":
        modul1_sta = modul1_open_status
        light_num = 23
    else:
        modul1_sta = modul1_down_status
        light_num = 0
    get_log(log_path).info(f"   ---   此次控制场景--{scene}")
    get_log(log_path).debug(f"模块1状态：{str(res)}")
    if modul1_sta in str(res):
        get_log(log_path).info(f"      ---      模块1状态正常")
    else:
        scene_res = False
        get_log(log_path).error(f"      !!!      模块1状态异常")
    get_log(log_path).info(f"   ---   查看筒射灯状态")
    # 点击屏幕规避浏览器自动退出
    pyautogui.click(50, 50)
    # 截屏并将其转换为 OpenCV 图像格式
    screenshot = ImageGrab.grab()  # 截屏，返回PIL格式图像
    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)  # 转换为OpenCV格式
    # 获取图像的高度和宽度
    height, width = image.shape[:2]
    image = image[:int(height * 0.8), :int(width * 0.3)]  # 左半部分并裁掉下边五分之一
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 应用高斯模糊以平滑图像（减少噪声）
    # 如果灯光周围噪声较多，可以尝试增大核大小为 (7, 7) 或 (9, 9)。
    # 如果灯光形状较小，核大小太大会模糊掉细节，建议减小为 (3, 3)。
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # 二值化处理，将图像转换为黑白,区分亮灯与背景
    # 200：阈值，像素值高于 200 设为 255（白），低于 200 设为 0（黑）,如果灯光较暗，可以降低阈值（如 150）。
    # 255：最大值，二值化后亮的部分为 255。
    _, binary = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
    # 寻找轮廓
    # cv2.RETR_EXTERNAL：只检测外轮廓（忽略嵌套的内轮廓）。
    # cv2.CHAIN_APPROX_SIMPLE：使用简单的方式压缩轮廓点（减少数据量）。
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 按大小过滤轮廓（避免误识别）
    # cv2.contourArea(cnt)：计算轮廓的面积。
    # > 10：保留面积大于 10 的轮廓。
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 10]
    # 判断是否存在24个灯亮
    if len(filtered_contours) != light_num:
        scene_res = False
        error = f"筒射灯状态异常：自动保存截图！"
        get_log(log_path).error(f"      !!!      {error}")
        result_text = f"本次操作场景--{scene}"
        # 存储灯的亮度状态
        # lights_status = []
        # 遍历每个轮廓，提取灯的亮度
        for contour in filtered_contours:
            # 获取轮廓的外接矩形
            x, y, w, h = cv2.boundingRect(contour)
            # 进一步筛选（限制灯的合理高度和宽度范围）
            # w：轮廓的宽度。
            # h：轮廓的高度。
            # 5：最小宽度 / 高度，过滤掉非常小的噪声。
            # 50：最大宽度 / 高度，排除异常的大区域。
            if 5 < w < 50 and 5 < h < 50:
                # 计算该区域的平均亮度
                roi = gray[y:y + h, x:x + w]
                mean_brightness = cv2.mean(roi)[0]
                # 判断灯是亮（亮度高）还是灭（亮度低）
                # 180：亮度阈值，大于该值认为灯是亮的。
                # lights_status.append(mean_brightness > 180)
                # 在图像上绘制矩形（可视化）
                color = (0, 255, 0) if mean_brightness > 180 else (0, 0, 255)
                cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

        # 显示结果
        cv2.putText(image, result_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        # 保存并显示输出图像
        img_time = datetime.now().strftime('%Y%m%d%H%M%S')
        output_path = f"D:\\pwy_log\\Leelen-ATT\\hotel\\{img_time}.png"
        cv2.imwrite(output_path, image)
    else:
        get_log(log_path).info(f"      ---      筒射灯状态正常")
    if not scene_res:
        get_log(log_path).error(f"      !!!      第{i+1}次场景控制失败")
        now = datetime.now()
        data = {
            "at": {
                "isAtAll": "false",
                "atUserIds": ["user001", "user002"],
                "atMobiles": ["17759212103"]
            },
            "text": {
                "content": f"error: 第{i+1}次场景控制失败--{now}"
            },
            "msgtype": "text",
            "actionCard": {
                "hideAvatar": "1",
                "btnOrientation": "1",
                "singleTitle": "1",
                "btns": [{
                    "actionURL": "1",
                    "title": "1"
                }],
                "text": "1",
                "singleURL": "1",
                "title": "1"
            }
        }
        app_request(accesstoken, url, data, log_path)
    time.sleep(3)
    get_log(log_path).debug(f"*********************************************************************************************")
    # 压测次数提示
    num = i + 1
    if i == 0:
        data = {
            "at": {
                "isAtAll": "false",
                "atUserIds": ["user001", "user002"],
                "atMobiles": ["17759212103"]
            },
            "text": {
                "content": f"info: 酒店项目已开始压测！"
            },
            "msgtype": "text",
            "actionCard": {
                "hideAvatar": "1",
                "btnOrientation": "1",
                "singleTitle": "1",
                "btns": [{
                    "actionURL": "1",
                    "title": "1"
                }],
                "text": "1",
                "singleURL": "1",
                "title": "1"
            }
        }
        app_request(accesstoken, url, data, log_path)
    if num % 100 == 0:
        data = {
            "at": {
                "isAtAll": "false",
                "atUserIds": ["user001", "user002"],
                "atMobiles": ["17759212103"]
            },
            "text": {
                "content": f"info: 酒店项目已压测{num}次"
            },
            "msgtype": "text",
            "actionCard": {
                "hideAvatar": "1",
                "btnOrientation": "1",
                "singleTitle": "1",
                "btns": [{
                    "actionURL": "1",
                    "title": "1"
                }],
                "text": "1",
                "singleURL": "1",
                "title": "1"
            }
        }
        app_request(accesstoken, url, data, log_path)
serial1.close()
