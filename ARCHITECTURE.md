# OpenClaw Harness Architecture

## 设计理念

基于 Harness Engineering 的核心思想：
- **Prompt Engineering** → 说什么
- **Context Engineering** → 给它看什么  
- **Harness Engineering** → 在什么系统里跑

## 核心模块

### 1. 三智能体闭环 (Tri-Agent Loop)

```
┌─────────┐     ┌───────────┐     ┌───────────┐
│ Planner │ --> │ Generator │ --> │ Evaluator │
└─────────┘     └───────────┘     └───────────┘
      ↑                                    │
      └────────────────────────────────────┘
                   (修正循环)
```

**Planner**: 拆解任务，生成执行计划
**Generator**: 执行具体任务，产出内容
**Evaluator**: 评估结果，发现问题，触发修正

### 2. 自动技能提取器 (Skill Extractor)

复杂任务完成后：
1. 分析任务执行过程
2. 提取可复用模式
3. 生成 SKILL.md 模板
4. 自动写入 description（用于触发匹配）

### 3. 黄金法则系统 (Golden Rules)

标准化的约束文档：
- `GOLDEN_RULES.md` - 全局约束
- `DOMAIN_RULES.md` - 领域特定约束
- `OUTPUT_FORMATS.md` - 输出格式规范

### 4. 状态外部化 (State Externalization)

```
project/
├── .harness/
│   ├── state/
│   │   ├── current_task.md      # 当前任务状态
│   │   ├── progress.md          # 进度追踪
│   │   └── checkpoint_*.md      # 检查点
│   ├── golden_rules/
│   │   ├── global.md
│   │   └── domain.md
│   ├── skills/
│   │   └── auto_extracted/
│   └── logs/
│       └── evaluation_*.md
```

## 工作流程

### 标准任务流程

```python
task = "Build a REST API for todos"

# 1. Planner 拆解
plan = planner.decompose(task)
# Output: Step-by-step plan

# 2. Generator 执行
result = generator.execute(plan)

# 3. Evaluator 评估
evaluation = evaluator.evaluate(result)

# 4. 修正循环 (如果需要)
while not evaluation.passed:
    corrections = evaluation.issues
    result = generator.fix(result, corrections)
    evaluation = evaluator.evaluate(result)

# 5. 技能提取 (如果是复杂任务)
if task.is_complex:
    skill = skill_extractor.extract(task, result)
    skill.save()
```

### 技能提取流程

```python
# 从完成的任务中提取技能
skill_extractor.extract(
    task_description="...",
    execution_trace=[...],
    final_result="...",
    success_metrics={...}
)

# 生成 SKILL.md
# - description: 基于任务模式自动生成（用于触发匹配）
# - steps: 提取的标准流程
# - checkpoints: 关键检查点
# - examples: 成功案例
```

## 与 OpenClaw 集成

### 作为 OpenClaw 技能

```
~/.openclaw/skills/harness-engineering/
├── SKILL.md              # 主技能描述
├── templates/
│   ├── golden_rules.md   # 黄金法则模板
│   └── skill_template.md # 技能模板
└── scripts/
    ├── extract_skill.py  # 技能提取脚本
    └── evaluate.py       # 评估脚本
```

### CLI 工具

```bash
# 初始化 Harness
harness init

# 运行任务（自动闭环）
harness run "Build a REST API"

# 提取技能
harness extract-skill --from-task .harness/state/current_task.md

# 添加黄金法则
harness add-rule "All output must be in Chinese"

# 评估结果
harness evaluate .harness/output/result.md
```

## 技术栈

- **Python 3.10+** - 核心实现
- **Pydantic** - 数据模型
- **Jinja2** - 模板系统
- **Click** - CLI 框架
- **OpenAI/Anthropic API** - LLM 调用

## 设计原则

1. **外部化一切状态** - 不依赖模型记忆
2. **强制闭环验证** - 生成后必须评估
3. **自动沉淀技能** - 复杂任务后自动提取
4. **可观测性优先** - 所有决策可追溯
5. **渐进式约束** - 黄金法则持续积累
