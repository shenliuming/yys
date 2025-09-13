# -*- coding: utf-8 -*-
"""结界突破任务模块"""

try:
    from .kekkai_toppa import KekkaiToppaTask
    __all__ = ['KekkaiToppaTask']
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from tasks.kekkai_toppa.kekkai_toppa import KekkaiToppaTask
    __all__ = ['KekkaiToppaTask']