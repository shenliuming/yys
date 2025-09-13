"""任务模块

包含周年庆任务和探索任务等游戏自动化任务。
"""

__version__ = '1.0.0'

def register_all_tasks():
    """注册所有任务"""
    try:
        # 注册周年庆任务
        from .anniversary.anniversary_task import register_task as register_anniversary
        register_anniversary()
        
        # 注册探索任务 - 暂时注释掉
        # from .exploration.exploration import register_task as register_exploration
        # register_exploration()
        
        print("任务注册完成")
    except Exception as e:
        print(f"任务注册失败: {e}")