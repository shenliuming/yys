#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试结界突破模式功能"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from tasks.kekkai_toppa.config import ToppaMode, create_config
from tasks.kekkai_toppa.kekkai_toppa import KekkaiToppaTask
from tasks.kekkai_toppa.assets import KekkaiToppaAssets

def test_personal_mode():
    """测试个人突破模式"""
    print("\n=== 测试个人突破模式 ===")
    
    try:
        # 创建配置
        config = create_config('default')
        config_dict = config.get_config()
        config_dict['toppa_mode'] = ToppaMode.PERSONAL
        
        # 创建任务实例
        task = KekkaiToppaTask(None)
        task.update_config(config_dict)
        
        print(f"✅ 个人突破模式配置成功")
        print(f"   突破模式: {config_dict['toppa_mode']}")
        print(f"   任务名称: {config_dict['task_name']}")
        print(f"   时间限制: {config_dict['limit_time_minutes']} 分钟")
        
        return True
    except Exception as e:
        print(f"❌ 个人突破模式测试失败: {e}")
        return False

def test_guild_mode():
    """测试阴阳寮突破模式"""
    print("\n=== 测试阴阳寮突破模式 ===")
    
    try:
        # 创建配置
        config = create_config('default')
        config_dict = config.get_config()
        config_dict['toppa_mode'] = ToppaMode.GUILD
        
        # 创建任务实例
        task = KekkaiToppaTask(None)
        task.update_config(config_dict)
        
        print(f"✅ 阴阳寮突破模式配置成功")
        print(f"   突破模式: {config_dict['toppa_mode']}")
        print(f"   任务名称: {config_dict['task_name']}")
        print(f"   时间限制: {config_dict['limit_time_minutes']} 分钟")
        
        return True
    except Exception as e:
        print(f"❌ 阴阳寮突破模式测试失败: {e}")
        return False

def test_assets():
    """测试资源管理器"""
    print("\n=== 测试资源管理器 ===")
    
    try:
        assets = KekkaiToppaAssets()
        
        # 测试个人突破资源
        area_1_click = assets.get_personal_area_click(1)
        if area_1_click:
            print(f"✅ 个人突破区域1点击规则: {area_1_click.description}")
        
        failure_signs = assets.get_personal_failure_signs(1)
        if failure_signs:
            print(f"✅ 个人突破区域1失败标识: {len(failure_signs)} 个")
        
        # 测试阴阳寮突破资源
        guild_click = assets.get_guild_click('select_first_ryou')
        if guild_click:
            print(f"✅ 阴阳寮突破点击规则: {guild_click.description}")
        
        guild_image = assets.get_guild_image('ryou_toppa_button')
        if guild_image:
            print(f"✅ 阴阳寮突破图像规则: {guild_image.description}")
        
        guild_ocr = assets.get_guild_ocr('guild_toppa_number')
        if guild_ocr:
            print(f"✅ 阴阳寮突破OCR规则: {guild_ocr.description}")
        
        return True
    except Exception as e:
        print(f"❌ 资源管理器测试失败: {e}")
        return False

def test_config_templates():
    """测试配置模板"""
    print("\n=== 测试配置模板 ===")
    
    templates = ['default', 'fast', 'thorough', 'debug']
    success_count = 0
    
    for template_name in templates:
        try:
            config = create_config(template_name)
            config_dict = config.get_config()
            print(f"✅ 配置模板 '{template_name}': {config_dict['task_name']}")
            success_count += 1
        except Exception as e:
            print(f"❌ 配置模板 '{template_name}' 测试失败: {e}")
    
    return success_count == len(templates)

def main():
    """主测试函数"""
    print("结界突破功能测试")
    print("=" * 50)
    
    tests = [
        test_config_templates,
        test_personal_mode,
        test_guild_mode,
        test_assets,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！结界突破功能正常")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)