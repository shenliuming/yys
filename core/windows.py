from core.logger import logger
import win32gui, win32con
import os


path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(path))
log = logger(BASE_DIR).logger

class windows:
    def __init__(self):
        # 设置进程句柄为空
        self._hwnd = 0
        # 当前文件路径
        self.path = os.getcwd()

    def check_window_handle(self):
        if self._hwnd == 0:
            log.warning("window handle not found  ! errCode : 10001")
            return None
        else:
            return 1

    def find_window(self, className, title):  # 获取窗口句柄
        hwnd = win32gui.FindWindow(className, title)
        if hwnd == 0:
            log.warning("window handle not found ! errCode : 10001")
            return None
        else:
            log.info("Gets the window handle...")
            self._hwnd = hwnd
            # 指定句柄设置为前台，也就是激活
            # win32gui.SetForegroundWindow(hwnd)
            # 设置为后台
            win32gui.SetBkMode(hwnd, win32con.TRANSPARENT)
            log.info("Set to background mode...")

    def get_window_position(self):  # 获取窗口位置
        #print(self.CheckWindowHandle())
        if self.check_window_handle() == 1:
            return win32gui.GetWindowRect(self._hwnd)

    def set_window_size(self, w, h):
        if self.check_window_handle() == 1:
            point = self.get_window_position()
            if point != None:
                win32gui.MoveWindow(self._hwnd, point[0], point[1], w, h, False)
                log.info('Changes window size...')
