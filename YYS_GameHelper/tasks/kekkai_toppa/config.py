# -*- coding: utf-8 -*-
"""
结界突破任务配置
"""

from typing import Dict, Any, List
from datetime import timedelta
from pydantic import BaseModel, Field
from enum import Enum


class ToppaMode(str, Enum):
    """突破模式"""
    PERSONAL = "personal"  # 个人突破
    GUILD = "guild"       # 阴阳寮突破


class KekkaiToppaConfig:
    """结界突破配置类"""
    
    def __init__(self):
        # 默认配置
        self.default_config = {
            # 基础设置
            "task_name": "结界突破",
            "enable": True,
            
            # 突破模式
            "mode": ToppaMode.PERSONAL,  # 突破模式：personal(个人突破) 或 guild(阴阳寮突破)
            
            # 时间和次数限制
            "limit_time_minutes": 99999,  # 时间限制（分钟）
            "limit_count": 99999,  # 次数限制
            
            # 个人突破配置
            "personal_areas": [1, 2, 3, 4, 5, 6, 7, 8],  # 个人突破区域列表
            "skip_failed_areas": True,  # 跳过失败的区域
            
            # 阴阳寮突破配置
            "guild_admin_mode": False,  # 寮管理员模式，可以开启寮突破
            "auto_select_guild": True,  # 自动选择第一个寮
            "lock_team": False,  # 锁定队伍
            "next_guild_toppa_hour": 7,  # 下次寮突破时间（小时）
            
            # 战斗设置
            "skip_difficult": True,  # 跳过困难区域（失败后不再攻打）
            "random_delay": True,  # 随机延迟（2-10秒）
            "enable_lock_team": False,  # 锁定队伍
            
            # 御魂切换配置
            "enable_switch_soul": False,  # 启用御魂切换
            "soul_group_name": "",  # 御魂组名称
            "soul_team_name": "",  # 御魂队伍名称
            
            # 高级设置
            "auto_start_if_admin": False,  # 作为寮管理自动开启结界突破
            "retry_failed_areas": False,  # 重试失败的区域
            "battle_timeout": 180,  # 单次战斗超时时间（秒）
            
            # 区域优先级设置（1-8，数字越小优先级越高）
            "area_priority": [1, 2, 3, 4, 5, 6, 7, 8],
            
            # 图像识别设置
            "image_threshold": 0.8,  # 图像匹配阈值
            "ocr_confidence": 0.7,  # OCR识别置信度
            
            # 调试设置
            "debug_mode": False,  # 调试模式
            "save_screenshots": False,  # 保存截图
        }
        
        # 当前配置
        self.config = self.default_config.copy()
    
    def load_config(self, config_dict: Dict[str, Any] = None) -> Dict[str, Any]:
        """加载配置
        
        Args:
            config_dict: 配置字典，如果为None则使用默认配置
            
        Returns:
            Dict: 加载后的配置
        """
        if config_dict is None:
            config_dict = {}
        
        # 合并配置
        for key, value in config_dict.items():
            if key in self.default_config:
                self.config[key] = value
        
        return self.config
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.config.copy()
    
    def update_config(self, key: str, value: Any) -> bool:
        """更新单个配置项
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            bool: 是否更新成功
        """
        if key in self.default_config:
            self.config[key] = value
            return True
        return False
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self.default_config.copy()
    
    def validate_config(self) -> tuple[bool, str]:
        """验证配置有效性
        
        Returns:
            tuple: (是否有效, 错误信息)
        """
        # 检查时间限制
        if self.config["limit_time_minutes"] <= 0:
            return False, "时间限制必须大于0"
        
        # 检查次数限制
        if self.config["limit_count"] <= 0:
            return False, "次数限制必须大于0"
        
        # 检查战斗超时时间
        if self.config["battle_timeout"] <= 0:
            return False, "战斗超时时间必须大于0"
        
        # 检查区域优先级
        priority = self.config["area_priority"]
        if not isinstance(priority, list) or len(priority) != 8:
            return False, "区域优先级必须是包含8个元素的列表"
        
        if set(priority) != set(range(1, 9)):
            return False, "区域优先级必须包含1-8的所有数字"
        
        # 检查阈值范围
        if not (0 < self.config["image_threshold"] <= 1):
            return False, "图像匹配阈值必须在0-1之间"
        
        if not (0 < self.config["ocr_confidence"] <= 1):
            return False, "OCR识别置信度必须在0-1之间"
        
        return True, ""
    
    def get_timedelta(self) -> timedelta:
        """获取时间限制的timedelta对象"""
        return timedelta(minutes=self.config["limit_time_minutes"])
    
    def get_sorted_areas(self) -> list[int]:
        """获取按优先级排序的区域索引列表
        
        Returns:
            list: 区域索引列表（0-7），按优先级排序
        """
        priority = self.config["area_priority"]
        # 创建(优先级, 索引)的元组列表
        priority_index_pairs = [(priority[i], i) for i in range(8)]
        # 按优先级排序
        priority_index_pairs.sort(key=lambda x: x[0])
        # 返回索引列表
        return [pair[1] for pair in priority_index_pairs]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.config.copy()
    
    def from_dict(self, config_dict: Dict[str, Any]):
        """从字典加载配置"""
        self.load_config(config_dict)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"KekkaiToppaConfig({self.config})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()


