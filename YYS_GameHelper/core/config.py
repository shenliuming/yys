"""
配置模块 - 处理配置信息
"""
import os
import json
import yaml
from typing import Dict, Any, Optional, Union, List

class Config:
    """配置类，负责处理配置信息"""
    
    def __init__(self, config_file: str = "config.yaml"):
        """
        初始化配置模块
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = {}
        
        # 加载配置文件
        self.load()
    
    def load(self) -> bool:
        """
        加载配置文件
        
        Returns:
            bool: 是否加载成功
        """
        if not os.path.exists(self.config_file):
            print(f"配置文件不存在: {self.config_file}")
            return False
        
        try:
            # 根据文件扩展名选择加载方式
            ext = os.path.splitext(self.config_file)[1].lower()
            
            if ext == '.json':
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            elif ext in ['.yaml', '.yml']:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
            else:
                print(f"不支持的配置文件格式: {ext}")
                return False
            
            print(f"成功加载配置文件: {self.config_file}")
            return True
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return False
    
    def save(self) -> bool:
        """
        保存配置文件
        
        Returns:
            bool: 是否保存成功
        """
        try:
            # 创建目录
            os.makedirs(os.path.dirname(os.path.abspath(self.config_file)), exist_ok=True)
            
            # 根据文件扩展名选择保存方式
            ext = os.path.splitext(self.config_file)[1].lower()
            
            if ext == '.json':
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
            elif ext in ['.yaml', '.yml']:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            else:
                print(f"不支持的配置文件格式: {ext}")
                return False
            
            print(f"成功保存配置文件: {self.config_file}")
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置项键名，支持点号分隔的多级键名
            default: 默认值
            
        Returns:
            Any: 配置项值
        """
        # 处理多级键名
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置项
        
        Args:
            key: 配置项键名，支持点号分隔的多级键名
            value: 配置项值
        """
        # 处理多级键名
        keys = key.split('.')
        config = self.config
        
        # 遍历除最后一个键以外的所有键
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            elif not isinstance(config[k], dict):
                # 如果当前键对应的值不是字典，则将其转换为字典
                config[k] = {}
            
            config = config[k]
        
        # 设置最后一个键的值
        config[keys[-1]] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        更新配置
        
        Args:
            config_dict: 配置字典
        """
        self._update_dict(self.config, config_dict)
    
    def _update_dict(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        递归更新字典
        
        Args:
            target: 目标字典
            source: 源字典
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                # 如果值是字典且目标中已存在该键，则递归更新
                self._update_dict(target[key], value)
            else:
                # 否则直接覆盖
                target[key] = value
    
    def reset(self) -> None:
        """重置配置"""
        self.config = {}
    
    def __getitem__(self, key: str) -> Any:
        """
        通过下标访问配置项
        
        Args:
            key: 配置项键名
            
        Returns:
            Any: 配置项值
        """
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """
        通过下标设置配置项
        
        Args:
            key: 配置项键名
            value: 配置项值
        """
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """
        检查配置项是否存在
        
        Args:
            key: 配置项键名
            
        Returns:
            bool: 是否存在
        """
        return self.get(key) is not None
    
    def __str__(self) -> str:
        """
        转换为字符串
        
        Returns:
            str: 配置字符串
        """
        return json.dumps(self.config, ensure_ascii=False, indent=2)

# 创建默认配置
def create_default_config(config_file: str = "config.yaml") -> Config:
    """
    创建默认配置
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        Config: 配置对象
    """
    config = Config(config_file)
    
    # 设备配置
    config.set("device.name", "default")
    config.set("device.type", "android")
    config.set("device.address", "127.0.0.1:5555")
    config.set("device.screenshot_method", "adb")
    config.set("device.control_method", "adb")
    
    # 游戏配置
    config.set("game.package", "com.netease.onmyoji")
    config.set("game.activity", "com.netease.onmyoji.MainActivity")
    
    # 界面配置
    config.set("ui.scale", 1.0)
    config.set("ui.resolution", [1280, 720])
    
    # 操作配置
    config.set("operation.click_delay", [0.3, 0.5])
    config.set("operation.swipe_delay", [0.5, 0.8])
    config.set("operation.random_offset", 10)
    
    # OCR配置
    config.set("ocr.engine", "paddle")
    config.set("ocr.lang", "ch")
    config.set("ocr.score", 0.6)
    
    # 日志配置
    config.set("log.level", "INFO")
    config.set("log.dir", "./log")
    
    # 保存配置
    config.save()
    
    return config

# 全局配置实例
config = Config()

if __name__ == "__main__":
    # 测试配置功能
    test_config = create_default_config("test_config.yaml")
    print(test_config)
    
    # 获取配置项
    print(f"设备名称: {test_config.get('device.name')}")
    print(f"设备地址: {test_config.get('device.address')}")
    
    # 设置配置项
    test_config.set("device.name", "模拟器")
    test_config.set("device.address", "127.0.0.1:7555")
    
    # 保存配置
    test_config.save()
    
    # 重新加载配置
    test_config.load()
    print(f"更新后的设备名称: {test_config.get('device.name')}")
    print(f"更新后的设备地址: {test_config.get('device.address')}")