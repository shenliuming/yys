"""
任务模块 - 基础任务框架
"""
import time
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List, Tuple, Callable

from .logger import logger
from .config import config

class Task(ABC):
    """任务基类，所有任务都应继承此类"""
    
    def __init__(self, name: str):
        """
        初始化任务
        
        Args:
            name: 任务名称
        """
        self.name = name
        self.running = False
        self.paused = False
        self.stopped = False
        self.result = None
        self.start_time = 0
        self.end_time = 0
        self.elapsed_time = 0
        self.retry_count = 0
        self.max_retries = 3
        self.retry_interval = 1.0
        self.timeout = 60.0  # 默认超时时间（秒）
        
        # 设备实例
        self.device = None
        
        # 子任务列表
        self.subtasks = []
        
        # 任务配置
        self.config = {}
        
        # 任务状态
        self.status = "initialized"
    
    def start(self) -> Any:
        """
        启动任务
        
        Returns:
            Any: 任务结果
        """
        if self.running:
            logger.warning(f"任务 [{self.name}] 已在运行中")
            return None
        
        # 重置状态
        self.running = True
        self.paused = False
        self.stopped = False
        self.result = None
        self.start_time = time.time()
        self.retry_count = 0
        
        # 记录任务开始
        logger.section(f"开始任务: {self.name}")
        
        try:
            # 执行任务
            self.status = "running"
            self.result = self._run()
            self.status = "completed"
            
            # 记录任务完成
            self.end_time = time.time()
            self.elapsed_time = self.end_time - self.start_time
            logger.task(self.name, f"完成 (耗时: {self.elapsed_time:.2f}秒)")
            
        except Exception as e:
            # 记录任务异常
            self.status = "failed"
            self.end_time = time.time()
            self.elapsed_time = self.end_time - self.start_time
            logger.error(f"任务 [{self.name}] 执行异常: {e}")
            
        finally:
            # 重置状态
            self.running = False
            
            # 返回结果
            return self.result
    
    def stop(self) -> None:
        """停止任务"""
        if not self.running:
            return
        
        logger.info(f"停止任务: {self.name}")
        self.stopped = True
        self.status = "stopped"
    
    def set_device(self, device) -> None:
        """设置设备实例"""
        self.device = device
    
    def is_running(self) -> bool:
        """检查任务是否正在运行"""
        return self.running
    
    def pause(self) -> None:
        """暂停任务"""
        if not self.running or self.paused:
            return
        
        logger.info(f"暂停任务: {self.name}")
        self.paused = True
        self.status = "paused"
    
    def resume(self) -> None:
        """恢复任务"""
        if not self.running or not self.paused:
            return
        
        logger.info(f"恢复任务: {self.name}")
        self.paused = False
        self.status = "running"
    
    def retry(self) -> Any:
        """
        重试任务
        
        Returns:
            Any: 任务结果
        """
        if self.retry_count >= self.max_retries:
            logger.warning(f"任务 [{self.name}] 已达到最大重试次数: {self.max_retries}")
            return None
        
        self.retry_count += 1
        logger.info(f"重试任务 [{self.name}] (第 {self.retry_count} 次)")
        
        # 等待重试间隔
        time.sleep(self.retry_interval)
        
        # 重新启动任务
        return self.start()
    
    def wait_until(self, condition: Callable[[], bool], timeout: float = None, interval: float = 0.5) -> bool:
        """
        等待直到条件满足或超时
        
        Args:
            condition: 条件函数，返回True表示条件满足
            timeout: 超时时间（秒），如果为None则使用任务默认超时时间
            interval: 检查间隔（秒）
            
        Returns:
            bool: 是否在超时前满足条件
        """
        if timeout is None:
            timeout = self.timeout
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 检查任务是否被停止
            if self.stopped:
                return False
            
            # 检查任务是否被暂停
            if self.paused:
                time.sleep(interval)
                continue
            
            # 检查条件是否满足
            if condition():
                return True
            
            # 等待检查间隔
            time.sleep(interval)
        
        # 超时
        logger.warning(f"任务 [{self.name}] 等待条件超时: {timeout}秒")
        return False
    
    def sleep(self, seconds: float) -> None:
        """
        等待指定时间
        
        Args:
            seconds: 等待时间（秒）
        """
        start_time = time.time()
        
        while time.time() - start_time < seconds:
            # 检查任务是否被停止
            if self.stopped:
                return
            
            # 检查任务是否被暂停
            if self.paused:
                time.sleep(0.1)
                continue
            
            # 等待
            time.sleep(0.1)
    
    def random_sleep(self, min_seconds: float, max_seconds: float) -> None:
        """
        随机等待时间
        
        Args:
            min_seconds: 最小等待时间（秒）
            max_seconds: 最大等待时间（秒）
        """
        seconds = random.uniform(min_seconds, max_seconds)
        self.sleep(seconds)
    
    def add_subtask(self, task: 'Task') -> None:
        """
        添加子任务
        
        Args:
            task: 子任务
        """
        self.subtasks.append(task)
    
    def run_subtasks(self) -> List[Any]:
        """
        运行所有子任务
        
        Returns:
            List[Any]: 子任务结果列表
        """
        results = []
        
        for task in self.subtasks:
            # 检查任务是否被停止
            if self.stopped:
                break
            
            # 运行子任务
            result = task.start()
            results.append(result)
            
            # 如果子任务失败，停止执行后续子任务
            if task.status == "failed":
                logger.warning(f"子任务 [{task.name}] 失败，停止执行后续子任务")
                break
        
        return results
    
    @abstractmethod
    def _run(self) -> Any:
        """
        任务执行逻辑，子类必须实现此方法
        
        Returns:
            Any: 任务结果
        """
        pass

