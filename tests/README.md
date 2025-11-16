# Mergington High School API Tests

This directory contains comprehensive test suites for the Mergington High School API using pytest and FastAPI's test client.

## Test Structure

```
tests/
├── __init__.py           # Test package marker
├── conftest.py           # Pytest configuration and shared fixtures
├── test_api.py           # Core API endpoint tests
└── test_edge_cases.py    # Edge cases and error handling tests
```

## Test Coverage

The test suite provides comprehensive coverage including:

### Core Functionality Tests (`test_api.py`)
- **Root endpoint**: Redirection to static files
- **Activities endpoint**: Listing all activities with proper structure
- **Activity signup**: Valid signups, duplicate prevention, error handling
- **Activity unregistration**: Removing participants, error conditions
- **Integration workflows**: Complete signup/unregister cycles

### Edge Cases and Error Handling (`test_edge_cases.py`)
- **Edge cases**: Special characters, email formats, boundary conditions
- **Data consistency**: Participant order, concurrent operations
- **Error handling**: HTTP status codes, malformed requests
- **Boundary conditions**: Activity limits, data preservation

## Fixtures

The `conftest.py` file provides several useful fixtures:

- `client`: FastAPI test client for making HTTP requests
- `reset_activities`: Resets activity data to original state before each test
- `sample_activity`: Provides sample activity data for testing
- `valid_email`: Valid test email address
- `invalid_email`: Invalid test email address

## Running Tests

### Basic test execution:
```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_api.py -v

# Run specific test class
python -m pytest tests/test_api.py::TestActivitySignup -v

# Run specific test method
python -m pytest tests/test_api.py::TestActivitySignup::test_signup_for_existing_activity -v
```

### Using the test runner script:
```bash
# Run all tests
python run_tests.py

# Run tests with coverage report
python run_tests.py coverage

# Run tests in fast mode (stop on first failure)
python run_tests.py fast

# Show help
python run_tests.py help
```

### Coverage reporting:
```bash
# Generate coverage report
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

# View HTML coverage report
open htmlcov/index.html
```

## Test Statistics

- **Total tests**: 26
- **Test files**: 2
- **Code coverage**: 100%
- **Test categories**:
  - Root endpoint: 1 test
  - Activities listing: 2 tests
  - Activity signup: 7 tests
  - Activity unregistration: 4 tests
  - Integration workflows: 2 tests
  - Edge cases: 4 tests
  - Data consistency: 3 tests
  - Boundary conditions: 2 tests
  - Error handling: 2 tests

## Dependencies

The test suite requires the following packages (specified in `requirements.txt`):

- `pytest`: Testing framework
- `httpx`: HTTP client for FastAPI test client
- `pytest-cov`: Coverage reporting
- `fastapi`: For the TestClient
- `python-multipart`: For form data handling in tests

## Test Philosophy

These tests follow several best practices:

1. **Isolation**: Each test is independent and doesn't rely on other tests
2. **Reset state**: Activity data is reset before each test using fixtures
3. **Comprehensive coverage**: Tests cover both happy path and error conditions
4. **Clear assertions**: Each test has clear, specific assertions
5. **Descriptive names**: Test names clearly describe what is being tested
6. **Edge cases**: Boundary conditions and error states are thoroughly tested

## Adding New Tests

When adding new tests:

1. Use descriptive test method names that explain what is being tested
2. Include both positive and negative test cases
3. Use the provided fixtures for consistent setup
4. Add docstrings explaining the test purpose
5. Group related tests into test classes
6. Ensure new functionality maintains 100% code coverage