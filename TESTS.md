# HugDimonXat Tests Documentation

This document provides a comprehensive overview of all tests in the HugDimonXat project, including both backend and frontend tests.

## Table of Contents

- [Introduction](#introduction)
- [Backend Tests](#backend-tests)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [Performance Tests](#performance-tests)
- [Frontend Tests](#frontend-tests)
  - [Component Tests](#component-tests)
- [Running Tests](#running-tests)
  - [Running Backend Tests](#running-backend-tests)
  - [Running Frontend Tests](#running-frontend-tests)
- [Test Coverage](#test-coverage)

## Introduction

HugDimonXat uses a comprehensive testing strategy to ensure code quality and reliability. The testing approach includes:

- **Backend Testing**: Using pytest for unit, integration, and performance testing
- **Frontend Testing**: Using Jest and React Testing Library for component testing

## Backend Tests

The backend tests are organized into three main categories: unit tests, integration tests, and performance tests. They are located in the `backend/tests` directory.

### Unit Tests

Unit tests focus on testing individual components and functions in isolation. They are located in the `backend/tests/unit` directory.

| Test File | Description | Purpose |
|-----------|-------------|---------|
| `test_chat_service.py` | Tests for the chat service | Verifies the functionality of the chat service, including message handling, response generation, and conversation management |
| `test_chatgpt_service.py` | Tests for the ChatGPT service | Ensures proper integration with the ChatGPT API, including request formatting and response parsing |
| `test_language_service.py` | Tests for the language service | Validates language detection, processing, and management functionality |
| `test_restaurant_service.py` | Tests for the restaurant service | Tests restaurant data retrieval, filtering, and recommendation functionality |
| `test_sentiment_service.py` | Tests for the sentiment analysis service | Verifies sentiment detection and analysis capabilities |
| `test_services.py` | General service tests | Tests common service functionality and utilities |
| `test_translation_service.py` | Tests for the translation service | Ensures proper translation between languages |

### Integration Tests

Integration tests verify that different components work together correctly. They are located in the `backend/tests/integration` directory.

| Test File | Description | Purpose |
|-----------|-------------|---------|
| `test_admin_routes.py` | Tests for admin API routes | Verifies admin functionality, including user management and system configuration |
| `test_api.py` | General API tests | Tests common API functionality and error handling |
| `test_chat_endpoint.py` | Tests for chat API endpoints | Ensures chat API endpoints correctly handle requests and responses |
| `test_feedback_routes.py` | Tests for feedback API routes | Validates user feedback submission and processing |
| `test_guide_routes.py` | Tests for guide API routes | Tests guide information retrieval and display |
| `test_health_routes.py` | Tests for health check endpoints | Verifies system health monitoring functionality |
| `test_metrics_routes.py` | Tests for metrics API routes | Ensures proper collection and reporting of system metrics |

### Performance Tests

Performance tests measure the system's performance under various conditions. They are located in the `backend/tests/performance` directory.

| Test File | Description | Purpose |
|-----------|-------------|---------|
| `test_benchmarks.py` | Performance benchmarks | Measures response times, throughput, and resource usage for critical system components |

## Frontend Tests

The frontend tests focus on component testing using Jest and React Testing Library. They are located in the `frontend/src` directory.

### Component Tests

Component tests verify that React components render correctly and behave as expected.

| Test File | Description | Purpose |
|-----------|-------------|---------|
| `App.test.tsx` | Tests for the main App component | Verifies that the App component renders correctly and displays the expected content |

## Running Tests

### Running Backend Tests

To run the backend tests, navigate to the `backend` directory and use the following commands:

```bash
# Run all tests
pytest

# Run unit tests only
pytest -m unit

# Run integration tests only
pytest -m integration

# Run performance tests only
pytest -m performance

# Generate coverage report
pytest --cov=app
```

### Running Frontend Tests

To run the frontend tests, navigate to the `frontend` directory and use the following commands:

```bash
# Run all tests
npm test

# Run tests without watch mode
npm test -- --watchAll=false
```

## Test Coverage

The project aims to maintain high test coverage to ensure code quality and reliability. Coverage reports can be generated using the following commands:

### Backend Coverage

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Generate XML coverage report
pytest --cov=app --cov-report=xml
```

The HTML report will be available in the `backend/htmlcov` directory.

### Frontend Coverage

```bash
# Generate coverage report
npm test -- --coverage
```

The coverage report will be available in the `frontend/coverage` directory.