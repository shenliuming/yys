# -*- coding: utf-8 -*-
"""
简化配置系统
支持动态配置、模板化、热重载
"""

import json
import os
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .logger import logger


@dataclass
class TaskConfig:
    """任务配置基类"""
    name: str
    enabled: bool = True
    priority: str = "normal"  # critical, high, normal, low
    timeout: int = 3600  # 超时时间（秒）
    retry_count: int = 3  # 重试次数
    retry_interval: float = 1.0  # 重试间隔（秒）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建"""
        return cls(**data)


@dataclass
class KekkaiToppaConfig(TaskConfig):
    """结界突破配置"""
    mode: str = "personal"  # personal, guild
    limit_time_minutes: int = 99999
    limit_count: int = 99999
    skip_failed_areas: bool = True
    random_delay: bool = True
    enable_lock_team: bool = False
    personal_areas: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5, 6, 7, 8])
    guild_admin_mode: bool = False
    
    # 资源清理触发条件
    cleanup_triggers: Dict[str, Any] = field(default_factory=lambda: {
        "time_based": {
            "enabled": True,
            "interval_minutes": 30  # 每30分钟检查一次
        },
        "count_based": {
            "enabled": True,
            "max_scrolls": 50  # 超过50个卷轴就清理
        }
    })


@dataclass
class ExplorationConfig(TaskConfig):
    """探索配置"""
    mode: str = "single"  # single, team
    chapter: int = 28
    difficulty: str = "hard"  # normal, hard
    team_size: int = 1
    auto_invite: bool = False
    max_duration_minutes: int = 30
    
    # 资源清理触发条件
    cleanup_triggers: Dict[str, Any] = field(default_factory=lambda: {
        "time_based": {
            "enabled": True,
            "interval_minutes": 30
        },
        "inventory_full": {
            "enabled": True,
            "check_interval_minutes": 5
        }
    })


class ConfigTemplate:
    """配置模板"""
    
    TEMPLATES = {
        "kekkai_toppa_quick": {
            "name": "结界突破-快速",
            "mode": "personal",
            "limit_count": 10,
            "skip_failed_areas": True,
            "random_delay": False
        },
        "kekkai_toppa_full": {
            "name": "结界突破-完整",
            "mode": "personal",
            "limit_time_minutes": 120,
            "skip_failed_areas": False,
            "random_delay": True
        },
        "exploration_solo": {
            "name": "探索-单人",
            "mode": "single",
            "chapter": 28,
            "difficulty": "hard",
            "max_duration_minutes": 30
        },
        "exploration_team": {
            "name": "探索-组队",
            "mode": "team",
            "chapter": 28,
            "team_size": 3,
            "auto_invite": True,
            "max_duration_minutes": 60
        }
    }
    
    @classmethod
    def get_template(cls, template_name: str) -> Optional[Dict[str, Any]]:
        """获取模板"""
        return cls.TEMPLATES.get(template_name)
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """列出所有模板"""
        return list(cls.TEMPLATES.keys())
    
    @classmethod
    def apply_template(cls, config_class, template_name: str, overrides: Dict[str, Any] = None):
        """应用模板创建配置"""
        template = cls.get_template(template_name)
        if not template:
            raise ValueError(f"模板不存在: {template_name}")
        
        # 合并覆盖参数
        if overrides:
            template = {**template, **overrides}
        
        return config_class.from_dict(template)


class SimpleConfigManager:
    """简化配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.configs: Dict[str, TaskConfig] = {}
        self.config_files: Dict[str, Path] = {}
        
    def register_config(self, config_id: str, config: TaskConfig, save_to_file: bool = True):
        """注册配置"""
        self.configs[config_id] = config
        
        if save_to_file:
            config_file = self.config_dir / f"{config_id}.json"
            self.config_files[config_id] = config_file
            self._save_config_to_file(config_id)
        
        logger.info(f"注册配置: {config_id}")
    
    def get_config(self, config_id: str) -> Optional[TaskConfig]:
        """获取配置"""
        return self.configs.get(config_id)
    
    def update_config(self, config_id: str, updates: Dict[str, Any]):
        """更新配置"""
        if config_id not in self.configs:
            raise ValueError(f"配置不存在: {config_id}")
        
        config = self.configs[config_id]
        config_dict = config.to_dict()
        config_dict.update(updates)
        
        # 重新创建配置对象
        config_class = type(config)
        self.configs[config_id] = config_class.from_dict(config_dict)
        
        # 保存到文件
        if config_id in self.config_files:
            self._save_config_to_file(config_id)
        
        logger.info(f"更新配置: {config_id}")
    
    def load_config_from_file(self, config_id: str, config_class, file_path: str = None):
        """从文件加载配置"""
        if file_path:
            config_file = Path(file_path)
        else:
            config_file = self.config_dir / f"{config_id}.json"
        
        if not config_file.exists():
            logger.warning(f"配置文件不存在: {config_file}")
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = config_class.from_dict(data)
            self.configs[config_id] = config
            self.config_files[config_id] = config_file
            
            logger.info(f"从文件加载配置: {config_id}")
            return config
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {config_file} - {e}")
            return None
    
    def _save_config_to_file(self, config_id: str):
        """保存配置到文件"""
        if config_id not in self.configs or config_id not in self.config_files:
            return
        
        config = self.configs[config_id]
        config_file = self.config_files[config_id]
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, ensure_ascii=False, indent=2)
            logger.debug(f"保存配置到文件: {config_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {config_file} - {e}")
    
    def create_from_template(self, config_id: str, config_class, template_name: str, 
                           overrides: Dict[str, Any] = None, save_to_file: bool = True):
        """从模板创建配置"""
        config = ConfigTemplate.apply_template(config_class, template_name, overrides)
        self.register_config(config_id, config, save_to_file)
        return config
    
    def list_configs(self) -> List[str]:
        """列出所有配置"""
        return list(self.configs.keys())
    
    def remove_config(self, config_id: str):
        """删除配置"""
        if config_id in self.configs:
            del self.configs[config_id]
        
        if config_id in self.config_files:
            config_file = self.config_files[config_id]
            if config_file.exists():
                config_file.unlink()
            del self.config_files[config_id]
        
        logger.info(f"删除配置: {config_id}")
    
    def reload_all_configs(self):
        """重新加载所有配置文件"""
        for config_id, config_file in self.config_files.items():
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 获取原配置类型
                    original_config = self.configs[config_id]
                    config_class = type(original_config)
                    
                    # 重新创建配置
                    self.configs[config_id] = config_class.from_dict(data)
                    logger.info(f"重新加载配置: {config_id}")
                    
                except Exception as e:
                    logger.error(f"重新加载配置失败: {config_id} - {e}")


# 全局配置管理器
config_manager = SimpleConfigManager()


# 便捷函数
def quick_config(task_type: str, template: str = None, **kwargs) -> TaskConfig:
    """快速创建配置"""
    config_classes = {
        "kekkai_toppa": KekkaiToppaConfig,
        "exploration": ExplorationConfig
    }
    
    config_class = config_classes.get(task_type)
    if not config_class:
        raise ValueError(f"不支持的任务类型: {task_type}")
    
    # 确保有name参数
    if 'name' not in kwargs:
        kwargs['name'] = f"{task_type}_task"
    
    if template:
        return ConfigTemplate.apply_template(config_class, template, kwargs)
    else:
        return config_class(**kwargs)