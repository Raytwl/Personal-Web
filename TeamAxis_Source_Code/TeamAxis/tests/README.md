# TeamAxis Test Suite

This directory contains comprehensive unit tests for the TeamAxis project management system.

## Test Structure

The test suite is organized as follows:

- `conftest.py` - Pytest configuration and shared fixtures
- `test_db_manager.py` - Tests for database operations
- `test_auth.py` - Tests for authentication and authorization
- `test_helpers.py` - Tests for utility helper functions
- `test_language_manager.py` - Tests for language management
- `test_theme_manager.py` - Tests for theme management
- `test_license_manager.py` - Tests for license management
- `test_progress_visualization.py` - Tests for progress visualization features
- `test_risk_warning.py` - Tests for risk warning system
- `test_task_allocation.py` - Tests for task allocation features
- `test_benchmarks.py` - Performance benchmark tests for critical functions

## Running Tests

### Prerequisites

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_db_manager.py
```

### Run Specific Test Class

```bash
pytest tests/test_db_manager.py::TestDatabaseManager
```

### Run Specific Test Function

```bash
pytest tests/test_db_manager.py::TestDatabaseManager::test_create_user
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=. --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov/` directory.

### Run Benchmark Tests

Benchmark tests measure the performance of critical functions:

```bash
# Run all benchmark tests
pytest tests/test_benchmarks.py --benchmark-only

# Run specific benchmark test
pytest tests/test_benchmarks.py::TestDatabaseBenchmarks::test_hash_password_benchmark --benchmark-only

# Run benchmarks with comparison (requires previous run data)
pytest tests/test_benchmarks.py --benchmark-only --benchmark-compare

# Run benchmarks with JSON output
pytest tests/test_benchmarks.py --benchmark-only --benchmark-json=benchmark_results.json

# Run benchmarks with minimum time threshold
pytest tests/test_benchmarks.py --benchmark-only --benchmark-min-rounds=5
```

The benchmark tests cover:
- Database operations (CRUD operations, queries)
- Helper functions (date validation, formatting, calculations)
- Task allocation functions (workload calculation, recommendations)
- Risk warning system (analysis, alerts, summaries)
- Progress visualization (data retrieval)
- Bulk operations and scalability tests

## Test Coverage

The test suite covers:

- **Database Manager**: User, project, task, license, and risk operations
- **Authentication**: Login, registration, logout, and authorization checks
- **Helper Functions**: Date validation, formatting, progress calculation, and color helpers
- **Language Manager**: Language switching, translation retrieval, and preference management
- **Theme Manager**: Theme switching, color retrieval, and preference management
- **License Manager**: License generation, validation, assignment, and expiration checks
- **Progress Visualization**: Data retrieval and chart generation
- **Risk Warning System**: Risk analysis, alerts, and summaries
- **Task Allocation**: Workload calculation, recommendations, and balance reports
- **Benchmark Tests**: Performance measurements for critical functions and operations

## Test Fixtures

The test suite uses pytest fixtures defined in `conftest.py`:

- `temp_db` - Temporary database for isolated testing
- `auth_manager` - AuthManager instance with temporary database
- `license_manager` - LicenseManager instance with temporary database
- `sample_user` - Sample user for testing
- `sample_admin` - Sample admin user for testing
- `sample_project` - Sample project for testing
- `sample_task` - Sample task for testing

## Notes

- All tests use temporary databases to ensure isolation
- Tests are designed to be independent and can run in any order
- The test suite uses pytest fixtures for setup and teardown
- Each test cleans up after itself to avoid side effects

