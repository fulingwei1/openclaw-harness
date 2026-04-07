"""
测试配置
"""

import pytest
from pathlib import Path
from harness.config import HarnessConfig


@pytest.fixture
def temp_harness_dir(tmp_path: Path):
    """创建临时 Harness 目录"""
    harness_dir = tmp_path / ".harness"
    harness_dir.mkdir()
    (harness_dir / "state").mkdir()
    (harness_dir / "golden_rules").mkdir()
    (harness_dir / "skills").mkdir()
    (harness_dir / "logs").mkdir()
    return harness_dir


@pytest.fixture
def sample_config():
    """示例配置"""
    return HarnessConfig()


@pytest.fixture
def sample_task():
    """示例任务"""
    from harness.models import Task
    return Task(
        id="test_task_1",
        description="创建一个简单的 REST API"
    )


@pytest.fixture
def sample_plan():
    """示例计划"""
    from harness.models import Plan, Step
    return Plan(
        task_id="test_task_1",
        steps=[
            Step(id="step_1", description="设计 API 路由"),
            Step(id="step_2", description="实现 API 端点"),
            Step(id="step_3", description="添加测试")
        ],
        estimated_complexity=0.6,
        is_complex=False
    )


@pytest.fixture
def sample_evaluation():
    """示例评估"""
    from harness.models import Evaluation
    return Evaluation(
        passed=True,
        score=0.85,
        issues=[],
        strengths=["代码清晰", "结构合理"],
        summary="整体表现良好"
    )
