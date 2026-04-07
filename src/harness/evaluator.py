"""
Evaluator - 结果评估器
"""

from typing import List
from .models import Evaluation, Issue, Plan
from .llm_adapter import LLMAdapter
from .golden_rules import GoldenRulesManager


class Evaluator:
    """评估执行结果"""

    SYSTEM_PROMPT = """你是一个严格但公正的评估者。你的职责是:
1. 检查结果是否符合要求
2. 发现问题和不足
3. 评估整体质量

输出格式：
```
SCORE: [0.0-1.0]
PASSED: [true/false]
ISSUES:
- [severity]: [description] | [location] | [suggestion]
STRENGTHS:
- [优点1]
- [优点2]
SUMMARY: [整体评价]
```"""

    def __init__(
        self,
        llm: LLMAdapter,
        golden_rules: GoldenRulesManager,
        pass_threshold: float = 0.8
    ):
        self.llm = llm
        self.golden_rules = golden_rules
        self.pass_threshold = pass_threshold

    def evaluate(self, output: str, plan: Plan) -> Evaluation:
        """评估执行结果"""
        # Build evaluation prompt
        prompt = f"评估以下执行结果：\n\n"
        prompt += f"任务计划：\n"
        for i, step in enumerate(plan.steps, 1):
            prompt += f"{i}. {step.description}\n"

        prompt += f"\n执行结果：\n{output}\n\n"

        # Add golden rules as evaluation criteria
        rules = self.golden_rules.get_all_rules()
        if rules:
            prompt += "评估标准（黄金法则）：\n"
            for rule in rules:
                prompt += f"- {rule.content}\n"

        prompt += "\n请评估："

        # Generate evaluation
        response = self.llm.generate(prompt, system=self.SYSTEM_PROMPT)

        # Parse response
        lines = response.strip().split('\n')
        score = 0.0
        passed = False
        issues = []
        strengths = []
        summary = ""

        for line in lines:
            if line.startswith("SCORE:"):
                try:
                    score = float(line.split(":")[1].strip())
                except:
                    pass
            elif line.startswith("PASSED:"):
                passed = "true" in line.lower()
            elif line.startswith("SUMMARY:"):
                summary = line.split(":", 1)[1].strip()
            elif line.startswith("-") and ":" in line:
                # Issue or strength
                content = line[1:].strip()
                if "|" in content:
                    # Issue format: [severity]: [description] | [location] | [suggestion]
                    parts = [p.strip() for p in content.split("|")]
                    severity_desc = parts[0]
                    if ":" in severity_desc:
                        severity, description = severity_desc.split(":", 1)
                        severity = severity.strip("[] ").lower()
                        description = description.strip()
                    else:
                        severity = "minor"
                        description = severity_desc

                    location = parts[1] if len(parts) > 1 else None
                    suggestion = parts[2] if len(parts) > 2 else None

                    issues.append(Issue(
                        severity=severity,
                        description=description,
                        location=location,
                        suggestion=suggestion
                    ))
                else:
                    # Strength
                    strengths.append(content)

        # Override passed based on score
        passed = passed or (score >= self.pass_threshold)

        return Evaluation(
            passed=passed,
            score=score,
            issues=issues,
            strengths=strengths,
            summary=summary
        )
