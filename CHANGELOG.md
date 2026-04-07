# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - v0.6.0 (2026-04-08)

#### 🤖 Agent Collaboration Dashboard

- **Agent Orchestration** - Real-time monitoring
  - Agent status tracking
  - Task assignment
  - Performance metrics
  - Activity logging

- **Collaboration Network** - Visual network graph
  - Interactive D3.js visualization
  - Node size = activity level
  - Edge weight = collaboration frequency
  - Drag and zoom support

- **Evolution Tracking** - Agent learning progress
  - Evolution history
  - Generation tracking
  - Performance improvements
  - Improvement details

- **Performance Analytics** - Visual analytics
  - Agent performance comparison
  - Evolution trend
  - Collaboration matrix
  - Efficiency metrics

- **Dashboard Features**
  - Overview cards (total agents, active, collaborations, evolutions)
  - Agent status list with performance bars
  - Real-time activity feed
  - Auto-refresh (5 seconds)
  - Modern responsive design

- **API Endpoints**
  - `GET /api/agents/overview` - Overview stats
  - `GET /api/agents/agents` - List all agents
  - `GET /api/agents/agents/{id}` - Agent details
  - `POST /api/agents/agents` - Create agent
  - `PATCH /api/agents/agents/{id}/status` - Update status
  - `GET /api/agents/collaborations` - Collaboration history
  - `GET /api/agents/network` - Network graph data
  - `GET /api/agents/evolutions` - Evolution history
  - `POST /api/agents/evolutions` - Record evolution
  - `GET /api/agents/activities` - Recent activities
  - `GET /api/agents/charts/performance` - Performance charts

#### 🎨 UI/UX

- **Agent Dashboard Page**
  - Gradient header (green theme)
  - Interactive network graph (D3.js)
  - Performance comparison charts (Chart.js)
  - Evolution timeline
  - Activity log with type indicators
  - Auto-refresh toggle

- **Visualizations**
  - Network graph with force simulation
  - Performance bars with gradients
  - Status badges (color-coded)
  - Evolution items with improvements

### Added - v0.5.0 (2026-04-08)

#### 📊 Analytics & Visualization

- **Cost Dashboard** - Visual cost analytics
  - Real-time cost tracking
  - Provider/model distribution charts
  - Cost trend analysis (30 days)
  - Budget monitoring with progress bars
  - Cost predictions (monthly/yearly)
  - Export to CSV/JSON
  - Alert system

- **Dashboard Features**
  - Summary cards (total cost, tokens, calls)
  - Pie chart for provider distribution
  - Line chart for cost trends
  - Bar chart for model usage
  - Budget progress indicators
  - Alert notifications
  - Auto-refresh every 30 seconds

- **API Endpoints**
  - `GET /api/costs/summary` - Cost summary
  - `GET /api/costs/recent` - Recent usage
  - `POST /api/costs/track` - Track usage
  - `GET /api/costs/budgets` - Budget status
  - `POST /api/costs/budgets` - Set budget
  - `GET /api/costs/alerts` - Get alerts
  - `GET /api/costs/export/csv` - Export CSV
  - `GET /api/costs/export/json` - Export JSON
  - `GET /api/costs/charts/usage` - Chart data
  - `GET /api/costs/analytics` - Analytics data

#### 🎨 UI/UX

- **Dashboard Page**
  - Modern responsive design
  - Bootstrap 5 styling
  - Chart.js visualizations
  - Color-coded status indicators
  - Interactive charts

- **Web Application**
  - Updated main app structure
  - `/dashboard` route for cost dashboard
  - Template rendering
  - Static file serving

### Added - v0.4.0 (2026-04-08)

#### 🔗 Integrations

- **LangChain Integration** - Workflow and tool chains
  - Code generation chain
  - Code evaluation chain
  - Code refactoring chain
  - Tool-enabled harness
  - Predefined workflows
  - Base tools (Generator, Evaluator, Search)

- **VS Code Extension** - IDE integration
  - Code generation from description
  - Code evaluation and feedback
  - Code explanation viewer
  - Automatic refactoring
  - Semantic code search
  - Context menu integration
  - Keyboard shortcuts (Ctrl+Alt+G, Ctrl+Alt+E)
  - Webview panels for results

#### 🎯 Features

- **Workflows**
  - Full development workflow
  - Generate and review workflow
  - Search and adapt workflow

- **VS Code Commands**
  - `harness.generate` - Generate code
  - `harness.evaluate` - Evaluate code
  - `harness.explain` - Explain code
  - `harness.refactor` - Refactor code
  - `harness.search` - Search similar code

- **Tools**
  - CodeGeneratorTool
  - CodeEvaluatorTool
  - CodeSearchTool

### Added - v0.3.0 (2026-04-08)

#### 🔍 Advanced Capabilities

- **Vector Search** - Code semantic search with embeddings
  - OpenAI text-embedding-3-small integration
  - Cosine similarity matching
  - Code snippet indexing
  - Directory-wide indexing
  - Multi-language support (Python, JS/TS, Java, Go, Rust)
  - Persistent vector storage

- **Cost Tracking** - LLM usage analytics
  - Real-time cost tracking per request
  - Support for OpenAI, Anthropic, z.ai, Kimi, MiniMax
  - Budget management with alerts
  - Cost reports by provider/model/date
  - CSV/JSON export
  - Historical usage analysis

- **Plugin System** - Extensible architecture
  - Plugin base class with lifecycle hooks
  - 8 hook types (before/after generate/evaluate/plan, error, success)
  - Plugin discovery and auto-loading
  - Example plugins (Metrics, Example)
  - Plugin CLI for management

#### 📊 Features

- **Code Indexer**
  - Automatic code splitting (functions/classes)
  - Language-specific parsers
  - Batch indexing for repositories

- **Budget Manager**
  - Daily/weekly/monthly budgets
  - Warning alerts at 80%
  - Critical alerts at 100%
  - Budget status API

- **Pricing Configuration**
  - Pre-configured pricing for major providers
  - Automatic cost calculation
  - Easy to update pricing data

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
