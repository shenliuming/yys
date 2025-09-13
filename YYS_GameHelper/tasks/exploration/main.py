#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阴阳师探索任务 - 主入口
自动探索指定章节，智能识别UP怪物，自动战斗和收集奖励
"""

import os
import sys
import argparse
from typing import Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.device import Device
from core.logger import logger
from core.emulator import emulator_manager
from tasks.exploration.exploration import (
    ExplorationTask, ExplorationLevel, UpType, DifficultyLevel,
    load_config, save_config, configure_task
)

def list_emulators():
    """列出可用的模拟器"""
    print("\n检测模拟器...")
    emulator_manager.detect_emulators()
    emulators = emulator_manager.list_emulators()
    
    if emulators:
        print("\n可用的模拟器:")
        for i, name in enumerate(emulators, 1):
            emulator = emulator_manager.get_emulator(name)
            print(f"{i}. {name} ({emulator['address']})")
    else:
        print("\n未检测到模拟器")
        print("请确保模拟器已启动并开启ADB调试")

def run_exploration_task(device_address: Optional[str] = None, 
                        chapter: Optional[str] = None,
                        up_type: Optional[str] = None,
                        battle_count: Optional[int] = None,
                        time_limit: Optional[int] = None):
    """运行探索任务"""
    try:
        # 加载配置
        config_dict = load_config()
        
        # 应用命令行参数
        if device_address:
            config_dict["device_address"] = device_address
        if chapter:
            # 查找匹配的章节枚举
            chapter_found = False
            for level in ExplorationLevel:
                if level.value == chapter:
                    config_dict["exploration_level"] = level.name
                    chapter_found = True
                    break
            if not chapter_found:
                logger.error(f"配置错误: '{chapter}'")
                return False
        if up_type:
            try:
                config_dict["up_type"] = up_type.upper()
            except:
                logger.error(f"无效的UP类型: {up_type}")
                return False
        if battle_count:
            config_dict["minions_cnt"] = battle_count
        if time_limit:
            config_dict["limit_time_minutes"] = time_limit
        
        # 创建设备连接
        device = Device(serial=config_dict["device_address"])
        if not device._connected:
            logger.error("设备连接失败")
            return False
        
        # 创建并配置任务
        task = ExplorationTask(device)
        
        # 应用配置
        try:
            task.config["exploration_level"] = ExplorationLevel[config_dict["exploration_level"]]
            task.config["up_type"] = UpType[config_dict["up_type"]]
            task.config["minions_cnt"] = config_dict["minions_cnt"]
            
            from datetime import timedelta
            task.config["limit_time"] = timedelta(minutes=config_dict["limit_time_minutes"])
        except KeyError as e:
            logger.error(f"配置错误: {e}")
            return False
        
        # 显示任务配置
        logger.info("任务配置:")
        logger.info(f"探索章节: {task.config['exploration_level'].value}")
        logger.info(f"UP类型: {task.config['up_type'].value}")
        logger.info(f"战斗次数: {task.config['minions_cnt']}")
        logger.info(f"时间限制: {task.config['limit_time']}")
        
        # 启动任务
        logger.info("启动探索任务")
        success = task.start()
        
        if success:
            logger.info("探索任务完成")
        else:
            logger.error("探索任务失败")
            
        return success
        
    except KeyboardInterrupt:
        logger.info("任务被用户中断")
        return False
    except Exception as e:
        logger.error(f"程序出错: {e}")
        return False

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description='阴阳师探索任务助手')
    parser.add_argument('--list-emulators', action='store_true', help='列出可用的模拟器')
    parser.add_argument('--device', type=str, help='设备地址 (例如: 127.0.0.1:7555)')
    parser.add_argument('--chapter', type=str, help='探索章节 (例如: CHAPTER_28)')
    parser.add_argument('--up-type', type=str, choices=['EXP', 'COIN', 'DARUMA', 'ALL'], 
                       help='UP类型 (EXP/COIN/DARUMA/ALL)')
    parser.add_argument('--battle-count', type=int, help='战斗次数')
    parser.add_argument('--time-limit', type=int, help='时间限制(分钟)')
    parser.add_argument('--interactive', action='store_true', help='交互式配置')
    
    args = parser.parse_args()
    
    # 列出模拟器
    if args.list_emulators:
        list_emulators()
        return
    
    # 交互式配置
    if args.interactive:
        from tasks.exploration.exploration import main as interactive_main
        interactive_main()
        return
    
    # 如果没有提供任何参数，默认进入交互模式
    if not any([args.device, args.chapter, args.up_type, args.battle_count, args.time_limit]):
        print("未提供配置参数，进入交互式配置模式...")
        from tasks.exploration.exploration import main as interactive_main
        interactive_main()
        return
    
    # 命令行模式
    success = run_exploration_task(
        device_address=args.device,
        chapter=args.chapter,
        up_type=args.up_type,
        battle_count=args.battle_count,
        time_limit=args.time_limit
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()