"""
WebSocket 实时通信
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import asyncio
import json
from datetime import datetime


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[str, Set[WebSocket]] = {
            "agents": set(),      # Agent 状态更新
            "costs": set(),       # 成本更新
            "evolutions": set(),  # 进化事件
            "tasks": set(),       # 任务状态
            "all": set()          # 订阅所有事件
        }
    
    async def connect(self, websocket: WebSocket):
        """接受新连接"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        # 发送欢迎消息
        await websocket.send_json({
            "type": "connected",
            "timestamp": datetime.now().isoformat(),
            "message": "WebSocket 连接成功",
            "available_channels": list(self.subscriptions.keys())
        })
    
    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        self.active_connections.discard(websocket)
        
        # 从所有订阅中移除
        for channel in self.subscriptions.values():
            channel.discard(websocket)
    
    async def subscribe(self, websocket: WebSocket, channel: str):
        """订阅频道"""
        if channel in self.subscriptions:
            self.subscriptions[channel].add(websocket)
            await websocket.send_json({
                "type": "subscribed",
                "channel": channel,
                "timestamp": datetime.now().isoformat()
            })
    
    async def unsubscribe(self, websocket: WebSocket, channel: str):
        """取消订阅"""
        if channel in self.subscriptions:
            self.subscriptions[channel].discard(websocket)
            await websocket.send_json({
                "type": "unsubscribed",
                "channel": channel,
                "timestamp": datetime.now().isoformat()
            })
    
    async def broadcast(self, channel: str, message: dict):
        """广播消息到频道"""
        if channel not in self.subscriptions:
            return
        
        # 添加时间戳
        message["timestamp"] = datetime.now().isoformat()
        message["channel"] = channel
        
        # 广播到订阅者
        disconnected = set()
        for connection in self.subscriptions[channel]:
            try:
                await connection.send_json(message)
            except:
                disconnected.add(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_to_all(self, message: dict):
        """广播到所有连接"""
        message["timestamp"] = datetime.now().isoformat()
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.add(connection)
        
        for conn in disconnected:
            self.disconnect(conn)


# 全局连接管理器
manager = ConnectionManager()


# WebSocket 端点
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点处理"""
    await manager.connect(websocket)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "subscribe":
                    # 订阅频道
                    channel = message.get("channel")
                    if channel:
                        await manager.subscribe(websocket, channel)
                
                elif action == "unsubscribe":
                    # 取消订阅
                    channel = message.get("channel")
                    if channel:
                        await manager.unsubscribe(websocket, channel)
                
                elif action == "ping":
                    # 心跳
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                
                else:
                    # 未知操作
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown action: {action}",
                        "timestamp": datetime.now().isoformat()
                    })
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# 事件发布函数
async def publish_agent_update(agent_id: str, status: str, data: dict = None):
    """发布 Agent 状态更新"""
    await manager.broadcast("agents", {
        "type": "agent_update",
        "agent_id": agent_id,
        "status": status,
        "data": data or {}
    })
    await manager.broadcast("all", {
        "type": "agent_update",
        "agent_id": agent_id,
        "status": status,
        "data": data or {}
    })


async def publish_cost_update(provider: str, model: str, cost: float):
    """发布成本更新"""
    await manager.broadcast("costs", {
        "type": "cost_update",
        "provider": provider,
        "model": model,
        "cost": cost
    })
    await manager.broadcast("all", {
        "type": "cost_update",
        "provider": provider,
        "model": model,
        "cost": cost
    })


async def publish_evolution_event(agent_id: str, generation: int, improvements: list):
    """发布进化事件"""
    await manager.broadcast("evolutions", {
        "type": "evolution",
        "agent_id": agent_id,
        "generation": generation,
        "improvements": improvements
    })
    await manager.broadcast("all", {
        "type": "evolution",
        "agent_id": agent_id,
        "generation": generation,
        "improvements": improvements
    })


async def publish_task_update(task_id: str, status: str, progress: float):
    """发布任务状态更新"""
    await manager.broadcast("tasks", {
        "type": "task_update",
        "task_id": task_id,
        "status": status,
        "progress": progress
    })
    await manager.broadcast("all", {
        "type": "task_update",
        "task_id": task_id,
        "status": status,
        "progress": progress
    })


# 统计信息
def get_stats() -> dict:
    """获取 WebSocket 统计信息"""
    return {
        "total_connections": len(manager.active_connections),
        "subscriptions": {
            channel: len(connections)
            for channel, connections in manager.subscriptions.items()
        }
    }
