"""
任务管理模块
提供任务创建、状态跟踪、结果管理等功能
"""

import json
import os
import threading
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import shutil


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 未开始
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"        # 失败


@dataclass
class TaskInfo:
    """任务信息数据类"""
    task_id: str
    filename: str
    file_path: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_file: Optional[str] = None
    token_usage: Optional[Dict[str, int]] = None
    processing_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data


class TaskManager:
    """任务管理器"""
    
    def __init__(self, tasks_dir: str = "tasks"):
        self.tasks_dir = tasks_dir
        self.tasks: Dict[str, TaskInfo] = {}
        self.lock = threading.Lock()
        
        # 确保任务目录存在
        os.makedirs(self.tasks_dir, exist_ok=True)
        os.makedirs(os.path.join(self.tasks_dir, "outputs"), exist_ok=True)
        
        # 加载已存在的任务
        self._load_tasks()
    
    def _load_tasks(self):
        """从磁盘加载任务信息"""
        tasks_file = os.path.join(self.tasks_dir, "tasks.json")
        if os.path.exists(tasks_file):
            try:
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_data in data.get('tasks', []):
                        task = TaskInfo(
                            task_id=task_data['task_id'],
                            filename=task_data['filename'],
                            file_path=task_data['file_path'],
                            status=TaskStatus(task_data['status']),
                            created_at=datetime.fromisoformat(task_data['created_at']),
                            started_at=datetime.fromisoformat(task_data['started_at']) if task_data.get('started_at') else None,
                            completed_at=datetime.fromisoformat(task_data['completed_at']) if task_data.get('completed_at') else None,
                            error_message=task_data.get('error_message'),
                            output_file=task_data.get('output_file'),
                            token_usage=task_data.get('token_usage'),
                            processing_time=task_data.get('processing_time')
                        )
                        self.tasks[task.task_id] = task
            except Exception as e:
                print(f"加载任务信息失败: {e}")
    
    def _save_tasks(self):
        """保存任务信息到磁盘"""
        tasks_file = os.path.join(self.tasks_dir, "tasks.json")
        try:
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'tasks': [task.to_dict() for task in self.tasks.values()]
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务信息失败: {e}")
    
    def create_task(self, filename: str, file_path: str) -> str:
        """创建新任务"""
        with self.lock:
            task_id = str(uuid.uuid4())
            task = TaskInfo(
                task_id=task_id,
                filename=filename,
                file_path=file_path,
                status=TaskStatus.PENDING,
                created_at=datetime.now()
            )
            self.tasks[task_id] = task
            self._save_tasks()
            return task_id
    
    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """获取任务信息"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[TaskInfo]:
        """获取所有任务"""
        return list(self.tasks.values())
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                          error_message: Optional[str] = None,
                          output_file: Optional[str] = None,
                          token_usage: Optional[Dict[str, int]] = None):
        """更新任务状态"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = status
                
                if status == TaskStatus.PROCESSING:
                    task.started_at = datetime.now()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    task.completed_at = datetime.now()
                    if task.started_at:
                        task.processing_time = (task.completed_at - task.started_at).total_seconds()
                
                if error_message:
                    task.error_message = error_message
                if output_file:
                    task.output_file = output_file
                if token_usage:
                    task.token_usage = token_usage
                
                self._save_tasks()
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                
                # 删除输出文件
                if task.output_file and os.path.exists(task.output_file):
                    try:
                        os.remove(task.output_file)
                    except Exception as e:
                        print(f"删除输出文件失败: {e}")
                
                # 删除任务记录
                del self.tasks[task_id]
                self._save_tasks()
                return True
            return False
    
    def get_task_output_path(self, task_id: str) -> str:
        """获取任务输出文件路径"""
        return os.path.join(self.tasks_dir, "outputs", f"{task_id}_output.jsonl")
    
    def cleanup_old_tasks(self, days: int = 7):
        """清理旧任务（超过指定天数的已完成任务）"""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        with self.lock:
            tasks_to_remove = []
            for task_id, task in self.tasks.items():
                if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and 
                    task.created_at.timestamp() < cutoff_time):
                    tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                self.delete_task(task_id)


# 全局任务管理器实例
task_manager = TaskManager()
