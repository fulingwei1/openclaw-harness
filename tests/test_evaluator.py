"""
测试 Evaluator
"""

import pytest
from harness.evaluator import Evaluator
from harness.golden_rules import GoldenRulesManager
from harness.models import Plan, Step
from unittest.mock import Mock


def test_evaluator_pass_high_score(temp_harness_dir, sample_plan):
    """测试高分数通过评估"""
    mock_llm = Mock()
    mock_llm.generate.return_value = """
SCORE: 0.9
PASSED: true
ISSUES:

STRENGTHS:
- 代码结构清晰
- 逻辑正确
- 符合最佳实践

SUMMARY: 优秀的实现，完全符合要求
"""
    
    golden_rules = GoldenRulesManager(str(temp_harness_dir))
    evaluator = Evaluator(mock_llm, golden_rules, pass_threshold=0.8)
    
    result = evaluator.evaluate("这是一个优秀的 API 实现", sample_plan)
    
    assert result.passed is True
    assert result.score >= 0.8
    assert len(result.issues) == 0


def test_evaluator_fail_low_score(temp_harness_dir, sample_plan):
    """测试低分数不通过评估"""
    mock_llm = Mock()
    mock_llm.generate.return_value = """
SCORE: 0.5
PASSED: false
ISSUES:
- [major]: 缺少错误处理 | 全局 | 添加 try-except 块
- [minor]: 代码格式不规范 | 第10行 | 使用 Black 格式化

STRENGTHS:
- 基本功能实现

SUMMARY: 存在明显问题，需要改进
"""
    
    golden_rules = GoldenRulesManager(str(temp_harness_dir))
    evaluator = Evaluator(mock_llm, golden_rules, pass_threshold=0.8)
    
    result = evaluator.evaluate("这是一个有问题的实现", sample_plan)
    
    assert result.passed is False
    assert result.score < 0.8
    assert len(result.issues) > 0


def test_evaluator_with_golden_rules(temp_harness_dir, sample_plan):
    """测试黄金法则在评估中的应用"""
    mock_llm = Mock()
    
    # 添加黄金法则
    golden_rules = GoldenRulesManager(str(temp_harness_dir))
    golden_rules.add_rule("必须使用中文注释", category="global", priority=5)
    golden_rules.add_rule("代码覆盖率必须 >80%", category="domain", priority=4)
    
    mock_llm.generate.return_value = """
SCORE: 0.85
PASSED: true
ISSUES:

STRENGTHS:
- 符合所有黄金法则

SUMMARY: 符合要求
"""
    
    evaluator = Evaluator(mock_llm, golden_rules, pass_threshold=0.8)
    result = evaluator.evaluate("代码实现", sample_plan)
    
    # 验证 LLM 调用时包含了黄金法则
    call_args = mock_llm.generate.call_args
    assert "黄金法则" in str(call_args) or "规则" in str(call_args)
