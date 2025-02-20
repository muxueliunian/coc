import cv2
import numpy as np
import pyautogui
import time
import ctypes
import sys
import os 
import pygetwindow as gw



def capture_window(window_title):
    """
    截取指定标题的窗口（改进版）
    :param window_title: 窗口标题（支持部分匹配）
    :return: 截图图像(OpenCV格式)或None
    """
    try:
        # 查找目标窗口
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            print(f"未找到标题包含 [{window_title}] 的窗口")
            return None
            
        win = windows[0]
        
        # 窗口激活逻辑增强
        if win.isMinimized:
            win.restore()  # 先恢复最小化窗口
        win.activate()     # 正确的激活方法（无需参数）
        
        # 等待窗口激活（使用渐进式等待）
        for _ in range(5):
            if win.isActive:
                break
            time.sleep(0.5)
        else:
            print("警告：窗口激活超时，可能截图不准确")
        
        # 重新获取最新的窗口坐标（防止恢复/激活后坐标变化）
        # 刷新窗口对象
        win = gw.getWindowsWithTitle(window_title)[0]  
        left, top, width, height = win.left, win.top, win.width, win.height
        
        # 添加边界保护（防止负坐标）
        screen_width, screen_height = pyautogui.size()
        left = max(0, min(left, screen_width - 1))
        top = max(0, min(top, screen_height - 1))
        width = max(1, min(width, screen_width - left))
        height = max(1, min(height, screen_height - top))
        
        time.sleep(1)
        # 截取窗口区域
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    except Exception as e:
        print(f"截图失败：{str(e)}")
        return None

