#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试探索入口点击功能
"""

import os
import sys
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from core.device import Device
from core.screenshot import Screenshot
from core.click import Click
from core.image import Image
from core.logger import logger
from tasks.exploration.exploration import ExplorationTask, Scene

def test_exploration_entrance():
    """测试探索入口检测和点击"""
    logger.info("开始测试探索入口功能")
    
    try:
        # 初始化设备
        device = Device()
        if not device.connect():
            logger.error("设备连接失败")
            return False
        
        # 创建探索任务实例
        task = ExplorationTask(device)
        
        # 获取当前截图
        image = task.screenshot.screenshot()
        if image is None:
            logger.error("获取截图失败")
            return False
        
        # 检测当前场景
        current_scene = task.get_current_scene(image)
        logger.info(f"当前场景: {current_scene}")
        
        # 检查探索入口模板是否加载
        entrance_template = task.templates.get("entrance")
        if entrance_template is None:
            logger.error("探索入口模板未加载")
            return False
        
        # 尝试找到探索入口
        entrance_pos = task.matcher.find_template(image, entrance_template, threshold=0.6)
        if entrance_pos is not None:
            logger.info(f"找到探索入口，位置: {entrance_pos}")
            
            # 测试点击（不实际点击，只记录）
            logger.info(f"模拟点击坐标: ({entrance_pos[0]}, {entrance_pos[1]})")
            
            # 如果需要实际测试点击，取消下面的注释
            # task.click.click(entrance_pos[0], entrance_pos[1])
            # time.sleep(2)
            
            return True
        else:
            logger.warning("未找到探索入口")
            
            # 尝试使用OCR识别探索按钮
            try:
                from core.ocr import BaseOcr
                explore_ocr = BaseOcr(
                    name="home_explore",
                    mode="FULL", 
                    method="DEFAULT",
                    roi=(310, 105, 858, 194),
                    area=(310, 105, 858, 194),
                    keyword="探索"
                )
                
                ocr_results = explore_ocr.detect_and_ocr(image)
                logger.info(f"OCR识别结果: {ocr_results}")
                
                for result in ocr_results:
                    if "探索" in result["text"] and result["score"] > 0.6:
                        box = result["box"]
                        center_x = int((box[0][0] + box[2][0]) / 2)
                        center_y = int((box[0][1] + box[2][1]) / 2)
                        
                        logger.info(f"OCR识别到探索按钮，位置: ({center_x}, {center_y})")
                        return True
                        
            except Exception as e:
                logger.warning(f"OCR识别失败: {e}")
            
            return False
            
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        return False

def main():
    """主函数"""
    logger.info("探索入口点击测试开始")
    
    success = test_exploration_entrance()
    
    if success:
        logger.info("测试成功：探索入口检测正常")
    else:
        logger.error("测试失败：探索入口检测异常")
    
    logger.info("测试结束")

if __name__ == "__main__":
    main()