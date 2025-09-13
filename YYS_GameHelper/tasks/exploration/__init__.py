"""探索任务模块

自动化执行阴阳师探索任务。
"""

from .exploration import ExplorationTask, ExplorationLevel, UpType, DifficultyLevel, ExplorationScene
from .exploration import load_config, save_config, select_chapter, select_up_type, select_difficulty, configure_task

__all__ = [
    'ExplorationTask',
    'ExplorationLevel',
    'UpType',
    'DifficultyLevel',
    'ExplorationScene',
    'load_config',
    'save_config',
    'select_chapter',
    'select_up_type',
    'select_difficulty',
    'configure_task'
]

__version__ = '1.0.0'