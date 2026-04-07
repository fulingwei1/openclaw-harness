"""
LLM 成本追踪和使用统计
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
from pathlib import Path
from collections import defaultdict


@dataclass
class UsageRecord:
    """使用记录"""
    timestamp: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    task: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "provider": self.provider,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost": self.cost,
            "task": self.task,
            "metadata": self.metadata
        }


class PricingConfig:
    """定价配置"""
    
    # 每 1K tokens 价格（美元）
    PRICING = {
        "openai": {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        },
        "anthropic": {
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
        },
        "zai": {
            "glm-4": {"input": 0.001, "output": 0.001},
            "glm-4-flash": {"input": 0.0001, "output": 0.0001},
        },
        "kimi": {
            "moonshot-v1-8k": {"input": 0.012, "output": 0.012},
            "moonshot-v1-32k": {"input": 0.024, "output": 0.024},
            "moonshot-v1-128k": {"input": 0.06, "output": 0.06},
        },
        "minimax": {
            "abab6-chat": {"input": 0.002, "output": 0.002},
        }
    }
    
    @classmethod
    def calculate_cost(
        cls,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """计算成本"""
        provider_pricing = cls.PRICING.get(provider, {})
        model_pricing = provider_pricing.get(model, {"input": 0, "output": 0})
        
        input_cost = (input_tokens / 1000) * model_pricing.get("input", 0)
        output_cost = (output_tokens / 1000) * model_pricing.get("output", 0)
        
        return input_cost + output_cost


class CostTracker:
    """成本追踪器"""
    
    def __init__(self, storage_path: str = "./cost_tracking"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.records: List[UsageRecord] = []
        self._load()
    
    async def track_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        task: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> UsageRecord:
        """追踪使用"""
        # 计算成本
        cost = PricingConfig.calculate_cost(
            provider,
            model,
            input_tokens,
            output_tokens
        )
        
        # 创建记录
        record = UsageRecord(
            timestamp=datetime.now().isoformat(),
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost=cost,
            task=task,
            metadata=metadata or {}
        )
        
        self.records.append(record)
        self._save()
        
        return record
    
    def get_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取统计信息"""
        # 过滤记录
        filtered = self.records
        
        if start_date:
            filtered = [r for r in filtered if r.timestamp >= start_date]
        if end_date:
            filtered = [r for r in filtered if r.timestamp <= end_date]
        if provider:
            filtered = [r for r in filtered if r.provider == provider]
        if model:
            filtered = [r for r in filtered if r.model == model]
        
        # 统计
        total_cost = sum(r.cost for r in filtered)
        total_tokens = sum(r.total_tokens for r in filtered)
        total_input = sum(r.input_tokens for r in filtered)
        total_output = sum(r.output_tokens for r in filtered)
        
        # 按提供商分组
        by_provider = defaultdict(lambda: {"cost": 0, "tokens": 0, "calls": 0})
        for record in filtered:
            by_provider[record.provider]["cost"] += record.cost
            by_provider[record.provider]["tokens"] += record.total_tokens
            by_provider[record.provider]["calls"] += 1
        
        # 按模型分组
        by_model = defaultdict(lambda: {"cost": 0, "tokens": 0, "calls": 0})
        for record in filtered:
            key = f"{record.provider}/{record.model}"
            by_model[key]["cost"] += record.cost
            by_model[key]["tokens"] += record.total_tokens
            by_model[key]["calls"] += 1
        
        # 按日期分组
        by_date = defaultdict(lambda: {"cost": 0, "tokens": 0, "calls": 0})
        for record in filtered:
            date = record.timestamp[:10]  # YYYY-MM-DD
            by_date[date]["cost"] += record.cost
            by_date[date]["tokens"] += record.total_tokens
            by_date[date]["calls"] += 1
        
        return {
            "summary": {
                "total_cost": round(total_cost, 6),
                "total_tokens": total_tokens,
                "total_input_tokens": total_input,
                "total_output_tokens": total_output,
                "total_calls": len(filtered),
                "avg_cost_per_call": round(total_cost / len(filtered), 6) if filtered else 0,
                "avg_tokens_per_call": total_tokens // len(filtered) if filtered else 0
            },
            "by_provider": dict(by_provider),
            "by_model": dict(by_model),
            "by_date": dict(by_date),
            "records_count": len(filtered),
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "provider": provider,
                "model": model
            }
        }
    
    def get_recent(self, hours: int = 24) -> List[UsageRecord]:
        """获取最近的使用记录"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            r for r in self.records
            if datetime.fromisoformat(r.timestamp) >= cutoff
        ]
    
    def get_top_tasks(self, limit: int = 10) -> List[Dict]:
        """获取成本最高的任务"""
        task_costs = defaultdict(float)
        for record in self.records:
            if record.task:
                task_costs[record.task] += record.cost
        
        sorted_tasks = sorted(
            task_costs.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {"task": task, "cost": round(cost, 6)}
            for task, cost in sorted_tasks[:limit]
        ]
    
    def export_csv(self, output_path: str):
        """导出为 CSV"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入表头
            writer.writerow([
                "timestamp", "provider", "model", "input_tokens",
                "output_tokens", "total_tokens", "cost", "task"
            ])
            
            # 写入数据
            for record in self.records:
                writer.writerow([
                    record.timestamp,
                    record.provider,
                    record.model,
                    record.input_tokens,
                    record.output_tokens,
                    record.total_tokens,
                    record.cost,
                    record.task or ""
                ])
    
    def export_json(self, output_path: str):
        """导出为 JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(
                [r.to_dict() for r in self.records],
                f,
                ensure_ascii=False,
                indent=2
            )
    
    def clear_old_records(self, days: int = 30):
        """清理旧记录"""
        cutoff = datetime.now() - timedelta(days=days)
        self.records = [
            r for r in self.records
            if datetime.fromisoformat(r.timestamp) >= cutoff
        ]
        self._save()
    
    def _save(self):
        """保存到磁盘"""
        data_file = self.storage_path / "usage_records.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(
                [r.to_dict() for r in self.records],
                f,
                ensure_ascii=False
            )
    
    def _load(self):
        """从磁盘加载"""
        data_file = self.storage_path / "usage_records.json"
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.records = [
                        UsageRecord(**item) for item in data
                    ]
            except Exception as e:
                print(f"加载成本记录失败: {e}")
                self.records = []


class BudgetManager:
    """预算管理器"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        self.budgets: Dict[str, float] = {}  # {period: limit}
        self.alerts: List[Dict] = []
    
    def set_budget(self, period: str, limit: float):
        """设置预算
        
        Args:
            period: daily / weekly / monthly
            limit: 预算限制（美元）
        """
        self.budgets[period] = limit
    
    async def check_budget(self) -> Dict[str, Any]:
        """检查预算"""
        now = datetime.now()
        results = {}
        
        for period, limit in self.budgets.items():
            # 计算时间范围
            if period == "daily":
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end = now
            elif period == "weekly":
                start = now - timedelta(days=now.weekday())
                start = start.replace(hour=0, minute=0, second=0, microsecond=0)
                end = now
            elif period == "monthly":
                start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end = now
            else:
                continue
            
            # 获取该时段的成本
            stats = self.cost_tracker.get_stats(
                start_date=start.isoformat(),
                end_date=end.isoformat()
            )
            current_cost = stats["summary"]["total_cost"]
            percentage = (current_cost / limit) * 100 if limit > 0 else 0
            
            results[period] = {
                "limit": limit,
                "current": round(current_cost, 6),
                "percentage": round(percentage, 2),
                "remaining": round(limit - current_cost, 6),
                "status": "ok" if percentage < 80 else ("warning" if percentage < 100 else "exceeded")
            }
            
            # 生成告警
            if percentage >= 80 and percentage < 100:
                alert = {
                    "type": "warning",
                    "period": period,
                    "message": f"{period}预算已使用 {percentage:.1f}% (${current_cost:.4f} / ${limit:.2f})",
                    "timestamp": now.isoformat()
                }
                self.alerts.append(alert)
            elif percentage >= 100:
                alert = {
                    "type": "critical",
                    "period": period,
                    "message": f"{period}预算已超支！({percentage:.1f}%)",
                    "timestamp": now.isoformat()
                }
                self.alerts.append(alert)
        
        return results
    
    def get_alerts(self, clear: bool = False) -> List[Dict]:
        """获取告警"""
        alerts = self.alerts.copy()
        if clear:
            self.alerts = []
        return alerts


# 便捷函数
def create_cost_tracker(storage_path: str = "./cost_tracking") -> CostTracker:
    """创建成本追踪器"""
    return CostTracker(storage_path)


def create_budget_manager(cost_tracker: CostTracker) -> BudgetManager:
    """创建预算管理器"""
    return BudgetManager(cost_tracker)
