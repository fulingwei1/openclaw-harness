"""
API 路由
"""
from fastapi import APIRouter, HTTPException, WebSocket
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import asyncio
from datetime import datetime
from ..progress import ProgressTracker, StepStatus
from ..planner import Planner
from ..evaluator import Evaluator
from ..generator import Generator
from ..llm import LLMClient


router = APIRouter()


class TaskCreate(BaseModel):
    """创建任务请求"""
    task: str
    max_steps: Optional[int] = 10
    evaluator_threshold: Optional[float] = 0.9


class TaskInfo(BaseModel):
    """任务信息"""
    task_id: str
    task: str
    status: str
    progress: float
    created_at: str
    updated_at: str


# 任务存储
tasks_db: Dict[str, Dict[str, Any]] = {}
progress_trackers: Dict[str, ProgressTracker] = {}


@router.post("/tasks", response_model=TaskInfo)
async def create_task(request: TaskCreate):
    """创建新任务"""
    task_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    task_data = {
        "task_id": task_id,
        "task": request.task,
        "status": "pending",
        "progress": 0.0,
        "created_at": now,
        "updated_at": now,
        "config": {
            "max_steps": request.max_steps,
            "evaluator_threshold": request.evaluator_threshold
        }
    }
    
    tasks_db[task_id] = task_data
    
    # 创建进度追踪器
    tracker = ProgressTracker()
    progress_trackers[task_id] = tracker
    
    # 启动后台任务
    asyncio.create_task(run_harness(task_id, request))
    
    return TaskInfo(**task_data)


@router.get("/tasks/{task_id}", response_model=TaskInfo)
async def get_task(task_id: str):
    """获取任务信息"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskInfo(**tasks_db[task_id])


@router.get("/tasks/{task_id}/progress")
async def get_task_progress(task_id: str):
    """获取任务进度"""
    if task_id not in progress_trackers:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return progress_trackers[task_id].get_progress()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 连接"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "subscribe":
                task_id = data.get("task_id")
                
                if task_id in progress_trackers:
                    tracker = progress_trackers[task_id]
                    
                    # 注册回调
                    async def send_progress(event, step, progress):
                        await websocket.send_json({
                            "event": "progress",
                            "progress": progress
                        })
                    
                    tracker.on_progress(send_progress)
                    
                    # 发送初始状态
                    await websocket.send_json({
                        "event": "progress",
                        "progress": tracker.get_progress()
                    })
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


async def run_harness(task_id: str, request: TaskCreate):
    """后台执行 Harness"""
    task_data = tasks_db[task_id]
    tracker = progress_trackers[task_id]
    
    try:
        # 更新状态
        task_data["status"] = "running"
        task_data["updated_at"] = datetime.now().isoformat()
        
        # 初始化组件
        llm_client = LLMClient()
        planner = Planner(llm_client)
        evaluator = Evaluator(llm_client)
        generator = Generator(llm_client)
        
        # 添加步骤
        tracker.add_step("step_0", "任务规划")
        tracker.add_step("step_1", "代码生成")
        tracker.add_step("step_2", "评估验证")
        tracker.add_step("step_3", "优化改进")
        tracker.add_step("step_4", "最终确认")
        
        # 1. 规划
        await tracker.start_step("step_0", "正在分解任务...")
        steps = await planner.plan(request.task)
        await tracker.update_step("step_0", 50, f"生成 {len(steps)} 个步骤")
        await tracker.complete_step("step_0", f"规划完成，共 {len(steps)} 步")
        
        # 2. 生成
        await tracker.start_step("step_1", "开始生成代码...")
        code = await generator.generate(request.task, steps)
        await tracker.update_step("step_1", 50, "代码生成中...")
        await tracker.complete_step("step_1", "代码生成完成")
        
        # 3. 评估
        await tracker.start_step("step_2", "开始评估...")
        score = await evaluator.evaluate(code, request.task)
        await tracker.update_step("step_2", 50, f"得分: {score:.2f}")
        
        if score >= request.evaluator_threshold:
            await tracker.complete_step("step_2", f"评估通过，得分: {score:.2f}")
            await tracker.skip_step("step_3", "评估通过，无需优化")
        else:
            await tracker.complete_step("step_2", f"评估得分: {score:.2f}，需要优化")
            
            # 4. 优化
            await tracker.start_step("step_3", "开始优化...")
            improved_code = await generator.improve(code, score)
            await tracker.update_step("step_3", 50, "优化中...")
            await tracker.complete_step("step_3", "优化完成")
        
        # 5. 完成
        await tracker.start_step("step_4", "最终确认...")
        await asyncio.sleep(0.5)  # 模拟最后检查
        await tracker.complete_step("step_4", "任务完成")
        
        # 更新任务状态
        task_data["status"] = "completed"
        task_data["progress"] = 100.0
        task_data["updated_at"] = datetime.now().isoformat()
        task_data["result"] = {
            "steps": [s.to_dict() for s in tracker.steps],
            "final_score": score if 'score' in locals() else 0.0
        }
        
    except Exception as e:
        # 失败处理
        task_data["status"] = "failed"
        task_data["updated_at"] = datetime.now().isoformat()
        task_data["error"] = str(e)
        
        # 标记当前步骤为失败
        if tracker.current_step:
            await tracker.fail_step(
                tracker.current_step.step_id,
                str(e)
            )


@router.get("/tasks")
async def list_tasks():
    """列出所有任务"""
    return {
        "tasks": list(tasks_db.values()),
        "total": len(tasks_db)
    }


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del tasks_db[task_id]
    if task_id in progress_trackers:
        del progress_trackers[task_id]
    
    return {"message": "Task deleted"}
