"""
测试 State Manager
"""

import pytest
from harness.state_manager import StateManager
from harness.models import Task, Evaluation


def test_save_and_load_task(temp_harness_dir):
    """测试保存和加载任务"""
    manager = StateManager(str(temp_harness_dir))
    manager.init()
    
    task = Task(id="task_123", description="测试任务")
    manager.save_task(task)
    
    # 加载任务
    loaded_task = manager.load_task()
    
    assert loaded_task is not None
    assert loaded_task.id == task.id
    assert loaded_task.description == task.description


def test_update_progress(temp_harness_dir):
    """测试更新进度"""
    manager = StateManager(str(temp_harness_dir))
    manager.init()
    
    manager.update_progress("开始任务")
    manager.update_progress("执行步骤 1")
    
    # 读取进度文件
    progress_file = temp_harness_dir / "state" / "progress.md"
    content = progress_file.read_text()
    
    assert "开始任务" in content
    assert "执行步骤 1" in content


def test_create_checkpoint(temp_harness_dir):
    """测试创建检查点"""
    manager = StateManager(str(temp_harness_dir))
    manager.init()
    
    checkpoint_data = {
        "step": 1,
        "result": "部分完成",
        "score": 0.7
    }
    manager.create_checkpoint("checkpoint_1", checkpoint_data)
    
    # 加载检查点
    loaded_data = manager.load_checkpoint("checkpoint_1")
    
    assert loaded_data is not None
    assert loaded_data["step"] == 1
    assert loaded_data["result"] == "部分完成"


def test_log_evaluation(temp_harness_dir, sample_evaluation):
    """测试记录评估日志"""
    manager = StateManager(str(temp_harness_dir))
    manager.init()
    
    manager.log_evaluation(sample_evaluation)
    
    # 检查日志文件是否创建
    logs_dir = temp_harness_dir / "logs"
    log_files = list(logs_dir.glob("evaluation_*.md"))
    
    assert len(log_files) > 0
    
    # 检查日志内容
    log_content = log_files[0].read_text()
    assert "Evaluation Log" in log_content
    assert str(sample_evaluation.score) in log_content
