#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结界突破功能测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tasks.kekkai_toppa.kekkai_toppa import KekkaiToppaTask
from tasks.kekkai_toppa.config import KekkaiToppaConfig, ToppaMode
from core.logger import logger

def test_kekkai_toppa_initialization():
    """测试结界突破任务初始化"""
    logger.info("=== 测试结界突破任务初始化 ===")
    
    try:
        # 创建配置
        config_manager = KekkaiToppaConfig()
        config = config_manager.get_config()
        
        # 创建任务实例
        task = KekkaiToppaTask(config)
        
        logger.info(f"任务名称: {task.task_name}")
        logger.info(f"配置模式: {config.get('mode')}")
        logger.info(f"时间限制: {config.get('limit_time_minutes')} 分钟")
        logger.info(f"次数限制: {config.get('limit_count')} 次")
        logger.info(f"跳过困难区域: {config.get('skip_difficult')}")
        logger.info(f"随机延迟: {config.get('random_delay')}")
        logger.info(f"锁定队伍: {config.get('enable_lock_team')}")
        
        # 测试区域映射
        logger.info(f"区域映射数量: {len(task.area_map)}")
        for i, area in enumerate(task.area_map[:3]):  # 只显示前3个区域
            logger.info(f"区域{i+1}: {area['name']} - 规则点击: {area['rule_click']}")
        
        logger.info("✅ 结界突破任务初始化测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 结界突破任务初始化测试失败: {e}")
        return False

def test_config_compatibility():
    """测试配置兼容性"""
    logger.info("=== 测试配置兼容性 ===")
    
    try:
        config_manager = KekkaiToppaConfig()
        
        # 测试个人突破配置
        personal_config = {
            "mode": ToppaMode.PERSONAL,
            "limit_time_minutes": 30,
            "limit_count": 50,
            "skip_difficult": True,
            "random_delay": False,
            "enable_lock_team": False,
            "personal_areas": [1, 2, 3, 4, 5, 6, 7, 8]
        }
        
        # 逐个更新配置项
        for key, value in personal_config.items():
            config_manager.update_config(key, value)
        updated_config = config_manager.get_config()
        
        # 验证配置更新
        assert updated_config["mode"] == ToppaMode.PERSONAL
        assert updated_config["limit_time_minutes"] == 30
        assert updated_config["limit_count"] == 50
        assert updated_config["skip_difficult"] == True
        assert updated_config["random_delay"] == False
        assert updated_config["enable_lock_team"] == False
        
        logger.info("✅ 配置兼容性测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 配置兼容性测试失败: {e}")
        return False

def test_area_mapping():
    """测试区域映射"""
    logger.info("=== 测试区域映射 ===")
    
    try:
        config_manager = KekkaiToppaConfig()
        config = config_manager.get_config()
        task = KekkaiToppaTask(config)
        
        # 验证区域映射结构
        assert len(task.area_map) == 8, f"期望8个区域，实际{len(task.area_map)}个"
        
        for i, area in enumerate(task.area_map):
            area_num = i + 1
            expected_name = f"区域{area_num}"
            expected_rule_click = f"C_AREA_{area_num}"
            
            assert area["name"] == expected_name, f"区域{area_num}名称不匹配"
            assert area["rule_click"] == expected_rule_click, f"区域{area_num}规则点击不匹配"
            assert "fail_sign" in area, f"区域{area_num}缺少失败标志"
            assert "finished_sign" in area, f"区域{area_num}缺少完成标志"
        
        logger.info("✅ 区域映射测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 区域映射测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("开始结界突破功能测试")
    
    tests = [
        test_kekkai_toppa_initialization,
        test_config_compatibility,
        test_area_mapping
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        logger.info("-" * 50)
    
    logger.info(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！结界突破功能修复成功")
        return True
    else:
        logger.error(f"❌ {total - passed} 个测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)