# 预定义的配置模板
CONFIG_TEMPLATES = {
    "default": {
        "task_name": "结界突破",
        "enable": True,
        "mode": ToppaMode.PERSONAL,
        "limit_time_minutes": 99999,
        "limit_count": 99999,
        "personal_areas": [1, 2, 3, 4, 5, 6, 7, 8],
        "skip_failed_areas": True,
        "guild_admin_mode": False,
        "auto_select_guild": True,
        "lock_team": False,
        "next_guild_toppa_hour": 7,
        "skip_difficult": True,
        "random_delay": True,
        "enable_lock_team": False,
        "enable_switch_soul": False,
        "soul_group_name": "",
        "soul_team_name": "",
        "auto_start_if_admin": False,
        "retry_failed_areas": False,
        "battle_timeout": 180,
        "area_priority": [1, 2, 3, 4, 5, 6, 7, 8],
        "image_threshold": 0.8,
        "ocr_confidence": 0.7,
        "debug_mode": False,
        "save_screenshots": False,
    },
    
    "quick": {
        "task_name": "结界突破-快速",
        "enable": True,
        "mode": ToppaMode.PERSONAL,
        "limit_time_minutes": 30,
        "limit_count": 20,
        "personal_areas": [1, 2, 3, 4, 5, 6, 7, 8],
        "skip_failed_areas": True,
        "guild_admin_mode": False,
        "auto_select_guild": True,
        "lock_team": True,
        "next_guild_toppa_hour": 7,
        "skip_difficult": True,
        "random_delay": False,
        "enable_lock_team": True,
        "enable_switch_soul": False,
        "soul_group_name": "",
        "soul_team_name": "",
        "auto_start_if_admin": False,
        "retry_failed_areas": False,
        "battle_timeout": 120,
        "area_priority": [1, 2, 3, 4, 5, 6, 7, 8],
        "image_threshold": 0.8,
        "ocr_confidence": 0.7,
        "debug_mode": False,
        "save_screenshots": False,
    },
    
    "thorough": {
        "task_name": "结界突破-彻底",
        "enable": True,
        "mode": ToppaMode.GUILD,
        "limit_time_minutes": 120,
        "limit_count": 100,
        "personal_areas": [1, 2, 3, 4, 5, 6, 7, 8],
        "skip_failed_areas": False,
        "guild_admin_mode": True,
        "auto_select_guild": True,
        "lock_team": False,
        "next_guild_toppa_hour": 7,
        "skip_difficult": False,
        "random_delay": True,
        "enable_lock_team": False,
        "enable_switch_soul": False,
        "soul_group_name": "",
        "soul_team_name": "",
        "auto_start_if_admin": True,
        "retry_failed_areas": True,
        "battle_timeout": 300,
        "area_priority": [1, 2, 3, 4, 5, 6, 7, 8],
        "image_threshold": 0.8,
        "ocr_confidence": 0.7,
        "debug_mode": False,
        "save_screenshots": False,
    },
    
    "debug": {
        "task_name": "结界突破-调试",
        "enable": True,
        "mode": ToppaMode.PERSONAL,
        "limit_time_minutes": 10,
        "limit_count": 5,
        "personal_areas": [1, 2, 3, 4, 5, 6, 7, 8],
        "skip_failed_areas": True,
        "guild_admin_mode": False,
        "auto_select_guild": True,
        "lock_team": False,
        "next_guild_toppa_hour": 7,
        "skip_difficult": True,
        "random_delay": False,
        "enable_lock_team": False,
        "enable_switch_soul": False,
        "soul_group_name": "",
        "soul_team_name": "",
        "auto_start_if_admin": False,
        "retry_failed_areas": False,
        "battle_timeout": 60,
        "area_priority": [1, 2, 3, 4, 5, 6, 7, 8],
        "image_threshold": 0.8,
        "ocr_confidence": 0.7,
        "debug_mode": True,
        "save_screenshots": True,
    },
}


def get_config_template(template_name: str = "default") -> Dict[str, Any]:
    """获取配置模板
    
    Args:
        template_name: 模板名称
        
    Returns:
        Dict: 配置模板
    """
    return CONFIG_TEMPLATES.get(template_name, CONFIG_TEMPLATES["default"]).copy()


def create_config(template_name: str = "default", **kwargs) -> KekkaiToppaConfig:
    """创建配置对象
    
    Args:
        template_name: 模板名称
        **kwargs: 额外的配置参数
        
    Returns:
        KekkaiToppaConfig: 配置对象
    """
    config = KekkaiToppaConfig()
    template = get_config_template(template_name)
    template.update(kwargs)
    config.load_config(template)
    return config