"""
OpenClaw Harness Web Application
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 导入路由
from .routes import generate, progress
from .cost_dashboard import router as cost_router
from .agent_dashboard import router as agent_router
from .websocket_manager import websocket_endpoint

# 创建应用
app = FastAPI(
    title="OpenClaw Harness",
    description="AI-powered code generation and evaluation",
    version="0.4.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板
templates = Jinja2Templates(directory="templates")

# 注册路由
app.include_router(generate.router)
app.include_router(progress.router)
app.include_router(cost_router)
app.include_router(agent_router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """成本仪表板"""
    return templates.TemplateResponse("cost_dashboard.html", {"request": request})


@app.get("/agents", response_class=HTMLResponse)
async def agents_dashboard(request: Request):
    """Agent 协作仪表板"""
    return templates.TemplateResponse("agent_dashboard.html", {"request": request})


@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    """WebSocket 实时通信"""
    await websocket_endpoint(websocket)


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "version": "0.4.0"}


def run():
    """运行 Web 服务"""
    uvicorn.run(
        "harness.web.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    run()
