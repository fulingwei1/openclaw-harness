"""
State Manager - 状态管理器
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from .models import Task, Plan, Evaluation


class StateManager:
    """外部化状态管理"""

    def __init__(self, harness_dir: str = ".harness"):
        self.harness_dir = Path(harness_dir)
        self.state_dir = self.harness_dir / "state"
        self.current_task_file = self.state_dir / "current_task.json"
        self.progress_file = self.state_dir / "progress.md"
        self.logs_dir = self.harness_dir / "logs"

    def init(self):
        """初始化状态目录"""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Initialize progress file
        if not self.progress_file.exists():
            self.progress_file.write_text("# Harness Progress\n\n")

    def save_task(self, task: Task):
        """保存当前任务"""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with open(self.current_task_file, 'w', encoding='utf-8') as f:
            json.dump(task.model_dump(), f, ensure_ascii=False, indent=2, default=str)

    def load_task(self) -> Optional[Task]:
        """加载当前任务"""
        if not self.current_task_file.exists():
            return None

        with open(self.current_task_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return Task(**data)

    def update_progress(self, message: str):
        """更新进度"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.progress_file, 'a', encoding='utf-8') as f:
            f.write(f"- [{timestamp}] {message}\n")

    def create_checkpoint(self, name: str, data: Dict[str, Any]):
        """创建检查点"""
        checkpoint_file = self.state_dir / f"checkpoint_{name}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump({
                "name": name,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }, f, ensure_ascii=False, indent=2, default=str)

    def load_checkpoint(self, name: str) -> Optional[Dict[str, Any]]:
        """加载检查点"""
        checkpoint_file = self.state_dir / f"checkpoint_{name}.json"
        if not checkpoint_file.exists():
            return None

        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
            return checkpoint.get("data")

    def log_evaluation(self, evaluation: Evaluation):
        """记录评估结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"evaluation_{timestamp}.md"

        content = f"""# Evaluation Log

- Time: {evaluation.evaluated_at}
- Passed: {evaluation.passed}
- Score: {evaluation.score}

## Issues

"""
        for issue in evaluation.issues:
            content += f"- [{issue.severity}] {issue.description}\n"
            if issue.location:
                content += f"  - Location: {issue.location}\n"
            if issue.suggestion:
                content += f"  - Suggestion: {issue.suggestion}\n"

        content += "\n## Strengths\n\n"
        for strength in evaluation.strengths:
            content += f"- {strength}\n"

        content += f"\n## Summary\n\n{evaluation.summary}\n"

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def get_state_summary(self) -> str:
        """获取状态摘要"""
        task = self.load_task()
        if not task:
            return "No active task"

        summary = f"Task: {task.description}\n"
        summary += f"Status: {task.status}\n"
        summary += f"Steps: {len(task.steps)}\n"
        summary += f"Created: {task.created_at}\n"

        return summary
