"""
Agent 协作仪表盘 API
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import asyncio

router = APIRouter(prefix="/api/agents", tags=["agents"])


@dataclass
class AgentInfo:
    """Agent 信息"""
    agent_id: str
    name: str
    type: str  # generator, evaluator, planner, etc.
    status: str  # idle, running, completed, failed
    current_task: Optional[str] = None
    performance: Dict[str, float] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CollaborationEvent:
    """协作事件"""
    event_id: str
    from_agent: str
    to_agent: str
    task: str
    timestamp: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvolutionRecord:
    """进化记录"""
    evolution_id: str
    agent_id: str
    generation: int
    improvements: List[str]
    performance_delta: float
    timestamp: str


class AgentOrchestrator:
    """Agent 编排器"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.collaborations: List[CollaborationEvent] = []
        self.evolutions: List[EvolutionRecord] = []
        self.task_queue: List[Dict] = []
        self.completed_tasks: List[Dict] = []
    
    def register_agent(self, agent_id: str, name: str, agent_type: str) -> AgentInfo:
        """注册 Agent"""
        agent = AgentInfo(
            agent_id=agent_id,
            name=name,
            type=agent_type,
            status="idle",
            performance={
                "tasks_completed": 0,
                "success_rate": 0.0,
                "avg_time": 0.0,
                "efficiency": 0.0
            }
        )
        self.agents[agent_id] = agent
        return agent
    
    def update_agent_status(
        self,
        agent_id: str,
        status: str,
        current_task: Optional[str] = None
    ):
        """更新 Agent 状态"""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            self.agents[agent_id].current_task = current_task
            self.agents[agent_id].last_activity = datetime.now().isoformat()
    
    def record_collaboration(
        self,
        from_agent: str,
        to_agent: str,
        task: str,
        data: Optional[Dict] = None
    ):
        """记录协作"""
        event = CollaborationEvent(
            event_id=f"collab_{len(self.collaborations)}",
            from_agent=from_agent,
            to_agent=to_agent,
            task=task,
            timestamp=datetime.now().isoformat(),
            data=data or {}
        )
        self.collaborations.append(event)
    
    def record_evolution(
        self,
        agent_id: str,
        generation: int,
        improvements: List[str],
        performance_delta: float
    ):
        """记录进化"""
        evolution = EvolutionRecord(
            evolution_id=f"evo_{len(self.evolutions)}",
            agent_id=agent_id,
            generation=generation,
            improvements=improvements,
            performance_delta=performance_delta,
            timestamp=datetime.now().isoformat()
        )
        self.evolutions.append(evolution)
    
    def get_collaboration_network(self) -> Dict[str, Any]:
        """获取协作网络"""
        nodes = [
            {
                "id": agent.agent_id,
                "name": agent.name,
                "type": agent.type,
                "status": agent.status,
                "performance": agent.performance
            }
            for agent in self.agents.values()
        ]
        
        edges = []
        edge_count = {}
        
        for collab in self.collaborations:
            key = f"{collab.from_agent}->{collab.to_agent}"
            if key not in edge_count:
                edge_count[key] = 0
            edge_count[key] += 1
        
        for key, count in edge_count.items():
            source, target = key.split("->")
            edges.append({
                "source": source,
                "target": target,
                "weight": count
            })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def get_evolution_history(self, agent_id: Optional[str] = None) -> List[Dict]:
        """获取进化历史"""
        evolutions = self.evolutions
        
        if agent_id:
            evolutions = [e for e in evolutions if e.agent_id == agent_id]
        
        return [
            {
                "evolution_id": e.evolution_id,
                "agent_id": e.agent_id,
                "generation": e.generation,
                "improvements": e.improvements,
                "performance_delta": e.performance_delta,
                "timestamp": e.timestamp
            }
            for e in evolutions
        ]
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """获取 Agent 统计"""
        total_agents = len(self.agents)
        active_agents = sum(1 for a in self.agents.values() if a.status == "running")
        idle_agents = sum(1 for a in self.agents.values() if a.status == "idle")
        total_collaborations = len(self.collaborations)
        total_evolutions = len(self.evolutions)
        
        # 按类型分组
        by_type = {}
        for agent in self.agents.values():
            if agent.type not in by_type:
                by_type[agent.type] = {"count": 0, "avg_performance": 0}
            by_type[agent.type]["count"] += 1
            by_type[agent.type]["avg_performance"] += agent.performance.get("efficiency", 0)
        
        for agent_type in by_type:
            count = by_type[agent_type]["count"]
            by_type[agent_type]["avg_performance"] /= count
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "idle_agents": idle_agents,
            "total_collaborations": total_collaborations,
            "total_evolutions": total_evolutions,
            "by_type": by_type
        }
    
    def get_recent_activities(self, hours: int = 24) -> List[Dict]:
        """获取最近活动"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        activities = []
        
        # Agent 状态变化
        for agent in self.agents.values():
            if datetime.fromisoformat(agent.last_activity) >= cutoff:
                activities.append({
                    "type": "agent_activity",
                    "agent_id": agent.agent_id,
                    "agent_name": agent.name,
                    "status": agent.status,
                    "task": agent.current_task,
                    "timestamp": agent.last_activity
                })
        
        # 协作事件
        for collab in self.collaborations:
            if datetime.fromisoformat(collab.timestamp) >= cutoff:
                activities.append({
                    "type": "collaboration",
                    "from_agent": collab.from_agent,
                    "to_agent": collab.to_agent,
                    "task": collab.task,
                    "timestamp": collab.timestamp
                })
        
        # 进化事件
        for evolution in self.evolutions:
            if datetime.fromisoformat(evolution.timestamp) >= cutoff:
                activities.append({
                    "type": "evolution",
                    "agent_id": evolution.agent_id,
                    "generation": evolution.generation,
                    "improvements": evolution.improvements,
                    "timestamp": evolution.timestamp
                })
        
        # 按时间排序
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return activities[:100]  # 返回最近100条


# 全局编排器实例
orchestrator = AgentOrchestrator()

# 初始化示例数据
orchestrator.register_agent("agent_1", "Code Generator", "generator")
orchestrator.register_agent("agent_2", "Code Evaluator", "evaluator")
orchestrator.register_agent("agent_3", "Planner", "planner")
orchestrator.register_agent("agent_4", "Optimizer", "optimizer")

orchestrator.update_agent_status("agent_1", "running", "生成 API 代码")
orchestrator.update_agent_status("agent_2", "idle")
orchestrator.update_agent_status("agent_3", "running", "规划测试流程")

# 示例协作
orchestrator.record_collaboration("agent_3", "agent_1", "规划 -> 生成")
orchestrator.record_collaboration("agent_1", "agent_2", "生成 -> 评估")
orchestrator.record_collaboration("agent_2", "agent_4", "评估 -> 优化")

# 示例进化
orchestrator.record_evolution("agent_1", 2, ["提高代码质量", "减少生成时间"], 0.15)
orchestrator.record_evolution("agent_2", 3, ["更准确的评估", "支持更多语言"], 0.22)


# API 端点

@router.get("/overview")
async def get_overview() -> Dict[str, Any]:
    """获取总览"""
    stats = orchestrator.get_agent_stats()
    network = orchestrator.get_collaboration_network()
    
    return {
        "stats": stats,
        "network": network,
        "recent_activities": orchestrator.get_recent_activities(24)[:10]
    }


@router.get("/agents")
async def list_agents() -> List[Dict[str, Any]]:
    """列出所有 Agent"""
    return [
        {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "type": agent.type,
            "status": agent.status,
            "current_task": agent.current_task,
            "performance": agent.performance,
            "last_activity": agent.last_activity
        }
        for agent in orchestrator.agents.values()
    ]


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str) -> Dict[str, Any]:
    """获取单个 Agent 详情"""
    if agent_id not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = orchestrator.agents[agent_id]
    evolutions = orchestrator.get_evolution_history(agent_id)
    
    return {
        **agent.__dict__,
        "evolutions": evolutions
    }


@router.post("/agents")
async def create_agent(name: str, agent_type: str) -> Dict[str, Any]:
    """创建新 Agent"""
    agent_id = f"agent_{len(orchestrator.agents) + 1}"
    agent = orchestrator.register_agent(agent_id, name, agent_type)
    
    return {
        "success": True,
        "agent": agent.__dict__
    }


@router.patch("/agents/{agent_id}/status")
async def update_status(
    agent_id: str,
    status: str,
    current_task: Optional[str] = None
) -> Dict[str, Any]:
    """更新 Agent 状态"""
    if agent_id not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    orchestrator.update_agent_status(agent_id, status, current_task)
    
    return {
        "success": True,
        "agent": orchestrator.agents[agent_id].__dict__
    }


@router.get("/collaborations")
async def get_collaborations(hours: int = 24) -> List[Dict[str, Any]]:
    """获取协作记录"""
    cutoff = datetime.now() - timedelta(hours=hours)
    
    return [
        {
            "event_id": c.event_id,
            "from_agent": c.from_agent,
            "to_agent": c.to_agent,
            "task": c.task,
            "timestamp": c.timestamp,
            "data": c.data
        }
        for c in orchestrator.collaborations
        if datetime.fromisoformat(c.timestamp) >= cutoff
    ]


@router.get("/network")
async def get_network() -> Dict[str, Any]:
    """获取协作网络图"""
    return orchestrator.get_collaboration_network()


@router.get("/evolutions")
async def get_evolutions(
    agent_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """获取进化历史"""
    evolutions = orchestrator.get_evolution_history(agent_id)
    return evolutions[:limit]


@router.post("/evolutions")
async def record_evolution(
    agent_id: str,
    generation: int,
    improvements: List[str],
    performance_delta: float
) -> Dict[str, Any]:
    """记录进化"""
    if agent_id not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    orchestrator.record_evolution(
        agent_id,
        generation,
        improvements,
        performance_delta
    )
    
    return {
        "success": True,
        "agent_id": agent_id,
        "generation": generation
    }


@router.get("/activities")
async def get_activities(hours: int = 24) -> List[Dict[str, Any]]:
    """获取最近活动"""
    return orchestrator.get_recent_activities(hours)


@router.get("/charts/performance")
async def get_performance_charts() -> Dict[str, Any]:
    """获取性能图表数据"""
    # Agent 性能对比（条形图）
    agent_performance = [
        {
            "agent": agent.name,
            "efficiency": agent.performance.get("efficiency", 0),
            "success_rate": agent.performance.get("success_rate", 0),
            "avg_time": agent.performance.get("avg_time", 0)
        }
        for agent in orchestrator.agents.values()
    ]
    
    # 协作频率（热力图）
    collaboration_matrix = {}
    for agent in orchestrator.agents.values():
        collaboration_matrix[agent.agent_id] = {}
        for other in orchestrator.agents.values():
            collaboration_matrix[agent.agent_id][other.agent_id] = 0
    
    for collab in orchestrator.collaborations:
        if collab.from_agent in collaboration_matrix and collab.to_agent in collaboration_matrix[collab.from_agent]:
            collaboration_matrix[collab.from_agent][collab.to_agent] += 1
    
    # 进化趋势（折线图）
    evolution_trend = []
    for evolution in sorted(orchestrator.evolutions, key=lambda x: x.timestamp):
        evolution_trend.append({
            "timestamp": evolution.timestamp,
            "agent_id": evolution.agent_id,
            "generation": evolution.generation,
            "performance_delta": evolution.performance_delta
        })
    
    return {
        "agent_performance": agent_performance,
        "collaboration_matrix": collaboration_matrix,
        "evolution_trend": evolution_trend
    }
