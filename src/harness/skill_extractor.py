"""
Skill Extractor - 自动技能提取器
"""

from typing import List, Optional
from .models import Skill, Task, Evaluation
from .llm_adapter import LLMAdapter


class SkillExtractor:
    """从完成的任务中提取可复用技能"""

    SYSTEM_PROMPT = """你是一个技能提取专家。你的职责是:
1. 分析任务执行过程
2. 识别可复用的模式
3. 生成标准化的技能模板

输出格式（JSON）：
```json
{
  "name": "技能名称",
  "description": "用于触发匹配的描述（50字以内）",
  "steps": [
    "步骤1",
    "步骤2"
  ],
  "checkpoints": [
    "检查点1",
    "检查点2"
  ],
  "tags": ["tag1", "tag2"]
}
```"""

    EXTRACTION_PROMPT = """任务描述：
{task_description}

执行步骤：
{steps}

最终结果：
{result}

成功指标：
- 评分: {score}
- 通过: {passed}

请从这个成功的任务执行中提取可复用的技能模式："""

    def __init__(self, llm: LLMAdapter, output_dir: str = ".harness/skills"):
        self.llm = llm
        self.output_dir = output_dir

    def extract(
        self,
        task: Task,
        result: str,
        evaluation: Evaluation
    ) -> Optional[Skill]:
        """从完成的任务中提取技能"""
        if not evaluation.passed:
            # Only extract from successful tasks
            return None

        if evaluation.score < 0.8:
            # Only extract from high-quality results
            return None

        # Format prompt
        steps_str = "\n".join([
            f"{i+1}. {step.description}"
            for i, step in enumerate(task.steps)
        ])

        prompt = self.EXTRACTION_PROMPT.format(
            task_description=task.description,
            steps=steps_str,
            result=result,
            score=evaluation.score,
            passed=evaluation.passed
        )

        # Extract
        response = self.llm.generate(prompt, system=self.SYSTEM_PROMPT)

        # Parse JSON response
        import json
        try:
            # Extract JSON from markdown code block
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            data = json.loads(json_str)

            skill = Skill(
                name=data["name"],
                description=data["description"],
                steps=data["steps"],
                checkpoints=data.get("checkpoints", []),
                examples=[f"成功完成任务：{task.description}"],
                tags=data.get("tags", []),
                source_task_id=task.id
            )

            return skill
        except Exception as e:
            print(f"Failed to parse skill: {e}")
            return None

    def save_skill(self, skill: Skill) -> str:
        """保存技能到文件"""
        import os
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate SKILL.md
        skill_md = f"""# {skill.name}

{skill.description}

## 标准流程

"""
        for i, step in enumerate(skill.steps, 1):
            skill_md += f"{i}. {step}\n"

        if skill.checkpoints:
            skill_md += "\n## 检查点\n\n"
            for checkpoint in skill.checkpoints:
                skill_md += f"- [ ] {checkpoint}\n"

        if skill.examples:
            skill_md += "\n## 成功案例\n\n"
            for example in skill.examples:
                skill_md += f"- {example}\n"

        if skill.tags:
            skill_md += f"\n## 标签\n\n{', '.join(skill.tags)}\n"

        skill_md += f"\n---\n- 源任务: {skill.source_task_id}\n"
        skill_md += f"- 创建时间: {skill.created_at}\n"

        # Save to file
        skill_file = f"{self.output_dir}/{skill.name.lower().replace(' ', '_')}.md"
        with open(skill_file, 'w', encoding='utf-8') as f:
            f.write(skill_md)

        return skill_file
