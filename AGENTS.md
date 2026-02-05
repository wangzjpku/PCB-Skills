# Agent Development Guidelines

This document provides comprehensive guidelines for developing and maintaining agents in the KiCad Automation Skill repository.

---

## Table of Contents

1. [Setup and Installation](#setup-and-installation)
2. [Code Style Guidelines](#code-style-guidelines)
3. [Testing Guidelines](#testing-guidelines)
4. [Build Commands](#build-commands)
5. [Lint Commands](#lint-commands)
6. [Error Handling](#error-handling)
7. [Development Workflow](#development-workflow)
8. [Repository Structure](#repository-structure)

---

## Setup and Installation

### Initial Setup

```bash
# Clone repository
git clone https://github.com/wangzjpku/PCB-Skills.git
cd PCB-Skills

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run linting and type checking
pip install black mypy pylint

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Development Environment

- **Python Version**: 3.8 or higher
- **KiCad Version**: 7.0 or later with Python scripting support
- **IDE**: Recommended: VS Code, PyCharm, or similar with Python support
- **Optional**: OpenAI API key for enhanced NLP capabilities

### KiCad Integration

**Standalone Mode** (for testing without KiCad):
- Use mock KiCad API for unit tests
- Tests can run independently of KiCad installation

**KiCad Plugin Mode**:
- Copy scripts to KiCad scripting/plugins/ directory
- Test within KiCad GUI
- KiCad must be built with Python scripting support

---

## Code Style Guidelines

### General Principles

- **Readability First**: Write code that is easy to understand and maintain
- **Type Safety**: Use type hints for all function signatures and class attributes
- **Modularity**: Keep functions focused and single-purpose
- **Documentation**: Document public APIs with docstrings
- **Testing**: Write tests for all public functionality

### Python Code Style

Follow **PEP 8** with these modifications:

#### Imports

```python
# Standard library imports first (sorted alphabetically)
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Union
from datetime import datetime

# Third-party imports second
try:
    import pandas as pd
except ImportError:
    pd = None  # Handle optional dependencies gracefully

# Local imports last (relative imports)
from core.exceptions import KiCadAutomationError
from core.utils import load_config, save_config
```

**Import Organization Rules**:
1. Group standard library imports alphabetically
2. Separate third-party imports
3. Use relative imports for local modules
4. Import only what you need
5. Handle ImportError gracefully for optional dependencies

#### Type Hints

```python
# Use modern type hints (Python 3.9+)
from typing import (
    List, Dict, Set, Tuple, Optional, Union,
    Callable, TypeVar, Generic, Any
)

# Define type aliases for complex types
ComponentID = str
Coordinate = Tuple[float, float]
LayerID = int

# Use Generic for flexible return types
T = TypeVar('T')

def process_items(items: List[T]) -> List[T]:
    """Process a list of items with type preservation."""
    pass
```

**Type Hinting Rules**:
- Use `Optional[T]` for nullable parameters
- Use `Union[str, int]` for flexible input types
- Define type aliases for commonly used types
- Use TypeVar for generic functions
- Always annotate function signatures
- Use `-> ReturnType` for return types

#### Naming Conventions

```python
# Classes: PascalCase
class KiCadAssistant:
    pass

class PCBDesignSpec:
    pass

# Functions and methods: snake_case
def create_pcb(spec: PCBDesignSpec) -> bool:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_HISTORY_SIZE = 1000
DEFAULT_LAYER = "F.Cu"
API_TIMEOUT = 30  # seconds

# Private methods: single underscore prefix
def _parse_with_keywords(text: str) -> Dict:
    pass

# Internal variables: double underscore prefix
self.__board = None
self.__history = []
```

**Naming Rules**:
- Classes: PascalCase (CamelCase with first letter capitalized)
- Functions/Methods: snake_case (words separated by underscores)
- Constants: UPPER_SNAKE_CASE (all caps, underscores)
- Private methods: _single_leading_underscore
- Internal variables: __double_leading_underscore
- Avoid single-letter variables (use descriptive names)

#### Formatting

**Indentation**: Use 4 spaces (no tabs)

```python
class Example:
    def method(self, param: str) -> bool:
        if param:
            # 4 space indentation
            result = self._helper(param)
            return result
        return False
```

**Black Formatter** (recommended):
```bash
# Install Black
pip install black

# Format code
black scripts/ core/ examples/ tests/

# Format with specific line length
black --line-length 100 scripts/core.py

# Check formatting (dry run)
black --check scripts/core.py
```

**Line Length**: Maximum 100-120 characters preferred

```python
# Bad: Too long
result = self.very_long_method_name_that_does_too_much(parameter_1, parameter_2, parameter_3)

# Good: Descriptive but concise
result = self._parse_command(text)
```

**Whitespace**:
- No trailing whitespace at end of lines
- Single blank line between functions/methods
- Two blank lines between top-level definitions
- No multiple consecutive blank lines

#### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def create_pcb(self, spec: PCBDesignSpec) -> bool:
    """
    Create a new PCB board with specified parameters.

    This function initializes a new PCB board object in KiCad and applies
    the specified design parameters such as dimensions, layer count, and thickness.

    Args:
        spec (PCBDesignSpec): Object containing board specifications including
            width (Union[str, float]): Board width in mm (e.g., "100mm" or 100.0)
            height (Union[str, float]): Board height in mm (e.g., "50mm" or 50.0)
            layers (int): Number of layers (default: 2)
            thickness (str): Board thickness in mm (default: "1.6mm")
            name (str): Board name/identifier (default: "Untitled")

    Returns:
        bool: True if PCB was created successfully, False otherwise

    Raises:
        KiCadAutomationError: If KiCad API is not available or board creation fails

    Example:
        >>> assistant = KiCadAssistant()
        >>> spec = PCBDesignSpec(width="100mm", height="50mm", name="MyBoard")
        >>> success = assistant.create_pcb(spec)
        >>> print(f"Created: {success}")
    """
    if not HAS_KICAD:
        raise KiCadAutomationError("KiCad API not available")
    # Implementation...
```

**Docstring Guidelines**:
- Triple double quotes (`"""`) for docstrings
- Include: description, args, returns, raises, example
- Use Google style (compatible with most tools)
- Document exceptions that can be raised
- Provide usage examples for complex functions

#### Dataclasses

Use `@dataclass` for structured data with default values:

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class PCBDesignSpec:
    """
    Specification for PCB design parameters.

    Attributes:
        width: Board width in mm (supports string like "100mm" or float)
        height: Board height in mm
        layers: Number of copper layers (default: 2)
        thickness: Board thickness (default: "1.6mm")
        name: Board identifier (default: "Untitled")
    """
    width: Union[str, float]
    height: Union[str, float]
    layers: int = 2
    thickness: str = "1.6mm"
    name: str = "Untitled"

    # Advanced usage with field()
    design_rules: Optional[str] = field(default=None)
    board_outline: Optional[List[Tuple[float, float]]] = None
```

**Dataclass Guidelines**:
- Use `@dataclass` for data containers
- Provide default values in the type annotation
- Use `field()` for complex defaults or metadata
- Use Optional[T] for nullable fields
- Include docstring for the dataclass
- Consider using `frozen=True` for immutable data structures

---

## Testing Guidelines

### Test Structure

```python
# tests/test_core.py
import pytest
from scripts.core import KiCadAssistant, PCBDesignSpec

class TestKiCadAssistant:
    """Test suite for KiCadAssistant class."""

    @pytest.fixture
    def assistant():
        """Fixture providing KiCadAssistant instance."""
        return KiCadAssistant()

    def test_create_pcb_success(self, assistant, mock_kicad):
        """Test successful PCB creation."""
        spec = PCBDesignSpec(width="100mm", height="50mm", name="TestBoard")
        result = assistant.create_pcb(spec)
        assert result is True
        assert assistant.board is not None

    def test_create_pcb_invalid_dimensions(self, assistant):
        """Test PCB creation with invalid dimensions."""
        spec = PCBDesignSpec(width="-10mm", height="0mm", name="InvalidBoard")
        result = assistant.create_pcb(spec)
        assert result is False

    def test_add_component_success(self, assistant):
        """Test successful component addition."""
        pass
```

### Test Organization

```
tests/
├── __init__.py
├── test_core.py          # Core functionality tests
├── test_pcb_design.py    # PCB design tests
├── test_schematic.py    # Schematic design tests
├── test_parsing.py       # NLP/parsing tests
├── test_export.py         # Export functionality tests
└── fixtures/              # Test data and mock objects
    ├── mock_kicad.py      # Mock KiCad API
    ├── sample_designs.py   # Sample PCB designs
    └── test_data.json       # JSON test data
```

### Testing Best Practices

**Unit Tests**:
- Test each public function independently
- Use pytest fixtures for setup/teardown
- Mock external dependencies (KiCad API, OpenAI)
- Test both success and failure cases
- Test edge cases (empty inputs, invalid values)

**Integration Tests**:
- Test workflows end-to-end
- Test file I/O operations
- Test with real KiCad installation (if available)

**Test Coverage**:
- Aim for >80% code coverage
- Use `pytest --cov=scripts --cov-report=html`
- Run coverage check in CI/CD

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=scripts --cov-report=html tests/

# Run specific test file
pytest tests/test_core.py

# Run tests with verbose output
pytest -v tests/

# Run tests in parallel (pytest-xdist)
pytest -n auto tests/
```

### Test Naming Conventions

- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<method_name>_<scenario>`
- Fixtures: Use `@pytest.fixture` for reusable setup

```python
# Good test names
def test_create_pcb_with_valid_dimensions(assistant, mock_kicad):
    pass

def test_create_pcb_with_negative_dimensions(assistant, mock_kicad):
    pass

def test_create_pcb_without_kicad_api(assistant):
    pass
```

---

## Build Commands

### Python Package Build

```bash
# Build source distribution
python -m build

# Build wheel distribution
python -m pip wheel

# Clean build artifacts
python setup.py clean
```

### Development Commands

```bash
# Format code
black scripts/ core/ examples/ tests/

# Type checking
mypy scripts/ --ignore-missing-imports

# Linting
pylint scripts/ --max-line-length=100 --disable=R0913

# Security scan
bandit -r scripts/ core/ examples/

# Sort imports
isort scripts/ --profile black
```

### Installation Test

```bash
# Test installation in development mode
pip install -e .

# Test installation from wheel
pip install dist/kicad_automation-1.0.0-py3-none-any.whl

# Verify installation
pip show kicad-automation
```

---

## Lint Commands

### PyLint

```bash
# Install pylint
pip install pylint

# Run pylint on core module
pylint scripts/core.py --rcfile=.pylintrc

# Run pylint on entire project
pylint scripts/ tests/ examples/ --errors-only

# Generate pylint report
pylint scripts/core.py --output-format=json > pylint_report.json
```

### Pylint Configuration

Create `.pylintrc` in project root:

```ini
[MASTER]
# Set expected Python version
py-version = 3.8

# Use multiple processes
jobs = 1

# Disable specific checks (customize as needed)
disable=
    C0111,  # Wrong-import-order (use isort instead)
    C0103,  # Missing-docstring-class
    R0901,  # Too-few-public-methods
    R0913,  # Too-many-arguments

# Configure checks
[FORMAT]
# Use 4 spaces for indentation
indent-string='    '

# Maximum line length
max-line-length=100

# Good variable names
good-names=i,j,k,ex,Run,_,temp,a,b,c,d,e

# Suggest method names if not snake_case
function-rgx=[a-z_][a-z0-9_]{2,}(?!_]$

[BASIC]
# Good variable names
good-names=i,j,k,ex,Run,_,temp,a,b,c,d,e,f,m,n,o,t,s,v,w

# Always check for __init__
include-naming-hint=no
```

### Black Configuration

Create `pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310']
include = '\.pyi$'
extend-exclude = '''
/(
  # Build artifacts
  build/
  dist/
  __pycache__/
  # Test cache
  .pytest_cache/
  .mypy_cache/
  # Version control
  \.git/
  # IDE
  \.vscode/
  \.idea/
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 100
```

### MyPy Configuration

Create `mypy.ini`:

```ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_ignores = True
disallow_untyped_defs = True
disallow_any_generics = True
show_error_codes = True
exclude = (?x)(
    build/
    dist/
    __pycache__/
    tests/fixtures/
    \.venv/
    \.venv2/
)

[[tool.mypy.overrides]]
module = "pcbnew"
ignore_missing_imports = True
```

---

## Error Handling

### Exception Hierarchy

```python
# Base exception for all KiCad automation errors
class KiCadAutomationError(Exception):
    """Base exception for KiCad automation errors."""
    pass

# Specific error types
class BoardNotFoundError(KiCadAutomationError):
    """Raised when attempting to operate on a non-existent board."""
    pass

class ComponentNotFoundError(KiCadAutomationError):
    """Raised when a footprint or component cannot be found."""
    pass

class ParsingError(KiCadAutomationError):
    """Raised when natural language parsing fails."""
    pass

class ExportError(KiCadAutomationError):
    """Raised when file export operations fail."""
    pass

class DRCViolationError(KiCadAutomationError):
    """Raised when DRC/ERC checks find violations."""
    pass

class ConfigurationError(KiCadAutomationError):
    """Raised when configuration is invalid or missing."""
    pass
```

### Error Handling Patterns

**Never Suppress Errors**:
```python
# BAD: Suppressing exceptions silently
try:
    result = risky_operation()
except Exception:
    pass  # Lost all error information!

# GOOD: Handle or re-raise with context
try:
    result = risky_operation()
except KiCadAutomationError as e:
    logger.error(f"Operation failed: {e}")
    raise  # Re-raise for caller to handle
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise KiCadAutomationError(f"Failed: {e}") from e
```

**Use Context Managers**:
```python
# For resource management
from contextlib import contextmanager

@contextmanager
def pcb_operation(board):
    """Context manager for safe PCB operations."""
    try:
        yield board
        # Perform operations
    finally:
        # Cleanup
        if board:
            board.Cleanup()
```

**Log Errors Appropriately**:
```python
import logging

logger = logging.getLogger(__name__)

try:
    result = operation()
except KiCadAutomationError as e:
    # Expected errors - log with info level
    logger.info(f"Expected error occurred: {e}")
except Exception as e:
    # Unexpected errors - log with error level
    logger.error(f"Unexpected error in operation: {e}")
    logger.debug(f"Traceback:", exc_info=True)
```

### Error Recovery

**Retry Logic**:
```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    """Decorator for retrying failed operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def unstable_operation():
    """Operation that may need retrying."""
    pass
```

---

## Development Workflow

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-functionality

# Make changes
# Edit files...

# Stage changes
git add .

# Commit with conventional commits
git commit -m "feat: add XYZ functionality"

# Push to remote
git push origin feature/new-functionality

# Create pull request on GitHub
```

**Commit Message Format** (Conventional Commits):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add schematic design support
fix: resolve Gerber export layer ordering issue
docs: update API reference documentation
test: add unit tests for component placement
refactor: simplify parsing strategy pattern
chore: update dependencies and requirements.txt
```

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] All public functions have docstrings
- [ ] Tests added or updated
- [ ] No new dependencies without justification
- [ ] Error handling implemented
- [ ] No commented-out code
- [ ] Imports organized correctly
- [ ] Type hints complete
- [ ] Code is self-documenting
- [ ] No hardcoded values that should be configurable

### Release Process

```bash
# Update version in core/__init__.py
__version__ = "1.0.1"  # Increment version

# Update CHANGELOG.md
# Add release notes

# Tag release
git tag -a v1.0.1 -m "Release version 1.0.1"

# Push tag
git push origin v1.0.1

# Create GitHub release
gh release create v1.0.1 --title "Release v1.0.1" --notes "..."
```

---

## Repository Structure

```
PCB-Skills/
├── .github/                 # GitHub-specific files
│   └── workflows/        # CI/CD workflows
│       └── test.yml     # Automated testing
├── docs/                    # Documentation
│   ├── api.md            # API reference
│   ├── tutorials.md       # Step-by-step guides
│   └── architecture.md   # System design docs
├── scripts/                 # Main source code
│   ├── __init__.py
│   ├── core.py           # Core functionality
│   ├── parsers/          # NLP/parsing modules
│   ├── exporters/        # Export functionality
│   └── validators/        # Input validation
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_core.py
│   ├── fixtures/         # Test data
│   └── conftest.py        # Pytest configuration
├── examples/               # Usage examples
│   ├── basic_usage.py
│   └── advanced_patterns.py
├── .gitignore             # Git ignore rules
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
├── pyproject.toml         # Project metadata
├── setup.py               # Package setup
├── README.md              # Project README
├── CHANGELOG.md            # Version history
├── LICENSE                 # License file
└── AGENTS.md              # This file
```

### Module Organization

**Core Module** (`scripts/core.py`):
- Main KiCadAssistant class
- Data structures (PCBDesignSpec, ComponentSpec, TrackSpec)
- Public API methods
- Helper methods (private)

**Parsers** (`scripts/parsers/`):
- Natural language parsing strategies
- Keyword matching
- OpenAI integration
- Pattern extraction

**Exporters** (`scripts/exporters/`):
- Gerber export
- STEP export
- BOM generation
- Format converters

**Validators** (`scripts/validators/`):
- Input validation
- Type checking
- Range validation
- Constraint checking

---

## Quick Reference

### Common Commands

```bash
# Setup environment
make setup

# Run tests
make test

# Format code
make format

# Type check
make type-check

# Lint code
make lint

# Build distribution
make build

# Run single test
make test-single TEST=tests/test_core.py::test_create_pcb

# Run with coverage
make test-cov
```

### File Templates

**New Feature Template**:
```python
"""
Module description.

Implements specific functionality for...
"""

from typing import Optional

def public_function(param: str) -> bool:
    """
    Brief description.

    Args:
        param: Description

    Returns:
        bool: Return value description
    """
    # Implementation
    pass

# Unit tests in tests/test_module.py
```

**New Test Template**:
```python
import pytest
from scripts.module import public_function

def test_public_function_success():
    """Test successful case."""
    assert public_function("valid_input") is True

def test_public_function_failure():
    """Test failure case."""
    with pytest.raises(Exception):
        public_function("invalid_input")
```

---

## Additional Resources

### Documentation

- [KiCad Python Scripting Reference](https://docs.kicad.org/python/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [pytest Documentation](https://docs.pytest.org/)
- [Type Hints Documentation](https://docs.python.org/3/library/typing.html)

### Tools

- **Black**: Code formatter - https://github.com/psf/black
- **Pylint**: Code linter - https://pylint.org/
- **MyPy**: Static type checker - https://mypy-lang.org/
- **pytest**: Testing framework - https://docs.pytest.org/
- **pre-commit**: Git hooks framework - https://pre-commit.com/

### IDE Extensions

- **VS Code**: Python extension pack (Pylance, Black formatter)
- **PyCharm**: Built-in Black and Pylint support
- **Git Integration**: Ensure proper Git hooks are configured

---

## Summary

Follow these guidelines to maintain code quality, consistency, and reliability across the KiCad Automation Skill codebase. Remember that code is read by other agents (including your future self!), so clarity and maintainability are essential.

**Key Principles**:
1. **Write clear, readable code**
2. **Use type hints consistently**
3. **Write comprehensive tests**
4. **Handle errors gracefully**
5. **Document public APIs**
6. **Follow naming conventions**
7. **Keep functions focused and single-purpose**
