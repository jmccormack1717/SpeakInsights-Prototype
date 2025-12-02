# Testing Guide

This document provides information about testing in the SpeakInsights project.

## Overview

The project includes comprehensive testing for both backend and frontend:

- **Backend**: pytest with async support, coverage reporting
- **Frontend**: Vitest with React Testing Library
- **CI/CD**: Automated testing via GitHub Actions

## Backend Testing

### Setup

All test dependencies are included in `backend/requirements.txt`:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for API testing

### Running Tests

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_playbooks.py -v

# Run specific test
pytest tests/test_playbooks.py::TestOverviewPlaybook::test_overview_playbook_basic -v

# Run tests in parallel (faster)
pytest tests/ -v -n auto
```

### Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_playbooks.py    # Playbook unit tests
│   ├── test_auth.py         # Authentication tests
│   └── test_api.py          # API integration tests
└── pytest.ini               # Pytest configuration
```

### Writing Tests

Example test structure:

```python
import pytest
from app.services import playbooks

def test_overview_playbook_basic(sample_dataframe):
    """Test overview playbook with valid data"""
    result = playbooks.overview_playbook(sample_dataframe)
    
    assert "visualization" in result
    assert result["visualization"]["type"] == "table"
```

## Frontend Testing

### Setup

Test dependencies are in `frontend/package.json`:
- `vitest` - Test framework
- `@testing-library/react` - React component testing
- `@testing-library/jest-dom` - DOM matchers
- `jsdom` - DOM environment for tests

### Running Tests

```bash
cd frontend

# Run tests once
npm run test

# Run tests in watch mode
npm run test -- --watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### Test Structure

```
frontend/
├── src/
│   ├── test/
│   │   └── setup.ts         # Test setup and mocks
│   ├── components/
│   │   └── __tests__/
│   │       └── QueryChat.test.tsx
│   └── stores/
│       └── __tests__/
│           └── queryStore.test.ts
└── vite.config.ts           # Vitest configuration
```

### Writing Tests

Example test structure:

```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryChat } from '../QueryChat'

describe('QueryChat', () => {
  it('renders the query input', () => {
    render(<QueryChat />)
    expect(screen.getByPlaceholderText(/ask a question/i)).toBeInTheDocument()
  })
})
```

## CI/CD Testing

### GitHub Actions

The `.github/workflows/ci.yml` workflow runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

### What Gets Tested

1. **Backend Tests**
   - All pytest tests
   - Coverage reporting
   - Uploads coverage to Codecov (if configured)

2. **Frontend Tests**
   - All Vitest tests
   - ESLint checks
   - Build verification

3. **Code Quality**
   - Backend: flake8 and black formatting checks
   - Frontend: ESLint

### Viewing Results

- Go to the "Actions" tab in your GitHub repository
- Click on a workflow run to see detailed results
- Green checkmark = all tests passed
- Red X = tests failed (click to see details)

## Coverage Goals

While not strictly enforced, aim for:
- **Backend**: >70% coverage on core business logic (playbooks, services)
- **Frontend**: >60% coverage on components and stores

View coverage reports:
- Backend: `pytest --cov=app --cov-report=html` → open `htmlcov/index.html`
- Frontend: `npm run test:coverage` → check terminal output

## Best Practices

1. **Write tests for new features** - Add tests alongside new code
2. **Test edge cases** - Empty data, invalid inputs, error conditions
3. **Keep tests fast** - Use mocks for external APIs (OpenAI)
4. **Test behavior, not implementation** - Focus on what, not how
5. **Use descriptive test names** - `test_correlation_playbook_insufficient_data` is better than `test_correlation`

## Troubleshooting

### Backend Tests Failing

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that test database paths are correct
- Verify environment variables are set (or use test defaults)

### Frontend Tests Failing

- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check that mocks are properly set up
- Verify Vitest configuration in `vite.config.ts`

### CI Tests Failing Locally

- Make sure you're using the same Python/Node versions as CI
- Check that all dependencies are committed (package-lock.json, requirements.txt)
- Run linting manually: `npm run lint` and `flake8 app/`


