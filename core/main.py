import json, os
from core.logger import logger
from core.windows import windows
from core.picture import picture

path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(path))
log = logger(BASE_DIR)

json_file = open(os.path.join(os.path.join(BASE_DIR, 'resource'), "page.json"))
data = json.load(json_file)
page_data = []

def main():
    # for entry in data["main_pages"]:
    #     page = {}
    #     page["name"] = entry["name"]
    #     page["img"] = entry["img"]
    #     page["matchingr_ate"] = entry["matchingr_ate"]
    #     log.logger.info(page["name"])
    window = windows()
    window.find_window("SunAwtFrame","yys – picture.py")
    # window.set_window_size(500,500)
    pic = picture(window._hwnd,BASE_DIR)
    pic.capture_the_currentscreen()


main()
