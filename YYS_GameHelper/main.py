"""主程序入口 - 命令行界面和任务启动"""
import os
import sys
import time
import argparse
from typing import List, Dict, Optional, Any

from core.device import Device
from core.emulator import emulator_manager
from core.logger import logger
from core.config import config, create_default_config
from core.task import task_manager
from tasks import register_all_tasks

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
    
    print("\n检测到以下模拟器:")
    for i, emulator in enumerate(emulators, 1):
        emulator_info = emulator_manager.get_emulator(emulator)
        print(f"{i}. {emulator_info['name']} ({emulator_info['address']})")
    
    while True:
        try:
            choice = input("\n请选择模拟器 (输入序号，0取消): ")
            if choice == "0":
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(emulators):
                return emulators[index]
            else:
                print("无效的选择，请重新输入")
        except ValueError:
            print("请输入有效的数字")
        except KeyboardInterrupt:
            return None

def select_task() -> Optional[str]:
    """
    交互式选择任务
    
    Returns:
        Optional[str]: 选择的任务名称，如果取消则返回None
    """
    tasks = list(task_manager.get_all_tasks().keys())
    
    if not tasks:
        print("没有可用的任务")
        return None
    
    print("\n可用任务:")
    for i, task_name in enumerate(tasks, 1):
        print(f"{i}. {task_name}")
    
    while True:
        try:
            choice = input("\n请选择任务 (输入序号，0取消): ")
            if choice == "0":
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(tasks):
                return tasks[index]
            else:
                print("无效的选择，请重新输入")
        except ValueError:
            print("请输入有效的数字")
        except KeyboardInterrupt:
            return None

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置调试模式
    if args.debug:
        logger.setLevel("DEBUG")
        print("调试模式已启用")
    
    # 加载配置
    config_path = args.config
    if not os.path.exists(config_path):
        print(f"配置文件不存在: {config_path}")
        print("正在创建默认配置文件...")
        create_default_config(config_path)
        print(f"已创建默认配置文件: {config_path}")
    
    config.config_file = config_path
    config.load()
    
    # 注册所有任务
    register_all_tasks()
    
    # 列出模拟器
    if args.list_emulators:
        emulator_manager.detect_emulators()
        emulators = emulator_manager.list_emulators()
        if emulators:
            print("检测到的模拟器:")
            for emulator in emulators:
                emulator_info = emulator_manager.get_emulator(emulator)
                print(f"  - {emulator_info['name']} ({emulator_info['address']})")
        else:
            print("未检测到任何模拟器")
        return
    
    # 列出任务
    if args.list_tasks:
        tasks = list(task_manager.get_all_tasks().keys())
        if tasks:
            print("可用任务:")
            for task_name in tasks:
                print(f"  - {task_name}")
        else:
            print("没有可用的任务")
        return
    
    # 选择模拟器
    emulator_name = args.emulator
    if not emulator_name:
        emulator_name = select_emulator()
        if not emulator_name:
            print("未选择模拟器，程序退出")
            return
    
    # 连接模拟器
    print(f"\n正在连接模拟器: {emulator_name}")
    if not emulator_manager.connect_emulator(emulator_name):
        print("连接模拟器失败，程序退出")
        return
    
    # 创建设备实例
    emulator_info = emulator_manager.get_emulator(emulator_name)
    device = Device(emulator_info["address"])
    
    # 连接设备
    if not device.connect():
        print("连接设备失败，程序退出")
        return
    
    print("设备连接成功")
    
    # 选择任务
    task_name = args.task
    if not task_name:
        task_name = select_task()
        if not task_name:
            print("未选择任务，程序退出")
            return
    
    # 执行任务
    print(f"\n开始执行任务: {task_name}")
    try:
        task = task_manager.get_task(task_name)
        if not task:
            print(f"任务不存在: {task_name}")
            return
        
        # 设置设备
        task.set_device(device)
        
        # 启动任务
        task.start()
        
        # 等待任务完成
        while task.is_running():
            time.sleep(1)
        
        print(f"任务执行完成: {task_name}")
        
    except KeyboardInterrupt:
        print("\n任务被用户中断")
        if 'task' in locals():
            task.stop()
    except Exception as e:
        logger.error(f"任务执行出错: {e}")
        print(f"任务执行出错: {e}")
    finally:
        # 断开设备连接
        device.disconnect()
        print("设备连接已断开")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序出错: {e}")
    finally:
        print("程序已退出")