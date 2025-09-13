"""
图像识别模块 - 处理图像模板匹配
"""
import os
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional, Union, Dict

class Image:
    """图像类，负责处理图像识别和模板匹配"""
    
    def __init__(self):
        """初始化图像模块"""
        self.sift = cv2.SIFT_create()  # 创建SIFT特征检测器
    
    def crop(self, image: np.ndarray, roi: Tuple[int, int, int, int]) -> np.ndarray:
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
    
    def match_template(self, image: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> Tuple[bool, Tuple[int, int]]:
        """
        模板匹配
        
        Args:
            image: 原始图像
            template: 模板图像
            threshold: 匹配阈值，越高要求越严格
            
        Returns:
            Tuple[bool, Tuple[int, int]]: (是否匹配成功, (匹配位置x, 匹配位置y))
        """
        # 检查图像和模板是否有效
        if image is None or template is None:
            print("图像或模板为空")
            return False, (0, 0)
        
        if template.shape[0] > image.shape[0] or template.shape[1] > image.shape[1]:
            print("模板尺寸大于图像尺寸")
            return False, (0, 0)
        
        # 执行模板匹配
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # 判断是否匹配成功
        if max_val >= threshold:
            return True, max_loc
        else:
            return False, (0, 0)
    
    def find_template(self, image: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        查找模板在图像中的位置
        
        Args:
            image: 原始图像
            template: 模板图像
            threshold: 匹配阈值
            
        Returns:
            Optional[Tuple[int, int]]: 如果找到返回位置坐标，否则返回None
        """
        found, pos = self.match_template(image, template, threshold)
        return pos if found else None
    
    def match_template_in_roi(self, image: np.ndarray, template: np.ndarray, roi: Tuple[int, int, int, int], 
                             threshold: float = 0.8) -> Tuple[bool, Tuple[int, int]]:
        """
        在指定区域内进行模板匹配
        
        Args:
            image: 原始图像
            template: 模板图像
            roi: 感兴趣区域 (x, y, width, height)
            threshold: 匹配阈值，越高要求越严格
            
        Returns:
            Tuple[bool, Tuple[int, int]]: (是否匹配成功, (匹配位置x, 匹配位置y))
        """
        # 裁剪感兴趣区域
        roi_image = self.crop(image, roi)
        
        # 执行模板匹配
        success, (x, y) = self.match_template(roi_image, template, threshold)
        
        # 如果匹配成功，转换坐标到原图
        if success:
            return True, (roi[0] + x, roi[1] + y)
        else:
            return False, (0, 0)
    
    def find_all_template(self, image: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> List[Tuple[float, int, int]]:
        """
        查找图像中所有匹配模板的位置
        
        Args:
            image: 原始图像
            template: 模板图像
            threshold: 匹配阈值，越高要求越严格
            
        Returns:
            List[Tuple[float, int, int]]: 匹配结果列表，每项为 (匹配度, x坐标, y坐标)
        """
        # 检查图像和模板是否有效
        if image is None or template is None:
            print("图像或模板为空")
            return []
        
        if template.shape[0] > image.shape[0] or template.shape[1] > image.shape[1]:
            print("模板尺寸大于图像尺寸")
            return []
        
        # 执行模板匹配
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        
        # 查找所有匹配位置
        locations = np.where(result >= threshold)
        matches = []
        
        # 收集匹配结果
        for pt in zip(*locations[::-1]):  # (x, y) 坐标
            score = result[pt[1], pt[0]]
            matches.append((score, pt[0], pt[1]))
        
        # 按匹配度排序
        matches.sort(reverse=True, key=lambda x: x[0])
        return matches
    
    def match_sift(self, image: np.ndarray, template: np.ndarray, min_match_count: int = 10) -> Tuple[bool, Tuple[int, int]]:
        """
        使用SIFT特征匹配
        
        Args:
            image: 原始图像
            template: 模板图像
            min_match_count: 最小匹配点数
            
        Returns:
            Tuple[bool, Tuple[int, int]]: (是否匹配成功, (匹配位置x, 匹配位置y))
        """
        # 检查图像和模板是否有效
        if image is None or template is None:
            print("图像或模板为空")
            return False, (0, 0)
        
        # 提取特征点和描述符
        kp1, des1 = self.sift.detectAndCompute(template, None)
        kp2, des2 = self.sift.detectAndCompute(image, None)
        
        # 如果没有足够的特征点，返回失败
        if des1 is None or des2 is None or len(kp1) < min_match_count or len(kp2) < min_match_count:
            print("特征点不足")
            return False, (0, 0)
        
        # 创建FLANN匹配器
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        
        # 进行特征匹配
        matches = flann.knnMatch(des1, des2, k=2)
        
        # 应用比率测试，筛选好的匹配
        good_matches = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good_matches.append(m)
        
        # 如果好的匹配点数量足够
        if len(good_matches) >= min_match_count:
            # 获取匹配点的坐标
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            
            # 计算单应性矩阵
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            
            if M is not None:
                # 计算模板的中心点在原图中的位置
                h, w = template.shape[:2]
                center_pt = np.float32([[w/2, h/2]]).reshape(-1, 1, 2)
                transformed_pt = cv2.perspectiveTransform(center_pt, M)
                
                return True, (int(transformed_pt[0][0][0]), int(transformed_pt[0][0][1]))
        
        return False, (0, 0)
    
    def match_color(self, image: np.ndarray, roi: Tuple[int, int, int, int], target_color: Tuple[int, int, int], 
                   tolerance: int = 10) -> bool:
        """
        检查区域内的平均颜色是否匹配目标颜色
        
        Args:
            image: 原始图像
            roi: 感兴趣区域 (x, y, width, height)
            target_color: 目标颜色 (R, G, B)
            tolerance: 颜色容差
            
        Returns:
            bool: 是否匹配
        """
        # 裁剪感兴趣区域
        roi_image = self.crop(image, roi)
        
        # 计算区域内的平均颜色
        average_color = cv2.mean(roi_image)[:3]  # 取RGB通道
        
        # 检查每个通道是否在容差范围内
        for i in range(3):
            if abs(average_color[i] - target_color[i]) > tolerance:
                return False
        
        return True
    
    def find_color_area(self, image: np.ndarray, target_color: Tuple[int, int, int], tolerance: int = 10) -> List[Tuple[int, int, int, int]]:
        """
        查找图像中符合目标颜色的区域
        
        Args:
            image: 原始图像
            target_color: 目标颜色 (R, G, B)
            tolerance: 颜色容差
            
        Returns:
            List[Tuple[int, int, int, int]]: 匹配区域列表，每项为 (x, y, width, height)
        """
        # 创建颜色范围掩码
        lower_bound = np.array([max(0, c - tolerance) for c in target_color])
        upper_bound = np.array([min(255, c + tolerance) for c in target_color])
        
        # 创建掩码
        mask = cv2.inRange(image, lower_bound, upper_bound)
        
        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 获取轮廓的边界框
        results = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            results.append((x, y, w, h))
        
        return results

class RuleImage:
    """规则图像类，用于定义图像匹配规则"""
    
    def __init__(self, roi_front: Tuple[int, int, int, int], roi_back: Tuple[int, int, int, int], 
                method: str, threshold: float, file: str):
        """
        初始化规则图像
        
        Args:
            roi_front: 前置ROI (x, y, width, height)
            roi_back: 后置ROI (x, y, width, height)
            method: 匹配方法，可选值: "Template matching", "Sift Flann"
            threshold: 匹配阈值
            file: 模板图像文件路径
        """
        self._match_init = False
        self._image = None
        self._kp = None
        self._des = None
        self.method = method
        
        self.roi_front = list(roi_front)
        self.roi_back = list(roi_back)
        self.threshold = threshold
        self.file = file
        
        # 加载图像
        self.load_image()
    
    @property
    def name(self) -> str:
        """获取规则名称"""
        return Path(self.file).stem.upper()
    
    def __str__(self):
        return self.name
    
    __repr__ = __str__
    
    def load_image(self) -> None:
        """加载模板图像"""
        if self._image is not None:
            return
        
        try:
            img = cv2.imread(self.file)
            if img is None:
                print(f"无法加载图像: {self.file}")
                return
            
            # 转换颜色空间从BGR到RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self._image = img
            
            # 更新ROI尺寸
            height, width, _ = self._image.shape
            if height != self.roi_front[3] or width != self.roi_front[2]:
                self.roi_front[2] = width
                self.roi_front[3] = height
                print(f"{self.name} roi_front尺寸已更新为 {width}x{height}")
        except Exception as e:
            print(f"加载图像时出错: {e}")
    
    def load_kp_des(self) -> None:
        """加载特征点和描述符"""
        if self._kp is not None and self._des is not None:
            return
        
        if self._image is None:
            self.load_image()
            if self._image is None:
                return
        
        # 创建SIFT特征检测器
        sift = cv2.SIFT_create()
        self._kp, self._des = sift.detectAndCompute(self._image, None)
    
    @property
    def image(self) -> np.ndarray:
        """获取模板图像"""
        if self._image is None:
            self.load_image()
        return self._image
    
    @property
    def is_template_match(self) -> bool:
        """是否使用模板匹配"""
        return self.method == "Template matching"
    
    @property
    def is_sift_flann(self) -> bool:
        """是否使用SIFT特征匹配"""
        return self.method == "Sift Flann"
    
    @property
    def kp(self):
        """获取特征点"""
        if self._kp is None:
            self.load_kp_des()
        return self._kp
    
    @property
    def des(self):
        """获取描述符"""
        if self._des is None:
            self.load_kp_des()
        return self._des
    
    def corp(self, image: np.ndarray, roi: List[int] = None) -> np.ndarray:
        """
        裁剪图像
        
        Args:
            image: 原始图像
            roi: 感兴趣区域 [x, y, width, height]，如果为None则使用roi_back
            
        Returns:
            np.ndarray: 裁剪后的图像
        """
        if roi is None:
            x, y, w, h = self.roi_back
        else:
            x, y, w, h = roi
        
        x, y, w, h = int(x), int(y), int(w), int(h)
        return image[y:y+h, x:x+w]
    
    def match(self, image: np.ndarray, threshold: float = None) -> bool:
        """
        匹配图像
        
        Args:
            image: 原始图像
            threshold: 匹配阈值，如果为None则使用默认阈值
            
        Returns:
            bool: 是否匹配成功
        """
        if threshold is None:
            threshold = self.threshold
        
        if not self.is_template_match:
            return self.sift_match(image)
        
        # 裁剪感兴趣区域
        source = self.corp(image)
        mat = self.image
        
        # 检查模板是否有效
        if mat is None or mat.shape[0] == 0 or mat.shape[1] == 0:
            print(f"模板图像无效: {mat.shape if mat is not None else None}")
            return True  # 如果模板无效，直接返回True
        
        # 执行模板匹配
        res = cv2.matchTemplate(source, mat, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        # 判断是否匹配成功
        if max_val > threshold:
            # 更新前置ROI位置
            self.roi_front[0] = max_loc[0] + self.roi_back[0]
            self.roi_front[1] = max_loc[1] + self.roi_back[1]
            return True
        else:
            return False
    
    def match_all(self, image: np.ndarray, threshold: float = None, roi: List[int] = None) -> List[Tuple[float, int, int, int, int]]:
        """
        查找所有匹配位置
        
        Args:
            image: 原始图像
            threshold: 匹配阈值，如果为None则使用默认阈值
            roi: 感兴趣区域 [x, y, width, height]，如果为None则使用roi_back
            
        Returns:
            List[Tuple[float, int, int, int, int]]: 匹配结果列表，每项为 (匹配度, x, y, width, height)
        """
        if roi is not None:
            self.roi_back = roi
        
        if threshold is None:
            threshold = self.threshold
        
        if not self.is_template_match:
            raise Exception(f"不支持的匹配方法: {self.method}")
        
        # 裁剪感兴趣区域
        source = self.corp(image)
        mat = self.image
        
        # 执行模板匹配
        results = cv2.matchTemplate(source, mat, cv2.TM_CCOEFF_NORMED)
        locations = np.where(results >= threshold)
        
        # 收集匹配结果
        matches = []
        for pt in zip(*locations[::-1]):  # (x, y) 坐标
            score = results[pt[1], pt[0]]
            # 转换坐标到原图
            x = self.roi_back[0] + pt[0]
            y = self.roi_back[1] + pt[1]
            matches.append((score, x, y, mat.shape[1], mat.shape[0]))
        
        return matches
    
    def coord(self) -> Tuple[int, int]:
        """
        获取前置ROI内的随机坐标
        
        Returns:
            Tuple[int, int]: 随机坐标 (x, y)
        """
        x, y, w, h = self.roi_front
        return x + np.random.randint(0, w), y + np.random.randint(0, h)
    
    def coord_more(self) -> Tuple[int, int]:
        """
        获取后置ROI内的随机坐标
        
        Returns:
            Tuple[int, int]: 随机坐标 (x, y)
        """
        x, y, w, h = self.roi_back
        return x + np.random.randint(0, w), y + np.random.randint(0, h)
    
    def front_center(self) -> Tuple[int, int]:
        """
        获取前置ROI的中心坐标
        
        Returns:
            Tuple[int, int]: 中心坐标 (x, y)
        """
        x, y, w, h = self.roi_front
        return int(x + w//2), int(y + h//2)
    
    def sift_match(self, image: np.ndarray, show: bool = False) -> bool:
        """
        使用SIFT特征匹配
        
        Args:
            image: 原始图像
            show: 是否显示匹配结果
            
        Returns:
            bool: 是否匹配成功
        """
        # 裁剪感兴趣区域
        source = self.corp(image)
        
        # 提取特征点和描述符
        sift = cv2.SIFT_create()
        kp, des = sift.detectAndCompute(source, None)
        
        # 创建FLANN匹配器
        index_params = dict(algorithm=1, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        
        # 进行特征匹配
        matches = flann.knnMatch(self.des, des, k=2)
        
        # 筛选好的匹配
        good = []
        result = True
        for i, (m, n) in enumerate(matches):
            if m.distance < 0.6 * n.distance:
                good.append(m)
        
        # 如果好的匹配点数量足够
        if len(good) >= 10:
            # 获取匹配点的坐标
            src_pts = np.float32([self.kp[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            
            # 计算单应性矩阵
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            
            # 如果计算成功
            if M is not None:
                # 计算模板四个角在原图中的位置
                w, h = self.roi_front[2], self.roi_front[3]
                pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
                dst = np.int32(cv2.perspectiveTransform(pts, M))
                
                # 更新前置ROI位置
                self.roi_front[0] = dst[0, 0, 0] + self.roi_back[0]
                self.roi_front[1] = dst[0, 0, 1] + self.roi_back[1]
                
                # 如果需要显示匹配结果
                if show:
                    cv2.polylines(source, [dst], isClosed=True, color=(0, 0, 255), thickness=2)
                
                # 检查变换后的形状是否接近矩形
                if not self._is_approx_rectangle(np.array([pos[0] for pos in dst])):
                    result = False
            else:
                result = False
        else:
            result = False
        
        # 如果需要显示匹配结果
        if show:
            # 准备掩码
            mask_matches = [[0, 0] for _ in range(len(matches))]
            for i, (m, n) in enumerate(matches):
                if m.distance < 0.6 * n.distance:
                    mask_matches[i] = [1, 0]
            
            # 绘制匹配结果
            img_matches = cv2.drawMatchesKnn(self.image, self.kp, source, kp, matches, None,
                                           matchColor=(0, 255, 0), singlePointColor=(255, 0, 0),
                                           matchesMask=mask_matches, flags=0)
            
            cv2.imshow(f'Sift Flann: {self.name}', img_matches)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        return result
    
    def _is_approx_rectangle(self, points: np.ndarray) -> bool:
        """
        检查点集是否近似构成矩形
        
        Args:
            points: 点集
            
        Returns:
            bool: 是否近似矩形
        """
        # 计算边长
        edges = []
        for i in range(4):
            edge = np.linalg.norm(points[i] - points[(i+1)%4])
            edges.append(edge)
        
        # 检查对边是否近似相等
        return (abs(edges[0] - edges[2]) / max(edges[0], edges[2]) < 0.2 and
                abs(edges[1] - edges[3]) / max(edges[1], edges[3]) < 0.2)
    
    def match_mean_color(self, image: np.ndarray, color: Tuple[int, int, int], bias: int = 10) -> bool:
        """
        检查区域内的平均颜色是否匹配目标颜色
        
        Args:
            image: 原始图像
            color: 目标颜色 (R, G, B)
            bias: 颜色容差
            
        Returns:
            bool: 是否匹配
        """
        # 裁剪感兴趣区域
        image = self.corp(image)
        
        # 计算区域内的平均颜色
        average_color = cv2.mean(image)[:3]  # 取RGB通道
        
        # 检查每个通道是否在容差范围内
        for i in range(3):
            if abs(average_color[i] - color[i]) > bias:
                return False
        
        return True