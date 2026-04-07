"""
插件系统 - 可扩展架构
"""
import asyncio
from typing import Dict, List, Any, Optional, Callable, Type
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import importlib
import inspect
from pathlib import Path
import json


@dataclass
class PluginInfo:
    """插件信息"""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)


class PluginBase(ABC):
    """插件基类"""
    
    @property
    @abstractmethod
    def info(self) -> PluginInfo:
        """插件信息"""
        pass
    
    @abstractmethod
    async def initialize(self, context: Dict[str, Any]):
        """初始化插件"""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """关闭插件"""
        pass


class HookType:
    """钩子类型"""
    BEFORE_GENERATE = "before_generate"
    AFTER_GENERATE = "after_generate"
    BEFORE_EVALUATE = "before_evaluate"
    AFTER_EVALUATE = "after_evaluate"
    BEFORE_PLAN = "before_plan"
    AFTER_PLAN = "after_plan"
    ON_ERROR = "on_error"
    ON_SUCCESS = "on_success"


class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, PluginBase] = {}
        self.hooks: Dict[str, List[Callable]] = {
            hook: [] for hook in [
                HookType.BEFORE_GENERATE,
                HookType.AFTER_GENERATE,
                HookType.BEFORE_EVALUATE,
                HookType.AFTER_EVALUATE,
                HookType.BEFORE_PLAN,
                HookType.AFTER_PLAN,
                HookType.ON_ERROR,
                HookType.ON_SUCCESS
            ]
        }
        self.context: Dict[str, Any] = {}
    
    async def load_plugin(
        self,
        plugin_path: str,
        config: Optional[Dict] = None
    ) -> bool:
        """加载插件"""
        try:
            # 导入模块
            module = importlib.import_module(plugin_path)
            
            # 查找插件类
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj) and
                    issubclass(obj, PluginBase) and
                    obj != PluginBase
                ):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                print(f"未找到插件类: {plugin_path}")
                return False
            
            # 实例化插件
            plugin = plugin_class()
            
            # 检查是否已加载
            if plugin.info.name in self.plugins:
                print(f"插件已加载: {plugin.info.name}")
                return False
            
            # 初始化插件
            await plugin.initialize({**self.context, **(config or {})})
            
            # 注册钩子
            for hook_name in plugin.info.hooks:
                if hasattr(plugin, hook_name):
                    hook_func = getattr(plugin, hook_name)
                    self.hooks[hook_name].append(hook_func)
            
            # 保存插件
            self.plugins[plugin.info.name] = plugin
            
            print(f"✓ 插件已加载: {plugin.info.name} v{plugin.info.version}")
            return True
            
        except Exception as e:
            print(f"加载插件失败 {plugin_path}: {e}")
            return False
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        if plugin_name not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_name]
        
        # 移除钩子
        for hook_name in plugin.info.hooks:
            if hasattr(plugin, hook_name):
                hook_func = getattr(plugin, hook_name)
                if hook_func in self.hooks[hook_name]:
                    self.hooks[hook_name].remove(hook_func)
        
        # 关闭插件
        await plugin.shutdown()
        
        # 移除插件
        del self.plugins[plugin_name]
        
        print(f"✓ 插件已卸载: {plugin_name}")
        return True
    
    async def execute_hook(
        self,
        hook_type: str,
        *args,
        **kwargs
    ) -> List[Any]:
        """执行钩子"""
        if hook_type not in self.hooks:
            return []
        
        results = []
        for hook_func in self.hooks[hook_type]:
            try:
                if asyncio.iscoroutinefunction(hook_func):
                    result = await hook_func(*args, **kwargs)
                else:
                    result = hook_func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"钩子执行失败 {hook_type}: {e}")
        
        return results
    
    def set_context(self, key: str, value: Any):
        """设置上下文"""
        self.context[key] = value
    
    def get_context(self, key: str) -> Any:
        """获取上下文"""
        return self.context.get(key)
    
    def list_plugins(self) -> List[PluginInfo]:
        """列出所有插件"""
        return [plugin.info for plugin in self.plugins.values()]
    
    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """获取插件"""
        return self.plugins.get(name)


