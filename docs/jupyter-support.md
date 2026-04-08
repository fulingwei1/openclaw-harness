# Harness Jupyter Notebook 支持

## 安装

```bash
# 安装 Harness
pip install openclaw-harness

# 安装 Jupyter 扩展
jupyter nbextension install --py harness.jupyter_extension
jupyter nbextension enable --py harness.jupyter_extension
```

## 快速开始

### 1. 初始化

```python
%load_ext harness.jupyter_extension
%harness_init
```

### 2. 生成代码

```python
%%harness_generate
创建一个 REST API，包含用户 CRUD 操作
```

### 3. 评估代码

```python
%%harness_evaluate
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### 4. 查看成本

```python
%harness_cost
```

### 5. 查看 Agent 状态

```python
%harness_agents
```

### 6. 绘制图表

```python
%harness_plot
```

## 配置选项

```python
# 设置输出格式
%harness_config output=html  # html, json, text

# 设置模型
%harness_config model=gpt-4
```

## 魔法命令

| 命令 | 类型 | 说明 |
|------|------|------|
| `%harness_init` | Line | 初始化 Harness |
| `%harness_config` | Line | 配置参数 |
| `%%harness_generate` | Cell | 生成代码 |
| `%%harness_evaluate` | Cell | 评估代码 |
| `%harness_cost` | Line | 查看成本统计 |
| `%harness_agents` | Line | 查看 Agent 状态 |
| `%harness_plot` | Line | 绘制成本图表 |

## 示例工作流

### 示例 1：API 开发

```python
# 初始化
%load_ext harness.jupyter_extension
%harness_init
%harness_config model=gpt-4

# 生成 API 代码
%%harness_generate
创建一个 FastAPI 应用，包含：
- 用户注册/登录
- JWT 认证
- CRUD 操作
- 数据库连接（PostgreSQL）

# 查看成本
%harness_cost
```

### 示例 2：代码评估

```python
# 评估代码质量
%%harness_evaluate
import pandas as pd

def process_data(filepath):
    df = pd.read_csv(filepath)
    df = df.dropna()
    df['date'] = pd.to_datetime(df['date'])
    return df.groupby('category').sum()

# 查看评估结果和改进建议
```

### 示例 3：数据分析

```python
# 初始化
%load_ext harness.jupyter_extension
%harness_init

# 生成分析代码
%%harness_generate
分析销售数据：
1. 数据清洗
2. 统计摘要
3. 可视化（matplotlib/seaborn）
4. 生成报告

# 绘制成本图表
%harness_plot
```

## 高级用法

### 自定义模板

```python
from harness import HarnessEngine

engine = HarnessEngine()

# 自定义生成
result = await engine.run(
    "创建 API",
    template="fastapi_crud",
    language="python"
)
```

### 批量操作

```python
tasks = [
    "创建用户模型",
    "创建订单模型",
    "创建产品模型"
]

for task in tasks:
    %%harness_generate
    {task}
```

### 与 Agent 协作

```python
# 查看 Agent 状态
%harness_agents

# 创建新 Agent
from harness.web.agent_dashboard import orchestrator

orchestrator.register_agent(
    "agent_data_analyst",
    "Data Analyst",
    "analyzer"
)
```

## 可视化输出

### HTML 格式（默认）

- 卡片式布局
- 代码高亮
- 评估分数
- 成本追踪

### JSON 格式

```python
%harness_config output=json
```

返回原始 JSON 数据，便于程序处理。

### 文本格式

```python
%harness_config output=text
```

纯文本输出，适合日志记录。

## 成本追踪

所有操作自动追踪成本：

```python
# 查看成本
%harness_cost

# 绘制图表
%harness_plot  # 需要 plotly
```

## 性能优化

### 缓存

Harness 自动缓存结果，避免重复调用 LLM。

### 并发

```python
import asyncio
from harness import HarnessEngine

engine = HarnessEngine()

# 并发生成
tasks = ["任务1", "任务2", "任务3"]
results = await asyncio.gather(*[
    engine.run(task) for task in tasks
])
```

## 故障排查

### 扩展未加载

```python
# 手动加载
import harness.jupyter_extension
harness.jupyter_extension.load_ipython_extension(get_ipython())
```

### 连接错误

检查 `.env` 配置：

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## 最佳实践

1. **使用配置文件** - 统一管理参数
2. **定期查看成本** - 使用 `%harness_cost`
3. **评估生成代码** - 使用 `%%harness_evaluate`
4. **利用缓存** - 避免重复生成
5. **Agent 协作** - 分工合作提高效率

## 资源

- 文档: https://github.com/fulingwei1/openclaw-harness
- 示例: https://github.com/fulingwei1/openclaw-harness/tree/main/examples
- 问题反馈: https://github.com/fulingwei1/openclaw-harness/issues
