import cv2
import numpy as np
from tasks.exploration.exploration import ExplorationTask
from core.device import Device

# 创建设备和任务实例
device = Device('127.0.0.1:5555')
task = ExplorationTask(device)
task._load_templates()

# 加载当前截图
current = cv2.imread('current_screen.png')
entrance_template = task.templates.get('entrance')

if entrance_template is not None:
    # 进行模板匹配
    result = cv2.matchTemplate(current, entrance_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    print(f'模板匹配最大值: {max_val}')
    print(f'匹配位置: {max_loc}')
    print(f'entrance模板尺寸: {entrance_template.shape}')
    print(f'当前截图尺寸: {current.shape}')
    
    # 检查匹配阈值
    threshold = 0.8
    if max_val >= threshold:
        print(f'找到匹配! 匹配度: {max_val}')
    else:
        print(f'未找到匹配，匹配度太低: {max_val} < {threshold}')
else:
    print('entrance模板未加载')