class ExamplePlugin(PluginBase):
    """示例插件"""
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="example_plugin",
            version="1.0.0",
            description="示例插件",
            author="OpenClaw",
            hooks=[
                HookType.BEFORE_GENERATE,
                HookType.AFTER_GENERATE
            ]
        )
    
    async def initialize(self, context: Dict[str, Any]):
        print(f"插件初始化: {self.info.name}")
    
    async def shutdown(self):
        print(f"插件关闭: {self.info.name}")
    
    async def before_generate(self, task: str, **kwargs):
        print(f"[Plugin] 生成前: {task}")
        return {"task": task, "enhanced": True}
    
    async def after_generate(self, code: str, **kwargs):
        print(f"[Plugin] 生成后: {len(code)} 字符")
        return {"code": code, "processed": True}


class MetricsPlugin(PluginBase):
    """指标收集插件"""
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="metrics_plugin",
            version="1.0.0",
            description="收集执行指标",
            author="OpenClaw",
            hooks=[
                HookType.AFTER_GENERATE,
                HookType.AFTER_EVALUATE,
                HookType.ON_ERROR,
                HookType.ON_SUCCESS
            ]
        )
    
    async def initialize(self, context: Dict[str, Any]):
        self.metrics = {
            "generations": 0,
            "evaluations": 0,
            "errors": 0,
            "successes": 0
        }
        print(f"指标插件已初始化")
    
    async def shutdown(self):
        print(f"指标统计: {self.metrics}")
    
    async def after_generate(self, code: str, **kwargs):
        self.metrics["generations"] += 1
        return None
    
    async def after_evaluate(self, score: float, **kwargs):
        self.metrics["evaluations"] += 1
        return None
    
    async def on_error(self, error: Exception, **kwargs):
        self.metrics["errors"] += 1
        return None
    
    async def on_success(self, result: Any, **kwargs):
        self.metrics["successes"] += 1
        return None


class PluginCLI:
    """插件管理 CLI"""
    
    def __init__(self, manager: PluginManager):
        self.manager = manager
    
    async def install(self, plugin_path: str, config_file: Optional[str] = None):
        """安装插件"""
        config = {}
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
        
        success = await self.manager.load_plugin(plugin_path, config)
        if success:
            print(f"✓ 插件安装成功: {plugin_path}")
        else:
            print(f"✗ 插件安装失败: {plugin_path}")
    
    async def uninstall(self, plugin_name: str):
        """卸载插件"""
        success = await self.manager.unload_plugin(plugin_name)
        if success:
            print(f"✓ 插件已卸载: {plugin_name}")
        else:
            print(f"✗ 插件不存在: {plugin_name}")
    
    def list(self):
        """列出所有插件"""
        plugins = self.manager.list_plugins()
        
        if not plugins:
            print("没有已安装的插件")
            return
        
        print("\n已安装的插件:")
        for plugin in plugins:
            print(f"  • {plugin.name} v{plugin.version}")
            print(f"    {plugin.description}")
            print(f"    作者: {plugin.author}")
            print()


# 插件发现器
class PluginDiscovery:
    """插件发现器"""
    
    @staticmethod
    def discover(directory: str) -> List[str]:
        """发现目录中的插件"""
        plugin_paths = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return plugin_paths
        
        # 查找包含 PluginBase 子类的模块
        for file_path in dir_path.rglob("*.py"):
            if file_path.name.startswith("_"):
                continue
            
            try:
                # 转换为模块路径
                relative = file_path.relative_to(dir_path.parent)
                module_path = str(relative.with_suffix("")).replace("/", ".")
                
                # 导入并检查
                module = importlib.import_module(module_path)
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj) and
                        issubclass(obj, PluginBase) and
                        obj != PluginBase
                    ):
                        plugin_paths.append(module_path)
                        break
            except Exception:
                continue
        
        return plugin_paths


# 便捷函数
def create_plugin_manager() -> PluginManager:
    """创建插件管理器"""
    return PluginManager()


def create_plugin_cli(manager: PluginManager) -> PluginCLI:
    """创建插件 CLI"""
    return PluginCLI(manager)
