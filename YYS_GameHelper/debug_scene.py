import cv2
from tasks.exploration.exploration import ExplorationTask
from core.device import Device

# 创建设备和任务实例
device = Device('127.0.0.1:5555')
task = ExplorationTask(device)
task._load_templates()

# 加载当前截图
current = cv2.imread('current_screen.png')

# 检查关键模板的匹配情况
print('关键模板匹配情况:')
key_templates = ['entrance', 'main', 'settings_button', 'exploration_click']
for template_name in key_templates:
    template_img = task.templates.get(template_name)
    if template_img is not None:
        result = cv2.matchTemplate(current, template_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(f'{template_name}: 最大匹配度 = {max_val:.3f}, 位置 = {max_loc}')
    else:
        print(f'{template_name}: 模板未加载')

# 检查当前截图的基本信息
print(f'\n当前截图尺寸: {current.shape}')
print(f'当前截图类型: {current.dtype}')