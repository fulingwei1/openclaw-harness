#!/usr/bin/env python3
"""
启动 Web UI
"""
import uvicorn
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.web.api import app
from harness.web.routes import router


# 注册路由
app.include_router(router, prefix="/api")


def main():
    """启动服务"""
    print("""
    ╔═══════════════════════════════════════╗
    ║   🚀 OpenClaw Harness Web UI          ║
    ╚═══════════════════════════════════════╝
    
    服务地址: http://localhost:8000
    API 文档: http://localhost:8000/docs
    
    按 Ctrl+C 停止服务
    """)
    
    uvicorn.run(
        "run_web:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
