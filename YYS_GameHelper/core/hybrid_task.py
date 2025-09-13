# -*- coding: utf-8 -*-
"""
混合事件驱动和状态机任务系统
解决复杂页面交互和状态管理问题
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Any, Tuple
from enum import Enum, auto
from dataclasses import dataclass
from collections import defaultdict

from .scheduler import InterruptibleTask, TaskPriority
from .simple_config import TaskConfig
from .logger import logger


class PageState(Enum):
    """页面状态枚举"""
    UNKNOWN = auto()
    MAIN_MENU = auto()
    KEKKAI_TOPPA = auto()
    KEKKAI_SELECTION = auto()
    BATTLE = auto()
    BATTLE_RESULT = auto()
    INVENTORY_FULL = auto()
    ERROR = auto()


class TaskEvent(Enum):
    """任务事件枚举"""
    PAGE_CHANGED = auto()
    BATTLE_STARTED = auto()
    BATTLE_ENDED = auto()
    INVENTORY_FULL = auto()
    RESOURCE_LOW = auto()
    ERROR_OCCURRED = auto()
    USER_INTERRUPT = auto()
    TIMEOUT = auto()


@dataclass
class EventData:
    """事件数据"""
    event_type: TaskEvent
    timestamp: float
    data: Dict[str, Any]
    source: str = "system"


class StateMachine:
    """状态机"""
    
    def __init__(self, initial_state: PageState):
        self.current_state = initial_state
        self.previous_state = None
        self.transitions: Dict[Tuple[PageState, TaskEvent], PageState] = {}
        self.state_handlers: Dict[PageState, Callable] = {}
        self.transition_handlers: Dict[Tuple[PageState, PageState], Callable] = {}
        self._lock = threading.RLock()
    
    def add_transition(self, from_state: PageState, event: TaskEvent, to_state: PageState):
        """添加状态转换"""
        self.transitions[(from_state, event)] = to_state
    
    def add_state_handler(self, state: PageState, handler: Callable):
        """添加状态处理器"""
        self.state_handlers[state] = handler
    
    def add_transition_handler(self, from_state: PageState, to_state: PageState, handler: Callable):
        """添加状态转换处理器"""
        self.transition_handlers[(from_state, to_state)] = handler
    
    def handle_event(self, event: TaskEvent, event_data: EventData = None) -> bool:
        """处理事件"""
        with self._lock:
            transition_key = (self.current_state, event)
            
            if transition_key not in self.transitions:
                logger.debug(f"无效状态转换: {self.current_state} -> {event}")
                return False
            
            new_state = self.transitions[transition_key]
            old_state = self.current_state
            
            # 执行状态转换处理器
            transition_handler = self.transition_handlers.get((old_state, new_state))
            if transition_handler:
                try:
                    transition_handler(old_state, new_state, event_data)
                except Exception as e:
                    logger.error(f"状态转换处理器异常: {e}")
                    return False
            
            # 更新状态
            self.previous_state = old_state
            self.current_state = new_state
            
            logger.debug(f"状态转换: {old_state} -> {new_state} (事件: {event})")
            
            # 执行新状态处理器
            state_handler = self.state_handlers.get(new_state)
            if state_handler:
                try:
                    state_handler(new_state, event_data)
                except Exception as e:
                    logger.error(f"状态处理器异常: {e}")
            
            return True
    
    def get_current_state(self) -> PageState:
        """获取当前状态"""
        return self.current_state
    
    def can_transition(self, event: TaskEvent) -> bool:
        """检查是否可以进行状态转换"""
        return (self.current_state, event) in self.transitions


class EventBus:
    """事件总线"""
    
    def __init__(self):
        self.listeners: Dict[TaskEvent, List[Callable]] = defaultdict(list)
        self.event_queue: List[EventData] = []
        self._lock = threading.RLock()
    
    def subscribe(self, event_type: TaskEvent, listener: Callable):
        """订阅事件"""
        with self._lock:
            self.listeners[event_type].append(listener)
    
    def unsubscribe(self, event_type: TaskEvent, listener: Callable):
        """取消订阅"""
        with self._lock:
            if listener in self.listeners[event_type]:
                self.listeners[event_type].remove(listener)
    
    def publish(self, event_data: EventData):
        """发布事件"""
        with self._lock:
            self.event_queue.append(event_data)
            
            # 立即通知监听器
            for listener in self.listeners[event_data.event_type]:
                try:
                    listener(event_data)
                except Exception as e:
                    logger.error(f"事件监听器异常: {e}")
    
    def process_events(self) -> List[EventData]:
        """处理事件队列"""
        with self._lock:
            events = self.event_queue.copy()
            self.event_queue.clear()
            return events


class HybridTask(InterruptibleTask):
    """混合事件驱动和状态机的任务"""
    
    def __init__(self, task_id: str, name: str, config: TaskConfig, 
                 priority: TaskPriority = TaskPriority.NORMAL):
        super().__init__(task_id, name, priority)
        self.config = config
        self.state_machine = StateMachine(PageState.UNKNOWN)
        self.event_bus = EventBus()
        self.device = None
        
        # 页面检测器
        self.page_detectors: Dict[PageState, Callable[[], bool]] = {}
        
        # 初始化状态机和事件处理
        self._setup_state_machine()
        self._setup_event_handlers()
    
    def set_device(self, device):
        """设置设备"""
        self.device = device
    
    def _setup_state_machine(self):
        """设置状态机（子类重写）"""
        pass
    
    def _setup_event_handlers(self):
        """设置事件处理器（子类重写）"""
        pass
    
    def add_page_detector(self, page_state: PageState, detector: Callable[[], bool]):
        """添加页面检测器"""
        self.page_detectors[page_state] = detector
    
    def detect_current_page(self) -> PageState:
        """检测当前页面状态"""
        for page_state, detector in self.page_detectors.items():
            try:
                if detector():
                    return page_state
            except Exception as e:
                logger.error(f"页面检测器异常: {page_state} - {e}")
        
        return PageState.UNKNOWN
    
    def publish_event(self, event_type: TaskEvent, data: Dict[str, Any] = None):
        """发布事件"""
        event_data = EventData(
            event_type=event_type,
            timestamp=time.time(),
            data=data or {},
            source=self.task_id
        )
        self.event_bus.publish(event_data)
    
    def _run(self, scheduler) -> Any:
        """执行任务主循环"""
        logger.info(f"开始执行混合任务: {self.name}")
        
        # 初始化
        self._initialize()
        
        # 主循环
        while not self._should_stop.is_set():
            try:
                # 检查中断
                self.check_interruption()
                
                # 检测页面状态
                current_page = self.detect_current_page()
                if current_page != self.state_machine.current_state:
                    self.publish_event(TaskEvent.PAGE_CHANGED, {"page": current_page})
                    self.state_machine.handle_event(TaskEvent.PAGE_CHANGED, 
                                                   EventData(TaskEvent.PAGE_CHANGED, time.time(), {"page": current_page}))
                
                # 处理事件队列
                events = self.event_bus.process_events()
                for event in events:
                    self.state_machine.handle_event(event.event_type, event)
                
                # 执行当前状态的逻辑
                self._execute_state_logic()
                
                # 检查完成条件
                if self._check_completion():
                    break
                
                time.sleep(0.1)  # 避免CPU占用过高
                
            except Exception as e:
                logger.error(f"任务执行异常: {e}")
                self.publish_event(TaskEvent.ERROR_OCCURRED, {"error": str(e)})
                break
        
        # 清理
        self._cleanup()
        
        return self._get_result()
    
    def _initialize(self):
        """初始化（子类重写）"""
        pass
    
    def _execute_state_logic(self):
        """执行当前状态逻辑（子类重写）"""
        pass
    
    def _check_completion(self) -> bool:
        """检查完成条件（子类重写）"""
        return False
    
    def _cleanup(self):
        """清理（子类重写）"""
        pass
    
    def _get_result(self) -> Any:
        """获取结果（子类重写）"""
        return None


class KekkaiToppaHybridTask(HybridTask):
    """结界突破混合任务示例"""
    
    def __init__(self, task_id: str, config: TaskConfig):
        super().__init__(task_id, "结界突破-混合", config)
        self.battle_count = 0
        self.max_battles = config.limit_count if hasattr(config, 'limit_count') else 10
        self.start_time = None
        self.max_duration = config.limit_time_minutes * 60 if hasattr(config, 'limit_time_minutes') else 3600
    
    def _setup_state_machine(self):
        """设置状态机"""
        # 定义状态转换
        transitions = [
            (PageState.UNKNOWN, TaskEvent.PAGE_CHANGED, PageState.MAIN_MENU),
            (PageState.MAIN_MENU, TaskEvent.PAGE_CHANGED, PageState.KEKKAI_TOPPA),
            (PageState.KEKKAI_TOPPA, TaskEvent.PAGE_CHANGED, PageState.KEKKAI_SELECTION),
            (PageState.KEKKAI_SELECTION, TaskEvent.BATTLE_STARTED, PageState.BATTLE),
            (PageState.BATTLE, TaskEvent.BATTLE_ENDED, PageState.BATTLE_RESULT),
            (PageState.BATTLE_RESULT, TaskEvent.PAGE_CHANGED, PageState.KEKKAI_SELECTION),
            (PageState.KEKKAI_SELECTION, TaskEvent.INVENTORY_FULL, PageState.INVENTORY_FULL),
            (PageState.INVENTORY_FULL, TaskEvent.PAGE_CHANGED, PageState.KEKKAI_SELECTION),
        ]
        
        for from_state, event, to_state in transitions:
            self.state_machine.add_transition(from_state, event, to_state)
        
        # 添加状态处理器
        self.state_machine.add_state_handler(PageState.MAIN_MENU, self._handle_main_menu)
        self.state_machine.add_state_handler(PageState.KEKKAI_TOPPA, self._handle_kekkai_toppa)
        self.state_machine.add_state_handler(PageState.KEKKAI_SELECTION, self._handle_kekkai_selection)
        self.state_machine.add_state_handler(PageState.BATTLE, self._handle_battle)
        self.state_machine.add_state_handler(PageState.BATTLE_RESULT, self._handle_battle_result)
        self.state_machine.add_state_handler(PageState.INVENTORY_FULL, self._handle_inventory_full)
    
    def _setup_event_handlers(self):
        """设置事件处理器"""
        self.event_bus.subscribe(TaskEvent.BATTLE_ENDED, self._on_battle_ended)
        self.event_bus.subscribe(TaskEvent.INVENTORY_FULL, self._on_inventory_full)
    
    def _initialize(self):
        """初始化"""
        self.start_time = time.time()
        self.battle_count = 0
        
        # 添加页面检测器（这里是示例，实际需要根据具体实现）
        self.add_page_detector(PageState.MAIN_MENU, lambda: self._is_main_menu())
        self.add_page_detector(PageState.KEKKAI_TOPPA, lambda: self._is_kekkai_toppa())
        self.add_page_detector(PageState.KEKKAI_SELECTION, lambda: self._is_kekkai_selection())
        self.add_page_detector(PageState.BATTLE, lambda: self._is_battle())
        self.add_page_detector(PageState.BATTLE_RESULT, lambda: self._is_battle_result())
        self.add_page_detector(PageState.INVENTORY_FULL, lambda: self._is_inventory_full())
    
    def _check_completion(self) -> bool:
        """检查完成条件"""
        # 检查次数限制
        if self.battle_count >= self.max_battles:
            logger.info(f"达到最大战斗次数: {self.max_battles}")
            return True
        
        # 检查时间限制
        if self.start_time and time.time() - self.start_time >= self.max_duration:
            logger.info(f"达到最大执行时间: {self.max_duration}秒")
            return True
        
        return False
    
    # 状态处理器
    def _handle_main_menu(self, state: PageState, event_data: EventData):
        """处理主菜单状态"""
        logger.info("在主菜单，导航到结界突破")
        # 这里实现导航逻辑
        time.sleep(1)  # 模拟操作
    
    def _handle_kekkai_toppa(self, state: PageState, event_data: EventData):
        """处理结界突破页面"""
        logger.info("在结界突破页面，进入选择界面")
        time.sleep(1)
    
    def _handle_kekkai_selection(self, state: PageState, event_data: EventData):
        """处理结界选择页面"""
        logger.info("在结界选择页面，开始战斗")
        self.publish_event(TaskEvent.BATTLE_STARTED)
        time.sleep(1)
    
    def _handle_battle(self, state: PageState, event_data: EventData):
        """处理战斗状态"""
        logger.info("战斗中...")
        time.sleep(3)  # 模拟战斗时间
        self.publish_event(TaskEvent.BATTLE_ENDED)
    
    def _handle_battle_result(self, state: PageState, event_data: EventData):
        """处理战斗结果"""
        logger.info("处理战斗结果")
        self.battle_count += 1
        self.save_progress(self.battle_count / self.max_battles)
        time.sleep(1)
    
    def _handle_inventory_full(self, state: PageState, event_data: EventData):
        """处理背包满状态"""
        logger.info("背包已满，需要清理")
        # 这里可以触发资源清理任务
        time.sleep(2)
    
    # 事件处理器
    def _on_battle_ended(self, event_data: EventData):
        """战斗结束事件处理"""
        logger.info(f"战斗结束，当前次数: {self.battle_count + 1}")
    
    def _on_inventory_full(self, event_data: EventData):
        """背包满事件处理"""
        logger.warning("检测到背包已满")
    
    # 页面检测器（示例实现）
    def _is_main_menu(self) -> bool:
        """检测是否在主菜单"""
        # 实际实现需要根据截图和图像识别
        return False
    
    def _is_kekkai_toppa(self) -> bool:
        """检测是否在结界突破页面"""
        return False
    
    def _is_kekkai_selection(self) -> bool:
        """检测是否在结界选择页面"""
        return False
    
    def _is_battle(self) -> bool:
        """检测是否在战斗中"""
        return False
    
    def _is_battle_result(self) -> bool:
        """检测是否在战斗结果页面"""
        return False
    
    def _is_inventory_full(self) -> bool:
        """检测背包是否已满"""
        return False
    
    def _get_result(self) -> Dict[str, Any]:
        """获取任务结果"""
        return {
            "battle_count": self.battle_count,
            "duration": time.time() - self.start_time if self.start_time else 0,
            "success": True
        }