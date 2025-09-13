"""
周年庆活动任务模块 - 处理阴阳师周年庆活动相关任务
"""
import time
import random
from typing import Dict, Any, Optional, List, Tuple
import cv2

from core.device import Device
from core.screenshot import Screenshot
from core.click import Click
from core.swipe import Swipe
from core.image import Image
from core.ocr import OCR
from core.logger import logger
from core.config import config
from core.task import Task, task_manager

class AnniversaryTask(Task):
    """周年庆活动任务类"""
    
    def __init__(self, device: Device, name: str = "周年庆活动"):
        """
        初始化周年庆活动任务
        
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
        
        # 加载模板
        self._load_templates()
        
        # 任务配置
        self.config = {
            "max_rounds": 100000,  # 最大循环次数
            "battle_wait_time": 0.5,    # 副本中等待时间(秒)
            "max_check_times": 20,      # 最大检查次数
            "click_offset": 10,         # 点击偏移量
            "template_threshold": 0.8,  # 模板匹配阈值(提高以减少误识别)
            "screenshot_cache_time": 0.1, # 截图缓存时间(秒)
        }
    
    def _load_templates(self) -> None:
        """加载模板图片"""
        from pathlib import Path
        import cv2
        
        template_dir = Path("templates")
        
        # 定义需要的模板
        template_files = {
            "start_button": "start_button.png",
            "end_button": "end_button.png",
            "battle_icon": "battle/battle_icon.png",  # 副本攻略图标
        }
        
        self.templates = {}
        for name, filename in template_files.items():
            path = template_dir / filename
            if path.exists():
                self.templates[name] = cv2.imread(str(path))
                logger.info(f"加载模板: {name} -> {path}")
            else:
                logger.warning(f"模板文件不存在: {path}")
    
    def _run(self) -> bool:
        """
        任务执行逻辑 - 优化后的循环点击逻辑
        
        Returns:
            bool: 是否成功
        """
        logger.section("开始执行周年庆活动任务")
        
        try:
            last_screenshot_time = 0
            cached_image = None
            
            # 优化的循环点击逻辑
            for i in range(self.config["max_rounds"]):
                if self.stopped:
                    logger.info("任务被停止")
                    break
                
                # 获取当前截图（使用缓存机制）
                current_time = time.time()
                if (current_time - last_screenshot_time) > self.config["screenshot_cache_time"] or cached_image is None:
                    cached_image = self.screenshot.screenshot()
                    last_screenshot_time = current_time
                    
                if cached_image is None:
                    logger.error("截图失败") 
                    continue
                
                # 检测是否在副本中
                in_battle = self._is_in_battle(cached_image)
                
                # 如果在战斗中，执行战斗逻辑
                if in_battle:
                    battle_handled = self._handle_battle(cached_image)
                    if battle_handled:
                        logger.info(f"第{i+1}轮: 执行战斗操作")
                        time.sleep(self.config["battle_wait_time"])
                        cached_image = None  # 强制刷新截图
                        continue
                
                # 尝试点击start_button
                start_clicked = self._click_template_button_optimized("start_button", cached_image)
                if start_clicked:
                    logger.info(f"第{i+1}轮: 点击start_button成功")
                    # 只在副本中等待，避免不必要的延时
                    if in_battle:
                        time.sleep(self.config["battle_wait_time"])
                    cached_image = None  # 强制刷新截图
                    continue
                
                # 尝试点击end_button
                end_clicked = self._click_template_button_optimized("end_button", cached_image)
                if end_clicked:
                    logger.info(f"第{i+1}轮: 点击end_button成功")
                    
                    # 等待动画过渡，避免误触
                    if self._wait_for_page_transition():
                        logger.info("页面过渡完成")
                    else:
                        logger.info("页面仍在过渡中，继续等待")
                    
                    cached_image = None  # 强制刷新截图
                    continue
                
                # 如果都没找到，输出状态但不额外等待
                if i % 10 == 0:  # 每10轮输出一次状态
                    logger.info(f"第{i+1}轮: 未找到可点击的按钮，继续搜索...")
            
            logger.section("周年庆活动任务执行完成")
            return True
            
        except Exception as e:
            logger.error(f"执行周年庆活动任务时出错: {e}")
            return False
    
    def _click_template_button_optimized(self, template_name: str, image) -> bool:
        """
        优化的模板按钮点击方法
        
        Args:
            template_name: 模板名称
            image: 当前截图
            
        Returns:
            bool: 是否成功点击
        """
        if template_name not in self.templates or image is None:
            return False
        
        template = self.templates[template_name]
        
        # 使用配置的阈值进行匹配，只有高置信度才执行点击
        success, (x, y) = self.matcher.match_template(
            image, template, threshold=self.config["template_threshold"]
        )
        
        if success:
            logger.info(f"{template_name}匹配成功，置信度满足阈值{self.config['template_threshold']}")
        
        if success:
            # 根据按钮类型调整点击逻辑
            if template_name == "start_button":
                # start_button必须在按钮内部点击，使用较小的偏移
                offset_x = random.randint(-10, 50)  # 较小偏移确保在按钮内
                offset_y = random.randint(-10, 55)
                final_x = x + offset_x
                final_y = y + offset_y
            elif template_name == "end_button":
                # end_button固定点击模拟器右下角区域
                final_x = 1280 - 50  # 屏幕右边缘向左50像素
                final_y = 720 - 50   # 屏幕下边缘向上50像素
                logger.info(f"end_button点击模拟器右下角坐标: ({final_x}, {final_y}) (模板识别位置: {x}, {y})")
            else:
                # 其他按钮使用默认偏移
                offset_x = random.randint(-self.config["click_offset"], self.config["click_offset"])
                offset_y = random.randint(-self.config["click_offset"], self.config["click_offset"])
                final_x = x + offset_x
                final_y = y + offset_y
            
            self.click.click(final_x, final_y)
            logger.info(f"点击{template_name} @ ({final_x}, {final_y}) (模板坐标: {x}, {y})")
            return True
        
        return False
    
    def _handle_battle(self, image) -> bool:
        """
        处理战斗中的逻辑 - 简化版本，只等待不点击
        
        Args:
            image: 当前截图
            
        Returns:
            bool: 是否执行了战斗操作
        """
        try:
            # 在战斗中只需要等待，不进行任何点击操作
            logger.debug("检测到战斗状态，等待战斗结束")
            return True
            
        except Exception as e:
            logger.error(f"处理战斗逻辑时出错: {e}")
            return False
    
    def _is_in_battle(self, image) -> bool:
        """
        检测是否在副本攻略中
        
        Args:
            image: 当前截图
            
        Returns:
            bool: 是否在副本中
        """
        if "battle_icon" not in self.templates or image is None:
            return False
        
        template = self.templates["battle_icon"]
        success, _ = self.matcher.match_template(
            image, template, threshold=self.config["template_threshold"]
        )
        
        if success:
            logger.debug("检测到副本攻略状态")
            return True
        
        return False
    
    def _wait_for_page_transition(self, max_wait_time: int = 3) -> bool:
        """
        等待页面过渡动画完成，避免误触
        参考OnmyojiAutoScript的实现方式
        
        Args:
            max_wait_time: 最大等待时间（秒）
            
        Returns:
            bool: True表示过渡完成，False表示仍在过渡中
        """
        try:
            start_time = time.time()
            stable_count = 0
            required_stable_count = 3  # 需要连续3次检测到稳定状态
            
            # 检测页面稳定的关键元素
            stable_indicators = [
                "start_button",
                "end_button", 
                "main_ui"  # 主界面UI元素
            ]
            
            while time.time() - start_time < max_wait_time:
                 current_image = self.screenshot.screenshot()
                 if current_image is None:
                     time.sleep(0.2)
                     continue
                 
                 # 检测是否有稳定的UI元素出现
                 found_stable_element = False
                 for indicator in stable_indicators:
                     if indicator in self.templates:
                         result = self.matcher.match_template(
                             current_image,
                             self.templates[indicator],
                             threshold=0.8
                         )
                         if result:
                             found_stable_element = True
                             break
                 
                 if found_stable_element:
                     stable_count += 1
                     if stable_count >= required_stable_count:
                         logger.info(f"页面过渡完成，稳定检测次数: {stable_count}")
                         return True
                 else:
                     stable_count = 0  # 重置计数
                 
                 time.sleep(0.2)  # 短暂等待后再次检测
            
            logger.warning(f"页面过渡等待超时({max_wait_time}秒)，可能仍在动画中")
            return False
            
        except Exception as e:
            logger.error(f"等待页面过渡时出错: {e}")
            return False
    
    def _click_template_button(self, template_name: str) -> bool:
        """
        兼容性方法 - 保持向后兼容
        
        Args:
            template_name: 模板名称
            
        Returns:
            bool: 是否成功点击
        """
        image = self.screenshot.screenshot()
        if image is None:
            return False
        return self._click_template_button_optimized(template_name, image)
    


# 注册任务
def register_task():
    """注册周年庆活动任务"""
    from core.device import Device
    
    device = Device()
    anniversary_task = AnniversaryTask(device)
    task_manager.register_task(anniversary_task)
    return anniversary_task

if __name__ == "__main__":
    # 测试任务
    from core.device import Device
    
    # 创建设备实例
    device = Device()
    device.connect()
    
    # 创建任务实例
    task = AnniversaryTask(device)
    
    # 运行任务
    task.start()
    
    # 断开设备连接
    # device.disconnect()  # Device类没有disconnect方法