"""
Golden Rules Manager - 黄金法则管理器
"""

import os
from typing import List, Optional
from pathlib import Path
from .models import GoldenRule


class GoldenRulesManager:
    """管理黄金法则/约束文档"""

    def __init__(self, harness_dir: str = ".harness"):
        self.harness_dir = Path(harness_dir)
        self.rules_dir = self.harness_dir / "golden_rules"
        self.rules_file = self.rules_dir / "rules.yaml"
        self.rules: List[GoldenRule] = []
        self._load_rules()

    def _load_rules(self):
        """从文件加载规则"""
        if not self.rules_file.exists():
            self.rules = []
            return

        import yaml
        with open(self.rules_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or []

        self.rules = [GoldenRule(**rule_data) for rule_data in data]

    def _save_rules(self):
        """保存规则到文件"""
        self.rules_dir.mkdir(parents=True, exist_ok=True)

        import yaml
        data = [rule.model_dump() for rule in self.rules]
        with open(self.rules_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def add_rule(
        self,
        content: str,
        category: str = "global",
        priority: int = 3
    ) -> GoldenRule:
        """添加新规则"""
        rule_id = f"rule_{len(self.rules) + 1}"
        rule = GoldenRule(
            id=rule_id,
            content=content,
            category=category,
            priority=priority
        )
        self.rules.append(rule)
        self._save_rules()
        return rule

    def remove_rule(self, rule_id: str) -> bool:
        """删除规则"""
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                self.rules.pop(i)
                self._save_rules()
                return True
        return False

    def get_rules_by_category(self, category: str) -> List[GoldenRule]:
        """按类别获取规则"""
        return [r for r in self.rules if r.category == category]

    def get_all_rules(self, sort_by_priority: bool = True) -> List[GoldenRule]:
        """获取所有规则"""
        if sort_by_priority:
            return sorted(self.rules, key=lambda r: r.priority, reverse=True)
        return self.rules

    def get_rules_as_prompt(self) -> str:
        """生成规则提示文本"""
        if not self.rules:
            return ""

        prompt = "# 必须遵守的黄金法则\n\n"
        for category in ["global", "domain", "format"]:
            rules = self.get_rules_by_category(category)
            if rules:
                prompt += f"## {category.upper()}\n\n"
                for rule in rules:
                    prompt += f"- [P{rule.priority}] {rule.content}\n"
                prompt += "\n"

        return prompt

    def init_default_rules(self):
        """初始化默认规则"""
        defaults = [
            ("所有输出必须使用中文", "global", 5),
            ("代码必须有清晰的注释", "global", 4),
            ("重要决策必须有理由说明", "domain", 3),
            ("输出格式必须整洁规范", "format", 3),
        ]

        for content, category, priority in defaults:
            self.add_rule(content, category, priority)
