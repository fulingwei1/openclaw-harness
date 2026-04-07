"""
测试 Golden Rules 管理器
"""

import pytest
from harness.golden_rules import GoldenRulesManager


def test_add_rule(temp_harness_dir):
    """测试添加规则"""
    manager = GoldenRulesManager(str(temp_harness_dir))
    
    rule = manager.add_rule(
        content="所有函数必须有文档字符串",
        category="domain",
        priority=4
    )
    
    assert rule.id.startswith("rule_")
    assert rule.content == "所有函数必须有文档字符串"
    assert rule.category == "domain"
    assert rule.priority == 4
    
    # 验证持久化
    new_manager = GoldenRulesManager(str(temp_harness_dir))
    rules = new_manager.get_all_rules()
    assert len(rules) > 0


def test_remove_rule(temp_harness_dir):
    """测试删除规则"""
    manager = GoldenRulesManager(str(temp_harness_dir))
    
    rule = manager.add_rule("测试规则", "global", 3)
    assert len(manager.get_all_rules()) > 0
    
    # 删除规则
    result = manager.remove_rule(rule.id)
    assert result is True
    
    # 验证已删除
    rules = manager.get_all_rules()
    assert rule.id not in [r.id for r in rules]


def test_get_rules_by_category(temp_harness_dir):
    """测试按类别获取规则"""
    manager = GoldenRulesManager(str(temp_harness_dir))
    
    # 添加不同类别的规则
    manager.add_rule("全局规则1", "global", 5)
    manager.add_rule("全局规则2", "global", 4)
    manager.add_rule("领域规则1", "domain", 3)
    manager.add_rule("格式规则1", "format", 2)
    
    # 获取 global 规则
    global_rules = manager.get_rules_by_category("global")
    assert len(global_rules) >= 2
    
    # 获取 domain 规则
    domain_rules = manager.get_rules_by_category("domain")
    assert len(domain_rules) >= 1


def test_get_rules_as_prompt(temp_harness_dir):
    """测试生成规则提示文本"""
    manager = GoldenRulesManager(str(temp_harness_dir))
    
    manager.add_rule("必须使用中文", "global", 5)
    manager.add_rule("代码要有注释", "domain", 4)
    
    prompt = manager.get_rules_as_prompt()
    
    assert "黄金法则" in prompt
    assert "必须使用中文" in prompt
    assert "代码要有注释" in prompt
