"""
OCR模块 - 处理文字识别
"""
import time
import cv2
import numpy as np
from enum import Enum
from typing import Tuple, List, Dict, Optional, Union, Any

class OcrMode(Enum):
    """OCR模式枚举"""
    FULL = 1         # 完整文本识别
    SINGLE = 2       # 单行文本识别
    DIGIT = 3        # 数字识别
    DIGITCOUNTER = 4 # 数字计数器识别
    DURATION = 5     # 时长识别
    QUANTITY = 6     # 数量识别

class OcrMethod(Enum):
    """OCR方法枚举"""
    DEFAULT = 1      # 默认方法

class OCR:
    """OCR类，负责处理文字识别"""
    
    def __init__(self, ocr_engine=None):
        """
        初始化OCR模块
        
        Args:
            ocr_engine: OCR引擎，如果为None则使用默认引擎
        """
        self.ocr_engine = ocr_engine
        self.lang = "ch"  # 默认语言为中文
        self.score = 0.6  # 默认置信度阈值
    
    def _ensure_ocr_engine(self):
        """确保OCR引擎已初始化"""
        if self.ocr_engine is None:
            try:
                # 尝试导入PaddleOCR
                from ppocronnx.predict_system import TextSystem
                self.ocr_engine = TextSystem()
                print("已初始化OCR引擎")
            except ImportError:
                print("未找到OCR引擎，请安装ppocronnx")
                return False
        return True
    
    def enlarge_canvas(self, image: np.ndarray) -> np.ndarray:
        """
        将图像扩展为正方形，并填充黑色背景
        
        Args:
            image: 原始图像
            
        Returns:
            np.ndarray: 扩展后的图像
        """
        height, width = image.shape[:2]
        length = int(max(width, height) // 32 * 32 + 32)
        border = (0, length - height, 0, length - width)
        if sum(border) > 0:
            image = cv2.copyMakeBorder(image, *border, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
        return image
    
    def ocr_single_line(self, image: np.ndarray) -> Tuple[str, float]:
        """
        识别单行文本
        
        Args:
            image: 图像数据
            
        Returns:
            Tuple[str, float]: (识别结果, 置信度)
        """
        if not self._ensure_ocr_engine():
            return "", 0.0
        
        try:
            # 预处理图像
            image = self.enlarge_canvas(image)
            
            # 执行OCR识别
            start_time = time.time()
            result, score = self.ocr_engine.ocr_single_line(image)
            
            # 记录识别时间
            elapsed_time = time.time() - start_time
            print(f"OCR识别耗时: {elapsed_time:.3f}秒")
            
            # 如果置信度低于阈值，返回空结果
            if score < self.score:
                return "", score
            
            return result, score
        except Exception as e:
            print(f"OCR识别出错: {e}")
            return "", 0.0
    
    def detect_and_ocr(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        检测并识别图像中的所有文本
        
        Args:
            image: 图像数据
            
        Returns:
            List[Dict[str, Any]]: 识别结果列表，每项包含文本、位置和置信度
        """
        if not self._ensure_ocr_engine():
            return []
        
        try:
            # 预处理图像
            image = self.enlarge_canvas(image)
            
            # 执行OCR识别
            start_time = time.time()
            boxed_results = self.ocr_engine.detect_and_ocr(image)
            
            # 记录识别时间
            elapsed_time = time.time() - start_time
            print(f"OCR检测识别耗时: {elapsed_time:.3f}秒")
            
            # 处理结果
            results = []
            for result in boxed_results:
                if result.score < self.score:
                    continue
                
                results.append({
                    "text": result.ocr_text,
                    "box": result.box,
                    "score": result.score
                })
            
            return results
        except Exception as e:
            print(f"OCR检测识别出错: {e}")
            return []
    
    def detect_text(self, image: np.ndarray) -> str:
        """
        识别图像中的所有文本并拼接
        
        Args:
            image: 图像数据
            
        Returns:
            str: 拼接后的文本
        """
        results = self.detect_and_ocr(image)
        return ''.join([result["text"] for result in results])

class BaseOcr:
    """基础OCR类，用于定义OCR规则"""
    
    def __init__(self, name: str, mode: str, method: str, roi: Tuple[int, int, int, int], 
                area: Tuple[int, int, int, int], keyword: str):
        """
        初始化基础OCR
        
        Args:
            name: OCR规则名称
            mode: OCR模式，可选值: "FULL", "SINGLE", "DIGIT", "DIGITCOUNTER", "DURATION", "QUANTITY"
            method: OCR方法，可选值: "DEFAULT"
            roi: 感兴趣区域 (x, y, width, height)
            area: 辅助区域 (x, y, width, height)
            keyword: 关键词
        """
        self.name = name.upper()
        
        # 设置OCR模式
        if isinstance(mode, str):
            self.mode = OcrMode[mode.upper()]
        elif isinstance(mode, OcrMode):
            self.mode = mode
        
        # 设置OCR方法
        if isinstance(method, str):
            self.method = OcrMethod[method.upper()]
        elif isinstance(method, OcrMethod):
            self.method = method
        
        self.roi = list(roi)
        self.area = list(area)
        self.keyword = keyword
        
        # OCR引擎相关
        self.lang = "ch"  # 默认语言为中文
        self.score = 0.6  # 默认置信度阈值
        self._ocr_engine = None
    
    @property
    def model(self):
        """获取OCR引擎"""
        if self._ocr_engine is None:
            try:
                # 尝试导入PaddleOCR
                from ppocronnx.predict_system import TextSystem
                self._ocr_engine = TextSystem()
            except ImportError:
                print("未找到OCR引擎，请安装ppocronnx")
        return self._ocr_engine
    
    def pre_process(self, image: np.ndarray) -> np.ndarray:
        """
        图像预处理
        
        Args:
            image: 原始图像
            
        Returns:
            np.ndarray: 预处理后的图像
        """
        # 默认不做处理，子类可重写此方法
        return image
    
    def after_process(self, result: str) -> str:
        """
        结果后处理
        
        Args:
            result: OCR识别结果
            
        Returns:
            str: 后处理后的结果
        """
        # 默认不做处理，子类可重写此方法
        return result
    
    @classmethod
    def crop(cls, image: np.ndarray, roi: Tuple[int, int, int, int]) -> np.ndarray:
        """
        裁剪图像
        
        Args:
            image: 原始图像
            roi: 感兴趣区域 (x, y, width, height)
            
        Returns:
            np.ndarray: 裁剪后的图像
        """
        x, y, w, h = roi
        return image[y:y+h, x:x+w]
    
    def enlarge_canvas(self, image: np.ndarray) -> np.ndarray:
        """
        将图像扩展为正方形，并填充黑色背景
        
        Args:
            image: 原始图像
            
        Returns:
            np.ndarray: 扩展后的图像
        """
        height, width = image.shape[:2]
        length = int(max(width, height) // 32 * 32 + 32)
        border = (0, length - height, 0, length - width)
        if sum(border) > 0:
            image = cv2.copyMakeBorder(image, *border, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
        return image
    
    def ocr_item(self, image: np.ndarray) -> str:
        """
        直接对图像进行OCR识别
        
        Args:
            image: 图像数据
            
        Returns:
            str: 识别结果
        """
        if self.model is None:
            return ""
        
        # 预处理
        start_time = time.time()
        image = self.pre_process(image)
        
        # OCR识别
        result, score = self.model.ocr_single_line(image)
        if score < self.score:
            result = ""
        
        # 后处理
        result = self.after_process(result)
        
        # 记录识别时间和结果
        elapsed_time = time.time() - start_time
        print(f"{self.name} OCR耗时: {elapsed_time:.3f}秒, 结果: [{result}]")
        
        return result
    
    def ocr_single_line(self, image: np.ndarray) -> str:
        """
        对ROI区域进行单行OCR识别
        
        Args:
            image: 图像数据
            
        Returns:
            str: 识别结果
        """
        if self.model is None:
            return ""
        
        # 预处理
        start_time = time.time()
        image = self.crop(image, self.roi)
        image = self.pre_process(image)
        
        # OCR识别
        result, score = self.model.ocr_single_line(image)
        if score < self.score:
            result = ""
        
        # 后处理
        result = self.after_process(result)
        
        # 记录识别时间和结果
        elapsed_time = time.time() - start_time
        print(f"{self.name} OCR耗时: {elapsed_time:.3f}秒, 结果: [{result}]")
        
        return result
    
    def detect_and_ocr(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        对ROI区域进行文本检测和识别
        
        Args:
            image: 图像数据
            
        Returns:
            List[Dict[str, Any]]: 识别结果列表
        """
        if self.model is None:
            return []
        
        # 预处理
        start_time = time.time()
        image = self.crop(image, self.roi)
        image = self.pre_process(image)
        image = self.enlarge_canvas(image)
        
        # OCR检测和识别
        boxed_results = self.model.detect_and_ocr(image)
        
        # 处理结果
        results = []
        for result in boxed_results:
            if result.score < self.score:
                continue
            
            # 后处理
            result.ocr_text = self.after_process(result.ocr_text)
            
            results.append({
                "text": result.ocr_text,
                "box": result.box,
                "score": result.score
            })
        
        # 记录识别时间和结果
        elapsed_time = time.time() - start_time
        texts = [result["text"] for result in results]
        print(f"{self.name} OCR检测识别耗时: {elapsed_time:.3f}秒, 结果: {texts}")
        
        return results
    
    def match(self, result: str, included: bool = False) -> bool:
        """
        匹配OCR结果和关键词
        
        Args:
            result: OCR识别结果
            included: 是否为包含关系，True表示只要包含关键词即可，False表示必须完全匹配
            
        Returns:
            bool: 是否匹配
        """
        if included:
            return self.keyword in result
        else:
            return self.keyword == result
    
    def filter(self, boxed_results: List[Dict[str, Any]], keyword: str = None) -> List[int]:
        """
        过滤OCR结果
        
        Args:
            boxed_results: OCR识别结果列表
            keyword: 关键词，如果为None则使用默认关键词
            
        Returns:
            List[int]: 匹配的结果索引列表
        """
        # 获取所有文本
        strings = [result["text"] for result in boxed_results]
        
        # 拼接所有文本
        concatenated_string = "".join(strings)
        
        # 使用默认关键词
        if keyword is None:
            keyword = self.keyword
        
        # 在拼接文本中查找关键词
        if keyword in concatenated_string:
            # 返回包含关键词的文本索引
            return [index for index, word in enumerate(strings) if keyword in word]
        
        # 如果拼接文本中没有找到关键词，尝试逐字符匹配
        indices = []
        max_index = len(strings) - 1
        
        # 对于关键词中的每个字符，在文本列表中查找
        for char in keyword:
            for i, string in enumerate(strings):
                if char in string and i <= max_index:
                    indices.append(i)
                    break
        
        # 去重并返回
        if indices:
            return list(set(indices))
        else:
            return None
    
    def detect_text(self, image: np.ndarray) -> str:
        """
        识别ROI区域中的所有文本并拼接
        
        Args:
            image: 图像数据
            
        Returns:
            str: 拼接后的文本
        """
        if self.model is None:
            return ""
        
        # 预处理
        start_time = time.time()
        image = self.crop(image, self.roi)
        image = self.pre_process(image)
        image = self.enlarge_canvas(image)
        
        # OCR检测和识别
        boxed_results = self.model.detect_and_ocr(image)
        
        # 拼接结果
        results = ""
        for result in boxed_results:
            if result.score < self.score:
                continue
            results += self.after_process(result.ocr_text)
        
        # 记录识别时间和结果
        elapsed_time = time.time() - start_time
        print(f"{self.name} OCR文本检测耗时: {elapsed_time:.3f}秒, 结果: [{results}]")
        
        return results