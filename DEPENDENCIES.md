# Dependency Management

## Overview

This project uses separate dependency files for production and development environments to ensure reproducibility and clear separation of concerns.

## Dependency Files

### requirements.txt
**Purpose:** Production runtime dependencies only
**Usage:** Deployed environments, Docker containers
**Install:** `pip install -r requirements.txt`

Contains pinned versions of:
- FastAPI: Web framework for building APIs
- Uvicorn: ASGI server for serving FastAPI applications
- Pydantic: Data validation and settings management
- python-json-logger: Structured JSON logging
- httpx: HTTP client for external API calls

### requirements-dev.txt
**Purpose:** Development and testing dependencies
**Usage:** Local development, CI/CD pipelines
**Install:** `pip install -r requirements.txt -r requirements-dev.txt`

Contains:
- **Testing:** pytest, pytest-cov, pytest-asyncio, pytest-mock
- **Code Quality:** black, flake8, mypy, isort
- **Development Tools:** ipython, pre-commit, faker

### requirements-lock.txt
**Purpose:** Fully locked dependency tree with all transitive dependencies
**Usage:** Reproducible builds, security audits
**Install:** `pip install -r requirements-lock.txt`

Includes all dependencies and their subdependencies with exact versions.

## Installation Instructions

### Production Environment
```bash
# Install only production dependencies
pip install -r requirements.txt
```

### Development Environment
```bash
# Install production + development dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Or use locked versions for reproducibility
pip install -r requirements-lock.txt
```

### CI/CD Environment
```bash
# Install all dependencies with locked versions
pip install -r requirements-lock.txt
```

## Dependency Rationale

### Production Dependencies

**fastapi==0.115.5**
- Modern, fast web framework
- Automatic API documentation (OpenAPI/Swagger)
- Native Pydantic integration for request/response validation
- Type hints and async support

**uvicorn==0.35.0**
- ASGI server for running FastAPI
- High performance with async support
- Standard extras include uvloop and httptools for better performance

**pydantic==2.10.4**
- Data validation using Python type hints
- Settings management with environment variable support
- JSON schema generation
- Fast validation with Rust-based core

**pydantic-settings==2.7.1**
- Configuration management from environment variables
- .env file support
- Type-safe settings with validation

**python-json-logger==3.2.1**
- Structured JSON logging for production environments
- Compatible with log aggregation systems (ELK, CloudWatch, etc.)
- Easy parsing and querying of log data

**httpx==0.28.1**
- Modern HTTP client with async support
- Used for health checks and external API calls
- Better than requests for async applications

### Development Dependencies

**Testing Framework:**
- **pytest==8.3.4**: Industry-standard testing framework
- **pytest-cov==6.0.0**: Code coverage reporting
- **pytest-asyncio==0.24.0**: Async test support
- **pytest-mock==3.14.0**: Mocking utilities

**Code Quality:**
- **black==24.10.0**: Opinionated code formatter
- **flake8==7.1.1**: Linting and style checking
- **mypy==1.13.0**: Static type checker
- **isort==5.13.2**: Import statement organizer

**Development Tools:**
- **ipython==8.31.0**: Enhanced interactive Python shell
- **pre-commit==4.0.1**: Git hook framework for code quality checks
- **faker==33.1.0**: Fake data generation for testing

## Version Pinning Strategy

### Production Dependencies
- **Exact versions** (==) for reproducibility
- Pin major, minor, and patch versions
- Update quarterly or for security patches

### Development Dependencies
- **Exact versions** (==) for consistency across team
- Can be updated more frequently
- Does not affect production runtime

### Rationale
- **Reproducibility**: Same versions on all environments
- **Security**: Easy to audit and update specific versions
- **Stability**: Prevents unexpected breakage from automatic updates
- **Compatibility**: Ensures all dependencies work together

## Updating Dependencies

### Check for Updates
```bash
pip list --outdated
```

### Update Individual Package
```bash
pip install --upgrade <package>==<new-version>
# Update requirements.txt with new version
```

### Security Updates
```bash
# Check for security vulnerabilities
pip-audit

# Or use
safety check
```

### Testing After Updates
```bash
# Run full test suite
pytest

# Check type hints
mypy src/

# Check code quality
black --check .
flake8 src/ app/
isort --check-only .
```

## Dependency Conflicts

If you encounter dependency conflicts:

1. **Create clean virtual environment**
   ```bash
   python -m venv venv-clean
   source venv-clean/bin/activate  # or venv-clean\Scripts\activate on Windows
   ```

2. **Install from requirements-lock.txt**
   ```bash
   pip install -r requirements-lock.txt
   ```

3. **If conflicts persist, regenerate lock file**
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   pip freeze > requirements-lock.txt
   ```

## Python Version Compatibility

**Minimum:** Python 3.11
**Recommended:** Python 3.11 or 3.12
**Tested:** Python 3.11, 3.12

Key features requiring Python 3.11+:
- PEP 673: Self type
- PEP 646: Variadic generics
- PEP 655: TypedDict with Required/NotRequired
- Performance improvements

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements-lock.txt

- name: Run tests
  run: pytest --cov=src --cov-report=xml

- name: Check code quality
  run: |
    black --check .
    flake8 src/ app/
    mypy src/
```

### Docker Example
```dockerfile
# Production stage
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM python:3.11-slim as dev
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
```

## Common Issues

### Issue: uvloop installation fails on Windows
**Solution:** Uvicorn falls back to asyncio on Windows automatically

### Issue: pytest not found after installation
**Solution:** Ensure virtual environment is activated

### Issue: Import errors after updates
**Solution:** Reinstall all dependencies
```bash
pip uninstall -r requirements-lock.txt -y
pip install -r requirements-lock.txt
```

## License Compliance

All dependencies use permissive licenses compatible with commercial use:
- MIT License: FastAPI, Pydantic, pytest, black
- Apache 2.0: httpx
- BSD License: uvicorn, flake8

Run `pip-licenses` to generate full license report.
