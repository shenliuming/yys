import json, os
import time

from core.logger import logger
from core.windows import windows
from core.picture import picture
from core.mouse import mouse
import win32gui,win32api,win32con
import ctypes,random

path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(path))
log = logger(BASE_DIR)

json_file = open(os.path.join(os.path.join(BASE_DIR, 'resource'), "page.json"))
data = json.load(json_file)
page_data = []


def get_random_point(top_left, bottom_right):
    """
    从给定的左上角和右下角坐标中生成一个随机坐标。

    :param top_left: 左上角坐标 (x1, y1)
    :param bottom_right: 右下角坐标 (x2, y2)
    :return: 随机坐标 (x, y)
    """
    x1, y1 = top_left
    x2, y2 = bottom_right

    # 生成随机坐标
    random_x = random.randint(x1, x2)
    random_y = random.randint(y1, y2)

    return (random_x, random_y)

def main():
    # for entry in data["main_pages"]:
    #     page = {}
    #     page["name"] = entry["name"]
    #     page["img"] = entry["img"]
    #     page["matchingr_ate"] = entry["matchingr_ate"]
    #     log.info(page["name"])
    window = windows()
    window.find_window("HLBRMainUI",None)
    # window._hwnd = int('00580F3C', 16)
    # window.set_window_size(500,500)
    pic = picture(window._hwnd,BASE_DIR)
    pic.capture_the_currentscreen2()


main()
