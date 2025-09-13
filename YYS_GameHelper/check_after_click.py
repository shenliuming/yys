import cv2
from tasks.exploration.exploration import ExplorationTask
from core.device import Device

# 创建设备和任务实例
device = Device('127.0.0.1:5555')
task = ExplorationTask(device)
task._load_templates()

# 加载点击后的截图
after_click = cv2.imread('after_click.png')
if after_click is None:
    print('无法加载 after_click.png')
    exit()

print('点击后的模板匹配情况:')

# 检查entrance模板
entrance_template = task.templates.get('entrance')
if entrance_template is not None:
    result = cv2.matchTemplate(after_click, entrance_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(f'entrance匹配度: {max_val:.3f}')
else:
    print('entrance模板未加载')

# 检查main模板
main_template = task.templates.get('main')
if main_template is not None:
    result2 = cv2.matchTemplate(after_click, main_template, cv2.TM_CCOEFF_NORMED)
    min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(result2)
    print(f'main匹配度: {max_val2:.3f}')
else:
    print('main模板未加载')

# 检查其他关键模板
other_templates = ['settings_button', 'exploration_click']
for template_name in other_templates:
    template_img = task.templates.get(template_name)
    if template_img is not None:
        result = cv2.matchTemplate(after_click, template_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(f'{template_name}匹配度: {max_val:.3f}')