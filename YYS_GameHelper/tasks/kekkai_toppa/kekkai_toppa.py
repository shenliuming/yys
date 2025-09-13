# -*- coding: utf-8 -*-
"""
结界突破任务实现
基于OnmyojiAutoScript的RyouToppa功能进行完整适配
"""

import time
from datetime import datetime, timedelta, time as dt_time
from typing import Dict, List, Tuple, Optional
import random
from enum import Enum

from core.task import Task
from core.logger import logger
from core.device import Device
from core.screenshot import Screenshot
from core.click import Click
from core.swipe import Swipe
# 移除不存在的模块导入
# from core.image import Image
# from core.ocr import OCR
# from module.exception import TaskEnd


class ToppaMode(Enum):
    """突破模式枚举"""
    PERSONAL = "personal"  # 个人突破
    GUILD = "guild"       # 阴阳寮突破


def random_delay(min_value: float = 1.0, max_value: float = 2.0, decimal: int = 1):
    """
    生成一个指定范围内的随机小数
    """
    random_float_in_range = random.uniform(min_value, max_value)
    return (round(random_float_in_range, decimal))


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
            self.matcher = None
            self.ocr = None
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
            "ryou_access": False,  # 寮管理员模式
        }
        
        # 8个区域的配置映射 - 基于OnmyojiAutoScript的area_map结构
        self.area_map = [
            {
                "name": "区域1",
                "fail_sign": ("I_AREA_1_IS_FAILURE_NEW", "I_AREA_1_IS_FAILURE"),
                "rule_click": "C_AREA_1",
                "finished_sign": ("I_AREA_1_FINISHED", "I_AREA_1_FINISHED_NEW")
            },
            {
                "name": "区域2",
                "fail_sign": ("I_AREA_2_IS_FAILURE_NEW", "I_AREA_2_IS_FAILURE"),
                "rule_click": "C_AREA_2",
                "finished_sign": ("I_AREA_2_FINISHED", "I_AREA_2_FINISHED_NEW")
            },
            {
                "name": "区域3",
                "fail_sign": ("I_AREA_3_IS_FAILURE_NEW", "I_AREA_3_IS_FAILURE"),
                "rule_click": "C_AREA_3",
                "finished_sign": ("I_AREA_3_FINISHED", "I_AREA_3_FINISHED_NEW")
            },
            {
                "name": "区域4",
                "fail_sign": ("I_AREA_4_IS_FAILURE_NEW", "I_AREA_4_IS_FAILURE"),
                "rule_click": "C_AREA_4",
                "finished_sign": ("I_AREA_4_FINISHED", "I_AREA_4_FINISHED_NEW")
            },
            {
                "name": "区域5",
                "fail_sign": ("I_AREA_5_IS_FAILURE_NEW", "I_AREA_5_IS_FAILURE"),
                "rule_click": "C_AREA_5",
                "finished_sign": ("I_AREA_5_FINISHED", "I_AREA_5_FINISHED_NEW")
            },
            {
                "name": "区域6",
                "fail_sign": ("I_AREA_6_IS_FAILURE_NEW", "I_AREA_6_IS_FAILURE"),
                "rule_click": "C_AREA_6",
                "finished_sign": ("I_AREA_6_FINISHED", "I_AREA_6_FINISHED_NEW")
            },
            {
                "name": "区域7",
                "fail_sign": ("I_AREA_7_IS_FAILURE_NEW", "I_AREA_7_IS_FAILURE"),
                "rule_click": "C_AREA_7",
                "finished_sign": ("I_AREA_7_FINISHED", "I_AREA_7_FINISHED_NEW")
            },
            {
                "name": "区域8",
                "fail_sign": ("I_AREA_8_IS_FAILURE_NEW", "I_AREA_8_IS_FAILURE"),
                "rule_click": "C_AREA_8",
                "finished_sign": ("I_AREA_8_FINISHED", "I_AREA_8_FINISHED_NEW")
            }
        ]
    
    def _run(self) -> bool:
        """执行结界突破任务 - 基于OnmyojiAutoScript的run方法"""
        try:
            ryou_config = self.config
            time_limit = ryou_config.get('limit_time_minutes', 30)
            time_delta = timedelta(minutes=time_limit)
            
            logger.info(f"开始执行{self.task_name}任务，模式: {self.config.get('mode', ToppaMode.PERSONAL)}")
            self.start_time = datetime.now()
            self.current_count = 0
            
            # 导航到结界突破页面
            if not self._navigate_to_kekkai_toppa():
                logger.error("无法导航到结界突破页面")
                return False
            
            # 检查突破状态
            ryou_toppa_start_flag = True
            ryou_toppa_success_penetration = False
            ryou_toppa_admin_flag = False
            
            # 点击突破 - 检查各种状态
            while True:
                self.screenshot()
                
                # 攻破阴阳寮，说明寮突已开，则退出
                if self._appear("I_SUCCESS_PENETRATION", threshold=0.8):
                    ryou_toppa_start_flag = True
                    ryou_toppa_success_penetration = True
                    break
                # 出现选择寮突说明寮突未开
                elif self._appear("I_SELECT_RYOU_BUTTON", threshold=0.8):
                    ryou_toppa_start_flag = False
                    ryou_toppa_admin_flag = True
                    break
                # 出现晴明说明寮突未开
                elif self._appear("I_NO_SELECT_RYOU", threshold=0.8):
                    ryou_toppa_start_flag = False
                    break
                # 出现寮奖励，说明寮突已开
                elif self._appear("I_RYOU_REWARD", threshold=0.8) or self._appear("I_RYOU_REWARD_90", threshold=0.8):
                    ryou_toppa_start_flag = True
                    break
            
            logger.info(f'ryou_toppa_start_flag: {ryou_toppa_start_flag}')
            logger.info(f'ryou_toppa_success_penetration: {ryou_toppa_success_penetration}')
            
            # 寮突未开 并且有权限，开启寮突，没有权限则标记失败
            if not ryou_toppa_start_flag:
                if ryou_config.get('ryou_access', False) and ryou_toppa_admin_flag:
                    logger.info("作为寮管理，尝试开启今天的寮突")
                    if not self._start_guild_toppa():
                        logger.error("无法开启寮突破")
                        return False
                else:
                    logger.info("寮突破未开启，且你是寮成员")
                    return False
            
            # 100% 攻破，第二天再执行
            if ryou_toppa_success_penetration:
                logger.info('寮突破已100%完成')
                self._plan_next_guild_toppa()
                return True
            
            # 设置队伍锁定状态
            self._set_team_lock()
            
            # 开始突破循环
            area_index = 0
            success = True
            
            while True:
                if not self._has_ticket():
                    logger.info("没有进攻机会了，1小时后重试")
                    success = False
                    break
                    
                if self.current_count >= ryou_config.get('limit_count', 50):
                    logger.warning("已达到进攻次数限制")
                    break
                    
                if datetime.now() >= self.start_time + time_delta:
                    logger.warning("已达到时间限制")
                    break
                
                # 进攻区域
                res = self._attack_area(area_index)
                
                # 如果战斗失败或区域不可用，则弹出当前区域索引，开始进攻下一个
                if not res:
                    area_index += 1
                    if area_index >= len(self.area_map):
                        logger.warning('所有区域都不可用，刷新区域缓存')
                        area_index = 0
                        self._flush_area_cache()
                    continue
            
            return success
                
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
            if self.config.get("ryou_access", False):
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
        
        logger.info(f"结界突破完成，成功攻击 {success_count} 次，总尝试 {attempt_count} 次")
        return success_count > 0
    
    def _appear(self, image_name: str, threshold: float = 0.8) -> bool:
        """检查图像是否出现"""
        if not hasattr(self, 'matcher') or not hasattr(self, 'screenshot'):
            return False
        # 这里需要实现图像匹配逻辑
        return False
    
    def _appear_then_click(self, image_name: str, interval: float = 1.0, threshold: float = 0.8) -> bool:
        """如果图像出现则点击"""
        if self._appear(image_name, threshold):
            # 这里需要实现点击逻辑
            time.sleep(interval)
            return True
        return False
    
    def _click_rule(self, rule_name: str, interval: float = 1.0) -> bool:
        """根据规则点击"""
        # 这里需要实现规则点击逻辑
        time.sleep(interval)
        return False
    
    def _wait_until_appear(self, image_name: str, timeout: float = 30.0) -> bool:
        """等待图像出现"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._appear(image_name):
                return True
            time.sleep(1)
        return False
    
    def _ocr_number(self) -> Tuple[int, int, int]:
        """OCR识别数字"""
        # 这里需要实现OCR识别逻辑
        return 0, 0, 0
    
    def _ui_click(self, from_image: str, to_image: str) -> bool:
        """UI点击切换"""
        if self._appear(from_image):
            return self._appear_then_click(from_image)
        return False
    
    def _run_general_battle(self) -> bool:
        """执行通用战斗"""
        logger.info("开始通用战斗")
        # 这里需要调用通用战斗模块
        time.sleep(30)  # 模拟战斗时间
        return True
    
    def take_screenshot(self):
        """截图"""
        if hasattr(self, 'screenshot') and self.screenshot:
            return self.screenshot.take_screenshot()
        return None
    
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
        """设置队伍锁定状态 - 基于OnmyojiAutoScript的实现"""
        if self.config.get("enable_lock_team", False):
            logger.info("锁定队伍")
            self._ui_click("I_TOPPA_UNLOCK_TEAM", "I_TOPPA_LOCK_TEAM")
        else:
            logger.info("解锁队伍")
            self._ui_click("I_TOPPA_LOCK_TEAM", "I_TOPPA_UNLOCK_TEAM")
    
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
        """检查是否还有进攻机会 - 基于OnmyojiAutoScript的has_ticket方法"""
        # 21点后、次日5点前无限进攻机会
        if datetime.now().hour >= 21 or datetime.now().hour <= 5:
            return True
            
        # 等待突破记录出现并截图
        self._wait_until_appear("I_TOPPA_RECORD")
        self.screenshot()
        
        # OCR识别进攻机会数量
        try:
            cu, res, total = self._ocr_number()
            if cu == 0 and cu + res == total:
                logger.warning('执行轮次失败，没有票了')
                return False
            return True
        except Exception as e:
            logger.error(f"检查进攻机会失败: {e}")
            return False
    
    def _attack_area(self, index: int) -> bool:
        """攻击指定区域 - 基于OnmyojiAutoScript的attack_area方法
        
        Args:
            index: 区域索引 (0-7)
            
        Returns:
            bool: 战斗成功(True) or 战斗失败(False) or 区域不可用（False） or 没有进攻机会（设定下次运行并退出）
        """
        # 每次进攻前检查区域可用性
        if not self._check_area(index):
            return False
        
        # 正式进攻会设定 2s - 10s 的随机延迟，避免攻击间隔及其相近被检测为脚本
        if self.config.get('random_delay', True):
            delay = random_delay(2.0, 10.0)
            time.sleep(delay)
        
        if index >= len(self.area_map):
            return False
            
        area_config = self.area_map[index]
        rule_click = area_config.get("rule_click", "")
        
        # 点击攻击区域，等待攻击按钮出现
        click_failure_count = 0
        while True:
            self.screenshot()
            
            if click_failure_count >= 3:
                logger.warning("点击失败，检查你的点击位置")
                return False
                
            if not self._appear("I_TOPPA_RECORD", threshold=0.85):
                time.sleep(1)
                self.screenshot()
                if self._appear("I_TOPPA_RECORD", threshold=0.85):
                    continue
                logger.info(f"开始攻击区域 [{index + 1}]")
                # 这里应该调用通用战斗模块
                return self._run_general_battle()
            
            if self._appear_then_click("I_FIRE", interval=2, threshold=0.8):
                click_failure_count += 1
                continue
                
            if self._click_rule(rule_click, interval=5):
                continue
    
    def _check_area(self, index: int) -> bool:
        """检查该区域是否攻略失败 - 基于OnmyojiAutoScript的check_area方法
        
        Args:
            index: 区域索引 (0-7)
            
        Returns:
            bool: True表示可以攻击，False表示不可攻击
        """
        if index >= len(self.area_map):
            return False
            
        area_config = self.area_map[index]
        f1, f2 = area_config.get("fail_sign", ("", ""))
        f3, f4 = area_config.get("finished_sign", ("", ""))
        
        self.screenshot()
        
        # 如果该区域已经被攻破则退出
        # 这时候能打过的都打过了，没有能攻打的结界了，代表任务已经完成
        if self._appear(f3, threshold=0.8) or self._appear(f4, threshold=0.8):
            logger.info('结界突破已尝试攻击完成')
            self._plan_next_guild_toppa()
            raise TaskEnd
            
        # 如果该区域攻略失败返回 False
        if self._appear(f1, threshold=0.8) or self._appear(f2, threshold=0.8):
            logger.info(f'区域 [{index + 1}] 攻略失败，跳过')
            return False
            
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
        """规划下次寮突破时间 - 基于OnmyojiAutoScript的plan_tomorrow_ryoutoppa方法"""
        logger.info("寮突破已完成，规划下次突破时间")
        now = datetime.now()
        # 如果时间在00:00-5:00之间则设定时间为当天的自定义时间
        if now.time() < dt_time(5, 0):
            next_hour = self.config.get('next_ryoutoppa_hour', 7)
            logger.info(f"设定今天 {next_hour}:00 进行下次寮突破")
        # 如果时间在05:00-23:59之间则设定时间为明天的自定义时间
        else:
            next_hour = self.config.get('next_ryoutoppa_hour', 7)
            logger.info(f"设定明天 {next_hour}:00 进行下次寮突破")
    
    def _flush_area_cache(self):
        """刷新区域缓存 - 基于OnmyojiAutoScript的flush_area_cache方法"""
        time.sleep(2)
        duration = 0.352
        count = random.randint(1, 3)
        
        for i in range(count):
            # 每次执行刚好刷新一组（2个）设定随机刷新 1 - 3 次
            safe_pos_x = random.randint(540, 1000)
            safe_pos_y = random.randint(320, 540)
            p1 = (safe_pos_x, safe_pos_y)
            p2 = (safe_pos_x, safe_pos_y - 101)
            logger.info(f'滑动 ({p1[0]}, {p1[1]}) -> ({p2[0]}, {p2[1]}), {duration}')
            
            if self.swipe:
                self.swipe.swipe(p1[0], p1[1], p2[0], p2[1], duration=duration)
            time.sleep(2)
        
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
            "ryou_access": self.config["ryou_access"],
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
        if "ryou_access" in config:
            self.config["ryou_access"] = config["ryou_access"]
        
        logger.info(f"更新{self.task_name}配置: {config}")
    
    def run(self) -> bool:
        """执行结界突破任务"""
        try:
            mode = self.config.get('mode', ToppaMode.PERSONAL)
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