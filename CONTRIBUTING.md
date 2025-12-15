# Contributing to AI Services Layer

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
3. Copy `.env.example` to `.env` and configure as needed
4. Run tests to verify setup:
   ```bash
   pytest
   ```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints on all public methods
- Add docstrings to all classes and public methods
- Maximum line length: 100 characters
- Use meaningful variable and function names

## Architecture Guidelines

### Adding a New Service

1. Define the interface in `ai/interfaces/`
2. Implement mock version in `ai/adapters/mock/`
3. Add real implementation in appropriate adapter directory
4. Update `ServiceFactory` to create the new service
5. Add tests in `ai/tests/`

### Creating a New Adapter

When adding support for a new AI service:

1. Create a new directory in `ai/adapters/`
2. Implement the relevant interfaces
3. Add API key configuration in `ai/config.py`
4. Update `ai/factory.py` to support the new adapter
5. Document API key requirements in README.md

## Testing

- Write unit tests for all new functionality
- Use mock services for testing (avoid API calls in tests)
- Aim for >80% code coverage
- Test both success and error paths

Run tests:
```bash
pytest                           # Run all tests
pytest ai/tests/test_file.py    # Run specific test file
pytest -v                        # Verbose output
pytest --cov=ai                  # With coverage
```

## Error Handling

- Use custom exceptions from `ai/exceptions.py`
- Log errors with appropriate context
- Provide helpful error messages
- Handle API failures gracefully

## Logging

- Use Python's logging module
- Log at appropriate levels:
  - DEBUG: Detailed information for debugging
  - INFO: General informational messages
  - WARNING: Warning messages for recoverable issues
  - ERROR: Error messages for failures
- Include context in log messages

## Documentation

- Update README.md for new features
- Add docstrings following Google style
- Include usage examples
- Document required API keys and configuration

## Pull Request Process

1. Create a feature branch
2. Make your changes
3. Add/update tests
4. Ensure all tests pass
5. Update documentation
6. Submit pull request with clear description

## Questions?

Open an issue for questions or discussions about the project.
