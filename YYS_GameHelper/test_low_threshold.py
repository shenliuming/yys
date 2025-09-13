from tasks.exploration.exploration import ExplorationTask
from core.device import Device
import cv2

# 创建设备和任务实例
device = Device('127.0.0.1:5555')
task = ExplorationTask(device)
task._load_templates()

# 临时降低匹配阈值进行测试
print('测试降低阈值后的entrance模板匹配:')
current = cv2.imread('current_screen.png')
entrance_template = task.templates.get('entrance')

if entrance_template is not None:
    result = cv2.matchTemplate(current, entrance_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    print(f'entrance模板匹配度: {max_val}')
    
    # 测试不同的阈值
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    for threshold in thresholds:
        if max_val >= threshold:
            print(f'阈值 {threshold}: 匹配成功')
        else:
            print(f'阈值 {threshold}: 匹配失败')
    
    # 如果使用0.4的阈值，尝试点击
    if max_val >= 0.4:
        print(f'\n使用0.4阈值，在位置 {max_loc} 尝试点击entrance')
        # 计算点击位置（模板中心）
        h, w = entrance_template.shape[:2]
        click_x = max_loc[0] + w // 2
        click_y = max_loc[1] + h // 2
        print(f'计算的点击位置: ({click_x}, {click_y})')
        
        # 实际点击
        from core.click import Click
        clicker = Click(device)
        clicker.click(click_x, click_y)
        print('已执行点击操作')
        
        # 等待并截图查看结果
        import time
        time.sleep(2)
        from core.screenshot import Screenshot
        screenshot = Screenshot(device)
        new_img = screenshot.screenshot()
        cv2.imwrite('after_click.png', new_img)
        print('点击后截图已保存为 after_click.png')
else:
    print('entrance模板未加载')