def find_and_click_image(template_path, threshold=0.8, wait_time=1, window_title=None):
    """
    参数：
    template_path - 模板图片路径
    threshold - 匹配阈值(0-1)
    wait_time - 检测间隔(秒)
    window_title - 目标窗口标题
    """
    # 加载模板
    template = cv2.imread(template_path)
    if template is None:
        raise ValueError(f"无法加载模板图片: {template_path}")

    # 转换到HSV并提取H通道
    template_hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
    template_h = template_hsv[:,:,0]
    h, w = template_h.shape[:2]

    while True:
        screenshot = capture_window(window_title)
        if screenshot is None:
            time.sleep(wait_time)
            continue
        
        # 执行模板匹配
        screenshot_hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        screenshot_h = screenshot_hsv[:,:,0]
        res = cv2.matchTemplate(screenshot_h, template_h, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            # 计算坐标
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2

            # 转换全局坐标
            try:
                win = gw.getWindowsWithTitle(window_title)[0]
                global_x = win.left + center_x
                global_y = win.top + center_y
            except:
                global_x = center_x
                global_y = center_y

    
            pyautogui.click(global_x, global_y)
            print(f"成功点击坐标：({global_x}, {global_y})")
            break
        else:
            print(f"检测中... 当前匹配度：{max_val:.2f}")

        time.sleep(wait_time)

def find_and_click_image_twice(template_path, threshold=0.8, wait_time=1, window_title=None):
    """
    双击版本图像匹配点击函数
    
    参数：
    template_path - 模板图片路径
    threshold - 匹配阈值(0-1)
    wait_time - 检测间隔(秒)
    window_title - 目标窗口标题
    """
    # 加载模板
    template = cv2.imread(template_path)
    if template is None:
        raise ValueError(f"无法加载模板图片: {template_path}")

    # 转换到HSV并提取H通道
    template_hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
    template_h = template_hsv[:,:,0]
    h, w = template_h.shape[:2]

    while True:
        screenshot = capture_window(window_title)
        if screenshot is None:
            time.sleep(wait_time)
            continue
        
        # 执行模板匹配
        screenshot_hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        screenshot_h = screenshot_hsv[:,:,0]
        res = cv2.matchTemplate(screenshot_h, template_h, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            # 计算坐标
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2

            # 转换全局坐标
            try:
                win = gw.getWindowsWithTitle(window_title)[0]
                global_x = win.left + center_x
                global_y = win.top + center_y
            except:
                global_x = center_x
                global_y = center_y

            pyautogui.click(global_x, global_y)
            time.sleep(0.3)  # 双击间隔
            pyautogui.click(global_x, global_y)
            print(f"成功双击坐标：({global_x}, {global_y})")
            break
        else:
            print(f"检测中... 当前匹配度：{max_val:.2f}")

        time.sleep(wait_time)

#点击叉叉特供函数找不到就跳过
def find_and_click_image_twice_XX(template_path, threshold=0.8, wait_time=1, window_title=None):
    """
    双击版本图像匹配点击函数
    
    参数：
    template_path - 模板图片路径
    threshold - 匹配阈值(0-1)
    wait_time - 检测间隔(秒)
    window_title - 目标窗口标题
    """
    # 加载模板
    template = cv2.imread(template_path)
    if template is None:
        raise ValueError(f"无法加载模板图片: {template_path}")

    # 转换到HSV并提取H通道
    template_hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
    template_h = template_hsv[:,:,0]
    h, w = template_h.shape[:2]

    while True:
        screenshot = capture_window(window_title)
        if screenshot is None:
            time.sleep(wait_time)
            continue
        
        # 执行模板匹配
        screenshot_hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        screenshot_h = screenshot_hsv[:,:,0]
        res = cv2.matchTemplate(screenshot_h, template_h, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            # 计算坐标
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2

            # 转换全局坐标
            try:
                win = gw.getWindowsWithTitle(window_title)[0]
                global_x = win.left + center_x
                global_y = win.top + center_y
            except:
                global_x = center_x
                global_y = center_y

            pyautogui.click(global_x, global_y)
            time.sleep(0.3)  # 双击间隔
            pyautogui.click(global_x, global_y)
            print(f"成功双击坐标：({global_x}, {global_y})")
            break
        else:
            print("未找到目标，执行下一步")
            break

        time.sleep(wait_time)

def is_admin():
    """检查当前是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员权限重新运行程序"""
    if sys.argv[0].endswith('.py'):  # 如果是直接运行的.py文件
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:])
    else:  # 如果是打包后的exe文件
        params = ' '.join(sys.argv)
    
    # 对路径和参数进行引号转义处理
    if ' ' in params:
        params = f'"{params}"'
    
    ctypes.windll.shell32.ShellExecuteW(
        None,  # 父窗口句柄
        "runas",  # 操作类型：提权运行
        sys.executable,  # 可执行文件路径
        params,  # 参数
        None,  # 工作目录
        1  # 窗口显示方式：SW_SHOWNORMAL
    )
    sys.exit()  # 退出当前非特权进程


import tkinter as tk
from tkinter import ttk
import threading

# 功能执行函数
def start_game():
    print("正在启动游戏")
    find_and_click_image(
        template_path=os.path.join('database', 'gamestart', 'game_start.png'),
        window_title="雷电",
        threshold=0.7,
        wait_time=1
    )
    print("游戏启动完成")
    time.sleep(15)

def close_xx():
    print("正在执行关闭叉叉")
    find_and_click_image_twice_XX(
        template_path=os.path.join('database', 'close.png'),
        window_title="雷电",
        threshold=0.7,
        wait_time=1
    )

def collect_dark_water():
    print("正在收集黑油")
    find_and_click_image(
        template_path=os.path.join('database', 'Collector_image', 'dark_water.png'),
        window_title="雷电",
        threshold=0.7,
        wait_time=1
    )

def collect_gold_coin():
    print("正在收集金币")
    find_and_click_image(
        template_path=os.path.join('database', 'Collector_image', 'gold_coin.png'),
        window_title="雷电",
        threshold=0.65,
        wait_time=1
    )

def collect_holy_water():
    print("正在收集圣水")
    find_and_click_image(
        template_path=os.path.join('database', 'Collector_image', 'holy_water.png'),
        window_title="雷电",
        threshold=0.7,
        wait_time=1
    )

def execute_operations():
    # 禁用按钮防止重复点击
    start_btn.config(state=tk.DISABLED)
    
    # 在新线程中执行任务
    def thread_task():
        try:
            # 必须执行启动游戏
            start_game()
            
            # 根据勾选状态执行其他操作
            if close_xx_var.get():
                close_xx()
            if dark_water_var.get():
                collect_dark_water()
            if gold_coin_var.get():
                collect_gold_coin()
            if holy_water_var.get():
                collect_holy_water()
                
        finally:
            # 重新启用按钮
            start_btn.config(state=tk.NORMAL)
    
    threading.Thread(target=thread_task, daemon=True).start()

def main():
    # 创建主窗口
    root = tk.Tk()
    root.title("COC自动化控制面板")
    root.geometry("350x300")

    # 使用ttk样式
    style = ttk.Style()
    style.configure('TCheckbutton', font=('微软雅黑', 10))
    style.configure('TButton', font=('微软雅黑', 10))

    # 创建变量
    global close_xx_var, dark_water_var, gold_coin_var, holy_water_var
    close_xx_var = tk.BooleanVar()
    dark_water_var = tk.BooleanVar()
    gold_coin_var = tk.BooleanVar()
    holy_water_var = tk.BooleanVar()

    # 创建控件
    frame = ttk.LabelFrame(root, text="功能选择")
    frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    ttk.Checkbutton(frame, text="1. 关闭叉叉", variable=close_xx_var).pack(anchor=tk.W, pady=2)
    ttk.Checkbutton(frame, text="2. 收集黑油", variable=dark_water_var).pack(anchor=tk.W, pady=2)
    ttk.Checkbutton(frame, text="3. 收集金币", variable=gold_coin_var).pack(anchor=tk.W, pady=2)
    ttk.Checkbutton(frame, text="4. 收集圣水", variable=holy_water_var).pack(anchor=tk.W, pady=2)

    global start_btn
    start_btn = ttk.Button(root, text="开始游戏", command=execute_operations)
    start_btn.pack(pady=10)

    root.mainloop()

    




if __name__ == "__main__":
    main()
