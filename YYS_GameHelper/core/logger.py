"""
日志模块 - 处理日志记录
"""
import os
import sys
import time
import logging
from datetime import datetime
from typing import Optional, Union, Dict, Any

class Logger:
    """日志类，负责处理日志记录"""
    
    def __init__(self, name: str = "YYS", log_dir: str = "./log"):
        """
        初始化日志模块
        
        Args:
            name: 日志名称
            log_dir: 日志目录
        """
        self.name = name
        self.log_dir = log_dir
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 设置日志格式
        self.formatter = logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 创建日志记录器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 清除已有的处理器
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 添加控制台处理器
        self._add_console_handler()
        
        # 添加文件处理器
        self._add_file_handler()
        
        # 记录启动信息
        self.hr("日志系统初始化")
    
    def _add_console_handler(self):
        """添加控制台日志处理器"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
    
    def _add_file_handler(self):
        """添加文件日志处理器"""
        # 生成日志文件名
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(self.log_dir, f"{self.name}_{timestamp}.log")
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, msg: str):
        """
        记录调试信息
        
        Args:
            msg: 日志消息
        """
        self.logger.debug(msg)
    
    def info(self, msg: str):
        """
        记录一般信息
        
        Args:
            msg: 日志消息
        """
        self.logger.info(msg)
    
    def warning(self, msg: str):
        """
        记录警告信息
        
        Args:
            msg: 日志消息
        """
        self.logger.warning(msg)
    
    def error(self, msg: str):
        """
        记录错误信息
        
        Args:
            msg: 日志消息
        """
        self.logger.error(msg)
    
    def critical(self, msg: str):
        """
        记录严重错误信息
        
        Args:
            msg: 日志消息
        """
        self.logger.critical(msg)
    
    def hr(self, title: str = ""):
        """
        记录分隔线
        
        Args:
            title: 分隔线标题
        """
        if title:
            self.info(f"{'=' * 20} {title} {'=' * 20}")
        else:
            self.info("=" * 50)
    
    def attr(self, name: str, text: str):
        """
        记录属性信息
        
        Args:
            name: 属性名
            text: 属性值
        """
        self.info(f"[{name}] {text}")
    
    def section(self, title: str):
        """
        记录章节标题
        
        Args:
            title: 章节标题
        """
        self.info("")
        self.info(f">>> {title} <<<")
    
    def screenshot(self, image_path: str):
        """
        记录截图信息
        
        Args:
            image_path: 截图路径
        """
        self.info(f"截图保存至: {image_path}")
    
    def click(self, x: int, y: int, name: str = ""):
        """
        记录点击信息
        
        Args:
            x: X坐标
            y: Y坐标
            name: 点击名称
        """
        if name:
            self.info(f"点击 [{name}] @ ({x}, {y})")
        else:
            self.info(f"点击 @ ({x}, {y})")
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, name: str = ""):
        """
        记录滑动信息
        
        Args:
            start_x: 起点X坐标
            start_y: 起点Y坐标
            end_x: 终点X坐标
            end_y: 终点Y坐标
            name: 滑动名称
        """
        if name:
            self.info(f"滑动 [{name}] @ ({start_x}, {start_y}) -> ({end_x}, {end_y})")
        else:
            self.info(f"滑动 @ ({start_x}, {start_y}) -> ({end_x}, {end_y})")
    
    def ocr(self, text: str, roi: tuple = None):
        """
        记录OCR识别信息
        
        Args:
            text: 识别文本
            roi: 识别区域 (x, y, width, height)
        """
        if roi:
            self.info(f"OCR @ {roi}: [{text}]")
        else:
            self.info(f"OCR: [{text}]")
    
    def match(self, name: str, success: bool):
        """
        记录图像匹配信息
        
        Args:
            name: 模板名称
            success: 是否匹配成功
        """
        if success:
            self.info(f"匹配成功: {name}")
        else:
            self.info(f"匹配失败: {name}")
    
    def task(self, name: str, status: str):
        """
        记录任务状态
        
        Args:
            name: 任务名称
            status: 任务状态
        """
        self.info(f"任务 [{name}]: {status}")
    
    def timer(self, name: str, elapsed: float):
        """
        记录计时信息
        
        Args:
            name: 计时名称
            elapsed: 耗时（秒）
        """
        self.info(f"计时 [{name}]: {elapsed:.3f}秒")

# 创建全局日志实例
logger = Logger()

if __name__ == "__main__":
    # 测试日志功能
    logger.debug("这是一条调试信息")
    logger.info("这是一条一般信息")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")
    logger.critical("这是一条严重错误信息")
    
    logger.hr("测试分隔线")
    logger.attr("测试属性", "属性值")
    logger.section("测试章节")
    
    logger.click(100, 200, "测试按钮")
    logger.swipe(100, 200, 300, 400, "测试滑动")
    logger.ocr("测试文本", (100, 200, 300, 400))
    logger.match("测试模板", True)
    logger.task("测试任务", "完成")
    logger.timer("测试计时", 1.234)