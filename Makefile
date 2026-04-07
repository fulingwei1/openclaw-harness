.PHONY: help install test lint format clean build publish

help: ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安装依赖
	poetry install

install-dev: ## 安装开发依赖
	poetry install --with dev

test: ## 运行测试
	poetry run pytest tests/ -v

test-cov: ## 运行测试并生成覆盖率报告
	poetry run pytest tests/ -v --cov=harness --cov-report=html --cov-report=term

lint: ## 运行代码检查
	poetry run flake8 src/ tests/
	poetry run mypy src/

format: ## 格式化代码
	poetry run black src/ tests/
	poetry run isort src/ tests/

format-check: ## 检查代码格式
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/

clean: ## 清理构建产物
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## 构建包
	poetry build

publish: ## 发布到 PyPI（需要配置 token）
	poetry publish

publish-test: ## 发布到 TestPyPI
	poetry config repositories.testpypi https://test.pypi.org/legacy/
	poetry publish -r testpypi

setup-hooks: ## 设置 pre-commit hooks
	poetry run pre-commit install

run-hooks: ## 手动运行 pre-commit
	poetry run pre-commit run --all-files

ci-test: ## CI 测试（包含所有检查）
	@echo "Running format check..."
	$(MAKE) format-check
	@echo "Running lint..."
	$(MAKE) lint
	@echo "Running tests..."
	$(MAKE) test-cov

demo: ## 运行演示
	poetry run harness init
	@echo "✓ Harness initialized. Try: poetry run harness run '创建一个 REST API'"

web: ## 启动 Web UI
	poetry run python run_web.py

web-dev: ## 启动开发服务器（热重载）
	poetry run uvicorn run_web:app --reload --host 0.0.0.0 --port 8000

docker-build: ## 构建 Docker 镜像
	docker build -t openclaw-harness:latest .

docker-run: ## 运行 Docker 容器
	docker run -p 8000:8000 openclaw-harness:latest

version: ## 显示版本
	@poetry version
