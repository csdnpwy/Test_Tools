"""
pywinauto：win桌面程序自动化处理范例
"""
from pywinauto import Application
from pywinauto import mouse
import time

# 连接到已运行的桌面应用
app = Application().connect(title="立林智慧酒店")  # 替换为你的应用窗口标题
window = app.window(title="立林智慧酒店")

# 获取按钮的 BoundingRectangle 属性
left, top, right, bottom = 187, 661, 214, 687  # 替换为具体的边界矩形坐标

# 计算按钮的中心点坐标
x = (left + right) // 2
y = (top + bottom) // 2

# 点击按钮
mouse.click(coords=(x, y))

# 记录点击时间
start_time = time.time()

# 设置超时时间，避免程序长时间等待
timeout = 30  # 最大等待时间（秒）
elapsed_time = 0

# 等待并检测“操作成功”警告窗口出现
while elapsed_time < timeout:
    # 遍历所有窗口并检查是否存在警告窗口
    for win in app.windows():
        if "操作成功！" in win.window_text():
            end_time = time.time()
            print(f"操作成功！提示框出现，耗时: {end_time - start_time} 秒")
            break
    else:
        # 如果没有找到警告窗口，则继续等待
        time.sleep(0.5)  # 延迟时间，避免占用过多的 CPU
        elapsed_time = time.time() - start_time
else:
    print("超时未检测到操作成功的警告窗口")
