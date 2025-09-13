"""核心功能模块

提供设备连接、截图、点击、滑动、图像识别、OCR、日志记录等基础功能。
"""

from .device import Device
from .screenshot import Screenshot
from .click import Click
from .swipe import Swipe
from .image import Image
from .ocr import OCR
from .logger import logger
from .config import config, create_default_config
from .task import Task, TaskManager, task_manager
from .emulator import emulator_manager

__all__ = [
    'Device',
    'Screenshot', 
    'Click',
    'Swipe',
    'Image',
    'OCR',
    'logger',
    'config',
    'create_default_config',
    'Task',
    'TaskManager',
    'task_manager',
    'emulator_manager'
]

__version__ = '1.0.0'