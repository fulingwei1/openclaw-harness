# OpenClaw Harness - 使用指南

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/fulingwei1/openclaw-harness.git
cd openclaw-harness

# 安装依赖
poetry install

# 设置开发环境
make setup-hooks
```

### 2. CLI 使用

```bash
# 初始化
poetry run harness init

# 运行任务
poetry run harness run "创建一个 REST API"

# 查看历史
poetry run harness history

# 评估代码
poetry run harness evaluate ./my_code.py
```

### 3. Web UI

```bash
# 启动 Web 界面
make web

# 或使用开发模式
make web-dev

# 访问 http://localhost:8000
```

## 📊 功能特性

### 缓存系统

自动缓存 LLM 响应，减少重复调用：

```python
from harness.cache import CacheManager
from harness.llm import LLMClient

# 初始化缓存
cache = CacheManager(backend="memory", ttl=3600)
# 或使用 Redis
# cache = CacheManager(backend="redis", redis_url="redis://localhost:6379")

# LLM 客户端使用缓存
llm = LLMClient(cache=cache)
```

### 进度追踪

实时追踪任务执行：

```python
from harness.progress import create_tracker

# 创建追踪器
tracker = create_tracker([
    "任务规划",
    "代码生成", 
    "评估验证",
    "优化改进"
])

# 开始步骤
await tracker.start_step("step_0", "开始规划...")
await tracker.update_step("step_0", 50, "生成步骤中...")
await tracker.complete_step("step_0", "规划完成")
```

### 多 LLM 提供商

支持多种 LLM：

```python
from harness.llm_providers import (
    OpenAIProvider,
    AnthropicProvider,
    ZaiProvider,
    KimiProvider
)

# OpenAI
openai = OpenAIProvider(api_key="sk-...")

# Anthropic Claude
claude = AnthropicProvider(api_key="sk-ant-...")

# z.ai GLM
glm = ZaiProvider(api_key="...")

# Kimi
kimi = KimiProvider(api_key="...")
```

## 🧪 测试

```bash
# 运行所有测试
make test

# 带覆盖率
make test-cov

# 特定测试
poetry run pytest tests/test_planner.py -v
```

## 🐳 Docker 部署

```bash
# 构建镜像
make docker-build

# 运行容器
make docker-run

# 或手动
docker build -t openclaw-harness .
docker run -p 8000:8000 openclaw-harness
```

## ⚙️ 配置

### 环境变量

创建 `.env` 文件：

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# z.ai
ZAI_API_KEY=...
ZAI_MODEL=glm-4

# Kimi
KIMI_API_KEY=...

# Redis（可选）
REDIS_URL=redis://localhost:6379

# 日志级别
LOG_LEVEL=INFO
```

### 配置文件

```python
from harness.config import HarnessConfig, LLMConfig

config = HarnessConfig(
    llm=LLMConfig(
        provider="openai",
        model="gpt-4",
        temperature=0.7
    ),
    cache_ttl=3600,
    log_level="INFO"
)
```

## 🔧 高级用法

### 异步执行

```python
import asyncio
from harness import HarnessEngine

async def main():
    engine = HarnessEngine()
    result = await engine.run("创建 API")
    print(result)

asyncio.run(main())
```

### 自定义评估器

```python
from harness.evaluator import Evaluator
from harness.models import EvaluationResult

class MyEvaluator(Evaluator):
    async def evaluate(self, code: str, task: str) -> EvaluationResult:
        # 自定义评估逻辑
        score = self._calculate_score(code)
        return EvaluationResult(
            score=score,
            passed=score >= 0.9,
            feedback="..."
        )
```

### Webhook 集成

```python
from harness.progress import ProgressTracker

tracker = ProgressTracker()

async def send_to_webhook(event, step, progress):
    # 发送到 Slack/Discord/自定义
    await webhook.send(progress)

tracker.on_progress(send_to_webhook)
```

## 📈 性能优化

### 1. 启用缓存

```bash
# Redis 缓存
REDIS_URL=redis://localhost:6379 poetry run harness run "任务"
```

### 2. 并行执行

```python
# 并行运行多个任务
results = await asyncio.gather(
    engine.run("任务1"),
    engine.run("任务2"),
    engine.run("任务3")
)
```

### 3. 批量处理

```python
tasks = ["任务1", "任务2", "任务3"]
results = await engine.batch_run(tasks)
```

## 🐛 故障排除

### 测试失败

```bash
# 清理缓存
make clean

# 重新安装
poetry install

# 检查依赖
poetry show --tree
```

### LLM 连接问题

```bash
# 检查 API Key
poetry run python -c "from harness.config import HarnessConfig; c = HarnessConfig(); print(c.llm)"

# 测试连接
poetry run harness test-connection
```

## 📚 更多资源

- [API 文档](http://localhost:8000/docs)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)
- [GitHub Issues](https://github.com/fulingwei1/openclaw-harness/issues)

## 💬 获取帮助

```bash
# CLI 帮助
poetry run harness --help

# Makefile 帮助
make help
```

---

**Happy Coding! 🎉**
