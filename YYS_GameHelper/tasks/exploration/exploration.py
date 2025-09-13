#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阴阳师探索任务 - 统一脚本
自动探索指定章节，智能识别UP怪物，自动战斗和收集奖励
"""

import os
import sys
import time
import json
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import cv2

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.device import Device
from core.screenshot import Screenshot
from core.click import Click
from core.swipe import Swipe
from core.image import Image
from core.ocr import OCR
from core.logger import logger
from core.config import config
from core.task import Task
from core.emulator import emulator_manager

# ==================== 枚举定义 ====================

class ExplorationLevel(Enum):
    """探索章节枚举"""
    CHAPTER_1 = "第一章"
    CHAPTER_2 = "第二章"
    CHAPTER_3 = "第三章"
    CHAPTER_4 = "第四章"
    CHAPTER_5 = "第五章"
    CHAPTER_6 = "第六章"
    CHAPTER_7 = "第七章"
    CHAPTER_8 = "第八章"
    CHAPTER_9 = "第九章"
    CHAPTER_10 = "第十章"
    CHAPTER_11 = "第十一章"
    CHAPTER_12 = "第十二章"
    CHAPTER_13 = "第十三章"
    CHAPTER_14 = "第十四章"
    CHAPTER_15 = "第十五章"
    CHAPTER_16 = "第十六章"
    CHAPTER_17 = "第十七章"
    CHAPTER_18 = "第十八章"
    CHAPTER_19 = "第十九章"
    CHAPTER_20 = "第二十章"
    CHAPTER_21 = "第二十一章"
    CHAPTER_22 = "第二十二章"
    CHAPTER_23 = "第二十三章"
    CHAPTER_24 = "第二十四章"
    CHAPTER_25 = "第二十五章"
    CHAPTER_26 = "第二十六章"
    CHAPTER_27 = "第二十七章"
    CHAPTER_28 = "第二十八章"

class UpType(Enum):
    """UP类型枚举"""
    EXP = "经验UP"
    COIN = "金币UP"
    DARUMA = "达摩UP"
    ALL = "全部UP"

class Scene(Enum):
    """场景类型 - 基于OnmyojiAutoScript架构增强"""
    UNKNOWN = 0
    WORLD = 1  # 探索大世界
    ENTRANCE = 2  # 入口弹窗  
    MAIN = 3  # 探索里面
    BATTLE_PREPARE = 4  # 战斗准备
    BATTLE_FIGHTING = 5  # 战斗中
    TEAM = 6  # 组队
    REWARD = 7  # 奖励界面
    SETTINGS = 8  # 设置界面
    CHAPTER_SELECT = 9  # 章节选择

class DifficultyLevel(Enum):
    """难度等级枚举"""
    NORMAL = "普通"
    HARD = "困难"

class ExplorationScene(Enum):
    """探索场景枚举"""
    MAIN_MENU = "主界面"
    EXPLORATION_ENTRANCE = "探索入口"
    CHAPTER_SELECT = "章节选择"
    EXPLORATION_MAP = "探索地图"
    BATTLE = "战斗中"
    REWARD = "奖励界面"
    SETTINGS = "设置界面"

# ==================== 探索任务类 ====================

class ExplorationTask(Task):
    """探索任务类"""
    
    def __init__(self, device: Device, name: str = "探索任务"):
        """
        初始化探索任务
        
        Args:
            device: 设备实例
            name: 任务名称
        """
        super().__init__(name)
        
        # 设备相关
        self.device = device
        self.screenshot = Screenshot(device)
        self.click = Click(device)
        self.swipe = Swipe(device)
        
        # 图像识别相关
        self.matcher = Image()
        self.ocr = OCR()
        
        # 任务配置 - 单人模式默认配置
        self.config = {
            "exploration_level": ExplorationLevel.CHAPTER_28,
            "auto_rotate": True,  # 开启自动轮换
            "limit_time": timedelta(minutes=30),  # 30分钟
            "minions_cnt": 9999,  # 循环次数9999
            "up_type": UpType.ALL,
            "mode": "solo",  # 单人模式
            "buff_gold_50": False,
            "buff_gold_100": False,
            "buff_exp_50": False,
            "buff_exp_100": False,
            "device_address": "127.0.0.1:5555",
            "screenshot_interval": 1.0,
            "battle_timeout": 120,
            "swipe_duration": 1000,
            "click_delay": 0.5
        }
        
        # 加载模板
        self._load_templates()
        
        # 统计信息
        self.stats = {
            "battles_count": 0,
            "exp_monsters": 0,
            "coin_monsters": 0,
            "daruma_monsters": 0,
            "treasure_boxes": 0,
            "start_time": None,
            "end_time": None
        }
    
    def _load_templates(self) -> None:
        """加载模板图片"""
        from pathlib import Path
        import os
        
        # 使用相对路径，基于当前工作目录
        template_dir = Path("templates") / "exploration" / "res"
        
        # 定义需要的模板 - 映射到OnmyojiAutoScript的文件名
        template_files = {
            # 界面导航
            "entrance": "res_e_exploration_open.png",  # 进入难度选择界面
            "main": "res_exploration_title.png",
            "settings_button": "res_e_settings_button.png",
            "exploration_click": "res_e_exploration_click.png",  # 探索按钮
            "open_settings": "res_e_open_settings.png",
            
            # 战斗相关
            "normal_monster": "res_normal_battle_button.png",
            "boss_monster": "res_boss_battle_button.png",
            "battle_start": "res_battle_start.png",
            
            # 奖励收集
            "treasure_box": "res_treasure_box_click.png",
            "get_reward": "res_get_reward.png",
            "battle_reward": "res_battle_reward.png",
            
            # 自动轮换设置
            "auto_rotate_on": "res_e_auto_rotate_on.png",
            "auto_rotate_off": "res_e_auto_rotate_off.png",
            "enter_choose_rarity": "res_e_enter_choose_rarity.png",
            "n_rarity": "res_e_n_rarity.png",
            "s_rarity": "res_e_s_rarity.png",
            "rotate_exist": "res_e_ratate_exsit.png",
            "sure_button": "res_e_sure_button.png",
            
            # 组队相关
            "team_emoji": "res_team_emoji.png",
            "create_team": "res_exp_create_team.png",
            "create_ensure": "res_exp_create_ensure.png",
            
            # 操作控制
            "swipe_end": "res_swipe_end.png",
            "exit_confirm": "res_e_exit_confirm.png",
            "red_close": "res_red_close.png"
        }
        
        self.templates = {}
        logger.info(f"模板目录: {template_dir}")
        logger.info(f"模板目录存在: {template_dir.exists()}")
        
        for name, filename in template_files.items():
            path = template_dir / filename
            logger.debug(f"检查模板文件: {path}")
            if path.exists():
                logger.debug(f"文件存在，尝试加载: {path}")
                template_img = cv2.imread(str(path))
                if template_img is not None:
                    self.templates[name] = template_img
                    logger.info(f"成功加载模板: {name}")
                else:
                    logger.error(f"cv2.imread失败: {path}")
            else:
                logger.error(f"模板文件不存在: {path}")
    
    def get_current_scene(self, image=None) -> Scene:
        """获取当前场景 - 基于OnmyojiAutoScript架构"""
        if image is None:
            image = self.screenshot.screenshot()
            if image is None:
                return Scene.UNKNOWN
        
        # 检查奖励界面
        reward_template = self.templates.get("get_reward")
        if reward_template is not None and self.matcher.find_template(image, reward_template) is not None:
            return Scene.REWARD
        
        # 检查战斗准备界面
        battle_prepare_template = self.templates.get("battle_prepare")
        if battle_prepare_template is not None and self.matcher.find_template(image, battle_prepare_template) is not None:
            return Scene.BATTLE_PREPARE
        
        # 检查战斗中界面
        battle_fighting_template = self.templates.get("battle_fighting")
        if battle_fighting_template is not None and self.matcher.find_template(image, battle_fighting_template) is not None:
            return Scene.BATTLE_FIGHTING
        
        # 检查设置界面
        settings_template = self.templates.get("settings")
        if settings_template is not None and self.matcher.find_template(image, settings_template) is not None:
            return Scene.SETTINGS
        
        # 检查章节选择界面
        chapter_select_template = self.templates.get("chapter_select")
        if chapter_select_template is not None and self.matcher.find_template(image, chapter_select_template) is not None:
            return Scene.CHAPTER_SELECT
        
        # 检查探索入口
        entrance_template = self.templates.get("entrance")
        if entrance_template is not None and self.matcher.find_template(image, entrance_template) is not None:
            return Scene.ENTRANCE
        
        # 检查探索主界面（通过UP怪物或普通怪物判断）
        normal_template = self.templates.get("normal_monster")
        boss_template = self.templates.get("boss_monster")
        if (normal_template and self.matcher.find_template(image, normal_template) is not None) or \
           (boss_template and self.matcher.find_template(image, boss_template) is not None):
            return Scene.MAIN
        
        # 检查大世界界面
        world_template = self.templates.get("world")
        if world_template is not None and self.matcher.find_template(image, world_template) is not None:
            return Scene.WORLD
        
        return Scene.UNKNOWN
    
    def enter_settings_and_do_operations(self, image=None) -> bool:
        """进入设置并执行自动轮换等操作 - 基于OnmyojiAutoScript完整实现"""
        if image is None:
            image = self.screenshot.screenshot()
            if image is None:
                return False
        
        # 检查是否已经在设置界面
        current_scene = self.get_current_scene(image)
        if current_scene != Scene.SETTINGS:
            # 查找设置按钮
            settings_button = self.templates.get("settings_button")
            if settings_button is not None:
                settings_pos = self.matcher.find_template(image, settings_button)
                if settings_pos is not None:
                    logger.info("点击设置按钮")
                    self.click.click(settings_pos[0], settings_pos[1])
                    time.sleep(2)
                else:
                    logger.warning("未找到设置按钮")
                    return False
            else:
                logger.warning("设置按钮模板未加载")
                return False
        
        # 等待设置界面加载
        time.sleep(1)
        current_image = self.screenshot.screenshot()
        if current_image is None:
            return False
        
        # 检查是否成功打开设置
        open_settings = self.templates.get("open_settings")
        if open_settings is None or self.matcher.find_template(current_image, open_settings) is None:
            logger.warning("设置界面未正确打开")
            return False
        
        # 检查自动轮换设置
        auto_rotate_off = self.templates.get("auto_rotate_off")
        if auto_rotate_off is not None:
            rotate_pos = self.matcher.find_template(current_image, auto_rotate_off)
            if rotate_pos is not None:
                logger.info("开启自动轮换")
                self.click.click(rotate_pos[0], rotate_pos[1])
                time.sleep(1)
                # 重新截图检查状态
                current_image = self.screenshot.screenshot()
                if current_image is None:
                    return False
        
        # 检查候补出战数量并添加式神
        self._check_and_add_shiki(current_image)
        
        # 退出设置界面
        sure_button = self.templates.get("sure_button")
        if sure_button is not None:
            sure_pos = self.matcher.find_template(current_image, sure_button)
            if sure_pos is not None:
                logger.info("点击确定按钮")
                self.click.click(sure_pos[0], sure_pos[1])
                time.sleep(2)
        
        return True
    
    def _check_and_add_shiki(self, image):
        """检查候补出战数量并添加式神"""
        # 检查是否已有候补出战的狗粮
        rotate_exist = self.templates.get("ratate_exsit")
        if rotate_exist is not None:
            exist_pos = self.matcher.find_template(image, rotate_exist)
            if exist_pos is not None:
                logger.info("已有候补出战的狗粮，跳过添加")
                return
        
        # 添加N卡和素材
        self._add_shiki_by_rarity(image, "n_rarity", "N卡")
        self._add_shiki_by_rarity(image, "s_rarity", "素材")
    
    def _add_shiki_by_rarity(self, image, rarity_template_name, rarity_name):
        """根据稀有度添加式神"""
        rarity_template = self.templates.get(rarity_template_name)
        if rarity_template is None:
            logger.warning(f"{rarity_name}模板未加载")
            return
        
        rarity_pos = self.matcher.find_template(image, rarity_template)
        if rarity_pos is not None:
            logger.info(f"点击{rarity_name}选项")
            self.click.click(rarity_pos[0], rarity_pos[1])
            time.sleep(1)
            
            # 添加多个式神（通常添加4个）
            for i in range(4):
                # 点击式神位置（根据OnmyojiAutoScript的经验值）
                shiki_x = 200 + i * 150  # 式神间距
                shiki_y = 400
                logger.info(f"添加第{i+1}个{rarity_name}式神")
                self.click.click(shiki_x, shiki_y)
                time.sleep(0.5)
            
            # 确认添加
            sure_button = self.templates.get("sure_button")
            if sure_button is not None:
                sure_pos = self.matcher.find_template(image, sure_button)
                if sure_pos is not None:
                    logger.info(f"确认添加{rarity_name}")
                    self.click.click(sure_pos[0], sure_pos[1])
                    time.sleep(1)
    
    def _run(self) -> bool:
        """
        任务执行逻辑
        
        Returns:
            bool: 是否成功
        """
        logger.section(f"开始执行探索任务 - {self.config['exploration_level'].value}")
        
        self.stats["start_time"] = datetime.now()
        
        try:
            # 1. 进入探索界面
            if not self._enter_exploration():
                logger.error("无法进入探索界面")
                return False
            
            # 2. 选择章节
            if not self._select_chapter():
                logger.error("无法选择章节")
                return False
            
            # 3. 开始探索循环
            return self._exploration_loop()
            
        except Exception as e:
            logger.error(f"探索任务执行失败: {e}")
            return False
        finally:
            self.stats["end_time"] = datetime.now()
            self._show_statistics()
    
    def _enter_exploration(self) -> bool:
        """检查是否在探索界面，如果在主界面则尝试进入探索 - 基于OnmyojiAutoScript的appear_then_click逻辑"""
        logger.info("检查当前界面状态...")
        
        # 最多尝试10次，类似OnmyojiAutoScript的循环逻辑
        max_attempts = 10
        for attempt in range(max_attempts):
            image = self.screenshot.screenshot()
            if image is None:
                logger.warning("获取截图失败")
                time.sleep(1)
                continue

            # 首先检查当前场景
            current_scene = self.get_current_scene(image)
            logger.info(f"当前场景: {current_scene}")
            
            # 如果已经在探索界面，直接返回
            if current_scene == Scene.MAIN:
                logger.info("已在探索界面")
                return True
            
            # 如果不在游戏主界面，先尝试返回主界面
            if current_scene == Scene.UNKNOWN:
                logger.warning("未识别到游戏界面，可能不在游戏中")
                # 尝试使用OCR识别探索按钮 - 参考OnmyojiAutoScript的home_explore方法
                try:
                    from core.ocr import BaseOcr
                    explore_ocr = BaseOcr(
                        name="home_explore",
                        mode="FULL", 
                        method="DEFAULT",
                        roi=(310, 105, 858, 194),  # 从OnmyojiAutoScript的ocr.json配置
                        area=(310, 105, 858, 194),
                        keyword="探索"
                    )
                    
                    ocr_results = explore_ocr.detect_and_ocr(image)
                    for result in ocr_results:
                        if "探索" in result["text"] and result["score"] > 0.6:
                            # 计算点击位置（OCR结果的中心点）
                            box = result["box"]
                            center_x = int((box[0][0] + box[2][0]) / 2)
                            center_y = int((box[0][1] + box[2][1]) / 2)
                            
                            logger.info(f"OCR识别到探索按钮，点击位置: ({center_x}, {center_y})")
                            self.click.click(center_x, center_y)
                            time.sleep(2)
                            break
                    else:
                        logger.warning("OCR未识别到探索按钮")
                        
                except Exception as e:
                    logger.warning(f"OCR识别失败: {e}")
             
            # 查找并点击探索入口 - 使用appear_then_click逻辑
            entrance_template = self.templates.get("entrance")
            if entrance_template is not None:
                entrance_pos = self.matcher.find_template(image, entrance_template, threshold=0.6)
                if entrance_pos is not None:
                    logger.info(f"第{attempt + 1}次尝试：找到探索入口，点击进入")
                    logger.info(f"点击坐标: {entrance_pos}")
                    self.click.click(entrance_pos[0], entrance_pos[1])
                    
                    # 等待界面切换 - 基于OnmyojiAutoScript的wait_until_appear逻辑
                    wait_start = time.time()
                    max_wait = 5  # 等待5秒
                    
                    while time.time() - wait_start < max_wait:
                        time.sleep(0.5)
                        current_image = self.screenshot.screenshot()
                        if current_image is None:
                            continue
                            
                        # 检查是否成功进入探索界面
                        new_scene = self.get_current_scene(current_image)
                        if new_scene == Scene.MAIN:
                            logger.info("成功进入探索界面")
                            return True
                        
                        # 检查是否还能看到入口按钮（说明点击可能失败）
                        still_entrance = self.matcher.find_template(current_image, entrance_template, threshold=0.6)
                        if still_entrance is not None:
                            logger.debug("仍能看到探索入口，继续等待")
                            continue
                    
                    logger.warning(f"第{attempt + 1}次点击后未能进入探索界面")
                    continue
            
            logger.warning(f"第{attempt + 1}次尝试：未找到探索入口")
            time.sleep(1)
        
        # 如果所有尝试都失败，返回失败
        logger.error(f"尝试{max_attempts}次仍无法进入探索界面")
        return False
    
    def _select_chapter(self) -> bool:
        """选择章节"""
        logger.info(f"正在选择章节: {self.config['exploration_level'].value}")
        target_chapter = self.config['exploration_level'].value
        
        swipe_count = 0
        max_swipes = 25
        
        # 寻找目标章节
        logger.info("开始寻找目标章节")
        while swipe_count < max_swipes:
            screenshot = self.screenshot.screenshot()
            if screenshot is None:
                logger.error("获取截图失败")
                return False
            
            # 使用OCR识别当前显示的章节
            try:
                from core.ocr import BaseOcr
                # 创建章节识别OCR对象，使用配置文件中的ROI区域
                chapter_ocr = BaseOcr(
                    name="exploration_level_number",
                    mode="FULL", 
                    method="DEFAULT",
                    roi=(1079, 193, 147, 467),  # 从ocr.json配置中获取
                    area=(1079, 193, 147, 467),
                    keyword=target_chapter
                )
                
                # 检测并识别章节文字
                ocr_results = chapter_ocr.detect_and_ocr(screenshot)
                current_chapters = [result["text"] for result in ocr_results if result["score"] > 0.6]
                logger.info(f"当前识别到的章节: {current_chapters}")
                
                # 判断是否找到目标章节
                if target_chapter in current_chapters:
                    logger.info(f"找到目标章节: {target_chapter}")
                    break
                    
            except Exception as e:
                logger.warning(f"OCR识别章节失败: {e}，使用模板匹配方式")
                # 如果OCR失败，回退到模板匹配方式
                entrance_template = self.templates.get("entrance")
                if entrance_template is not None:
                    entrance_pos = self.matcher.find_template(screenshot, entrance_template, threshold=0.8)
                    if entrance_pos is not None:
                        logger.info(f"找到探索入口，位置: {entrance_pos}")
                        break
                
            # 检查确认按钮并点击
            confirm_template = self.templates.get("exit_confirm")
            if confirm_template is not None:
                confirm_pos = self.matcher.find_template(screenshot, confirm_template)
                if confirm_pos is not None:
                    logger.info("发现确认按钮，点击确认")
                    self.click.click(confirm_pos[0], confirm_pos[1])
                    time.sleep(1)
                    continue
            
            # 向上滑动寻找章节 - 使用OnmyojiAutoScript的精确滑动坐标
            logger.info(f"滑动寻找章节，第{swipe_count + 1}次")
            # 从swipe.json配置中获取的精确滑动坐标：swipe_level_up
            # roiFront: "1142,328,21,21" -> 中心点 (1152, 338)
            # roiBack: "1143,444,21,21" -> 中心点 (1153, 454)
            self.swipe.swipe(1152, 338, 1153, 454, 0.5)
            swipe_count += 1
            time.sleep(1)
        
        if swipe_count >= max_swipes:
            logger.error(f"滑动{max_swipes}次仍未找到目标章节")
            return False
        
        # 点击目标章节
        click_attempts = 0
        max_click_attempts = 10
        logger.info(f"开始尝试点击章节: {self.config['exploration_level'].value}")
        
        while click_attempts < max_click_attempts:
            click_attempts += 1
            logger.info(f"第{click_attempts}次尝试点击章节")
            
            screenshot = self.screenshot.screenshot()
            if screenshot is None:
                logger.warning("获取截图失败，跳过本次尝试")
                continue
                
            # 检查确认按钮
            confirm_template = self.templates.get("exit_confirm")
            if confirm_template is not None:
                confirm_pos = self.matcher.find_template(screenshot, confirm_template)
                if confirm_pos is not None:
                    logger.info("发现确认按钮，点击确认")
                    self.click.click(confirm_pos[0], confirm_pos[1])
                    time.sleep(1)
                    continue
            
            # 使用OCR识别章节位置并点击
            try:
                from core.ocr import BaseOcr
                chapter_ocr = BaseOcr(
                    name="exploration_level_number",
                    mode="FULL", 
                    method="DEFAULT",
                    roi=(1079, 193, 147, 467),
                    area=(1079, 193, 147, 467),
                    keyword=target_chapter
                )
                
                ocr_results = chapter_ocr.detect_and_ocr(screenshot)
                target_found = False
                
                for result in ocr_results:
                    if result["text"] == target_chapter and result["score"] > 0.6:
                        # 计算点击位置（OCR结果的中心点）
                        box = result["box"]
                        # box是四个点的坐标，计算中心点
                        center_x = int((box[0][0] + box[2][0]) / 2) + 1079  # 加上ROI的偏移
                        center_y = int((box[0][1] + box[2][1]) / 2) + 193
                        
                        logger.info(f"OCR识别到目标章节，点击位置: ({center_x}, {center_y})")
                        self.click.click(center_x, center_y)
                        target_found = True
                        break
                
                if not target_found:
                    # 如果OCR没找到，使用默认位置
                    logger.info("OCR未找到目标章节，使用默认位置点击")
                    chapter_y = 400  # 默认章节位置
                    chapter_name = self.config['exploration_level'].value
                    if "二十八" in chapter_name:
                        chapter_y = 450
                    elif "二十七" in chapter_name:
                        chapter_y = 400
                    elif "二十六" in chapter_name:
                        chapter_y = 350
                    
                    logger.info(f"点击章节位置: (640, {chapter_y})")
                    self.click.click(640, chapter_y)
                    
            except Exception as e:
                logger.warning(f"OCR点击章节失败: {e}，使用默认位置")
                # 回退到原来的固定位置点击方式
                chapter_y = 400
                chapter_name = self.config['exploration_level'].value
                if "二十八" in chapter_name:
                    chapter_y = 450
                elif "二十七" in chapter_name:
                    chapter_y = 400
                elif "二十六" in chapter_name:
                    chapter_y = 350
                
                logger.info(f"点击章节位置: (640, {chapter_y})")
                self.click.click(640, chapter_y)
            
            time.sleep(2)
            
            # 检查是否出现探索按钮
            exploration_click_template = self.templates.get("exploration_click")
            if exploration_click_template is not None:
                exploration_pos = self.matcher.find_template(self.screenshot.screenshot(), exploration_click_template)
                if exploration_pos is not None:
                    logger.info(f"找到探索按钮，位置: {exploration_pos}")
                    break
                else:
                    logger.info("未找到探索按钮，继续尝试")
            else:
                logger.warning("探索按钮模板未加载")
        
        if click_attempts >= max_click_attempts:
            logger.error(f"尝试{max_click_attempts}次仍未找到探索按钮")
            return False
        
        # 点击进入探索
        exploration_click_template = self.templates.get("exploration_click")
        if exploration_click_template is not None:
            exploration_pos = self.matcher.find_template(self.screenshot.screenshot(), exploration_click_template)
            if exploration_pos is not None:
                logger.info(f"点击探索按钮，位置: {exploration_pos}")
                self.click.click(exploration_pos[0], exploration_pos[1])
                
                # 等待并验证是否成功进入探索界面 - 基于OnmyojiAutoScript的wait_until_appear逻辑
                max_wait_time = 10  # 最多等待10秒
                wait_start = time.time()
                
                while time.time() - wait_start < max_wait_time:
                    time.sleep(0.5)
                    current_image = self.screenshot.screenshot()
                    if current_image is None:
                        continue
                        
                    # 检查是否进入了探索界面（查找探索相关的界面元素）
                    main_template = self.templates.get("main")
                    if main_template is not None:
                        main_pos = self.matcher.find_template(current_image, main_template)
                        if main_pos is not None:
                            logger.info("成功进入探索界面")
                            return True
                    
                    # 检查是否还在章节选择界面（说明点击失败）
                    entrance_template = self.templates.get("entrance")
                    if entrance_template is not None:
                        still_entrance = self.matcher.find_template(current_image, entrance_template)
                        if still_entrance is not None:
                            logger.warning("仍在章节选择界面，可能点击失败")
                            continue
                
                logger.error("点击探索按钮后未能进入探索界面")
                return False
        
        logger.error("未找到探索按钮")
        return False
    
    def _exploration_loop(self) -> bool:
        """探索主循环 - 基于OnmyojiAutoScript的run_solo方法增强"""
        logger.info("开始探索循环")
        
        start_time = datetime.now()
        battle_count = 0
        search_fail_count = 0
        explore_init = False
        last_scene = Scene.UNKNOWN
        
        while not self.stopped:
            # 检查退出条件
            if self._check_exit_conditions(start_time, battle_count):
                break
            
            # 获取当前截图和场景
            image = self.screenshot.screenshot()
            if image is None:
                logger.error("获取截图失败")
                time.sleep(1)
                continue
            
            current_scene = self.get_current_scene(image)
            
            # 场景切换日志
            if current_scene != last_scene:
                logger.debug(f"场景切换: {last_scene} -> {current_scene}")
                last_scene = current_scene
            
            # 根据当前场景执行对应操作
            if current_scene == Scene.WORLD:
                # 探索大世界场景
                logger.debug("处理探索大世界场景")
                
                # 检查宝箱
                treasure_template = self.templates.get("treasure_box")
                if treasure_template and self.matcher.find_template(image, treasure_template):
                    logger.info('发现宝箱，收集中...')
                    if self._collect_treasure_box(image):
                        search_fail_count = 0
                        continue
                
                # 检查退出条件
                if self._check_exit_conditions(start_time, battle_count):
                    break
                
                # 使用新的庭院场景处理方法
                if self._handle_world_scene(image):
                    continue
                
                # 打开指定章节
                if not self._open_expect_level():
                    logger.error("打开章节失败")
                    break
                
                explore_init = False
                continue
            
            elif current_scene == Scene.ENTRANCE:
                # 探索入口场景
                logger.debug("处理探索入口场景")
                
                if self._check_exit_conditions(start_time, battle_count):
                    break
                
                # 使用新的入口场景处理方法
                if self._handle_entrance_scene(image):
                    continue
                
                entrance_template = self.templates.get("exploration_click")
                if entrance_template:
                    entrance_pos = self.matcher.find_template(image, entrance_template)
                    if entrance_pos:
                        self.click.click(entrance_pos[0], entrance_pos[1])
                        time.sleep(2)
                        # 等待进入探索界面
                        self._wait_for_scene(Scene.MAIN, timeout=10)
                
                explore_init = False
                continue
            
            elif current_scene == Scene.MAIN:
                # 探索主界面场景
                if not explore_init:
                    logger.info("初始化探索设置")
                    # 开启自动轮换
                    auto_rotate_template = self.templates.get("auto_rotate_off")
                    if auto_rotate_template and self.matcher.find_template(image, auto_rotate_template):
                        auto_rotate_pos = self.matcher.find_template(image, auto_rotate_template)
                        if auto_rotate_pos:
                            self.click.click(auto_rotate_pos[0], auto_rotate_pos[1])
                            time.sleep(1)
                    
                    # 如果配置了自动轮换，进入设置
                    if self.config.get("auto_rotate", True):
                        self.enter_settings_and_do_operations(image)
                    
                    explore_init = True
                    continue
                
                # 处理战斗奖励
                battle_reward_template = self.templates.get("battle_reward")
                if battle_reward_template and self.matcher.find_template(image, battle_reward_template):
                    logger.debug("处理战斗奖励")
                    if self._collect_battle_reward(image):
                        continue
                
                # 使用新的主场景处理方法
                continue_loop, search_fail_count = self._handle_main_scene(image, search_fail_count)
                if continue_loop:
                    # 如果找到了目标并处理，更新战斗计数
                    if search_fail_count == 0:
                        battle_count += 1
                        logger.info(f'战斗完成，当前战斗次数: {battle_count}')
                    continue
                
                # 检查搜索失败次数，决定是否滑动或退出
                if search_fail_count >= 4:
                    search_fail_count = 0
                    
                    # 检查是否到达地图边界或特定章节的结束标志
                    if (self.config.get("exploration_level") == "第二十八章" and 
                        self._check_swipe_end(image)) or self._check_match_end(image):
                        logger.info("到达地图边界，退出探索")
                        self._quit_explore()
                        continue
                    
                    # 向右滑动寻找怪物
                    logger.debug("滑动地图寻找目标")
                    self.swipe.swipe(400, 360, 800, 360, 1000)
                    time.sleep(3)
                else:
                    time.sleep(0.5)
            
            elif current_scene == Scene.BATTLE_PREPARE or current_scene == Scene.BATTLE_FIGHTING:
                # 战斗场景处理
                logger.debug("处理战斗场景")
                self._handle_battle_scene(image)
            
            elif current_scene == Scene.REWARD:
                # 奖励界面处理
                logger.debug("处理奖励界面")
                if self._collect_battle_reward(image):
                    continue
            
            elif current_scene == Scene.UNKNOWN:
                logger.warning("未知场景，尝试恢复")
                # 尝试点击安全区域
                self.click.click(640, 360)
                time.sleep(2)
            
            else:
                # 其他场景的通用处理
                time.sleep(1)
        
        logger.info(f"探索循环结束，共战斗{battle_count}次")
        return True
    
    def _check_exit_conditions(self, start_time: datetime, battle_count: int) -> bool:
        """检查退出条件"""
        # 检查时间限制
        if datetime.now() - start_time > self.config["limit_time"]:
            logger.info("达到时间限制，结束探索")
            return True
        
        # 检查战斗次数限制
        if battle_count >= self.config["minions_cnt"]:
            logger.info("达到战斗次数限制，结束探索")
            return True
        
        return False
    
    def _handle_world_scene(self, image):
        """处理庭院场景"""
        logger.info("当前在庭院，尝试进入探索")
        entrance_template = self.templates.get("exploration_entrance")
        if entrance_template:
            entrance_pos = self.matcher.find_template(image, entrance_template)
            if entrance_pos:
                self.click.click(entrance_pos[0], entrance_pos[1])
                time.sleep(2)
                return True
        return False
    
    def _handle_entrance_scene(self, image):
        """处理探索入口场景"""
        logger.info("当前在探索入口，尝试进入探索地图")
        enter_template = self.templates.get("enter_exploration")
        if enter_template:
            enter_pos = self.matcher.find_template(image, enter_template)
            if enter_pos:
                self.click.click(enter_pos[0], enter_pos[1])
                time.sleep(3)
                return True
        return False
    
    def _handle_main_scene(self, image, search_fail_count):
        """处理探索主界面场景"""
        # 检查并处理BOSS
        if self._check_and_battle_boss(image):
            return True, 0
        
        # 检查并处理UP怪物
        if self._search_up_fight(image):
            return True, 0
        
        # 检查并处理普通怪物
        if self._check_and_battle_monster(image):
            return True, 0
        
        # 收集宝箱
        if self._check_and_collect_treasure(image):
            return True, 0
        
        # 没有找到任何目标，增加搜索失败计数
        search_fail_count += 1
        logger.debug(f"未找到目标，搜索失败计数: {search_fail_count}")
        
        # 滑动地图寻找目标
        self._slide_map()
        time.sleep(1)
        
        return True, search_fail_count
    
    def _slide_map(self):
        """滑动地图寻找目标"""
        import random
        
        # 随机选择滑动方向
        directions = ['up', 'down', 'left', 'right']
        direction = random.choice(directions)
        
        screen_width = 1280
        screen_height = 720
        
        if direction == 'up':
            start_x, start_y = screen_width // 2, screen_height * 3 // 4
            end_x, end_y = screen_width // 2, screen_height // 4
        elif direction == 'down':
            start_x, start_y = screen_width // 2, screen_height // 4
            end_x, end_y = screen_width // 2, screen_height * 3 // 4
        elif direction == 'left':
            start_x, start_y = screen_width * 3 // 4, screen_height // 2
            end_x, end_y = screen_width // 4, screen_height // 2
        else:  # right
            start_x, start_y = screen_width // 4, screen_height // 2
            end_x, end_y = screen_width * 3 // 4, screen_height // 2
        
        logger.debug(f"滑动地图: {direction}")
        self.swipe.swipe(start_x, start_y, end_x, end_y, duration=800)
    
    def _check_and_battle_boss(self, image) -> bool:
        """检查并战斗BOSS"""
        boss_template = self.templates.get("boss_button")
        if boss_template:
            boss_pos = self.matcher.find_template(image, boss_template)
            if boss_pos:
                logger.info(f"发现BOSS，位置: {boss_pos}")
                if self._fire_battle(boss_pos):
                    self.stats["battles_count"] += 1
                    return True
        return False
    
    def _wait_for_scene(self, target_scene: Scene, timeout: int = 10) -> bool:
        """等待特定场景出现"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            image = self.screenshot.screenshot()
            if image and self.get_current_scene(image) == target_scene:
                return True
            time.sleep(1)
        return False
    
    def _open_expect_level(self) -> bool:
        """打开指定章节 - 简化版本"""
        max_swipes = 25
        swipe_count = 0
        
        while swipe_count < max_swipes:
            image = self.screenshot.screenshot()
            if image is None:
                continue
            
            # 检查是否找到目标章节
            exploration_click = self.templates.get("exploration_click")
            if exploration_click and self.matcher.find_template(image, exploration_click):
                break
            
            # 处理确认弹窗
            confirm_template = self.templates.get("confirm_button")
            if confirm_template and self.matcher.find_template(image, confirm_template):
                confirm_pos = self.matcher.find_template(image, confirm_template)
                if confirm_pos:
                    self.click.click(confirm_pos[0], confirm_pos[1])
                    time.sleep(1)
                    continue
            
            # 滑动寻找章节
            self.swipe.swipe(640, 300, 640, 500, 1000)  # 向上滑动
            swipe_count += 1
            logger.debug(f"滑动寻找章节，第{swipe_count}次")
            time.sleep(1)
        
        if swipe_count >= max_swipes:
            logger.error(f"滑动{max_swipes}次仍未找到目标章节")
            return False
        
        return True
    
    def _collect_treasure_box(self, image) -> bool:
        """收集宝箱"""
        treasure_template = self.templates.get("treasure_box")
        if not treasure_template:
            return False
        
        treasure_pos = self.matcher.find_template(image, treasure_template)
        if treasure_pos:
            logger.info('收集宝箱')
            self.click.click(treasure_pos[0], treasure_pos[1])
            time.sleep(2)
            
            # 等待并处理奖励
            max_wait = 10
            for _ in range(max_wait):
                current_image = self.screenshot.screenshot()
                if current_image is None:
                    continue
                
                # 查找奖励按钮
                reward_template = self.templates.get("get_reward")
                if reward_template:
                    reward_pos = self.matcher.find_template(current_image, reward_template)
                    if reward_pos:
                        self.click.click(reward_pos[0], reward_pos[1])
                        time.sleep(1)
                        break
                
                time.sleep(1)
            
            self.statistics["treasure_boxes"] += 1
            return True
        
        return False
    
    def _check_swipe_end(self, image) -> bool:
        """检查是否到达滑动边界"""
        swipe_end_template = self.templates.get("swipe_end")
        if swipe_end_template:
            return self.matcher.find_template(image, swipe_end_template) is not None
        return False
    
    def _check_match_end(self, image) -> bool:
        """检查匹配结束条件 - 简化实现"""
        # 这里可以添加更复杂的结束检测逻辑
        return False
    
    def _quit_explore(self):
        """退出探索"""
        logger.info('退出探索')
        max_attempts = 15
        attempt = 0
        
        while attempt < max_attempts:
            image = self.screenshot.screenshot()
            if image is None:
                time.sleep(1)
                attempt += 1
                continue
            
            # 检查是否已经回到探索入口
            back_red_template = self.templates.get("back_red")
            exploration_click_template = self.templates.get("exploration_click")
            
            if (back_red_template and self.matcher.find_template(image, back_red_template) and
                exploration_click_template and self.matcher.find_template(image, exploration_click_template)):
                break
            
            # 查找退出确认按钮
            exit_confirm_template = self.templates.get("exit_confirm")
            if exit_confirm_template and self.matcher.find_template(image, exit_confirm_template):
                exit_pos = self.matcher.find_template(image, exit_confirm_template)
                if exit_pos:
                    self.click.click(exit_pos[0], exit_pos[1])
                    time.sleep(1)
                    attempt += 1
                    continue
            
            # 查找返回按钮
            back_blue_template = self.templates.get("back_blue")
            if back_blue_template and self.matcher.find_template(image, back_blue_template):
                back_pos = self.matcher.find_template(image, back_blue_template)
                if back_pos:
                    self.click.click(back_pos[0], back_pos[1])
                    time.sleep(3.5)
                    attempt += 1
                    continue
            
            time.sleep(1)
            attempt += 1
    
    def _handle_battle_scene(self, image):
        """处理战斗场景"""
        # 这里可以添加战斗接管逻辑
        # 目前简单等待战斗完成
        time.sleep(2)
    
    def _search_up_fight(self, image):
        """搜索UP怪物并返回战斗按钮位置 - 基于OnmyojiAutoScript精确实现"""
        up_type = self.config.get('up_type', UpType.ALL)
        
        # UP类型优先级映射
        up_priority = {
            UpType.DARUMA: 3,  # 达摩优先级最高
            UpType.EXP: 2,     # 经验次之
            UpType.COIN: 1     # 金币最低
        }
        
        # 搜索所有UP标识和战斗按钮
        up_candidates = []
        
        # 搜索UP标识
        up_templates = {
            UpType.EXP: self.templates.get("up_exp"),
            UpType.COIN: self.templates.get("up_coin"), 
            UpType.DARUMA: self.templates.get("up_daruma")
        }
        
        for up_type_key, template in up_templates.items():
            if template is None:
                continue
                
            # 根据配置过滤UP类型
            if up_type != UpType.ALL and up_type != up_type_key:
                continue
                
            positions = self.matcher.find_all_template(image, template) if hasattr(self.matcher, 'find_all_template') else [self.matcher.find_template(image, template)]
            if not positions or positions[0] is None:
                continue
                
            if not isinstance(positions, list):
                positions = [positions]
                
            for up_pos in positions:
                if up_pos is None:
                    continue
                    
                logger.info(f"发现{up_type_key.value}标识，位置: {up_pos}")
                
                # 搜索对应的战斗按钮
                battle_pos = self._find_battle_button_near_up(image, up_pos)
                if battle_pos:
                    # 计算距离（用于优先级排序）
                    distance = ((up_pos[0] - 640) ** 2 + (up_pos[1] - 360) ** 2) ** 0.5
                    up_candidates.append({
                        'up_type': up_type_key,
                        'up_pos': up_pos,
                        'battle_pos': battle_pos,
                        'distance': distance,
                        'priority': up_priority.get(up_type_key, 0)
                    })
        
        # 如果找到UP怪物，按优先级和距离排序
        if up_candidates:
            # 按优先级降序，距离升序排序
            up_candidates.sort(key=lambda x: (-x['priority'], x['distance']))
            best_candidate = up_candidates[0]
            logger.info(f"选择最优UP目标: {best_candidate['up_type'].value}，位置: {best_candidate['battle_pos']}")
            return best_candidate['battle_pos']
        
        # 如果没有找到UP怪物，搜索boss和普通怪物
        return self._search_normal_monsters(image, up_type)
    
    def _find_battle_button_near_up(self, image, up_pos):
        """在UP标识附近搜索战斗按钮"""
        x, y = up_pos
        
        # 定义搜索区域（基于OnmyojiAutoScript的经验值）
        search_region = {
            'x': max(0, x - 160),
            'y': max(0, y - 300), 
            'w': min(1280, x + 200) - max(0, x - 160),
            'h': y - 20 - max(0, y - 300)
        }
        
        if search_region['w'] <= 0 or search_region['h'] <= 0:
            return None
            
        # 提取搜索区域
        region_image = image[search_region['y']:search_region['y']+search_region['h'], 
                           search_region['x']:search_region['x']+search_region['w']]
        
        # 优先搜索boss按钮
        boss_template = self.templates.get("boss_battle_button")
        if boss_template is not None:
            region_pos = self.matcher.find_template(region_image, boss_template)
            if region_pos is not None:
                global_pos = (region_pos[0] + search_region['x'], region_pos[1] + search_region['y'])
                logger.info(f"在UP附近找到boss战斗按钮: {global_pos}")
                return global_pos
        
        # 搜索普通怪物按钮
        normal_template = self.templates.get("normal_battle_button")
        if normal_template is not None:
            region_pos = self.matcher.find_template(region_image, normal_template)
            if region_pos is not None:
                global_pos = (region_pos[0] + search_region['x'], region_pos[1] + search_region['y'])
                logger.info(f"在UP附近找到普通战斗按钮: {global_pos}")
                return global_pos
        
        return None
    
    def _search_normal_monsters(self, image, up_type):
        """搜索普通怪物和boss"""
        # 优先搜索boss
        boss_template = self.templates.get("boss_battle_button")
        if boss_template is not None:
            pos = self.matcher.find_template(image, boss_template)
            if pos is not None:
                logger.info(f"发现boss，位置: {pos}")
                return pos
        
        # 搜索普通怪物（只有在配置允许时）
        if up_type == UpType.ALL:
            normal_template = self.templates.get("normal_battle_button")
            if normal_template is not None:
                pos = self.matcher.find_template(image, normal_template)
                if pos is not None:
                    logger.info(f"发现普通怪物，位置: {pos}")
                    return pos
        
        return None
    
    def _fire_battle(self, pos) -> bool:
        """开始战斗 - 基于OnmyojiAutoScript增强"""
        if not pos:
            return False
            
        logger.info(f"点击战斗按钮，位置: {pos}")
        # 点击直到按钮消失
        click_count = 0
        max_clicks = 5
        
        while click_count < max_clicks:
            self.click.click(pos[0], pos[1])
            time.sleep(1)
            
            # 检查是否还在探索界面
            image = self.screenshot.screenshot()
            if image is None:
                time.sleep(1)
                continue
                
            current_scene = self.get_current_scene(image)
            
            # 如果还在探索界面，说明按钮可能因为滑动不在范围内
            if current_scene == Scene.MAIN:
                settings_template = self.templates.get("settings_button")
                if settings_template and self.matcher.find_template(image, settings_template):
                    logger.warning('战斗按钮消失，但仍在探索界面，可能是滑动导致按钮不在范围内')
                    return False
            
            # 检查是否进入战斗准备或战斗中
            if current_scene in [Scene.BATTLE_PREPARE, Scene.BATTLE_FIGHTING]:
                break
                
            click_count += 1
        
        if click_count >= max_clicks:
            logger.warning('多次点击战斗按钮失败')
            return False
        
        # 等待战斗完成并处理
        success = self._wait_battle_complete()
        if success:
            self.statistics["battles_won"] += 1
        
        return success
    
    def _check_and_battle_monster(self, image) -> bool:
        """检查并战斗怪物"""
        # 检查普通怪物
        normal_template = self.templates.get("normal_monster")
        if normal_template is not None:
            monster_pos = self.matcher.find_template(image, normal_template)
            if monster_pos is not None:
                # 检查是否是UP怪物
                up_type = self._check_up_type(image, monster_pos)
                if self._should_battle_monster(up_type):
                    logger.info(f"发现{up_type.value if up_type else '普通'}怪物，开始战斗")
                    self.click.click(monster_pos[0], monster_pos[1])
                    self._wait_battle_complete()
                    return True
        
        # 检查BOSS怪物
        boss_template = self.templates.get("boss_monster")
        if boss_template is not None:
            boss_pos = self.matcher.find_template(image, boss_template)
            if boss_pos is not None:
                logger.info("发现BOSS怪物，开始战斗")
                self.click.click(boss_pos[0], boss_pos[1])
                self._wait_battle_complete()
                return True
        
        return False
    
    def _check_up_type(self, image, monster_pos: Tuple[int, int]) -> Optional[UpType]:
        """检查怪物UP类型"""
        # 在怪物周围区域检查UP标识
        x, y = monster_pos
        region = image[max(0, y-50):y+50, max(0, x-50):x+50]
        
        # 检查各种UP类型
        up_exp_template = self.templates.get("up_exp")
        if up_exp_template is not None and self.matcher.find_template(region, up_exp_template) is not None:
            return UpType.EXP
            
        up_coin_template = self.templates.get("up_coin")
        if up_coin_template is not None and self.matcher.find_template(region, up_coin_template) is not None:
            return UpType.COIN
            
        up_daruma_template = self.templates.get("up_daruma")
        if up_daruma_template is not None and self.matcher.find_template(region, up_daruma_template) is not None:
            return UpType.DARUMA
        
        return None
    
    def _should_battle_monster(self, up_type: Optional[UpType]) -> bool:
        """判断是否应该战斗怪物"""
        if self.config["up_type"] == UpType.ALL:
            return True
        
        return up_type == self.config["up_type"]
    
    def _wait_battle_complete(self) -> bool:
        """等待战斗完成 - 基于OnmyojiAutoScript增强"""
        logger.debug("等待战斗完成...")
        
        start_time = time.time()
        battle_started = False
        battle_prepare_handled = False
        
        while time.time() - start_time < self.config["battle_timeout"]:
            image = self.screenshot.screenshot()
            if image is None:
                time.sleep(1)
                continue
            
            current_scene = self.get_current_scene(image)
            
            # 检查是否进入战斗准备界面
            if current_scene == Scene.BATTLE_PREPARE and not battle_prepare_handled:
                logger.debug("进入战斗准备界面")
                battle_prepare_handled = True
                
                # 查找开始战斗按钮
                start_battle = self.templates.get("start_battle")
                if start_battle is not None:
                    start_pos = self.matcher.find_template(image, start_battle)
                    if start_pos is not None:
                        logger.info("点击开始战斗")
                        self.click.click(start_pos[0], start_pos[1])
                        time.sleep(2)
                        battle_started = True
                        continue
                
                # 如果没有找到开始战斗按钮，尝试点击屏幕中央
                logger.debug("未找到开始战斗按钮，点击屏幕中央")
                screen_center = (image.shape[1] // 2, image.shape[0] // 2)
                self.click.click(screen_center[0], screen_center[1])
                time.sleep(2)
                battle_started = True
                continue
            
            # 检查是否在战斗中
            elif current_scene == Scene.BATTLE_FIGHTING:
                if not battle_started:
                    logger.debug("直接进入战斗中")
                    battle_started = True
                
                # 在战斗中，等待战斗结束
                time.sleep(2)
                continue
            
            # 检查奖励界面
            elif current_scene == Scene.REWARD:
                logger.debug("检测到奖励界面")
                reward_collected = self._collect_battle_reward(image)
                if reward_collected:
                    logger.info("战斗完成，奖励已收集")
                    return True
                time.sleep(1)
                continue
            
            # 检查是否返回探索界面
            elif current_scene == Scene.MAIN:
                if battle_started:
                    logger.info("战斗完成，返回探索界面")
                    return True
                else:
                    logger.warning("未开始战斗就返回探索界面")
                    return False
            
            # 处理其他可能的界面
            else:
                # 检查是否有奖励弹窗
                reward_template = self.templates.get("battle_reward")
                if reward_template and self.matcher.find_template(image, reward_template):
                    logger.debug("发现奖励弹窗")
                    reward_pos = self.matcher.find_template(image, reward_template)
                    if reward_pos:
                        self.click.click(reward_pos[0], reward_pos[1])
                        time.sleep(1)
                        continue
                
                # 检查确认按钮
                confirm_template = self.templates.get("confirm_button")
                if confirm_template and self.matcher.find_template(image, confirm_template):
                    confirm_pos = self.matcher.find_template(image, confirm_template)
                    if confirm_pos:
                        self.click.click(confirm_pos[0], confirm_pos[1])
                        time.sleep(1)
                        continue
            
            time.sleep(1)
        
        logger.warning(f"战斗超时 ({self.config['battle_timeout']}秒)")
        return False
    
    def _collect_battle_reward(self, image) -> bool:
        """收集战斗奖励"""
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            # 查找奖励相关按钮
            reward_template = self.templates.get("battle_reward")
            if reward_template:
                reward_pos = self.matcher.find_template(image, reward_template)
                if reward_pos:
                    self.click.click(reward_pos[0], reward_pos[1])
                    time.sleep(1)
                    image = self.screenshot.screenshot()
                    if image is None:
                        break
                    attempt += 1
                    continue
            
            # 查找确认按钮
            confirm_template = self.templates.get("confirm_button")
            if confirm_template:
                confirm_pos = self.matcher.find_template(image, confirm_template)
                if confirm_pos:
                    self.click.click(confirm_pos[0], confirm_pos[1])
                    time.sleep(1)
                    image = self.screenshot.screenshot()
                    if image is None:
                        break
                    attempt += 1
                    continue
            
            # 检查是否返回探索界面
            current_scene = self.get_current_scene(image)
            if current_scene == Scene.MAIN:
                return True
            
            # 尝试点击屏幕中央
            screen_center = (image.shape[1] // 2, image.shape[0] // 2)
            self.click.click(screen_center[0], screen_center[1])
            time.sleep(1)
            
            image = self.screenshot.screenshot()
            if image is None:
                break
            
            attempt += 1
        
        return False
            elif current_scene == Scene.BATTLE_FIGHTING:
                if not battle_started:
                    battle_started = True
                    logger.debug("战斗已开始")
                # 在战斗中等待
                time.sleep(2)
                continue
            
            # 检查是否有奖励界面
            elif current_scene == Scene.REWARD:
                logger.debug("战斗完成，收集奖励")
                # 查找奖励收集按钮
                reward_template = self.templates.get("get_reward")
                if reward_template is not None:
                    reward_pos = self.matcher.find_template(image, reward_template)
                    if reward_pos is not None:
                        self.click.click(reward_pos[0], reward_pos[1])
                    else:
                        # 点击屏幕中央收集奖励
                        self.click.click(640, 360)
                else:
                    self.click.click(640, 360)
                
                time.sleep(2)
                
                # 检查是否还有奖励界面
                new_image = self.screenshot.screenshot()
                if new_image and self.get_current_scene(new_image) != Scene.REWARD:
                    return True
                
                # 继续点击收集可能的多重奖励
                self.click.click(640, 360)
                time.sleep(1)
            
            # 检查是否回到探索主界面
            elif current_scene == Scene.MAIN:
                if battle_started:
                    logger.debug("战斗完成，返回探索界面")
                    return True
            
            time.sleep(1)
        
        logger.warning("战斗超时")
        return False
    
    def _check_and_collect_treasure(self, image) -> bool:
        """检查并收集宝箱"""
        treasure_template = self.templates.get("treasure_box")
        if treasure_template is None:
            return False
        
        treasure_pos = self.matcher.find_template(image, treasure_template)
        if treasure_pos is not None:
            logger.info(f"发现宝箱，位置: {treasure_pos}")
            self.click.click(treasure_pos[0], treasure_pos[1])
            time.sleep(2)
            
            # 等待宝箱打开并收集奖励
            max_wait = 10
            wait_count = 0
            while wait_count < max_wait:
                current_image = self.screenshot.screenshot()
                if current_image is None:
                    break
                    
                # 检查是否有奖励界面
                reward_template = self.templates.get("get_reward")
                if reward_template is not None:
                    reward_pos = self.matcher.find_template(current_image, reward_template)
                    if reward_pos is not None:
                        self.click.click(reward_pos[0], reward_pos[1])
                        logger.info("收集宝箱奖励")
                        time.sleep(1)
                        break
                
                # 点击屏幕中央收集可能的奖励
                self.click.click(640, 360)
                time.sleep(1)
                wait_count += 1
            
            self.stats["treasure_boxes"] += 1
            return True
        
        return False
    
    def _check_and_swipe_map(self, image) -> bool:
        """检查并滑动地图"""
        # 检查是否到达地图边缘
        swipe_end_template = self.templates.get("swipe_end")
        if swipe_end_template is not None:
            swipe_end_pos = self.matcher.find_template(image, swipe_end_template)
            if swipe_end_pos is not None:
                logger.debug("到达地图边缘，滑动地图")
                # 随机方向滑动
                self.swipe.swipe_random()
                time.sleep(1)
                return True
        
        return False
    
    def _show_statistics(self) -> None:
        """显示统计信息"""
        if self.stats["start_time"] and self.stats["end_time"]:
            duration = self.stats["end_time"] - self.stats["start_time"]
            
            logger.section("探索任务统计")
            logger.info(f"任务时长: {duration}")
            logger.info(f"战斗次数: {self.stats['battles_count']}")
            logger.info(f"经验怪物: {self.stats['exp_monsters']}")
            logger.info(f"金币怪物: {self.stats['coin_monsters']}")
            logger.info(f"达摩怪物: {self.stats['daruma_monsters']}")
            logger.info(f"宝箱收集: {self.stats['treasure_boxes']}")

# ==================== 配置管理 ====================

def load_config() -> Dict[str, Any]:
    """加载配置"""
    default_config = {
        "device_address": "127.0.0.1:7555",
        "exploration_level": "CHAPTER_28",
        "difficulty_level": "NORMAL",
        "auto_rotate": False,
        "limit_time_minutes": 30,
        "minions_cnt": 30,
        "up_type": "ALL",
        "buff_gold_50": False,
        "buff_gold_100": False,
        "buff_exp_50": False,
        "buff_exp_100": False,
        "screenshot_interval": 1.0,
        "battle_timeout": 120,
        "swipe_duration": 1000,
        "click_delay": 0.5
    }
    
    config_file = "exploration_config.json"
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        else:
            logger.info("配置文件不存在，使用默认配置")
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}，使用默认配置")
    
    return default_config

def save_config(config_dict: Dict[str, Any]) -> bool:
    """保存配置"""
    config_file = "exploration_config.json"
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
        logger.info(f"配置已保存到 {config_file}")
        return True
    except Exception as e:
        logger.error(f"保存配置文件失败: {e}")
        return False

# ==================== 用户交互 ====================

def select_chapter() -> ExplorationLevel:
    """选择探索章节"""
    print("\n" + "="*50)
    print("请选择探索章节:")
    print("="*50)
    
    # 按行显示章节选项
    chapters = list(ExplorationLevel)
    for i in range(0, len(chapters), 4):
        row_chapters = chapters[i:i+4]
        row_text = "  ".join([f"{j+1:2d}. {ch.value:8s}" for j, ch in enumerate(row_chapters, i)])
        print(row_text)
    
    print("="*50)
    
    while True:
        try:
            choice = input(f"请选择章节 (1-{len(chapters)}, 或输入q退出): ")
            
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(chapters):
                selected = chapters[index]
                print(f"已选择: {selected.value}")
                return selected
            else:
                print("无效的选择，请重新输入")
        except ValueError:
            print("请输入有效的数字")

def select_up_type() -> UpType:
    """选择UP类型"""
    print("\n请选择UP类型:")
    up_types = list(UpType)
    for i, up_type in enumerate(up_types, 1):
        print(f"{i}. {up_type.value}")
    
    while True:
        try:
            choice = input(f"请选择UP类型 (1-{len(up_types)}): ")
            index = int(choice) - 1
            if 0 <= index < len(up_types):
                selected = up_types[index]
                print(f"已选择: {selected.value}")
                return selected
            else:
                print("无效的选择，请重新输入")
        except ValueError:
            print("请输入有效的数字")

def select_difficulty() -> DifficultyLevel:
    """选择难度等级"""
    print("\n请选择难度等级:")
    difficulties = list(DifficultyLevel)
    for i, difficulty in enumerate(difficulties, 1):
        print(f"{i}. {difficulty.value}")
    
    while True:
        try:
            choice = input(f"请选择难度等级 (1-{len(difficulties)}): ")
            index = int(choice) - 1
            if 0 <= index < len(difficulties):
                selected = difficulties[index]
                print(f"已选择: {selected.value}")
                return selected
            else:
                print("无效的选择，请重新输入")
        except ValueError:
            print("请输入有效的数字")



def select_device() -> Optional[str]:
    """选择设备/模拟器"""
    # 检测模拟器
    emulator_manager.detect_emulators()
    emulators = emulator_manager.list_emulators()
    
    print("\n" + "="*50)
    print("设备选择")
    print("="*50)
    
    # 添加手动输入选项
    device_options = []
    device_addresses = []
    
    # 添加检测到的模拟器
    if emulators:
        print("检测到的模拟器:")
        for i, name in enumerate(emulators, 1):
            emulator = emulator_manager.get_emulator(name)
            device_options.append(f"{name} ({emulator['address']})")
            device_addresses.append(emulator['address'])
            print(f"{i}. {name} ({emulator['address']})")
    
    # 添加手动输入选项
    manual_option_index = len(device_options) + 1
    device_options.append("手动输入设备地址")
    print(f"{manual_option_index}. 手动输入设备地址")
    
    # 添加默认选项
    default_option_index = len(device_options) + 1
    device_options.append("使用默认地址 (127.0.0.1:7555)")
    device_addresses.append("127.0.0.1:7555")
    print(f"{default_option_index}. 使用默认地址 (127.0.0.1:7555)")
    
    # 选择设备
    while True:
        try:
            choice = input(f"\n请选择设备 (1-{len(device_options)}, 或输入q退出): ")
            
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(device_options):
                if index == manual_option_index - 1:  # 手动输入
                    address = input("请输入设备地址 (格式: IP:端口): ")
                    if address.strip():
                        return address.strip()
                    else:
                        print("地址不能为空")
                        continue
                else:
                    return device_addresses[index]
            else:
                print("无效的选择，请重新输入")
        except ValueError:
            print("请输入有效的序号")

def configure_task() -> Dict[str, Any]:
    """配置任务参数"""
    config_dict = load_config()
    
    print("\n" + "="*50)
    print("探索任务配置")
    print("="*50)
    
    # 选择设备
    device_address = select_device()
    if device_address is None:
        return None
    config_dict["device_address"] = device_address
    
    # 选择章节
    chapter = select_chapter()
    if chapter is None:
        return None
    config_dict["exploration_level"] = chapter.name
    
    # 选择难度等级
    difficulty = select_difficulty()
    config_dict["difficulty_level"] = difficulty.name
    
    # 选择UP类型
    up_type = select_up_type()
    config_dict["up_type"] = up_type.name
    
    # 配置战斗次数
    while True:
        try:
            count = input(f"请输入战斗次数 (当前: {config_dict['minions_cnt']}): ")
            if count.strip():
                config_dict["minions_cnt"] = int(count)
            break
        except ValueError:
            print("请输入有效的数字")
    
    # 配置时间限制
    while True:
        try:
            minutes = input(f"请输入时间限制(分钟) (当前: {config_dict['limit_time_minutes']}): ")
            if minutes.strip():
                config_dict["limit_time_minutes"] = int(minutes)
            break
        except ValueError:
            print("请输入有效的数字")
    
    # 保存配置
    save_config(config_dict)
    
    return config_dict

# ==================== 主程序 ====================

def main():
    """主程序入口"""
    print("\n" + "="*60)
    print("阴阳师探索助手 v2.0 - 简化版")
    print("="*60)
    print("功能特点:")
    print("• 自动探索指定章节")
    print("• 智能识别UP怪物")
    print("• 自动战斗和收集奖励")
    print("• 支持自动轮换式神")
    print("• 可配置战斗次数和时间限制")
    print("="*60)
    
    try:
        # 配置任务
        task_config = configure_task()
        if task_config is None:
            print("任务配置取消")
            return
        
        # 创建设备连接
        device_address = task_config.get("device_address", "127.0.0.1:7555")
        device = Device(serial=device_address)
        if not device._connected:
            logger.error("设备连接失败")
            return
        
        # 创建并配置任务
        task = ExplorationTask(device)
        
        # 应用配置
        task.config["exploration_level"] = ExplorationLevel[task_config["exploration_level"]]
        task.config["up_type"] = UpType[task_config["up_type"]]
        task.config["minions_cnt"] = task_config["minions_cnt"]
        task.config["limit_time"] = timedelta(minutes=task_config["limit_time_minutes"])
        
        # 显示任务配置
        print("\n任务配置:")
        print(f"探索章节: {task.config['exploration_level'].value}")
        print(f"UP类型: {task.config['up_type'].value}")
        print(f"战斗次数: {task.config['minions_cnt']}")
        print(f"时间限制: {task.config['limit_time']}")
        
        # 确认开始
        confirm = input("\n确认开始探索任务? (y/n): ")
        if confirm.lower() != 'y':
            print("任务取消")
            return
        
        # 启动任务
        logger.info("启动探索任务")
        success = task.start()
        
        if success:
            logger.info("探索任务完成")
        else:
            logger.error("探索任务失败")
            
    except KeyboardInterrupt:
        print("\n任务被用户中断")
    except Exception as e:
        logger.error(f"程序出错: {e}")
    finally:
        print("程序已退出")

def register_task():
    """注册探索任务"""
    from core.task import task_manager
    from core.device import Device
    
    # 创建一个临时设备实例用于注册
    device = Device()
    exploration_task = ExplorationTask(device, "探索任务")
    task_manager.register_task(exploration_task)
    print("注册任务: 探索任务")

if __name__ == "__main__":
    main()