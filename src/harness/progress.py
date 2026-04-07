"""
实时进度追踪系统
"""
import asyncio
from datetime import datetime
from enum import Enum
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass, field
import json


class StepStatus(str, Enum):
    """步骤状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepProgress:
    """单个步骤的进度"""
    step_id: str
    name: str
    status: StepStatus = StepStatus.PENDING
    progress: float = 0.0  # 0-100
    message: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "step_id": self.step_id,
            "name": self.name,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "metadata": self.metadata
        }


class ProgressTracker:
    """进度追踪器"""
    
    def __init__(self):
        self.steps: List[StepProgress] = []
        self.current_step: Optional[StepProgress] = None
        self.callbacks: List[Callable] = []
        self.total_progress: float = 0.0
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
    
    def add_step(self, step_id: str, name: str, metadata: Optional[dict] = None):
        """添加步骤"""
        step = StepProgress(
            step_id=step_id,
            name=name,
            metadata=metadata or {}
        )
        self.steps.append(step)
    
    async def start_step(self, step_id: str, message: str = ""):
        """开始步骤"""
        step = self._get_step(step_id)
        if not step:
            return
        
        step.status = StepStatus.RUNNING
        step.started_at = datetime.now()
        step.message = message or f"开始 {step.name}"
        self.current_step = step
        
        if not self.started_at:
            self.started_at = datetime.now()
        
        await self._notify_callbacks("step_started", step)
    
    async def update_step(
        self,
        step_id: str,
        progress: float,
        message: str = ""
    ):
        """更新步骤进度"""
        step = self._get_step(step_id)
        if not step:
            return
        
        step.progress = min(100, max(0, progress))
        step.message = message or step.message
        
        # 更新总进度
        completed_steps = sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)
        current_step_progress = step.progress / 100
        total_steps = len(self.steps)
        
        if total_steps > 0:
            self.total_progress = (
                (completed_steps / total_steps) * 100 +
                (current_step_progress / total_steps) * 100
            )
        
        await self._notify_callbacks("step_updated", step)
    
    async def complete_step(self, step_id: str, message: str = ""):
        """完成步骤"""
        step = self._get_step(step_id)
        if not step:
            return
        
        step.status = StepStatus.COMPLETED
        step.completed_at = datetime.now()
        step.progress = 100
        step.message = message or f"完成 {step.name}"
        
        await self._notify_callbacks("step_completed", step)
    
    async def fail_step(self, step_id: str, error: str):
        """步骤失败"""
        step = self._get_step(step_id)
        if not step:
            return
        
        step.status = StepStatus.FAILED
        step.completed_at = datetime.now()
        step.error = error
        step.message = f"失败: {error}"
        
        await self._notify_callbacks("step_failed", step)
    
    async def skip_step(self, step_id: str, reason: str = ""):
        """跳过步骤"""
        step = self._get_step(step_id)
        if not step:
            return
        
        step.status = StepStatus.SKIPPED
        step.completed_at = datetime.now()
        step.message = reason or f"跳过 {step.name}"
        
        await self._notify_callbacks("step_skipped", step)
    
    def on_progress(self, callback: Callable):
        """注册进度回调"""
        self.callbacks.append(callback)
    
    def get_progress(self) -> dict:
        """获取总体进度"""
        completed = sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)
        failed = sum(1 for s in self.steps if s.status == StepStatus.FAILED)
        
        return {
            "total_progress": round(self.total_progress, 2),
            "completed_steps": completed,
            "failed_steps": failed,
            "total_steps": len(self.steps),
            "current_step": self.current_step.to_dict() if self.current_step else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "steps": [s.to_dict() for s in self.steps]
        }
    
    def to_json(self) -> str:
        """导出为 JSON"""
        return json.dumps(self.get_progress(), indent=2)
    
    async def _notify_callbacks(self, event: str, step: StepProgress):
        """通知所有回调"""
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event, step, self.get_progress())
                else:
                    callback(event, step, self.get_progress())
            except Exception as e:
                print(f"回调失败: {e}")
    
    def _get_step(self, step_id: str) -> Optional[StepProgress]:
        """获取步骤"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None


class ProgressUI:
    """进度显示 UI（Rich）"""
    
    def __init__(self, tracker: ProgressTracker):
        self.tracker = tracker
        self.tracker.on_progress(self._update_ui)
        self.progress_bar = None
        self.step_panels = {}
    
    async def _update_ui(self, event: str, step: StepProgress, progress: dict):
        """更新 UI"""
        from rich.console import Console
        from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
        from rich.layout import Layout
        from rich.panel import Panel
        
        console = Console()
        
        if event == "step_started":
            console.print(f"\n[bold blue]▶[/] {step.name}...")
        
        elif event == "step_updated":
            if step.progress > 0:
                console.print(f"  {step.progress:.0f}% - {step.message}")
        
        elif event == "step_completed":
            console.print(f"[bold green]✓[/] {step.name} 完成")
        
        elif event == "step_failed":
            console.print(f"[bold red]✗[/] {step.name} 失败: {step.error}")
        
        elif event == "step_skipped":
            console.print(f"[dim]○[/] {step.name} 已跳过")
        
        # 显示总体进度
        if progress["total_progress"] > 0:
            console.print(
                f"\n[bold]总体进度:[/] {progress['total_progress']:.1f}% "
                f"({progress['completed_steps']}/{progress['total_steps']})"
            )


# 便捷函数
def create_tracker(steps: List[str]) -> ProgressTracker:
    """创建进度追踪器"""
    tracker = ProgressTracker()
    for i, step_name in enumerate(steps):
        tracker.add_step(f"step_{i}", step_name)
    return tracker
