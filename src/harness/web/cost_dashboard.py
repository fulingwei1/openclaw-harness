"""
成本仪表板 API
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json

from ..cost_tracker import create_cost_tracker, create_budget_manager

router = APIRouter(prefix="/api/costs", tags=["costs"])

# 全局实例
cost_tracker = create_cost_tracker()
budget_manager = create_budget_manager(cost_tracker)


@router.get("/summary")
async def get_cost_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """获取成本摘要"""
    stats = cost_tracker.get_stats(
        start_date=start_date,
        end_date=end_date,
        provider=provider,
        model=model
    )
    
    # 添加趋势数据（最近 7 天）
    trends = []
    today = datetime.now()
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        daily_stats = cost_tracker.get_stats(
            start_date=f"{date_str}T00:00:00",
            end_date=f"{date_str}T23:59:59"
        )
        trends.append({
            "date": date_str,
            "cost": daily_stats["summary"]["total_cost"],
            "tokens": daily_stats["summary"]["total_tokens"],
            "calls": daily_stats["summary"]["total_calls"]
        })
    
    return {
        "summary": stats["summary"],
        "by_provider": stats["by_provider"],
        "by_model": stats["by_model"],
        "by_date": stats["by_date"],
        "trends": trends,
        "top_tasks": cost_tracker.get_top_tasks(10)
    }


@router.get("/recent")
async def get_recent_usage(hours: int = 24) -> List[Dict[str, Any]]:
    """获取最近使用记录"""
    records = cost_tracker.get_recent(hours)
    return [r.to_dict() for r in records]


@router.post("/track")
async def track_usage(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    task: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """追踪使用"""
    record = await cost_tracker.track_usage(
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        task=task,
        metadata=metadata
    )
    
    return {
        "success": True,
        "record": record.to_dict()
    }


@router.get("/budgets")
async def get_budgets() -> Dict[str, Any]:
    """获取预算状态"""
    budget_status = await budget_manager.check_budget()
    alerts = budget_manager.get_alerts()
    
    return {
        "budgets": budget_status,
        "alerts": alerts,
        "alert_count": len(alerts)
    }


@router.post("/budgets")
async def set_budget(period: str, limit: float) -> Dict[str, Any]:
    """设置预算"""
    if period not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Invalid period")
    
    budget_manager.set_budget(period, limit)
    
    # 检查新预算
    budget_status = await budget_manager.check_budget()
    
    return {
        "success": True,
        "period": period,
        "limit": limit,
        "status": budget_status.get(period, {})
    }


@router.get("/alerts")
async def get_alerts(clear: bool = False) -> List[Dict[str, Any]]:
    """获取告警"""
    return budget_manager.get_alerts(clear=clear)


@router.get("/export/csv")
async def export_csv():
    """导出为 CSV"""
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        cost_tracker.export_csv(f.name)
        
        with open(f.name, 'r') as csv_file:
            csv_content = csv_file.read()
        
        os.unlink(f.name)
        
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=harness_costs_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )


@router.get("/export/json")
async def export_json():
    """导出为 JSON"""
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        cost_tracker.export_json(f.name)
        
        with open(f.name, 'r') as json_file:
            json_content = json_file.read()
        
        os.unlink(f.name)
        
        from fastapi.responses import Response
        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=harness_costs_{datetime.now().strftime('%Y%m%d')}.json"
            }
        )


@router.get("/charts/usage")
async def get_usage_charts() -> Dict[str, Any]:
    """获取使用图表数据"""
    stats = cost_tracker.get_stats()
    
    # 按提供商分布（饼图）
    provider_distribution = [
        {
            "name": provider,
            "value": data["cost"],
            "tokens": data["tokens"],
            "calls": data["calls"]
        }
        for provider, data in stats["by_provider"].items()
    ]
    
    # 按模型分布（条形图）
    model_distribution = [
        {
            "model": model,
            "cost": data["cost"],
            "tokens": data["tokens"],
            "calls": data["calls"]
        }
        for model, data in stats["by_model"].items()
    ]
    
    # 成本趋势（折线图）
    today = datetime.now()
    trend_data = []
    for i in range(29, -1, -1):  # 最近 30 天
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        daily_stats = cost_tracker.get_stats(
            start_date=f"{date_str}T00:00:00",
            end_date=f"{date_str}T23:59:59"
        )
        trend_data.append({
            "date": date_str,
            "cost": daily_stats["summary"]["total_cost"],
            "tokens": daily_stats["summary"]["total_tokens"],
            "calls": daily_stats["summary"]["total_calls"]
        })
    
    # 成本预测（简单线性预测）
    if len(trend_data) >= 7:
        recent_costs = [d["cost"] for d in trend_data[-7:]]
        avg_daily_cost = sum(recent_costs) / len(recent_costs)
        
        predicted_monthly_cost = avg_daily_cost * 30
        predicted_yearly_cost = avg_daily_cost * 365
    else:
        predicted_monthly_cost = 0
        predicted_yearly_cost = 0
    
    return {
        "provider_distribution": provider_distribution,
        "model_distribution": model_distribution,
        "cost_trend": trend_data,
        "predictions": {
            "monthly": round(predicted_monthly_cost, 6),
            "yearly": round(predicted_yearly_cost, 6)
        }
    }


@router.get("/analytics")
async def get_analytics() -> Dict[str, Any]:
    """获取分析数据"""
    stats = cost_tracker.get_stats()
    
    # 成本效率分析
    avg_cost_per_call = stats["summary"]["avg_cost_per_call"]
    avg_tokens_per_call = stats["summary"]["avg_tokens_per_call"]
    
    # 最昂贵的任务
    expensive_tasks = cost_tracker.get_top_tasks(5)
    
    # 最常用的模型
    most_used_models = sorted(
        [
            {"model": k, "calls": v["calls"]}
            for k, v in stats["by_model"].items()
        ],
        key=lambda x: x["calls"],
        reverse=True
    )[:5]
    
    # 成本分布
    cost_distribution = {
        "<$0.01": 0,
        "$0.01-$0.10": 0,
        "$0.10-$1.00": 0,
        ">$1.00": 0
    }
    
    for record in cost_tracker.records:
        if record.cost < 0.01:
            cost_distribution["<$0.01"] += 1
        elif record.cost < 0.10:
            cost_distribution["$0.01-$0.10"] += 1
        elif record.cost < 1.00:
            cost_distribution["$0.10-$1.00"] += 1
        else:
            cost_distribution[">$1.00"] += 1
    
    return {
        "efficiency": {
            "avg_cost_per_call": avg_cost_per_call,
            "avg_tokens_per_call": avg_tokens_per_call,
            "cost_per_1k_tokens": (
                (stats["summary"]["total_cost"] / stats["summary"]["total_tokens"] * 1000)
                if stats["summary"]["total_tokens"] > 0
                else 0
            )
        },
        "expensive_tasks": expensive_tasks,
        "most_used_models": most_used_models,
        "cost_distribution": cost_distribution
    }
