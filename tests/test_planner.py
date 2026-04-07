"""
测试 Planner
"""

import pytest
from harness.planner import Planner
from harness.models import Task
from unittest.mock import Mock, patch


def test_planner_decompose_simple_task(sample_task, sample_config):
    """测试简单任务拆解"""
    # Mock LLM
    mock_llm = Mock()
    mock_llm.generate.return_value = """
COMPLEXITY: 0.3
IS_COMPLEX: false
STEPS:
1. 设计数据模型
2. 创建 API 路由
3. 实现业务逻辑
RATIONALE: 这是一个简单的 CRUD API 任务
"""
    
    planner = Planner(mock_llm)
    plan = planner.decompose(sample_task)
    
    assert plan.task_id == sample_task.id
    assert len(plan.steps) == 3
    assert plan.is_complex is False
    assert plan.estimated_complexity < 0.5


def test_planner_decompose_complex_task(sample_config):
    """测试复杂任务拆解"""
    complex_task = Task(
        id="complex_task_1",
        description="构建一个微服务架构的电商系统，包含用户、商品、订单、支付等服务"
    )
    
    # Mock LLM
    mock_llm = Mock()
    mock_llm.generate.return_value = """
COMPLEXITY: 0.9
IS_COMPLEX: true
STEPS:
1. 设计系统架构
2. 拆分微服务边界
3. 定义服务间通信协议
4. 实现用户服务
5. 实现商品服务
6. 实现订单服务
7. 实现支付服务
8. 配置 API 网关
9. 设置服务发现
10. 添加监控和日志
RATIONALE: 这是一个复杂的分布式系统，需要多个微服务协同工作
"""
    
    planner = Planner(mock_llm)
    plan = planner.decompose(complex_task)
    
    assert plan.is_complex is True
    assert plan.estimated_complexity > 0.8
    assert len(plan.steps) >= 5
