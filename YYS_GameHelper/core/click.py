"""
点击模块 - 处理点击操作
"""
import time
import random
import numpy as np
from typing import Tuple, Union, List, Optional

class Click:
    """点击类，负责处理点击操作"""
    
    def __init__(self, device):
        """
        初始化点击模块
        
        Args:
            device: 设备对象
        """
        self.device = device
        self._click_method = "ADB"  # 默认使用ADB点击
        self.click_interval = 0.1  # 点击间隔，单位秒
        self.last_click_time = 0
    
    @property
    def click_method(self) -> str:
        """获取点击方法"""
        return self._click_method
    
    @click_method.setter
    def click_method(self, method: str) -> None:
        """
        设置点击方法
        
        Args:
            method: 点击方法，可选值: "ADB", "minitouch", "uiautomator2"
        """
        valid_methods = ["ADB", "minitouch", "uiautomator2"]
        if method in valid_methods:
            self._click_method = method
        else:
            print(f"不支持的点击方法: {method}，使用默认方法: ADB")
            self._click_method = "ADB"
    
    def click(self, x: int, y: int, random_offset: int = 5) -> None:
        """
        点击指定坐标
        
        Args:
            x: X坐标
            y: Y坐标
            random_offset: 随机偏移量，使点击位置更自然
        """
        # 检查点击间隔
        current_time = time.time()
        if current_time - self.last_click_time < self.click_interval:
            time.sleep(self.click_interval - (current_time - self.last_click_time))
        
        # 添加随机偏移
        if random_offset > 0:
            x += random.randint(-random_offset, random_offset)
            y += random.randint(-random_offset, random_offset)
        
        # 确保坐标在屏幕范围内
        width, height = self.device.screen_size
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))
        
        # 根据不同方法执行点击
        if self._click_method == "ADB":
            self._click_adb(x, y)
        elif self._click_method == "minitouch":
            self._click_minitouch(x, y)
        elif self._click_method == "uiautomator2":
            self._click_uiautomator2(x, y)
        
        # 更新点击时间
        self.last_click_time = time.time()
        print(f"点击坐标: ({x}, {y})")
    
    def _click_adb(self, x: int, y: int) -> None:
        """
        使用ADB执行点击
        
        Args:
            x: X坐标
            y: Y坐标
        """
        try:
            self.device._exec_adb_cmd(f"shell input tap {x} {y}")
        except Exception as e:
            print(f"ADB点击时出错: {e}")
    
    def _click_minitouch(self, x: int, y: int) -> None:
        """
        使用minitouch执行点击
        
        Args:
            x: X坐标
            y: Y坐标
        """
        try:
            # 这里需要安装minitouch
            # 简化版本，实际使用时需要安装并配置minitouch
            print("minitouch方法需要安装minitouch")
            print("使用ADB方法代替")
            self._click_adb(x, y)
        except Exception as e:
            print(f"minitouch点击时出错: {e}")
    
    def _click_uiautomator2(self, x: int, y: int) -> None:
        """
        使用uiautomator2执行点击
        
        Args:
            x: X坐标
            y: Y坐标
        """
        try:
            # 这里需要安装uiautomator2库
            # 简化版本，实际使用时需要安装并导入uiautomator2
            print("uiautomator2方法需要安装uiautomator2库")
            print("使用ADB方法代替")
            self._click_adb(x, y)
        except Exception as e:
            print(f"uiautomator2点击时出错: {e}")
    
    def click_area(self, area: Tuple[int, int, int, int]) -> None:
        """
        点击区域内的随机位置
        
        Args:
            area: 区域坐标 (x, y, width, height)
        """
        x, y, width, height = area
        random_x = x + random.randint(0, width)
        random_y = y + random.randint(0, height)
        self.click(random_x, random_y)
    
    def multi_click(self, x: int, y: int, times: int, interval: float = 0.1) -> None:
        """
        连续点击多次
        
        Args:
            x: X坐标
            y: Y坐标
            times: 点击次数
            interval: 点击间隔，单位秒
        """
        for _ in range(times):
            self.click(x, y)
            time.sleep(interval)
    
    def long_click(self, x: int, y: int, duration: float = 1.0) -> None:
        """
        长按指定坐标
        
        Args:
            x: X坐标
            y: Y坐标
            duration: 按住时长，单位秒
        """
        try:
            if self._click_method == "ADB":
                self.device._exec_adb_cmd(f"shell input swipe {x} {y} {x} {y} {int(duration * 1000)}")
            elif self._click_method == "minitouch":
                # 简化版本，实际使用时需要安装并配置minitouch
                print("minitouch方法需要安装minitouch")
                print("使用ADB方法代替")
                self.device._exec_adb_cmd(f"shell input swipe {x} {y} {x} {y} {int(duration * 1000)}")
            elif self._click_method == "uiautomator2":
                # 简化版本，实际使用时需要安装并导入uiautomator2
                print("uiautomator2方法需要安装uiautomator2库")
                print("使用ADB方法代替")
                self.device._exec_adb_cmd(f"shell input swipe {x} {y} {x} {y} {int(duration * 1000)}")
            
            print(f"长按坐标: ({x}, {y}), 时长: {duration}秒")
        except Exception as e:
            print(f"长按时出错: {e}")

class RuleClick:
    """规则点击类，用于定义点击规则"""
    
    def __init__(self, roi_front: Tuple[int, int, int, int], roi_back: Tuple[int, int, int, int], name: str = None):
        """
        初始化规则点击
        
        Args:
            roi_front: 前置ROI (x, y, width, height)
            roi_back: 后置ROI (x, y, width, height)
            name: 规则名称
        """
        self.roi_front = list(roi_front)
        self.roi_back = list(roi_back)
        self.name = name if name else "click"
    
    def coord(self) -> Tuple[int, int]:
        """
        获取前置ROI内的随机坐标
        
        Returns:
            Tuple[int, int]: 随机坐标 (x, y)
        """
        x, y, w, h = self.roi_front
        random_x = np.random.randint(x, x + w)
        random_y = np.random.randint(y, y + h)
        return random_x, random_y
    
    def coord_more(self) -> Tuple[int, int]:
        """
        获取后置ROI内的随机坐标
        
        Returns:
            Tuple[int, int]: 随机坐标 (x, y)
        """
        x, y, w, h = self.roi_back
        random_x = np.random.randint(x, x + w)
        random_y = np.random.randint(y, y + h)
        return random_x, random_y
    
    @property
    def center(self) -> Tuple[int, int]:
        """
        获取前置ROI的中心坐标
        
        Returns:
            Tuple[int, int]: 中心坐标 (x, y)
        """
        x, y, w, h = self.roi_front
        return x + w // 2, y + h // 2
    
    def move(self, x: int, y: int) -> None:
        """
        移动前置ROI
        
        Args:
            x: X方向移动量
            y: Y方向移动量
        """
        self.roi_front[0] += x
        self.roi_front[1] += y
        
        # 限制在屏幕范围内
        self.roi_front[0] = max(0, min(self.roi_front[0], 1280))
        self.roi_front[1] = max(0, min(self.roi_front[1], 720))