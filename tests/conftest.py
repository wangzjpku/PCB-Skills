[pytest]
# Pytest configuration file

# Discover tests in the tests directory
testpaths = tests

# Only look in scripts and examples directories for tests
python_files = scripts/ examples/

# Minimum pytest version
minversion = 7.0

# Command-line options
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=scripts
    --cov-report=term-missing
    --cov-report=html

# Test markers
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, may require external resources)
    slow: Slow running tests (explicitly mark with @pytest.mark.slow)
    kicad_required: Tests that require KiCad to be installed
    openai_required: Tests that require OpenAI API key

# Logging options
log_cli_level = INFO
log_cli_format = %(levelname)s: %(message)s

# Filtering options
filterwarnings =
    # Ignore deprecation warnings during testing
    ignore::DeprecationWarning

# Coverage options
[coverage:run]
source = scripts
omit =
    */tests/*
    */tests/*
    */__pycache__/*
    */venv/*

[coverage:report]
exclude_lines =
    # Exclude exception raising from coverage
    raise NotImplementedError
    raise KiCadAutomationError
