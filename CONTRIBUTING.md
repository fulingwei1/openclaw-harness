# Contributing to OpenClaw Harness

感谢你考虑为 OpenClaw Harness 做贡献！

## 开发环境设置

### 1. Fork 并克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/openclaw-harness.git
cd openclaw-harness
```

### 2. 安装开发依赖

```bash
# 安装 Poetry（如果还没有）
curl -ssl https://install.python-poetry.org | python3 -

# 安装项目依赖
poetry install

# 设置 pre-commit hooks
poetry run pre-commit install
```

### 3. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

## 代码规范

### 代码风格

- 使用 **Black** 格式化代码
- 使用 **isort** 排序 imports
- 遵循 **PEP 8** 规范
- 使用类型注解

### 运行检查

```bash
# 格式化代码
make format

# 检查代码
make lint

# 运行测试
make test
```

## 测试

### 运行测试

```bash
# 运行所有测试
poetry run pytest

# 运行带覆盖率的测试
poetry run pytest --cov=harness --cov-report=html

# 运行特定测试
poetry run pytest tests/test_planner.py -v
```

### 编写测试

- 为新功能编写测试
- 保持测试覆盖率 > 80%
- 使用 pytest fixtures
- Mock 外部依赖

## 提交代码

### Commit 消息格式

使用 [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(planner): 支持自定义规划策略

- 添加策略配置选项
- 支持策略切换
- 添加单元测试

Closes #123
```

### 提交前检查

```bash
# 运行所有检查
make ci-test
```

## Pull Request 流程

1. **Fork** 仓库并创建分支
2. **编写代码** 和测试
3. **确保通过** 所有测试和检查
4. **提交 PR**，填写完整的 PR 模板
5. **等待审核**，及时响应反馈

### PR 模板

```markdown
## 描述
[描述你的更改]

## 类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 重构
- [ ] 文档更新
- [ ] 其他

## 测试
[描述如何测试这些更改]

## Checklist
- [ ] 代码通过所有测试
- [ ] 更新了相关文档
- [ ] 遵循代码规范
```

## 项目结构

```
openclaw-harness/
├── src/harness/          # 源代码
│   ├── cli/              # CLI 工具
│   ├── models.py         # 数据模型
│   ├── planner.py        # 规划器
│   ├── generator.py      # 生成器
│   ├── evaluator.py      # 评估器
│   └── ...
├── tests/                # 测试
├── docs/                 # 文档
├── templates/            # 模板
└── .github/              # GitHub 配置
```

## 添加新的 LLM 提供商

1. 在 `src/harness/llm_providers.py` 添加适配器
2. 实现 `LLMAdapter` 接口
3. 添加测试
4. 更新文档

## 问题和建议

- **Bug 报告**: 使用 GitHub Issues
- **功能建议**: 使用 GitHub Discussions
- **安全问题**: 私下联系维护者

## 许可证

提交代码即表示你同意你的代码将在 MIT 许可证下发布。

---

再次感谢你的贡献！🎉
