# Contributing to AzureSearch FileShare Indexer

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

This project follows a Code of Conduct. By participating, you agree to uphold this code.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment details** (Python version, OS, Azure tier)
- **Screenshots** (if applicable)
- **Configuration** (with secrets removed)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** and rationale
- **Proposed solution**
- **Alternative solutions** considered
- **Additional context**

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
```bash
   git checkout -b feature/amazing-feature
```

3. **Make your changes**:
   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation as needed

4. **Run tests**:
```bash
   pytest tests/
```

5. **Commit your changes**:
```bash
   git commit -m 'Add amazing feature'
```
   
   Follow conventional commit format:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation
   - `test:` Tests
   - `refactor:` Code refactoring
   - `style:` Code style changes
   - `chore:` Maintenance tasks

6. **Push to your fork**:
```bash
   git push origin feature/amazing-feature
```

7. **Open a Pull Request**

## Development Setup
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/AzureSearch-FileShare-Indexer.git
cd AzureSearch-FileShare-Indexer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## Code Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/)
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use docstrings for all public methods
```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")
    
    return True
```

### Code Formatting

Use `black` for code formatting:
```bash
black src/ scripts/ tests/
```

Use `flake8` for linting:
```bash
flake8 src/ scripts/ tests/
```

###