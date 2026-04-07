# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - v0.2.0 (2026-04-08)

#### 🚀 Performance & UX Enhancements

- **Cache System** - Redis and memory-based caching to reduce LLM costs
  - Automatic response caching with configurable TTL
  - Support for both memory and Redis backends
  - `@cached` decorator for easy function caching
  - Cache statistics and management API

- **Real-time Progress Tracking** - WebSocket-based progress updates
  - Step-by-step progress visualization
  - Progress callbacks and webhooks
  - Rich-based terminal UI
  - JSON export for integration

- **Web UI** - FastAPI-based web interface
  - Real-time progress dashboard
  - WebSocket live updates
  - Beautiful gradient design
  - Task management interface

- **Async Support** - Full async/await implementation
  - Async LLM clients
  - Concurrent task execution
  - Background task processing

#### 🔧 Infrastructure

- **Docker Support** - Containerized deployment
  - Multi-stage Dockerfile
  - Optimized for production
  - Easy deployment with `make docker-run`

- **Enhanced Configuration** - Pydantic-based config
  - Type-safe configuration models
  - Environment variable support
  - Validation and defaults

- **Structured Logging** - Rich-based logging system
  - Colored console output
  - File logging support
  - Configurable log levels

#### 📚 Documentation

- **Advanced Features Guide** - Comprehensive usage documentation
- **API Documentation** - Auto-generated FastAPI docs
- **Docker Guide** - Container deployment instructions
- **Performance Tips** - Optimization recommendations

### Added - v0.1.0 (2026-04-07)

#### 🎯 Core Features

- **Harness Engineering Framework**
  - Planner: Task decomposition
  - Generator: Code generation
  - Evaluator: Quality assessment
  - Golden Rules: Best practices enforcement

- **CLI Interface** - Click-based command line tool
  - `harness init` - Initialize project
  - `harness run` - Execute tasks
  - `harness history` - View execution history
  - `harness evaluate` - Evaluate code

- **Multi-LLM Support**
  - OpenAI GPT-4/3.5
  - Anthropic Claude
  - z.ai GLM-4
  - Kimi/Moonshot
  - MiniMax

- **Testing Framework**
  - pytest with 80%+ coverage
  - Async test support
  - Fixtures and mocks

- **CI/CD Pipeline**
  - GitHub Actions workflow
  - Multi-version testing (3.10-3.12)
  - Automatic coverage reports
  - Code quality checks

- **Code Quality Tools**
  - Pre-commit hooks
  - Black formatting
  - isort import sorting
  - flake8 linting
  - mypy type checking

- **Exception Handling**
  - Custom exception hierarchy
  - Retry mechanism
  - Detailed error messages

- **Makefile** - Simplified development workflow
  - `make test` - Run tests
  - `make lint` - Code checks
  - `make format` - Format code
  - `make ci-test` - Full CI pipeline

## [0.1.0] - 2026-04-07

### Added
- Initial release
- Core harness engineering framework
- CLI interface
- Multi-LLM support
- Testing infrastructure
- CI/CD pipeline

---

## Future Plans

### v0.3.0 (Planned)

- **LangChain Integration** - Chain-based workflows
- **Vector Search** - Embedding-based code search
- **Plugin System** - Extensible architecture
- **Multi-language Support** - Beyond Python

### v0.4.0 (Planned)

- **VS Code Extension** - IDE integration
- **Jupyter Notebooks** - Interactive execution
- **Team Collaboration** - Shared workspaces
- **Cost Tracking** - LLM usage analytics

### v1.0.0 (Planned)

- **Production Ready** - Battle-tested stability
- **Enterprise Features** - SSO, audit logs
- **Cloud Deployment** - One-click deploy
- **SLA Guarantees** - 99.9% uptime

---

**Full Changelog**: https://github.com/fulingwei1/openclaw-harness/commits/main
