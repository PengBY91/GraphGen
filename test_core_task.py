#!/usr/bin/env python3
"""
核心任务管理功能测试（不依赖gradio）
"""

import os
import sys
import tempfile
from importlib.resources import files

# 添加项目路径
root_dir = str(files("webui").parent)
sys.path.append(root_dir)

def test_task_manager_only():
    """只测试任务管理器核心功能"""
    try:
        from webui.task_manager import task_manager, TaskStatus
        
        print("✅ 任务管理器导入成功")
        
        # 创建测试文件
        test_content = "这是一个测试文档。"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            test_file = f.name
        
        # 测试任务创建
        task_id = task_manager.create_task("test.txt", test_file)
        print(f"✅ 任务创建成功，ID: {task_id}")
        
        # 测试任务获取
        task = task_manager.get_task(task_id)
        if task:
            print(f"✅ 任务获取成功，状态: {task.status.value}")
        else:
            print("❌ 任务获取失败")
            return False
        
        # 测试状态更新
        task_manager.update_task_status(task_id, TaskStatus.PROCESSING)
        task = task_manager.get_task(task_id)
        print(f"✅ 状态更新成功，新状态: {task.status.value}")
        
        # 测试获取所有任务
        all_tasks = task_manager.get_all_tasks()
        print(f"✅ 获取所有任务成功，共 {len(all_tasks)} 个任务")
        
        # 测试任务删除
        success = task_manager.delete_task(task_id)
        if success:
            print("✅ 任务删除成功")
        else:
            print("❌ 任务删除失败")
            return False
        
        # 清理测试文件
        if os.path.exists(test_file):
            os.unlink(test_file)
        
        return True
        
    except Exception as e:
        print(f"❌ 任务管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_task_data_structures():
    """测试任务数据结构"""
    try:
        from webui.task_manager import TaskInfo, TaskStatus
        from datetime import datetime
        
        # 创建任务信息
        task = TaskInfo(
            task_id="test-123",
            filename="test.txt",
            file_path="/tmp/test.txt",
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )
        
        print("✅ 任务信息对象创建成功")
        
        # 测试转换为字典
        task_dict = task.to_dict()
        print(f"✅ 任务信息转换为字典成功: {task_dict}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试核心任务管理功能...")
    print("=" * 50)
    
    # 测试数据结构
    print("1. 测试任务数据结构...")
    if not test_task_data_structures():
        print("数据结构测试失败，退出")
        sys.exit(1)
    
    # 测试任务管理器
    print("\n2. 测试任务管理器...")
    if not test_task_manager_only():
        print("任务管理器测试失败")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ 核心任务管理功能测试通过！")
