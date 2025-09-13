"""模拟器模块 - 处理模拟器选择和管理"""
import os
import re
import subprocess
from typing import List, Dict, Optional, Tuple

class Emulator:
    """模拟器类，负责模拟器选择和管理"""
    
    def __init__(self):
        """初始化模拟器模块"""
        self.emulators = {}  # 模拟器字典，键为模拟器名称，值为模拟器信息
    
    def detect_emulators(self) -> Dict[str, Dict]:
        """
        检测系统中的模拟器
        
        Returns:
            Dict[str, Dict]: 模拟器字典，键为模拟器名称，值为模拟器信息
        """
        # 清空已有模拟器列表
        self.emulators = {}
        
        # 检测模拟器
        self._detect_mumu()
        self._detect_nox()
        self._detect_bluestacks()
        self._detect_ldplayer()
        
        # 检测ADB设备
        self._detect_adb_devices()
        
        return self.emulators
    
    def _detect_mumu(self) -> None:
        """检测MuMu模拟器"""
        # MuMu模拟器可能的安装路径
        mumu_paths = [
            "C:\\Program Files\\MuMu\\emulator\\nemu\\vmonitor\\bin",
            "D:\\Program Files\\MuMu\\emulator\\nemu\\vmonitor\\bin",
            "C:\\Program Files\\NetEase\\MuMu\\emulator\\nemu\\vmonitor\\bin",
            "D:\\Program Files\\NetEase\\MuMu\\emulator\\nemu\\vmonitor\\bin"
        ]
        
        for path in mumu_paths:
            if os.path.exists(path):
                self.emulators["MuMu"] = {
                    "name": "MuMu模拟器",
                    "path": path,
                    "adb_port": 7555,
                    "address": "127.0.0.1:7555",
                    "type": "mumu"
                }
                break
    
    def _detect_nox(self) -> None:
        """检测夜神模拟器"""
        # 夜神模拟器可能的安装路径
        nox_paths = [
            "C:\\Program Files\\Nox\\bin",
            "D:\\Program Files\\Nox\\bin",
            "C:\\Program Files (x86)\\Nox\\bin",
            "D:\\Program Files (x86)\\Nox\\bin"
        ]
        
        for path in nox_paths:
            if os.path.exists(path):
                self.emulators["Nox"] = {
                    "name": "夜神模拟器",
                    "path": path,
                    "adb_port": 62001,
                    "address": "127.0.0.1:62001",
                    "type": "nox"
                }
                break
    
    def _detect_bluestacks(self) -> None:
        """检测蓝叠模拟器"""
        # 蓝叠模拟器可能的安装路径
        bluestacks_paths = [
            "C:\\Program Files\\BlueStacks",
            "D:\\Program Files\\BlueStacks",
            "C:\\Program Files (x86)\\BlueStacks",
            "D:\\Program Files (x86)\\BlueStacks"
        ]
        
        for path in bluestacks_paths:
            if os.path.exists(path):
                self.emulators["BlueStacks"] = {
                    "name": "蓝叠模拟器",
                    "path": path,
                    "adb_port": 5555,
                    "address": "127.0.0.1:5555",
                    "type": "bluestacks"
                }
                break
    
    def _detect_ldplayer(self) -> None:
        """检测雷电模拟器"""
        # 雷电模拟器可能的安装路径
        ldplayer_paths = [
            "C:\\Program Files\\LDPlayer",
            "D:\\Program Files\\LDPlayer",
            "C:\\LDPlayer",
            "D:\\LDPlayer"
        ]
        
        for path in ldplayer_paths:
            if os.path.exists(path):
                self.emulators["LDPlayer"] = {
                    "name": "雷电模拟器",
                    "path": path,
                    "adb_port": 5555,
                    "address": "127.0.0.1:5555",
                    "type": "ldplayer"
                }
                break
    
    def _detect_adb_devices(self) -> None:
        """检测ADB设备"""
        try:
            # 执行ADB命令获取设备列表
            result = subprocess.run(
                ["adb", "devices"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # 解析设备列表
            lines = result.stdout.strip().split('\n')
            if len(lines) <= 1:
                return
            
            # 遍历设备列表
            for i, line in enumerate(lines[1:], 1):
                if not line.strip():
                    continue
                
                parts = line.split('\t')
                if len(parts) != 2:
                    continue
                
                address, status = parts
                if status != "device":
                    continue
                
                # 处理模拟器地址
                if address.startswith('emulator-'):
                    # 模拟器设备，emulator-5554对应127.0.0.1:5555
                    port_num = int(address.replace('emulator-', ''))
                    tcp_port = port_num + 1  # emulator-5554 -> 127.0.0.1:5555
                    address = f"127.0.0.1:{tcp_port}"
                
                # 添加到模拟器列表
                self.emulators[f"ADB设备{i}"] = {
                    "name": f"ADB设备{i}",
                    "path": "",
                    "adb_port": int(address.split(':')[1]) if ":" in address else 5555,
                    "address": address,
                    "type": "adb"
                }
        except Exception as e:
            print(f"检测ADB设备出错: {e}")
    
    def list_emulators(self) -> List[str]:
        """
        列出所有检测到的模拟器
        
        Returns:
            List[str]: 模拟器名称列表
        """
        return list(self.emulators.keys())
    
    def get_emulator(self, name: str) -> Optional[Dict]:
        """
        获取指定模拟器信息
        
        Args:
            name: 模拟器名称
            
        Returns:
            Optional[Dict]: 模拟器信息，如果不存在则返回None
        """
        return self.emulators.get(name)
    
    def connect_emulator(self, name: str) -> bool:
        """
        连接到指定模拟器
        
        Args:
            name: 模拟器名称
            
        Returns:
            bool: 是否连接成功
        """
        emulator = self.get_emulator(name)
        if not emulator:
            print(f"模拟器不存在: {name}")
            return False
        
        # 先断开已有连接，避免冲突
        self._disconnect_emulator(emulator["address"])
        
        try:
            # 设置编码为UTF-8，避免中文系统下的GBK编码问题
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # 连接到模拟器
            print(f"正在连接: {emulator['address']}...")
            result = subprocess.run(
                ["adb", "connect", emulator["address"]], 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                errors='ignore',
                env=env,
                timeout=10,
                check=True
            )
            
            # 检查连接结果
            if result and ("connected" in result.stdout or "already" in result.stdout):
                # 验证设备是否真正连接
                if self._verify_connection(emulator["address"]):
                    print(f"成功连接到模拟器: {name}")
                    return True
            
            print(f"连接模拟器失败: {name}")
            print(f"ADB输出: {result.stdout if result else '无输出'}")
            return False
            
        except subprocess.TimeoutExpired:
            print(f"连接超时: {name}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"ADB命令执行失败: {e.stderr if e.stderr else str(e)}")
            return False
        except Exception as e:
            print(f"连接模拟器出错: {str(e)}")
            return False
    
    def _disconnect_emulator(self, address: str) -> None:
        """断开指定地址的模拟器连接"""
        try:
            subprocess.run(
                ["adb", "disconnect", address],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )
        except Exception:
            pass
    
    def _verify_connection(self, address: str) -> bool:
        """验证设备是否真正连接"""
        try:
            result = subprocess.run(
                ["adb", "-s", address, "shell", "getprop", "ro.product.model"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=5,
                check=True
            )
            return bool(result.stdout.strip())
        except Exception:
            return False
    
    def disconnect_emulator(self, name: str) -> bool:
        """
        断开与指定模拟器的连接
        
        Args:
            name: 模拟器名称
            
        Returns:
            bool: 是否断开成功
        """
        emulator = self.get_emulator(name)
        if not emulator:
            print(f"模拟器不存在: {name}")
            return False
        
        try:
            # 断开与模拟器的连接
            result = subprocess.run(
                ["adb", "disconnect", emulator["address"]], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # 检查断开结果
            if "disconnected" in result.stdout:
                print(f"成功断开与模拟器的连接: {name}")
                return True
            else:
                print(f"断开与模拟器的连接失败: {name}")
                return False
        except Exception as e:
            print(f"断开与模拟器的连接出错: {e}")
            return False
    
    def start_emulator(self, name: str) -> bool:
        """
        启动指定模拟器
        
        Args:
            name: 模拟器名称
            
        Returns:
            bool: 是否启动成功
        """
        emulator = self.get_emulator(name)
        if not emulator:
            print(f"模拟器不存在: {name}")
            return False
        
        try:
            # 根据模拟器类型启动
            if emulator["type"] == "mumu":
                # 启动MuMu模拟器
                subprocess.Popen(
                    [os.path.join(emulator["path"], "MEmu.exe")],
                    cwd=emulator["path"]
                )
            elif emulator["type"] == "nox":
                # 启动夜神模拟器
                subprocess.Popen(
                    [os.path.join(emulator["path"], "Nox.exe")],
                    cwd=emulator["path"]
                )
            elif emulator["type"] == "bluestacks":
                # 启动蓝叠模拟器
                subprocess.Popen(
                    [os.path.join(emulator["path"], "HD-Player.exe")],
                    cwd=emulator["path"]
                )
            elif emulator["type"] == "ldplayer":
                # 启动雷电模拟器
                subprocess.Popen(
                    [os.path.join(emulator["path"], "dnplayer.exe")],
                    cwd=emulator["path"]
                )
            else:
                print(f"不支持启动此类型的模拟器: {emulator['type']}")
                return False
            
            print(f"已发送启动命令到模拟器: {name}")
            return True
        except Exception as e:
            print(f"启动模拟器出错: {e}")
            return False
    
    def stop_emulator(self, name: str) -> bool:
        """
        停止指定模拟器
        
        Args:
            name: 模拟器名称
            
        Returns:
            bool: 是否停止成功
        """
        emulator = self.get_emulator(name)
        if not emulator:
            print(f"模拟器不存在: {name}")
            return False
        
        try:
            # 根据模拟器类型停止
            if emulator["type"] == "adb":
                # 使用ADB关闭模拟器
                subprocess.run(
                    ["adb", "-s", emulator["address"], "shell", "reboot", "-p"], 
                    capture_output=True, 
                    check=True
                )
            else:
                # 使用任务管理器关闭模拟器
                if emulator["type"] == "mumu":
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "MEmu.exe"], 
                        capture_output=True, 
                        check=True
                    )
                elif emulator["type"] == "nox":
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "Nox.exe"], 
                        capture_output=True, 
                        check=True
                    )
                elif emulator["type"] == "bluestacks":
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "HD-Player.exe"], 
                        capture_output=True, 
                        check=True
                    )
                elif emulator["type"] == "ldplayer":
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "dnplayer.exe"], 
                        capture_output=True, 
                        check=True
                    )
                else:
                    print(f"不支持停止此类型的模拟器: {emulator['type']}")
                    return False
            
            print(f"已发送停止命令到模拟器: {name}")
            return True
        except Exception as e:
            print(f"停止模拟器出错: {e}")
            return False

# 创建全局模拟器实例
emulator_manager = Emulator()

if __name__ == "__main__":
    # 检测模拟器
    emulator_manager.detect_emulators()
    
    # 列出模拟器
    emulators = emulator_manager.list_emulators()
    print(f"检测到的模拟器: {emulators}")
    
    # 如果有模拟器，尝试连接第一个
    if emulators:
        emulator_manager.connect_emulator(emulators[0])