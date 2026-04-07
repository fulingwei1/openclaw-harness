"""
Web 模块初始化
"""
from .api import app
from .routes import router


__all__ = ["app", "router"]
