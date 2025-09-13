# -*- coding: utf-8 -*-
"""
结界突破任务实现
基于OnmyojiAutoScript的RyouToppa功能进行简化适配
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random
from enum import Enum

from core.task import Task
from core.logger import logger
from core.device import Device
from core.screenshot import Screenshot
from core.click import Click
from core.swipe import Swipe
from core.image import Image
from core.ocr import OCR


class ToppaMode(Enum):
    """突破模式枚举"""
    PERSONAL = "personal"  # 个人突破
    GUILD = "guild"       # 阴阳寮突破


class KekkaiToppaTask(Task):
    """结界突破任务类"""
    
    def __init__(self, device=None, name: str = "结界突破"):
        super().__init__(name)
        self.device = device
        self.device_manager = device  # 添加device_manager属性以保持兼容性
        self.task_name = "结界突破"
        self.current_count = 0
        self.start_time = None
        self.area_cache = {}  # 区域状态缓存
        
        # 设备相关组件
        if device:
            self.screenshot = Screenshot(device)
            self.click = Click(device)
            self.swipe = Swipe(device)
            self.matcher = Image()
            self.ocr = OCR()
        else:
            self.screenshot = None
            self.click = None
            self.swipe = None
            self.matcher = None
            self.ocr = None
        
        # 配置参数
        self.config = {
            "mode": ToppaMode.PERSONAL,  # 突破模式
            "limit_time_minutes": 99999,  # 时间限制（分钟）
            "limit_count": 99999,  # 次数限制
            "skip_failed_areas": True,  # 跳过失败区域
            "random_delay": True,  # 随机延迟
            "enable_lock_team": False,  # 锁定队伍
            "personal_areas": [1, 2, 3, 4, 5, 6, 7, 8],  # 个人突破区域
            "guild_admin_mode": False,  # 寮管理员模式
        }
        
        # 8个区域的配置映射
        self.area_map = [
            {
                "name": "区域1",
                "click_pos": (621, 199),  # 点击位置
                "fail_check_pos": (673, 162),  # 失败检查位置
                "finished_check_pos": (705, 187),  # 完成检查位置
            },
            {
                "name": "区域2", 
                "click_pos": (954, 200),
                "fail_check_pos": (1011, 161),
                "finished_check_pos": (1033, 187),
            },
            {
                "name": "区域3",
                "click_pos": (623, 336),
                "fail_check_pos": (702, 303),
                "finished_check_pos": (705, 330),
            },
            {
                "name": "区域4",
                "click_pos": (949, 332),
                "fail_check_pos": (1036, 302),
                "finished_check_pos": (1046, 321),
            },
            {
                "name": "区域5",
                "click_pos": (625, 466),
                "fail_check_pos": (702, 434),
                "finished_check_pos": (697, 454),
            },
            {
                "name": "区域6",
                "click_pos": (959, 466),
                "fail_check_pos": (1030, 435),
                "finished_check_pos": (1071, 463),
            },
            {
                "name": "区域7",
                "click_pos": (613, 594),
                "fail_check_pos": (703, 575),
                "finished_check_pos": (693, 594),
            },
            {
                "name": "区域8",
                "click_pos": (951, 594),
                "fail_check_pos": (1036, 571),
                "finished_check_pos": (1033, 594),
            },
        ]
    
    def _run(self) -> bool:
        """执行结界突破任务"""
        try:
            logger.info(f"开始执行{self.task_name}任务，模式: {self.config.get('mode', ToppaMode.PERSONAL)}")
            self.start_time = datetime.now()
            self.current_count = 0
            
            # 根据模式选择不同的执行逻辑
            if self.config.get('mode', ToppaMode.PERSONAL) == ToppaMode.GUILD:
                return self._run_guild_toppa()
            else:
                return self._run_personal_toppa()
                
        except Exception as e:
            logger.error(f"{self.task_name}任务执行失败: {e}")
            return False
    
    def _run_personal_toppa(self) -> bool:
        """执行个人突破"""
        logger.info("开始个人突破")
        
        # 导航到结界突破页面
        if not self._navigate_to_kekkai_toppa():
            logger.error("无法导航到结界突破页面")
            return False
        
        # 检查突破状态
        toppa_status = self._check_toppa_status()
        if toppa_status == "completed":
            logger.info("结界突破已完成")
            return True
        elif toppa_status == "not_started":
            logger.warning("结界突破未开启")
            return False
        
        # 设置队伍锁定状态
        self._set_team_lock()
        
        # 开始突破循环
        success_count = 0
        attempt_count = 0
        start_time = datetime.now()
        failed_areas = set()  # 记录失败的区域
        
        while attempt_count < self.config["limit_count"]:
            # 检查时间限制
            elapsed_time = datetime.now() - start_time
            if elapsed_time.total_seconds() > self.config["limit_time_minutes"] * 60:
                logger.info(f"达到时间限制 {self.config['limit_time_minutes']} 分钟")
                break
            
            # 尝试攻击区域
            areas_to_attack = self.config.get("personal_areas", [1, 2, 3, 4, 5, 6, 7, 8])
            attacked_this_round = False
            
            for area_id in areas_to_attack:
                # 跳过失败的区域
                if self.config.get("skip_failed_areas", True) and area_id in failed_areas:
                    continue
                
                attack_result = self._attack_area(area_id - 1)  # 转换为索引
                if attack_result:
                    success_count += 1
                    attacked_this_round = True
                    self.current_count += 1
                    logger.info(f"成功攻击区域 {area_id}")
                else:
                    failed_areas.add(area_id)
                    logger.warning(f"区域 {area_id} 攻击失败，标记为失败区域")
                
                attempt_count += 1
                if attempt_count >= self.config["limit_count"]:
                    break
                
                # 随机延迟
                if self.config.get("random_delay", True):
                    delay = random.uniform(2.0, 5.0)
                    time.sleep(delay)
            
            # 如果这轮没有攻击任何区域，说明都完成或失败了
            if not attacked_this_round:
                logger.info("没有可攻击的区域了")
                break
        
        logger.info(f"个人突破完成，成功攻击 {success_count} 次，总尝试 {attempt_count} 次")
        return success_count > 0
    
    def _run_guild_toppa(self) -> bool:
        """执行阴阳寮突破"""
        logger.info("开始阴阳寮突破")
        
        # 导航到结界突破页面
        if not self._navigate_to_kekkai_toppa():
            logger.error("无法导航到结界突破页面")
            return False
        
        # 检查寮突破状态
        guild_status = self._check_guild_toppa_status()
        
        if guild_status == "not_started":
            if self.config.get("guild_admin_mode", False):
                logger.info("作为寮管理员，尝试开启寮突破")
                if not self._start_guild_toppa():
                    logger.error("无法开启寮突破")
                    return False
            else:
                logger.warning("寮突破未开启，且非管理员模式")
                return False
        elif guild_status == "completed":
            logger.info("寮突破已100%完成")
            self._plan_next_guild_toppa()
            return True
        
        # 设置队伍锁定状态
        self._set_team_lock()
        
        # 开始寮突破循环
        success_count = 0
        attempt_count = 0
        start_time = datetime.now()
        failed_areas = set()
        
        while attempt_count < self.config["limit_count"]:
            # 检查时间限制
            elapsed_time = datetime.now() - start_time
            if elapsed_time.total_seconds() > self.config["limit_time_minutes"] * 60:
                logger.info(f"达到时间限制 {self.config['limit_time_minutes']} 分钟")
                break
            
            # 检查是否还有攻击机会
            if not self._has_guild_ticket():
                logger.info("没有攻击机会了，1小时后重试")
                break
            
            # 尝试攻击区域
            attacked_this_round = False
            for area_id in range(1, 9):
                if area_id in failed_areas and self.config.get("skip_failed_areas", True):
                    continue
                
                attack_result = self._attack_guild_area(area_id - 1)  # 转换为索引
                if attack_result:
                    success_count += 1
                    attacked_this_round = True
                    self.current_count += 1
                    logger.info(f"成功攻击寮区域 {area_id}")
                else:
                    failed_areas.add(area_id)
                    logger.warning(f"寮区域 {area_id} 攻击失败")
                
                attempt_count += 1
                if attempt_count >= self.config["limit_count"]:
                    break
                
                # 随机延迟
                if self.config.get("random_delay", True):
                    delay = random.uniform(2.0, 10.0)  # 寮突破延迟更长
                    time.sleep(delay)
            
            if not attacked_this_round:
                logger.info("没有可攻击的寮区域了")
                break
        
        logger.info(f"寮突破完成，成功攻击 {success_count} 次，总尝试 {attempt_count} 次")
        return success_count > 0
    
    def _navigate_to_kekkai_toppa(self) -> bool:
        """导航到结界突破页面"""
        logger.info("导航到结界突破页面")
        
        # 这里需要根据实际游戏界面实现导航逻辑
        # 暂时返回True，实际使用时需要实现具体的导航代码
        time.sleep(2)
        return True
    
    def _check_toppa_status(self) -> str:
        """检查结界突破状态
        
        Returns:
            str: 'active' - 进行中, 'completed' - 已完成, 'not_started' - 未开始
        """
        logger.info("检查结界突破状态")
        
        # 这里需要根据实际游戏界面实现状态检查逻辑
        # 暂时返回active，实际使用时需要实现具体的检查代码
        return "active"
    
    def _set_team_lock(self):
        """设置队伍锁定状态"""
        if self.config["enable_lock_team"]:
            logger.info("锁定队伍")
            # 实现锁定队伍的逻辑
        else:
            logger.info("解锁队伍")
            # 实现解锁队伍的逻辑
    
    def _run_toppa_loop(self) -> bool:
        """执行突破循环"""
        area_index = 0
        success = True
        
        while True:
            # 检查是否还有进攻机会
            if not self._has_ticket():
                logger.info("没有进攻机会了，1小时后重试")
                success = False
                break
            
            # 检查次数限制
            if self.current_count >= self.config["limit_count"]:
                logger.warning("已达到进攻次数限制")
                break
            
            # 检查时间限制
            if datetime.now() >= self.start_time + self.config["limit_time"]:
                logger.warning("已达到时间限制")
                break
            
            # 进攻区域
            attack_result = self._attack_area(area_index)
            
            if not attack_result:
                # 当前区域不可用，尝试下一个区域
                area_index += 1
                if area_index >= len(self.area_map):
                    logger.warning("所有区域都不可用，刷新区域缓存")
                    area_index = 0
                    self._flush_area_cache()
                continue
        
        return success
    
    def _has_ticket(self) -> bool:
        """检查是否还有进攻机会"""
        # 这里需要实现OCR识别进攻机会数的逻辑
        # 暂时返回True，实际使用时需要实现具体的检查代码
        return True
    
    def _attack_area(self, area_index: int) -> bool:
        """进攻指定区域
        
        Args:
            area_index: 区域索引 (0-7)
            
        Returns:
            bool: 是否成功进攻
        """
        if area_index >= len(self.area_map):
            return False
        
        area = self.area_map[area_index]
        logger.info(f"尝试进攻{area['name']}")
        
        # 检查区域状态
        if not self._check_area_available(area_index):
            logger.info(f"{area['name']}不可用，跳过")
            return False
        
        # 点击区域
        click_pos = area["click_pos"]
        if self.device_manager:
            self.device_manager.click(click_pos[0], click_pos[1])
        
        # 随机延迟
        if self.config["random_delay"]:
            delay = random.uniform(2, 10)
            time.sleep(delay)
        
        # 等待进入战斗
        time.sleep(3)
        
        # 执行战斗
        battle_result = self._run_battle()
        
        if battle_result:
            self.current_count += 1
            logger.info(f"{area['name']}进攻成功，当前进攻次数: {self.current_count}")
        else:
            logger.info(f"{area['name']}进攻失败")
            # 标记该区域为失败状态
            self.area_cache[area_index] = "failed"
        
        return battle_result
    
    def _check_area_available(self, area_index: int) -> bool:
        """检查区域是否可用
        
        Args:
            area_index: 区域索引
            
        Returns:
            bool: 区域是否可用
        """
        # 检查缓存中的区域状态
        if area_index in self.area_cache:
            if self.area_cache[area_index] == "failed" and self.config["skip_difficult"]:
                return False
            elif self.area_cache[area_index] == "finished":
                return False
        
        area = self.area_map[area_index]
        
        # 这里需要实现图像识别逻辑来检查区域状态
        # 检查是否已完成
        # 检查是否失败
        
        # 暂时返回True，实际使用时需要实现具体的检查代码
        return True
    
    def _run_battle(self) -> bool:
        """执行战斗
        
        Returns:
            bool: 战斗是否成功
        """
        logger.info("开始战斗")
        
        # 这里需要实现具体的战斗逻辑
        # 包括：
        # 1. 检测战斗开始
        # 2. 等待战斗结束
        # 3. 判断战斗结果
        # 4. 处理战斗后的界面
        
        # 暂时模拟战斗过程
        time.sleep(30)  # 模拟战斗时间
        
        # 暂时返回True，实际使用时需要实现具体的战斗逻辑
        return True
    
    def _check_guild_toppa_status(self) -> str:
        """检查阴阳寮突破状态
        
        Returns:
            str: 'active' - 进行中, 'completed' - 已完成, 'not_started' - 未开始
        """
        logger.info("检查阴阳寮突破状态")
        # 这里需要根据实际游戏界面实现状态检查逻辑
        return "active"
    
    def _start_guild_toppa(self) -> bool:
        """开启阴阳寮突破（管理员功能）"""
        logger.info("开启阴阳寮突破")
        # 这里需要实现开启寮突破的逻辑
        return True
    
    def _has_guild_ticket(self) -> bool:
        """检查是否还有寮突破机会"""
        # 这里需要实现OCR识别寮突破机会数的逻辑
        return True
    
    def _attack_guild_area(self, area_index: int) -> bool:
        """攻击阴阳寮区域
        
        Args:
            area_index: 区域索引 (0-7)
            
        Returns:
            bool: 是否成功攻击
        """
        # 寮突破的攻击逻辑可能与个人突破不同
        return self._attack_area(area_index)
    
    def _plan_next_guild_toppa(self):
        """规划下次寮突破时间"""
        logger.info("寮突破已完成，规划下次突破时间")
        # 这里可以实现自动规划下次寮突破的逻辑
    
    def _flush_area_cache(self):
        """刷新区域缓存"""
        logger.info("刷新区域缓存")
        self.area_cache.clear()
    
    def get_task_config(self) -> Dict:
        """获取任务配置"""
        return {
            "task_name": self.task_name,
            "mode": self.config["mode"].value if isinstance(self.config["mode"], ToppaMode) else self.config["mode"],
            "limit_time_minutes": self.config["limit_time_minutes"],
            "limit_count": self.config["limit_count"],
            "skip_failed_areas": self.config["skip_failed_areas"],
            "random_delay": self.config["random_delay"],
            "enable_lock_team": self.config["enable_lock_team"],
            "personal_areas": self.config["personal_areas"],
            "guild_admin_mode": self.config["guild_admin_mode"],
        }
    
    def update_config(self, config: Dict):
        """更新任务配置"""
        if "mode" in config:
            if isinstance(config["mode"], str):
                self.config["mode"] = ToppaMode(config["mode"])
            else:
                self.config["mode"] = config["mode"]
        if "limit_time_minutes" in config:
            self.config["limit_time_minutes"] = config["limit_time_minutes"]
        if "limit_count" in config:
            self.config["limit_count"] = config["limit_count"]
        if "skip_failed_areas" in config:
            self.config["skip_failed_areas"] = config["skip_failed_areas"]
        if "random_delay" in config:
            self.config["random_delay"] = config["random_delay"]
        if "enable_lock_team" in config:
            self.config["enable_lock_team"] = config["enable_lock_team"]
        if "personal_areas" in config:
            self.config["personal_areas"] = config["personal_areas"]
        if "guild_admin_mode" in config:
            self.config["guild_admin_mode"] = config["guild_admin_mode"]
        
        logger.info(f"更新{self.task_name}配置: {config}")
    
    def run(self) -> bool:
        """执行结界突破任务"""
        try:
            mode = getattr(self.config, 'toppa_mode', ToppaMode.PERSONAL)
            logger.info(f"开始执行结界突破任务，模式: {mode}")
            
            if mode == ToppaMode.PERSONAL:
                return self._run_personal_toppa()
            elif mode == ToppaMode.GUILD:
                return self._run_guild_toppa()
            else:
                logger.error(f"未知的突破模式: {mode}")
                return False
                
        except Exception as e:
            logger.error(f"结界突破任务执行失败: {e}")
            return False