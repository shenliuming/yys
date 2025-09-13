#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结界突破任务主程序
"""

import sys
import os
import argparse
from datetime import datetime
from typing import Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.device import Device
from core.logger import logger
from core.emulator import emulator_manager
from tasks.kekkai_toppa.kekkai_toppa import KekkaiToppaTask
from tasks.kekkai_toppa.config import KekkaiToppaConfig, create_config, CONFIG_TEMPLATES, ToppaMode


def configure_task(mode: ToppaMode = None) -> dict:
    """配置任务参数"""
    print("\n=== 结界突破任务配置 ===")
    
    # 选择突破模式
    if mode is None:
        print("\n突破模式:")
        print("1. 个人突破 - 挑战个人结界")
        print("2. 阴阳寮突破 - 挑战寮结界")
        
        while True:
            try:
                mode_choice = input("\n请选择突破模式 (1-2，默认1): ").strip()
                if not mode_choice:
                    mode_choice = "1"
                if mode_choice == "1":
                    mode = ToppaMode.PERSONAL
                    break
                elif mode_choice == "2":
                    mode = ToppaMode.GUILD
                    break
                else:
                    print("无效选择，请重新输入")
            except ValueError:
                print("请输入数字")
    
    # 显示可用的配置模板
    print("\n可用的配置模板:")
    for i, (name, template) in enumerate(CONFIG_TEMPLATES.items(), 1):
        print(f"{i}. {name} - {template['task_name']}")
    
    # 选择配置模板
    while True:
        try:
            choice = input("\n请选择配置模板 (1-4，默认1): ").strip()
            if not choice:
                choice = "1"
            choice_idx = int(choice) - 1
            template_names = list(CONFIG_TEMPLATES.keys())
            if 0 <= choice_idx < len(template_names):
                template_name = template_names[choice_idx]
                break
            else:
                print("无效选择，请重新输入")
        except ValueError:
            print("请输入数字")
    
    # 创建配置
    config = create_config(template_name)
    config_dict = config.get_config()
    
    # 设置突破模式
    config_dict['toppa_mode'] = mode
    
    print(f"\n已选择模式: {'个人突破' if mode == ToppaMode.PERSONAL else '阴阳寮突破'}")
    print(f"已选择模板: {template_name}")
    print(f"任务名称: {config_dict['task_name']}")
    print(f"时间限制: {config_dict['limit_time_minutes']} 分钟")
    print(f"次数限制: {config_dict['limit_count']} 次")
    print(f"跳过困难区域: {'是' if config_dict['skip_difficult'] else '否'}")
    print(f"随机延迟: {'是' if config_dict['random_delay'] else '否'}")
    print(f"锁定队伍: {'是' if config_dict['enable_lock_team'] else '否'}")
    
    # 询问是否需要自定义配置
    custom = input("\n是否需要自定义配置? (y/n，默认n): ").strip().lower()
    if custom == 'y':
        config_dict = customize_config(config_dict)
    
    return config_dict


def customize_config(config_dict: dict) -> dict:
    """自定义配置"""
    print("\n=== 自定义配置 ===")
    
    # 时间限制
    time_limit = input(f"时间限制(分钟，当前: {config_dict['limit_time_minutes']}): ").strip()
    if time_limit and time_limit.isdigit():
        config_dict['limit_time_minutes'] = int(time_limit)
    
    # 次数限制
    count_limit = input(f"次数限制(当前: {config_dict['limit_count']}): ").strip()
    if count_limit and count_limit.isdigit():
        config_dict['limit_count'] = int(count_limit)
    
    # 跳过困难区域
    skip_difficult = input(f"跳过困难区域? (y/n，当前: {'y' if config_dict['skip_difficult'] else 'n'}): ").strip().lower()
    if skip_difficult in ['y', 'n']:
        config_dict['skip_difficult'] = skip_difficult == 'y'
    
    # 随机延迟
    random_delay = input(f"启用随机延迟? (y/n，当前: {'y' if config_dict['random_delay'] else 'n'}): ").strip().lower()
    if random_delay in ['y', 'n']:
        config_dict['random_delay'] = random_delay == 'y'
    
    # 锁定队伍
    lock_team = input(f"锁定队伍? (y/n，当前: {'y' if config_dict['enable_lock_team'] else 'n'}): ").strip().lower()
    if lock_team in ['y', 'n']:
        config_dict['enable_lock_team'] = lock_team == 'y'
    
    return config_dict


def select_device() -> Optional[str]:
    """选择设备"""
    print("\n=== 设备选择 ===")
    
    # 获取可用设备列表
    devices = DeviceUtils.get_available_devices()
    
    if not devices:
        print("未找到可用设备")
        return None
    
    print("\n可用设备:")
    for i, device in enumerate(devices, 1):
        print(f"{i}. {device}")
    
    # 选择设备
    while True:
        try:
            choice = input(f"\n请选择设备 (1-{len(devices)}): ").strip()
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(devices):
                return devices[choice_idx]
            else:
                print("无效选择，请重新输入")
        except ValueError:
            print("请输入数字")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='结界突破任务')
    parser.add_argument('--config', '-c', help='配置模板名称', default='default')
    parser.add_argument('--device', '-d', help='设备ID')
    parser.add_argument('--auto', '-a', action='store_true', help='自动模式（使用默认配置）')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    parser.add_argument('--mode', '-m', choices=['personal', 'guild'], 
                       help='突破模式: personal=个人突破, guild=阴阳寮突破', default='personal')
    
    args = parser.parse_args()
    
    try:
        print("\n" + "="*50)
        print("         阴阳师 - 结界突破任务")
        print("="*50)
        
        # 解析突破模式
        mode = ToppaMode.PERSONAL if args.mode == 'personal' else ToppaMode.GUILD
        
        # 配置任务
        if args.auto:
            # 自动模式，使用指定的配置模板
            config = create_config(args.config)
            config_dict = config.get_config()
            config_dict['toppa_mode'] = mode
            print(f"\n使用配置模板: {args.config}")
            print(f"突破模式: {'个人突破' if mode == ToppaMode.PERSONAL else '阴阳寮突破'}")
        else:
            # 交互模式
            config_dict = configure_task(mode)
        
        # 如果是调试模式，覆盖部分配置
        if args.debug:
            config_dict.update({
                'debug_mode': True,
                'save_screenshots': True,
                'limit_time_minutes': 5,
                'limit_count': 3,
            })
            print("\n已启用调试模式")
        
        # 选择设备
        device_id = args.device
        if not device_id and not args.auto:
            device_id = select_device()
            if not device_id:
                print("\n未选择设备，程序退出")
                return
        
        # 创建设备管理器
        device_manager = None
        if device_id:
            try:
                device_manager = DeviceUtils.create_device_manager(device_id)
                print(f"\n已连接设备: {device_id}")
            except Exception as e:
                logger.error(f"连接设备失败: {e}")
                if not args.auto:
                    return
        
        # 创建任务实例
        task = KekkaiToppaTask(device_manager)
        task.update_config(config_dict)
        
        # 显示任务信息
        print(f"\n任务配置:")
        print(f"  突破模式: {'个人突破' if config_dict['toppa_mode'] == ToppaMode.PERSONAL else '阴阳寮突破'}")
        print(f"  任务名称: {config_dict['task_name']}")
        print(f"  时间限制: {config_dict['limit_time_minutes']} 分钟")
        print(f"  次数限制: {config_dict['limit_count']} 次")
        print(f"  跳过困难: {'是' if config_dict['skip_difficult'] else '否'}")
        print(f"  随机延迟: {'是' if config_dict['random_delay'] else '否'}")
        print(f"  锁定队伍: {'是' if config_dict['enable_lock_team'] else '否'}")
        
        # 开始任务
        print(f"\n开始执行结界突破任务...")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 执行任务
        success = task.run()
        
        # 显示结果
        end_time = datetime.now()
        print(f"\n任务完成时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success:
            print("✅ 结界突破任务执行成功！")
        else:
            print("❌ 结界突破任务执行失败！")
        
        # 显示统计信息
        print(f"\n任务统计:")
        print(f"  进攻次数: {task.current_count}")
        if task.start_time:
            duration = end_time - task.start_time
            print(f"  执行时长: {duration}")
        
    except KeyboardInterrupt:
        print("\n\n用户中断任务")
    except Exception as e:
        logger.error(f"任务执行出错: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
    finally:
        print("\n程序结束")


if __name__ == "__main__":
    main()