class TaskManager:
    """任务管理器，负责管理和调度任务"""
    
    def __init__(self):
        """初始化任务管理器"""
        self.tasks = {}  # 任务字典，键为任务名称，值为任务对象
        self.current_task = None  # 当前正在执行的任务
    
    def register_task(self, task: Task) -> None:
        """
        注册任务
        
        Args:
            task: 任务对象
        """
        self.tasks[task.name] = task
        logger.info(f"注册任务: {task.name}")
    
    def unregister_task(self, task_name: str) -> None:
        """
        注销任务
        
        Args:
            task_name: 任务名称
        """
        if task_name in self.tasks:
            del self.tasks[task_name]
            logger.info(f"注销任务: {task_name}")
    
    def get_task(self, task_name: str) -> Optional[Task]:
        """
        获取任务
        
        Args:
            task_name: 任务名称
            
        Returns:
            Optional[Task]: 任务对象，如果不存在则返回None
        """
        return self.tasks.get(task_name)
    
    def run_task(self, task_name: str) -> Any:
        """
        运行任务
        
        Args:
            task_name: 任务名称
            
        Returns:
            Any: 任务结果
        """
        task = self.get_task(task_name)
        
        if task is None:
            logger.error(f"任务不存在: {task_name}")
            return None
        
        # 停止当前任务
        if self.current_task is not None and self.current_task.running:
            self.current_task.stop()
        
        # 设置当前任务
        self.current_task = task
        
        # 运行任务
        return task.start()
    
    def stop_current_task(self) -> None:
        """停止当前任务"""
        if self.current_task is not None and self.current_task.running:
            self.current_task.stop()
    
    def pause_current_task(self) -> None:
        """暂停当前任务"""
        if self.current_task is not None and self.current_task.running:
            self.current_task.pause()
    
    def resume_current_task(self) -> None:
        """恢复当前任务"""
        if self.current_task is not None and self.current_task.running:
            self.current_task.resume()
    
    def get_task_status(self, task_name: str) -> Optional[str]:
        """
        获取任务状态
        
        Args:
            task_name: 任务名称
            
        Returns:
            Optional[str]: 任务状态，如果任务不存在则返回None
        """
        task = self.get_task(task_name)
        
        if task is None:
            return None
        
        return task.status
    
    def get_all_tasks(self) -> Dict[str, Task]:
        """
        获取所有任务
        
        Returns:
            Dict[str, Task]: 任务字典
        """
        return self.tasks.copy()
    
    def get_running_tasks(self) -> Dict[str, Task]:
        """
        获取正在运行的任务
        
        Returns:
            Dict[str, Task]: 任务字典
        """
        return {name: task for name, task in self.tasks.items() if task.running}

# 创建全局任务管理器
task_manager = TaskManager()

# 示例任务类
class ExampleTask(Task):
    """示例任务类"""
    
    def __init__(self, name: str = "示例任务"):
        """
        初始化示例任务
        
        Args:
            name: 任务名称
        """
        super().__init__(name)
    
    def _run(self) -> bool:
        """
        任务执行逻辑
        
        Returns:
            bool: 是否成功
        """
        logger.info(f"执行任务: {self.name}")
        
        # 模拟任务执行
        for i in range(5):
            # 检查任务是否被停止
            if self.stopped:
                logger.info(f"任务 [{self.name}] 被停止")
                return False
            
            # 检查任务是否被暂停
            if self.paused:
                logger.info(f"任务 [{self.name}] 被暂停")
                while self.paused and not self.stopped:
                    time.sleep(0.5)
                
                if self.stopped:
                    logger.info(f"任务 [{self.name}] 被停止")
                    return False
                
                logger.info(f"任务 [{self.name}] 恢复执行")
            
            # 执行任务步骤
            logger.info(f"任务 [{self.name}] 步骤 {i+1}/5")
            self.sleep(1)
        
        logger.info(f"任务 [{self.name}] 执行完成")
        return True

if __name__ == "__main__":
    # 测试任务功能
    example_task = ExampleTask()
    task_manager.register_task(example_task)
    
    # 运行任务
    result = task_manager.run_task("示例任务")
    print(f"任务结果: {result}")
    
    # 获取任务状态
    status = task_manager.get_task_status("示例任务")
    print(f"任务状态: {status}")