"""
Generator - 内容生成器
"""

from typing import Optional
from .models import Step, Task
from .llm_adapter import LLMAdapter
from .golden_rules import GoldenRulesManager


class Generator:
    """执行步骤，生成内容"""

    SYSTEM_PROMPT = """你是一个高效的执行者。你的职责是:
1. 按照给定的步骤执行
2. 产出高质量的结果
3. 遵守所有约束和黄金法则

注意：
- 严格遵循步骤描述
- 输出要具体可执行
- 如遇到问题，明确说明"""

    def __init__(
        self,
        llm: LLMAdapter,
        golden_rules: Optional[GoldenRulesManager] = None
    ):
        self.llm = llm
        self.golden_rules = golden_rules

    def execute(self, step: Step, context: dict) -> str:
        """执行单个步骤"""
        # Build prompt with context and golden rules
        prompt = f"执行步骤：{step.description}\n\n"

        if context:
            prompt += "上下文：\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"

        if self.golden_rules:
            rules = self.golden_rules.get_all_rules()
            if rules:
                prompt += "必须遵守的规则：\n"
                for rule in rules:
                    prompt += f"- {rule.content}\n"
                prompt += "\n"

        prompt += "请执行并输出结果："

        # Generate
        result = self.llm.generate(prompt, system=self.SYSTEM_PROMPT)
        return result

    def fix(self, step: Step, issues: list, previous_output: str) -> str:
        """根据问题修正输出"""
        prompt = f"之前的输出：\n{previous_output}\n\n"
        prompt += "发现的问题：\n"
        for issue in issues:
            prompt += f"- [{issue.severity}] {issue.description}\n"
            if issue.suggestion:
                prompt += f"  建议：{issue.suggestion}\n"

        prompt += "\n请修正这些问题，输出改进后的版本："

        return self.llm.generate(prompt, system=self.SYSTEM_PROMPT)
