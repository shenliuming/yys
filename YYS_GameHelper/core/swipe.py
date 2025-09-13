"""
滑动模块 - 处理滑动操作
"""
import time
import random
import numpy as np
from typing import Tuple, Union, List, Optional

class Swipe:
    """滑动类，负责处理滑动操作"""
    
    def __init__(self, device):
        """
        初始化滑动模块
        
        Args:
            device: 设备对象
        """
        self.device = device
        self._swipe_method = "ADB"  # 默认使用ADB滑动
        self.swipe_interval = 0.3  # 滑动间隔，单位秒
        self.last_swipe_time = 0
    
    @property
    def swipe_method(self) -> str:
        """获取滑动方法"""
        return self._swipe_method
    
    @swipe_method.setter
    def swipe_method(self, method: str) -> None:
        """
        设置滑动方法
        
        Args:
            method: 滑动方法，可选值: "ADB", "minitouch", "uiautomator2"
        """
        valid_methods = ["ADB", "minitouch", "uiautomator2"]
        if method in valid_methods:
            self._swipe_method = method
        else:
            print(f"不支持的滑动方法: {method}，使用默认方法: ADB")
            self._swipe_method = "ADB"
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> None:
        """
        从起点滑动到终点
        
        Args:
            start_x: 起点X坐标
            start_y: 起点Y坐标
            end_x: 终点X坐标
            end_y: 终点Y坐标
            duration: 滑动时长，单位秒
        """
        # 检查滑动间隔
        current_time = time.time()
        if current_time - self.last_swipe_time < self.swipe_interval:
            time.sleep(self.swipe_interval - (current_time - self.last_swipe_time))
        
        # 确保坐标在屏幕范围内
        width, height = self.device.screen_size
        start_x = max(0, min(start_x, width - 1))
        start_y = max(0, min(start_y, height - 1))
        end_x = max(0, min(end_x, width - 1))
        end_y = max(0, min(end_y, height - 1))
        
        # 检查滑动距离
        distance = np.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
        if distance < 10:
            print(f"滑动距离过短: {distance}像素，可能被识别为点击")
            return
        
        # 根据不同方法执行滑动
        if self._swipe_method == "ADB":
            self._swipe_adb(start_x, start_y, end_x, end_y, duration)
        elif self._swipe_method == "minitouch":
            self._swipe_minitouch(start_x, start_y, end_x, end_y, duration)
        elif self._swipe_method == "uiautomator2":
            self._swipe_uiautomator2(start_x, start_y, end_x, end_y, duration)
        
        # 更新滑动时间
        self.last_swipe_time = time.time()
        print(f"滑动: ({start_x}, {start_y}) -> ({end_x}, {end_y}), 时长: {duration}秒")
    
    def _swipe_adb(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float) -> None:
        """
        使用ADB执行滑动
        
        Args:
            start_x: 起点X坐标
            start_y: 起点Y坐标
            end_x: 终点X坐标
            end_y: 终点Y坐标
            duration: 滑动时长，单位秒
        """
        try:
            # ADB滑动时间单位是毫秒
            duration_ms = int(duration * 1000)
            self.device._exec_adb_cmd(f"shell input swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}")
        except Exception as e:
            print(f"ADB滑动时出错: {e}")
    
    def _swipe_minitouch(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float) -> None:
        """
        使用minitouch执行滑动
        
        Args:
            start_x: 起点X坐标
            start_y: 起点Y坐标
            end_x: 终点X坐标
            end_y: 终点Y坐标
            duration: 滑动时长，单位秒
        """
        try:
            # 这里需要安装minitouch
            # 简化版本，实际使用时需要安装并配置minitouch
            print("minitouch方法需要安装minitouch")
            print("使用ADB方法代替")
            self._swipe_adb(start_x, start_y, end_x, end_y, duration)
        except Exception as e:
            print(f"minitouch滑动时出错: {e}")
    
    def _swipe_uiautomator2(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float) -> None:
        """
        使用uiautomator2执行滑动
        
        Args:
            start_x: 起点X坐标
            start_y: 起点Y坐标
            end_x: 终点X坐标
            end_y: 终点Y坐标
            duration: 滑动时长，单位秒
        """
        try:
            # 这里需要安装uiautomator2库
            # 简化版本，实际使用时需要安装并导入uiautomator2
            print("uiautomator2方法需要安装uiautomator2库")
            print("使用ADB方法代替")
            self._swipe_adb(start_x, start_y, end_x, end_y, duration)
        except Exception as e:
            print(f"uiautomator2滑动时出错: {e}")
    
    def swipe_vector(self, vector: Tuple[int, int], box: Tuple[int, int, int, int] = (0, 0, 1280, 720),
                    random_range: Tuple[int, int, int, int] = (0, 0, 0, 0), duration: float = 0.5) -> None:
        """
        按向量方向滑动
        
        Args:
            vector: 滑动向量 (x, y)
            box: 滑动区域 (x, y, width, height)
            random_range: 随机范围 (x_min, y_min, x_max, y_max)
            duration: 滑动时长，单位秒
        """
        # 计算起点
        x_min, y_min, width, height = box
        x_max = x_min + width
        y_max = y_min + height
        
        start_x = random.randint(x_min + random_range[0], x_max - random_range[2])
        start_y = random.randint(y_min + random_range[1], y_max - random_range[3])
        
        # 计算终点
        vector_x, vector_y = vector
        end_x = start_x + vector_x
        end_y = start_y + vector_y
        
        # 确保终点在屏幕范围内
        end_x = max(0, min(end_x, self.device.screen_size[0] - 1))
        end_y = max(0, min(end_y, self.device.screen_size[1] - 1))
        
        # 执行滑动
        self.swipe(start_x, start_y, end_x, end_y, duration)
    
    def swipe_up(self, distance: int = 300, box: Tuple[int, int, int, int] = (640, 360, 200, 400),
                duration: float = 0.5) -> None:
        """
        向上滑动
        
        Args:
            distance: 滑动距离
            box: 滑动区域 (center_x, center_y, width, height)
            duration: 滑动时长，单位秒
        """
        center_x, center_y, width, height = box
        x_min = center_x - width // 2
        y_min = center_y - height // 2
        
        start_x = random.randint(x_min, x_min + width)
        start_y = random.randint(y_min + height // 2, y_min + height)
        end_x = start_x
        end_y = start_y - distance
        
        self.swipe(start_x, start_y, end_x, end_y, duration)
    
    def swipe_down(self, distance: int = 300, box: Tuple[int, int, int, int] = (640, 360, 200, 400),
                 duration: float = 0.5) -> None:
        """
        向下滑动
        
        Args:
            distance: 滑动距离
            box: 滑动区域 (center_x, center_y, width, height)
            duration: 滑动时长，单位秒
        """
        center_x, center_y, width, height = box
        x_min = center_x - width // 2
        y_min = center_y - height // 2
        
        start_x = random.randint(x_min, x_min + width)
        start_y = random.randint(y_min, y_min + height // 2)
        end_x = start_x
        end_y = start_y + distance
        
        self.swipe(start_x, start_y, end_x, end_y, duration)
    
    def swipe_left(self, distance: int = 300, box: Tuple[int, int, int, int] = (640, 360, 400, 200),
                 duration: float = 0.5) -> None:
        """
        向左滑动
        
        Args:
            distance: 滑动距离
            box: 滑动区域 (center_x, center_y, width, height)
            duration: 滑动时长，单位秒
        """
        center_x, center_y, width, height = box
        x_min = center_x - width // 2
        y_min = center_y - height // 2
        
        start_x = random.randint(x_min + width // 2, x_min + width)
        start_y = random.randint(y_min, y_min + height)
        end_x = start_x - distance
        end_y = start_y
        
        self.swipe(start_x, start_y, end_x, end_y, duration)
    
    def swipe_right(self, distance: int = 300, box: Tuple[int, int, int, int] = (640, 360, 400, 200),
                  duration: float = 0.5) -> None:
        """
        向右滑动
        
        Args:
            distance: 滑动距离
            box: 滑动区域 (center_x, center_y, width, height)
            duration: 滑动时长，单位秒
        """
        center_x, center_y, width, height = box
        x_min = center_x - width // 2
        y_min = center_y - height // 2
        
        start_x = random.randint(x_min, x_min + width // 2)
        start_y = random.randint(y_min, y_min + height)
        end_x = start_x + distance
        end_y = start_y
        
        self.swipe(start_x, start_y, end_x, end_y, duration)