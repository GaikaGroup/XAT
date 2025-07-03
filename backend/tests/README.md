# HugDimonXat Testing Guide

This guide provides instructions for running tests and generating coverage reports for the HugDimonXat backend.

## Table of Contents

- [Setup](#setup)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Coverage Reports](#coverage-reports)
- [Performance Benchmarks](#performance-benchmarks)
- [Adding New Tests](#adding-new-tests)

## Setup

1. Install test dependencies:

```bash
cd backend
pip install -r requirements-test.txt
```

2. Make sure the application is properly configured with a `.env` file or environment variables.

## Running Tests

### Run all tests:

```bash
cd backend
pytest
```

### Run tests with verbose output:

```bash
pytest -v
```

### Run specific test categories:

```bash
# Run unit tests only
pytest -m unit

# Run integration tests only
pytest -m integration

# Run API tests only
pytest -m api

# Run performance tests only
pytest -m performance
```

### Run specific test files:

```bash
# Run a specific test file
pytest tests/unit/test_chat_service.py

# Run a specific test function
pytest tests/unit/test_chat_service.py::TestChatService::test_get_response
```

## Test Categories

The tests are organized into the following categories:

- **Unit Tests**: Test individual functions and classes in isolation
  - Located in `tests/unit/`
  - Marked with `@pytest.mark.unit`

- **Integration Tests**: Test the interaction between components
  - Located in `tests/integration/`
  - Marked with `@pytest.mark.integration`

- **API Tests**: Test the API endpoints
  - Located in `tests/integration/`
  - Marked with `@pytest.mark.api`

- **Performance Tests**: Benchmark critical paths in the application
  - Located in `tests/performance/`
  - Marked with `@pytest.mark.performance`

## Coverage Reports

### Generate a coverage report:

```bash
pytest --cov=app
```

### Generate a detailed HTML coverage report:

```bash
pytest --cov=app --cov-report=html
```

The HTML report will be generated in the `htmlcov` directory. Open `htmlcov/index.html` in a web browser to view the report.

### Generate an XML coverage report (for CI/CD):

```bash
pytest --cov=app --cov-report=xml
```

The XML report will be generated as `coverage.xml` in the current directory.

## Performance Benchmarks

Performance benchmarks are implemented using the `pytest-benchmark` plugin. They measure the performance of critical paths in the application.

### Run performance benchmarks:

```bash
pytest -m performance
```

### Generate a benchmark report:

```bash
pytest -m performance --benchmark-json=benchmark.json
```

The benchmark report will be generated as `benchmark.json` in the current directory.

## Adding New Tests

### Unit Tests

1. Create a new test file in `tests/unit/` with the name `test_<module_name>.py`
2. Import the module to be tested
3. Create a test class with the name `Test<ModuleName>`
4. Add test methods with the name `test_<function_name>`
5. Use the `@pytest.mark.unit` decorator to mark the test class as a unit test

Example:

```python
import pytest
from app.services.my_service import MyService

@pytest.mark.unit
class TestMyService:
    def test_my_function(self):
        # Arrange
        service = MyService()
        
        # Act
        result = service.my_function()
        
        # Assert
        assert result == expected_result
```

### Integration Tests

1. Create a new test file in `tests/integration/` with the name `test_<feature>.py`
2. Import the necessary modules
3. Create a test class with the name `Test<Feature>`
4. Add test methods with the name `test_<scenario>`
5. Use the `@pytest.mark.integration` decorator to mark the test class as an integration test

### Performance Tests

1. Create a new test file in `tests/performance/` with the name `test_<feature>_benchmarks.py`
2. Import the necessary modules
3. Create a test class with the name `Test<Feature>Benchmarks`
4. Add test methods with the name `test_<function>_performance`
5. Use the `@pytest.mark.performance` decorator to mark the test class as a performance test
6. Use the `@pytest.mark.benchmark` decorator to configure the benchmark

Example:

```python
import pytest
import time
from app.services.my_service import my_function

@pytest.mark.performance
class TestMyServiceBenchmarks:
    @pytest.mark.benchmark(
        group="services",
        min_time=0.1,
        max_time=0.5,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_my_function_performance(self, benchmark):
        # Benchmark the function
        result = benchmark(my_function, arg1, arg2)
        
        # Verify the result
        assert result == expected_result
```