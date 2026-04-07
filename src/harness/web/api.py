"""
Web UI - FastAPI 服务
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import json
from datetime import datetime


app = FastAPI(
    title="OpenClaw Harness",
    description="Harness Engineering 可视化界面",
    version="0.1.0"
)

# WebSocket 连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()

# 任务管理
tasks_db: Dict[str, Dict[str, Any]] = {}


class TaskRequest(BaseModel):
    """任务请求"""
    task: str
    max_steps: Optional[int] = 10
    evaluator_threshold: Optional[float] = 0.9


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    status: str
    message: str


@app.get("/", response_class=HTMLResponse)
async def home():
    """主页"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenClaw Harness</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            .header {
                background: #1a1a2e;
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                opacity: 0.8;
            }
            .content {
                padding: 40px;
            }
            .input-section {
                margin-bottom: 30px;
            }
            textarea {
                width: 100%;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                resize: vertical;
                min-height: 120px;
            }
            textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            .button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 40px;
                font-size: 18px;
                border-radius: 8px;
                cursor: pointer;
                transition: transform 0.2s;
            }
            .button:hover {
                transform: translateY(-2px);
            }
            .button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }
            .progress-section {
                margin-top: 30px;
                display: none;
            }
            .progress-bar {
                height: 30px;
                background: #f0f0f0;
                border-radius: 15px;
                overflow: hidden;
                margin-bottom: 20px;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                transition: width 0.3s;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
            }
            .steps {
                border-left: 3px solid #e0e0e0;
                padding-left: 20px;
            }
            .step {
                margin: 15px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
                position: relative;
            }
            .step::before {
                content: '';
                position: absolute;
                left: -27px;
                top: 50%;
                transform: translateY(-50%);
                width: 12px;
                height: 12px;
                background: #667eea;
                border-radius: 50%;
            }
            .step.running::before {
                animation: pulse 1s infinite;
            }
            .step.completed::before {
                background: #28a745;
            }
            .step.failed::before {
                background: #dc3545;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .step-name {
                font-weight: bold;
                margin-bottom: 5px;
            }
            .step-message {
                color: #666;
                font-size: 14px;
            }
            .step-progress {
                margin-top: 8px;
                height: 6px;
                background: #e0e0e0;
                border-radius: 3px;
            }
            .step-progress-fill {
                height: 100%;
                background: #667eea;
                transition: width 0.3s;
            }
            .status {
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 20px;
                font-weight: bold;
            }
            .status.running {
                background: #fff3cd;
                color: #856404;
            }
            .status.completed {
                background: #d4edda;
                color: #155724;
            }
            .status.failed {
                background: #f8d7da;
                color: #721c24;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 OpenClaw Harness</h1>
                <p>Harness Engineering 可视化执行平台</p>
            </div>
            
            <div class="content">
                <div class="input-section">
                    <h2>任务描述</h2>
                    <p style="margin-bottom: 15px; color: #666;">
                        描述你要完成的任务，Harness 会自动分解、执行并优化
                    </p>
                    <textarea id="taskInput" placeholder="例如：创建一个 FastAPI 项目，包含用户认证和数据库连接"></textarea>
                    <br><br>
                    <button class="button" onclick="startTask()">开始执行</button>
                </div>
                
                <div id="progressSection" class="progress-section">
                    <div id="status" class="status running">⏳ 执行中...</div>
                    
                    <h3>总体进度</h3>
                    <div class="progress-bar">
                        <div id="totalProgress" class="progress-fill" style="width: 0%">0%</div>
                    </div>
                    
                    <h3>执行步骤</h3>
                    <div id="steps" class="steps"></div>
                </div>
            </div>
        </div>
        
        <script>
            let ws;
            let taskId;
            
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    handleUpdate(data);
                };
                
                ws.onclose = () => {
                    console.log('WebSocket disconnected');
                };
            }
            
            async function startTask() {
                const task = document.getElementById('taskInput').value;
                if (!task.trim()) {
                    alert('请输入任务描述');
                    return;
                }
                
                const button = document.querySelector('.button');
                button.disabled = true;
                button.textContent = '执行中...';
                
                document.getElementById('progressSection').style.display = 'block';
                document.getElementById('steps').innerHTML = '';
                
                connectWebSocket();
                
                try {
                    const response = await fetch('/api/tasks', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({task})
                    });
                    
                    const result = await response.json();
                    taskId = result.task_id;
                    
                    ws.send(JSON.stringify({type: 'subscribe', task_id: taskId}));
                    
                } catch (error) {
                    alert('启动失败: ' + error.message);
                    button.disabled = false;
                    button.textContent = '开始执行';
                }
            }
            
            function handleUpdate(data) {
                if (data.event === 'progress') {
                    updateProgress(data.progress);
                } else if (data.event === 'completed') {
                    showCompletion(data.result);
                } else if (data.event === 'failed') {
                    showFailure(data.error);
                }
            }
            
            function updateProgress(progress) {
                // 更新总进度
                const totalProgress = document.getElementById('totalProgress');
                totalProgress.style.width = progress.total_progress + '%';
                totalProgress.textContent = progress.total_progress.toFixed(1) + '%';
                
                // 更新步骤
                const stepsDiv = document.getElementById('steps');
                stepsDiv.innerHTML = '';
                
                progress.steps.forEach(step => {
                    const stepDiv = document.createElement('div');
                    stepDiv.className = `step ${step.status}`;
                    stepDiv.innerHTML = `
                        <div class="step-name">${step.name}</div>
                        <div class="step-message">${step.message || ''}</div>
                        <div class="step-progress">
                            <div class="step-progress-fill" style="width: ${step.progress}%"></div>
                        </div>
                    `;
                    stepsDiv.appendChild(stepDiv);
                });
            }
            
            function showCompletion(result) {
                const status = document.getElementById('status');
                status.className = 'status completed';
                status.textContent = '✅ 执行完成！';
                
                const button = document.querySelector('.button');
                button.disabled = false;
                button.textContent = '开始执行';
            }
            
            function showFailure(error) {
                const status = document.getElementById('status');
                status.className = 'status failed';
                status.textContent = '❌ 执行失败: ' + error;
                
                const button = document.querySelector('.button');
                button.disabled = false;
                button.textContent = '开始执行';
            }
        </script>
    </body>
    </html>
    """
