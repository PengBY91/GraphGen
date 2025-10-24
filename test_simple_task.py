#!/usr/bin/env python3
"""
简化的任务管理功能测试
"""

import os
import sys
import tempfile
from importlib.resources import files

# 添加项目路径
root_dir = str(files("webui").parent)
sys.path.append(root_dir)

def test_basic_imports():
    """测试基本导入"""
    try:
        from webui.task_manager import task_manager, TaskStatus
        print("✅ 任务管理器导入成功")
        
        from webui.task_api import TaskAPI
        print("✅ 任务API导入成功")
        
        from webui.base import WebuiParams
        print("✅ 基础参数类导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_task_creation():
    """测试任务创建"""
    try:
        from webui.task_manager import task_manager, TaskStatus
        
        # 创建测试文件
        test_content = "这是一个测试文档。"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            test_file = f.name
        
        # 创建任务
        task_id = task_manager.create_task("test.txt", test_file)
        print(f"✅ 任务创建成功，ID: {task_id}")
        
        # 获取任务
        task = task_manager.get_task(task_id)
        if task:
            print(f"✅ 任务获取成功，状态: {task.status.value}")
        else:
            print("❌ 任务获取失败")
            return False
        
        # 更新任务状态
        task_manager.update_task_status(task_id, TaskStatus.PROCESSING)
        task = task_manager.get_task(task_id)
        print(f"✅ 任务状态更新成功，新状态: {task.status.value}")
        
        # 删除任务
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
        print(f"❌ 任务创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_functions():
    """测试API功能"""
    try:
        from webui.task_api import TaskAPI
        
        # 创建测试文件
        test_content = "API测试文档。"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            test_file = f.name
        
        # 创建API实例
        api = TaskAPI(root_dir)
        
        # 测试创建任务
        result = api.create_task("api_test.txt", test_file)
        if result.get("success"):
            task_id = result.get("task_id")
            print(f"✅ API任务创建成功，ID: {task_id}")
            
            # 测试获取任务
            result = api.get_task(task_id)
            if result.get("success"):
                print("✅ API任务获取成功")
            else:
                print("❌ API任务获取失败")
                return False
            
            # 测试删除任务
            result = api.delete_task(task_id)
            if result.get("success"):
                print("✅ API任务删除成功")
            else:
                print("❌ API任务删除失败")
                return False
        else:
            print("❌ API任务创建失败")
            return False
        
        # 清理测试文件
        if os.path.exists(test_file):
            os.unlink(test_file)
        
        return True
        
    except Exception as e:
        print(f"❌ API功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试任务管理功能...")
    print("=" * 50)
    
    # 测试基本导入
    print("1. 测试基本导入...")
    if not test_basic_imports():
        print("基本导入测试失败，退出")
        sys.exit(1)
    
    print("\n2. 测试任务创建...")
    if not test_task_creation():
        print("任务创建测试失败")
        sys.exit(1)
    
    print("\n3. 测试API功能...")
    if not test_api_functions():
        print("API功能测试失败")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ 所有测试通过！任务管理功能正常工作。")
