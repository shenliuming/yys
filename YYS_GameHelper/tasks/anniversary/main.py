"""
主程序入口 - 命令行界面和任务启动
"""
import os
import sys
import time
import argparse
from typing import List, Dict, Optional, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.device import Device
from core.logger import logger
from core.config import config, create_default_config
from core.task import task_manager
from core.emulator import emulator_manager

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="阴阳师自动化脚本")
    
    # 模拟器选择参数
    parser.add_argument("--list-emulators", action="store_true", help="列出可用的模拟器")
    parser.add_argument("--emulator", type=str, help="指定要使用的模拟器名称")
    
    # 任务选择参数
    parser.add_argument("--list-tasks", action="store_true", help="列出可用的任务")
    parser.add_argument("--task", type=str, help="指定要执行的任务名称")
    
    # 配置参数
    parser.add_argument("--config", type=str, default="config.yaml", help="指定配置文件路径")
    
    # 调试参数
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    return parser.parse_args()

def select_emulator() -> Optional[str]:
    """
    交互式选择模拟器
    
    Returns:
        Optional[str]: 选择的模拟器名称，如果取消则返回None
    """
    # 检测模拟器
    emulator_manager.detect_emulators()
    emulators = emulator_manager.list_emulators()
    
    if not emulators:
        print("未检测到任何模拟器，请确保模拟器已安装并运行")
        return None
    
    # 显示模拟器列表
    print("\n可用的模拟器:")
    for i, name in enumerate(emulators, 1):
        emulator = emulator_manager.get_emulator(name)
        print(f"{i}. {name} ({emulator['address']})")
    
    # 选择模拟器
    while True:
        try:
            choice = input("\n请选择模拟器 (输入序号，或输入q退出): ")
            
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(emulators):
                return emulators[index]
            else:
                print("无效的选择，请重新输入")
        except ValueError:
            print("请输入有效的序号")

def select_task() -> Optional[str]:
    """
    交互式选择任务
    
    Returns:
        Optional[str]: 选择的任务名称，如果取消则返回None
    """
    # 获取可用任务
    tasks = list(task_manager.get_all_tasks().keys())
    
    if not tasks:
        print("未注册任何任务")
        return None
    
    # 显示任务列表
    print("\n可用的任务:")
    for i, name in enumerate(tasks, 1):
        print(f"{i}. {name}")
    
    # 选择任务
    while True:
        try:
            choice = input("\n请选择任务 (输入序号，或输入q退出): ")
            
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(tasks):
                return tasks[index]
            else:
                print("无效的选择，请重新输入")
        except ValueError:
            print("请输入有效的序号")

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置调试模式
    if args.debug:
        logger.logger.setLevel("DEBUG")
    
    # 加载配置
    if os.path.exists(args.config):
        config.config_file = args.config
        config.load()
    else:
        print(f"配置文件不存在: {args.config}，将创建默认配置")
        create_default_config(args.config)
    
    # 列出模拟器
    if args.list_emulators:
        emulator_manager.detect_emulators()
        emulators = emulator_manager.list_emulators()
        
        if not emulators:
            print("未检测到任何模拟器")
        else:
            print("\n可用的模拟器:")
            for i, name in enumerate(emulators, 1):
                emulator = emulator_manager.get_emulator(name)
                print(f"{i}. {name} ({emulator['address']})")
        
        return
    
    # 列出任务
    if args.list_tasks:
        tasks = list(task_manager.get_all_tasks().keys())
        
        if not tasks:
            print("未注册任何任务")
        else:
            print("\n可用的任务:")
            for i, name in enumerate(tasks, 1):
                print(f"{i}. {name}")
        
        return
    
    # 选择模拟器
    emulator_name = args.emulator
    if not emulator_name:
        emulator_name = select_emulator()
        if not emulator_name:
            print("已取消操作")
            return
    
    # 连接模拟器
    print(f"正在连接到模拟器: {emulator_name}")
    if not emulator_manager.connect_emulator(emulator_name):
        print("连接模拟器失败，请确保模拟器已启动")
        return
    
    # 创建设备实例
    emulator = emulator_manager.get_emulator(emulator_name)
    device = Device(serial=emulator["address"])
    
    # 连接设备
    if not device.connect():
        print("连接设备失败")
        return
    
    # 注册任务
    from tasks.anniversary.anniversary_task import AnniversaryTask, register_task
    anniversary_task = AnniversaryTask(device)
    task_manager.register_task(anniversary_task)
    
    # 选择任务
    task_name = args.task
    if not task_name:
        task_name = select_task()
        if not task_name:
            print("已取消操作")
            return
    
    # 运行任务
    print(f"正在运行任务: {task_name}")
    result = task_manager.run_task(task_name)
    
    # 显示任务结果
    if result:
        print(f"任务 [{task_name}] 执行成功")
    else:
        print(f"任务 [{task_name}] 执行失败")
    
    # 断开设备连接
    device.disconnect()
    
    # 断开模拟器连接
    emulator_manager.disconnect_emulator(emulator_name)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序出错: {e}")
    finally:
        print("程序已退出")