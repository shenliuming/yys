"""
截图模块 - 处理屏幕截图获取
"""
import os
import time
import cv2
import numpy as np
from typing import Optional, Union, Tuple
from PIL import Image
import subprocess
import tempfile

class Screenshot:
    """截图类，负责获取屏幕截图"""
    
    def __init__(self, device):
        """
        初始化截图模块
        
        Args:
            device: 设备对象
        """
        self.device = device
        self.image = None
        self.last_screenshot_time = 0
        self.screenshot_interval = 0.1  # 截图间隔，单位秒
        self._screenshot_method = "ADB"  # 默认使用ADB截图
        self._temp_file = os.path.join(tempfile.gettempdir(), "yys_screenshot.png")
    
    @property
    def screenshot_method(self) -> str:
        """获取截图方法"""
        return self._screenshot_method
    
    @screenshot_method.setter
    def screenshot_method(self, method: str) -> None:
        """
        设置截图方法
        
        Args:
            method: 截图方法，可选值: "ADB", "ADB_nc", "uiautomator2", "DroidCast"
        """
        valid_methods = ["ADB", "ADB_nc", "uiautomator2", "DroidCast"]
        if method in valid_methods:
            self._screenshot_method = method
        else:
            print(f"不支持的截图方法: {method}，使用默认方法: ADB")
            self._screenshot_method = "ADB"
    
    def screenshot(self) -> np.ndarray:
        """
        获取屏幕截图
        
        Returns:
            np.ndarray: 截图图像数据
        """
        # 检查截图间隔
        current_time = time.time()
        if current_time - self.last_screenshot_time < self.screenshot_interval:
            time.sleep(self.screenshot_interval - (current_time - self.last_screenshot_time))
        
        # 根据不同方法获取截图
        if self._screenshot_method == "ADB":
            self.image = self._screenshot_adb()
        elif self._screenshot_method == "ADB_nc":
            self.image = self._screenshot_adb_nc()
        elif self._screenshot_method == "uiautomator2":
            self.image = self._screenshot_uiautomator2()
        elif self._screenshot_method == "DroidCast":
            self.image = self._screenshot_droidcast()
        
        # 更新截图时间
        self.last_screenshot_time = time.time()
        
        # 检查截图是否有效
        if self.image is None or self.image.size == 0:
            print("获取截图失败")
            return np.zeros((720, 1280, 3), dtype=np.uint8)
        
        return self.image
    
    def _screenshot_adb(self) -> np.ndarray:
        """
        使用ADB获取截图（内存方式，避免文件冲突）
        
        Returns:
            np.ndarray: 截图图像数据
        """
        try:
            # 直接从ADB获取截图数据到内存
            cmd = [self.device.adb_path]
            if self.device.serial:
                cmd.extend(["-s", self.device.serial])
            cmd.extend(["shell", "screencap", "-p"])
            
            # 执行命令并获取输出
            result = subprocess.run(cmd, capture_output=True, check=True)
            
            # 处理ADB输出数据
            raw_data = result.stdout
            
            # 在Windows上，ADB可能会在PNG数据中插入额外的\r字符
            # 我们需要清理这些字符以确保PNG数据的完整性
            if b'\r\n' in raw_data:
                # 移除多余的\r字符，但保留PNG文件结构
                cleaned_data = raw_data.replace(b'\r\n', b'\n')
            else:
                cleaned_data = raw_data
            
            # 将字节数据转换为numpy数组并解码
            image_data = np.frombuffer(cleaned_data, dtype=np.uint8)
            image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            
            if image is None:
                # 如果解码失败，尝试直接使用原始数据
                image_data = np.frombuffer(raw_data, dtype=np.uint8)
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
                
                if image is None:
                    print("截图数据解码失败")
                    return np.zeros((720, 1280, 3), dtype=np.uint8)
            
            # 转换颜色空间从BGR到RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
        except Exception as e:
            print(f"ADB截图时出错: {e}")
            return np.zeros((720, 1280, 3), dtype=np.uint8)
    
    def _screenshot_adb_nc(self) -> np.ndarray:
        """
        使用ADB no-compress获取截图
        
        Returns:
            np.ndarray: 截图图像数据
        """
        try:
            # 使用管道直接获取截图数据，避免压缩
            cmd = f"{self.device.adb_path} "
            if self.device.serial:
                cmd += f"-s {self.device.serial} "
            cmd += "shell screencap -p | sed 's/\r$//' > " + self._temp_file
            
            os.system(cmd)
            
            # 读取图像
            image = cv2.imread(self._temp_file)
            # 转换颜色空间从BGR到RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
        except Exception as e:
            print(f"ADB_nc截图时出错: {e}")
            return np.zeros((720, 1280, 3), dtype=np.uint8)
    
    def _screenshot_uiautomator2(self) -> np.ndarray:
        """
        使用uiautomator2获取截图
        
        Returns:
            np.ndarray: 截图图像数据
        """
        try:
            # 这里需要安装uiautomator2库
            # 简化版本，实际使用时需要安装并导入uiautomator2
            print("uiautomator2方法需要安装uiautomator2库")
            print("使用ADB方法代替")
            return self._screenshot_adb()
        except Exception as e:
            print(f"uiautomator2截图时出错: {e}")
            return np.zeros((720, 1280, 3), dtype=np.uint8)
    
    def _screenshot_droidcast(self) -> np.ndarray:
        """
        使用DroidCast获取截图
        
        Returns:
            np.ndarray: 截图图像数据
        """
        try:
            # 这里需要安装DroidCast
            # 简化版本，实际使用时需要安装并配置DroidCast
            print("DroidCast方法需要安装DroidCast")
            print("使用ADB方法代替")
            return self._screenshot_adb()
        except Exception as e:
            print(f"DroidCast截图时出错: {e}")
            return np.zeros((720, 1280, 3), dtype=np.uint8)
    
    def save_screenshot(self, path: str) -> bool:
        """
        保存截图
        
        Args:
            path: 保存路径
            
        Returns:
            bool: 是否保存成功
        """
        if self.image is None:
            self.screenshot()
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            # 保存图像
            cv2.imwrite(path, cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
            return True
        except Exception as e:
            print(f"保存截图时出错: {e}")
            return False
    
    def check_screen_size(self) -> bool:
        """
        检查屏幕尺寸是否为1280x720
        
        Returns:
            bool: 是否为1280x720
        """
        if self.image is None:
            self.screenshot()
        
        height, width = self.image.shape[:2]
        if width == 1280 and height == 720:
            return True
        else:
            print(f"屏幕尺寸不是1280x720，当前尺寸: {width}x{height}")
            return False