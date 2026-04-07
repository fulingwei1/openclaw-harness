# OpenClaw Harness 部署指南

## 环境要求

- Python 3.10+
- Poetry（推荐）或 pip
- OpenAI API Key 或 Anthropic API Key

## 本地安装

### 方式一：从 GitHub 安装

```bash
# 克隆仓库
git clone https://github.com/fulingwei1/openclaw-harness.git
cd openclaw-harness

# 使用 Poetry 安装
poetry install

# 或者使用 pip
pip install -e .
```

### 方式二：直接安装（发布后）

```bash
pip install openclaw-harness
```

## 配置

### 1. 设置 API Key

```bash
# OpenAI
export OPENAI_API_KEY="your-key-here"

# 或 Anthropic
export ANTHROPIC_API_KEY="your-key-here"
```

### 2. 初始化项目

```bash
# 在项目目录下初始化
harness init

# 这会创建 .harness/ 目录结构：
# .harness/
# ├── state/          # 状态文件
# ├── golden_rules/   # 黄金法则
# ├── skills/         # 自动提取的技能
# └── logs/           # 评估日志
```

## 使用

### 基本命令

```bash
# 查看帮助
harness --help

# 运行任务
harness run "Build a REST API for todos"

# 添加黄金法则
harness add-rule "所有输出必须使用中文"

# 列出规则
harness list-rules

# 查看状态
harness status
```

### 示例：创建 API 项目

```bash
# 初始化
harness init

# 添加领域规则
harness add-rule "使用 FastAPI 框架" --category domain
harness add-rule "必须包含单元测试" --category domain

# 运行任务
harness run "创建一个用户管理 API，包含注册、登录、查询功能"
```

## 与 OpenClaw 集成

### 作为 OpenClaw 技能使用

将 `openclaw-harness` 作为技能安装到 OpenClaw：

```bash
# 创建技能目录
mkdir -p ~/.openclaw/skills/harness-engineering

# 复制技能文件
cp -r ~/Projects/openclaw-harness/templates/* ~/.openclaw/skills/harness-engineering/

# 创建 SKILL.md
cat > ~/.openclaw/skills/harness-engineering/SKILL.md << 'EOF'
---
description: 使用 Harness Engineering 方法执行复杂任务，包括自动规划、生成、评估闭环
---

# Harness Engineering 技能

使用 Harness Engineering 方法执行任务。

## 触发条件

- 用户要求"用 Harness 方式"执行任务
- 复杂的编程任务
- 需要多次迭代的任务

## 使用方式

1. Planner 拆解任务
2. Generator 执行步骤
3. Evaluator 评估结果
4. 不通过则修正重试
5. 复杂任务自动提取技能
EOF
```

### 在 OpenClaw 中调用

在 OpenClaw 对话中：

```
用 Harness 方式帮我创建一个 REST API
```

OpenClaw 会自动加载这个技能并使用 Harness 流程执行。

## Docker 部署（可选）

```bash
# 构建 Docker 镜像
docker build -t openclaw-harness .

# 运行容器
docker run -it --rm \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/.harness:/app/.harness \
  openclaw-harness harness run "Your task"
```

## 进阶配置

### 自定义评估器

编辑 `.harness/golden_rules/rules.yaml`：

```yaml
- id: rule_1
  content: "所有输出必须使用中文"
  category: "global"
  priority: 5

- id: rule_2
  content: "代码必须有清晰注释"
  category: "domain"
  priority: 4
```

### 调整评估阈值

```bash
# 设置通过阈值为 0.9
harness run --threshold 0.9 "Your task"
```

## 常见问题

### Q: 技能提取失败？

确保任务评分 >= 0.8 且通过了评估。

### Q: 评估一直不通过？

检查黄金法则是否过于严格，可以降低优先级或删除部分规则。

### Q: 如何查看评估日志？

```bash
cat .harness/logs/evaluation_*.md
```

## License

MIT
