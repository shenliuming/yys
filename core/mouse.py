from core.logger import logger
import os, threading
import win32gui, win32con, win32api, win32ui
import time,random

path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(path))
log = logger(BASE_DIR).logger



class mouse:
    def __init__(self, hwnd, base_dir):
        self._hwnd = hwnd
        self.lock = threading.Lock()
        self.base_dir = base_dir
        self.last_position = None

    def left_click(self,cx, cy):
        try:
            self.lock.acquire()
            win32gui.SendMessage(self._hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)

            lp = win32api.MAKELONG(cx, cy)
            if None != self.last_position:
                ls = win32api.MAKELONG(self.last_position[0], self.last_position[1])
                win32api.SendMessage(self._hwnd, win32con.WM_MOUSEMOVE, win32con.MK_RBUTTON, ls)

            self.last_position = (cx, cy)

            time.sleep(0.003 + random.uniform(0.0005, 0.0015))
            win32api.SendMessage(self._hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, lp)
            win32api.PostMessage(self._hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lp)
            time.sleep(random.uniform(0.003, 0.009) + random.uniform(0.0005, 0.0035))
            win32api.PostMessage(self._hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, lp)
        finally:
            self.lock.release()

    def right_click(self,cx, cy):
        try:
            self.lock.acquire()
            win32gui.SendMessage(self._hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
            lp = win32api.MAKELONG(cx, cy)
            if None != self.last_position:
                ls = win32api.MAKELONG(self.last_position[0], self.last_position[1])
                win32api.SendMessage(self._hwnd, win32con.WM_MOUSEMOVE, win32con.MK_RBUTTON, ls)

            self.last_position = (cx, cy)
            time.sleep(0.003 + random.uniform(0.0005, 0.0015))

            win32api.SendMessage(self._hwnd, win32con.WM_MOUSEMOVE, win32con.MK_RBUTTON, lp)
            win32api.PostMessage(self._hwnd, win32con.WM_RBUTTONDOWN,win32con.MK_RBUTTON, lp)
            time.sleep(random.uniform(0.003, 0.009) + random.uniform(0.0005, 0.0035))
            win32api.PostMessage(self._hwnd, win32con.WM_RBUTTONUP,win32con.MK_RBUTTON, lp)

        finally:
            self.lock.release()

    def send_str(self,text):
        astrToint = [ord(c) for c in text]
        for item in astrToint:
            win32api.PostMessage(self._hwnd, win32con.WM_CHAR, item, 0)

    def send_key(self,id):
        win32api.SendMessage(self._hwnd, win32con.WM_KEYDOWN, id, 0)
        win32api.SendMessage(self._hwnd, win32con.WM_KEYUP, id, 0)
