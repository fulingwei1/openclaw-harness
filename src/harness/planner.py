"""
Planner - 任务拆解器
"""

from typing import List
from .models import Step, Plan, Task
from .llm_adapter import LLMAdapter


class Planner:
    """拆解任务成执行计划"""

    SYSTEM_PROMPT = """你是一个任务规划专家。你的职责是:
1. 分析任务描述
2. 识别复杂度（简单任务 vs 复杂任务）
3. 生成清晰的执行步骤

输出格式：
```
COMPLEXITY: [0.0-1.0]
IS_COMPLEX: [true/false]
STEPS:
1. [第一步描述]
2. [第二步描述]
...
RATIONALE: [为什么这样规划]
```"""

    def __init__(self, llm: LLMAdapter):
        self.llm = llm

    def decompose(self, task: Task) -> Plan:
        """拆解任务成计划"""
        prompt = f"请拆解以下任务：\n\n{task.description}"

        response = self.llm.generate(prompt, system=self.SYSTEM_PROMPT)

        # Parse response
        lines = response.strip().split('\n')
        complexity = 0.5
        is_complex = False
        steps = []
        rationale = ""

        for line in lines:
            if line.startswith("COMPLEXITY:"):
                try:
                    complexity = float(line.split(":")[1].strip())
                except:
                    pass
            elif line.startswith("IS_COMPLEX:"):
                is_complex = "true" in line.lower()
            elif line.startswith("RATIONALE:"):
                rationale = line.split(":", 1)[1].strip()
            elif line.strip() and line[0].isdigit() and "." in line:
                # Step line: "1. Description"
                step_desc = line.split(".", 1)[1].strip()
                step_id = f"step_{len(steps)+1}"
                steps.append(Step(id=step_id, description=step_desc))

        return Plan(
            task_id=task.id,
            steps=steps,
            estimated_complexity=complexity,
            is_complex=is_complex,
            rationale=rationale
        )
