"""设备模块 - 负责设备连接和基础操作"""
import os
import time
import subprocess
import re
from typing import Optional, Tuple, List, Dict, Any, Union
import numpy as np

class Device:
    """设备类，负责与设备的连接和基础操作"""
    
    def __init__(self, serial: str = None, adb_path: str = "adb"):
        """
        初始化设备
        
        Args:
            serial: 设备序列号，为None时使用默认设备
            adb_path: adb可执行文件路径
        """
        self.serial = serial
        self.adb_path = adb_path
        self._screen_size = None
        self._orientation = 0
        self._connected = False
        self.connect()
    
    def connect(self) -> bool:
        """
        连接到设备，支持重试机制
        
        Returns:
            bool: 是否连接成功
        """
        # 如果没有指定serial，尝试自动检测
        if not self.serial:
            self.serial = self._auto_detect_device()
            if not self.serial:
                print("未检测到可用设备")
                return False
        
        # 尝试连接设备，最多重试3次
        for attempt in range(3):
            try:
                print(f"尝试连接设备 {self.serial} (第{attempt + 1}次)")
                
                # 检查设备是否需要adb connect
                if self._need_adb_connect(self.serial):
                    if not self._adb_connect(self.serial):
                        print(f"ADB连接失败: {self.serial}")
                        continue
                
                # 检查设备状态
                if self._check_device_status(self.serial):
                    self._connected = True
                    self._update_screen_info()
                    print(f"成功连接到设备: {self.serial}")
                    return True
                else:
                    print(f"设备状态检查失败: {self.serial}")
                    
            except Exception as e:
                print(f"连接设备时出错 (第{attempt + 1}次): {e}")
            
            # 等待后重试
            if attempt < 2:
                time.sleep(2)
        
        print(f"连接设备失败: {self.serial}")
        return False
    
    def _update_screen_info(self) -> None:
        """更新屏幕信息"""
        try:
            size = self._exec_adb_cmd("shell wm size")
            if "Physical size:" in size:
                size = size.split("Physical size:")[1].strip()
                width, height = map(int, size.split("x"))
                self._screen_size = (width, height)
            
            # Windows系统兼容性：使用findstr替代grep
            try:
                orientation = self._exec_adb_cmd("shell dumpsys input")
                # 查找包含SurfaceOrientation的行
                for line in orientation.split('\n'):
                    if "SurfaceOrientation" in line:
                        # 提取方向值
                        parts = line.split("SurfaceOrientation")
                        if len(parts) > 1:
                            orientation_str = parts[1].strip().split()[0]
                            self._orientation = int(orientation_str)
                            break
            except:
                # 如果获取方向失败，设置默认值
                self._orientation = 0
        except Exception as e:
            print(f"获取屏幕信息时出错: {e}")
    
    def _need_adb_connect(self, serial: str) -> bool:
        """
        判断是否需要执行adb connect
        
        Args:
            serial: 设备序列号
            
        Returns:
            bool: 是否需要adb connect
        """
        # emulator-xxxx 和 Android设备序列号不需要connect
        if serial.startswith('emulator-') or re.match(r'^[a-zA-Z0-9]+$', serial):
            return False
        # IP地址格式需要connect
        if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', serial):
            return True
        return False
    
    def _adb_connect(self, serial: str) -> bool:
        """
        执行adb connect
        
        Args:
            serial: 设备序列号
            
        Returns:
            bool: 连接是否成功
        """
        try:
            cmd = f"{self.adb_path} connect {serial}"
            result = subprocess.check_output(cmd, shell=True, timeout=10).decode('utf-8')
            
            if 'connected' in result.lower():
                return True
            elif 'already connected' in result.lower():
                return True
            elif '(10061)' in result:
                print(f"连接被拒绝，请检查模拟器是否启动: {serial}")
                return False
            else:
                print(f"ADB连接结果: {result.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"ADB连接超时: {serial}")
            return False
        except Exception as e:
            print(f"ADB连接异常: {e}")
            return False
    
    def _check_device_status(self, serial: str) -> bool:
        """
        检查设备状态
        
        Args:
            serial: 设备序列号
            
        Returns:
            bool: 设备是否可用
        """
        try:
            devices_output = self._exec_adb_cmd("devices")
            lines = devices_output.strip().split('\n')
            
            for line in lines[1:]:  # 跳过第一行标题
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        device_serial, status = parts[0], parts[1]
                        if device_serial == serial:
                            if status == 'device':
                                return True
                            elif status == 'offline':
                                print(f"设备离线: {serial}")
                                # 尝试断开重连
                                self._adb_disconnect(serial)
                                time.sleep(1)
                                return self._adb_connect(serial)
                            elif status == 'unauthorized':
                                print(f"设备未授权，请在设备上允许USB调试: {serial}")
                                return False
                            else:
                                print(f"设备状态异常: {serial} - {status}")
                                return False
            
            print(f"未找到设备: {serial}")
            return False
            
        except Exception as e:
            print(f"检查设备状态时出错: {e}")
            return False
    
    def _adb_disconnect(self, serial: str) -> None:
        """
        断开ADB连接
        
        Args:
            serial: 设备序列号
        """
        try:
            if self._need_adb_connect(serial):
                cmd = f"{self.adb_path} disconnect {serial}"
                subprocess.run(cmd, shell=True, timeout=5, capture_output=True)
        except Exception:
            pass  # 忽略断开连接的错误
    
    def _auto_detect_device(self) -> Optional[str]:
        """
        自动检测可用设备
        
        Returns:
            Optional[str]: 检测到的设备序列号
        """
        try:
            devices_output = self._exec_adb_cmd("devices")
            lines = devices_output.strip().split('\n')
            available_devices = []
            
            for line in lines[1:]:  # 跳过第一行标题
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2 and parts[1] == 'device':
                        available_devices.append(parts[0])
            
            if len(available_devices) == 1:
                return available_devices[0]
            elif len(available_devices) > 1:
                print(f"检测到多个设备: {available_devices}")
                print("提示: 如需指定设备，请在初始化时传入 serial 参数")
                return available_devices[0]  # 返回第一个设备
            else:
                return None
                
        except Exception as e:
            print(f"自动检测设备时出错: {e}")
            return None
    
    def _exec_adb_cmd(self, cmd: str) -> str:
        """
        执行adb命令
        
        Args:
            cmd: 要执行的adb命令
            
        Returns:
            str: 命令输出
        """
        if self.serial and not cmd.startswith('devices'):
            full_cmd = f"{self.adb_path} -s {self.serial} {cmd}"
        else:
            full_cmd = f"{self.adb_path} {cmd}"
        
        try:
            result = subprocess.check_output(full_cmd, shell=True, timeout=10).decode('utf-8')
            return result
        except subprocess.TimeoutExpired:
            print(f"ADB命令超时: {full_cmd}")
            return ""
        except subprocess.CalledProcessError as e:
            print(f"执行adb命令时出错: {e}")
            return ""
    
    def app_start(self, package_name: str) -> bool:
        """
        启动应用
        
        Args:
            package_name: 应用包名
            
        Returns:
            bool: 是否成功启动
        """
        if not self._connected:
            print("设备未连接")
            return False
        
        try:
            self._exec_adb_cmd(f"shell am start -n {package_name}")
            return True
        except Exception as e:
            print(f"启动应用时出错: {e}")
            return False
    
    def app_stop(self, package_name: str) -> bool:
        """
        停止应用
        
        Args:
            package_name: 应用包名
            
        Returns:
            bool: 是否成功停止
        """
        if not self._connected:
            print("设备未连接")
            return False
        
        try:
            self._exec_adb_cmd(f"shell am force-stop {package_name}")
            return True
        except Exception as e:
            print(f"停止应用时出错: {e}")
            return False
    
    def app_is_running(self, package_name: str) -> bool:
        """
        检查应用是否正在运行
        
        Args:
            package_name: 应用包名
            
        Returns:
            bool: 应用是否正在运行
        """
        if not self._connected:
            print("设备未连接")
            return False
        
        try:
            result = self._exec_adb_cmd(f"shell ps | grep {package_name}")
            return package_name in result
        except Exception as e:
            print(f"检查应用是否运行时出错: {e}")
            return False
    
    @property
    def screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸"""
        if not self._screen_size:
            self._update_screen_info()
        return self._screen_size
    
    @property
    def orientation(self) -> int:
        """获取屏幕方向"""
        return self._orientation
    
    def disconnect(self) -> None:
        """断开设备连接"""
        if self._connected and self.serial:
            try:
                # 如果是网络设备，执行adb disconnect
                if self._need_adb_connect(self.serial):
                    self._adb_disconnect(self.serial)
                self._connected = False
                print(f"已断开设备连接: {self.serial}")
            except Exception as e:
                print(f"断开设备连接时出错: {e}")