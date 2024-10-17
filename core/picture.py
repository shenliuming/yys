from core.logger import logger
import win32gui, win32con, win32ui
from time import sleep
import os, threading
import cv2 # OpenCV 替换 aircv
import numpy as np

path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(path))
log = logger(BASE_DIR)


class picture:
    def __init__(self, hwnd, base_dir):
        self._hwnd = hwnd
        self._pic = None
        self.lock = threading.Lock()
        self.base_dir = base_dir

    def check_window_handle(self):
        if self._hwnd == 0:
            log.logger.warning("window handle not found! errCode: 10001")
            return None
        else:
            return 1

    def match_the_picture(self, matchedPicture, confidence=0.6):
        if self._pic is None:
            log.logger.warning("current picture not found! errCode: 11001")
            return None
        if matchedPicture is None:
            log.logger.warning("matched picture not found! errCode: 11002")
            return None

        # 使用 OpenCV 读取图片
        imsrc = cv2.imread(self._pic)
        imobj = cv2.imread(matchedPicture)

        # 转为灰度图
        imsrc_gray = cv2.cvtColor(imsrc, cv2.COLOR_BGR2GRAY)
        imobj_gray = cv2.cvtColor(imobj, cv2.COLOR_BGR2GRAY)

        # 模板匹配
        result = cv2.matchTemplate(imsrc_gray, imobj_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= confidence:
            match_result = {
                'confidence': max_val,
                'result': max_loc,
                'shape': (imsrc.shape[1], imsrc.shape[0])
            }
            return match_result
        else:
            return None

    def match_the_pages(self, pages):
        self.capture_the_currentscreen()
        sleep(0.2)
        for entry in pages:
            img = entry['img']
            name = entry['name']
            pagePicUrl = os.path.join(os.path.join(BASE_DIR, "resource"), img)
            print(pagePicUrl)
            rate = self.match_the_picture(pagePicUrl, float(entry["matching_rate"]))
            log.logger.info(name + " matching rate is " + str(rate))
            if rate is not None:
                log.logger.info("capture currentPage is " + name)
                return name
        return None

    def get_currentpoint(self, point):
        self.capture_the_currentscreen()
        sleep(0.25)
        img = cv2.imread(self._pic)
        result = img[point[1], point[0], 1]  # 获取 G 通道的值
        log.logger.info("OpenCV result : " + str(result))
        return result

    def get_currentpointRGB(self, point):
        self.capture_the_currentscreen()
        sleep(0.25)
        img = cv2.imread(self._pic)
        result = img[point[1], point[0]]  # 获取 RGB 值
        log.logger.info("OpenCV result : " + str(result))
        return result

    def capture_the_currentscreen(self):  # 获取当前窗口截图并保存
        self.lock.acquire()
        if self.check_window_handle() == 1:
            sleep(0.1)
            left, top, right, bot = win32gui.GetWindowRect(self._hwnd)
            SW = right - left
            SH = bot - top

            # 获取窗口设备上下文
            wDC = win32gui.GetWindowDC(self._hwnd)
            dcObj = win32ui.CreateDCFromHandle(wDC)
            saveDC = dcObj.CreateCompatibleDC()
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(dcObj, SW, SH)
            saveDC.SelectObject(saveBitMap)

            # 截图保存到内存
            saveDC.BitBlt((0, 0), (SW, SH), dcObj, (0, 0), win32con.SRCCOPY)

            # 将截图转换为 OpenCV 格式
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)  # BGRA 格式

            # BGRX 转换为 BGR 格式，适用于 OpenCV
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # 释放资源
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            dcObj.DeleteDC()
            win32gui.ReleaseDC(self._hwnd, wDC)

            # 保存截图
            cv2.imwrite(os.path.join(self.base_dir, 'current_screen.png'), img_bgr)
            cv2.imshow("Captured Image", img_bgr)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            self._pic = os.path.join(self.base_dir, 'current_screen.png')
            log.logger.info('Capture the current screen...')

        self.lock.release()
