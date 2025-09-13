"""结界突破资源管理

该模块定义了结界突破任务所需的各种资源，包括：
- 个人突破资源
- 阴阳寮突破资源
- 图像识别规则
- 点击区域定义
- OCR识别规则
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ClickRule:
    """点击规则"""
    name: str
    roi_front: str
    roi_back: str
    description: str
    
    @property
    def coordinates(self) -> Tuple[int, int, int, int]:
        """获取坐标元组 (x, y, width, height)"""
        parts = self.roi_front.split(',')
        return tuple(map(int, parts))


@dataclass
class ImageRule:
    """图像识别规则"""
    name: str
    roi_front: str
    roi_back: str
    threshold: float
    method: str
    description: str
    
    @property
    def coordinates(self) -> Tuple[int, int, int, int]:
        """获取坐标元组 (x, y, width, height)"""
        parts = self.roi_front.split(',')
        return tuple(map(int, parts))


@dataclass
class OCRRule:
    """OCR识别规则"""
    name: str
    roi: str
    area: str
    mode: str
    method: str
    keyword: str
    description: str
    
    @property
    def coordinates(self) -> Tuple[int, int, int, int]:
        """获取坐标元组 (x, y, width, height)"""
        parts = self.roi.split(',')
        return tuple(map(int, parts))


class KekkaiToppaAssets:
    """结界突破资源管理器"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = os.path.dirname(__file__)
        self.base_path = base_path
        self.dev_path = os.path.join(base_path, 'dev')
        self.res_path = os.path.join(base_path, 'res')
        
        # 加载资源
        self._load_personal_assets()
        self._load_guild_assets()
    
    def _load_personal_assets(self):
        """加载个人突破资源"""
        # 个人突破区域点击规则
        self.personal_areas = {
            1: ClickRule("area_1", "533,162,177,74", "533,162,177,74", "区域1"),
            2: ClickRule("area_2", "863,164,181,71", "863,164,181,71", "区域2"),
            3: ClickRule("area_3", "532,292,181,87", "532,292,181,87", "区域3"),
            4: ClickRule("area_4", "863,301,171,62", "863,301,171,62", "区域4"),
            5: ClickRule("area_5", "540,432,169,68", "540,432,169,68", "区域5"),
            6: ClickRule("area_6", "876,432,165,74", "876,432,165,74", "区域6"),
            7: ClickRule("area_7", "538,557,149,71", "538,557,149,71", "区域7"),
            8: ClickRule("area_8", "876,562,150,67", "876,562,150,67", "区域8"),
        }
        
        # 个人突破状态识别
        self.personal_status = {
            "failure_signs": {
                1: [ImageRule("area_1_failure", "673,146,63,32", "421,127,325,134", 0.8, "Template matching", "区域1失败标识"),
                    ImageRule("area_1_failure_new", "673,146,63,32", "421,123,325,138", 0.8, "Template matching", "区域1失败标识新")],
                2: [ImageRule("area_2_failure", "1011,146,63,30", "757,125,327,140", 0.8, "Template matching", "区域2失败标识"),
                    ImageRule("area_2_failure_new", "1011,146,63,30", "757,126,327,139", 0.8, "Template matching", "区域2失败标识新")],
                3: [ImageRule("area_3_failure", "665,283,73,40", "419,254,327,144", 0.8, "Template matching", "区域3失败标识"),
                    ImageRule("area_3_failure_new", "665,283,73,40", "419,261,327,137", 0.8, "Template matching", "区域3失败标识新")],
                4: [ImageRule("area_4_failure", "1000,283,72,38", "756,260,325,139", 0.8, "Template matching", "区域4失败标识"),
                    ImageRule("area_4_failure_new", "1000,283,72,38", "756,258,325,141", 0.8, "Template matching", "区域4失败标识新")],
                5: [ImageRule("area_5_failure", "669,419,65,29", "418,392,328,142", 0.8, "Template matching", "区域5失败标识"),
                    ImageRule("area_5_failure_new", "669,419,65,29", "418,394,328,140", 0.8, "Template matching", "区域5失败标识新")],
                6: [ImageRule("area_6_failure", "988,416,84,37", "755,395,328,141", 0.8, "Template matching", "区域6失败标识"),
                    ImageRule("area_6_failure_new", "988,416,84,37", "755,395,328,141", 0.8, "Template matching", "区域6失败标识新")],
                7: [ImageRule("area_7_failure", "672,556,61,37", "420,530,326,127", 0.8, "Template matching", "区域7失败标识"),
                    ImageRule("area_7_failure_new", "672,556,61,37", "420,533,326,124", 0.8, "Template matching", "区域7失败标识新")],
                8: [ImageRule("area_8_failure", "1004,556,64,29", "756,530,327,124", 0.8, "Template matching", "区域8失败标识"),
                    ImageRule("area_8_failure_new", "1004,556,64,29", "756,532,327,122", 0.8, "Template matching", "区域8失败标识新")],
            },
            "finished_signs": {
                1: [ImageRule("area_1_finished", "658,141,93,91", "421,127,325,134", 0.8, "Template matching", "区域1完成标识"),
                    ImageRule("area_1_finished_new", "658,141,93,91", "421,127,325,134", 0.8, "Template matching", "区域1完成标识新")],
                2: [ImageRule("area_2_finished", "983,137,100,100", "757,125,327,140", 0.8, "Template matching", "区域2完成标识"),
                    ImageRule("area_2_finished_new", "983,137,100,100", "757,125,327,140", 0.8, "Template matching", "区域2完成标识新")],
                3: [ImageRule("area_3_finished", "681,312,47,37", "419,254,327,144", 0.8, "Template matching", "区域3完成标识"),
                    ImageRule("area_3_finished_new", "681,312,47,37", "419,254,327,144", 0.8, "Template matching", "区域3完成标识新")],
                4: [ImageRule("area_4_finished", "996,271,100,100", "756,260,325,139", 0.8, "Template matching", "区域4完成标识"),
                    ImageRule("area_4_finished_new", "996,271,100,100", "756,260,325,139", 0.8, "Template matching", "区域4完成标识新")],
                5: [ImageRule("area_5_finished", "647,404,100,100", "418,392,328,142", 0.8, "Template matching", "区域5完成标识"),
                    ImageRule("area_5_finished_new", "647,404,100,100", "418,392,328,142", 0.8, "Template matching", "区域5完成标识新")],
                6: [ImageRule("area_6_finished", "1015,448,56,35", "755,395,328,141", 0.8, "Template matching", "区域6完成标识"),
                    ImageRule("area_6_finished_new", "1015,448,56,35", "755,395,328,141", 0.8, "Template matching", "区域6完成标识新")],
                7: [ImageRule("area_7_finished", "643,543,100,100", "420,530,326,127", 0.8, "Template matching", "区域7完成标识"),
                    ImageRule("area_7_finished_new", "643,543,100,100", "420,530,326,127", 0.8, "Template matching", "区域7完成标识新")],
                8: [ImageRule("area_8_finished", "983,541,100,100", "756,530,327,124", 0.8, "Template matching", "区域8完成标识"),
                    ImageRule("area_8_finished_new", "983,541,100,100", "756,530,327,124", 0.8, "Template matching", "区域8完成标识新")],
            }
        }
    
    def _load_guild_assets(self):
        """加载阴阳寮突破资源"""
        # 加载点击规则
        click_file = os.path.join(self.res_path, 'click.json')
        if os.path.exists(click_file):
            with open(click_file, 'r', encoding='utf-8') as f:
                click_data = json.load(f)
            self.guild_clicks = {item['itemName']: ClickRule(
                item['itemName'], item['roiFront'], item['roiBack'], item['description']
            ) for item in click_data}
        else:
            self.guild_clicks = {}
        
        # 加载图像规则
        image_file = os.path.join(self.res_path, 'image.json')
        if os.path.exists(image_file):
            with open(image_file, 'r', encoding='utf-8') as f:
                image_data = json.load(f)
            self.guild_images = {item['itemName']: ImageRule(
                item['itemName'], item['roiFront'], item['roiBack'], 
                item['threshold'], item['method'], item['description']
            ) for item in image_data}
        else:
            self.guild_images = {}
        
        # 加载OCR规则
        ocr_file = os.path.join(self.res_path, 'ocr.json')
        if os.path.exists(ocr_file):
            with open(ocr_file, 'r', encoding='utf-8') as f:
                ocr_data = json.load(f)
            self.guild_ocrs = {item['itemName']: OCRRule(
                item['itemName'], item['roi'], item['area'], 
                item['mode'], item['method'], item['keyword'], item['description']
            ) for item in ocr_data}
        else:
            self.guild_ocrs = {}
    
    def get_personal_area_click(self, area_id: int) -> Optional[ClickRule]:
        """获取个人突破区域点击规则"""
        return self.personal_areas.get(area_id)
    
    def get_personal_failure_signs(self, area_id: int) -> List[ImageRule]:
        """获取个人突破区域失败标识"""
        return self.personal_status["failure_signs"].get(area_id, [])
    
    def get_personal_finished_signs(self, area_id: int) -> List[ImageRule]:
        """获取个人突破区域完成标识"""
        return self.personal_status["finished_signs"].get(area_id, [])
    
    def get_guild_click(self, name: str) -> Optional[ClickRule]:
        """获取阴阳寮突破点击规则"""
        return self.guild_clicks.get(name)
    
    def get_guild_image(self, name: str) -> Optional[ImageRule]:
        """获取阴阳寮突破图像规则"""
        return self.guild_images.get(name)
    
    def get_guild_ocr(self, name: str) -> Optional[OCRRule]:
        """获取阴阳寮突破OCR规则"""
        return self.guild_ocrs.get(name)


# 全局资源实例
assets = KekkaiToppaAssets()