# Build configuration for Make commands

.PHONY: help setup install test format lint type-check clean build dist upload

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m

help:  ## Show this help message
	@echo "$(BLUE)Available targets:$(NC)"
	@echo ""
	@echo "$(BLUE)  Development:$(NC)"
	@echo "  $(GREEN)setup$(NC)          - Setup development environment"
	@echo "  $(GREEN)install$(NC)        - Install dependencies"
	@echo "  $(GREEN)dev-install$(NC)     - Install development dependencies"
	@echo ""
	@echo "$(BLUE)  Quality:$(NC)"
	@echo "  $(GREEN)format$(NC)         - Format code with Black"
	@echo "  $(GREEN)lint$(NC)           - Run Pylint"
	@echo "  $(GREEN)type-check$(NC)     - Run MyPy type checking"
	@echo "  $(GREEN)sort-imports$(NC)   - Sort imports with isort"
	@echo ""
	@echo "$(BLUE)  Testing:$(NC)"
	@echo "  $(GREEN)test$(NC)           - Run all tests"
	@echo "  $(GREEN)test-cov$(NC)       - Run tests with coverage"
	@echo "  $(GREEN)test-single$(NC)    - Run a specific test"
	@echo ""
	@echo "$(BLUE)  Build:$(NC)"
	@echo "  $(GREEN)build$(NC)          - Build distribution packages"
	@echo "  $(GREEN)dist$(NC)           - Build wheel distribution"
	@echo ""
	@echo "$(BLUE)  Cleanup:$(NC)"
	@echo "  $(GREEN)clean$(NC)          - Clean build artifacts"
	@echo "  $(GREEN)dist-clean$(NC)   - Clean distribution files"
	@echo ""
	@echo "$(BLUE)  Help:$(NC)"
	@echo "  $(GREEN)help$(NC)           - Show this help message"

setup: ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	python -m venv venv || true
	@if exist venv\Scripts\activate.bat (
		venv\Scripts\activate.bat
	) else if exist venv\bin\activate (
		source venv/bin/activate
	)
	@echo "$(GREEN)✓ Virtual environment ready$(NC)"
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

install: ## Install production dependencies
	pip install --upgrade pip
	pip install -r requirements.txt

dev-install: ## Install development dependencies
	pip install --upgrade pip
	pip install -r requirements-dev.txt

format: ## Format code with Black
	@echo "$(BLUE)Formatting code...$(NC)"
	black scripts/ core/ examples/ tests/
	@echo "$(GREEN)✓ Code formatted$(NC)"

lint: ## Run Pylint
	@echo "$(BLUE)Running Pylint...$(NC)"
	pylint scripts/ tests/ examples/ --rcfile=.pylintrc
	@if errorlevel 1 (
		@echo "$(RED)✗ Pylint found issues$(NC)"
		exit /b 1
	) else (
		@echo "$(GREEN)✓ No Pylint issues$(NC)"
	)

type-check: ## Run MyPy type checking
	@echo "$(BLUE)Running MyPy type checking...$(NC)"
	mypy scripts/ --config-file=mypy.ini
	@if errorlevel 1 (
		@echo "$(RED)✗ Type checking failed$(NC)"
		exit /b 1
	) else (
		@echo "$(GREEN)✓ Type checking passed$(NC)"
	)

sort-imports: ## Sort imports with isort
	@echo "$(BLUE)Sorting imports...$(NC)"
	isort scripts/ tests/ examples/
	@echo "$(GREEN)✓ Imports sorted$(NC)"

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	pytest tests/ -v
	@if errorlevel 1 (
		@echo "$(RED)✗ Tests failed$(NC)"
		exit /b 1
	) else (
		@echo "$(GREEN)✓ All tests passed$(NC)"
	)

test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest tests/ --cov=scripts --cov-report=html --cov-report=term
	@if errorlevel 1 (
		@echo "$(RED)✗ Tests failed$(NC)"
		exit /b 1
	) else (
		@echo "$(GREEN)✓ Tests completed$(NC)"
		@echo "$(YELLOW)Coverage report: htmlcov/index.html$(NC)"
	)

test-single: ## Run a specific test
	@if "$(TEST)"=="" (
		@echo "$(RED)Error: Please specify TEST variable$(NC)"
		@echo "$(YELLOW)Example:$(NC)"
		@echo "  make test-single TEST=tests/test_core.py::test_create_pcb"
		exit /b 1
	)
	@echo "$(BLUE)Running test: $(TEST)$(NC)"
	pytest $(TEST) -v
	@if errorlevel 1 (
		@echo "$(RED)✗ Test failed$(NC)"
		exit /b 1
	) else (
		@echo "$(GREEN)✓ Test passed$(NC)"
	)

check: ## Run format and lint checks (quick check)
	@echo "$(BLUE)Running quick checks...$(NC)"
	@$(MAKE) format lint type-check

clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	if exist build rmdir /s /q build
	if exist dist rmdir /s /q dist
	if exist __pycache__ rmdir /s /q __pycache__
	@echo "$(GREEN)✓ Clean complete$(NC)"

dist-clean: ## Clean distribution files only
	@echo "$(BLUE)Cleaning distribution files...$(NC)"
	if exist dist rmdir /s /q dist
	@echo "$(GREEN)✓ Distribution files cleaned$(NC)"

build: ## Build source distribution
	@echo "$(BLUE)Building source distribution...$(NC)"
	python -m build
	@echo "$(GREEN)✓ Source distribution built$(NC)"

dist: ## Build wheel distribution
	@echo "$(BLUE)Building wheel distribution...$(NC)"
	python -m pip wheel
	@echo "$(GREEN)✓ Wheel distribution built$(NC)"

upload: ## Upload to PyPI (requires twine)
	@echo "$(BLUE)Uploading to PyPI...$(NC)"
	twine upload dist/*
	@echo "$(GREEN)✓ Upload complete$(NC)"

.PHONY: help setup install test format lint type-check clean build dist
