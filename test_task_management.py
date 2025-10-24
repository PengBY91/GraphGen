#!/usr/bin/env python3
"""
测试任务管理功能
"""

import os
import sys
import tempfile
from importlib.resources import files

# 添加项目路径
root_dir = str(files("webui").parent)
sys.path.append(root_dir)

from webui.task_manager import task_manager, TaskStatus
from webui.task_api import TaskAPI
from webui.base import WebuiParams


def test_task_management():
    """测试任务管理功能"""
    print("开始测试任务管理功能...")
    
    # 创建测试文件
    test_content = "这是一个测试文档。它包含一些文本内容用于测试GraphGen功能。"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        test_file = f.name
    
    try:
        # 测试创建任务
        print("1. 测试创建任务...")
        task_id = task_manager.create_task("test.txt", test_file)
        print(f"   任务ID: {task_id}")
        
        # 测试获取任务
        print("2. 测试获取任务...")
        task = task_manager.get_task(task_id)
        print(f"   任务状态: {task.status.value}")
        print(f"   文件名: {task.filename}")
        
        # 测试更新任务状态
        print("3. 测试更新任务状态...")
        task_manager.update_task_status(task_id, TaskStatus.PROCESSING)
        task = task_manager.get_task(task_id)
        print(f"   更新后状态: {task.status.value}")
        
        # 测试获取所有任务
        print("4. 测试获取所有任务...")
        all_tasks = task_manager.get_all_tasks()
        print(f"   任务总数: {len(all_tasks)}")
        
        # 测试任务状态统计
        print("5. 测试任务状态统计...")
        summary = {}
        for task in all_tasks:
            status = task.status.value
            summary[status] = summary.get(status, 0) + 1
        print(f"   状态统计: {summary}")
        
        # 测试删除任务
        print("6. 测试删除任务...")
        success = task_manager.delete_task(task_id)
        print(f"   删除结果: {success}")
        
        # 验证任务已删除
        task = task_manager.get_task(task_id)
        print(f"   删除后任务: {task}")
        
        print("✅ 任务管理功能测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_task_api():
    """测试任务API"""
    print("\n开始测试任务API...")
    
    # 创建测试文件
    test_content = "这是一个API测试文档。"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        test_file = f.name
    
    try:
        # 创建API实例
        api = TaskAPI(root_dir)
        
        # 测试创建任务
        print("1. 测试API创建任务...")
        result = api.create_task("api_test.txt", test_file)
        print(f"   创建结果: {result}")
        
        if result.get("success"):
            task_id = result.get("task_id")
            
            # 测试获取任务
            print("2. 测试API获取任务...")
            result = api.get_task(task_id)
            print(f"   获取结果: {result}")
            
            # 测试获取所有任务
            print("3. 测试API获取所有任务...")
            result = api.get_all_tasks()
            print(f"   所有任务: {len(result.get('tasks', []))}")
            
            # 测试删除任务
            print("4. 测试API删除任务...")
            result = api.delete_task(task_id)
            print(f"   删除结果: {result}")
        
        print("✅ 任务API测试完成！")
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.unlink(test_file)


if __name__ == "__main__":
    test_task_management()
    test_task_api()
