# -*- coding: utf-8 -*-
"""
轻量级任务调度系统
解决任务间切换、优先级管理、资源清理等核心问题
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, field
from queue import PriorityQueue, Queue
import json

from .logger import logger


class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = 0    # 紧急任务（如资源清理）
    HIGH = 1        # 高优先级（如结界突破）
    NORMAL = 2      # 普通任务（如探索）
    LOW = 3         # 低优先级（如日常任务）


class TaskState(Enum):
    """任务状态"""
    PENDING = "pending"        # 等待执行
    RUNNING = "running"        # 正在执行
    PAUSED = "paused"          # 已暂停
    INTERRUPTED = "interrupted" # 被中断
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 执行失败
    CANCELLED = "cancelled"    # 已取消


@dataclass
class TaskContext:
    """任务上下文，保存任务执行状态"""
    task_id: str
    name: str
    priority: TaskPriority
    state: TaskState = TaskState.PENDING
    progress: float = 0.0  # 执行进度 0-1
    start_time: Optional[float] = None
    pause_time: Optional[float] = None
    resume_time: Optional[float] = None
    data: Dict[str, Any] = field(default_factory=dict)  # 任务数据
    checkpoints: List[Dict] = field(default_factory=list)  # 检查点
    
    def save_checkpoint(self, name: str, data: Dict[str, Any]):
        """保存检查点"""
        checkpoint = {
            "name": name,
            "timestamp": time.time(),
            "progress": self.progress,
            "data": data.copy()
        }
        self.checkpoints.append(checkpoint)
        logger.debug(f"任务 {self.task_id} 保存检查点: {name}")
    
    def get_latest_checkpoint(self) -> Optional[Dict]:
        """获取最新检查点"""
        return self.checkpoints[-1] if self.checkpoints else None


class InterruptibleTask:
    """可中断任务基类"""
    
    def __init__(self, task_id: str, name: str, priority: TaskPriority = TaskPriority.NORMAL):
        self.task_id = task_id
        self.name = name
        self.priority = priority
        self.context = TaskContext(task_id, name, priority)
        self._should_stop = threading.Event()
        self._should_pause = threading.Event()
        
    def execute(self, scheduler: 'TaskScheduler') -> Any:
        """执行任务（由调度器调用）"""
        self.context.state = TaskState.RUNNING
        self.context.start_time = time.time()
        
        try:
            result = self._run(scheduler)
            self.context.state = TaskState.COMPLETED
            self.context.progress = 1.0
            return result
        except InterruptedException:
            self.context.state = TaskState.INTERRUPTED
            logger.info(f"任务 {self.name} 被中断")
            return None
        except Exception as e:
            self.context.state = TaskState.FAILED
            logger.error(f"任务 {self.name} 执行失败: {e}")
            raise
    
    def _run(self, scheduler: 'TaskScheduler') -> Any:
        """具体任务实现（子类重写）"""
        raise NotImplementedError
    
    def request_stop(self):
        """请求停止任务"""
        self._should_stop.set()
    
    def request_pause(self):
        """请求暂停任务"""
        self._should_pause.set()
    
    def resume(self):
        """恢复任务"""
        self._should_pause.clear()
        self.context.resume_time = time.time()
        self.context.state = TaskState.RUNNING
    
    def check_interruption(self):
        """检查是否需要中断（任务内部调用）"""
        if self._should_stop.is_set():
            raise InterruptedException("任务被请求停止")
        
        if self._should_pause.is_set():
            self.context.state = TaskState.PAUSED
            self.context.pause_time = time.time()
            logger.info(f"任务 {self.name} 已暂停")
            
            # 等待恢复
            while self._should_pause.is_set() and not self._should_stop.is_set():
                time.sleep(0.1)
            
            if self._should_stop.is_set():
                raise InterruptedException("任务在暂停期间被停止")
            
            self.resume()
    
    def save_progress(self, progress: float, data: Dict[str, Any] = None):
        """保存进度"""
        self.context.progress = progress
        if data:
            self.context.data.update(data)


class InterruptedException(Exception):
    """任务中断异常"""
    pass


class TaskScheduler:
    """轻量级任务调度器"""
    
    def __init__(self):
        self.task_queue = PriorityQueue()
        self.running_tasks: Dict[str, InterruptibleTask] = {}
        self.task_contexts: Dict[str, TaskContext] = {}
        self.interrupt_handlers: Dict[str, Callable] = {}
        self._running = False
        self._scheduler_thread = None
        self._lock = threading.RLock()
        
        # 资源清理触发器
        self.resource_triggers: List[Callable[[], bool]] = []
        self.cleanup_tasks: List[str] = []
    
    def start(self):
        """启动调度器"""
        if self._running:
            return
        
        self._running = True
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        logger.info("任务调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        logger.info("任务调度器已停止")
    
    def submit_task(self, task: InterruptibleTask, delay: float = 0):
        """提交任务"""
        with self._lock:
            # 计算执行时间（优先级 + 延迟）
            execute_time = time.time() + delay
            priority_value = (task.priority.value, execute_time)
            
            self.task_queue.put((priority_value, task))
            self.task_contexts[task.task_id] = task.context
            
            logger.info(f"提交任务: {task.name} (优先级: {task.priority.name})")
    
    def interrupt_task(self, task_id: str, new_task: InterruptibleTask = None):
        """中断指定任务"""
        with self._lock:
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                task.request_stop()
                logger.info(f"中断任务: {task.name}")
                
                # 如果有新任务，立即提交
                if new_task:
                    self.submit_task(new_task)
    
    def pause_task(self, task_id: str):
        """暂停任务"""
        with self._lock:
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                task.request_pause()
                logger.info(f"暂停任务: {task.name}")
    
    def resume_task(self, task_id: str):
        """恢复任务"""
        with self._lock:
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                task.resume()
                logger.info(f"恢复任务: {task.name}")
    
    def add_resource_trigger(self, trigger: Callable[[], bool], cleanup_task_id: str):
        """添加资源清理触发器"""
        self.resource_triggers.append(trigger)
        if cleanup_task_id not in self.cleanup_tasks:
            self.cleanup_tasks.append(cleanup_task_id)
    
    def check_resource_triggers(self) -> Optional[str]:
        """检查是否需要资源清理"""
        for i, trigger in enumerate(self.resource_triggers):
            try:
                if trigger():
                    cleanup_task_id = self.cleanup_tasks[i] if i < len(self.cleanup_tasks) else None
                    logger.info(f"触发资源清理: {cleanup_task_id}")
                    return cleanup_task_id
            except Exception as e:
                logger.error(f"资源触发器检查失败: {e}")
        return None
    
    def get_task_status(self, task_id: str) -> Optional[TaskContext]:
        """获取任务状态"""
        return self.task_contexts.get(task_id)
    
    def _scheduler_loop(self):
        """调度器主循环"""
        while self._running:
            try:
                # 检查资源清理触发器
                cleanup_task_id = self.check_resource_triggers()
                if cleanup_task_id:
                    # 暂停当前所有任务，执行清理
                    self._pause_all_tasks()
                    # 这里可以提交清理任务
                
                # 获取下一个任务
                if not self.task_queue.empty():
                    try:
                        priority_info, task = self.task_queue.get(timeout=1)
                        self._execute_task(task)
                    except:
                        pass  # 队列为空或超时
                else:
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"调度器循环异常: {e}")
                time.sleep(1)
    
    def _execute_task(self, task: InterruptibleTask):
        """执行任务"""
        with self._lock:
            self.running_tasks[task.task_id] = task
        
        try:
            logger.info(f"开始执行任务: {task.name}")
            result = task.execute(self)
            logger.info(f"任务完成: {task.name}")
        except Exception as e:
            logger.error(f"任务执行异常: {task.name} - {e}")
        finally:
            with self._lock:
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]
    
    def _pause_all_tasks(self):
        """暂停所有运行中的任务"""
        with self._lock:
            for task in self.running_tasks.values():
                task.request_pause()


# 全局调度器实例
scheduler = TaskScheduler()