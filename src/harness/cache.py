"""
缓存系统 - 减少重复 LLM 调用
"""
import hashlib
import json
from datetime import timedelta
from typing import Any, Optional
import redis
from core.cache import CacheBackend, MemoryCache


class CacheManager:
    """统一的缓存管理器"""
    
    def __init__(
        self,
        backend: str = "memory",
        ttl: int = 3600,
        redis_url: Optional[str] = None
    ):
        """
        初始化缓存管理器
        
        Args:
            backend: 缓存后端 ("memory" 或 "redis")
            ttl: 默认过期时间（秒）
            redis_url: Redis 连接 URL
        """
        self.ttl = ttl
        self.backend_type = backend
        
        if backend == "redis":
            if not redis_url:
                raise ValueError("Redis backend requires redis_url")
            self.backend = RedisCache(redis_url, ttl)
        else:
            self.backend = MemoryCache(ttl)
    
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        content = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def get_or_compute(
        self,
        compute_func,
        *args,
        ttl: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        获取缓存或计算新值
        
        Args:
            compute_func: 计算函数
            *args: 位置参数
            ttl: 过期时间（可选）
            **kwargs: 关键字参数
            
        Returns:
            缓存值或新计算的值
        """
        key = self._generate_key(compute_func.__name__, *args, **kwargs)
        
        # 尝试从缓存获取
        cached = await self.backend.get(key)
        if cached is not None:
            return cached
        
        # 计算新值
        if asyncio.iscoroutinefunction(compute_func):
            value = await compute_func(*args, **kwargs)
        else:
            value = compute_func(*args, **kwargs)
        
        # 存入缓存
        await self.backend.set(key, value, ttl or self.ttl)
        
        return value
    
    async def clear(self):
        """清空缓存"""
        await self.backend.clear()
    
    async def get_stats(self) -> dict:
        """获取缓存统计"""
        return await self.backend.get_stats()


class MemoryCache(CacheBackend):
    """内存缓存实现"""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache = {}
        self.default_ttl = default_ttl
        self._stats = {"hits": 0, "misses": 0}
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self.cache:
            value, expires_at = self.cache[key]
            if datetime.now() < expires_at:
                self._stats["hits"] += 1
                return value
            else:
                del self.cache[key]
        
        self._stats["misses"] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值"""
        expires_at = datetime.now() + timedelta(seconds=ttl or self.default_ttl)
        self.cache[key] = (value, expires_at)
    
    async def clear(self):
        """清空缓存"""
        self.cache.clear()
    
    async def get_stats(self) -> dict:
        """获取统计信息"""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0
        
        return {
            "backend": "memory",
            "total_keys": len(self.cache),
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate": f"{hit_rate:.2%}"
        }


class RedisCache(CacheBackend):
    """Redis 缓存实现"""
    
    def __init__(self, redis_url: str, default_ttl: int = 3600):
        self.client = redis.from_url(redis_url)
        self.default_ttl = default_ttl
        self._prefix = "harness:"
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        full_key = f"{self._prefix}{key}"
        value = self.client.get(full_key)
        
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值"""
        full_key = f"{self._prefix}{key}"
        serialized = json.dumps(value)
        self.client.setex(full_key, ttl or self.default_ttl, serialized)
    
    async def clear(self):
        """清空缓存"""
        keys = self.client.keys(f"{self._prefix}*")
        if keys:
            self.client.delete(*keys)
    
    async def get_stats(self) -> dict:
        """获取统计信息"""
        info = self.client.info()
        keys = self.client.keys(f"{self._prefix}*")
        
        return {
            "backend": "redis",
            "total_keys": len(keys),
            "used_memory": info.get("used_memory_human", "N/A"),
            "connected_clients": info.get("connected_clients", 0)
        }


# 缓存装饰器
def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    缓存装饰器
    
    Usage:
        @cached(ttl=1800, key_prefix="planner")
        async def plan_steps(self, task: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # 如果对象有 cache 属性，使用缓存
            if hasattr(self, 'cache') and isinstance(self.cache, CacheManager):
                cache_key = f"{key_prefix}:{func.__name__}"
                return await self.cache.get_or_compute(
                    func, self, *args, ttl=ttl, **kwargs
                )
            
            # 否则直接执行
            if asyncio.iscoroutinefunction(func):
                return await func(self, *args, **kwargs)
            return func(self, *args, **kwargs)
        
        return wrapper
    return decorator


import asyncio
from datetime import datetime
from functools import wraps
