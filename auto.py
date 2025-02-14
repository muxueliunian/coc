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
    :return: 截图图像（OpenCV格式）或None
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
        win = gw.getWindowsWithTitle(window_title)[0]  # 刷新窗口对象
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

def find_and_click_image(template_path, threshold=0.7, wait_time=1, window_title=None):  # 修正函数名
    """
    基于颜色特征进行图像匹配的增强版本
    
    参数：
    template_path - 模板图片路径
    threshold - 匹配阈值(0-1),默认0.7
    wait_time - 检测间隔(秒),默认1
    window_title - 目标窗口标题
    """
    # 加载模板
    template = cv2.imread(template_path)  # 修正变量名
    if template is None:
        raise ValueError(f"无法加载模板图片:{template_path}")
    
    # 转换到HSV并提取H通道（修正颜色空间常量）
    template_hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)  # 修正BRG->BGR
    template_h = template_hsv[:,:,0]

    # 获取模板尺寸
    h, w = template_h.shape[:2]  # 修正变量名

    while True:
        screenshot = capture_window(window_title)
        if screenshot is None:
            time.sleep(wait_time)
            continue
        
        # 转换为HSV空间
        screenshot_hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)  # 已从RGB转BGR，直接转换
        screenshot_h = screenshot_hsv[:,:,0]

        # 执行模板匹配
        res = cv2.matchTemplate(screenshot_h, template_h, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            # 计算点击坐标（相对于窗口）
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2

            # 转换为全局坐标
            try:
                win = gw.getWindowsWithTitle(window_title)[0]
                global_x = win.left + center_x
                global_y = win.top + center_y
            except:
                global_x = center_x
                global_y = center_y

            # 执行点击前进行二次颜色验证
            if color_verify(global_x, global_y, template_hsv):
                pyautogui.click(global_x, global_y)
                print(f"成功点击：({global_x}, {global_y}) 匹配度：{max_val:.2f}")
                break
            else:
                print(f"颜色验证未通过，可能为错误匹配")
        else:
            print(f"持续检测中... 当前最大匹配度：{max_val:.2f}")

        time.sleep(wait_time)

def color_verify(x, y, template_hsv, tolerance=15):
    """
    二次颜色验证函数
    参数：
    x, y - 待验证的屏幕坐标（全局坐标）
    template_hsv - 模板的HSV图像
    tolerance - 色相允许误差（0-180），默认15
    """
    # 获取目标区域颜色
    screen_pixel = np.array(pyautogui.screenshot(region=(x, y, 1, 1)))  # 修复缺少括号的问题
    screen_bgr = cv2.cvtColor(screen_pixel, cv2.COLOR_RGB2BGR)
    screen_hsv = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2HSV)
    
    # 获取模板主色调（取中心点）
    t_center = template_hsv[template_hsv.shape[0]//2, template_hsv.shape[1]//2]
    
    # 色相环形差值计算
    diff = abs(int(screen_hsv[0,0,0]) - t_center[0])
    color_diff = min(diff, 180 - diff)
    
    return color_diff <= tolerance


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


def main():
    if not is_admin():
        print("检测到当前未使用管理员权限，正在尝试提权...")
        run_as_admin()
    else:
        print("当前已获得管理员权限")
    
    time.sleep(1)
    image_1 = capture_window("QQ")
    time.sleep(1)
    cv2.imshow("QQ",image_1)
    cv2.waitKey(0)
    cv2.destroyAllWindows()





if __name__ == "__main__":
    main()





