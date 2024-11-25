"""
opencv：图像处理范例
"""
import cv2

# 读取图像
image_path = r"C:/Users/panwy/Desktop/2.png"
image = cv2.imread(image_path)
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

# # 反转图像，使灯的区域为白色
# binary = cv2.bitwise_not(binary)
# binary_output_path = "C:/Users/panwy/Desktop/binary_debug.png"
# cv2.imwrite(binary_output_path, binary)
# print(f"二值化图像已保存到：{binary_output_path}")

# 寻找轮廓
# cv2.RETR_EXTERNAL：只检测外轮廓（忽略嵌套的内轮廓）。
# cv2.CHAIN_APPROX_SIMPLE：使用简单的方式压缩轮廓点（减少数据量）。
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 按大小过滤轮廓（避免误识别）
# cv2.contourArea(cnt)：计算轮廓的面积。
# > 10：保留面积大于 10 的轮廓。
filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 10]

# 判断是否存在24个灯亮
if len(filtered_contours) != 24:
    result_text = f"Total:24 OFF:{24 - len(filtered_contours)}"
else:
    result_text = "All Lights ON"

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
# 判断是否所有灯都亮
# all_lights_on = all(lights_status)

# 显示结果
cv2.putText(image, result_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

# 保存并显示输出图像
output_path = r"C:/Users/panwy/Desktop/res.png"
cv2.imwrite(output_path, image)

print(f"处理完成！检测结果：{result_text}")
print(f"结果图像已保存到：{output_path}")
